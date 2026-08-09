"""IND diff notification pipeline — orchestrates the six stages.

Each stage reads the previous stage's file from a shared run directory and writes
its own, so every stage is independently runnable (see the `just` recipes). This
module simply runs them in order over one run directory.

    scrape → diff → summarise → classify → notify → update corpus

From repo root:
    uv run --project data_pipeline python3 data_pipeline/diff_detector/pipeline.py
    uv run --project data_pipeline python3 data_pipeline/diff_detector/pipeline.py --limit 10
    uv run --project data_pipeline python3 data_pipeline/diff_detector/pipeline.py --dry-run
    uv run --project data_pipeline python3 data_pipeline/diff_detector/pipeline.py --data-dir data/runs/2026-07-19
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

_pipeline_root = Path(__file__).resolve().parents[1]
if str(_pipeline_root) not in sys.path:
    sys.path.insert(0, str(_pipeline_root))

from langsmith import traceable

from diff_detector.classify import RelevanceMap, run_classify_stage
from diff_detector.diff import PageDiff, run_diff_stage
from diff_detector.snapshot import snapshot
from diff_detector.summarize import PageDiffSummary, run_summarize_stage
from diff_detector.notify import run_notify_stage
from diff_detector.update_corpus import run_update_corpus_stage
from lib.config import ensure_run_dir


@dataclass(slots=True)
class INDDiffPipelineResult:
    data_dir: Path
    snapshot_path: Path
    diffs: list[PageDiff]
    summaries: list[tuple[PageDiff, PageDiffSummary]]
    relevance_map: RelevanceMap
    recipients: int = 0
    emails_sent: int = 0
    emails_failed: int = 0
    skipped_no_changes: bool = False


def _trace_outputs(result: INDDiffPipelineResult) -> dict:
    """Trace run counts only — the diffs carry whole pages of text."""
    return {
        "diffs": len(result.diffs),
        "summaries": len(result.summaries),
        "recipients": result.recipients,
        "emails_sent": result.emails_sent,
        "emails_failed": result.emails_failed,
        "skipped_no_changes": result.skipped_no_changes,
    }


# Root span: every LLM call the stages make nests under one trace per run.
@traceable(
    run_type="chain",
    name="ind_diff_pipeline",
    tags=["ind_diff_pipeline"],
    process_outputs=_trace_outputs,
)
def run_ind_diff_pipeline(
    limit: int | None = None,
    dry_run: bool = False,
    data_dir: Path | str | None = None,
    use_cache: bool = False,
) -> INDDiffPipelineResult:
    """Run the full IND diff notification pipeline over a shared run directory.

    Steps (each persists its output into the run directory):
      1. Scrape IND pages into snapshot.json.
      2. Diff snapshot against the stored corpus in Supabase → diff.json.
      3. Summarise each changed page with an LLM → summaries.json.
      4. Classify summaries into a relevance map → relevance.json.
      5. Query opted-in users and send personalised emails → notify_report.json.
      6. Refresh changed/added sources and remove deleted ones → corpus_update.json.
    """
    run_dir = ensure_run_dir(data_dir)
    print(f"Run directory: {run_dir}")

    # Step 1 — scrape
    print("Step 1/6: Scraping IND pages...")
    snapshot_path = snapshot(limit=limit, data_dir=run_dir, use_cache=use_cache)

    # Step 2 — diff
    print("Step 2/6: Diffing snapshot against corpus...")
    diffs = run_diff_stage(data_dir=run_dir)

    if not diffs:
        print("No changes detected — skipping remaining steps.")
        return INDDiffPipelineResult(
            data_dir=run_dir,
            snapshot_path=snapshot_path,
            diffs=[],
            summaries=[],
            relevance_map={},
            skipped_no_changes=True,
        )

    # Step 3 — summarise
    print(f"Step 3/6: Summarising {len(diffs)} diff(s)...")
    summaries = run_summarize_stage(data_dir=run_dir)

    # Step 4 — classify
    print("Step 4/6: Classifying summaries into relevance map...")
    relevance_map = run_classify_stage(data_dir=run_dir)

    # Step 5 — notify
    print("Step 5/6: Notifying opted-in users...")
    stats = run_notify_stage(data_dir=run_dir, dry_run=dry_run)

    # Step 6 — update corpus so the same changes are not notified again tomorrow.
    print("Step 6/6: Updating corpus...")
    run_update_corpus_stage(data_dir=run_dir)

    return INDDiffPipelineResult(
        data_dir=run_dir,
        snapshot_path=snapshot_path,
        diffs=diffs,
        summaries=summaries,
        relevance_map=relevance_map,
        recipients=stats.recipients,
        emails_sent=stats.sent,
        emails_failed=stats.failed,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="IND diff notification pipeline")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max IND pages to scrape (useful for testing).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Render emails but do not send them; the corpus is still refreshed.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Run directory for all stage artifacts (default: data/latest/).",
    )
    parser.add_argument(
        "--use-cache",
        action="store_true",
        help="Scrape step only: serve pages already in the page cache instead of refetching.",
    )
    args = parser.parse_args()

    result = run_ind_diff_pipeline(
        limit=args.limit,
        dry_run=args.dry_run,
        data_dir=args.data_dir,
        use_cache=args.use_cache,
    )

    if result.skipped_no_changes:
        print("Pipeline complete: no changes detected.")
        return

    print(
        "Pipeline complete: "
        f"diffs={len(result.diffs)}, "
        f"recipients={result.recipients}, "
        f"sent={result.emails_sent}, "
        f"failed={result.emails_failed}"
    )


if __name__ == "__main__":
    main()

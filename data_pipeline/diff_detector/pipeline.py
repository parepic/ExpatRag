"""IND diff notification pipeline.

Runs the full chain: scrape → diff → summarise → classify → notify → update corpus.

From repo root:
    uv run --package data-pipeline python3 data_pipeline/diff_detector/pipeline.py
    uv run --package data-pipeline python3 data_pipeline/diff_detector/pipeline.py --limit 10
    uv run --package data-pipeline python3 data_pipeline/diff_detector/pipeline.py --dry-run
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

_pipeline_root = Path(__file__).resolve().parents[1]
if str(_pipeline_root) not in sys.path:
    sys.path.insert(0, str(_pipeline_root))

from diff_detector.classify import RelevanceMap, build_relevance_map
from diff_detector.diff import PageDiff, load_corpus, load_snapshot, run_diff
from diff_detector.notify import notify_users
from diff_detector.snapshot import snapshot
from diff_detector.summarize import PageDiffSummary, summarize_page_diffs
from lib.supabase_client import get_supabase_client


@dataclass(slots=True)
class INDDiffPipelineResult:
    snapshot_path: Path
    diffs: list[PageDiff]
    summaries: list[tuple[PageDiff, PageDiffSummary]]
    relevance_map: RelevanceMap
    recipients: int = 0
    emails_sent: int = 0
    emails_failed: int = 0
    skipped_no_changes: bool = False


def run_ind_diff_pipeline(
    limit: int | None = None,
    dry_run: bool = False,
) -> INDDiffPipelineResult:
    """Run the full IND diff notification pipeline.

    Steps:
      1. Scrape IND pages into a fresh snapshot file.
      2. Diff snapshot against the stored corpus in Supabase.
      3. Summarise each changed page with an LLM.
      4. Classify summaries into a relevance map (which user segments care about what).
      5. Query opted-in users and send personalised notification emails.
      6. TODO: upsert changed/added pages back to the sources table and re-embed.
    """
    client = get_supabase_client()

    # Step 1 — scrape
    print("Step 1/5: Scraping IND pages...")
    snapshot_path = snapshot(limit=limit)

    # Step 2 — diff
    print("Step 2/5: Diffing snapshot against corpus...")
    corpus = load_corpus(client)
    new_snapshot = load_snapshot(snapshot_path)
    diffs = run_diff(corpus, new_snapshot)
    print(f"  {len(diffs)} changed page(s) detected")

    if not diffs:
        print("No changes detected — skipping remaining steps.")
        return INDDiffPipelineResult(
            snapshot_path=snapshot_path,
            diffs=[],
            summaries=[],
            relevance_map={},
            skipped_no_changes=True,
        )

    # Step 3 — summarise
    print(f"Step 3/5: Summarising {len(diffs)} diff(s)...")
    summaries = summarize_page_diffs(diffs)

    # Step 4 — classify
    print("Step 4/5: Classifying summaries into relevance map...")
    relevance_map = build_relevance_map(summaries)

    # Step 5 — notify
    print("Step 5/5: Notifying opted-in users...")
    stats = notify_users(relevance_map, client, dry_run=dry_run)
    print(
        f"  recipients={stats.recipients}, "
        f"sent={stats.sent}, failed={stats.failed}"
    )

    # Step 6 — update corpus (TODO)
    # Once this lands, upsert changed/added pages back to the sources table and
    # re-chunk/re-embed so the RAG chatbot reflects the updated IND content.

    return INDDiffPipelineResult(
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
        help="Render emails but do not send them; print recipient count only.",
    )
    args = parser.parse_args()

    result = run_ind_diff_pipeline(limit=args.limit, dry_run=args.dry_run)

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

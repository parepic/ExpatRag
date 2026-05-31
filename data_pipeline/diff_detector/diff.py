"""Diff pipeline: compare corpus (Supabase sources) against snapshot (JSON) and write a report."""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_pipeline_root = Path(__file__).resolve().parents[1]
if str(_pipeline_root) not in sys.path:
    sys.path.insert(0, str(_pipeline_root))

from lib.config import DIFF_DIR, SNAPSHOT_DIR
from lib.supabase_client import get_supabase_client


def load_corpus() -> dict[str, str]:
    """Load full page text for all sources from Supabase. Returns {url: content}."""
    client = get_supabase_client()
    result: dict[str, str] = {}
    page_size = 200
    offset = 0

    while True:
        rows = (
            client.table("sources")
            .select("source_url, content")
            .range(offset, offset + page_size - 1)
            .execute()
            .data
        )
        for row in rows:
            if row.get("content"):
                result[row["source_url"]] = row["content"]
        if len(rows) < page_size:
            break
        offset += page_size

    print(f"Loaded {len(result)} pages from Supabase (corpus)")
    return result


def load_snapshot(path: Path | None = None) -> dict[str, str]:
    """Load full page text from a snapshot JSON file. Returns {url: content}.

    If path is None, uses the most recent snapshot_*.json in SNAPSHOT_DIR.
    """
    if path is None:
        snapshots = sorted(SNAPSHOT_DIR.glob("snapshot_*.json"))
        if not snapshots:
            raise FileNotFoundError(
                f"No snapshot files found in {SNAPSHOT_DIR}. Run `just reindex` first."
            )
        path = snapshots[-1]

    print(f"Loading snapshot from {path}")
    records = json.loads(path.read_text())
    return {r["url"]: r["content"] for r in records if r.get("content")}


def run_diff(corpus: dict[str, str], snapshot: dict[str, str]) -> str:
    """Compare corpus and snapshot, classify pages, and return the full report as a string."""
    all_urls = sorted(set(corpus) | set(snapshot))
    sections: list[str] = []

    changed = added = removed = unchanged = 0

    for url in all_urls:
        in_corpus = url in corpus
        in_snapshot = url in snapshot

        if in_corpus and in_snapshot:
            old_lines = corpus[url].splitlines(keepends=True)
            new_lines = snapshot[url].splitlines(keepends=True)
            diff = list(difflib.unified_diff(old_lines, new_lines, fromfile="corpus", tofile="snapshot"))
            if diff:
                sections.append(f"=== CHANGED: {url} ===\n" + "".join(diff))
                changed += 1
            else:
                unchanged += 1
        elif in_snapshot:
            sections.append(f"=== ADDED: {url} ===")
            added += 1
        else:
            sections.append(f"=== REMOVED: {url} ===")
            removed += 1

    summary = (
        f"Summary: {changed} changed, {added} added, {removed} removed, {unchanged} unchanged "
        f"({len(all_urls)} total pages)\n"
    )
    return summary + "\n" + "\n\n".join(sections)


def write_report(report: str) -> Path:
    """Write the diff report to data/diffs/diff_<timestamp>.txt and return the path."""
    DIFF_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = DIFF_DIR / f"diff_{timestamp}.txt"
    output_path.write_text(report)
    print(f"Report written to {output_path}")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare corpus (Supabase sources) against snapshot (JSON) and write a diff report."
    )
    parser.add_argument(
        "--snapshot",
        type=Path,
        default=None,
        help="Path to snapshot JSON file. Defaults to the most recent snapshot_*.json in data/snapshots/.",
    )
    args = parser.parse_args()

    corpus = load_corpus()
    snapshot = load_snapshot(args.snapshot)
    report = run_diff(corpus, snapshot)
    write_report(report)


if __name__ == "__main__":
    main()

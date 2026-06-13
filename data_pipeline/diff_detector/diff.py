"""Diff pipeline: compare corpus (Supabase sources) against snapshot (JSON) and write a report."""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

_pipeline_root = Path(__file__).resolve().parents[1]
if str(_pipeline_root) not in sys.path:
    sys.path.insert(0, str(_pipeline_root))

from lib.config import DIFF_DIR, SNAPSHOT_DIR
from lib.supabase_client import get_supabase_client


@dataclass(slots=True)
class PageDiff:
    url: str
    change_type: Literal["CHANGED", "ADDED", "REMOVED"]
    unified_diff: str  # non-empty for CHANGED; empty string otherwise
    content: str       # new content for CHANGED/ADDED; old content for REMOVED


def load_corpus(client: Any | None = None) -> dict[str, str]:
    """Load full page text for all sources from Supabase. Returns {url: content}."""
    client = client or get_supabase_client()
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


def load_snapshot_records(path: Path) -> list[dict]:
    """Load full snapshot records (url, title, content, scraped_at) from a snapshot JSON file."""
    return [r for r in json.loads(path.read_text()) if r.get("content")]


def run_diff(corpus: dict[str, str], snapshot: dict[str, str]) -> list[PageDiff]:
    """Compare corpus and snapshot and return a structured list of page-level changes."""
    all_urls = sorted(set(corpus) | set(snapshot))
    diffs: list[PageDiff] = []

    for url in all_urls:
        in_corpus = url in corpus
        in_snapshot = url in snapshot

        if in_corpus and in_snapshot:
            old_lines = corpus[url].splitlines(keepends=True)
            new_lines = snapshot[url].splitlines(keepends=True)
            diff_lines = list(
                difflib.unified_diff(old_lines, new_lines, fromfile="corpus", tofile="snapshot")
            )
            if diff_lines:
                diffs.append(PageDiff(
                    url=url,
                    change_type="CHANGED",
                    unified_diff="".join(diff_lines),
                    content=snapshot[url],
                ))
        elif in_snapshot:
            new_lines = snapshot[url].splitlines(keepends=True)
            diffs.append(PageDiff(
                url=url,
                change_type="ADDED",
                unified_diff="".join(f"+{line}" for line in new_lines),
                content=snapshot[url],
            ))
        else:
            old_lines = corpus[url].splitlines(keepends=True)
            diffs.append(PageDiff(
                url=url,
                change_type="REMOVED",
                unified_diff="".join(f"-{line}" for line in old_lines),
                content=corpus[url],
            ))

    return diffs


def render_report(diffs: list[PageDiff], total_pages: int) -> str:
    """Render a human-readable diff report. Only CHANGED pages are shown in the body."""
    changed = sum(1 for d in diffs if d.change_type == "CHANGED")
    added = sum(1 for d in diffs if d.change_type == "ADDED")
    removed = sum(1 for d in diffs if d.change_type == "REMOVED")
    unchanged = total_pages - len(diffs)

    summary = (
        f"Summary: {changed} changed, {added} added, {removed} removed, {unchanged} unchanged "
        f"({total_pages} total pages)\n"
    )
    sections = [
        f"=== CHANGED: {d.url} ===\n{d.unified_diff}"
        for d in diffs
        if d.change_type == "CHANGED"
    ]
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
    snapshot_data = load_snapshot(args.snapshot)
    total_pages = len(set(corpus) | set(snapshot_data))
    diffs = run_diff(corpus, snapshot_data)
    report = render_report(diffs, total_pages)
    write_report(report)


if __name__ == "__main__":
    main()

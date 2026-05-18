"""Diff pipeline: compare D (Supabase sources) against D' (snapshot JSON) and write a report."""

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

from lib.config import DATA_DIR
from lib.supabase_client import get_supabase_client


def load_d() -> dict[str, str]:
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

    print(f"Loaded {len(result)} pages from Supabase (D)")
    return result


def load_d_prime(path: Path | None = None) -> dict[str, str]:
    """Load full page text from a snapshot JSON file. Returns {url: content}.

    If path is None, uses the most recent snapshot_*.json in DATA_DIR.
    """
    if path is None:
        snapshots = sorted(DATA_DIR.glob("snapshot_*.json"))
        if not snapshots:
            raise FileNotFoundError(
                f"No snapshot files found in {DATA_DIR}. Run `just reindex` first."
            )
        path = snapshots[-1]

    print(f"Loading snapshot from {path} (D')")
    records = json.loads(path.read_text())
    return {r["url"]: r["content"] for r in records if r.get("content")}


def run_diff(d: dict[str, str], d_prime: dict[str, str]) -> str:
    """Compare D and D', classify pages, and return the full report as a string."""
    all_urls = sorted(set(d) | set(d_prime))
    sections: list[str] = []

    changed = added = removed = unchanged = 0

    for url in all_urls:
        in_d = url in d
        in_d_prime = url in d_prime

        if in_d and in_d_prime:
            old_lines = d[url].splitlines(keepends=True)
            new_lines = d_prime[url].splitlines(keepends=True)
            diff = list(difflib.unified_diff(old_lines, new_lines, fromfile="D", tofile="D'"))
            if diff:
                sections.append(f"=== CHANGED: {url} ===\n" + "".join(diff))
                changed += 1
            else:
                unchanged += 1
        elif in_d_prime:
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
    """Write the diff report to data/diff_<timestamp>.txt and return the path."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = DATA_DIR / f"diff_{timestamp}.txt"
    output_path.write_text(report)
    print(f"Report written to {output_path}")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare D (Supabase sources) against D' (snapshot JSON) and write a diff report."
    )
    parser.add_argument(
        "--snapshot",
        type=Path,
        default=None,
        help="Path to snapshot JSON file. Defaults to the most recent snapshot_*.json in data/.",
    )
    args = parser.parse_args()

    d = load_d()
    d_prime = load_d_prime(args.snapshot)
    report = run_diff(d, d_prime)
    write_report(report)


if __name__ == "__main__":
    main()

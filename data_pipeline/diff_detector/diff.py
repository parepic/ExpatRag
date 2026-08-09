"""Stage 2 — diff: compare corpus (Supabase sources) against the snapshot and
write <data_dir>/diff.json (a serialized list of page-level changes)."""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

_pipeline_root = Path(__file__).resolve().parents[1]
if str(_pipeline_root) not in sys.path:
    sys.path.insert(0, str(_pipeline_root))

from lib.config import (
    DIFF_FILENAME,
    SCRAPE_SITES,
    SNAPSHOT_FILENAME,
    ensure_run_dir,
)
from lib.supabase_client import get_supabase_client


# Paragraphs of unchanged context kept on each side of a hunk. Page text is split by
# line, and each line is a whole paragraph, so this is paragraphs — not short lines.
DIFF_CONTEXT_LINES = 5


@dataclass(slots=True)
class PageDiff:
    url: str
    change_type: Literal["CHANGED", "ADDED", "REMOVED"]
    unified_diff: str      # non-empty for CHANGED; empty string otherwise
    content: str           # new content for CHANGED/ADDED; old content for REMOVED
    old_content: str = ""  # corpus text (empty for ADDED)
    new_content: str = ""  # snapshot text (empty for REMOVED)
    title: str = ""        # snapshot page title (empty for REMOVED)
    source: str = ""       # site the page came from, e.g. "ind.nl" (empty for REMOVED)


def load_corpus(
    client: Any | None = None,
    sites: list[str] | None = None,
) -> dict[str, str]:
    """Load full page text for the scraped sites' sources. Returns {url: content}.

    Rows are filtered by the `type` column, which holds the site a page came from
    ("ind.nl"). Only the sites in SCRAPE_SITES are loaded, so the snapshot and the corpus
    cover the same ground — otherwise a site that was not scraped this run would have
    every one of its pages reported as REMOVED, and stage 6 would delete them.
    """
    client = client or get_supabase_client()
    sites = SCRAPE_SITES if sites is None else sites
    result: dict[str, str] = {}
    page_size = 200
    offset = 0

    while True:
        rows = (
            client.table("sources")
            .select("source_url, content")
            .in_("type", sites)
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


def load_snapshot_records(path: Path) -> list[dict]:
    """Load full snapshot records (url, title, source, content, scraped_at) from a snapshot file."""
    return [r for r in json.loads(path.read_text()) if r.get("content")]


def run_diff(
    corpus: dict[str, str],
    snapshot: dict[str, str],
    titles: dict[str, str] | None = None,
    sources: dict[str, str] | None = None,
) -> list[PageDiff]:
    """Compare corpus and snapshot and return a structured list of page-level changes.

    ``titles`` and ``sources`` map a snapshot URL to its page title and to the site it
    came from. Both are carried onto CHANGED/ADDED diffs so stage 6 can refresh the
    corpus — including the `type` column — without re-reading the snapshot. REMOVED pages
    are only ever deleted, so they need neither.
    """
    titles = titles or {}
    sources = sources or {}
    all_urls = sorted(set(corpus) | set(snapshot))
    diffs: list[PageDiff] = []

    for url in all_urls:
        in_corpus = url in corpus
        in_snapshot = url in snapshot

        if in_corpus and in_snapshot:
            old_lines = corpus[url].splitlines(keepends=True)
            new_lines = snapshot[url].splitlines(keepends=True)
            diff_lines = list(
                difflib.unified_diff(
                    old_lines, new_lines, fromfile="corpus", tofile="snapshot",
                    n=DIFF_CONTEXT_LINES,
                )
            )
            if diff_lines:
                diffs.append(PageDiff(
                    url=url,
                    change_type="CHANGED",
                    unified_diff="".join(diff_lines),
                    content=snapshot[url],
                    old_content=corpus[url],
                    new_content=snapshot[url],
                    title=titles.get(url, ""),
                    source=sources.get(url, ""),
                ))
        elif in_snapshot:
            new_lines = snapshot[url].splitlines(keepends=True)
            diffs.append(PageDiff(
                url=url,
                change_type="ADDED",
                unified_diff="".join(f"+{line}" for line in new_lines),
                content=snapshot[url],
                old_content="",
                new_content=snapshot[url],
                title=titles.get(url, ""),
                source=sources.get(url, ""),
            ))
        else:
            old_lines = corpus[url].splitlines(keepends=True)
            diffs.append(PageDiff(
                url=url,
                change_type="REMOVED",
                unified_diff="".join(f"-{line}" for line in old_lines),
                content=corpus[url],
                old_content=corpus[url],
                new_content="",
                title="",
            ))

    return diffs


def write_diffs(diffs: list[PageDiff], path: Path) -> Path:
    """Serialize a list of PageDiff to a JSON file."""
    payload = [asdict(d) for d in diffs]
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"Diff written to {path} ({len(payload)} changed page(s))")
    return path


def load_diffs(path: Path) -> list[PageDiff]:
    """Load a list of PageDiff from a JSON file written by write_diffs."""
    return [PageDiff(**record) for record in json.loads(path.read_text())]


def run_diff_stage(
    data_dir: Path | str | None = None,
    client: Any | None = None,
) -> list[PageDiff]:
    """Diff <data_dir>/snapshot.json against the corpus and write <data_dir>/diff.json."""
    run_dir = ensure_run_dir(data_dir)
    records = load_snapshot_records(run_dir / SNAPSHOT_FILENAME)
    snapshot_content = {r["url"]: r["content"] for r in records}
    titles = {r["url"]: r.get("title", "") for r in records}
    sources = {r["url"]: r.get("source", "") for r in records}

    corpus = load_corpus(client)
    diffs = run_diff(corpus, snapshot_content, titles=titles, sources=sources)
    print(f"{len(diffs)} changed page(s) detected")

    write_diffs(diffs, run_dir / DIFF_FILENAME)
    return diffs


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Stage 2 — compare the corpus (Supabase sources) against "
            "<data_dir>/snapshot.json and write <data_dir>/diff.json."
        )
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Run directory holding snapshot.json (default: data/latest/).",
    )
    args = parser.parse_args()
    run_diff_stage(data_dir=args.data_dir)


if __name__ == "__main__":
    main()

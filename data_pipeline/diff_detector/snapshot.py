"""Stage 1 — snapshot: scrape IND pages and write <data_dir>/snapshot.json (D')."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_pipeline_root = Path(__file__).resolve().parents[1]
if str(_pipeline_root) not in sys.path:
    sys.path.insert(0, str(_pipeline_root))

from lib.config import PAGE_LIMIT, SCRAPE_SITES, SNAPSHOT_FILENAME, ensure_run_dir
from scrape.discovery import discover_all_pages
from scrape.extractor import extract_documents
from scrape.fetcher import fetch_pages


def snapshot(
    limit: int | None = None,
    data_dir: Path | str | None = None,
    use_cache: bool = False,
) -> Path:
    """Scrape the configured sites and write them to <data_dir>/snapshot.json.

    Returns the path.
    """
    pages = discover_all_pages(SCRAPE_SITES)
    effective_limit = limit if limit is not None else PAGE_LIMIT
    if effective_limit is not None:
        pages = pages[:effective_limit]
        print(f"Limited to {effective_limit} pages")

    fetched_pages = fetch_pages(pages, use_cache=use_cache)
    documents = extract_documents(fetched_pages)

    scraped_at = datetime.now(timezone.utc).isoformat()
    records = [
        {
            "url": doc["url"],
            "title": doc.get("title", ""),
            # The site the page came from, e.g. "ind.nl". Stage 2 carries it onto each
            # diff so stage 6 can write it to the `sources.type` column.
            "source": doc.get("source", ""),
            "content": doc.get("content", ""),
            "scraped_at": scraped_at,
        }
        for doc in documents
    ]

    run_dir = ensure_run_dir(data_dir)
    output_path = run_dir / SNAPSHOT_FILENAME
    output_path.write_text(json.dumps(records, indent=2, ensure_ascii=False))
    print(f"Snapshot written to {output_path} ({len(records)} pages)")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stage 1 — scrape IND pages and write <data_dir>/snapshot.json (D')."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of pages to scrape (overrides PAGE_LIMIT config).",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Run directory to write snapshot.json into (default: data/latest/).",
    )
    parser.add_argument(
        "--use-cache",
        action="store_true",
        help="Serve pages already in the page cache from disk instead of refetching.",
    )
    args = parser.parse_args()
    snapshot(limit=args.limit, data_dir=args.data_dir, use_cache=args.use_cache)


if __name__ == "__main__":
    main()

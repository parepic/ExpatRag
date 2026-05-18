"""Snapshot pipeline: scrape IND pages and write to a timestamped JSON file (D')."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_pipeline_root = Path(__file__).resolve().parents[1]
if str(_pipeline_root) not in sys.path:
    sys.path.insert(0, str(_pipeline_root))

from lib.config import DATA_DIR, PAGE_LIMIT
from scrape.discovery import discover_pages
from scrape.extractor import extract_documents
from scrape.fetcher import fetch_pages


def snapshot(limit: int | None = None) -> Path:
    pages = discover_pages()
    effective_limit = limit if limit is not None else PAGE_LIMIT
    if effective_limit is not None:
        pages = pages[:effective_limit]
        print(f"Limited to {effective_limit} pages")

    fetched_pages = fetch_pages(pages)
    documents = extract_documents(fetched_pages)

    scraped_at = datetime.now(timezone.utc).isoformat()
    records = [
        {
            "url": doc["url"],
            "title": doc.get("title", ""),
            "content": doc.get("content", ""),
            "scraped_at": scraped_at,
        }
        for doc in documents
    ]

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = DATA_DIR / f"snapshot_{timestamp}.json"
    output_path.write_text(json.dumps(records, indent=2, ensure_ascii=False))
    print(f"Snapshot written to {output_path} ({len(records)} pages)")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape IND pages and write a JSON snapshot (D')."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of pages to scrape (overrides PAGE_LIMIT config).",
    )
    args = parser.parse_args()
    snapshot(limit=args.limit)


if __name__ == "__main__":
    main()

"""
Data pipeline — scrape pages, then store in db.

From repo root:

    uv run --package data-pipeline python3 data_pipeline/pipeline.py
    uv run --package data-pipeline python3 data_pipeline/pipeline.py --skip-data-fetch

From within data_pipeline/:

    uv run pipeline.py
    uv run pipeline.py --skip-data-fetch
"""

import argparse
import sys

from config import PAGE_LIMIT
from discovery import discover_pages
from extractor import extract_documents
from fetcher import fetch_pages
from store import store_documents


def _scrape() -> list[dict]:
    pages = discover_pages()

    if PAGE_LIMIT is not None:
        pages = pages[:PAGE_LIMIT]
        print(f"Limited to {PAGE_LIMIT} pages")

    fetched = fetch_pages(pages)
    return fetched


def main() -> None:
    parser = argparse.ArgumentParser(description="ExpatRag data pipeline")
    parser.add_argument(
        "--skip-data-fetch",
        action="store_true",
        help="Skip discover/fetch/extract and Supabase upsert (for local dev when the DB is already seeded).",
    )
    args = parser.parse_args()

    print("Starting data pipeline")
    if not args.skip_data_fetch:
        print("Mode: full scrape → extract → store")
        fetched_pages = _scrape()
        documents = extract_documents(fetched_pages)
        store_documents(documents)
    else:
        print(
            "Mode: --skip-data-fetch — not running scrape or store (use seeded data, e.g. supabase db reset)."
        )
    print("Pipeline complete")


if __name__ == "__main__":
    sys.exit(main() or 0)

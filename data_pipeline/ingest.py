"""Ingest pipeline: scrape → JSONL → Supabase, or JSONL → Supabase when skipping fetch."""

from __future__ import annotations
from lib.store import store_documents
from lib.jsonl import load_documents_from_jsonl, write_documents_jsonl
from lib.fetcher import fetch_pages
from lib.extractor import extract_documents
from lib.discovery import discover_pages
from lib.config import DOCUMENTS_JSONL_PATH, PAGE_LIMIT

import argparse
import sys
from pathlib import Path

_pipeline_root = Path(__file__).resolve().parent.parent
if str(_pipeline_root) not in sys.path:
    sys.path.insert(0, str(_pipeline_root))


def ingest(*, skip_data_fetch: bool) -> None:
    if not skip_data_fetch:
        print("Mode: discover → fetch → extract → write JSONL → store")
        pages = discover_pages()
        if PAGE_LIMIT is not None:
            pages = pages[:PAGE_LIMIT]
            print(f"Limited to {PAGE_LIMIT} pages")

        fetched_pages = fetch_pages(pages)
        documents = extract_documents(fetched_pages)
        write_documents_jsonl(DOCUMENTS_JSONL_PATH, documents)
    else:
        print(
            f"Mode: --skip-data-fetch — load documents from {DOCUMENTS_JSONL_PATH} → store"
        )
        documents = load_documents_from_jsonl(DOCUMENTS_JSONL_PATH)

    store_documents(documents)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ExpatRag ingest (sources table + JSONL snapshot)"
    )
    parser.add_argument(
        "--skip-data-fetch",
        action="store_true",
        help=f"Skip scrape; load from {DOCUMENTS_JSONL_PATH} and upsert into Supabase.",
    )
    args = parser.parse_args()
    ingest(skip_data_fetch=args.skip_data_fetch)
    print("Ingest complete")


if __name__ == "__main__":
    main()

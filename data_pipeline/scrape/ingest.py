"""Ingest pipeline: scrape to JSONL and optionally store documents in Supabase."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_pipeline_root = Path(__file__).resolve().parents[1]
if str(_pipeline_root) not in sys.path:
    sys.path.insert(0, str(_pipeline_root))

from lib.config import DOCUMENTS_JSONL_PATH, PAGE_LIMIT
from lib.jsonl import load_documents_from_jsonl, write_documents_jsonl
from scrape.discovery import discover_pages
from scrape.extractor import extract_documents
from scrape.fetcher import fetch_pages
from scrape.store import store_documents


def ingest(*, skip_data_fetch: bool, store: bool = True) -> None:
    if not skip_data_fetch:
        mode = "discover → fetch → extract → write JSONL"
        if store:
            mode += " → store"
        print(f"Mode: {mode}")
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

    if store:
        store_documents(documents)
    else:
        print("Skipping Supabase store (--skip-store).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ExpatRag ingest (sources table + JSONL snapshot)"
    )
    parser.add_argument(
        "--skip-data-fetch",
        action="store_true",
        help=f"Skip scrape; load from {DOCUMENTS_JSONL_PATH} and upsert into Supabase.",
    )
    parser.add_argument(
        "--skip-store",
        action="store_true",
        help="Write/load JSONL but do not upsert documents into Supabase.",
    )
    args = parser.parse_args()
    ingest(skip_data_fetch=args.skip_data_fetch, store=not args.skip_store)
    print("Ingest complete")


if __name__ == "__main__":
    main()

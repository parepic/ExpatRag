"""
Data pipeline — scrape/store pages, chunk/embed them, then fetch/classify/store news.

From repo root:

    uv run --package data-pipeline python3 data_pipeline/scrape/pipeline.py
    uv run --package data-pipeline python3 data_pipeline/scrape/pipeline.py --skip-data-fetch
    uv run --package data-pipeline python3 data_pipeline/scrape/pipeline.py --skip-chunk
"""

import argparse
import sys
from pathlib import Path

_pipeline_root = Path(__file__).resolve().parents[1]
if str(_pipeline_root) not in sys.path:
    sys.path.insert(0, str(_pipeline_root))

from lib.config import DOCUMENTS_JSONL_PATH
from news.ingest import ingest_iamexpat_news
from news.store import store_news_from_jsonl
from scrape.chunk import chunk_sources
from scrape.ingest import ingest


def main() -> None:
    parser = argparse.ArgumentParser(description="ExpatRag data pipeline")
    parser.add_argument(
        "--skip-data-fetch",
        action="store_true",
        help=(
            "Skip scrape; load documents from JSONL and upsert into Supabase "
            f"({DOCUMENTS_JSONL_PATH})."
        ),
    )
    parser.add_argument(
        "--skip-chunk",
        action="store_true",
        help="Skip embedding chunking (no writes to document_chunks).",
    )
    parser.add_argument(
        "--skip-news",
        action="store_true",
        help="Skip news RSS fetching, classification, and storage.",
    )
    parser.add_argument(
        "--skip-news-fetch",
        action="store_true",
        help="News step only: classify/store existing news JSONL without fetching RSS first.",
    )
    parser.add_argument(
        "--news-limit",
        type=int,
        default=None,
        help="News step only: maximum number of news items to classify/store.",
    )
    parser.add_argument(
        "--news-include-all",
        action="store_true",
        help="News fetch only: fetch all RSS items instead of only today's items.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max sources to process in the chunk step (only when chunking runs).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Chunk step only: compute splits and embeddings but do not write to the DB.",
    )
    args = parser.parse_args()

    print("Starting data pipeline")
    ingest(skip_data_fetch=args.skip_data_fetch, store=True)

    if not args.skip_chunk:
        stats = chunk_sources(limit=args.limit, dry_run=args.dry_run)
        if args.dry_run:
            print(
                "Dry run completed: "
                f"sources_processed={stats.sources_processed}, "
                f"sources_skipped={stats.sources_skipped}, "
                f"chunks={stats.chunks_saved}"
            )
        else:
            print(
                "Chunking completed: "
                f"sources_processed={stats.sources_processed}, "
                f"sources_skipped={stats.sources_skipped}, "
                f"chunks_saved={stats.chunks_saved}"
            )
    else:
        print("Skipping chunking (--skip-chunk).")

    if not args.skip_news:
        if args.skip_news_fetch:
            print("Skipping news fetch (--skip-news-fetch); using existing news JSONL.")
        else:
            print("Fetching news RSS into JSONL.")
            ingest_iamexpat_news(include_all=args.news_include_all)

        store_news_from_jsonl(limit=args.news_limit)
    else:
        print("Skipping news pipeline (--skip-news).")

    print("Pipeline complete")


if __name__ == "__main__":
    sys.exit(main() or 0)

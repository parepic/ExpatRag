"""
Data pipeline — ingest into `sources` (see ingest.ingest_runner), then chunk + embed into `document_chunks`.

From repo root:

    uv run --package data-pipeline python3 data_pipeline/pipeline.py
    uv run --package data-pipeline python3 data_pipeline/pipeline.py --skip-data-fetch
    uv run --package data-pipeline python3 data_pipeline/pipeline.py --skip-chunk
"""

import argparse
import sys

from chunk import chunk_sources
from ingest import ingest
from lib.config import DOCUMENTS_JSONL_PATH


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
    ingest(skip_data_fetch=args.skip_data_fetch)

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

    print("Pipeline complete")


if __name__ == "__main__":
    sys.exit(main() or 0)

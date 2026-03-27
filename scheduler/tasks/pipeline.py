"""High-level orchestration for scheduler ingestion tasks."""

import argparse

from scheduler.tasks.chunk import chunk_sources
from scheduler.tasks.save_page import save_pages


def parse_args() -> argparse.Namespace:
    """Parse temporary pipeline CLI flags for selectively running stages."""
    parser = argparse.ArgumentParser(description="Run the scheduler ingestion pipeline.")
    parser.add_argument("--skip-save-pages", action="store_true")
    parser.add_argument("--skip-chunk", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    """Run the configured save-page and chunk stages in sequence."""
    args = parse_args()

    if not args.skip_save_pages:
        save_pages(limit=args.limit, dry_run=args.dry_run)

    if not args.skip_chunk:
        chunk_sources(limit=args.limit, dry_run=args.dry_run)

    print("Pipeline finished.")


if __name__ == "__main__":
    main()

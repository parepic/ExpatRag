"""Ingest today's RSS news items into a local JSONL snapshot.

From repo root:

    uv run --package data-pipeline python3 data_pipeline/news/ingest.py
    uv run --package data-pipeline python3 data_pipeline/news/ingest.py --date 2026-05-14
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

_pipeline_root = Path(__file__).resolve().parents[1]
if str(_pipeline_root) not in sys.path:
    sys.path.insert(0, str(_pipeline_root))

from lib.config import IAMEXPAT_NEWS_RSS_URL, NEWS_ITEMS_JSONL_PATH
from news.feed import fetch_rss_feed, filter_items_by_date, parse_rss_items


def parse_date(value: str) -> date:
    """Parse YYYY-MM-DD CLI dates."""
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Expected date in YYYY-MM-DD format, got {value!r}"
        )
    

def parse_timezone(value: str) -> ZoneInfo:
    """Parse an IANA timezone name."""
    try:
        return ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise argparse.ArgumentTypeError(
            f"Expected an IANA timezone name, got {value!r}"
        ) from exc


def write_news_jsonl(path: Path, items: list[dict]) -> None:
    """Write normalized news items as UTF-8 JSONL."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for item in items:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"Wrote {len(items)} news items to {path}")


def ingest_iamexpat_news(
    *,
    feed_url: str = IAMEXPAT_NEWS_RSS_URL,
    output_path: Path = NEWS_ITEMS_JSONL_PATH,
    target_date: date | None = None,
    timezone: ZoneInfo = ZoneInfo("Europe/Amsterdam"),
    limit: int | None = None,
    include_all: bool = False,
) -> list[dict]:
    """Fetch IamExpat RSS news and write normalized items for the requested date."""
    target_date = target_date or datetime.now(timezone).date()

    print(f"Fetching IamExpat news RSS: {feed_url}")
    feed_xml = fetch_rss_feed(feed_url)
    items = parse_rss_items(feed_xml, source="iamexpat", feed_url=feed_url)

    if include_all:
        selected_items = items
        print(f"Selected all {len(selected_items)} RSS items")
    else:
        selected_items = filter_items_by_date(
            items,
            target_date=target_date,
            timezone=timezone,
        )
        print(
            "Selected "
            f"{len(selected_items)} RSS items for {target_date.isoformat()} "
            f"({timezone.key})"
        )

    if limit is not None:
        selected_items = selected_items[: max(limit, 0)]
        print(f"Limited output to {len(selected_items)} items")

    records = [item.to_dict() for item in selected_items]
    write_news_jsonl(output_path, records)
    return records


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch IamExpat RSS news and write normalized JSONL."
    )
    parser.add_argument(
        "--date",
        type=parse_date,
        default=None,
        help="Publication date to ingest in YYYY-MM-DD format; defaults to today in --timezone.",
    )
    parser.add_argument(
        "--url",
        default=IAMEXPAT_NEWS_RSS_URL,
        help=f"RSS feed URL, default: {IAMEXPAT_NEWS_RSS_URL}",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=NEWS_ITEMS_JSONL_PATH,
        help=f"Output JSONL path, default: {NEWS_ITEMS_JSONL_PATH}",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of matching items to write.",
    )
    parser.add_argument(
        "--timezone",
        type=parse_timezone,
        default=ZoneInfo("Europe/Amsterdam"),
        help="Timezone used for the --date/today filter, default: Europe/Amsterdam.",
    )
    parser.add_argument(
        "--include-all",
        action="store_true",
        help="Write all RSS items instead of filtering to one publication date.",
    )
    args = parser.parse_args()

    ingest_iamexpat_news(
        feed_url=args.url,
        output_path=args.output,
        target_date=args.date,
        timezone=args.timezone,
        limit=args.limit,
        include_all=args.include_all,
    )


if __name__ == "__main__":
    main()

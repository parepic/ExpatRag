"""Classify RSS news JSONL and store alert-worthy items in Supabase.

From repo root:

    uv run --package data-pipeline python3 data_pipeline/news/store.py
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_pipeline_root = Path(__file__).resolve().parents[1]
if str(_pipeline_root) not in sys.path:
    sys.path.insert(0, str(_pipeline_root))

from lib.config import NEWS_ITEMS_JSONL_PATH
from lib.jsonl import load_documents_from_jsonl
from lib.supabase_client import get_supabase_client
from news.alerts import NewsAlertDecision, classify_news_items


def build_news_row(item: dict[str, Any], decision: NewsAlertDecision) -> dict[str, Any]:
    """Map a normalized RSS item and alert decision to the Supabase row shape."""
    now = datetime.now(timezone.utc).isoformat()
    metadata = dict(item.get("metadata") or {})
    metadata.update(
        {
            "guid": item.get("guid"),
            "fetched_at": item.get("fetched_at"),
            "classifier": {
                "name": "patty_watch_llm1",
                "alert": decision.alert,
                "reason": decision.reason,
            },
        }
    )

    return {
        "source": item.get("source") or "unknown",
        "title": item["title"],
        "source_url": item["url"],
        "summary": item.get("summary") or "",
        "published_at": item.get("published_at"),
        "alert_reason": decision.reason,
        "metadata": metadata,
        "last_synced_at": now,
    }


def store_alert_news_items(rows: list[dict[str, Any]]) -> int:
    """Upsert selected alert-worthy news items into Supabase."""
    if not rows:
        print("No alert-worthy news items to store.")
        return 0

    client = get_supabase_client()
    batch_size = 50
    written = 0

    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        client.table("news_items").upsert(
            batch,
            on_conflict="source_url",
        ).execute()
        written += len(batch)
        print(f"  Upserted {written}/{len(rows)} alert news rows")

    print(f"Stored {written} alert-worthy news items in news_items table")
    return written


def store_news_from_jsonl(
    *,
    path: Path = NEWS_ITEMS_JSONL_PATH,
    dry_run: bool = False,
    limit: int | None = None,
) -> int:
    """Read RSS news JSONL, classify items, and store alert-worthy entries."""
    items = load_documents_from_jsonl(path)
    if limit is not None:
        items = items[: max(limit, 0)]

    print(f"Loaded {len(items)} news items from {path}")
    classified = classify_news_items(items)

    selected_rows = [
        build_news_row(item, decision)
        for item, decision in classified
        if decision.alert == 1
    ]
    print(f"Selected {len(selected_rows)}/{len(items)} alert-worthy news items")

    if dry_run:
        for row in selected_rows:
            print(f"  DRY RUN alert: {row['title']} ({row['source_url']})")
        print("Skipping Supabase store (--dry-run).")
        return len(selected_rows)

    return store_alert_news_items(selected_rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Read data_pipeline/data/news_items.jsonl, classify with Patty Watch "
            "LLM1, and store alert-worthy items in Supabase."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=NEWS_ITEMS_JSONL_PATH,
        help=f"Input news JSONL path, default: {NEWS_ITEMS_JSONL_PATH}",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of news items to classify.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Classify and print selected items without writing to Supabase.",
    )
    args = parser.parse_args()

    stored = store_news_from_jsonl(
        path=args.input,
        dry_run=args.dry_run,
        limit=args.limit,
    )
    print(f"News store complete: {stored} rows")


if __name__ == "__main__":
    main()

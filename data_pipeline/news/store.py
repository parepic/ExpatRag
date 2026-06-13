"""Classify unseen RSS news and store alert-worthy items in Supabase."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_pipeline_root = Path(__file__).resolve().parents[1]
if str(_pipeline_root) not in sys.path:
    sys.path.insert(0, str(_pipeline_root))

from lib.config import (
    NEW_ALERT_NEWS_ITEMS_JSONL_PATH,
    NEWS_ITEMS_JSONL_PATH,
)
from lib.jsonl import load_documents_from_jsonl, write_documents_jsonl
from lib.supabase_client import get_supabase_client
from news.alerts import NewsAlertDecision, classify_news_items


@dataclass(slots=True)
class StoreNewsResult:
    loaded: int = 0
    unseen: int = 0
    selected: int = 0
    inserted_rows: list[dict[str, Any]] = field(default_factory=list)

    @property
    def inserted(self) -> int:
        return len(self.inserted_rows)


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


def load_existing_news_urls(client: Any, urls: list[str]) -> set[str]:
    """Return candidate URLs already present in news_items."""
    existing: set[str] = set()
    unique_urls = sorted({url for url in urls if url})

    for start in range(0, len(unique_urls), 100):
        batch = unique_urls[start : start + 100]
        rows = (
            client.table("news_items")
            .select("source_url")
            .in_("source_url", batch)
            .execute()
            .data
            or []
        )
        existing.update(row["source_url"] for row in rows)

    return existing


def store_alert_news_items(
    rows: list[dict[str, Any]],
    *,
    client: Any | None = None,
) -> list[dict[str, Any]]:
    """Insert one atomic batch and return the rows confirmed by Supabase."""
    if not rows:
        print("No alert-worthy news items to store.")
        return []

    client = client or get_supabase_client()
    response = client.table("news_items").insert(rows).execute()
    inserted_rows = response.data or []
    print(f"Stored {len(inserted_rows)} alert-worthy news items")
    return inserted_rows


def store_news_from_jsonl(
    *,
    path: Path = NEWS_ITEMS_JSONL_PATH,
    output_path: Path = NEW_ALERT_NEWS_ITEMS_JSONL_PATH,
    dry_run: bool = False,
    limit: int | None = None,
    client: Any | None = None,
) -> StoreNewsResult:
    """Deduplicate, classify, store, and write the fresh notification handoff."""
    write_documents_jsonl(output_path, [])

    items = load_documents_from_jsonl(path)
    if limit is not None:
        items = items[: max(limit, 0)]

    result = StoreNewsResult(loaded=len(items))
    print(f"Loaded {result.loaded} news items from {path}")
    if not items:
        return result

    client = client or get_supabase_client()
    existing_urls = load_existing_news_urls(
        client,
        [str(item.get("url") or "") for item in items],
    )
    unseen_items = [
        item
        for item in items
        if item.get("url") and item["url"] not in existing_urls
    ]
    result.unseen = len(unseen_items)
    print(f"Selected {result.unseen}/{result.loaded} unseen news items")
    if not unseen_items:
        return result

    classified = classify_news_items(unseen_items)
    selected_rows = [
        build_news_row(item, decision)
        for item, decision in classified
        if decision.alert == 1
    ]
    result.selected = len(selected_rows)
    print(f"Selected {result.selected}/{result.unseen} alert-worthy news items")

    if dry_run:
        for row in selected_rows:
            print(f"  DRY RUN alert: {row['title']} ({row['source_url']})")
        print("Skipping Supabase store and handoff write (--dry-run).")
        return result

    result.inserted_rows = store_alert_news_items(selected_rows, client=client)
    write_documents_jsonl(output_path, result.inserted_rows)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Read news JSONL, skip stored URLs, classify unseen items, and "
            "store alert-worthy entries in Supabase."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=NEWS_ITEMS_JSONL_PATH,
        help=f"Input news JSONL path, default: {NEWS_ITEMS_JSONL_PATH}",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=NEW_ALERT_NEWS_ITEMS_JSONL_PATH,
        help=(
            "Freshly inserted news JSONL handoff, default: "
            f"{NEW_ALERT_NEWS_ITEMS_JSONL_PATH}"
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of input news items to consider.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Classify without writing to Supabase or the notification handoff.",
    )
    args = parser.parse_args()

    result = store_news_from_jsonl(
        path=args.input,
        output_path=args.output,
        dry_run=args.dry_run,
        limit=args.limit,
    )
    print(
        "News store complete: "
        f"loaded={result.loaded}, unseen={result.unseen}, "
        f"selected={result.selected}, inserted={result.inserted}"
    )


if __name__ == "__main__":
    main()

"""Run the three-stage weekly news pipeline."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

_pipeline_root = Path(__file__).resolve().parents[1]
if str(_pipeline_root) not in sys.path:
    sys.path.insert(0, str(_pipeline_root))

from langsmith import traceable

from news.ingest import ingest_iamexpat_news
from news.notify import NotificationStats, send_news_digest_to_subscribers
from news.store import StoreNewsResult, store_news_from_jsonl


@dataclass(slots=True)
class WeeklyNewsResult:
    fetched: int
    store: StoreNewsResult
    notifications: NotificationStats


# Root span: the per-item news classifications nest under one trace per run.
@traceable(
    run_type="chain",
    name="weekly_news_pipeline",
    tags=["weekly_news_pipeline"],
    process_outputs=lambda result: {
        "fetched": result.fetched,
        "unseen": result.store.unseen,
        "alerted": result.store.inserted,
        "recipients": result.notifications.recipients,
        "sent": result.notifications.sent,
    },
)
def run_weekly_news() -> WeeklyNewsResult:
    """Fetch the previous 7 days, store unseen alerts, then notify subscribers."""
    fetched_items = ingest_iamexpat_news(lookback_hours=24 * 7)
    store_result = store_news_from_jsonl()
    notification_stats = send_news_digest_to_subscribers(
        store_result.inserted_rows
    )
    return WeeklyNewsResult(
        fetched=len(fetched_items),
        store=store_result,
        notifications=notification_stats,
    )


def main() -> None:
    result = run_weekly_news()
    print(
        "Weekly news complete: "
        f"fetched={result.fetched}, loaded={result.store.loaded}, "
        f"unseen={result.store.unseen}, selected={result.store.selected}, "
        f"inserted={result.store.inserted}, "
        f"recipients={result.notifications.recipients}, "
        f"sent={result.notifications.sent}, "
        f"failed={result.notifications.failed}"
    )


if __name__ == "__main__":
    main()

from news.daily import run_daily_news
from news.notify import NotificationStats
from news.store import StoreNewsResult


def test_daily_news_runs_stages_in_order_and_passes_inserted_rows(monkeypatch):
    calls: list[object] = []
    inserted_rows = [{"id": "news-1", "source_url": "https://example.com/news"}]

    def ingest(**kwargs):
        calls.append(("fetch", kwargs))
        return [{"url": "https://example.com/news"}]

    def store():
        calls.append(("store",))
        return StoreNewsResult(
            loaded=1,
            unseen=1,
            selected=1,
            inserted_rows=inserted_rows,
        )

    def notify(items):
        calls.append(("notify", items))
        return NotificationStats(items=1, recipients=2, sent=2)

    monkeypatch.setattr("news.daily.ingest_iamexpat_news", ingest)
    monkeypatch.setattr("news.daily.store_news_from_jsonl", store)
    monkeypatch.setattr("news.daily.send_news_digest_to_subscribers", notify)

    result = run_daily_news()

    assert calls == [
        ("fetch", {"lookback_hours": 48}),
        ("store",),
        ("notify", inserted_rows),
    ]
    assert result.fetched == 1
    assert result.store.inserted == 1
    assert result.notifications.sent == 2

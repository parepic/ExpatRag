from datetime import UTC, datetime

import pytest

from lib.jsonl import load_documents_from_jsonl, write_documents_jsonl
from news.alerts import NewsAlertDecision
from news.store import store_news_from_jsonl


def news_item(url: str) -> dict:
    now = datetime(2026, 6, 7, 8, tzinfo=UTC).isoformat()
    return {
        "source": "iamexpat",
        "title": f"Title for {url}",
        "url": url,
        "published_at": now,
        "summary": "A useful summary.",
        "guid": url,
        "fetched_at": now,
        "metadata": {},
    }


def test_store_deduplicates_before_classification(monkeypatch, tmp_path):
    existing = news_item("https://example.com/existing")
    unseen = news_item("https://example.com/unseen")
    input_path = tmp_path / "news.jsonl"
    output_path = tmp_path / "new.jsonl"
    write_documents_jsonl(input_path, [existing, unseen])
    classified_urls: list[str] = []

    monkeypatch.setattr(
        "news.store.load_existing_news_urls",
        lambda _client, _urls: {existing["url"]},
    )

    def classify(items):
        classified_urls.extend(item["url"] for item in items)
        return [
            (item, NewsAlertDecision(alert=0, reason="Not relevant"))
            for item in items
        ]

    monkeypatch.setattr("news.store.classify_news_items", classify)

    result = store_news_from_jsonl(
        path=input_path,
        output_path=output_path,
        client=object(),
    )

    assert classified_urls == [unseen["url"]]
    assert result.loaded == 2
    assert result.unseen == 1
    assert result.inserted_rows == []
    assert load_documents_from_jsonl(output_path) == []


def test_store_ignores_rejected_and_writes_only_inserted_rows(
    monkeypatch,
    tmp_path,
):
    accepted = news_item("https://example.com/accepted")
    rejected = news_item("https://example.com/rejected")
    input_path = tmp_path / "news.jsonl"
    output_path = tmp_path / "new.jsonl"
    write_documents_jsonl(input_path, [accepted, rejected])

    monkeypatch.setattr(
        "news.store.load_existing_news_urls",
        lambda _client, _urls: set(),
    )
    monkeypatch.setattr(
        "news.store.classify_news_items",
        lambda _items: [
            (accepted, NewsAlertDecision(alert=1, reason="Rule change")),
            (rejected, NewsAlertDecision(alert=0, reason="General news")),
        ],
    )

    def insert(rows, **_kwargs):
        return [{"id": "news-1", **rows[0]}]

    monkeypatch.setattr("news.store.store_alert_news_items", insert)

    result = store_news_from_jsonl(
        path=input_path,
        output_path=output_path,
        client=object(),
    )

    assert result.selected == 1
    assert result.inserted == 1
    assert result.inserted_rows[0]["source_url"] == accepted["url"]
    assert load_documents_from_jsonl(output_path) == result.inserted_rows


def test_store_clears_stale_handoff_before_failure(monkeypatch, tmp_path):
    input_path = tmp_path / "news.jsonl"
    output_path = tmp_path / "new.jsonl"
    write_documents_jsonl(input_path, [news_item("https://example.com/new")])
    write_documents_jsonl(output_path, [{"source_url": "stale"}])

    monkeypatch.setattr(
        "news.store.load_existing_news_urls",
        lambda _client, _urls: set(),
    )
    monkeypatch.setattr(
        "news.store.classify_news_items",
        lambda _items: (_ for _ in ()).throw(RuntimeError("classification failed")),
    )

    with pytest.raises(RuntimeError, match="classification failed"):
        store_news_from_jsonl(
            path=input_path,
            output_path=output_path,
            client=object(),
        )

    assert load_documents_from_jsonl(output_path) == []


def test_store_dry_run_leaves_handoff_empty(monkeypatch, tmp_path):
    item = news_item("https://example.com/accepted")
    input_path = tmp_path / "news.jsonl"
    output_path = tmp_path / "new.jsonl"
    write_documents_jsonl(input_path, [item])
    write_documents_jsonl(output_path, [{"source_url": "stale"}])

    monkeypatch.setattr(
        "news.store.load_existing_news_urls",
        lambda _client, _urls: set(),
    )
    monkeypatch.setattr(
        "news.store.classify_news_items",
        lambda _items: [
            (item, NewsAlertDecision(alert=1, reason="Rule change"))
        ],
    )
    monkeypatch.setattr(
        "news.store.store_alert_news_items",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("dry run must not insert")
        ),
    )

    result = store_news_from_jsonl(
        path=input_path,
        output_path=output_path,
        dry_run=True,
        client=object(),
    )

    assert result.selected == 1
    assert result.inserted == 0
    assert load_documents_from_jsonl(output_path) == []

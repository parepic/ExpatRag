from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from lib.jsonl import load_documents_from_jsonl
from news.feed import RssNewsItem
from news.ingest import ingest_iamexpat_news


def rss_item(url: str, published_at: datetime) -> RssNewsItem:
    return RssNewsItem(
        source="iamexpat",
        title=url,
        url=url,
        published_at=published_at.isoformat(),
        summary="Summary",
        guid=url,
        fetched_at=published_at.isoformat(),
        metadata={},
    )


def stub_feed(monkeypatch, items):
    monkeypatch.setattr("news.ingest.fetch_rss_feed", lambda _url: b"<rss />")
    monkeypatch.setattr(
        "news.ingest.parse_rss_items",
        lambda *_args, **_kwargs: items,
    )


def test_ingest_lookback_selects_exact_48_hour_window(monkeypatch, tmp_path):
    now = datetime(2026, 6, 7, 8, tzinfo=UTC)
    items = [
        rss_item("boundary", now - timedelta(hours=48)),
        rss_item("recent", now - timedelta(hours=2)),
        rss_item("old", now - timedelta(hours=48, seconds=1)),
        rss_item("future", now + timedelta(seconds=1)),
    ]
    stub_feed(monkeypatch, items)
    output = tmp_path / "news.jsonl"

    records = ingest_iamexpat_news(
        output_path=output,
        lookback_hours=48,
        now=now,
    )

    assert [record["url"] for record in records] == ["boundary", "recent"]
    assert load_documents_from_jsonl(output) == records


def test_ingest_preserves_date_mode(monkeypatch, tmp_path):
    amsterdam = ZoneInfo("Europe/Amsterdam")
    items = [
        rss_item("matching", datetime(2026, 6, 6, 10, tzinfo=UTC)),
        rss_item("other", datetime(2026, 6, 5, 10, tzinfo=UTC)),
    ]
    stub_feed(monkeypatch, items)

    records = ingest_iamexpat_news(
        output_path=tmp_path / "news.jsonl",
        target_date=date(2026, 6, 6),
        timezone=amsterdam,
    )

    assert [record["url"] for record in records] == ["matching"]


def test_ingest_defaults_to_today_in_amsterdam(monkeypatch, tmp_path):
    amsterdam = ZoneInfo("Europe/Amsterdam")
    now = datetime(2026, 6, 7, 8, tzinfo=UTC)
    today = now.astimezone(amsterdam).date()
    items = [
        rss_item(
            "today",
            datetime.combine(
                today,
                datetime.min.time(),
                tzinfo=amsterdam,
            ).astimezone(UTC),
        ),
        rss_item(
            "yesterday",
            datetime.combine(
                today - timedelta(days=1),
                datetime.min.time(),
                tzinfo=amsterdam,
            ).astimezone(UTC),
        ),
    ]
    stub_feed(monkeypatch, items)

    records = ingest_iamexpat_news(
        output_path=tmp_path / "news.jsonl",
        timezone=amsterdam,
        now=now,
    )

    assert [record["url"] for record in records] == ["today"]


def test_ingest_preserves_include_all_mode(monkeypatch, tmp_path):
    now = datetime(2026, 6, 7, 8, tzinfo=UTC)
    items = [
        rss_item("first", now),
        rss_item("second", now - timedelta(days=30)),
    ]
    stub_feed(monkeypatch, items)

    records = ingest_iamexpat_news(
        output_path=tmp_path / "news.jsonl",
        include_all=True,
    )

    assert [record["url"] for record in records] == ["first", "second"]


def test_ingest_selection_modes_are_mutually_exclusive(tmp_path):
    with pytest.raises(ValueError, match="mutually exclusive"):
        ingest_iamexpat_news(
            output_path=tmp_path / "news.jsonl",
            target_date=date(2026, 6, 6),
            lookback_hours=48,
        )

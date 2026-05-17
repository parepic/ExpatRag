"""Fetch and normalize RSS news items for downstream Patty Watch processing."""

from __future__ import annotations

import html
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime
from email.utils import parsedate_to_datetime
from typing import Any
from zoneinfo import ZoneInfo

import requests


@dataclass(frozen=True, slots=True)
class RssNewsItem:
    """A normalized RSS item ready to be written as JSONL."""

    source: str
    title: str
    url: str
    published_at: str | None
    summary: str
    guid: str | None
    fetched_at: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def child_text(element: ET.Element, tag: str, default: str = "") -> str:
    """Return unescaped child text for a non-namespaced RSS tag."""
    child = element.find(tag)
    if child is None or child.text is None:
        return default
    return html.unescape(child.text.strip())


def fetch_rss_feed(url: str, *, timeout: int = 20) -> bytes:
    """Download an RSS/Atom feed."""
    response = requests.get(
        url,
        headers={
            "User-Agent": "ExpatRagPattyWatch/0.1 (+https://www.iamexpat.nl/rss-feeds/)",
            "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
        },
        timeout=timeout,
    )
    response.raise_for_status()
    return response.content


def parse_rss_datetime(value: str) -> datetime | None:
    """Parse an RSS pubDate into a timezone-aware UTC datetime."""
    if not value:
        return None

    parsed = parsedate_to_datetime(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def parse_rss_items(
    feed_xml: bytes,
    *,
    source: str,
    feed_url: str,
    fetched_at: datetime | None = None,
) -> list[RssNewsItem]:
    """Parse RSS XML into normalized news items."""
    fetched_at = (fetched_at or datetime.now(UTC)).astimezone(UTC)
    root = ET.fromstring(feed_xml)
    items: list[RssNewsItem] = []

    for item in root.findall("./channel/item"):
        raw_published = child_text(item, "pubDate")
        published = parse_rss_datetime(raw_published)
        guid = child_text(item, "guid") or None

        items.append(
            RssNewsItem(
                source=source,
                title=child_text(item, "title", "Untitled"),
                url=child_text(item, "link"),
                published_at=published.isoformat() if published else None,
                summary=" ".join(child_text(item, "description").split()),
                guid=guid,
                fetched_at=fetched_at.isoformat(),
                metadata={
                    "feed_url": feed_url,
                    "raw_pub_date": raw_published,
                    "ingest_type": "rss",
                },
            )
        )

    return items


def filter_items_by_date(
    items: list[RssNewsItem],
    *,
    target_date: date,
    timezone: ZoneInfo,
) -> list[RssNewsItem]:
    """Keep items whose parsed publication date matches the target date in the given timezone."""
    filtered: list[RssNewsItem] = []

    for item in items:
        if item.published_at is None:
            continue
        published = datetime.fromisoformat(item.published_at)
        if published.astimezone(timezone).date() == target_date:
            filtered.append(item)

    return filtered

"""Page discovery for government.nl — walks the XML sitemap, incrementally.

government.nl declares a real sitemap in robots.txt. It is a <sitemapindex> pointing at
~39 child sitemaps, and every <url> in a child carries a <lastmod>. The index entries
themselves carry no <lastmod>, so each child has to be opened to see anything.

Only pages worth fetching are returned: a URL is included when it is new to the corpus,
or when its <lastmod> is newer than the `last_synced_at` we stored for it. Everything
else is skipped, so a run costs 39 XML requests plus one query instead of re-scraping
thousands of pages.
"""

from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

import requests
from lxml import etree

from lib.scrape_config.government import (
    BASE_URL,
    EXCLUDE_PREFIXES,
    INCLUDE_PREFIXES,
    SITEMAP_URL,
    SOURCE_NAME,
)
from lib.supabase_client import get_supabase_client

# The sitemaps are plain XML served without bot protection, so they are fetched
# directly rather than through scrape.do — 39 requests per run is not worth the quota.
USER_AGENT = "ExpatComplianceCopilot/1.0 (educational research project)"
REQUEST_TIMEOUT = 60
DB_PAGE_SIZE = 1000


def _categorize(path: str) -> str:
    """Derive a category from a URL path like '/ministries/ministry-of-health/organisation'."""
    parts = [part for part in path.strip("/").split("/") if part]
    if len(parts) >= 2:
        return "/".join(parts[:-1])
    if parts:
        return parts[0]
    return "other"


def _parse_lastmod(raw: str | None) -> datetime | None:
    """Parse a <lastmod> value into an aware UTC datetime, or None if unusable.

    Values look like '2026-03-11T10:10:50.513Z'. The spec also allows a bare date, and
    a naive value is read as UTC so comparisons never mix aware and naive datetimes.
    """
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _fetch_xml(url: str) -> etree._Element:
    """Fetch and parse one sitemap document."""
    response = requests.get(
        url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()
    return etree.fromstring(response.content)


def _child_sitemap_urls(index: etree._Element) -> list[str]:
    """Return the <sitemap><loc> entries of a sitemap index.

    Matched by local name so a missing or unexpected namespace does not silently
    produce zero results.
    """
    return [
        loc.strip()
        for loc in index.xpath(
            "//*[local-name()='sitemap']/*[local-name()='loc']/text()"
        )
        if loc.strip()
    ]


def _url_entries(urlset: etree._Element) -> list[tuple[str, datetime | None]]:
    """Return (url, lastmod) for every <url> in a child sitemap."""
    entries: list[tuple[str, datetime | None]] = []
    for node in urlset.xpath("//*[local-name()='url']"):
        loc = node.xpath("*[local-name()='loc']/text()")
        if not loc or not loc[0].strip():
            continue
        lastmod = node.xpath("*[local-name()='lastmod']/text()")
        entries.append(
            (loc[0].strip(), _parse_lastmod(lastmod[0] if lastmod else None))
        )
    return entries


def _is_wanted(url: str) -> bool:
    """True when the URL is on-site, under an included prefix, and not under an excluded one.

    The include list is the primary filter — most of government.nl is news, parliamentary
    documents, and organisational pages. An empty INCLUDE_PREFIXES matches nothing.
    """
    if not url.startswith(BASE_URL):
        return False
    path = urlparse(url).path
    return path.startswith(tuple(INCLUDE_PREFIXES)) and not path.startswith(
        tuple(EXCLUDE_PREFIXES)
    )


def load_last_synced(client: Any | None = None) -> dict[str, datetime]:
    """Return {source_url: last_synced_at} for the government.nl pages already stored.

    Matched on the URL prefix rather than on `type`, so rows stored before pages
    recorded their source are still recognised.
    """
    client = client or get_supabase_client()
    synced: dict[str, datetime] = {}
    offset = 0

    while True:
        rows = (
            client.table("sources")
            .select("source_url, last_synced_at")
            .like("source_url", f"{BASE_URL}%")
            .range(offset, offset + DB_PAGE_SIZE - 1)
            .execute()
            .data
        )
        for row in rows:
            stored = _parse_lastmod(row.get("last_synced_at"))
            if stored is not None:
                synced[row["source_url"]] = stored
        if len(rows) < DB_PAGE_SIZE:
            break
        offset += DB_PAGE_SIZE

    return synced


def discover_pages(client: Any | None = None) -> list[dict]:
    """Return page dicts with url, category, and source for pages that need fetching.

    ``source`` is the config's SOURCE_NAME ("government.nl") — it is what ends up in the
    `sources.type` column.
    """
    print(f"Fetching sitemap index: {SITEMAP_URL}")
    child_sitemaps = _child_sitemap_urls(_fetch_xml(SITEMAP_URL))
    print(f"  {len(child_sitemaps)} child sitemap(s)")

    entries: dict[str, datetime | None] = {}
    for index, child in enumerate(child_sitemaps, start=1):
        try:
            found = _url_entries(_fetch_xml(child))
        except (requests.RequestException, etree.XMLSyntaxError) as error:
            print(f"  [{index}/{len(child_sitemaps)}] Failed {child}: {error}")
            continue
        for url, lastmod in found:
            # A URL listed in several sitemaps keeps its newest lastmod.
            if url not in entries or (
                lastmod and (entries[url] is None or lastmod > entries[url])
            ):
                entries[url] = lastmod
        print(f"  [{index}/{len(child_sitemaps)}] {child} — {len(found)} url(s)")

    wanted = {url: lastmod for url, lastmod in entries.items() if _is_wanted(url)}
    synced = load_last_synced(client)

    pages: list[dict] = []
    new_count = unchanged = 0
    for url, lastmod in sorted(wanted.items()):
        stored = synced.get(url)
        if stored is None:
            new_count += 1
        elif lastmod is not None and lastmod <= stored:
            unchanged += 1
            continue
        # A page with no usable lastmod is re-fetched: there is no evidence it is current.
        pages.append({
            "url": url,
            "category": _categorize(urlparse(url).path),
            "source": SOURCE_NAME,
        })

    print(
        f"Discovered {len(pages)} page(s) to fetch from {len(wanted)} sitemap url(s) "
        f"({new_count} new, {unchanged} unchanged since last sync)"
    )
    return pages

from urllib.parse import urljoin

import requests
from lxml import html

from src.config import BASE_URL, SITEMAP_PATH
from src.scraper.fetcher import scrape_do_url

EXCLUDE_PREFIXES = (
    "/en/service-contact",
    "/en/form",
    "/en/search",
    "/en/decision-aid",
)


def _categorize(path: str) -> str:
    """Derive a category from a URL path like '/en/residence-permits/work/...'."""
    parts = path.strip("/").split("/")
    category_parts = parts[1:]
    if len(category_parts) >= 2:
        return "/".join(category_parts[:-1])
    if category_parts:
        return category_parts[0]
    return "other"


def discover_pages() -> list[dict]:
    """Fetch the IND HTML sitemap and return a list of page dicts with url and category."""
    sitemap_url = BASE_URL + SITEMAP_PATH
    print(f"Fetching sitemap: {sitemap_url}")

    api_url = scrape_do_url(sitemap_url)
    response = requests.get(api_url, timeout=60)
    response.raise_for_status()

    tree = html.fromstring(response.content)
    links = tree.xpath("//a[@href]")

    seen = set()
    pages = []
    for link in links:
        href = link.get("href", "")
        url = urljoin(BASE_URL, href)

        if not url.startswith(BASE_URL + "/en/"):
            continue

        path = url.replace(BASE_URL, "")
        if any(path.startswith(prefix) for prefix in EXCLUDE_PREFIXES):
            continue

        if url in seen:
            continue
        seen.add(url)

        pages.append({
            "url": url,
            "category": _categorize(path),
        })

    print(f"Discovered {len(pages)} pages")
    return pages

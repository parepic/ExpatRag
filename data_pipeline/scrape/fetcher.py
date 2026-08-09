import time
import urllib.parse

import requests

from lib.cache import Cache
from lib.config import REQUEST_DELAY, SCRAPE_DO_TOKEN

USER_AGENT = "ExpatComplianceCopilot/1.0 (educational research project)"
SCRAPE_DO_BASE = "https://api.scrape.do"


def scrape_do_url(target_url: str) -> str:
    """Build a scrape.do API URL for the given target URL."""
    if not SCRAPE_DO_TOKEN:
        raise RuntimeError(
            "SCRAPE_DO_TOKEN is not set. Please configure it in your environment or .env file."
        )

    encoded_url = urllib.parse.quote(target_url, safe="")
    return f"{SCRAPE_DO_BASE}/?token={SCRAPE_DO_TOKEN}&url={encoded_url}"


def fetch_pages(pages: list[dict], use_cache: bool = False) -> list[dict]:
    """Download HTML for each page via scrape.do. Returns a new list with an 'html' key added.

    Every successful fetch is written to the Cache. With ``use_cache=True`` a page already
    stored there is served from disk instead — no request, no delay.
    """
    fetched = []
    cache_hits = 0

    with Cache() as cache:
        for i, page in enumerate(pages):
            url = page["url"]

            if use_cache:
                cached_html = cache.get(url)
                if cached_html is not None:
                    cache_hits += 1
                    print(f"[{i + 1}/{len(pages)}] Cached  {url}")
                    fetched.append({**page, "html": cached_html})
                    continue

            print(f"[{i + 1}/{len(pages)}] Fetching {url}")

            try:
                api_url = scrape_do_url(url)
                response = requests.get(
                    api_url,
                    headers={"User-Agent": USER_AGENT},
                    timeout=60,
                )
                response.raise_for_status()
                cache.set(url, response.text)
                fetched.append({**page, "html": response.text})
            except requests.RequestException as e:
                print(f"  Failed to fetch {url}: {e}")

            if i < len(pages) - 1:
                time.sleep(REQUEST_DELAY)

    suffix = f" ({cache_hits} from cache)" if cache_hits else ""
    print(f"Fetched {len(fetched)}/{len(pages)} pages{suffix}")
    return fetched

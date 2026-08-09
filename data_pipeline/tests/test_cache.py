"""Tests for the SQLite page Cache and its wiring into fetch_pages."""

from unittest.mock import MagicMock

import pytest

from lib.cache import Cache
from lib.config import DATA_DIR
from scrape import fetcher


@pytest.fixture
def cache(tmp_path):
    with Cache(path=tmp_path / "cache.db") as instance:
        yield instance


@pytest.fixture
def patched_fetcher_cache(tmp_path, monkeypatch):
    """Make fetch_pages open the temp cache instead of data/cache.db."""
    db = tmp_path / "cache.db"
    monkeypatch.setattr(fetcher, "Cache", lambda: Cache(path=db))
    return db


def _fake_response(text):
    return MagicMock(text=text, raise_for_status=lambda: None)


def test_set_then_get_round_trips(cache):
    cache.set("https://ind.nl/a", "<html>A</html>")

    assert cache.get("https://ind.nl/a") == "<html>A</html>"


def test_get_unknown_url_returns_none(cache):
    assert cache.get("https://ind.nl/never-fetched") is None


def test_set_twice_replaces_the_html(cache):
    cache.set("https://ind.nl/a", "old")
    cache.set("https://ind.nl/a", "new")

    assert cache.get("https://ind.nl/a") == "new"
    assert len(cache) == 1


def test_distinct_urls_are_separate_rows(cache):
    cache.set("https://ind.nl/a", "A")
    cache.set("https://ind.nl/b", "B")

    assert (cache.get("https://ind.nl/a"), cache.get("https://ind.nl/b")) == ("A", "B")
    assert len(cache) == 2


def test_entries_survive_reopening_the_file(tmp_path):
    db = tmp_path / "cache.db"
    with Cache(path=db) as first:
        first.set("https://ind.nl/a", "<html>A</html>")

    with Cache(path=db) as second:
        assert second.get("https://ind.nl/a") == "<html>A</html>"


def test_bare_filename_lands_in_the_data_dir(tmp_path):
    """A relative default must not drop cache.db wherever the command was run from."""
    instance = Cache(path="test-cache-location.db")
    try:
        assert instance.path == DATA_DIR / "test-cache-location.db"
    finally:
        instance.close()
        instance.path.unlink(missing_ok=True)


def test_fetch_writes_to_cache_even_without_use_cache(patched_fetcher_cache, monkeypatch):
    """Fetching always populates the cache — the flag only controls reads."""
    monkeypatch.setattr(fetcher, "scrape_do_url", lambda url: url)
    monkeypatch.setattr(fetcher.requests, "get", lambda *a, **kw: _fake_response("<html>fresh</html>"))

    fetcher.fetch_pages([{"url": "https://ind.nl/a", "category": "c", "source": "ind.nl"}])

    with Cache(path=patched_fetcher_cache) as cache:
        assert cache.get("https://ind.nl/a") == "<html>fresh</html>"


def test_use_cache_serves_from_disk_without_fetching(patched_fetcher_cache, monkeypatch):
    with Cache(path=patched_fetcher_cache) as cache:
        cache.set("https://ind.nl/a", "<html>cached</html>")

    def explode(*_args, **_kwargs):
        raise AssertionError("network was used despite a cache hit")

    monkeypatch.setattr(fetcher, "scrape_do_url", explode)
    monkeypatch.setattr(fetcher.requests, "get", explode)

    fetched = fetcher.fetch_pages(
        [{"url": "https://ind.nl/a", "category": "c", "source": "ind.nl"}],
        use_cache=True,
    )

    assert [p["html"] for p in fetched] == ["<html>cached</html>"]
    # Keys added by discovery must survive a cache hit.
    assert (fetched[0]["source"], fetched[0]["category"]) == ("ind.nl", "c")


def test_without_use_cache_the_network_wins(patched_fetcher_cache, monkeypatch):
    """A stale entry must not be served when the flag is absent."""
    with Cache(path=patched_fetcher_cache) as cache:
        cache.set("https://ind.nl/a", "<html>stale</html>")
    monkeypatch.setattr(fetcher, "scrape_do_url", lambda url: url)
    monkeypatch.setattr(fetcher.requests, "get", lambda *a, **kw: _fake_response("<html>fresh</html>"))

    fetched = fetcher.fetch_pages([{"url": "https://ind.nl/a"}], use_cache=False)

    assert [p["html"] for p in fetched] == ["<html>fresh</html>"]
    with Cache(path=patched_fetcher_cache) as cache:
        assert cache.get("https://ind.nl/a") == "<html>fresh</html>"


def test_cache_miss_falls_back_to_fetching(patched_fetcher_cache, monkeypatch):
    monkeypatch.setattr(fetcher, "scrape_do_url", lambda url: url)
    monkeypatch.setattr(fetcher.requests, "get", lambda *a, **kw: _fake_response("<html>fetched</html>"))

    fetched = fetcher.fetch_pages([{"url": "https://ind.nl/uncached"}], use_cache=True)

    assert [p["html"] for p in fetched] == ["<html>fetched</html>"]

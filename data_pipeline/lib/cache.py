"""SQLite cache of fetched page HTML.

Every successful fetch is stored here. Reads only happen when a caller passes
``use_cache=True`` (``--use-cache`` on the scraping commands), so a normal run always
talks to the network and refreshes the cache, while a cached run can re-extract,
re-chunk, or re-diff the same pages without spending scrape.do quota.

Entries never expire — ``--use-cache`` means "reuse whatever is stored".
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from lib.config import DATA_DIR

_SCHEMA = """
CREATE TABLE IF NOT EXISTS pages (
    url        TEXT PRIMARY KEY,
    html       TEXT NOT NULL,
    fetched_at TEXT NOT NULL
)
"""


class Cache:
    """URL → HTML store backed by a single SQLite file."""

    def __init__(self, path: str | Path = "page_cache.db"):
        # A bare filename resolves under data_pipeline/data/ (git-ignored) rather than
        # whatever directory the command was run from.
        self.path = Path(path)
        if not self.path.is_absolute() and self.path.parent == Path("."):
            self.path = DATA_DIR / self.path
        self.path.parent.mkdir(parents=True, exist_ok=True)

        self._connection = sqlite3.connect(self.path)
        self._connection.execute(_SCHEMA)
        self._connection.commit()

    def get(self, url: str) -> str | None:
        """Return the stored HTML for a URL, or None when it has not been fetched."""
        row = self._connection.execute(
            "SELECT html FROM pages WHERE url = ?", (url,)
        ).fetchone()
        return row[0] if row else None

    def set(self, url: str, html: str) -> None:
        """Store a page's HTML, replacing whatever was there before."""
        self._connection.execute(
            """
            INSERT INTO pages (url, html, fetched_at) VALUES (?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET html = excluded.html,
                                           fetched_at = excluded.fetched_at
            """,
            (url, html, datetime.now(timezone.utc).isoformat()),
        )
        self._connection.commit()

    def __len__(self) -> int:
        return self._connection.execute("SELECT COUNT(*) FROM pages").fetchone()[0]

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> Cache:
        return self

    def __exit__(self, *_exc_info) -> None:
        self.close()

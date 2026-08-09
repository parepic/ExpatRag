"""Per-source page discovery.

Every site gets its own module here exposing ``discover_pages()``, and its own config in
``lib/scrape_config/``. ``DISCOVERY_FUNCTIONS`` maps a site's domain to its
implementation; ``discover_all_pages`` runs a set of them and returns one combined list.
Fetching and document extraction then run over that list.

Sites are named by domain ("ind.nl", "government.nl") — the same value each config
exposes as SOURCE_NAME and that lands in the `sources.type` column, so ``SCRAPE_SITES``
in lib/config.py lists domains too.

Adding a site means three things: a ``discovery_<name>.py`` module here, a
``lib/scrape_config/<name>.py`` config, and one entry in ``DISCOVERY_FUNCTIONS``.
"""

from collections.abc import Callable

from lib.scrape_config.government import SOURCE_NAME as GOVERNMENT_NL
from lib.scrape_config.ind import SOURCE_NAME as IND_NL

from . import discovery_government, discovery_ind

DISCOVERY_FUNCTIONS: dict[str, Callable[[], list[dict]]] = {
    IND_NL: discovery_ind.discover_pages,
    GOVERNMENT_NL: discovery_government.discover_pages,
}

def discover_all_pages(websites: list[str]) -> list[dict]:
    """Discover pages for each named source and return them as one list.

    Duplicate URLs are dropped, keeping the first source that reported them.
    """
    unknown = [website for website in websites if website not in DISCOVERY_FUNCTIONS]
    if unknown:
        raise ValueError(
            f"Unknown source(s): {', '.join(unknown)}. "
            f"Known sources: {', '.join(DISCOVERY_FUNCTIONS)}."
        )

    pages: list[dict] = []
    seen: set[str] = set()
    for website in websites:
        for page in DISCOVERY_FUNCTIONS[website]():
            if page["url"] in seen:
                continue
            seen.add(page["url"])
            pages.append(page)

    print(f"Discovered {len(pages)} page(s) across {len(websites)} source(s)")
    return pages

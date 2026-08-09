"""Discovery configuration for ind.nl."""

# Carried on every discovered page and stored in the `sources.type` column, so later
# stages can tell one site's pages from another's.
SOURCE_NAME = "ind.nl"

BASE_URL = "https://ind.nl"

# IND publishes a human-readable HTML sitemap; discovery scrapes the links out of it.
SITEMAP_PATH = "/en/sitemap"

EXCLUDE_PREFIXES = (
    "/en/service-contact",
    "/en/form",
    "/en/search",
    "/en/decision-aid",
)

"""Discovery configuration for government.nl."""

# Carried on every discovered page and stored in the `sources.type` column, so later
# stages can tell one site's pages from another's.
SOURCE_NAME = "government.nl"

BASE_URL = "https://www.government.nl"

# Declared in https://www.government.nl/robots.txt. Unlike IND's HTML page this is a
# real <sitemapindex>, so discovery has to walk its child sitemaps.
SITEMAP_URL = "https://www.government.nl/sitemap.xml"

# The sitemap holds ~3,700 URLs, and most of it is not expat-facing: /documents (1,435
# dated parliamentary letters and reports), /latest (557 news items), /ministries and
# /government (org charts and cabinet pages). Discovery therefore keeps only the sections
# below — roughly 920 pages. An empty tuple here discovers nothing.
INCLUDE_PREFIXES = (
    "/faq",
    "/themes/migration-and-travel",
    "/themes/taxes-benefits-and-allowances",
    "/themes/work",
    "/themes/building-and-housing",
    "/themes/family-health-and-care",
    "/themes/education",
    "/themes/life-events",
)

# Carve-outs inside the included sections above. /latest and /documents are already
# outside INCLUDE_PREFIXES, so they never reach this check.
EXCLUDE_PREFIXES = (
    "/latest",
    "/documents",
)

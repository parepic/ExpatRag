"""Static backend configuration."""

import os

SESSION_COOKIE = "session_token"
SESSION_DURATION_DAYS = 7
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "true").lower() in {
    "1",
    "true",
    "yes",
}


EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4.1-mini"

SEARCH_STRATEGY = "multi query hybrid search"   # hybrid, multi-query-vector, multi-query-hybrid

CHAT_HISTORY_WINDOW = 20

# When true, the web search agent only returns results from the official Dutch
# government / regulatory domains in `dutch_regulatory_domains.py`. This is a hard
# filter: anything off the list is dropped, so set it to false to search the open web.
WEB_SEARCH_RESTRICT_TO_OFFICIAL_DOMAINS = os.getenv(
    "WEB_SEARCH_RESTRICT_TO_OFFICIAL_DOMAINS", "true"
).lower() in {"1", "true", "yes"}

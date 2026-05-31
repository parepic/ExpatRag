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
RAG_MATCH_COUNT = 5
RAG_MATCH_THRESHOLD = 0.0

SEARCH_STRATEGY = "basic"   # hybrid, multi-query-vector, multi-query-hybrid

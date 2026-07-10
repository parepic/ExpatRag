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

# # Conversation summarization (agent middleware). When the agent's message history
# # exceeds the trigger token budget, older messages are summarized while the most
# # recent ones are kept verbatim, so per-request cost stays bounded as chats grow.
# SUMMARIZATION_TRIGGER_TOKENS = 4000
# SUMMARIZATION_KEEP_MESSAGES = 10

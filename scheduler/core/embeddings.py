"""Embedding client helpers used by the chunking pipeline."""

from functools import lru_cache
import os

from langchain_openai import OpenAIEmbeddings

from scheduler.core.config import CHUNK_EMBEDDING_MODEL
from scheduler.core.env import load_scheduler_env


@lru_cache(maxsize=4)
def get_embeddings(model: str | None = None) -> OpenAIEmbeddings:
    """Return a cached LangChain embeddings client for the configured model."""
    load_scheduler_env()

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY must be set before running scheduler chunking tasks"
        )

    return OpenAIEmbeddings(model=model or CHUNK_EMBEDDING_MODEL)
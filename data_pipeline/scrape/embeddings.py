"""Embedding client for chunking."""

from functools import lru_cache
import os

from langchain_openai import OpenAIEmbeddings

from lib.config import CHUNK_EMBEDDING_MODEL
from lib.env import load_pipeline_env


@lru_cache(maxsize=4)
def get_embeddings(model: str | None = None) -> OpenAIEmbeddings:
    load_pipeline_env()

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY must be set before running chunking."
        )

    return OpenAIEmbeddings(model=model or CHUNK_EMBEDDING_MODEL)

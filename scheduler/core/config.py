"""Shared configuration values for scheduler tasks."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SAVE_PAGE_INPUT_PATH = REPO_ROOT / "scheduler" / "documents.jsonl"
SAVE_PAGE_LIMIT: int | None = None
SAVE_PAGE_DRY_RUN = False
SAVE_PAGE_SOURCE_TYPE = "web_page"

CHUNK_SOURCE_ID: str | None = "7e837dd7-792f-49d9-a3c4-93519c2401c4"
CHUNK_LIMIT: int | None = None
CHUNK_DRY_RUN = False
CHUNK_EMBEDDING_MODEL = "text-embedding-3-small"
CHUNK_OVERRIDE_CHUNKS = False
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
CHUNK_DB_BATCH_SIZE = 100

ENV_FILE_CANDIDATES = (
    REPO_ROOT / ".env",
    REPO_ROOT.parent / ".env",
)
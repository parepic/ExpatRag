import os
from pathlib import Path

from lib.env import load_pipeline_env

load_pipeline_env()

# --- Local data (JSONL under data_pipeline/data/) ---
_DATA_PIPELINE_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = _DATA_PIPELINE_ROOT / "data"
DOCUMENTS_JSONL_PATH = DATA_DIR / "documents.jsonl"

# --- Scraper ---
BASE_URL = "https://ind.nl"
SITEMAP_PATH = "/en/sitemap"
SCRAPE_DO_TOKEN = os.getenv("SCRAPE_DO_TOKEN")
REQUEST_DELAY = 0.5
PAGE_LIMIT = 100

# --- Supabase ---
SUPABASE_URL = os.getenv("SUPABASE_API_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# --- Chunking ---
CHUNK_SOURCE_ID: str | None = None
CHUNK_LIMIT: int | None = None
CHUNK_DRY_RUN = False
CHUNK_EMBEDDING_MODEL = "text-embedding-3-small"
CHUNK_OVERRIDE_CHUNKS = False
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
CHUNK_DB_BATCH_SIZE = 100

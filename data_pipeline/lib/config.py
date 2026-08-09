import os
from pathlib import Path

from lib.env import load_pipeline_env

load_pipeline_env()

# --- Local data (JSONL under data_pipeline/data/) ---
_DATA_PIPELINE_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = _DATA_PIPELINE_ROOT / "data"
DOCUMENTS_JSONL_PATH = DATA_DIR / "documents.jsonl"
IAMEXPAT_NEWS_RSS_URL = "https://www.iamexpat.nl/rss/news-netherlands/news"
NEWS_ITEMS_JSONL_PATH = DATA_DIR / "news_items.jsonl"
NEW_ALERT_NEWS_ITEMS_JSONL_PATH = DATA_DIR / "new_alert_news_items.jsonl"

# --- IND diff pipeline run directory ---
# Each pipeline run writes its per-stage artifacts (snapshot → diff → summaries →
# relevance → notify report → corpus update) into one directory, using the fixed
# filenames below. Stages read the previous stage's file from the same directory.
# The default run directory is overwritten on each run; pass a distinct --data-dir
# to keep a run's artifacts around.
LATEST_RUN_DIR = DATA_DIR / "latest"
SNAPSHOT_FILENAME = "snapshot.json"
DIFF_FILENAME = "diff.json"
SUMMARIES_FILENAME = "summaries.json"
RELEVANCE_FILENAME = "relevance.json"
NOTIFY_REPORT_FILENAME = "notify_report.json"
CORPUS_UPDATE_FILENAME = "corpus_update.json"


def ensure_run_dir(data_dir: Path | str | None = None) -> Path:
    """Resolve a pipeline run directory (default LATEST_RUN_DIR) and create it."""
    run_dir = Path(data_dir) if data_dir else LATEST_RUN_DIR
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


# --- Scraper ---
# Sites to discover pages from, named by domain ("ind.nl", "government.nl"). Each needs a
# key in scrape/discovery/DISCOVERY_FUNCTIONS, the discovery module it points at, and
# per-site settings (base URL, sitemap, path filters) in lib/scrape_config/<name>.py.
SCRAPE_SITES = ["ind.nl", "government.nl"]

SCRAPE_DO_TOKEN = os.getenv("SCRAPE_DO_TOKEN")
REQUEST_DELAY = 0.5
PAGE_LIMIT = None

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

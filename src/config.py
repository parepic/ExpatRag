from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://ind.nl"
SITEMAP_PATH = "/en/sitemap"

# scrape.do configuration
SCRAPE_DO_TOKEN = os.getenv("SCRAPE_DO_TOKEN")

# Delay between requests to scrape.do (seconds)
REQUEST_DELAY = 0.5

# Set to an integer to limit pages during development, None for all
PAGE_LIMIT = 100

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data"
CHROMADB_DIR = PROJECT_ROOT / "data" / "chromadb"

OLLAMA_EMBED_MODEL = "nomic-embed-text"
OLLAMA_LLM_MODEL = "llama3.2"

CHUNK_SIZE = 500

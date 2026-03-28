import os

from dotenv import load_dotenv

load_dotenv()

# --- Scraper ---
BASE_URL = "https://ind.nl"
SITEMAP_PATH = "/en/sitemap"
SCRAPE_DO_TOKEN = os.getenv("SCRAPE_DO_TOKEN")
REQUEST_DELAY = 0.5
# Set to an integer to limit pages during development, None for all
PAGE_LIMIT = 100

# --- Supabase ---
SUPABASE_URL = os.getenv("SUPABASE_API_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

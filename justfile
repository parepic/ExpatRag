default:
    @just --list

# Install each service's dependencies
install:
    uv sync --project backend
    uv sync --project data_pipeline
    cd frontend && pnpm install

# Run the FastAPI backend
backend:
    uv run --project backend fastapi dev backend/app/main.py

# Run the Next.js frontend
frontend:
    cd frontend && pnpm dev

# Full pipeline: scrape pages → store → chunk, then fetch/classify/store news
pipeline-full:
    uv run --project data_pipeline python3 data_pipeline/scrape/pipeline.py

# Store existing page JSONL → Supabase sources table (no HTTP)
store-pages:
    uv run --project data_pipeline python3 data_pipeline/scrape/ingest.py --skip-data-fetch

# Scrape pages → data_pipeline/data/documents.jsonl (no DB writes)
scrape-pages:
    uv run --project data_pipeline python3 data_pipeline/scrape/ingest.py --skip-store

# Fetch today's IamExpat RSS news → data_pipeline/data/news_items.jsonl
fetch-news:
    uv run --project data_pipeline python3 data_pipeline/news/ingest.py

# Deduplicate, classify, store, and write the fresh notification handoff
store-news:
    uv run --project data_pipeline python3 data_pipeline/news/store.py

# Email the fresh store-stage handoff to subscribed users
send-news:
    uv run --project data_pipeline python3 data_pipeline/news/notify.py

# Fetch, classify, store, and email the weekly news digest
weekly-news:
    uv run --project data_pipeline python3 data_pipeline/news/weekly.py

# Chunk sources only (no ingest)
chunk-pages:
    uv run --project data_pipeline python3 data_pipeline/scrape/chunk.py

# Scrape IND pages and write a JSON snapshot to data_pipeline/data/ (no DB writes)
# Pass --limit N to cap the number of pages, e.g.: just reindex --limit 5
reindex *ARGS:
    uv run --project data_pipeline python3 data_pipeline/diff_detector/snapshot.py {{ARGS}}

# Run data pipeline tests
test:
    uv run --project data_pipeline pytest data_pipeline/tests/ -v

# Compare D (Supabase sources) against D' (latest snapshot) and write a diff report
# Pass --snapshot path/to/snapshot.json to use a specific snapshot file
diff *ARGS:
    uv run --project data_pipeline python3 data_pipeline/diff_detector/diff.py {{ARGS}}

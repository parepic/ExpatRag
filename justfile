default:
    @just --list

# Install all dependencies
install:
    uv sync --all-packages
    cd frontend && pnpm install

# Run the FastAPI backend
backend:
    uv run --package backend fastapi dev backend/app/main.py

# Run the Next.js frontend
frontend:
    cd frontend && pnpm dev

# Full pipeline: scrape pages → store → chunk, then fetch/classify/store news
pipeline-full:
    uv run --package data-pipeline python3 data_pipeline/scrape/pipeline.py

# Store existing page JSONL → Supabase sources table (no HTTP)
store-pages:
    uv run --package data-pipeline python3 data_pipeline/scrape/ingest.py --skip-data-fetch

# Scrape pages → data_pipeline/data/documents.jsonl (no DB writes)
scrape-pages:
    uv run --package data-pipeline python3 data_pipeline/scrape/ingest.py --skip-store

# Fetch today's IamExpat RSS news → data_pipeline/data/news_items.jsonl
fetch-news:
    uv run --package data-pipeline python3 data_pipeline/news/ingest.py

# Classify existing news JSONL and store alert-worthy items → Supabase news_items
store-news:
    uv run --package data-pipeline python3 data_pipeline/news/store.py

# Chunk sources only (no ingest)
chunk-pages:
    uv run --package data-pipeline python3 data_pipeline/scrape/chunk.py

# Scrape IND pages and write a JSON snapshot to data_pipeline/data/ (no DB writes)
# Pass --limit N to cap the number of pages, e.g.: just reindex --limit 5
reindex *ARGS:
    uv run --package data-pipeline python3 data_pipeline/scrape/snapshot.py {{ARGS}}

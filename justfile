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

# Run the scheduler pipeline
scheduler:
    uv run --package scheduler python3 -m scheduler.tasks.pipeline

# Load demo pages into sources
save-pages:
    uv run --package scheduler python3 -m scheduler.tasks.save_page

# Chunk sources and save embeddings
chunk-pages:
    uv run --package scheduler python3 -m scheduler.tasks.chunk
# Run the data pipeline (scrape → store)
pipeline:
    uv run --package data-pipeline python3 data_pipeline/pipeline.py

# Skip scrape + store (use seeded DB, e.g. after supabase db reset)
pipeline-skip-data-fetch:
    uv run --package data-pipeline python3 data_pipeline/pipeline.py --skip-data-fetch

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

# Full pipeline: ingest (scrape → JSONL → store) → chunk
pipeline-full:
    uv run --package data-pipeline python3 data_pipeline/pipeline.py

# Ingest from JSONL only → store (no HTTP)
ingest-from-json:
    uv run --package data-pipeline python3 data_pipeline/ingest.py --skip-data-fetch

# Ingest only (scrape → data_pipeline/data/documents.jsonl → store)
ingest:
    uv run --package data-pipeline python3 data_pipeline/ingest.py

# Chunk sources only (no ingest)
chunk-pages:
    uv run --package data-pipeline python3 data_pipeline/chunk.py

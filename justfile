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
    uv run --package scheduler python3 scheduler/tasks/pipeline.py

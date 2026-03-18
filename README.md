# ExpatRag

A RAG-powered legal and compliance assistant for expats and small businesses in the Netherlands. It translates complex rules from government sources (IND, Belastingdienst, KVK) into plain, actionable answers — with every claim cited back to the official source.

## Key Features

- **Up-to-date document pipeline** — Scheduled scraper that pulls the latest Dutch and English documentation from IND, Rijksoverheid, and Belastingdienst
- **RAG-based Q&A** — User questions are embedded, matched against retrieved legal chunks, and answered by an LLM
- **Citation engine** — Every answer includes direct hyperlinks to the source paragraph on the government website, preventing hallucinated legal advice
- **Bilingual** — Handles both Dutch and English government content
- **Personalized answers** — Users provide personal details (visa type, employment situation, country of origin, etc.) that are used to tailor answers to their specific situation. User profiles are currently stored in browser cookies; a database-backed user system is planned for later

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package manager)
- [Node.js](https://nodejs.org/) (v20+)
- [pnpm](https://pnpm.io/installation)
- [just](https://github.com/casey/just#installation) (command runner)

## Project Structure

```
backend/    → FastAPI API server
frontend/   → Next.js web app
scheduler/  → Scheduled scraping/chunking pipeline
```

All Python packages are managed as a [uv workspace](https://docs.astral.sh/uv/concepts/workspaces/) from the repo root. Each service (`backend/`, `scheduler/`) has its own `pyproject.toml` declaring its dependencies, but they share a single `.venv` and `uv.lock` at the root.

## Why just?

This is a monorepo with multiple languages (Python + Node). There's no single package manager that spans both, so we use [just](https://github.com/casey/just) as a simple command runner to provide a unified interface. Instead of remembering different commands for each service, you run `just <recipe>` from the repo root. Run `just --list` to see all available recipes.

## Setup

```bash
just install
```

This installs all Python dependencies (via uv) and frontend dependencies (via pnpm).

Or manually:

```bash
uv sync --all-packages
cd frontend && pnpm install
```

## Running

```bash
just backend
just frontend
just scheduler
```

Or manually without just:

```bash
uv run --package backend fastapi dev backend/app/main.py
cd frontend && pnpm dev
uv run --package scheduler python3 scheduler/tasks/pipeline.py
```

## Adding Dependencies

```bash
uv add --package backend sqlalchemy
uv add --package scheduler beautifulsoup4
cd frontend && pnpm add axios
```

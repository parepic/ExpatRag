# ExpatRag

A RAG-powered legal and compliance assistant for expats and small businesses in the Netherlands. It translates complex rules from government sources (IND, Belastingdienst, KVK) into plain, actionable answers — with every claim cited back to the official source.

## Key Features

- **Data pipeline** — Walks the IND.nl English HTML sitemap, fetches pages via [scrape.do](https://scrape.do), extracts main text with Unstructured, writes a JSONL snapshot to `data_pipeline/data/documents.jsonl`, upserts into Supabase `sources`, then chunks and embeds into `document_chunks` (OpenAI). Use `just pipeline-full` for the full flow, `just ingest` for ingest by web scraping, `just ingest-from-jsonl` to load from JSONL into `sources`, or `just chunk-pages` for chunking only.
- **RAG-based Q&A** — User questions are embedded, matched against retrieved legal chunks, and answered by an LLM
- **Citation engine** — Every answer includes direct hyperlinks to the source paragraph on the government website, preventing hallucinated legal advice
- **Bilingual** — Handles both Dutch and English government content
- **Personalized answers** — Users provide personal details (visa type, employment situation, country of origin, etc.) that are used to tailor answers to their specific situation. User profiles are currently stored in browser cookies; a database-backed user system is planned for later

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package manager)
- [Node.js](https://nodejs.org/) (v20+)
- [pnpm](https://pnpm.io/installation)
- [just](https://github.com/casey/just#installation) (command runner)
- [Supabase CLI](https://supabase.com/docs/guides/cli) (or use `npx supabase ...`)

## Project Structure

```

backend/        → FastAPI API server
frontend/       → Next.js web app
data_pipeline/  → scrape / extract → Supabase + chunking
supabase/   → Local Supabase config + SQL migrations
```

All Python packages are managed as a [uv workspace](https://docs.astral.sh/uv/concepts/workspaces/) from the repo root. Each package (`backend/`, `data_pipeline/`) has its own `pyproject.toml`, sharing a single `.venv` and `uv.lock` at the root.

## Setup

```bash
just install
```

This installs all Python dependencies (via uv) and frontend dependencies (via pnpm).

## Local Development (Step-by-step)

### 1) Start Supabase (required first)

Supabase is configured from the repository root (`supabase/config.toml`).

```bash
# start local stack (Docker required)
npx supabase start

# print API URL + keys
npx supabase status
```

If this is your first run (or after schema changes), apply migrations:

```bash
npx supabase db reset
```

### 2) Create `.env` at repo root

Use values from `npx supabase status`:

```env
SUPABASE_API_URL=http://127.0.0.1:54321
SUPABASE_SERVICE_KEY=<service_role_key_from_supabase_status> (starts with sb_secret)
OPENAI_API_KEY=<your_openai_key>
LANGSMITH_API_KEY=<your_langsmith_key> (optional: enables LangChain tracing)
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=expatrag
SCRAPE_DO_TOKEN=<your_scrape_do_token> (optional: should be set if you want to use the web scraper)
```

Notes:

- For local Supabase, the `SUPABASE_SERVICE_KEY` should be in the terminal after starting supabase.
- If LangSmith variables are set, backend and pipeline LangChain calls will be traced automatically.

### 3) Run app services (recommended with just)

From the repo root, use separate terminals:

```bash
# terminal 1
just backend

# terminal 2
just frontend

# terminal 3 (pipeline: scrape → JSONL → store → chunk)
just pipeline-full
```

Additional pipeline commands:

```bash
just ingest       # ingest only (scrape → JSONL → store)
just ingest-from-jsonl  # JSONL → store (no HTTP)
just chunk-pages        # chunk only
```

## Running (Manual Commands — Alternative to just)

Use these only if you prefer not to run `just` recipes.

From the repo root:

```bash
npx supabase start
uv run --package backend fastapi dev backend/app/main.py
cd frontend && pnpm dev
uv run --package data-pipeline python3 data_pipeline/pipeline.py
```

Ingest only:

```bash
uv run --package data-pipeline python3 data_pipeline/ingest.py
uv run --package data-pipeline python3 data_pipeline/ingest.py --skip-data-fetch
```

Chunking only:

```bash
uv run --package data-pipeline python3 data_pipeline/chunk.py
```

## Supabase (Useful urls)

Useful URLs after startup:

- API: `http://127.0.0.1:54321`
- Studio: `http://127.0.0.1:54323`

## Backend API Docs

With backend running, open:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Quick Start (Order)

```bash
just install
npx supabase start
npx supabase status
# create .env using the values above
just backend
just frontend
just pipeline-full
```

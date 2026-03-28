# ExpatRag

A RAG-powered legal and compliance assistant for expats and small businesses in the Netherlands. It translates complex rules from government sources (IND, Belastingdienst, KVK) into plain, actionable answers — with every claim cited back to the official source.

## Key Features

- **Data pipeline** — Walks the IND.nl English HTML sitemap, fetches pages via [scrape.do](https://scrape.do), extracts main text with Unstructured, and upserts into the Supabase `sources` table (by `source_url`). Run `just pipeline` for a full run, or `just pipeline-skip` to skip scrape and store when the DB is already filled (for example from `backend/supabase/seed.sql` after `db reset`).
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
data_pipeline/  → IND scrape / extract → Supabase 
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
OPENAI_API_KEY=<your_openai_key> ()
```

Notes:

- For local Supabase, the `SUPABASE_SERVICE_KEY` should be in the terminal after starting supabase.

### 3) Run app services (recommended with just)

From the repo root, use separate terminals:

```bash
# terminal 1
just backend

# terminal 2
just frontend

# terminal 3 (pipeline)
just scheduler
```

Additional scheduler commands:

```bash
just save-pages
just chunk-pages
```

## Running (Manual Commands — Alternative to just)

Use these only if you prefer not to run `just` recipes.

From the repo root:

```bash
npx supabase start
uv run --package backend fastapi dev backend/app/main.py
cd frontend && pnpm dev
uv run --package scheduler python3 -m scheduler.tasks.pipeline
```

Scheduler stages can also run individually:

```bash
uv run --package scheduler python3 -m scheduler.tasks.save_page
uv run --package scheduler python3 -m scheduler.tasks.chunk
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
just pipeline          # scrape → store (see data_pipeline/config.py for limits)
just pipeline-skip-data-fetch     # no HTTP / no Supabase writes (seeded DB)
```

Run backend, frontend, and scheduler in separate terminal sessions.
Or manually without just:

```bash
uv run --package backend fastapi dev backend/app/main.py
cd frontend && pnpm dev
uv run --package data-pipeline python3 data_pipeline/pipeline.py
uv run --package data-pipeline python3 data_pipeline/pipeline.py --skip-data-fetch
```

## Adding Dependencies

```bash
uv add --package backend sqlalchemy
uv add --package data-pipeline httpx
cd frontend && pnpm add axios
```

## Supabase (Local Development)

### 1) Prerequisites

- Docker is running
- Node.js installed (v20+ recommended)

### 2) Initialize and start Supabase

From the backend folder:

```bash
cd backend
npx supabase init       # run once per project
npx supabase start
```

When startup completes, Supabase prints values like:

- **API URL** (use this in .env file): `http://127.0.0.1:54321`
- **Studio URL** (browser UI only): `http://127.0.0.1:54323`

> Important: use the **API URL**, not the Studio URL, for `SUPABASE_API_URL`.

### 3) Configure backend environment

Create/update `backend/.env`:

```env
SUPABASE_API_URL=http://127.0.0.1:54321
SUPABASE_SERVICE_KEY=<secret_key_from_supabase_start_output>
SCRAPE_DO_TOKEN=<token from scrape.do> // NOT NEEDED IF RUNNING --from-file option
```

### 4) Install backend dependencies (if needed)

From repo root (uv workspace):

```bash
uv add --package backend supabase python-dotenv
```

### 5) Create and apply schema changes

From `backend/`:

```bash
supabase migration new <migration_name>
# add SQL to the generated migration file
supabase db reset
```

After reset, open Studio and verify tables in Table Editor.

> If there is already something in `backend/supabase/migrations/<migration>.sql`, then directly run `supabase db reset`

### 6) Run the backend API

From `backend/`:

```bash
uv run uvicorn app.main:app --reload
```

## Configure pipeline environment

Create/update `backend/.env`:

```env
SUPABASE_API_URL=http://127.0.0.1:54321
SUPABASE_SERVICE_KEY=<secret_key_from_supabase_start_output>
SCRAPE_DO_TOKEN=<token from scrape.do> // NOT NEEDED IF RUNNING --from-file option
```

### Useful commands

```bash
# stop local supabase
supabase stop

# start again later
supabase start
```

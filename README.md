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

## Supabase

For now, lets just do a local instance of Supabase.

1. Make sure you have docker running
2. Install node.js
3. cd backend
4. npx supabase init
5. npx supabase start
   then you will see some output in the terminall. copy the Project URL from the APIs section, and then your secret key from the authentication keys section, and add them to the env file
   to stop - supabase stop
   to run next time, personally i dont use npx, i use supabase start
6. uv add supabase python-dotenv

7. supabase migration new <migration_name>
8. Copy all the SQL commands that you made in the migration file
9. supabase db reset
10. now go to the studio link, and see the tables in the table editor.
11. uv run uvicorn app.main:app --reload

Absolutely. Here’s a cleaner, copy-paste replacement for the **Supabase** section.

## Supabase (Local Development)

Use a local Supabase instance for backend development.

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

### Useful commands

```bash
# stop local supabase
supabase stop

# start again later
supabase start
```

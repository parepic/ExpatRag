# ExpatRag

A RAG-powered assistant that helps expats navigate Dutch immigration, visa, and residency rules. It retrieves content from official government sources (IND.nl), answers questions in plain language, and cites the exact source for every claim.

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Node.js](https://nodejs.org/) v20+ and [pnpm](https://pnpm.io/installation)
- [just](https://github.com/casey/just#installation)
- [Supabase CLI](https://supabase.com/docs/guides/cli) (or `npx supabase`)
- Docker (required by Supabase)

## Project Structure

```
backend/         FastAPI API server
frontend/        Next.js web app
data_pipeline/   Scrape → extract → chunk → embed into Supabase
supabase/        Local Supabase config and SQL migrations
```

## Setup

### 1. Install dependencies

```bash
just install
```

### 2. Start Supabase

```bash
npx supabase start
```

On first run, or after schema changes:

```bash
npx supabase db reset
```

### 3. Configure environment variables

**Root `.env`** (used by backend and data pipeline):

```env
SUPABASE_API_URL=http://127.0.0.1:54321
SUPABASE_SERVICE_KEY=          # from `npx supabase status` → service_role key
OPENAI_API_KEY=                # required for embeddings and generation
FRONTEND_URL=http://localhost:3000

# LangSmith — optional for tracing, required for running tests
LANGSMITH_API_KEY=
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=expatrag

# Required only if running the web scraper (not needed for ingest-from-json)
SCRAPE_DO_TOKEN=
```

**`frontend/.env.local`**:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### 4. Run

Open three terminals from the repo root:

```bash
just backend     # FastAPI on :8000
just frontend    # Next.js on :3000
```

The database needs data before the app is useful — see **Data Pipeline** below.

## Data Pipeline

Scrapes IND.nl, stores pages in Supabase, then chunks and embeds them.

```bash
just pipeline-full       # full flow: scrape → store → chunk
just ingest              # scrape → JSONL → store (no chunking)
just ingest-from-json    # load from existing JSONL → store (no HTTP requests)
just chunk-pages         # chunk and embed already-stored pages
```

`data_pipeline/data/documents.jsonl` contains a pre-scraped snapshot, so you can run `just ingest-from-json && just chunk-pages` without needing a `SCRAPE_DO_TOKEN`.

## Testing

Tests run the full RAG pipeline against a golden dataset of 10 Q&A pairs and score results with two LLM-as-judge evaluators:

- **Answer Correctness** — generated answer vs. reference answer
- **Retrieval Relevance** — retrieved chunks vs. the question

Both require LangSmith. On first run the golden dataset is uploaded to LangSmith as `expatrag-golden-v1` and reused on every subsequent run, so results across experiments are comparable. Detailed scores and judge reasoning are visible in the LangSmith UI.

```bash
npx supabase start   # must be running
uv run --package backend pytest backend/tests/test_rag_eval.py -v -s
```

## Useful URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| Supabase Studio | http://127.0.0.1:54323 |
| Supabase API | http://127.0.0.1:54321 |

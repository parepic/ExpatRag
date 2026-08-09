default:
    @just --list

# Install each service's dependencies
install:
    uv sync --project backend
    uv sync --project data_pipeline
    cd frontend && pnpm install

# Run the FastAPI backend
backend:
    uv run --project backend uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload --reload-dir backend/app

# Run the Next.js frontend
frontend:
    cd frontend && pnpm dev

# Full pipeline: scrape pages → store → chunk, then fetch/classify/store news
pipeline-full *ARGS:
    uv run --project data_pipeline python3 data_pipeline/scrape/pipeline.py {{ARGS}}

# Store existing page JSONL → Supabase sources table (no HTTP)
store-pages:
    uv run --project data_pipeline python3 data_pipeline/scrape/ingest.py --skip-data-fetch

# Scrape pages → data_pipeline/data/documents.jsonl (no DB writes)
scrape-pages *ARGS:
    uv run --project data_pipeline python3 data_pipeline/scrape/ingest.py --skip-store {{ARGS}}

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

# IND diff pipeline — six independent stages sharing a run directory (default
# data_pipeline/data/latest/). Each stage reads the previous stage's JSON and writes
# its own, so run them in order (1→6). Pass --data-dir DIR to use a different run.

# Stage 1 — scrape IND pages → <data-dir>/snapshot.json (--limit N caps pages; no DB writes)
reindex *ARGS:
    uv run --project data_pipeline python3 data_pipeline/diff_detector/snapshot.py {{ARGS}}

# Stage 2 — diff corpus (Supabase sources) against snapshot.json → <data-dir>/diff.json
diff *ARGS:
    uv run --project data_pipeline python3 data_pipeline/diff_detector/diff.py {{ARGS}}

# Stage 3 — summarise changed pages with an LLM (reads diff.json) → <data-dir>/summaries.json
summarize *ARGS:
    uv run --project data_pipeline python3 data_pipeline/diff_detector/summarize.py {{ARGS}}

# Stage 4 — classify summaries into a relevance map (reads summaries.json) → <data-dir>/relevance.json
classify *ARGS:
    uv run --project data_pipeline python3 data_pipeline/diff_detector/classify.py {{ARGS}}

# Stage 5 — email opted-in users from relevance.json (--dry-run to skip sending) → <data-dir>/notify_report.json
notify *ARGS:
    uv run --project data_pipeline python3 data_pipeline/diff_detector/notify.py {{ARGS}}

# Stage 6 — apply diff.json to the corpus (upsert/re-chunk/delete) → <data-dir>/corpus_update.json
update-corpus *ARGS:
    uv run --project data_pipeline python3 data_pipeline/diff_detector/update_corpus.py {{ARGS}}

# Run all six IND diff stages in order over one run directory
ind-pipeline *ARGS:
    uv run --project data_pipeline python3 data_pipeline/diff_detector/pipeline.py {{ARGS}}

# Run data pipeline tests
test:
    uv run --project data_pipeline pytest data_pipeline/tests/ -v

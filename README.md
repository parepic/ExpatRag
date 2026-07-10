# ExpatRag

ExpatRag helps expats understand Dutch immigration and residency rules. It
retrieves information from IND.nl, answers questions with citations, and sends
personalised alerts for relevant IND and Dutch news updates.

## Architecture

| Component | Technology | Purpose |
|---|---|---|
| `frontend/` | Next.js | Web application |
| `backend/` | FastAPI | Authentication, chat, and RAG API |
| `data_pipeline/` | Python | Scraping, indexing, news, and notifications |
| `supabase/` | Supabase/PostgreSQL | Users, sessions, content, vectors, and news |

The frontend talks only to the backend. The backend and data pipeline connect
to Supabase with `SUPABASE_API_URL` and `SUPABASE_SERVICE_KEY`.

## Local development

### Requirements

- Docker
- Node.js 20+ and pnpm
- [uv](https://docs.astral.sh/uv/)
- [just](https://github.com/casey/just)
- Supabase CLI, available as `npx supabase`

### 1. Install dependencies

```bash
just install
```

### 2. Start local Supabase

```bash
npx supabase start
npx supabase status
```

Copy the reported API URL and service-role key into the root `.env`:

```env
SUPABASE_API_URL=http://127.0.0.1:54321
SUPABASE_SERVICE_KEY=<local service-role key>
OPENAI_API_KEY=<development key>
FRONTEND_URL=http://localhost:3000
SESSION_COOKIE_SECURE=false
```

Optional integrations:

```env
SCRAPE_DO_TOKEN=        # IND scraping
RESEND_API_KEY=         # Sending notification email
EMAIL_SENDER=           # For example: onboarding@resend.dev
LANGSMITH_API_KEY=      # Tracing and RAG evaluation
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=expatrag
```

The frontend needs `frontend/.env.local`:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### 3. Apply migrations

For a fresh local database:

```bash
npx supabase db reset --no-seed
```

This deletes local data and reapplies every file in `supabase/migrations/` in
timestamp order. To preserve local data and apply only pending migrations:

```bash
npx supabase migration up
```

Do not edit a migration after it has been applied. Create a new one instead:

```bash
npx supabase migration new <description>
```

### 4. Run the application

In separate terminals:

```bash
just backend
just frontend
```

Useful local URLs:

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API documentation | http://localhost:8000/docs |
| Supabase Studio | http://127.0.0.1:54323 |

The local database starts empty. Populate the RAG corpus from the included IND
snapshot:

```bash
just store-pages
just chunk-pages
```

## Data pipeline

Run `just` to list all recipes. The main commands are:

| Command | Action |
|---|---|
| `just pipeline-full` | Scrape/store IND pages, chunk them, then fetch/store news |
| `just scrape-pages` | Scrape IND pages to JSONL without database writes |
| `just store-pages` | Store the included IND JSONL snapshot |
| `just chunk-pages` | Embed sources that do not already have chunks |
| `just fetch-news` | Fetch news to JSONL |
| `just store-news` | Classify and store unseen news |
| `just weekly-news` | Fetch the past week, store news, and email the digest |
| `just send-news` | Email the current handoff file; it may resend old items |
| `just reindex --limit 5` | Create a limited fresh IND snapshot |
| `just diff` | Compare the latest snapshot with stored sources |
| `just test` | Run data-pipeline tests |

Run the IND change notification pipeline directly:

```bash
uv run --project data_pipeline \
  python3 data_pipeline/diff_detector/pipeline.py --dry-run
```

`--dry-run` suppresses email delivery, but the pipeline still refreshes the
indexed corpus. Remove it only when you intend to send notifications.

## Docker development

Supabase remains managed by `npx supabase`; Compose runs the application
containers. Compose automatically changes the Supabase URL to
`http://host.docker.internal:54321` while keeping the remaining values from
`.env`.

```bash
npx supabase start
docker compose up --build backend frontend
```

Run pipeline tasks in containers:

```bash
docker compose run --rm store-pages
docker compose run --rm chunk-pages
docker compose run --rm weekly-news
```

If Docker-created files under `data_pipeline/data/` are not writable by your
host user, repair their ownership once:

```bash
sudo chown -R "$(id -u):$(id -g)" data_pipeline/data
```

## Azure deployment

Production uses Azure Container Apps rather than Docker Compose:

| Azure resource | Image |
|---|---|
| Container App `backend` | `expatrag.azurecr.io/backend:<tag>` |
| Container App `frontend` | `expatrag.azurecr.io/frontend:<tag>` |
| Job `notifications-weekly` | `expatrag.azurecr.io/data-pipeline:<tag>` |

The job runs every Monday at 07:00 UTC and executes both the IND change
notifications and weekly news digest. Production configuration is stored in
Azure Container Apps secrets, not the local `.env`. The commands below assume
these Azure resources already exist.

### Deploy manually

Authenticate and choose an immutable tag:

```bash
TAG=$(date -u +%Y%m%d-%H%M%S)
REGISTRY=expatrag.azurecr.io
RESOURCE_GROUP=expatrag-rg
BACKEND_URL=https://backend.lemonpebble-f3e0ccda.westeurope.azurecontainerapps.io

az acr login --name expatrag
```

Backend:

```bash
docker build -f backend/Dockerfile -t "$REGISTRY/backend:$TAG" backend
docker push "$REGISTRY/backend:$TAG"
az containerapp update \
  --resource-group "$RESOURCE_GROUP" \
  --name backend \
  --image "$REGISTRY/backend:$TAG"
```

Frontend:

```bash
docker build -f frontend/Dockerfile \
  --build-arg NEXT_PUBLIC_BACKEND_URL="$BACKEND_URL" \
  -t "$REGISTRY/frontend:$TAG" \
  frontend
docker push "$REGISTRY/frontend:$TAG"
az containerapp update \
  --resource-group "$RESOURCE_GROUP" \
  --name frontend \
  --image "$REGISTRY/frontend:$TAG"
```

Data pipeline:

```bash
docker build -f data_pipeline/Dockerfile \
  -t "$REGISTRY/data-pipeline:$TAG" \
  data_pipeline
docker push "$REGISTRY/data-pipeline:$TAG"
az containerapp job update \
  --resource-group "$RESOURCE_GROUP" \
  --name notifications-weekly \
  --image "$REGISTRY/data-pipeline:$TAG"
```

### Operate the scheduled job

Run it immediately:

```bash
az containerapp job start \
  --resource-group expatrag-rg \
  --name notifications-weekly
```

Follow the latest execution:

```bash
az containerapp job logs show \
  --resource-group expatrag-rg \
  --name notifications-weekly \
  --container notifications-weekly \
  --follow true \
  --tail 100 \
  --format text
```

List execution history:

```bash
az containerapp job execution list \
  --resource-group expatrag-rg \
  --name notifications-weekly \
  --output table
```

Automatic job retries are disabled because retrying after a partial failure
could send duplicate emails.

## Tests

Data-pipeline tests:

```bash
just test
```

Backend RAG evaluation requires local Supabase data, OpenAI, and LangSmith:

```bash
uv run --project backend pytest backend/tests/test_rag_eval.py -v -s
```

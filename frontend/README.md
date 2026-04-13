# Frontend

Next.js web app for ExpatRag.

## Setup

1. Install dependencies:

```bash
pnpm install
```

2. Create a local env file at `frontend/.env.local`:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

This is required. The frontend calls the backend through `NEXT_PUBLIC_BACKEND_URL`, so if `.env.local` is missing the app will start but auth and chat requests will fail.

3. Start the dev server:

```bash
pnpm dev
```

Open `http://localhost:3000`.

## Available Commands

```bash
pnpm dev
pnpm build
pnpm start
pnpm lint
pnpm test
pnpm test:watch
pnpm smoke:auth
```

## Notes

- Run these commands from `frontend/`.
- The backend is expected to be running locally at `http://localhost:8000` unless you point `NEXT_PUBLIC_BACKEND_URL` somewhere else.
- `pnpm smoke:auth` also needs a backend URL. It reads `BACKEND_URL` first, then falls back to `NEXT_PUBLIC_BACKEND_URL`.

# CLAUDE.md
This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.


## Working Style
- I am not a Next.js expert. When adding or changing code, briefly explain what was changed and why in plain terms — including any Next.js concepts involved (e.g. Server Components vs Client Components, App Router conventions, etc.).


## Architecture
- **Framework**: Next.js 16 with App Router (`src/app/`)
- **Styling**: Tailwind CSS v4 (configured via PostCSS, no `tailwind.config.*` file — uses CSS-first config in `globals.css`)
- **Language**: TypeScript with strict mode; path alias `@/*` → `./src/*`
- **Turbopack**: Enabled for dev, configured in `next.config.ts` with repo root as the Turbopack root path


## Frontend Commands
All commands run from `frontend/` using pnpm:

```bash
pnpm dev      # start dev server (uses Turbopack)
pnpm build    # production build
pnpm start    # start production server
pnpm lint     # run ESLint
```


## Adding Dependencies
```bash
pnpm add <package>          # runtime dependency
pnpm add -D <package>       # dev dependency
```

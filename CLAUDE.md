# CLAUDE.md
This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.


## Working Style
- I am a beginner with Claude Code. When relevant, suggest useful Claude Code commands or workflows (e.g. when to use /compact, how to give feedback, how to scope requests, how to delegate work to sub-agents).
- Write tests whenever possible for new functionality.

My remaing personal preferences are stored in @~/.claude/personal-instructions.md


## Monorepo Context
This is the `frontend/` service of the ExpatRag monorepo. The repo root contains:
- `backend/` — FastAPI API server (Python, managed with uv)
- `frontend/` — Next.js web app (this directory), with more instructions in @frontend/CLAUDE.md
- `scheduler/` — Scheduled scraping/chunking pipeline (Python, managed with uv)

From the **repo root**, use `just` recipes for cross-service commands
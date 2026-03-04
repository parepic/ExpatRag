# Expat & SME Compliance Copilot

A RAG-powered Q&A system for Dutch immigration and residency information, built on data scraped from the IND (Immigration and Naturalisation Service) website.

## Setup

### 1. Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Ollama (local LLM + embeddings)

```bash
brew install ollama
ollama pull llama3.2
ollama pull nomic-embed-text
```

Make sure the Ollama server is running (`ollama serve`) before using ingest or query.

## Usage

### Scrape documents

```bash
python3 src/pipeline.py
```

Output is written to `data/documents.jsonl`.

### Ingest into vector store

```bash
python3 -m src.ingest
```

Chunks documents, embeds them with `nomic-embed-text`, and stores in ChromaDB at `data/chromadb/`.

### Query (interactive)
****
```bash
python3 -m src.query
```

Asks for your question, retrieves relevant chunks, and answers using `llama3.2` with source citations.

## Configuration

Edit `src/config.py` to adjust settings:

- `PAGE_LIMIT` — set to a number to limit pages during development, `None` for all
- `REQUEST_DELAY` — seconds between HTTP requests (default 1.5)
- `MAX_RETRIES` — retry count on transient failures (default 3)
- `OLLAMA_LLM_MODEL` — Ollama model for answering (default `llama3.2`)
- `OLLAMA_EMBED_MODEL` — Ollama model for embeddings (default `nomic-embed-text`)
- `CHUNK_SIZE` — target chunk size in characters (default 500)

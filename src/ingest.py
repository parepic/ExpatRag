"""Load documents, chunk by element structure, embed with Ollama, store in ChromaDB."""

import json
import hashlib
import sys

import chromadb
import ollama

from src.config import CHROMADB_DIR, CHUNK_SIZE, OLLAMA_EMBED_MODEL, OUTPUT_DIR


def _chunk_elements(elements: list[dict], max_chars: int = CHUNK_SIZE) -> list[dict]:
    """Split a document's elements into section-aware chunks.

    Groups elements by Title boundaries.  Each chunk gets the section
    heading prepended so it's self-contained for retrieval.
    """
    sections: list[dict] = []
    current_heading = ""
    current_texts: list[str] = []

    def _flush():
        if not current_texts:
            return
        body = "\n".join(current_texts)
        sections.append({"section": current_heading, "text": body})

    for el in elements:
        if el["type"] == "Title":
            _flush()
            current_heading = el["text"]
            current_texts = []
        else:
            text = el["text"].strip()
            if text:
                current_texts.append(text)

    _flush()

    chunks: list[dict] = []
    for sec in sections:
        prefix = f"## {sec['section']}\n" if sec["section"] else ""
        text = prefix + sec["text"]

        if len(text) <= max_chars:
            if len(text) < 50 and chunks:
                prev = chunks[-1]
                prev["text"] += "\n" + text
                continue
            chunks.append({"section": sec["section"], "text": text})
        else:
            sentences = _split_sentences(sec["text"])
            buf = prefix
            for sentence in sentences:
                if len(buf) + len(sentence) > max_chars and len(buf) > len(prefix):
                    chunks.append(
                        {"section": sec["section"], "text": buf.rstrip()})
                    buf = prefix + sentence
                else:
                    buf += sentence
            if buf.strip() and buf != prefix:
                chunks.append(
                    {"section": sec["section"], "text": buf.rstrip()})

    return chunks


def _split_sentences(text: str) -> list[str]:
    """Rough sentence split that keeps the delimiter attached."""
    result: list[str] = []
    current = ""
    for char in text:
        current += char
        if char in ".!?\n":
            result.append(current)
            current = ""
    if current:
        result.append(current)
    return result


def _chunk_id(url: str, idx: int) -> str:
    return hashlib.sha256(f"{url}::{idx}".encode()).hexdigest()[:16]


def load_documents() -> list[dict]:
    path = OUTPUT_DIR / "documents.jsonl"
    if not path.exists():
        sys.exit(
            f"No documents found at {path}. Run the scrape pipeline first.")
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def ingest():
    docs = load_documents()
    print(f"Loaded {len(docs)} documents from documents.jsonl")

    all_chunks: list[dict] = []
    for doc in docs:
        chunks = _chunk_elements(doc.get("elements", []))
        for i, chunk in enumerate(chunks):
            chunk["url"] = doc["url"]
            chunk["title"] = doc["title"]
            chunk["category"] = doc["category"]
            chunk["chunk_id"] = _chunk_id(doc["url"], i)
        all_chunks.extend(chunks)

    print(f"Created {len(all_chunks)} chunks")

    if not all_chunks:
        sys.exit("No chunks to ingest.")

    print(f"Embedding with {OLLAMA_EMBED_MODEL}...")
    texts = [c["text"] for c in all_chunks]

    batch_size = 64
    all_embeddings: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i: i + batch_size]
        response = ollama.embed(model=OLLAMA_EMBED_MODEL, input=batch)
        all_embeddings.extend(response["embeddings"])
        print(f"  Embedded {min(i + batch_size, len(texts))}/{len(texts)}")

    CHROMADB_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMADB_DIR))
    collection = client.get_or_create_collection(
        name="ind_documents",
        metadata={"hnsw:space": "cosine"},
    )

    collection.upsert(
        ids=[c["chunk_id"] for c in all_chunks],
        embeddings=all_embeddings,
        documents=texts,
        metadatas=[
            {
                "url": c["url"],
                "title": c["title"],
                "category": c["category"],
                "section": c["section"],
            }
            for c in all_chunks
        ],
    )

    print(f"Stored {len(all_chunks)} chunks in ChromaDB at {CHROMADB_DIR}")


if __name__ == "__main__":
    ingest()

"""Interactive RAG query loop: retrieve context from ChromaDB, answer with Ollama."""

import sys

import chromadb
import ollama

from src.config import CHROMADB_DIR, OLLAMA_EMBED_MODEL, OLLAMA_LLM_MODEL

TOP_K = 10

SYSTEM_PROMPT = """\
You are an assistant that helps expats with questions about \
Dutch immigration and residency, based on information from the IND \
(Immigration and Naturalisation Service) website.

Answer the user's question using ONLY the provided context. If the \
context does not contain enough information, say so honestly. \
Important: Always cite the source URL for each piece of information you use."""


def _build_context(results: dict) -> str:
    parts: list[str] = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        source = f"[{meta['title']} — {meta['section']}]({meta['url']})"
        parts.append(f"Source: {source}\n{doc}")
    return "\n\n---\n\n".join(parts)


def query_loop():
    if not CHROMADB_DIR.exists():
        sys.exit(
            "ChromaDB not found. Run ingestion first: python3 -m src.ingest"
        )

    client = chromadb.PersistentClient(path=str(CHROMADB_DIR))
    collection = client.get_collection("ind_documents")

    print(f"RAG ready — {collection.count()} chunks indexed")
    print(f"LLM: {OLLAMA_LLM_MODEL}  |  Embeddings: {OLLAMA_EMBED_MODEL}")
    print('Type your question (or "quit" to exit)\n')

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not question or question.lower() in ("quit", "exit", "q"):
            print("Bye!")
            break

        query_embedding = ollama.embed(
            model=OLLAMA_EMBED_MODEL, input=[question]
        )["embeddings"][0]

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=TOP_K,
        )

        context = _build_context(results)

        prompt = f"Context:\n{context}\n\nQuestion: {question}"

        print("\nAssistant: ", end="", flush=True)

        stream = ollama.chat(
            model=OLLAMA_LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            stream=True,
        )

        for chunk in stream:
            print(chunk["message"]["content"], end="", flush=True)

        print("\n")


if __name__ == "__main__":
    query_loop()

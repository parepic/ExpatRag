"""Chunk source content and store embeddings in `document_chunks`."""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Any

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from supabase import Client

from scheduler.core.config import (
    CHUNK_DRY_RUN,
    CHUNK_EMBEDDING_MODEL,
    CHUNK_LIMIT,
    CHUNK_OVERLAP,
    CHUNK_OVERRIDE_CHUNKS,
    CHUNK_SIZE,
    CHUNK_SOURCE_ID,
    CHUNK_DB_BATCH_SIZE,
)
from scheduler.core.embeddings import get_embeddings
from scheduler.core.supabase_client import get_supabase_client


@dataclass(slots=True)
class ChunkStats:
    """Summary of processed sources and stored chunks for one chunking run."""

    sources_processed: int = 0
    sources_skipped: int = 0
    chunks_saved: int = 0


def batched(items: list[dict[str, Any]], batch_size: int = CHUNK_DB_BATCH_SIZE) -> Iterator[list[dict[str, Any]]]:
    """Yield lists in database-friendly batch sizes."""
    for start in range(0, len(items), batch_size):
        yield items[start : start + batch_size]


def iter_sources(
    supabase: Client,
    *,
    source_id: str | None = None,
    limit: int | None = None,
    page_size: int = 200,
) -> Iterable[dict[str, Any]]:
    """Stream source rows from Supabase, optionally filtered or limited."""
    if source_id:
        response = (
            supabase.table("sources")
            .select("id, title, source_url, content, metadata, type, last_synced_at")
            .eq("id", source_id)
            .limit(1)
            .execute()
        )
        yield from response.data or []
        return

    offset = 0
    yielded = 0

    while True:
        upper_bound = offset + page_size - 1
        response = (
            supabase.table("sources")
            .select("id, title, source_url, content, metadata, type, last_synced_at")
            .order("created_at")
            .range(offset, upper_bound)
            .execute()
        )
        rows = response.data or []
        if not rows:
            break

        for row in rows:
            if limit is not None and yielded >= limit:
                return
            yield row
            yielded += 1

        offset += page_size


def extract_source_text(source: dict[str, Any]) -> str:
    """Choose the best available text body from a source row."""
    content = str(source.get("content") or "").strip()
    if content:
        return content

    metadata = source.get("metadata") or {}

    elements = metadata.get("elements") or []
    if isinstance(elements, list):
        element_texts = [
            str(element.get("text", "")).strip()
            for element in elements
            if isinstance(element, dict) and str(element.get("text", "")).strip()
        ]
        if element_texts:
            return "\n\n".join(element_texts)

    title = str(source.get("title") or "").strip()
    return title


def normalize_chunk_text(text: str) -> str:
    """Collapse whitespace so stored chunk content stays compact and searchable."""
    return re.sub(r"\s+", " ", text).strip()


def build_source_document(source: dict[str, Any]) -> Document | None:
    """Convert a source row into a LangChain `Document` for chunking."""
    text = extract_source_text(source)
    if not text:
        return None

    metadata = source.get("metadata") or {}
    return Document(
        page_content=text,
        metadata={
            "source_id": source["id"],
            "title": source.get("title"),
            "source_url": source.get("source_url"),
            "source_type": source.get("type"),
            "category": metadata.get("category"),
            "fetch_date": metadata.get("fetch_date"),
            "last_synced_at": source.get("last_synced_at"),
        },
    )


def build_chunk_payloads(
    source: dict[str, Any],
    split_documents: list[Document],
    *,
    chunk_size: int,
    chunk_overlap: int,
    embedding_model: str,
) -> list[dict[str, Any]]:
    """Build `document_chunks` insert payloads with embeddings for one source."""
    embeddings = get_embeddings(embedding_model)
    chunk_texts = [document.page_content for document in split_documents]
    vectors = embeddings.embed_documents(chunk_texts)

    payloads: list[dict[str, Any]] = []
    for index, (document, vector) in enumerate(zip(split_documents, vectors, strict=True)):
        original_content = document.page_content.strip()
        normalized_content = normalize_chunk_text(original_content)
        if not normalized_content:
            continue

        payloads.append(
            {
                "source_id": source["id"],
                "content": normalized_content,
                "chunk_index": index,
                "page_number": None,
                "char_count": len(original_content),
                "original_content": original_content,
                "metadata": {
                    **document.metadata,
                    "chunking": {
                        "strategy": "recursive_character_text_splitter",
                        "chunk_size": chunk_size,
                        "chunk_overlap": chunk_overlap,
                        "embedding_model": embedding_model,
                    },
                },
                "embedding": vector,
            }
        )

    return payloads


def replace_source_chunks(supabase: Client, source_id: str, payloads: list[dict[str, Any]]) -> None:
    """Replace all chunks for one source with freshly generated chunk rows."""
    supabase.table("document_chunks").delete().eq("source_id", source_id).execute()
    for batch in batched(payloads):
        supabase.table("document_chunks").insert(batch).execute()


def source_has_chunks(supabase: Client, source_id: str) -> bool:
    """Return whether at least one chunk already exists for the given source id."""
    response = (
        supabase.table("document_chunks")
        .select("id")
        .eq("source_id", source_id)
        .limit(1)
        .execute()
    )
    return bool(response.data)


def chunk_sources(
    *,
    source_id: str | None = CHUNK_SOURCE_ID,
    limit: int | None = CHUNK_LIMIT,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
    embedding_model: str = CHUNK_EMBEDDING_MODEL,
    override_chunks: bool = CHUNK_OVERRIDE_CHUNKS,
    dry_run: bool = CHUNK_DRY_RUN,
) -> ChunkStats:
    """Read source rows, split them into chunks, and persist chunk embeddings."""
    supabase = get_supabase_client()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    stats = ChunkStats()

    for source in iter_sources(supabase, source_id=source_id, limit=limit):
        has_existing_chunks = source_has_chunks(supabase, source["id"])
        if has_existing_chunks and not override_chunks:
            stats.sources_skipped += 1
            print(
                f"Skipping source {source['id']}: chunks already exist and CHUNK_OVERRIDE_CHUNKS is False"
            )
            continue

        source_document = build_source_document(source)
        if source_document is None:
            stats.sources_skipped += 1
            print(f"Skipping source {source['id']}: no content available")
            continue

        split_documents = splitter.split_documents([source_document])
        if not split_documents:
            stats.sources_skipped += 1
            print(f"Skipping source {source['id']}: chunk splitter returned no chunks")
            continue

        if dry_run:
            stats.sources_processed += 1
            stats.chunks_saved += len(split_documents)
            action = "override" if has_existing_chunks else "create"
            print(
                f"[dry-run] source {source['id']} ({action}) -> {len(split_documents)} chunks "
                f"from {source.get('source_url')}"
            )
            continue

        payloads = build_chunk_payloads(
            source,
            split_documents,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            embedding_model=embedding_model,
        )
        replace_source_chunks(supabase, source["id"], payloads)

        stats.sources_processed += 1
        stats.chunks_saved += len(payloads)

    return stats


def main() -> None:
    """Run the chunking task using values from scheduler config."""
    stats = chunk_sources()

    if CHUNK_DRY_RUN:
        print(
            "Dry run completed: "
            f"sources_processed={stats.sources_processed}, "
            f"sources_skipped={stats.sources_skipped}, "
            f"chunks={stats.chunks_saved}"
        )
        return

    print(
        "Chunking completed: "
        f"sources_processed={stats.sources_processed}, "
        f"sources_skipped={stats.sources_skipped}, "
        f"chunks_saved={stats.chunks_saved}"
    )


if __name__ == "__main__":
    main()
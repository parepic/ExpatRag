-- Similarity search function for RAG retrieval over document_chunks.
-- Uses inner product (vector_ip_ops) to match the HNSW index on the embedding column.

CREATE OR REPLACE FUNCTION match_document_chunks(
    query_embedding  VECTOR(1536),
    match_threshold  FLOAT  DEFAULT 0.7,
    match_count      INT    DEFAULT 5
)
RETURNS TABLE (
    id               UUID,
    source_id        UUID,
    content          TEXT,
    chunk_index      INTEGER,
    page_number      INTEGER,
    metadata         JSONB,
    source_title     TEXT,
    source_url       TEXT,
    similarity       FLOAT
)
LANGUAGE sql STABLE
AS $$
    SELECT
        dc.id,
        dc.source_id,
        dc.content,
        dc.chunk_index,
        dc.page_number,
        dc.metadata,
        s.title       AS source_title,
        s.source_url  AS source_url,
        (dc.embedding <#> query_embedding) * -1 AS similarity
    FROM document_chunks dc
    LEFT JOIN sources s ON s.id = dc.source_id
    WHERE (dc.embedding <#> query_embedding) * -1 >= match_threshold
    ORDER BY dc.embedding <#> query_embedding
    LIMIT match_count;
$$;

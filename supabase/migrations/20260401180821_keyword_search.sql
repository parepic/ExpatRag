-- Keyword Search --

CREATE OR REPLACE FUNCTION keyword_search_document_chunks(
    query_text text, 
    match_count integer DEFAULT 20
)
RETURNS TABLE(
    id               UUID,
    source_id        UUID,
    content          TEXT,
    chunk_index      INTEGER,
    page_number      INTEGER,
    metadata         JSONB,
    source_title     TEXT,
    source_url       TEXT
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
    s.source_url  AS source_url
FROM
    document_chunks dc
LEFT JOIN 
    sources s ON s.id = dc.source_id
WHERE
    dc.fts @@ websearch_to_tsquery('english', query_text)
ORDER BY 
    ts_rank_cd(dc.fts, websearch_to_tsquery('english', query_text)) DESC
LIMIT 
    match_count;
$$;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

-- --- TABLES ---

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    nationality TEXT,
    purpose_of_stay TEXT,
    reason_for_visit TEXT,
    employment_status TEXT,
    registration_status TEXT,
    has_fiscal_partner BOOLEAN,
    salary_band TEXT,
    age_bracket_under_30 BOOLEAN,
    prior_nl_residency BOOLEAN,
    languages TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    content TEXT,
    role TEXT,
    citations JSONB,
    trace_id TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE project_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    embedding_model TEXT,
    rag_strategy TEXT,
    agent_type TEXT,
    chunks_per_search INTEGER,
    final_context_size INTEGER,
    similarity_threshold DECIMAL,
    number_of_queries INTEGER,
    reranking_enabled BOOLEAN,
    reranking_model TEXT,
    vector_weight DECIMAL,
    keyword_weight DECIMAL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT,
    source_url TEXT,
    metadata JSONB,
    type TEXT,
    last_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    content TEXT,
    chunk_index INTEGER,
    page_number INTEGER,
    char_count INTEGER,
    original_content TEXT,
    metadata JSONB,
    embedding VECTOR(1536), -- Adjust dimension (e.g., 1536 for OpenAI) as needed
    fts tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- --- INDEXES ---

CREATE INDEX document_chunks_fts_idx ON document_chunks USING gin (fts);

CREATE INDEX document_chunks_embeddinghnsw_idx ON document_chunks 
USING hnsw (embedding vector_ip_ops);

-- --- MAINTENANCE ---

-- To permanently remove chats deleted more than 30 days ago:
-- DELETE FROM chats WHERE deleted_at < now() - INTERVAL '30 days';

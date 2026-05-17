-- Patty Watch alert-worthy news items selected from RSS/news feeds.

CREATE TABLE news_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    source_url TEXT NOT NULL UNIQUE,
    summary TEXT,
    published_at TIMESTAMPTZ,
    alert_reason TEXT,
    metadata JSONB,
    last_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);
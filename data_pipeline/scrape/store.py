"""
Upsert scraped documents into the Supabase `sources` table.

Each document is matched by `source_url` — existing rows are updated,
new URLs are inserted. This makes the pipeline safely re-runnable.
"""

from datetime import datetime, timezone

from lib.supabase_client import get_supabase_client


def store_documents(documents: list[dict]) -> int:
    """Upsert documents into the `sources` table. Returns the number of rows written."""
    client = get_supabase_client()
    now = datetime.now(timezone.utc).isoformat()

    rows = [
        {
            "title": doc["title"],
            "source_url": doc["url"],
            "type": "webpage",
            "content": doc["content"],
            "metadata": {
                "category": doc.get("category"),
                "elements": doc.get("elements"),
                "fetch_date": doc.get("fetch_date"),
            },
            "last_synced_at": now,
        }
        for doc in documents
    ]

    BATCH_SIZE = 50
    written = 0

    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i: i + BATCH_SIZE]
        client.table("sources").upsert(
            batch, on_conflict="source_url"
        ).execute()
        written += len(batch)
        print(f"  Upserted {written}/{len(rows)} rows")

    print(f"Stored {written} documents in sources table")
    return written

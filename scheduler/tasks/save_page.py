"""Load demo source pages into the `sources` table."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from supabase import Client

from scheduler.core.config import (
    REPO_ROOT,
    SAVE_PAGE_DRY_RUN,
    SAVE_PAGE_INPUT_PATH,
    SAVE_PAGE_LIMIT,
    SAVE_PAGE_SOURCE_TYPE,
)
from scheduler.core.supabase_client import get_supabase_client



@dataclass(slots=True)
class SavePageStats:
    """Summary of rows inserted, updated, or skipped during source sync."""

    inserted: int = 0
    updated: int = 0
    skipped: int = 0


def iter_documents(input_path: Path) -> Iterable[dict[str, Any]]:
    """Yield JSON objects from the configured JSONL input file."""
    with input_path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue

            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number} of {input_path}"
                ) from exc

            if not isinstance(payload, dict):
                raise ValueError(
                    f"Expected a JSON object on line {line_number} of {input_path}"
                )

            yield payload


def build_last_synced_at(fetch_date: str | None) -> str:
    """Convert a fetch date string into a timezone-aware ISO timestamp."""
    if not fetch_date:
        return datetime.now(UTC).isoformat()

    parsed_date = datetime.fromisoformat(fetch_date)
    if parsed_date.tzinfo is None:
        parsed_date = parsed_date.replace(tzinfo=UTC)

    return parsed_date.isoformat()


def build_source_payload(document: dict[str, Any], *, source_file: Path) -> dict[str, Any]:
    """Map a scraped document record into the `sources` table payload shape."""
    source_url = str(document.get("url") or "").strip()
    title = str(document.get("title") or "").strip() or source_url
    content = str(document.get("content") or "").strip()
    fetch_date = document.get("fetch_date")

    if not source_url:
        raise ValueError("Document is missing a url field")

    metadata = {
        "category": document.get("category"),
        "elements": document.get("elements") or [],
        "fetch_date": fetch_date,
        "ingestion": {
            "mode": "demo_jsonl",
            "source_file": str(source_file.relative_to(REPO_ROOT)),
        },
    }

    return {
        "title": title,
        "source_url": source_url,
        "type": SAVE_PAGE_SOURCE_TYPE,
        "content": content,
        "last_synced_at": build_last_synced_at(fetch_date if isinstance(fetch_date, str) else None),
        "metadata": metadata,
    }


def upsert_source(supabase: Client, payload: dict[str, Any]) -> str:
    """Insert a new source or update an existing one matched by `source_url`."""
    existing = (
        supabase.table("sources")
        .select("id")
        .eq("source_url", payload["source_url"])
        .limit(1)
        .execute()
    )

    if existing.data:
        source_id = existing.data[0]["id"]
        supabase.table("sources").update(payload).eq("id", source_id).execute()
        return "updated"

    supabase.table("sources").insert(payload).execute()
    return "inserted"


def save_pages(
    *,
    input_path: Path = SAVE_PAGE_INPUT_PATH,
    limit: int | None = SAVE_PAGE_LIMIT,
    dry_run: bool = SAVE_PAGE_DRY_RUN,
) -> SavePageStats:
    """Sync source records from the JSONL file into the database."""
    input_path = input_path.resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")

    supabase = None if dry_run else get_supabase_client()
    stats = SavePageStats()

    for index, document in enumerate(iter_documents(input_path), start=1):
        if limit is not None and index > limit:
            break

        try:
            payload = build_source_payload(document, source_file=input_path)
        except ValueError as exc:
            stats.skipped += 1
            print(f"Skipping record {index}: {exc}")
            continue

        if dry_run:
            print(f"[dry-run] would sync {payload['source_url']}")
            continue

        result = upsert_source(supabase, payload)
        if result == "inserted":
            stats.inserted += 1
        else:
            stats.updated += 1

    return stats


def main() -> None:
    """Run the save-page task using values from scheduler config."""
    stats = save_pages()

    if SAVE_PAGE_DRY_RUN:
        print("Dry run completed.")
        return

    print(
        "Finished syncing sources: "
        f"inserted={stats.inserted}, updated={stats.updated}, skipped={stats.skipped}"
    )


if __name__ == "__main__":
    main()
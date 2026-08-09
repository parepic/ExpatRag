"""Stage 6 — update corpus: apply <data_dir>/diff.json to Supabase so the same
changes are not notified again, then write <data_dir>/corpus_update.json.

CHANGED/ADDED pages are upserted into `sources` and re-chunked; REMOVED pages are
deleted. Reads only diff.json (enriched with title + source + new_content by stage 2)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_pipeline_root = Path(__file__).resolve().parents[1]
if str(_pipeline_root) not in sys.path:
    sys.path.insert(0, str(_pipeline_root))

from diff_detector.diff import load_diffs
from lib.config import CORPUS_UPDATE_FILENAME, DIFF_FILENAME, ensure_run_dir
from lib.supabase_client import get_supabase_client
from scrape.chunk import chunk_sources
from scrape.store import store_documents


def run_update_corpus_stage(
    data_dir: Path | str | None = None,
    client: Any | None = None,
) -> dict:
    """Apply <data_dir>/diff.json to the corpus and write <data_dir>/corpus_update.json."""
    run_dir = ensure_run_dir(data_dir)
    diffs = load_diffs(run_dir / DIFF_FILENAME)
    client = client or get_supabase_client()

    changed = [d for d in diffs if d.change_type in ("CHANGED", "ADDED")]
    removed = [d for d in diffs if d.change_type == "REMOVED"]
    changed_urls = [d.url for d in changed]
    removed_urls = [d.url for d in removed]

    # Upsert changed/added pages back into the corpus. `source` sets the `type` column:
    # without it an ADDED page would be inserted with a null type, drop out of
    # load_corpus's site filter, and be re-detected as ADDED on every later run.
    changed_docs = [
        {
            "url": d.url,
            "title": d.title,
            "content": d.new_content,
            "source": d.source,
        }
        for d in changed
    ]
    if changed_docs:
        store_documents(changed_docs)

    # Re-chunk each updated source by its DB id so the RAG index stays current.
    rechunked: list[str] = []
    if changed_urls:
        rows = (
            client.table("sources")
            .select("id, source_url")
            .in_("source_url", changed_urls)
            .execute()
            .data
            or []
        )
        for row in rows:
            chunk_sources(source_id=row["id"], override_chunks=True)
            rechunked.append(row["id"])

    # Delete removed pages from the corpus.
    if removed_urls:
        client.table("sources").delete().in_("source_url", removed_urls).execute()
        print(f"  Removed {len(removed_urls)} deleted source(s)")

    update = {"updated": changed_urls, "removed": removed_urls, "rechunked": rechunked}
    output_path = run_dir / CORPUS_UPDATE_FILENAME
    output_path.write_text(json.dumps(update, indent=2, ensure_ascii=False))
    print(
        f"Corpus update written to {output_path} "
        f"(updated={len(changed_urls)}, removed={len(removed_urls)}, rechunked={len(rechunked)})"
    )
    return update


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Stage 6 — apply <data_dir>/diff.json to the Supabase corpus "
            "(upsert + re-chunk changed, delete removed) and write corpus_update.json."
        )
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Run directory holding diff.json (default: data/latest/).",
    )
    args = parser.parse_args()
    run_update_corpus_stage(data_dir=args.data_dir)


if __name__ == "__main__":
    main()

"""Read and write the documents JSONL snapshot (extractor-shaped dicts per line)."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any


def iter_documents(path: Path) -> Iterable[dict[str, Any]]:
    """Yield one dict per non-empty line; raise ValueError on invalid JSON or non-object lines."""
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number} of {path}"
                ) from exc
            if not isinstance(payload, dict):
                raise ValueError(
                    f"Expected a JSON object on line {line_number} of {path}"
                )
            yield payload


def load_documents_from_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load all document records from a JSONL file."""
    if not path.exists():
        raise FileNotFoundError(f"JSONL file does not exist: {path}")
    return list(iter_documents(path))


def write_documents_jsonl(path: Path, documents: list[dict[str, Any]]) -> None:
    """Write documents as UTF-8 JSONL (one object per line)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for doc in documents:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")
    print(f"Wrote {len(documents)} documents to {path}")

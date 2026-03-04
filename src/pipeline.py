import json
import sys

from src.config import OUTPUT_DIR, PAGE_LIMIT
from src.scraper.discovery import discover_pages
from src.scraper.extractor import extract_documents
from src.scraper.fetcher import fetch_pages


def run():
    print("Starting IND data pipeline")

    pages = discover_pages()

    if PAGE_LIMIT is not None:
        pages = pages[:PAGE_LIMIT]
        print(f"Limited to {PAGE_LIMIT} pages")

    fetched = fetch_pages(pages)
    documents = extract_documents(fetched)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "documents.jsonl"

    with open(output_path, "w", encoding="utf-8") as f:
        for doc in documents:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    print(f"Wrote {len(documents)} documents to {output_path}")


if __name__ == "__main__":
    sys.exit(run() or 0)

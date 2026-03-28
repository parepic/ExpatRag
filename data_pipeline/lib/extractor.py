from datetime import date

from unstructured.partition.html import partition_html


def extract_documents(fetched_pages: list[dict]) -> list[dict]:
    """Extract structured documents from fetched HTML pages using unstructured."""
    documents = []
    today = date.today().isoformat()

    for i, page in enumerate(fetched_pages):
        url = page["url"]
        print(f"[{i + 1}/{len(fetched_pages)}] Extracting {url}")

        try:
            elements = partition_html(text=page["html"])
        except Exception as e:
            print(f"  Failed to extract {url}: {e}")
            continue

        if not elements:
            print(f"  No elements found for {url}, skipping")
            continue

        title = next(
            (str(el) for el in elements if el.category == "Title"),
            "Untitled",
        )

        element_dicts = [
            {"type": el.category, "text": str(el)}
            for el in elements
        ]

        content = "\n\n".join(str(el) for el in elements)

        documents.append({
            "url": url,
            "title": title,
            "category": page["category"],
            "content": content,
            "elements": element_dicts,
            "fetch_date": today,
        })

    print(f"Extracted {len(documents)} documents")
    return documents

"""Tests for stage 6 (update_corpus): applying diff.json to the Supabase corpus."""

from types import SimpleNamespace

import diff_detector.update_corpus as update_corpus_module
from diff_detector.diff import PageDiff, write_diffs
from diff_detector.update_corpus import run_update_corpus_stage


class FakeSourcesQuery:
    def __init__(self):
        self.deleted_urls = []

    def select(self, *_args):
        return self

    def delete(self):
        return self

    def in_(self, _column, values):
        self.values = values
        return self

    def execute(self):
        if getattr(self, "values", None) == ["removed-url"]:
            self.deleted_urls.extend(self.values)
            return SimpleNamespace(data=[])
        return SimpleNamespace(data=[{"id": "source-id", "source_url": "changed-url"}])


class FakeClient:
    def __init__(self):
        self.sources = FakeSourcesQuery()

    def table(self, name):
        assert name == "sources"
        return self.sources


def test_update_corpus_refreshes_changed_and_removed_sources(monkeypatch, tmp_path):
    diffs = [
        PageDiff(
            url="changed-url",
            change_type="CHANGED",
            unified_diff="",
            content="new body",
            old_content="old body",
            new_content="new body",
            title="Changed",
            source="ind.nl",
        ),
        PageDiff(
            url="removed-url",
            change_type="REMOVED",
            unified_diff="",
            content="old body",
            old_content="old body",
            new_content="",
            title="",
        ),
    ]
    write_diffs(diffs, tmp_path / "diff.json")

    stored: list[dict] = []
    chunked: list[dict] = []
    monkeypatch.setattr(update_corpus_module, "store_documents", lambda docs: stored.extend(docs))
    monkeypatch.setattr(update_corpus_module, "chunk_sources", lambda **kwargs: chunked.append(kwargs))

    client = FakeClient()
    result = run_update_corpus_stage(data_dir=tmp_path, client=client)

    # `source` must reach store_documents — it becomes the row's `type`, which
    # load_corpus filters on.
    assert stored == [
        {
            "url": "changed-url",
            "title": "Changed",
            "content": "new body",
            "source": "ind.nl",
        }
    ]
    assert chunked == [{"source_id": "source-id", "override_chunks": True}]
    assert client.sources.deleted_urls == ["removed-url"]
    assert result == {
        "updated": ["changed-url"],
        "removed": ["removed-url"],
        "rechunked": ["source-id"],
    }

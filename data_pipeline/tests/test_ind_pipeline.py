from pathlib import Path
from types import SimpleNamespace

from diff_detector.pipeline import run_ind_diff_pipeline


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


def test_ind_pipeline_refreshes_changed_and_removed_sources(monkeypatch):
    client = FakeClient()
    diffs = [
        SimpleNamespace(url="changed-url", change_type="CHANGED"),
        SimpleNamespace(url="removed-url", change_type="REMOVED"),
    ]
    stored = []
    chunked = []

    monkeypatch.setattr("diff_detector.pipeline.get_supabase_client", lambda: client)
    monkeypatch.setattr(
        "diff_detector.pipeline.snapshot", lambda limit=None: Path("snapshot.json")
    )
    monkeypatch.setattr("diff_detector.pipeline.load_corpus", lambda _client: {})
    monkeypatch.setattr("diff_detector.pipeline.load_snapshot", lambda _path: {})
    monkeypatch.setattr("diff_detector.pipeline.run_diff", lambda *_args: diffs)
    monkeypatch.setattr(
        "diff_detector.pipeline.summarize_page_diffs", lambda _diffs: []
    )
    monkeypatch.setattr(
        "diff_detector.pipeline.build_relevance_map", lambda _summaries: {}
    )
    monkeypatch.setattr(
        "diff_detector.pipeline.notify_users",
        lambda *_args, **_kwargs: SimpleNamespace(
            recipients=1,
            sent=1,
            failed=0,
        ),
    )
    monkeypatch.setattr(
        "diff_detector.pipeline.load_snapshot_records",
        lambda _path: [{"url": "changed-url", "title": "Changed"}],
    )
    monkeypatch.setattr(
        "diff_detector.pipeline.store_documents",
        lambda documents: stored.extend(documents),
    )
    monkeypatch.setattr(
        "diff_detector.pipeline.chunk_sources",
        lambda **kwargs: chunked.append(kwargs),
    )

    run_ind_diff_pipeline()

    assert stored == [{"url": "changed-url", "title": "Changed"}]
    assert chunked == [{"source_id": "source-id", "override_chunks": True}]
    assert client.sources.deleted_urls == ["removed-url"]

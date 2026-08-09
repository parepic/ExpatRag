"""Orchestration tests for the IND diff pipeline.

The pipeline now delegates to six independently-tested stage functions; here we only
verify it calls them in order, short-circuits when there are no diffs, and threads
the notify stats into its result. Stage internals are covered by their own tests.
"""

from pathlib import Path
from types import SimpleNamespace

import diff_detector.pipeline as pipeline_module
from diff_detector.pipeline import run_ind_diff_pipeline


def _patch_stages(monkeypatch, calls, diffs):
    monkeypatch.setattr(pipeline_module, "ensure_run_dir", lambda data_dir=None: Path("run"))

    def snapshot(limit=None, data_dir=None, use_cache=False):
        calls.append(("snapshot", limit))
        return Path("run/snapshot.json")

    def run_diff_stage(data_dir=None):
        calls.append(("diff",))
        return diffs

    def run_summarize_stage(data_dir=None):
        calls.append(("summarize",))
        return []

    def run_classify_stage(data_dir=None):
        calls.append(("classify",))
        return {}

    def run_notify_stage(data_dir=None, dry_run=False):
        calls.append(("notify", dry_run))
        return SimpleNamespace(recipients=3, sent=2, failed=1)

    def run_update_corpus_stage(data_dir=None):
        calls.append(("update_corpus",))
        return {}

    monkeypatch.setattr(pipeline_module, "snapshot", snapshot)
    monkeypatch.setattr(pipeline_module, "run_diff_stage", run_diff_stage)
    monkeypatch.setattr(pipeline_module, "run_summarize_stage", run_summarize_stage)
    monkeypatch.setattr(pipeline_module, "run_classify_stage", run_classify_stage)
    monkeypatch.setattr(pipeline_module, "run_notify_stage", run_notify_stage)
    monkeypatch.setattr(pipeline_module, "run_update_corpus_stage", run_update_corpus_stage)


def test_pipeline_runs_all_stages_in_order_when_changes_exist(monkeypatch):
    calls: list[tuple] = []
    diffs = [SimpleNamespace(url="changed-url", change_type="CHANGED")]
    _patch_stages(monkeypatch, calls, diffs)

    result = run_ind_diff_pipeline(limit=5, dry_run=True)

    assert [c[0] for c in calls] == [
        "snapshot",
        "diff",
        "summarize",
        "classify",
        "notify",
        "update_corpus",
    ]
    assert ("snapshot", 5) in calls
    assert ("notify", True) in calls
    assert result.skipped_no_changes is False
    assert (result.recipients, result.emails_sent, result.emails_failed) == (3, 2, 1)
    assert result.diffs == diffs


def test_pipeline_short_circuits_when_no_changes(monkeypatch):
    calls: list[tuple] = []
    _patch_stages(monkeypatch, calls, [])

    result = run_ind_diff_pipeline()

    assert [c[0] for c in calls] == ["snapshot", "diff"]
    assert result.skipped_no_changes is True
    assert result.emails_sent == 0
    assert result.emails_failed == 0

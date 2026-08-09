import json
from pathlib import Path

from diff_detector.diff import load_diffs, run_diff, write_diffs

FIXTURES = Path(__file__).parent / "fixtures"


def _load_fixture(name: str) -> dict[str, str]:
    return {
        r["url"]: r["content"]
        for r in json.loads((FIXTURES / name).read_text())
        if r.get("content")
    }


def _load_titles(name: str) -> dict[str, str]:
    return {
        r["url"]: r.get("title", "")
        for r in json.loads((FIXTURES / name).read_text())
        if r.get("content")
    }


def test_ind_diff_detects_changed_pages():
    baseline = _load_fixture("ind_snapshot_baseline.json")
    modified = _load_fixture("ind_snapshot_modified.json")
    titles = _load_titles("ind_snapshot_modified.json")

    diffs = run_diff(baseline, modified, titles=titles)

    assert diffs, "expected at least one change between the fixtures"
    changed = [d for d in diffs if d.change_type == "CHANGED"]
    assert changed, "fixtures should include CHANGED pages"
    for d in changed:
        assert d.old_content and d.new_content
        assert d.old_content != d.new_content


def test_ind_diff_round_trips_through_json(tmp_path):
    baseline = _load_fixture("ind_snapshot_baseline.json")
    modified = _load_fixture("ind_snapshot_modified.json")
    titles = _load_titles("ind_snapshot_modified.json")

    diffs = run_diff(baseline, modified, titles=titles)
    path = tmp_path / "diff.json"
    write_diffs(diffs, path)

    assert load_diffs(path) == diffs


def test_added_and_removed_pages_carry_content_and_title():
    baseline = _load_fixture("ind_snapshot_baseline.json")
    modified = _load_fixture("ind_snapshot_modified.json")

    added_url = "https://ind.nl/en/new-policy-page"
    added_content = "This is a brand new IND policy page about something important."
    removed_url = next(iter(baseline))  # pick the first real baseline page as the removed one
    removed_content = baseline[removed_url]

    # REMOVED = in corpus (baseline) but absent from snapshot (modified)
    # ADDED   = absent from corpus but present in snapshot
    corpus = baseline
    snapshot = {url: c for url, c in modified.items() if url != removed_url}
    snapshot[added_url] = added_content
    titles = {added_url: "New Policy Page"}

    diffs = run_diff(corpus, snapshot, titles=titles)

    added = next(d for d in diffs if d.change_type == "ADDED")
    assert added.url == added_url
    assert added.content == added_content
    assert added.new_content == added_content
    assert added.title == "New Policy Page"
    assert all(line.startswith("+") for line in added.unified_diff.splitlines())

    removed = next(d for d in diffs if d.change_type == "REMOVED")
    assert removed.url == removed_url
    assert removed.content == removed_content
    assert removed.old_content == removed_content
    assert removed.new_content == ""
    assert removed.title == ""
    assert all(line.startswith("-") for line in removed.unified_diff.splitlines())

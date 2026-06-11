import json
from pathlib import Path

from diff_detector.diff import render_report, run_diff

FIXTURES = Path(__file__).parent / "fixtures"


def _load_fixture(name: str) -> dict[str, str]:
    return {
        r["url"]: r["content"]
        for r in json.loads((FIXTURES / name).read_text())
        if r.get("content")
    }


def test_ind_diff_matches_golden():
    baseline = _load_fixture("ind_snapshot_baseline.json")
    modified = _load_fixture("ind_snapshot_modified.json")
    total = len(set(baseline) | set(modified))

    expected = (FIXTURES / "ind_diff_expected.txt").read_text()
    assert render_report(run_diff(baseline, modified), total) == expected


def test_added_and_removed_pages_carry_content_but_not_in_report():
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

    total = len(set(corpus) | set(snapshot))
    diffs = run_diff(corpus, snapshot)
    report = render_report(diffs, total)

    added = next(d for d in diffs if d.change_type == "ADDED")
    assert added.url == added_url
    assert added.content == added_content
    assert all(line.startswith("+") for line in added.unified_diff.splitlines())

    removed = next(d for d in diffs if d.change_type == "REMOVED")
    assert removed.url == removed_url
    assert removed.content == removed_content
    assert all(line.startswith("-") for line in removed.unified_diff.splitlines())

    assert "ADDED" not in report
    assert "REMOVED" not in report
    assert added_url not in report
    assert removed_url not in report

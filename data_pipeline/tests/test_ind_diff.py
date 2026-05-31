import json
from pathlib import Path

from diff_detector.diff import run_diff

FIXTURES = Path(__file__).parent / "fixtures"


def test_ind_diff_matches_golden():
    baseline = {
        r["url"]: r["content"]
        for r in json.loads((FIXTURES / "ind_snapshot_baseline.json").read_text())
        if r.get("content")
    }
    modified = {
        r["url"]: r["content"]
        for r in json.loads((FIXTURES / "ind_snapshot_modified.json").read_text())
        if r.get("content")
    }

    expected = (FIXTURES / "ind_diff_expected.txt").read_text()
    assert run_diff(baseline, modified) == expected

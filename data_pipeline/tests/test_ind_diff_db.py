"""
Integration test: diff the live Supabase sources table against the modified IND fixture.

The modified fixture is identical to ind_snapshot_baseline.json except for 3 simulated
policy changes:
  - apply-for-recognition-as-sponsor: penalty lookback 4 years → 3 years, points 50 → 65
  - directive-eu-2016801-short-term-mobility-of-researchers: mobility window 180 → 120 days

The golden file (ind_diff_db_expected.txt) was generated from the DB state at the time
this test was written. The test may fail in the future if:
  - The IND website is updated and the DB is re-ingested
  - New pages are added to or removed from the sources table
"""
import json
from pathlib import Path

import pytest

from diff_detector.diff import load_corpus, render_report, run_diff

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.integration
# may fail if DB or IND website changes
def test_ind_diff_db_matches_golden():
    corpus = load_corpus()
    snapshot = {
        r["url"]: r["content"]
        for r in json.loads((FIXTURES / "ind_snapshot_modified.json").read_text())
        if r.get("content")
    }

    total = len(set(corpus) | set(snapshot))
    expected = (FIXTURES / "ind_diff_db_expected.txt").read_text()
    assert render_report(run_diff(corpus, snapshot), total) == expected

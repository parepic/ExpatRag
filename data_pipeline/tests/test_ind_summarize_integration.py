"""
Integration test: summarize a real IND page diff using the LLM.

Uses the same fixture diffs as test_ind_diff.py. The modified fixture changes
two pages with concrete numeric values — the test asserts the LLM picked up
the right numbers, not just that it returned something.

Run with:
    uv run --project data_pipeline pytest -m integration data_pipeline/tests/test_ind_summarize_integration.py -v
"""
import json
from pathlib import Path

import pytest

from diff_detector.diff import run_diff
from diff_detector.summarize import summarize_page_diff

FIXTURES = Path(__file__).parent / "fixtures"

SPONSOR_URL = "https://ind.nl/en/residence-permits/work/apply-for-recognition-as-sponsor"
RESEARCHER_URL = "https://ind.nl/en/residence-permits/work/directive-eu-2016801-short-term-mobility-of-researchers"


def _load_fixture(name: str) -> dict[str, str]:
    return {
        r["url"]: r["content"]
        for r in json.loads((FIXTURES / name).read_text())
        if r.get("content")
    }


@pytest.fixture(scope="module")
def ind_diffs():
    baseline = _load_fixture("ind_snapshot_baseline.json")
    modified = _load_fixture("ind_snapshot_modified.json")
    return {d.url: d for d in run_diff(baseline, modified)}


@pytest.mark.integration
def test_summarize_sponsor_page_catches_point_and_penalty_changes(ind_diffs):
    """The sponsor page changed the RVO point threshold (50→65) and the
    penalty lookback window (4→3 years). The summary must mention both."""
    diff = ind_diffs[SPONSOR_URL]
    print(f"\n--- DIFF ---\n{diff.unified_diff}")

    summary = summarize_page_diff(diff)
    print(f"\n--- SUMMARY ---")
    for bullet in summary.bullets:
        print(f"  • {bullet}")

    bullets_text = " ".join(summary.bullets).lower()
    assert "65" in bullets_text, "Expected the new 65-point threshold to appear"
    assert "50" in bullets_text, "Expected the old 50-point threshold to appear"
    assert "3" in bullets_text, "Expected the new 3-year penalty window to appear"
    assert "4" in bullets_text, "Expected the old 4-year penalty window to appear"


@pytest.mark.integration
def test_summarize_researcher_page_catches_day_window_change(ind_diffs):
    """The researcher mobility page changed the short-term window (180→120 days)
    in multiple places. The summary must mention both values."""
    diff = ind_diffs[RESEARCHER_URL]
    print(f"\n--- DIFF ---\n{diff.unified_diff}")

    summary = summarize_page_diff(diff)
    print(f"\n--- SUMMARY ---")
    for bullet in summary.bullets:
        print(f"  • {bullet}")

    bullets_text = " ".join(summary.bullets).lower()
    assert "120" in bullets_text, "Expected the new 120-day window to appear"
    assert "180" in bullets_text, "Expected the old 180-day window to appear"

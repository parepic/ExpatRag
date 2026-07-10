"""
Integration test: run the full summarize → classify → build_relevance_map pipeline
on a real IND diff and assert the resulting map makes sense.

Uses the sponsor recognition page diff (50→65 points, 4→3 year penalty window),
which is clearly relevant to HSM-related users and not to students.

Run with:
    uv run --project data_pipeline pytest -m integration data_pipeline/tests/test_ind_classify_integration.py -v -s
"""
import json
from pathlib import Path

import pytest

from diff_detector.classify import build_relevance_map
from diff_detector.diff import run_diff
from diff_detector.summarize import summarize_page_diffs

FIXTURES = Path(__file__).parent / "fixtures"

SPONSOR_URL = "https://ind.nl/en/residence-permits/work/apply-for-recognition-as-sponsor"


def _load_fixture(name: str) -> dict[str, str]:
    return {
        r["url"]: r["content"]
        for r in json.loads((FIXTURES / name).read_text())
        if r.get("content")
    }


@pytest.fixture(scope="module")
def relevance_map():
    baseline = _load_fixture("ind_snapshot_baseline.json")
    modified = _load_fixture("ind_snapshot_modified.json")

    # Only test the sponsor page to keep the test focused
    sponsor_diff = next(d for d in run_diff(baseline, modified) if d.url == SPONSOR_URL)
    summaries = summarize_page_diffs([sponsor_diff])
    return build_relevance_map(summaries)


@pytest.mark.integration
def test_hsm_slot_is_populated(relevance_map):
    """The sponsor recognition page is about HSM employer criteria — HSM users must be notified."""
    bullets = relevance_map["purpose_of_stay"]["Highly Skilled Migrant"]
    assert bullets, "Expected bullets for Highly Skilled Migrant"
    combined = " ".join(bullets)
    assert "65" in combined or "50" in combined, "Expected point threshold values in bullets"


@pytest.mark.integration
def test_study_slot_is_empty(relevance_map):
    """Sponsor recognition rules have nothing to do with students."""
    assert relevance_map["purpose_of_stay"]["Study"] == []

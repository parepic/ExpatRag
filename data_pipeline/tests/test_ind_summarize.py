from unittest.mock import MagicMock, patch

import pytest

from diff_detector.diff import PageDiff
from diff_detector.summarize import PageDiffSummary, summarize_page_diff, summarize_page_diffs


def make_diff(change_type, unified_diff="+ some content"):
    return PageDiff(
        url="https://ind.nl/en/some-page",
        change_type=change_type,
        unified_diff=unified_diff,
        content="some content",
    )


def mock_summary(bullets):
    return PageDiffSummary(bullets=bullets)


@pytest.fixture(autouse=True)
def patch_chain(monkeypatch):
    chain = MagicMock()
    monkeypatch.setattr("diff_detector.summarize._get_summarize_chain", lambda: chain)
    return chain


def test_summarize_changed_returns_bullets(patch_chain):
    patch_chain.invoke.return_value = mock_summary(["Before: 50 points. Now: 65 points."])
    diff = make_diff("CHANGED", "-need 50 points\n+need 65 points\n")

    result = summarize_page_diff(diff)

    assert result.bullets == ["Before: 50 points. Now: 65 points."]
    call_kwargs = patch_chain.invoke.call_args[0][0]
    assert call_kwargs["change_type"] == "CHANGED"
    assert call_kwargs["unified_diff"] == diff.unified_diff
    assert "Before:" in call_kwargs["instructions"]


def test_summarize_added_uses_added_instructions(patch_chain):
    patch_chain.invoke.return_value = mock_summary(["This page introduces: new visa category."])
    diff = make_diff("ADDED", "+new visa category details\n")

    result = summarize_page_diff(diff)

    assert "introduces" in result.bullets[0]
    call_kwargs = patch_chain.invoke.call_args[0][0]
    assert call_kwargs["change_type"] == "ADDED"
    assert "introduces" in call_kwargs["instructions"]


def test_summarize_removed_uses_removed_instructions(patch_chain):
    patch_chain.invoke.return_value = mock_summary(["This no longer applies: old requirement."])
    diff = make_diff("REMOVED", "-old requirement details\n")

    result = summarize_page_diff(diff)

    assert "no longer" in result.bullets[0]
    call_kwargs = patch_chain.invoke.call_args[0][0]
    assert call_kwargs["change_type"] == "REMOVED"
    assert "no longer" in call_kwargs["instructions"]


def test_summarize_batch_returns_paired_results(patch_chain):
    patch_chain.invoke.side_effect = [
        mock_summary(["Before: 180 days. Now: 120 days."]),
        mock_summary(["This page introduces: new sponsorship rules."]),
    ]
    diffs = [make_diff("CHANGED"), make_diff("ADDED")]

    results = summarize_page_diffs(diffs)

    assert len(results) == 2
    assert results[0][0] is diffs[0]
    assert results[1][0] is diffs[1]
    assert results[0][1].bullets == ["Before: 180 days. Now: 120 days."]
    assert results[1][1].bullets == ["This page introduces: new sponsorship rules."]


def test_summarize_passes_url_to_llm(patch_chain):
    patch_chain.invoke.return_value = mock_summary(["Before: A. Now: B."])
    diff = PageDiff(
        url="https://ind.nl/en/specific-page",
        change_type="CHANGED",
        unified_diff="-old\n+new\n",
        content="new",
    )

    summarize_page_diff(diff)

    assert patch_chain.invoke.call_args[0][0]["url"] == "https://ind.nl/en/specific-page"

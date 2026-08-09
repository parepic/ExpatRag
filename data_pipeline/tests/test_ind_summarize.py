from unittest.mock import MagicMock, patch

import pytest

from diff_detector.diff import PageDiff
from diff_detector.summarize import (
    PageDiffSummary,
    has_substantive_lines,
    strip_mechanical_noise,
    summarize_page_diff,
    summarize_page_diffs,
)

FILE_SIZE_DIFF = (
    "--- corpus\n+++ snapshot\n@@ -1,1 +1,1 @@\n"
    "-Application residence permit B07001E (PDF, 609.97 KB)\n"
    "+Application residence permit B07001E (PDF, 529.56 KB)\n"
)

DATE_STAMP_DIFF = (
    "--- corpus\n+++ snapshot\n@@ -1,1 +1,1 @@\n"
    "-Last update: 30 June 2026\n"
    "+Last update: 14 July 2026\n"
)

DATE_PLUS_REAL_DIFF = (
    "--- corpus\n+++ snapshot\n@@ -1,4 +1,4 @@\n"
    "-Last update: 30 June 2026\n"
    "+Last update: 14 July 2026\n"
    " context line\n"
    "-You may stay outside the Netherlands for 8 months only for seconded work.\n"
    "+You may stay outside the Netherlands for 8 months without that condition.\n"
)


def make_diff(change_type, unified_diff="+ some content"):
    return PageDiff(
        url="https://ind.nl/en/some-page",
        change_type=change_type,
        unified_diff=unified_diff,
        content="some content",
    )


def mock_summary(bullets, has_regulatory_change=True):
    return PageDiffSummary(has_regulatory_change=has_regulatory_change, bullets=bullets)


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


def test_summarize_batch_filters_out_non_regulatory_pages(patch_chain):
    patch_chain.invoke.side_effect = [
        mock_summary(["Before: 180 days. Now: 120 days."]),
        # e.g. a "Last update" date stamp or PDF file-size change
        mock_summary([], has_regulatory_change=False),
        mock_summary(["Before: fee was 200. Now: fee is 210."]),
    ]
    diffs = [make_diff("CHANGED"), make_diff("CHANGED"), make_diff("CHANGED")]

    results = summarize_page_diffs(diffs)

    assert len(results) == 2
    assert results[0][0] is diffs[0]
    assert results[1][0] is diffs[2]


def test_summarize_batch_filters_regulatory_flag_with_no_bullets(patch_chain):
    """A page flagged regulatory but with no bullets carries no information — drop it."""
    patch_chain.invoke.side_effect = [mock_summary([], has_regulatory_change=True)]

    results = summarize_page_diffs([make_diff("CHANGED")])

    assert results == []


def test_summarize_prompt_instructs_filtering(patch_chain):
    patch_chain.invoke.return_value = mock_summary(["Before: A. Now: B."])

    summarize_page_diff(make_diff("CHANGED"))

    instructions = patch_chain.invoke.call_args[0][0]["instructions"]
    assert "KEEP-worthy" in instructions


class TestMechanicalNoiseFilter:
    """File sizes and date stamps are cancelled deterministically, before the LLM."""

    def test_file_size_only_diff_reduces_to_nothing(self):
        assert not has_substantive_lines(strip_mechanical_noise(FILE_SIZE_DIFF))

    def test_date_stamp_only_diff_reduces_to_nothing(self):
        assert not has_substantive_lines(strip_mechanical_noise(DATE_STAMP_DIFF))

    def test_real_change_survives_alongside_date_stamp(self):
        reduced = strip_mechanical_noise(DATE_PLUS_REAL_DIFF)
        assert has_substantive_lines(reduced)
        assert "Last update" not in reduced
        assert "seconded work" in reduced

    def test_diff_without_noise_is_untouched(self):
        diff = "--- corpus\n+++ snapshot\n-need 50 points\n+need 65 points\n"
        assert strip_mechanical_noise(diff) == diff

    def test_file_size_only_page_skips_llm_entirely(self, patch_chain):
        result = summarize_page_diff(make_diff("CHANGED", FILE_SIZE_DIFF))

        assert result.has_regulatory_change is False
        assert result.bullets == []
        patch_chain.invoke.assert_not_called()

    def test_date_only_page_skips_llm_entirely(self, patch_chain):
        result = summarize_page_diff(make_diff("CHANGED", DATE_STAMP_DIFF))

        assert result.has_regulatory_change is False
        patch_chain.invoke.assert_not_called()

    def test_llm_receives_diff_with_noise_already_stripped(self, patch_chain):
        patch_chain.invoke.return_value = mock_summary(["Before: A. Now: B."])

        summarize_page_diff(make_diff("CHANGED", DATE_PLUS_REAL_DIFF))

        sent = patch_chain.invoke.call_args[0][0]["unified_diff"]
        assert "Last update" not in sent
        assert "seconded work" in sent


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

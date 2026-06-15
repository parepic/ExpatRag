from diff_detector.diff import PageDiff, render_report, run_diff


def test_unchanged_page_produces_no_diff():
    corpus = {"https://ind.nl/page-a": "Same content"}
    snapshot = {"https://ind.nl/page-a": "Same content"}
    diffs = run_diff(corpus, snapshot)
    assert diffs == []


def test_changed_page_has_unified_diff_and_new_content():
    corpus = {"https://ind.nl/page-a": "old line\n"}
    snapshot = {"https://ind.nl/page-a": "new line\n"}
    diffs = run_diff(corpus, snapshot)
    assert len(diffs) == 1
    assert diffs[0].change_type == "CHANGED"
    assert diffs[0].url == "https://ind.nl/page-a"
    assert "-old line" in diffs[0].unified_diff
    assert "+new line" in diffs[0].unified_diff
    assert diffs[0].content == "new line\n"


def test_added_page_has_full_new_content():
    corpus = {}
    snapshot = {"https://ind.nl/new-page": "Some content"}
    diffs = run_diff(corpus, snapshot)
    assert len(diffs) == 1
    assert diffs[0].change_type == "ADDED"
    assert diffs[0].url == "https://ind.nl/new-page"
    assert diffs[0].content == "Some content"
    assert "+Some content" in diffs[0].unified_diff
    assert "-" not in diffs[0].unified_diff


def test_removed_page_has_full_old_content():
    corpus = {"https://ind.nl/old-page": "Some content"}
    snapshot = {}
    diffs = run_diff(corpus, snapshot)
    assert len(diffs) == 1
    assert diffs[0].change_type == "REMOVED"
    assert diffs[0].url == "https://ind.nl/old-page"
    assert diffs[0].content == "Some content"
    assert "-Some content" in diffs[0].unified_diff
    assert "+" not in diffs[0].unified_diff


def test_summary_counts_are_correct():
    corpus = {
        "https://ind.nl/changed": "old\n",
        "https://ind.nl/unchanged": "same\n",
        "https://ind.nl/removed": "gone\n",
    }
    snapshot = {
        "https://ind.nl/changed": "new\n",
        "https://ind.nl/unchanged": "same\n",
        "https://ind.nl/added": "fresh\n",
    }
    total = len(set(corpus) | set(snapshot))
    diffs = run_diff(corpus, snapshot)
    report = render_report(diffs, total)
    assert "1 changed" in report
    assert "1 added" in report
    assert "1 removed" in report
    assert "1 unchanged" in report


def test_report_body_contains_only_changed_pages():
    corpus = {
        "https://ind.nl/changed": "old\n",
        "https://ind.nl/removed": "gone\n",
    }
    snapshot = {
        "https://ind.nl/changed": "new\n",
        "https://ind.nl/added": "fresh\n",
    }
    total = len(set(corpus) | set(snapshot))
    diffs = run_diff(corpus, snapshot)
    report = render_report(diffs, total)
    assert "CHANGED: https://ind.nl/changed" in report
    assert "ADDED" not in report
    assert "REMOVED" not in report

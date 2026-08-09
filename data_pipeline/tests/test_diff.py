from collections import Counter

from diff_detector.diff import PageDiff, load_diffs, run_diff, write_diffs


def test_unchanged_page_produces_no_diff():
    corpus = {"https://ind.nl/page-a": "Same content"}
    snapshot = {"https://ind.nl/page-a": "Same content"}
    diffs = run_diff(corpus, snapshot)
    assert diffs == []


def test_changed_page_has_unified_diff_and_new_content():
    corpus = {"https://ind.nl/page-a": "old line\n"}
    snapshot = {"https://ind.nl/page-a": "new line\n"}
    diffs = run_diff(corpus, snapshot, titles={"https://ind.nl/page-a": "Page A"})
    assert len(diffs) == 1
    assert diffs[0].change_type == "CHANGED"
    assert diffs[0].url == "https://ind.nl/page-a"
    assert "-old line" in diffs[0].unified_diff
    assert "+new line" in diffs[0].unified_diff
    assert diffs[0].content == "new line\n"
    assert diffs[0].old_content == "old line\n"
    assert diffs[0].new_content == "new line\n"
    assert diffs[0].title == "Page A"


def test_added_page_has_full_new_content():
    corpus = {}
    snapshot = {"https://ind.nl/new-page": "Some content"}
    diffs = run_diff(corpus, snapshot, titles={"https://ind.nl/new-page": "New Page"})
    assert len(diffs) == 1
    assert diffs[0].change_type == "ADDED"
    assert diffs[0].url == "https://ind.nl/new-page"
    assert diffs[0].content == "Some content"
    assert diffs[0].new_content == "Some content"
    assert diffs[0].old_content == ""
    assert diffs[0].title == "New Page"
    assert "+Some content" in diffs[0].unified_diff
    assert "-" not in diffs[0].unified_diff


def test_removed_page_has_full_old_content_and_no_title():
    corpus = {"https://ind.nl/old-page": "Some content"}
    snapshot = {}
    diffs = run_diff(corpus, snapshot)
    assert len(diffs) == 1
    assert diffs[0].change_type == "REMOVED"
    assert diffs[0].url == "https://ind.nl/old-page"
    assert diffs[0].content == "Some content"
    assert diffs[0].old_content == "Some content"
    assert diffs[0].new_content == ""
    assert diffs[0].title == ""
    assert "-Some content" in diffs[0].unified_diff
    assert "+" not in diffs[0].unified_diff


def test_change_type_counts_are_correct():
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
    diffs = run_diff(corpus, snapshot)
    counts = Counter(d.change_type for d in diffs)
    assert counts == {"CHANGED": 1, "ADDED": 1, "REMOVED": 1}


def test_write_and_load_diffs_round_trip(tmp_path):
    corpus = {"https://ind.nl/changed": "old\n", "https://ind.nl/removed": "gone\n"}
    snapshot = {"https://ind.nl/changed": "new\n", "https://ind.nl/added": "fresh\n"}
    titles = {"https://ind.nl/changed": "Changed", "https://ind.nl/added": "Added"}
    diffs = run_diff(corpus, snapshot, titles=titles)

    path = tmp_path / "diff.json"
    write_diffs(diffs, path)
    loaded = load_diffs(path)

    assert loaded == diffs
    assert all(isinstance(d, PageDiff) for d in loaded)

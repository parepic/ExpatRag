from diff_detector.diff import run_diff


def test_unchanged_page_excluded_from_report():
    d = {"https://ind.nl/page-a": "Same content"}
    d_prime = {"https://ind.nl/page-a": "Same content"}
    report = run_diff(d, d_prime)
    assert "UNCHANGED" not in report
    assert "page-a" not in report
    assert "1 unchanged" in report


def test_changed_page_shows_unified_diff():
    d = {"https://ind.nl/page-a": "old line\n"}
    d_prime = {"https://ind.nl/page-a": "new line\n"}
    report = run_diff(d, d_prime)
    assert "CHANGED: https://ind.nl/page-a" in report
    assert "-old line" in report
    assert "+new line" in report


def test_added_page():
    d = {}
    d_prime = {"https://ind.nl/new-page": "Some content"}
    report = run_diff(d, d_prime)
    assert "ADDED: https://ind.nl/new-page" in report


def test_removed_page():
    d = {"https://ind.nl/old-page": "Some content"}
    d_prime = {}
    report = run_diff(d, d_prime)
    assert "REMOVED: https://ind.nl/old-page" in report


def test_summary_counts_are_correct():
    d = {
        "https://ind.nl/changed": "old\n",
        "https://ind.nl/unchanged": "same\n",
        "https://ind.nl/removed": "gone\n",
    }
    d_prime = {
        "https://ind.nl/changed": "new\n",
        "https://ind.nl/unchanged": "same\n",
        "https://ind.nl/added": "fresh\n",
    }
    report = run_diff(d, d_prime)
    assert "1 changed" in report
    assert "1 added" in report
    assert "1 removed" in report
    assert "1 unchanged" in report

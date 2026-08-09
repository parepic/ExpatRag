"""Tests for the JSON handoff seams introduced by the staged pipeline:
diff → summaries → relevance (de)serialization and run_diff_stage plumbing.
"""

import json
from types import SimpleNamespace

from diff_detector.classify import load_relevance, write_relevance
from diff_detector.diff import (
    SNAPSHOT_FILENAME,
    load_corpus,
    load_diffs,
    run_diff_stage,
)
from lib.config import SCRAPE_SITES
from diff_detector.summarize import PageDiffSummary, load_summaries, write_summaries
from diff_detector.diff import PageDiff


class FakeCorpusClient:
    """Minimal Supabase stand-in returning a fixed corpus for load_corpus()."""

    def __init__(self, rows):
        self._rows = rows
        self.filtered_types = None

    def table(self, _name):
        return self

    def select(self, *_args):
        return self

    def in_(self, column, values):
        if column == "type":
            self.filtered_types = list(values)
        return self

    def range(self, *_args):
        return self

    def execute(self):
        return SimpleNamespace(data=self._rows)


def test_load_corpus_only_loads_the_configured_sites():
    """A site that was not scraped this run must stay out of the corpus, or every one of
    its pages would be reported REMOVED and deleted by stage 6."""
    client = FakeCorpusClient([{"source_url": "https://ind.nl/a", "content": "A\n"}])

    load_corpus(client=client, sites=["ind.nl"])

    assert client.filtered_types == ["ind.nl"]


def test_load_corpus_defaults_to_scrape_sites():
    client = FakeCorpusClient([])

    load_corpus(client=client)

    assert client.filtered_types == list(SCRAPE_SITES)


def test_run_diff_stage_reads_snapshot_and_writes_diff(tmp_path):
    (tmp_path / SNAPSHOT_FILENAME).write_text(
        json.dumps(
            [
                {"url": "https://ind.nl/a", "title": "A", "content": "new A\n", "scraped_at": "t"},
                {"url": "https://ind.nl/b", "title": "B", "content": "brand new\n", "scraped_at": "t"},
            ]
        )
    )
    client = FakeCorpusClient([{"source_url": "https://ind.nl/a", "content": "old A\n"}])

    diffs = run_diff_stage(data_dir=tmp_path, client=client)

    by_url = {d.url: d for d in diffs}
    assert by_url["https://ind.nl/a"].change_type == "CHANGED"
    assert by_url["https://ind.nl/a"].title == "A"
    assert by_url["https://ind.nl/b"].change_type == "ADDED"
    # diff.json was written and round-trips
    assert load_diffs(tmp_path / "diff.json") == diffs


def test_load_summaries_round_trip(tmp_path):
    pairs = [
        (
            PageDiff(url="https://ind.nl/a", change_type="CHANGED", unified_diff="x", content="y"),
            PageDiffSummary(has_regulatory_change=True, bullets=["one", "two"]),
        )
    ]
    write_summaries(pairs, tmp_path / "summaries.json")

    loaded = load_summaries(tmp_path / "summaries.json")
    assert len(loaded) == 1
    diff, summary = loaded[0]
    assert diff.url == "https://ind.nl/a"
    assert diff.change_type == "CHANGED"
    assert summary.bullets == ["one", "two"]


def test_relevance_boolean_keys_survive_round_trip(tmp_path):
    partner = {"text": "partner bullet", "url": "https://ind.nl/en/a"}
    over_30 = {"text": "over-30 bullet", "url": "https://ind.nl/en/b"}
    hsm = {"text": "hsm bullet", "url": "https://ind.nl/en/c"}
    relevance = {
        "has_fiscal_partner": {True: [partner], False: []},
        "age_bracket_under_30": {True: [], False: [over_30]},
        "prior_nl_residency": {True: [], False: []},
        "purpose_of_stay": {"Highly Skilled Migrant": [hsm], "Study": []},
    }
    write_relevance(relevance, tmp_path / "relevance.json")

    loaded = load_relevance(tmp_path / "relevance.json")

    # Boolean keys must come back as real bools, not "true"/"false" strings.
    assert loaded["has_fiscal_partner"][True] == [partner]
    assert loaded["age_bracket_under_30"][False] == [over_30]
    assert loaded["purpose_of_stay"]["Highly Skilled Migrant"] == [hsm]
    # Every allowed slot is present, matching build_relevance_map's shape.
    assert set(loaded["has_fiscal_partner"].keys()) == {True, False}


def test_relevance_written_before_urls_loads_with_empty_url(tmp_path):
    """Relevance files from before bullets carried a URL hold bare strings."""
    path = tmp_path / "relevance.json"
    path.write_text('{"purpose_of_stay": {"Study": ["legacy bullet"]}}')

    loaded = load_relevance(path)

    assert loaded["purpose_of_stay"]["Study"] == [{"text": "legacy bullet", "url": ""}]

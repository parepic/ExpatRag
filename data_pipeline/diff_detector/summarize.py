"""Stage 3 — summarize: turn <data_dir>/diff.json into <data_dir>/summaries.json
using an LLM (one bullet list of semantic changes per page)."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import date
from functools import lru_cache
from pathlib import Path

_pipeline_root = Path(__file__).resolve().parents[1]
if str(_pipeline_root) not in sys.path:
    sys.path.insert(0, str(_pipeline_root))

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langsmith import traceable
from pydantic import BaseModel, Field

from diff_detector.diff import PageDiff, load_diffs
from lib.config import DIFF_FILENAME, SUMMARIES_FILENAME, ensure_run_dir
from lib.env import load_pipeline_env


IND_DIFF_SUMMARY_MODEL = os.getenv("IND_DIFF_SUMMARY_MODEL", "gpt-5.1")

CHANGE_TYPE_INSTRUCTIONS: dict[str, str] = {
    "CHANGED": (
        "The page content has been modified. "
        "For each KEEP-worthy change, write one bullet point in the form "
        "'Before: <old state>. Now: <new state>.' "
        "Group related line changes into a single bullet — do not produce one "
        "bullet per diff line. Write no bullet at all for DISCARD-worthy changes."
    ),
    "ADDED": (
        "This is a brand new page that did not exist before. "
        "If it introduces a requirement, option, right, or constraint, frame each "
        "bullet as 'This page introduces: <topic>.' "
        "If it is a news, story, or purely informational page that sets no rules, "
        "set has_regulatory_change to false."
    ),
    "REMOVED": (
        "This page has been removed entirely. "
        "If it covered a requirement, procedure, option, or right that no longer "
        "applies, frame each bullet as 'This no longer applies: <topic>.' "
        "If it was a news, story, or staff page that set no rules, set "
        "has_regulatory_change to false."
    ),
}

SYSTEM_PROMPT = """
You are a filter for changes to the Dutch IND (Immigration and Naturalisation
Service) website. A separate, later system will summarise and route genuine policy
updates to expats. Your job is to decide whether a page change is conclusive
evidence that a rule itself changed, and if so, to state plainly what changed.

You will be given the URL of a page and a diff showing what changed.
Lines starting with '+' are new content. Lines starting with '-' are removed content.
Lines with neither prefix are unchanged context.

KEEP a change only if the new text itself says a rule changed, or is going to change.
It must either:
- name the date it takes or took effect, or
- state outright that a requirement, fee, condition, or procedure has changed, been
  introduced, or been withdrawn, or
- report that such a change is planned, proposed, expected, or under discussion.

It must be the rules that changed, not the website or the service around them. A form,
portal, payment method, or appointment system becoming available, unavailable, or
moving online changes nothing about what an applicant must qualify for, supply, or
pay — discard those even when a date is attached.

Silent rewording is never a change, however material it looks. If the page states a
requirement differently without saying that anything changed, discard it.

DISCARD everything else. The following are never meaningful on their own:
- "Last update", publication, or revision date stamps
- file sizes of linked PDFs or attachments (e.g. "was 609 KB, now 529 KB")
- a downloadable form or brochure being re-uploaded, renamed, added, or removed
  while the underlying requirement is unchanged
- news items, stories, interviews, staff profiles, or press releases
- translations, typo/grammar/spelling fixes, or rewording that preserves meaning
- navigation, menus, link text, headings, or organisational descriptions
- formatting, whitespace, punctuation, or layout

Judge the page as a whole:
- Set has_regulatory_change to true only if at least one change clears both bars.
  Then write one concise bullet per such change, and none for the rest.
- Otherwise set has_regulatory_change to false and return an empty bullet list.

Be factual and specific — include the concrete values, deadlines, or conditions
named in the diff, and never invent any. Today's date is given below; use it only to
say whether a stated date is already in force or still upcoming, never to decide
whether to keep a change. When in doubt, discard: a missed minor edit costs nothing,
while a false alert wastes every recipient's attention.
""".strip()

HUMAN_TEMPLATE = """\
Today's date: {today}
URL: {url}
Change type: {change_type}
Instructions: {instructions}

Diff:
{unified_diff}
"""

SUMMARIZE_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", HUMAN_TEMPLATE),
    ]
)


class PageDiffSummary(BaseModel):
    has_regulatory_change: bool = Field(
        description=(
            "True only if the new text says a rule changed or will change — naming a "
            "date it applies from, stating that a requirement, fee, condition, or "
            "procedure has changed, been introduced, or been withdrawn, or reporting "
            "that such a change is planned, proposed, or under discussion. False for "
            "silent rewording, "
            "service/availability notices, date stamps, PDF file sizes, news/stories, "
            "translations, navigation, and formatting."
        )
    )
    bullets: list[str] = Field(
        default_factory=list,
        description=(
            "One bullet point per meaningful change. Empty when "
            "has_regulatory_change is false."
        ),
    )


@lru_cache(maxsize=1)
def _get_summarize_chain():
    load_pipeline_env()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY must be set before summarizing diffs.")

    llm = ChatOpenAI(
        model=IND_DIFF_SUMMARY_MODEL,
        temperature=0,
        api_key=api_key,
    )
    return SUMMARIZE_PROMPT | llm.with_structured_output(PageDiffSummary)


# Mechanical churn the LLM should never see. These patterns are perfectly detectable,
# so we cancel them deterministically rather than relying on the model to ignore them.
_FILE_SIZE_RE = re.compile(r"\d+(?:[.,]\d+)?\s*(?:KB|MB|GB)", re.IGNORECASE)
_DATE_RE = re.compile(r"\d{1,2}\s+\w+\s+\d{4}")


def _normalize_noise(text: str) -> str:
    """Blank out file sizes/date stamps so lines differing only by those compare equal."""
    text = _FILE_SIZE_RE.sub("<SIZE>", text)
    text = _DATE_RE.sub("<DATE>", text)
    return " ".join(text.split())


def _is_removed(line: str) -> bool:
    return line.startswith("-") and not line.startswith("---")


def _is_added(line: str) -> bool:
    return line.startswith("+") and not line.startswith("+++")


def strip_mechanical_noise(unified_diff: str) -> str:
    """Drop -/+ line pairs that differ only by a file size or date stamp.

    A page whose entire diff is "(PDF, 609 KB)" → "(PDF, 529 KB)" or
    "Last update: 30 June" → "Last update: 14 July" reduces to nothing, so it never
    reaches the LLM. Real changes on the same page survive untouched.
    """
    lines = unified_diff.splitlines(keepends=True)
    removed: Counter[str] = Counter()
    added: Counter[str] = Counter()
    for line in lines:
        if _is_removed(line):
            removed[_normalize_noise(line[1:])] += 1
        elif _is_added(line):
            added[_normalize_noise(line[1:])] += 1

    cancel = {key: min(count, added[key]) for key, count in removed.items() if key in added}
    if not cancel:
        return unified_diff

    budget_removed = dict(cancel)
    budget_added = dict(cancel)
    kept: list[str] = []
    for line in lines:
        if _is_removed(line):
            key = _normalize_noise(line[1:])
            if budget_removed.get(key, 0) > 0:
                budget_removed[key] -= 1
                continue
        elif _is_added(line):
            key = _normalize_noise(line[1:])
            if budget_added.get(key, 0) > 0:
                budget_added[key] -= 1
                continue
        kept.append(line)
    return "".join(kept)


def has_substantive_lines(unified_diff: str) -> bool:
    """True if the diff still contains a non-empty added/removed line."""
    for line in unified_diff.splitlines():
        if line.startswith(("---", "+++", "@@")):
            continue
        if line.startswith(("-", "+")) and line[1:].strip():
            return True
    return False


@traceable(
    run_type="chain",
    name="summarize_page_diff",
    tags=["summarize_page_diff"],
    process_inputs=lambda inputs: {
        "url": inputs["diff"].url,
        "change_type": inputs["diff"].change_type,
        "unified_diff": inputs["diff"].unified_diff,
        "old_content": inputs["diff"].old_content,
        "new_content": inputs["diff"].new_content,
    },
)
def summarize_page_diff(diff: PageDiff) -> PageDiffSummary:
    """Summarize a single PageDiff into bullet points using an LLM.

    Mechanical churn (file sizes, date stamps) is stripped first; if nothing
    substantive remains, the page is rejected without spending an LLM call.
    """
    reduced_diff = strip_mechanical_noise(diff.unified_diff)
    if not has_substantive_lines(reduced_diff):
        return PageDiffSummary(has_regulatory_change=False, bullets=[])

    return _get_summarize_chain().invoke(
        {
            # The model has no clock — without this it assumes a date years in the past.
            "today": date.today().isoformat(),
            "url": diff.url,
            "change_type": diff.change_type,
            "instructions": CHANGE_TYPE_INSTRUCTIONS[diff.change_type],
            "unified_diff": reduced_diff,
        }
    )


def summarize_page_diffs(diffs: list[PageDiff]) -> list[tuple[PageDiff, PageDiffSummary]]:
    """Summarize a batch of PageDiffs, dropping pages with no likely regulatory change.

    Only pages the LLM flags as regulatory (and for which it produced bullets) are
    returned, so downstream stages never see date-stamp/file-size/editorial noise.
    """
    results: list[tuple[PageDiff, PageDiffSummary]] = []
    for index, diff in enumerate(diffs, start=1):
        summary = summarize_page_diff(diff)
        if not (summary.has_regulatory_change and summary.bullets):
            print(
                f"  Filtered {index}/{len(diffs)} ({diff.change_type}): "
                f"{diff.url} — no likely regulatory change"
            )
            continue
        results.append((diff, summary))
        print(
            f"  Summarized {index}/{len(diffs)} ({diff.change_type}): "
            f"{diff.url} — {len(summary.bullets)} bullet(s)"
        )
    print(
        f"Retained {len(results)}/{len(diffs)} page(s) with likely regulatory changes"
    )
    return results


def write_summaries(
    summaries: list[tuple[PageDiff, PageDiffSummary]],
    path: Path,
) -> Path:
    """Write the LLM summaries as JSON ([{url, change_type, bullets}]) to path."""
    payload = [
        {
            "url": diff.url,
            "change_type": diff.change_type,
            "bullets": summary.bullets,
        }
        for diff, summary in summaries
    ]
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"Summaries written to {path} ({len(payload)} page(s))")
    return path


def load_summaries(path: Path) -> list[tuple[PageDiff, PageDiffSummary]]:
    """Load summaries.json back into (PageDiff, PageDiffSummary) pairs.

    Only the fields the classifier needs (url, change_type, bullets) are restored;
    unused PageDiff fields default to empty.
    """
    records = json.loads(path.read_text())
    return [
        (
            PageDiff(
                url=record["url"],
                change_type=record["change_type"],
                unified_diff="",
                content="",
            ),
            # Only pages that passed the regulatory filter are ever written out.
            PageDiffSummary(has_regulatory_change=True, bullets=record["bullets"]),
        )
        for record in records
    ]


# One span per `just summarize` run. LangSmith rolls tokens and cost up the tree, so
# this run's totals are the whole stage's spend — the per-page spans stay as children.
@traceable(
    run_type="chain",
    name="ind_summarize_stage",
    tags=["ind_summarize_stage"],
    process_inputs=lambda inputs: {"data_dir": str(inputs.get("data_dir") or "default")},
    process_outputs=lambda retained: {
        "retained_pages": len(retained),
        "pages": [
            {"url": d.url, "change_type": d.change_type, "bullets": s.bullets}
            for d, s in retained
        ],
    },
)
def run_summarize_stage(
    data_dir: Path | str | None = None,
) -> list[tuple[PageDiff, PageDiffSummary]]:
    """Read <data_dir>/diff.json, summarise each page, write <data_dir>/summaries.json."""
    run_dir = ensure_run_dir(data_dir)
    diffs = load_diffs(run_dir / DIFF_FILENAME)
    summaries = summarize_page_diffs(diffs)
    write_summaries(summaries, run_dir / SUMMARIES_FILENAME)
    return summaries


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Stage 3 — summarise each changed page in <data_dir>/diff.json with an "
            "LLM and write <data_dir>/summaries.json."
        )
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Run directory holding diff.json (default: data/latest/).",
    )
    args = parser.parse_args()
    run_summarize_stage(data_dir=args.data_dir)


if __name__ == "__main__":
    main()

"""LLM summarizer for IND page diffs."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from diff_detector.diff import PageDiff
from lib.env import load_pipeline_env


IND_DIFF_SUMMARY_MODEL = os.getenv("IND_DIFF_SUMMARY_MODEL", "gpt-4o-mini")

CHANGE_TYPE_INSTRUCTIONS: dict[str, str] = {
    "CHANGED": (
        "The page content has been modified. "
        "For each distinct semantic change you identify, write one bullet point "
        "in the form 'Before: <old state>. Now: <new state>.' "
        "Group related line changes into a single bullet — do not produce one "
        "bullet per diff line."
    ),
    "ADDED": (
        "This is a brand new page that did not exist before. "
        "Summarize what this page introduces: what requirement, option, right, "
        "or constraint now exists that did not before. "
        "Frame each bullet as 'This page introduces: <topic>.'"
    ),
    "REMOVED": (
        "This page has been removed entirely. "
        "Summarize what it covered: what requirement, option, right, or "
        "constraint no longer applies. "
        "Frame each bullet as 'This no longer applies: <topic>.'"
    ),
}

SYSTEM_PROMPT = """
You are a policy analyst summarizing changes to the Dutch IND (Immigration and
Naturalisation Service) website for expats and international residents in the
Netherlands.

You will be given the URL of a page and a diff showing what changed.
Lines starting with '+' are new content. Lines starting with '-' are removed content.
Lines with neither prefix are unchanged context.

Your job:
- Identify every distinct semantic change in the diff.
- Write one concise bullet point per semantic change following the instructions
  provided for the change type.
- Be factual and specific — include concrete values, deadlines, or conditions
  mentioned in the diff.
- Do not invent information not present in the diff.
- Do not comment on formatting, whitespace, or punctuation changes.
""".strip()

HUMAN_TEMPLATE = """\
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
    bullets: list[str] = Field(
        description="One bullet point per distinct semantic change."
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


def summarize_page_diff(diff: PageDiff) -> PageDiffSummary:
    """Summarize a single PageDiff into bullet points using an LLM."""
    return _get_summarize_chain().invoke(
        {
            "url": diff.url,
            "change_type": diff.change_type,
            "instructions": CHANGE_TYPE_INSTRUCTIONS[diff.change_type],
            "unified_diff": diff.unified_diff,
        }
    )


def summarize_page_diffs(diffs: list[PageDiff]) -> list[tuple[PageDiff, PageDiffSummary]]:
    """Summarize a batch of PageDiffs."""
    results: list[tuple[PageDiff, PageDiffSummary]] = []
    for index, diff in enumerate(diffs, start=1):
        summary = summarize_page_diff(diff)
        results.append((diff, summary))
        print(
            f"  Summarized {index}/{len(diffs)} ({diff.change_type}): "
            f"{diff.url} — {len(summary.bullets)} bullet(s)"
        )
    return results

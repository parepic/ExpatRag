"""LLM classifier: maps a PageDiffSummary to affected user profile (attribute, value) pairs."""

from __future__ import annotations

import json
import os
from functools import lru_cache

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from diff_detector.diff import PageDiff
from diff_detector.summarize import PageDiffSummary
from lib.env import load_pipeline_env
from lib.user_attributes import USER_PROFILE_ATTRIBUTES

IND_DIFF_CLASSIFY_MODEL = os.getenv("IND_DIFF_CLASSIFY_MODEL", "gpt-4o-mini")

# Pre-rendered once for inclusion in the prompt
_ATTRIBUTES_JSON = json.dumps(USER_PROFILE_ATTRIBUTES, indent=2, ensure_ascii=False)

RelevanceMap = dict[str, dict[str | bool, list[str]]]

SYSTEM_PROMPT = """
You are a relevance classifier for an expat assistant in the Netherlands.

You will be given a summary of changes to an IND (Immigration and Naturalisation
Service) web page, and a dictionary of user profile attributes with their possible
values.

Your job is to decide which (attribute, value) pairs are affected by these changes.
Only include pairs where the change is genuinely relevant to a user with that value.
If a change affects all users regardless of profile, include all applicable values.
If a change is irrelevant to a particular group, exclude them.

Return only attribute keys and values from the provided dictionary — do not invent new ones.
""".strip()

HUMAN_TEMPLATE = """\
Page URL: {url}
Change type: {change_type}

Summary of changes:
{bullets}

User profile attributes and allowed values:
{attributes}
"""

CLASSIFY_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", HUMAN_TEMPLATE),
    ]
)


class PageRelevance(BaseModel):
    affected: dict[str, list[str | bool]] = Field(
        description=(
            "For each relevant attribute, the list of values affected by this change. "
            "Only include attributes and values from the provided dictionary."
        )
    )


@lru_cache(maxsize=1)
def _get_classify_chain():
    load_pipeline_env()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY must be set before classifying relevance.")

    llm = ChatOpenAI(
        model=IND_DIFF_CLASSIFY_MODEL,
        temperature=0,
        api_key=api_key,
    )
    return CLASSIFY_PROMPT | llm.with_structured_output(PageRelevance, method="function_calling")


def classify_page_relevance(diff: PageDiff, summary: PageDiffSummary) -> PageRelevance:
    """Classify which (attribute, value) pairs are affected by a page change."""
    return _get_classify_chain().invoke(
        {
            "url": diff.url,
            "change_type": diff.change_type,
            # TODO: classify per bullet instead of per page for more precise relevance matching.
            "bullets": "\n".join(f"- {b}" for b in summary.bullets),
            "attributes": _ATTRIBUTES_JSON,
        }
    )


def build_relevance_map(
    summaries: list[tuple[PageDiff, PageDiffSummary]],
) -> RelevanceMap:
    """Build the full relevance map from a list of summarized page diffs.

    Returns dict[attribute, dict[value, list[bullet_strings]]].
    All (attribute, value) pairs are initialised — empty list means no relevant changes.
    """
    relevance_map: RelevanceMap = {
        attribute: {value: [] for value in values}
        for attribute, values in USER_PROFILE_ATTRIBUTES.items()
    }

    for index, (diff, summary) in enumerate(summaries, start=1):
        relevance = classify_page_relevance(diff, summary)
        for attribute, affected_values in relevance.affected.items():
            if attribute not in relevance_map:
                continue
            for value in affected_values:
                if value not in relevance_map[attribute]:
                    continue
                # TODO: classify per bullet instead of per page so each bullet
                # only lands in the slots it's relevant to, avoiding duplication
                # across multiple affected values.
                relevance_map[attribute][value].extend(summary.bullets)
        print(
            f"  Classified {index}/{len(summaries)} ({diff.change_type}): "
            f"{diff.url} — affects {sum(len(v) for v in relevance.affected.values())} value(s)"
        )

    return relevance_map

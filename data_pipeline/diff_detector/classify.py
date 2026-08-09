"""Stage 4 — classify: turn <data_dir>/summaries.json into <data_dir>/relevance.json,
a map of which user profile (attribute, value) pairs each change is relevant to."""

from __future__ import annotations

import argparse
import json
import os
import sys
from functools import lru_cache
from pathlib import Path

_pipeline_root = Path(__file__).resolve().parents[1]
if str(_pipeline_root) not in sys.path:
    sys.path.insert(0, str(_pipeline_root))

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langsmith import traceable
from pydantic import BaseModel, Field

from diff_detector.diff import PageDiff
from diff_detector.summarize import PageDiffSummary, load_summaries
from lib.config import RELEVANCE_FILENAME, SUMMARIES_FILENAME, ensure_run_dir
from lib.env import load_pipeline_env
from lib.user_attributes import USER_PROFILE_ATTRIBUTES

IND_DIFF_CLASSIFY_MODEL = os.getenv("IND_DIFF_CLASSIFY_MODEL", "gpt-4o-mini")

# Pre-rendered once for inclusion in the prompt
_ATTRIBUTES_JSON = json.dumps(USER_PROFILE_ATTRIBUTES, indent=2, ensure_ascii=False)

# One change relevant to a profile slot: the bullet text plus the page it came from,
# so the notification email can link the reader to the source.
RelevantChange = dict[str, str]  # {"text": ..., "url": ...}
RelevanceMap = dict[str, dict[str | bool, list[RelevantChange]]]

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


@traceable(
    run_type="chain",
    name="classify_page_relevance",
    tags=["classify_page_relevance"],
    process_inputs=lambda inputs: {
        "url": inputs["diff"].url,
        "change_type": inputs["diff"].change_type,
        "bullets": inputs["summary"].bullets,
    },
)
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

    Returns dict[attribute, dict[value, list[{text, url}]]] — each bullet keeps the URL
    of the page it came from. All (attribute, value) pairs are initialised; an empty
    list means no relevant changes.
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
                relevance_map[attribute][value].extend(
                    {"text": bullet, "url": diff.url} for bullet in summary.bullets
                )
        print(
            f"  Classified {index}/{len(summaries)} ({diff.change_type}): "
            f"{diff.url} — affects {sum(len(v) for v in relevance.affected.values())} value(s)"
        )

    return relevance_map


def _relevance_json_key(value: str | bool) -> str:
    """The string key json.dumps produces for a relevance-map value (bools → 'true'/'false')."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return value


def write_relevance(relevance_map: RelevanceMap, path: Path) -> Path:
    """Write the relevance map as JSON. Boolean value-keys are stored as 'true'/'false'."""
    path.write_text(json.dumps(relevance_map, indent=2, ensure_ascii=False))
    populated = sum(
        1 for values in relevance_map.values() for bullets in values.values() if bullets
    )
    print(f"Relevance map written to {path} ({populated} populated slot(s))")
    return path


def _as_relevant_change(entry: RelevantChange | str) -> RelevantChange:
    """Normalise one stored entry. Relevance files written before bullets carried a URL
    hold bare strings; those load with an empty url rather than breaking stage 5."""
    if isinstance(entry, str):
        return {"text": entry, "url": ""}
    return {"text": entry.get("text", ""), "url": entry.get("url", "")}


def load_relevance(path: Path) -> RelevanceMap:
    """Load relevance.json back into a RelevanceMap, restoring boolean value-keys.

    Rebuilt against USER_PROFILE_ATTRIBUTES so every allowed (attribute, value) slot
    is present, matching what build_relevance_map produces.
    """
    raw = json.loads(path.read_text())
    result: RelevanceMap = {}
    for attribute, values in USER_PROFILE_ATTRIBUTES.items():
        slot = raw.get(attribute, {})
        result[attribute] = {
            value: [
                _as_relevant_change(entry)
                for entry in slot.get(_relevance_json_key(value), [])
            ]
            for value in values
        }
    return result


# One span per `just classify` run; its totals are the whole stage's token spend.
@traceable(
    run_type="chain",
    name="ind_classify_stage",
    tags=["ind_classify_stage"],
    process_inputs=lambda inputs: {"data_dir": str(inputs.get("data_dir") or "default")},
    process_outputs=lambda relevance_map: {
        "populated_slots": {
            f"{attribute}={value}": len(bullets)
            for attribute, values in relevance_map.items()
            for value, bullets in values.items()
            if bullets
        }
    },
)
def run_classify_stage(data_dir: Path | str | None = None) -> RelevanceMap:
    """Read <data_dir>/summaries.json, classify relevance, write <data_dir>/relevance.json."""
    run_dir = ensure_run_dir(data_dir)
    summaries = load_summaries(run_dir / SUMMARIES_FILENAME)
    relevance_map = build_relevance_map(summaries)
    write_relevance(relevance_map, run_dir / RELEVANCE_FILENAME)
    return relevance_map


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Stage 4 — classify each summary in <data_dir>/summaries.json into a "
            "relevance map and write <data_dir>/relevance.json."
        )
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Run directory holding summaries.json (default: data/latest/).",
    )
    args = parser.parse_args()
    run_classify_stage(data_dir=args.data_dir)


if __name__ == "__main__":
    main()

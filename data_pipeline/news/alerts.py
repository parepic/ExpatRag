"""LLM classifier for Patty Watch news alerts."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from lib.env import load_pipeline_env


NEWS_ALERT_MODEL = os.getenv("PATTY_WATCH_NEWS_ALERT_MODEL", "gpt-4.1-mini")


class NewsAlertDecision(BaseModel):
    """Structured output for the news alert classifier."""

    alert: Literal[0, 1] = Field(
        description=(
            "1 if this news item should definitely trigger a Patty Watch alert; "
            "otherwise 0."
        )
    )
    reason: str = Field(description="Short reason for the decision.")


SYSTEM_PROMPT = """
You are LLM1 for Patty Watch, an alert filter for expats and international
residents in the Netherlands.

Your job is to decide whether a news item should definitely trigger a Patty
Watch alert.

Return 1 only when the title and summary strongly suggest a concrete impact on
a user's:
- legal status, immigration, visa, residency, naturalisation, or travel rights;
- taxes, benefits, salary, employment rights, leave, pension, fines, or household costs;
- housing rights, rent, mortgage/tax rules, tenant/landlord obligations;
- healthcare access, insurance obligations, education/student deadlines, or civic integration;
- privacy/security rights when there is likely user action, such as a data leak,
  claim, deadline, or warning;
- official procedure, eligibility rule, application deadline, mandatory
  obligation, or government relief program.

Return 0 for general news, weather, sports, rankings, lifestyle, entertainment,
commercial launches, market trends without a concrete rule/action, one-off
incidents, company branding, or local convenience updates.

Be strict. If the item might be interesting but is not definitely actionable or
rights/rules/money related, return 0.

Hypothetical examples:
- Title: "Residence permit fees to rise from January" -> 1
- Title: "New deadline announced for student finance applications" -> 1
- Title: "Amsterdam cafe opens a new terrace" -> 0
- Title: "Dutch beaches ranked among Europe's prettiest" -> 0
- Title: "Storm expected this weekend" -> 0

Return your answer using the required structured output schema.
""".strip()


NEWS_ALERT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "Title: {title}\nSummary: {summary}"),
    ]
)


@lru_cache(maxsize=1)
def _get_news_alert_chain():
    load_pipeline_env()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY must be set before classifying news.")

    llm = ChatOpenAI(
        model=os.getenv("PATTY_WATCH_NEWS_ALERT_MODEL", NEWS_ALERT_MODEL),
        temperature=0,
        api_key=api_key,
    )
    return NEWS_ALERT_PROMPT | llm.with_structured_output(NewsAlertDecision)


def classify_news_item(item: dict) -> NewsAlertDecision:
    """Classify one RSS news item using its title and summary only."""
    title = item.get("title") or ""
    summary = item.get("summary") or ""
    if not title.strip():
        return NewsAlertDecision(alert=0, reason="Missing title.")

    return _get_news_alert_chain().invoke(
        {
            "title": title,
            "summary": summary,
        }
    )


def classify_news_items(items: list[dict]) -> list[tuple[dict, NewsAlertDecision]]:
    """Classify a batch of RSS news items."""
    decisions: list[tuple[dict, NewsAlertDecision]] = []
    for index, item in enumerate(items, start=1):
        decision = classify_news_item(item)
        decisions.append((item, decision))
        print(
            f"  Classified {index}/{len(items)}: "
            f"alert={decision.alert} | {item.get('title', 'Untitled')}"
        )
    return decisions

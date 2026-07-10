"""
RAG evaluation using LangSmith.

Runs the full retrieval + generation pipeline against the golden dataset and
scores each result with two LLM-as-judge evaluators:
  - answer_correctness:   AI answer vs reference answer
  - retrieval_relevance:  Retrieved chunks vs the input question

Results are posted to the LangSmith project configured in the environment,
under a persistent named dataset so experiments can be compared over time.

Run with:
    uv run --project backend pytest backend/tests/test_rag_eval.py -v -s
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from langsmith import Client
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.services.rag_service import (
    _build_context,
    _format_user_profile,
    _get_retrieval_function,
    generate_grounded_answer,
)
from app.core.config import EMBEDDING_MODEL, LLM_MODEL, SEARCH_STRATEGY

GOLDEN_DATASET_PATH = Path(__file__).parent / "test_set" / "golden_dataset.json"
DATASET_NAME = "expatrag-golden-v1"

CORRECTNESS_THRESHOLD = 0.7
RELEVANCE_THRESHOLD = 0.7


# ---------------------------------------------------------------------------
# Configuration under test
# ---------------------------------------------------------------------------
# Every knob that defines this run's configuration is captured here, then both
# (a) used by the pipeline below and (b) recorded as experiment metadata, so runs
# can be grouped and compared by any of these keys in the LangSmith UI. Sweep
# settings without editing code by overriding via env, e.g.:
#   EVAL_CHUNKS_PER_SEARCH=8 EVAL_SIMILARITY_THRESHOLD=0.3 uv run ... pytest ...
AGENT_TYPE = os.getenv("EVAL_AGENT_TYPE", "direct")
CHUNKS_PER_SEARCH = int(os.getenv("EVAL_CHUNKS_PER_SEARCH", "5"))
SIMILARITY_THRESHOLD = float(os.getenv("EVAL_SIMILARITY_THRESHOLD", "0.0"))
VECTOR_WEIGHT = float(os.getenv("EVAL_VECTOR_WEIGHT", "0.5"))
KEYWORD_WEIGHT = float(os.getenv("EVAL_KEYWORD_WEIGHT", "0.5"))
NUMBER_OF_QUERIES = int(os.getenv("EVAL_NUMBER_OF_QUERIES", "3"))

# Full configuration recorded on every experiment. Flat scalar keys only, so each
# is groupable / chartable as an x-axis in LangSmith.
EXPERIMENT_CONFIG = {
    "search_strategy": SEARCH_STRATEGY,
    "embedding_model": EMBEDDING_MODEL,
    "llm_model": LLM_MODEL,
    "agent_type": AGENT_TYPE,
    "chunks_per_search": CHUNKS_PER_SEARCH,
    "similarity_threshold": SIMILARITY_THRESHOLD,
    "vector_weight": VECTOR_WEIGHT,
    "keyword_weight": KEYWORD_WEIGHT,
    "number_of_queries": NUMBER_OF_QUERIES,
}

# Short human-readable label for clean chart x-axes when comparing runs.
CONFIG_LABEL = f"{SEARCH_STRATEGY}|{LLM_MODEL}|k={CHUNKS_PER_SEARCH}|t={SIMILARITY_THRESHOLD}"


def _retrieval_kwargs() -> dict:
    """Build retrieval params for the configured strategy.

    Mirrors retrieve_rag_context_for_agent: only pass weights for hybrid strategies
    and number_of_queries for multi-query strategies, so each retrieval function
    receives exactly the kwargs it accepts.
    """
    kwargs: dict = {
        "match_count": CHUNKS_PER_SEARCH,
        "match_threshold": SIMILARITY_THRESHOLD,
    }
    strategy = SEARCH_STRATEGY.strip().lower()
    if "hybrid" in strategy:
        kwargs["vector_weight"] = VECTOR_WEIGHT
        kwargs["keyword_weight"] = KEYWORD_WEIGHT
    if "multi query" in strategy:
        kwargs["number_of_queries"] = NUMBER_OF_QUERIES
    return kwargs


# ---------------------------------------------------------------------------
# Dataset — created once in LangSmith, reused across experiment runs
# ---------------------------------------------------------------------------


def _get_or_create_dataset(client: Client) -> None:
    """Upload the golden dataset to LangSmith if it does not already exist."""
    if any(ds.name == DATASET_NAME for ds in client.list_datasets()):
        print(f"\nDataset '{DATASET_NAME}' already exists in LangSmith, skipping upload.")
        return

    golden = json.loads(GOLDEN_DATASET_PATH.read_text())
    dataset = client.create_dataset(
        DATASET_NAME,
        description="Golden Q&A pairs for ExpatRag RAG evaluation",
    )
    client.create_examples(
        dataset_id=dataset.id,
        examples=[
            {
                "inputs": {
                    "question": item["question"],
                    "user_info": item["user_info"],
                },
                "outputs": {
                    "expected_answer": item["expected_answer"],
                },
            }
            for item in golden
        ],
    )
    print(f"\nDataset '{DATASET_NAME}' created in LangSmith with {len(golden)} examples.")


# ---------------------------------------------------------------------------
# Target function — called once per example
# ---------------------------------------------------------------------------


def _rag_target(inputs: dict) -> dict:
    """Run the RAG pipeline with a question and user_info from the golden dataset.

    Bypasses the Supabase user lookup: user_info is passed directly, which is
    exactly what we have in the golden dataset.

    Returns both the generated answer and the retrieved chunks so that both
    evaluators (answer correctness and retrieval relevance) have what they need.
    """
    question: str = inputs["question"]
    user_info: dict = inputs["user_info"]

    retrieval_fn = _get_retrieval_function(SEARCH_STRATEGY)
    chunks = retrieval_fn(question, **_retrieval_kwargs())
    context = _build_context(chunks)
    user_profile_text = _format_user_profile(user_info)

    # Use the same generation step production serves (via the simple/supervisor agents),
    # so the eval reflects the live prompt instead of a diverging copy.
    response = generate_grounded_answer(
        question=question,
        context=context,
        user_profile_text=user_profile_text,
        chat_history=[],
    )
    return {
        "answer": response.answer.strip(),
        "retrieved_chunks": [
            {
                "source_title": c.get("source_title", ""),
                "source_url": c.get("source_url", ""),
                "content": c.get("content", "")[:400],
            }
            for c in chunks
        ],
    }


# ---------------------------------------------------------------------------
# Shared judge helpers
# ---------------------------------------------------------------------------


class _JudgeScore(BaseModel):
    score: float
    reasoning: str


def _make_judge() -> ChatOpenAI:
    return ChatOpenAI(model="gpt-4.1", temperature=0)


def _format_chunks_for_judge(chunks: list[dict]) -> str:
    parts = []
    for i, c in enumerate(chunks, start=1):
        title = c.get("source_title") or "Unknown"
        url = c.get("source_url") or ""
        content = c.get("content") or ""
        parts.append(f"[{i}] {title} ({url})\n{content}")
    return "\n\n---\n\n".join(parts) if parts else "No chunks retrieved."


# ---------------------------------------------------------------------------
# Evaluator 1 — Answer Correctness
# ---------------------------------------------------------------------------


_CORRECTNESS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are evaluating whether an AI assistant's answer correctly addresses a question compared to a reference answer.

Score the answer correctness from 0.0 to 1.0:
- 1.0: Completely correct, all key points from the reference are covered
- 0.7–0.9: Mostly correct, minor omissions or slight inaccuracies
- 0.4–0.6: Partially correct, missing important information
- 0.1–0.3: Some relevance but largely incorrect or misleading
- 0.0: Completely wrong or irrelevant

Respond with a JSON object with "score" (float 0.0–1.0) and "reasoning" (one sentence).""",
        ),
        (
            "human",
            "Question: {question}\n\nReference answer: {reference_answer}\n\nAI answer: {ai_answer}",
        ),
    ]
)


def answer_correctness(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    result: _JudgeScore = (_CORRECTNESS_PROMPT | _make_judge().with_structured_output(_JudgeScore)).invoke(
        {
            "question": inputs["question"],
            "reference_answer": reference_outputs["expected_answer"],
            "ai_answer": outputs["answer"],
        }
    )
    return {"key": "answer_correctness", "score": result.score, "comment": result.reasoning}


# ---------------------------------------------------------------------------
# Evaluator 2 — Retrieval Relevance
# ---------------------------------------------------------------------------


_RELEVANCE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are evaluating whether a set of retrieved document chunks is relevant to a user's question.

Score the overall retrieval relevance from 0.0 to 1.0:
- 1.0: All or most chunks are highly relevant and directly address the question
- 0.7–0.9: Most chunks are relevant, minor noise
- 0.4–0.6: Mixed — some relevant chunks but also significant irrelevant ones
- 0.1–0.3: Few relevant chunks, mostly off-topic
- 0.0: No chunks are relevant to the question

Respond with a JSON object with "score" (float 0.0–1.0) and "reasoning" (one sentence).""",
        ),
        (
            "human",
            "Question: {question}\n\nRetrieved chunks:\n{chunks}",
        ),
    ]
)


def retrieval_relevance(inputs: dict, outputs: dict) -> dict:
    chunks_text = _format_chunks_for_judge(outputs.get("retrieved_chunks", []))
    result: _JudgeScore = (_RELEVANCE_PROMPT | _make_judge().with_structured_output(_JudgeScore)).invoke(
        {
            "question": inputs["question"],
            "chunks": chunks_text,
        }
    )
    return {"key": "retrieval_relevance", "score": result.score, "comment": result.reasoning}


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------


def _extract_scores(results, key: str) -> list[float]:
    return [
        eval_result.score
        for result in results
        for eval_result in result["evaluation_results"]["results"]
        if eval_result.key == key and eval_result.score is not None
    ]


def _assert_threshold(scores: list[float], key: str, threshold: float) -> None:
    assert scores, f"No '{key}' scores were returned by the evaluator"
    avg = sum(scores) / len(scores)
    print(f"\n{key} scores: {[round(s, 2) for s in scores]}")
    print(f"{key} average: {avg:.2f}  (threshold: {threshold})")
    assert avg >= threshold, (
        f"{key} average {avg:.2f} is below the threshold of {threshold}"
    )


def test_rag_evaluation():
    client = Client()
    _get_or_create_dataset(client)

    results = client.evaluate(
        _rag_target,
        data=DATASET_NAME,
        evaluators=[answer_correctness, retrieval_relevance],
        experiment_prefix=f"expatrag-{SEARCH_STRATEGY.replace(' ', '-')}",
        metadata={
            "dataset": DATASET_NAME,
            "config_label": CONFIG_LABEL,
            **EXPERIMENT_CONFIG,
        },
    )

    _assert_threshold(
        _extract_scores(results, "answer_correctness"),
        "answer_correctness",
        CORRECTNESS_THRESHOLD,
    )
    _assert_threshold(
        _extract_scores(results, "retrieval_relevance"),
        "retrieval_relevance",
        RELEVANCE_THRESHOLD,
    )

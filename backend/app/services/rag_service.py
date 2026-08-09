"""RAG service: retrieves relevant chunks from Supabase + generates a reply via LangChain."""

from __future__ import annotations

import os
from functools import lru_cache
from dotenv import load_dotenv
from typing import List, Callable, Any, Optional, Dict
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langsmith import traceable
from pydantic import BaseModel, Field

from app.core.config import EMBEDDING_MODEL, LLM_MODEL, SEARCH_STRATEGY
from app.core.logging import get_logger
from app.core.supabase_client import supabase
from app.services.rag_utils import reciprocal_rank_fusion

load_dotenv()
logger = get_logger(__name__)

class QueryVariations(BaseModel):
    variations: List[str]=Field(..., description="Query variations generated for Multi Query Search")

class RAGAnswer(BaseModel):
    answer: str = Field(description="Final answer to show to the user")
    used_chunk_refs: list[int] = Field(
        default_factory=list,
        description="Subset of candidate chunk references (1..N) actually used to answer",
    )
    answers_question: bool = Field(
        default=True,
        description=(
            "True only if the retrieved context actually answers the question that was asked. "
            "False when the context merely covers the general topic while missing the specific "
            "thing asked, or when answering would require knowledge beyond the context."
        ),
    )


# ---------------------------------------------------------------------------
# Lazy-initialised singletons
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _get_embeddings() -> OpenAIEmbeddings:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY must be set")
    return OpenAIEmbeddings(model=EMBEDDING_MODEL)


@lru_cache(maxsize=1)
def _get_llm() -> ChatOpenAI:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY must be set")
    return ChatOpenAI(model=LLM_MODEL, temperature=0.2)


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------

@traceable(run_type="retriever", name="vector_search_retrieval")
def vector_search(
    question: str,
    match_count: int | None = None,
    match_threshold: float | None = None,
) -> list[dict]:
    """Return the top-k most relevant document chunks for *question* using VECTOR SEARCH"""
    embedding_vector = _get_embeddings().embed_query(question)

    result = supabase.rpc(
        "match_document_chunks",
        {
            "query_embedding": embedding_vector,
            "match_threshold": match_threshold,
            "match_count": match_count,
        },
    ).execute()
    logger.info("vector_search_results", result_count=len(result.data or []))
    return result.data or []


@traceable(run_type="retriever", name="keyword_search_retrieval")
def _keyword_search(
    question: str,
    match_count: int | None = None,
) -> list[dict]:
    """Return the top-k most relevant document chunks for *question* using KEYWORD SEARCH"""
    result = supabase.rpc(
        "keyword_search_document_chunks",
        {
            "query_text": question,
            "match_count": match_count,
        },
    ).execute()
    logger.info("keyword_search_results", result_count=len(result.data or []))
    return result.data or []

@traceable(run_type="retriever", name="hybrid_search_retrieval")
def hybrid_search(
    question: str,
    match_count: int | None = None,
    match_threshold: float | None = None,
    vector_weight: float | None = None,
    keyword_weight: float | None = None,
) -> list[dict]:
    vector_search_results = vector_search(
        question, match_count=match_count, match_threshold=match_threshold
    )
    keyword_search_results = _keyword_search(question, match_count=match_count)

    vw = vector_weight if vector_weight is not None else 0.5
    kw = keyword_weight if keyword_weight is not None else 1.0 - vw

    return reciprocal_rank_fusion([vector_search_results, keyword_search_results], weights=[vw, kw])

@traceable(run_type="retriever", name="multi_query_vector_search_retrieval")
def multi_query_vector_search(
    question: str,
    number_of_queries: int | None = None,
    match_count: int | None = None,
    match_threshold: float | None = None,

) -> list[dict]:
    queries = _generate_query_variations(question, num_queries=number_of_queries or 3)
    logger.info("multi_query_vector_search_started", query_count=len(queries))
    all_results = []
    for i, query in enumerate(queries):
        results = vector_search(query, match_count=match_count, match_threshold=match_threshold)
        logger.info(
            "multi_query_vector_search_iteration",
            query_index=i + 1,
            query=query,
            result_count=len(results),
        )
        all_results.append(results)
    return reciprocal_rank_fusion(all_results)

@traceable(run_type="retriever", name="multi_query_hybrid_search_retrieval")
def multi_query_hybrid_search(
    question: str,
    number_of_queries: int | None = None,
    match_count: int | None = None,
    match_threshold: float | None = None,
    vector_weight: float | None = None,
    keyword_weight: float | None = None,
) -> list[dict]:
    queries = _generate_query_variations(question, num_queries=number_of_queries or 3)
    logger.info("multi_query_hybrid_search_started", query_count=len(queries))
    all_results = []
    for i, query in enumerate(queries):
        results = hybrid_search(
            query,
            match_count=match_count,
            match_threshold=match_threshold,
            vector_weight=vector_weight,
            keyword_weight=keyword_weight,
        )
        logger.info(
            "multi_query_hybrid_search_iteration",
            query_index=i + 1,
            query=query,
            result_count=len(results),
        )
        all_results.append(results)
    # When fusing multiple hybrid runs, keep the same weighting per-source group
    # (each inner list is already a fusion of vector+keyword). We pass None to
    # reciprocal_rank_fusion so it uses equal weights across the multi-query runs.
    return reciprocal_rank_fusion(all_results)


def _get_retrieval_function(strategy: str) -> Callable[..., list[dict]]:
    strategy_to_function: dict[str, Callable[[str], list[dict]]] = {
        "vector search": vector_search,
        "hybrid search": hybrid_search,
        "multi query vector search": multi_query_vector_search,
        "multi query hybrid search": multi_query_hybrid_search,
    }
    normalized_strategy = strategy.strip().lower()
    retrieval_function = strategy_to_function.get(normalized_strategy)
    if retrieval_function is None:
        valid_strategies = ", ".join(sorted(strategy_to_function.keys()))
        raise ValueError(
            f"Unsupported retrieval strategy '{strategy}'. Valid options: {valid_strategies}"
        )
    return retrieval_function


@traceable(run_type="retriever", name="generate_query_variations")
def _generate_query_variations(user_query: str, num_queries: int = 3) -> list[str]:
    """
        Take the original query and make multiple variations of it. Used in multi query search strategies.
    """
    system_prompt = f"""Generate {num_queries-1} alternative ways to phrase this questions for document search. Use different keywords and synonyms while maintaining the same intent. Return exactly {num_queries-1} variations."""

    logger.info("generating_query_variations", requested_count=num_queries)
    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Original query: {user_query}")
        ]
        structured_llm = _get_llm().with_structured_output(QueryVariations)
        result: QueryVariations = structured_llm.invoke(messages)
        logger.info("query_variations_generated", requested_count=num_queries, returned_count=len(result.variations) + 1)
        return [user_query, *result.variations][:num_queries]
    
    except Exception as e:
        logger.error("query_variation_generation_failed", error=str(e), exc_info=True)
        return [user_query]

# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------


def _build_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a single context string for the prompt."""
    parts: list[str] = []
    for i, chunk in enumerate(chunks, start=1):
        title = chunk.get("source_title") or "Unknown source"
        url = chunk.get("source_url") or ""
        content = chunk.get("content", "")
        header = f"[{i}] chunk_ref={i} | {title}" + (f" ({url})" if url else "")
        parts.append(f"{header}\n{content}")
    return "\n\n---\n\n".join(parts) if parts else "No relevant context found."


def _load_user_profile(user_id: str) -> dict:
    user_result = (
        supabase.table("users")
        .select(
            "nationality, purpose_of_stay, reason_for_visit,"
            "employment_status, registration_status, has_fiscal_partner,"
            "salary_band, age_bracket_under_30, prior_nl_residency, languages"
        )
        .eq("id", user_id)
        .limit(1)
        .execute()
    )
    if not user_result.data:
        return {}
    return user_result.data[0]


def _format_user_profile(user_profile: dict) -> str:
    if not user_profile:
        return "No user profile available."

    profile_lines: list[str] = []
    for key, value in user_profile.items():
        if value is None:
            continue
        label = key.replace("_", " ")
        profile_lines.append(f"- {label}: {value}")

    return "\n".join(profile_lines) if profile_lines else "No user profile available."


# ---------------------------------------------------------------------------
# Shared prompt context (domain + user profile)
# ---------------------------------------------------------------------------

DEFAULT_DOMAIN_CONTEXT = (
    "This assistant supports expats living in or relocating to the Netherlands. "
    "The project knowledge base contains guidance on Dutch immigration and residence permits (IND), "
    "the 30% ruling and income tax, BSN and municipal registration (gemeente), housing and rental rules, "
    "health insurance and healthcare, banking, and employment. "
    "Treat questions as relating to the Netherlands unless the user clearly states otherwise."
)


def get_domain_context(project_settings: Optional[Dict[str, Any]] = None) -> str:
    """Return the per-project corpus description if configured, else the default domain context.

    Looks for an optional ``corpus_description`` field on ``project_settings`` so the domain framing
    can be tuned per project without code changes; falls back to :data:`DEFAULT_DOMAIN_CONTEXT`.

    Args:
        project_settings: The project settings row (may be empty/None).

    Returns:
        A short description of what the knowledge base covers.
    """
    if project_settings:
        description = project_settings.get("corpus_description")
        if description and str(description).strip():
            return str(description).strip()
    return DEFAULT_DOMAIN_CONTEXT


def _format_profile_section(user_profile_text: Optional[str]) -> str:
    """Build a system-prompt section for the user profile, or empty string if unavailable."""
    if not user_profile_text or user_profile_text.strip() == "No user profile available.":
        return ""
    return (
        "\n### Current User Profile\n"
        "Use these details to interpret the question and to phrase the search queries you run "
        "(for example, nationality can change which immigration or tax rules apply). "
        "Do not repeat the profile back to the user unless they ask.\n\n"
        f"{user_profile_text}\n"
    )


def _build_chat_history(history: list[dict]) -> list[HumanMessage | AIMessage]:
    """Convert raw message dicts into LangChain message objects."""
    messages: list[HumanMessage | AIMessage] = []
    for msg in history:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    return messages


def _load_project_settings(user_id: str):
    logger.info("fetching_retrieval_settings", user_id=user_id)
    result = (
        supabase.table("project_settings")
        .select("*")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    data = result.data or []
    if not data:
        logger.info("no_project_settings_found", user_id=user_id)
        return {}

    settings = data[0]
    logger.info("project_settings_fetched", user_id=user_id, project_settings=settings)
    return settings



def retrieve_rag_context_for_agent(
    user_id: str,
    question: str,
) -> tuple[str, list[dict], str]:
    """Retrieve context/citations for agent tools without running final legacy generation."""
    logger.info(
        "rag_context_retrieval_for_agent_started",
        user_id=user_id,
        retrieval_strategy=SEARCH_STRATEGY,
    )

    project_settings = _load_project_settings(user_id=user_id) or {}

    # build params from project settings
    chunks_per_search = project_settings.get("chunks_per_search")
    similarity_threshold = project_settings.get("similarity_threshold")
    vector_weight = project_settings.get("vector_weight")
    keyword_weight = project_settings.get("keyword_weight")
    num_queries = project_settings.get("number_of_queries")

    logger.info("RAG STRATEGGY", rag_strategy=project_settings.get("rag_strategy"))
    retrieval_function = _get_retrieval_function(project_settings.get("rag_strategy"))

    # Build kwargs based on which retrieval function is being used
    kwargs = {
        "question": question,
        "match_count": chunks_per_search,
        "match_threshold": similarity_threshold,
    }
    
    strategy = project_settings.get("rag_strategy", "").strip().lower()
    if "hybrid" in strategy:
        kwargs["vector_weight"] = vector_weight
        kwargs["keyword_weight"] = keyword_weight
    if "multi query" in strategy:
        kwargs["number_of_queries"] = num_queries

    chunks = retrieval_function(**kwargs)

    context = _build_context(chunks)
    user_profile = _load_user_profile(user_id)
    user_profile_text = _format_user_profile(user_profile)

    citations = [
        {
            "chunk_ref": idx,
            "chunk_id": str(chunk.get("id", "")),
            "source_id": str(chunk.get("source_id", "")),
            "source_title": chunk.get("source_title"),
            "source_url": chunk.get("source_url"),
            "page_number": chunk.get("page_number"),
            "similarity": chunk.get("similarity"),
        }
        for idx, chunk in enumerate(chunks, start=1)
    ]

    logger.info(
        "rag_context_retrieval_for_agent_completed",
        user_id=user_id,
        retrieved_chunk_count=len(chunks),
        citation_count=len(citations),
    )
    return context, citations, user_profile_text


def generate_grounded_answer(
    question: str,
    context: str,
    user_profile_text: str,
    chat_history: list[dict] | None = None,
) -> RAGAnswer:
    """Generate a grounded answer plus the chunk refs the model actually relied on.

    The context blocks built by :func:`_build_context` are labelled with ``chunk_ref=N``.
    Using structured output, the model returns both the ``answer`` and ``used_chunk_refs`` so
    callers can show citations for the used chunks only (instead of every retrieved chunk).

    Args:
        question: The user's question.
        context: The formatted, chunk-ref-labelled context string.
        user_profile_text: Formatted user profile (or a "no profile" sentinel).
        chat_history: Optional prior turns to provide conversational context.

    Returns:
        A :class:`RAGAnswer` with the answer text and the chunk refs used.
    """
    instructions = (
        "Use the retrieved context to answer the user question. Stay grounded in the provided "
        "information and do not invent facts beyond it. Each context block is labelled with a "
        "chunk_ref number. In used_chunk_refs, return ONLY the chunk_ref numbers you actually "
        "relied on to write the answer; omit any chunk you did not use.\n\n"
        "Set answers_question to false whenever the context does not actually answer what was "
        "asked — including when it discusses the general topic but omits the specific detail "
        "requested, or when you would need knowledge beyond the context to be useful. Judge the "
        "context, not your own knowledge: if you find yourself about to write that the documents "
        "do not specify something, answers_question is false.\n\n"
        f"User profile:\n{user_profile_text}\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{question}"
    )

    messages: list[HumanMessage | AIMessage] = _build_chat_history(chat_history or [])
    messages.append(HumanMessage(content=instructions))

    structured_llm = _get_llm().with_structured_output(RAGAnswer)
    return structured_llm.invoke(messages)


def filter_citations_by_used_refs(
    citations: list[dict],
    used_chunk_refs: list[int],
) -> list[dict]:
    """Keep only the citations whose ``chunk_ref`` is in ``used_chunk_refs`` (order preserved).

    Refs that do not match any retrieved citation (e.g. a hallucinated number) are dropped.
    """
    used = set(used_chunk_refs)
    return [citation for citation in citations if citation.get("chunk_ref") in used]


@traceable(run_type="chain", name="generate_rag_reply")
def generate_rag_reply(
    user_id: str,
    question: str,
    agent_type: str,
    chat_history: list[dict] | None = None,
) -> tuple[str, list[dict]]:

    if agent_type == "simple":
        logger.info("rag_reply_generation_via_simple_agent", user_id=user_id)
        from app.agents.simple_agent.simple_agent import run_simple_agent_reply
        return run_simple_agent_reply(
            user_id=user_id,
            question=question,
            chat_history=chat_history,
            model=LLM_MODEL,
        )

    logger.info("rag_reply_generation_via_supervisor_agent", user_id=user_id)
    from app.agents.supervisor_agent.supervisor_agent import run_supervisor_agent_reply
    return run_supervisor_agent_reply(
        user_id=user_id,
        question=question,
        chat_history=chat_history,
        model=LLM_MODEL,
    )
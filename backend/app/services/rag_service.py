"""RAG service: retrieves relevant chunks from Supabase + generates a reply via LangChain."""

from __future__ import annotations

import os
from functools import lru_cache
from dotenv import load_dotenv
from typing import List, Callable
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langsmith import traceable
from pydantic import BaseModel, Field

from app.core.config import EMBEDDING_MODEL, LLM_MODEL, RAG_MATCH_COUNT, RAG_MATCH_THRESHOLD, SEARCH_STRATEGY
from app.core.prompts import RAG_PROMPT
from app.core.supabase_client import supabase
from app.services.rag_utils import reciprocal_rank_fusion

load_dotenv()

class QueryVariations(BaseModel):
    variations: List[str]=Field(..., description="Query variations generated for Multi Query Search")

class RAGAnswer(BaseModel):
    answer: str = Field(description="Final answer to show to the user")
    used_chunk_refs: list[int] = Field(
        default_factory=list,
        description="Subset of candidate chunk references (1..N) actually used to answer",
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
# Retrieval
# ---------------------------------------------------------------------------

# Add Hybrid Search and Keyword Search here.

@traceable(run_type="retriever", name="context_retrieval")
def vector_search(question: str) -> list[dict]:
    """Return the top-k most relevant document chunks for *question* using VECTOR SEARCH"""
    embedding_vector = _get_embeddings().embed_query(question)

    result = supabase.rpc(
        "match_document_chunks",
        {
            "query_embedding": embedding_vector,
            "match_threshold": RAG_MATCH_THRESHOLD,
            "match_count": RAG_MATCH_COUNT,
        },
    ).execute()

    return result.data or []


@traceable(run_type="retriever", name="context_retrieval")
def _keyword_search(question: str) -> list[dict]:
    """Return the top-k most relevant document chunks for *question* using KEYWORD SEARCH"""
    result = supabase.rpc(
        "keyword_search_document_chunks",
        {
            "query_text": question,
            "match_count": RAG_MATCH_COUNT,
        },
    ).execute()

    return result.data or []

@traceable(run_type="retriever", name="context_retrieval")
def hybrid_search(question: str) -> list[dict]:
    vector_search_results = vector_search(question)
    keyword_search_results = _keyword_search(question)

    return reciprocal_rank_fusion([vector_search_results, keyword_search_results])

@traceable(run_type="retriever", name="context_retrieval")
def multi_query_vector_search(question: str) -> list[dict]:
    queries = _generate_query_variations(question)
    all_results = []
    for i, query in enumerate(queries):
        results = vector_search(query)
        print(f"Query {i+1}: {query}\nReturned {len(results)} chunks\n\n")
        all_results.append(results)
    return reciprocal_rank_fusion(all_results)

@traceable(run_type="retriever", name="context_retrieval")
def multi_query_hybrid_search(question: str) -> list[dict]:
    queries = _generate_query_variations(question)
    all_results = []
    for i, query in enumerate(queries):
        results = hybrid_search(query)
        print(f"Query {i+1}: {query}\nReturned {len(results)} chunks\n\n")
        all_results.append(results)
    return reciprocal_rank_fusion(all_results)


def _get_retrieval_function(strategy: str) -> Callable[[str], list[dict]]:
    strategy_to_function: dict[str, Callable[[str], list[dict]]] = {
        "basic": vector_search,
        "hybrid": hybrid_search,
        "multi-query-vector": multi_query_vector_search,
        "multi-query-hybrid": multi_query_hybrid_search,
    }
    normalized_strategy = strategy.strip().lower()
    retrieval_function = strategy_to_function.get(normalized_strategy)
    if retrieval_function is None:
        valid_strategies = ", ".join(sorted(strategy_to_function.keys()))
        raise ValueError(
            f"Unsupported retrieval strategy '{strategy}'. Valid options: {valid_strategies}"
        )
    return retrieval_function



@traceable(run_type="retriever", name="context_retrieval")
def _generate_query_variations(user_query: str, num_queries: int = 3) -> list[str]:
    """
        Take the original query and make multiple variations of it. Used in multi query search strategies.
    """
    system_prompt = f"""Generate {num_queries-1} alternative ways to phrase this questions for document search. Use different keywords and synonyms while maintaining the same intent. Return exactly {num_queries-1} variations."""

    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Original query: {user_query}")
        ]
        structured_llm = _get_llm().with_structured_output(QueryVariations)
        result: QueryVariations = structured_llm.invoke(messages)
        return [user_query, *result.variations][:num_queries]
    
    except Exception as e:
        print(f"Cannot generate query variations. Reason: {str(e)}")
        import traceback
        traceback.print_exc()
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
            "username, nationality, purpose_of_stay, reason_for_visit,"
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


def generate_rag_reply(
    user_id: str,
    question: str,
    chat_history: list[dict] | None = None,
) -> tuple[str, list[dict]]:
    """Generate an LLM reply using retrieved context.

    Parameters
    ----------
    user_id:
        User ID used to load optional profile data for personalization.
    question:
        The user's latest message.
    chat_history:
        Ordered list of previous message dicts (``{"role": ..., "content": ...}``).
        Most recent messages last.

    Returns
    -------
    (reply_text, citations)
        *reply_text* is the assistant's answer.
        *citations* is a list of dicts carrying source metadata for storage in
        the ``messages.citations`` JSONB column.
    """

    
    retrieval_function = _get_retrieval_function(SEARCH_STRATEGY)
    chunks = retrieval_function(
        question,
        langsmith_extra={
            "tags": ["expatrag", "backend", "retrieval", "supabase"],
            "metadata": {
                "user_id": user_id,
                "embedding_model": EMBEDDING_MODEL,
                "retrieval_strategy": retrieval_function,
                "rag_match_count": RAG_MATCH_COUNT,
                "rag_match_threshold": RAG_MATCH_THRESHOLD,
                "question_char_count": len(question),
            },
        },
    )
    context = _build_context(chunks)
    user_profile = _load_user_profile(user_id)
    user_profile_text = _format_user_profile(user_profile)
    chunk_ref_map = {index: chunk for index, chunk in enumerate(chunks, start=1)}
    candidate_chunk_refs = list(chunk_ref_map.keys())

    lc_history = _build_chat_history(chat_history or [])

    chain = (RAG_PROMPT | _get_llm().with_structured_output(RAGAnswer)).with_config(
        {
            "run_name": "expatrag_rag_reply",
            "tags": ["expatrag", "backend", "rag"],
            "metadata": {
                "llm_model": LLM_MODEL,
                "embedding_model": EMBEDDING_MODEL,
                "rag_match_count": RAG_MATCH_COUNT,
            },
        }
    )
    response: RAGAnswer = chain.invoke(
        {
            "context": context,
            "question": question,
            "chat_history": lc_history,
            "user_profile": user_profile_text,
            "candidate_chunk_refs": ", ".join(str(chunk_ref) for chunk_ref in candidate_chunk_refs)
            if candidate_chunk_refs
            else "none",
        },
        config={
            "metadata": {
                "user_id": user_id,
                "question_char_count": len(question),
                "retrieved_chunk_count": len(chunks),
            }
        },
    )
    reply_text = response.answer.strip()
    valid_used_chunk_refs = [
        chunk_ref
        for chunk_ref in response.used_chunk_refs
        if chunk_ref in chunk_ref_map
    ]

    citations = [
        {
            "chunk_ref": chunk_ref,
            "chunk_id": str(chunk_ref_map[chunk_ref].get("id", "")),
            "source_id": str(chunk_ref_map[chunk_ref].get("source_id", "")),
            "source_title": chunk_ref_map[chunk_ref].get("source_title"),
            "source_url": chunk_ref_map[chunk_ref].get("source_url"),
            "page_number": chunk_ref_map[chunk_ref].get("page_number"),
            "similarity": chunk_ref_map[chunk_ref].get("similarity"),
        }
        for chunk_ref in valid_used_chunk_refs
    ]

    return reply_text, citations

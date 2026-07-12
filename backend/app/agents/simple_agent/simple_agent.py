"""Simple LangGraph RAG agent adapted for this repository.

This module intentionally keeps the imported simple-agent shape, but uses the
existing `rag_service` retrieval/generation pipeline under the hood.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from typing_extensions import Annotated

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools.base import InjectedToolCallId
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.types import Command

from app.core.config import LLM_MODEL
from app.core.logging import get_logger


# =============================================================================
# STATE DEFINITION
# =============================================================================

logger = get_logger(__name__)


class CustomAgentState(MessagesState):
    """State that accumulates citations across tool calls."""

    citations: Annotated[List[Dict[str, Any]], lambda x, y: x + y] = []


# =============================================================================
# PROMPTS
# =============================================================================

BASE_SYSTEM_PROMPT = """You are ExpatRag, a helpful AI assistant.

For every user question:

1. Call the `rag_search` tool first, using the knowledge base domain and the user profile (when provided) to phrase a precise search query.
2. Ground your answer in the tool result.
3. If information is insufficient, say so clearly.
4. Keep responses concise and practical.
"""


def get_system_prompt(
    domain_context: Optional[str] = None,
    user_profile_text: Optional[str] = None,
) -> str:
    """Get system prompt for the simple agent.

    Conversation history is supplied at invoke time as prior messages, not via the
    system prompt, so it is not handled here.

    Args:
        domain_context: Optional description of what the knowledge base covers.
        user_profile_text: Optional formatted user profile for personalization.
    """
    # Local import keeps the established circular-import-safe pattern with rag_service.
    from app.services.rag_service import _format_profile_section

    prompt = BASE_SYSTEM_PROMPT

    if domain_context:
        prompt += f"\n### Knowledge Base Domain\n{domain_context}\n"

    prompt += _format_profile_section(user_profile_text)

    return prompt


def create_rag_tool(user_id: str):
    """Create a tool that proxies to the existing RAG pipeline."""

    @tool
    def rag_search(
        query: str,
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        """Retrieve grounded context and citations for the agent to synthesize an answer."""
        try:
            # Local import avoids circular import at module load time.
            from app.services.rag_service import (
                retrieve_rag_context_for_agent,
                generate_grounded_answer,
                filter_citations_by_used_refs,
            )

            context, citations, user_profile_text = retrieve_rag_context_for_agent(
                user_id=user_id,
                question=query,
            )

            if not citations:
                return Command(
                    update={
                        "messages": [
                            ToolMessage(
                                content="No relevant context was found in the indexed documents.",
                                tool_call_id=tool_call_id,
                            )
                        ]
                    },
                )

            # Generate a grounded answer and let the model report which chunks it actually used,
            # so only those are surfaced as citations (not every retrieved chunk).
            rag_answer = generate_grounded_answer(
                question=query,
                context=context,
                user_profile_text=user_profile_text,
            )
            used_citations = filter_citations_by_used_refs(citations, rag_answer.used_chunk_refs)

            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content=rag_answer.answer,
                            tool_call_id=tool_call_id,
                        )
                    ],
                    "citations": used_citations,
                },
            )
        except Exception as e:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            f"Error retrieving information: {str(e)}",
                            tool_call_id=tool_call_id,
                        )
                    ]
                }
            )

    return rag_search


# =============================================================================
# GRAPH NODES
# =============================================================================

def pass_through_node(_: CustomAgentState) -> Dict[str, Any]:
    """Compatibility node for keeping the simple graph shape."""
    return {}


# =============================================================================
# AGENT CREATION
# =============================================================================

def create_simple_rag_agent(
    user_id: str,
    model: str = LLM_MODEL,
):
    """Create a simple tool-calling RAG agent for this repository.

    Conversation history is supplied at invoke time as prior messages (see
    run_simple_agent_reply), not baked into the system prompt. History is a sliding
    window of recent turns, which bounds token cost as chats grow.
    """
    # Local import keeps the established circular-import-safe pattern with rag_service.
    from app.services.rag_service import (
        get_domain_context,
        _load_project_settings,
        _load_user_profile,
        _format_user_profile,
    )

    project_settings = _load_project_settings(user_id=user_id) or {}
    domain_context = get_domain_context(project_settings)
    user_profile_text = _format_user_profile(_load_user_profile(user_id))

    tools = [create_rag_tool(user_id=user_id)]
    system_prompt = get_system_prompt(
        domain_context=domain_context,
        user_profile_text=user_profile_text,
    )

    base_agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        state_schema=CustomAgentState,
    ).with_config({"recursion_limit": 5})

    workflow = StateGraph(CustomAgentState)

    workflow.add_node("pass_through", pass_through_node)
    workflow.add_node("agent", base_agent)

    workflow.add_edge(START, "pass_through")
    workflow.add_edge("pass_through", "agent")
    workflow.add_edge("agent", END)

    return workflow.compile()


def run_simple_agent_reply(
    user_id: str,
    question: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
    model: str = LLM_MODEL,
) -> tuple[str, list[dict]]:
    """Invoke the simple agent and return (answer, citations).

    ``chat_history`` is a sliding window of recent turns, fed to the agent as prior
    messages; the current question is the final message.
    """
    from app.services.rag_service import _build_chat_history

    agent = create_simple_rag_agent(user_id=user_id, model=model)
    history_messages = _build_chat_history(chat_history or [])
    result = agent.invoke(
        {"messages": [*history_messages, HumanMessage(content=question)]}
    )

    messages = result.get("messages", [])
    reply_text = ""
    for msg in reversed(messages):
        content = getattr(msg, "content", "")
        if isinstance(content, str) and content.strip():
            reply_text = content.strip()
            break

    citations = result.get("citations", []) or []
    logger.info("simple_agent_completed", citation_count=len(citations))
    return reply_text, citations
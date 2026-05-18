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

1. Call the `rag_search` tool first.
2. Ground your answer in the tool result.
3. If information is insufficient, say so clearly.
4. Keep responses concise and practical.
"""


def format_chat_history(chat_history: List[Dict[str, str]]) -> str: 
    """
    Format chat history into a readable string for the system prompt.
    
    Args:
        chat_history: List of message dictionaries with 'role' and 'content' keys
        
    Returns:
        Formatted string representation of the chat history
        
    Example:
        >>> history = [
        ...     {"role": "user", "content": "What is attention?"},
        ...     {"role": "assistant", "content": "Attention is a mechanism..."}
        ... ]
        >>> formatted = format_chat_history(history)
        >>> print(formatted)
        User: What is attention?
        Assistant: Attention is a mechanism...
    """
    if not chat_history:
        return ""
    
    formatted_messages = []
    for msg in chat_history:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        # Format: "User Message: message" or "AI Message: message"
        role_label = "User Message" if role.lower() == "user" else "AI Message"
        formatted_messages.append(f"{role_label}: {content}")
    
    return "\n\n".join(formatted_messages)


def get_system_prompt(chat_history: Optional[List[Dict[str, str]]] = None) -> str:
    """Get system prompt for the simple agent."""
    prompt = BASE_SYSTEM_PROMPT
    
    if chat_history:
        formatted_history = format_chat_history(chat_history)
        if formatted_history:
            prompt += "\n\n### Previous Conversation Context\n"
            prompt += "The following is the recent conversation history for context:\n\n"
            prompt += formatted_history
            prompt += "\n\nUse this conversation history to understand context and references in the current question."
    
    return prompt 


def create_rag_tool(user_id: str, chat_history: Optional[List[Dict[str, str]]] = None):
    """Create a tool that proxies to the existing RAG pipeline."""

    @tool
    def rag_search(
        query: str,
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        """Retrieve grounded context and citations for the agent to synthesize an answer."""
        try:
            # Local import avoids circular import at module load time.
            from app.services.rag_service import retrieve_rag_context_for_agent

            context, citations, user_profile_text = retrieve_rag_context_for_agent(
                user_id=user_id,
                question=query,
            )

            if not citations:
                context = "No relevant context was found in the indexed documents."

            response = (
                "Use the retrieved context below to answer the user question. "
                "Do not invent facts beyond this context.\n\n"
                f"User profile:\n{user_profile_text}\n\n"
                f"Retrieved context:\n{context}"
            )

            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content=response,
                            tool_call_id=tool_call_id,
                        )
                    ],
                    "citations": citations,
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
    chat_history: Optional[List[Dict[str, str]]] = None,
):
    """Create a simple tool-calling RAG agent for this repository."""
    tools = [create_rag_tool(user_id=user_id, chat_history=chat_history)]
    system_prompt = get_system_prompt(chat_history=chat_history)

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
    """Invoke the simple agent and return (answer, citations)."""
    agent = create_simple_rag_agent(
        user_id=user_id,
        model=model,
        chat_history=chat_history,
    )
    result = agent.invoke({"messages": [HumanMessage(content=question)]})

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
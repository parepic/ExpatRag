from datetime import datetime, timezone

from fastapi import HTTPException

from app.core.config import CHAT_HISTORY_WINDOW
from app.core.logging import get_logger
from app.core.supabase_client import supabase
from app.services.rag_service import generate_rag_reply, _load_project_settings


logger = get_logger(__name__)


def _store_user_message(user_id: str, chat_id: str, message: str) -> dict:
    logger.info("storing_user_message", user_id=user_id, chat_id=chat_id)
    user_message_result = (
        supabase.table("messages")
        .insert({
            "chat_id": chat_id,
            "user_id": user_id,
            "role": "user",
            "content": message,
        })
        .execute()
    )
    if not user_message_result.data:
        logger.error("user_message_store_failed", user_id=user_id, chat_id=chat_id)
        raise HTTPException(status_code=500, detail="Failed to store user message")

    logger.info("user_message_stored", user_id=user_id, chat_id=chat_id)
    return user_message_result.data[0]


def _store_assistant_message(chat_id: str, content: str, citations: list[dict]) -> dict:
    logger.info("storing_assistant_message", chat_id=chat_id, citation_count=len(citations))
    assistant_message_result = (
        supabase.table("messages")
        .insert({
            "chat_id": chat_id,
            "role": "assistant",
            "content": content,
            "citations": citations,
        })
        .execute()
    )
    if not assistant_message_result.data:
        logger.error("assistant_message_store_failed", chat_id=chat_id)
        raise HTTPException(status_code=500, detail="Failed to store assistant message")

    logger.info("assistant_message_stored", chat_id=chat_id)
    return assistant_message_result.data[0]


def _load_chat_history(chat_id: str, limit: int = CHAT_HISTORY_WINDOW) -> list[dict]:
    """Load the most recent ``limit`` messages for a chat, in chronological order."""
    logger.info("loading_chat_history", chat_id=chat_id, limit=limit)
    history_result = (
        supabase.table("messages")
        .select("role, content")
        .eq("chat_id", chat_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    rows = list(reversed(history_result.data or []))
    logger.info("chat_history_loaded", chat_id=chat_id, message_count=len(rows))
    return rows


def create_chat(user_id: str, message: str) -> dict:
    logger.info("creating_chat_record", user_id=user_id, message_length=len(message))
    now = datetime.now(timezone.utc).isoformat()

    chat_result = (
        supabase.table("chats")
        .insert({
            "user_id": user_id,
            "title": message[:60],
            "created_at": now,
        })
        .execute()
    )
    if not chat_result.data:
        logger.error("chat_create_failed", user_id=user_id)
        raise HTTPException(status_code=500, detail="Failed to create chat")

    chat_id = chat_result.data[0]["id"]
    logger.info("chat_record_created", user_id=user_id, chat_id=chat_id)
    user_message = _store_user_message(user_id=user_id, chat_id=chat_id, message=message)

    project_settings = _load_project_settings(user_id)
    reply_text, citations = generate_rag_reply(
        user_id=user_id,
        question=message,
        agent_type=project_settings.get("agent_type"),
        chat_history=[],
    )
    logger.info("rag_reply_generated", user_id=user_id, chat_id=chat_id, citation_count=len(citations))
    assistant_message = _store_assistant_message(
        chat_id=chat_id,
        content=reply_text,
        citations=citations,
    )

    logger.info("chat_created_successfully", user_id=user_id, chat_id=chat_id)
    return {
        "chat_id": chat_id,
        "user_message": user_message,
        "assistant_message": assistant_message,
    }


def add_chat_message(user_id: str, chat_id: str, message: str) -> dict:
    logger.info("adding_chat_message", user_id=user_id, chat_id=chat_id, message_length=len(message))
    chat_result = (
        supabase.table("chats")
        .select("id")
        .eq("id", chat_id)
        .eq("user_id", user_id)
        .is_("deleted_at", "null")
        .execute()
    )
    if not chat_result.data:
        logger.warning("chat_not_found_for_message", user_id=user_id, chat_id=chat_id)
        raise HTTPException(status_code=404, detail="Chat not found")

    user_message = _store_user_message(user_id=user_id, chat_id=chat_id, message=message)

    # Sliding window of prior turns, excluding the message we just stored (it is passed
    # separately as `question`).
    prior_messages = _load_chat_history(chat_id, limit=CHAT_HISTORY_WINDOW + 1)[:-1]
    project_settings = _load_project_settings(user_id)
    reply_text, citations = generate_rag_reply(
        user_id=user_id,
        question=message,
        agent_type=project_settings.get("agent_type"),
        chat_history=prior_messages,
    )

    logger.info("rag_reply_generated", user_id=user_id, chat_id=chat_id, citation_count=len(citations))
    assistant_message = _store_assistant_message(
        chat_id=chat_id,
        content=reply_text,
        citations=citations,
    )

    logger.info("chat_message_added", user_id=user_id, chat_id=chat_id)
    return {
        "chat_id": chat_id,
        "user_message": user_message,
        "assistant_message": assistant_message,
    }
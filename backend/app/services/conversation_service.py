from datetime import datetime, timezone

from fastapi import HTTPException

from app.core.logging import get_logger
from app.core.supabase_client import supabase
from app.services.rag_service import generate_rag_reply


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


def _load_chat_history(chat_id: str) -> list[dict]:
    logger.info("loading_chat_history", chat_id=chat_id)
    history_result = (
        supabase.table("messages")
        .select("role, content")
        .eq("chat_id", chat_id)
        .order("created_at", desc=False)
        .execute()
    )

    logger.info("chat_history_loaded", chat_id=chat_id, message_count=len(history_result.data or []))
    return history_result.data or []


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

    reply_text, citations = generate_rag_reply(
        user_id=user_id,
        question=message,
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

    chat_history = _load_chat_history(chat_id)
    prior_messages = chat_history[:-1] if chat_history else []

    reply_text, citations = generate_rag_reply(
        user_id=user_id,
        question=message,
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
from datetime import datetime, timezone

from fastapi import HTTPException

from app.core.supabase_client import supabase
from app.services.rag_service import generate_rag_reply


def _store_user_message(user_id: str, chat_id: str, message: str) -> dict:
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
        raise HTTPException(status_code=500, detail="Failed to store user message")

    return user_message_result.data[0]


def _store_assistant_message(chat_id: str, content: str, citations: list[dict]) -> dict:
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
        raise HTTPException(status_code=500, detail="Failed to store assistant message")

    return assistant_message_result.data[0]


def _load_chat_history(chat_id: str) -> list[dict]:
    history_result = (
        supabase.table("messages")
        .select("role, content")
        .eq("chat_id", chat_id)
        .order("created_at", desc=False)
        .execute()
    )

    return history_result.data or []


def create_chat(user_id: str, message: str) -> dict:
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
        raise HTTPException(status_code=500, detail="Failed to create chat")

    chat_id = chat_result.data[0]["id"]
    user_message = _store_user_message(user_id=user_id, chat_id=chat_id, message=message)

    reply_text, citations = generate_rag_reply(
        user_id=user_id,
        question=message,
        chat_history=[],
    )
    assistant_message = _store_assistant_message(
        chat_id=chat_id,
        content=reply_text,
        citations=citations,
    )

    return {
        "chat_id": chat_id,
        "user_message": user_message,
        "assistant_message": assistant_message,
    }


def add_chat_message(user_id: str, chat_id: str, message: str) -> dict:
    chat_result = (
        supabase.table("chats")
        .select("id")
        .eq("id", chat_id)
        .eq("user_id", user_id)
        .is_("deleted_at", "null")
        .execute()
    )
    if not chat_result.data:
        raise HTTPException(status_code=404, detail="Chat not found")

    user_message = _store_user_message(user_id=user_id, chat_id=chat_id, message=message)

    chat_history = _load_chat_history(chat_id)
    prior_messages = chat_history[:-1] if chat_history else []

    reply_text, citations = generate_rag_reply(
        user_id=user_id,
        question=message,
        chat_history=prior_messages,
    )
    assistant_message = _store_assistant_message(
        chat_id=chat_id,
        content=reply_text,
        citations=citations,
    )

    return {
        "chat_id": chat_id,
        "user_message": user_message,
        "assistant_message": assistant_message,
    }
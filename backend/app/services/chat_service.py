from datetime import datetime, timezone

from fastapi import HTTPException

from app.core.constants import DUMMY_LLM_REPLY
from app.core.supabase_client import supabase


def create_chat_with_dummy_reply(user_id: str, message: str) -> dict:
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

    assistant_message_result = (
        supabase.table("messages")
        .insert({
            "chat_id": chat_id,
            "role": "assistant",
            "content": DUMMY_LLM_REPLY,
        })
        .execute()
    )
    if not assistant_message_result.data:
        raise HTTPException(status_code=500, detail="Failed to store assistant message")

    return {
        "chat_id": chat_id,
        "user_message": user_message_result.data[0],
        "assistant_message": assistant_message_result.data[0],
    }


def add_message_with_dummy_reply(user_id: str, chat_id: str, message: str) -> dict:
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

    assistant_message_result = (
        supabase.table("messages")
        .insert({
            "chat_id": chat_id,
            "role": "assistant",
            "content": DUMMY_LLM_REPLY,
        })
        .execute()
    )
    if not assistant_message_result.data:
        raise HTTPException(status_code=500, detail="Failed to store assistant message")

    return {
        "chat_id": chat_id,
        "user_message": user_message_result.data[0],
        "assistant_message": assistant_message_result.data[0],
    }

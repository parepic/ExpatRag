from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.core.logging import get_logger
from app.core.supabase_client import supabase
from app.dependencies.auth import get_current_user
from app.schemas.chat import AddMessageRequest, CreateChatRequest
from app.services.conversation_service import (
    add_chat_message,
    create_chat as create_chat_record,
)

router = APIRouter(prefix="/chats")
logger = get_logger(__name__)


@router.get("")
def fetch_all_chats(user: dict = Depends(get_current_user)):
    logger.info("fetching_chats", user_id=user["id"])
    result = (
        supabase.table("chats")
        .select("id, title, created_at")
        .eq("user_id", user["id"])
        .is_("deleted_at", "null")
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )
    logger.info("chats_retrieved", user_id=user["id"], chat_count=len(result.data or []))
    return result.data


@router.get("/{chat_id}")
def fetch_chat(chat_id: str, user: dict = Depends(get_current_user)):
    logger.info("fetching_chat", user_id=user["id"], chat_id=chat_id)
    chat_result = (
        supabase.table("chats")
        .select("id")
        .eq("id", chat_id)
        .eq("user_id", user["id"])
        .is_("deleted_at", "null")
        .execute()
    )
    if not chat_result.data:
        logger.warning("chat_not_found", user_id=user["id"], chat_id=chat_id)
        raise HTTPException(status_code=404, detail="Chat not found")

    messages_result = (
        supabase.table("messages")
        .select("id, role, content, citations, trace_id, created_at")
        .eq("chat_id", chat_id)
        .order("created_at", desc=False)
        .execute()
    )
    logger.info("chat_retrieved", user_id=user["id"], chat_id=chat_id, message_count=len(messages_result.data or []))
    return {"chat_id": chat_id, "messages": messages_result.data}


@router.delete("/{chat_id}", status_code=204)
def delete_chat(chat_id: str, user: dict = Depends(get_current_user)):
    logger.info("deleting_chat", user_id=user["id"], chat_id=chat_id)
    chat_result = (
        supabase.table("chats")
        .select("id")
        .eq("id", chat_id)
        .eq("user_id", user["id"])
        .is_("deleted_at", "null")
        .execute()
    )
    if not chat_result.data:
        logger.warning("chat_not_found_for_delete", user_id=user["id"], chat_id=chat_id)
        raise HTTPException(status_code=404, detail="Chat not found")

    supabase.table("chats").update(
        {"deleted_at": datetime.now(timezone.utc).isoformat()}
    ).eq("id", chat_id).execute()
    logger.info("chat_deleted", user_id=user["id"], chat_id=chat_id)


@router.post("", status_code=201)
def create_chat_endpoint(
    body: CreateChatRequest,
    user: dict = Depends(get_current_user),
):
    logger.info("creating_chat", user_id=user["id"], initial_message_length=len(body.message))
    return create_chat_record(user_id=user["id"], message=body.message)


@router.post("/{chat_id}/messages")
def add_message_to_chat_endpoint(
    chat_id: str,
    body: AddMessageRequest,
    user: dict = Depends(get_current_user),
):
    logger.info("adding_chat_message", user_id=user["id"], chat_id=chat_id, message_length=len(body.message))
    return add_chat_message(
        user_id=user["id"],
        chat_id=chat_id,
        message=body.message,
    )

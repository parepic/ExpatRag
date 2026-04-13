from datetime import datetime, timezone

from fastapi import Cookie, HTTPException

from app.core.logging import get_logger, set_user_id
from app.core.supabase_client import supabase


logger = get_logger(__name__)


def get_current_user(session_token: str | None = Cookie(default=None)) -> dict:
    """Resolve a session cookie to a user row, raising 401 on any failure."""
    if not session_token:
        logger.error("missing_session_token")
        raise HTTPException(status_code=401, detail="Not authenticated")

    now = datetime.now(timezone.utc).isoformat()

    session_result = (
        supabase.table("sessions")
        .select("user_id")
        .eq("session_token", session_token)
        .gt("expires_at", now)
        .execute()
    )
    if not session_result.data:
        logger.error("invalid_or_expired_session")
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    user_id = session_result.data[0]["user_id"]
    set_user_id(user_id)
    user_result = (
        supabase.table("users")
        .select("*")
        .eq("id", user_id)
        .execute()
    )
    if not user_result.data:
        logger.error("session_user_not_found", user_id=user_id)
        raise HTTPException(status_code=401, detail="User not found")

    logger.info("authenticated_user_resolved", user_id=user_id)
    return user_result.data[0]

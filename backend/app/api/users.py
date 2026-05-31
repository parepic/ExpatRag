from fastapi import APIRouter, Depends, HTTPException

from app.core.logging import get_logger
from app.core.supabase_client import supabase
from app.dependencies.auth import get_current_user
from app.schemas.user import UpdateUserRequest, ProjectSettings

router = APIRouter(prefix="/users")
logger = get_logger(__name__)


@router.patch("/me")
def update_user_info(
    body: UpdateUserRequest,
    user: dict = Depends(get_current_user),
):
    logger.info("updating_user_profile", user_id=user["id"])
    updates = body.model_dump(exclude_none=True)
    if not updates:
        logger.warning("empty_user_update_payload", user_id=user["id"])
        raise HTTPException(status_code=400, detail="No fields provided to update")

    result = (
        supabase.table("users")
        .update(updates)
        .eq("id", user["id"])
        .execute()
    )
    updated = result.data[0]
    for field in ("id", "password", "created_at"):
        updated.pop(field, None)
    logger.info("user_profile_updated", user_id=user["id"], updated_fields=sorted(updates.keys()))
    return updated


@router.patch("/retrieval")
def update_retrieval_settings(
    body: ProjectSettings,
    user: dict = Depends(get_current_user),
):
    logger.info("updating_retrieval_settings", user_id=user["id"])
    updates = body.model_dump(exclude_none=True)
    if not updates:
        logger.warning("empty_project_setting_update_payload", user_id=user["id"])
        raise HTTPException(status_code=400, detail="No fields provided to update")

    result = (
        supabase.table("project_settings")
        .update(updates)
        .eq("user_id", user["id"])
        .execute()
    )
    updated = result.data[0]
    logger.info("project_settings_updated", user_id=user["id"], updated_fields=sorted(updates.keys()))
    return updated


@router.get("/retrieval")
def get_retrieval_settings(
    user: dict = Depends(get_current_user),
):
    logger.info("fetching_retrieval_settings", user_id=user["id"])
    result = (
        supabase.table("project_settings")
        .select("*")
        .eq("user_id", user["id"])
        .limit(1)
        .execute()
    )
    data = result.data or []
    if not data:
        logger.info("no_project_settings_found", user_id=user["id"])
        return {}

    settings = data[0]
    logger.info("project_settings_fetched", user_id=user["id"])
    return settings



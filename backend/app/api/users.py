from fastapi import APIRouter, Depends, HTTPException

from app.core.supabase_client import supabase
from app.dependencies.auth import get_current_user
from app.schemas.user import UpdateUserRequest

router = APIRouter(prefix="/users")


@router.patch("/me")
def update_user_info(
    body: UpdateUserRequest,
    user: dict = Depends(get_current_user),
):
    updates = body.model_dump(exclude_none=True)
    if not updates:
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
    return updated

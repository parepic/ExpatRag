import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response

from app.core.constants import SESSION_COOKIE, SESSION_DURATION_DAYS
from app.core.supabase_client import supabase
from app.dependencies.auth import get_current_user
from app.schemas.auth import LoginRequest, RegisterRequest

router = APIRouter(prefix="/auth")


@router.post("/register", status_code=201)
def register(body: RegisterRequest):
    existing = (
        supabase.table("users")
        .select("id")
        .eq("username", body.username)
        .execute()
    )
    if existing.data:
        raise HTTPException(status_code=409, detail="Username already taken")

    password_hash = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()
    result = (
        supabase.table("users")
        .insert({"username": body.username, "password": password_hash})
        .execute()
    )
    user = result.data[0]
    return {"id": user["id"], "username": user["username"]}


@router.post("/login")
def login(body: LoginRequest, response: Response):
    result = (
        supabase.table("users")
        .select("id, password")
        .eq("username", body.username)
        .execute()
    )
    user = result.data[0] if result.data else None
    dummy_hash = "$2b$12$aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    stored_hash = user["password"] if user else dummy_hash
    password_ok = bcrypt.checkpw(body.password.encode(), stored_hash.encode())

    if not user or not password_ok:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    raw_token = secrets.token_urlsafe(32)
    expires_at = (
        datetime.now(timezone.utc) + timedelta(days=SESSION_DURATION_DAYS)
    ).isoformat()

    supabase.table("sessions").insert({
        "user_id": user["id"],
        "session_token": raw_token,
        "expires_at": expires_at,
    }).execute()

    response.set_cookie(
        key=SESSION_COOKIE,
        value=raw_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=SESSION_DURATION_DAYS * 24 * 3600,
    )
    return {"message": "Logged in"}


@router.post("/logout")
def logout(response: Response, session_token: str | None = Cookie(default=None)):
    if session_token:
        supabase.table("sessions").delete().eq("session_token", session_token).execute()
    response.delete_cookie(key=SESSION_COOKIE)
    return {"message": "Logged out"}


@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    safe_user = dict(user)
    safe_user.pop("password", None)
    return safe_user

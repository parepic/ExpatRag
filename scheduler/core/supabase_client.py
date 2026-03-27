"""Supabase client factory for scheduler-side database access."""

from functools import lru_cache
import os

from supabase import Client, create_client

from scheduler.core.env import load_scheduler_env


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """Return a cached Supabase client configured from environment variables."""
    load_scheduler_env()

    supabase_url = os.getenv("SUPABASE_API_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")

    if not supabase_url or not service_key:
        raise RuntimeError(
            "SUPABASE_API_URL and SUPABASE_SERVICE_KEY must be set before running scheduler tasks"
        )

    return create_client(supabase_url=supabase_url, supabase_key=service_key)
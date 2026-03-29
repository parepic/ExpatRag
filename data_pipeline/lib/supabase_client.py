"""Cached Supabase client for the data pipeline."""

from functools import lru_cache
import os

from supabase import Client, create_client

from lib.env import load_pipeline_env


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    load_pipeline_env()

    supabase_url = os.getenv("SUPABASE_API_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")

    if not supabase_url or not service_key:
        raise RuntimeError(
            "SUPABASE_API_URL and SUPABASE_SERVICE_KEY must be set before running the pipeline."
        )

    return create_client(supabase_url=supabase_url, supabase_key=service_key)

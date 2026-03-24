import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

if not os.getenv("SUPABASE_API_URL") or not os.getenv("SUPABASE_SERVICE_KEY"):
    raise ValueError("Need to set the supabase API keys")

supabase: Client = create_client(
    supabase_url=os.getenv("SUPABASE_API_URL"),
    supabase_key=os.getenv("SUPABASE_SERVICE_KEY"),
)

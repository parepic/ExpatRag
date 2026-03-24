from fastapi import FastAPI
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

if not os.getenv("SUPABASE_API_URL") or not os.getenv("SUPABASE_SERVICE_KEY"):
    raise ValueError("Need to set the supabase API keys")

supabase: Client = create_client(
        supabase_url=os.getenv("SUPABASE_API_URL"),
        supabase_key=os.getenv("SUPABASE_SERVICE_KEY")
    )

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/users")
def get_users():
    try:
        users = supabase.table("users").select("*").execute()
        return users.data
    except Exception as e:
        print(f"Cannot query table: {str(e)}")

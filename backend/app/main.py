from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.chats import router as chats_router
from app.api.users import router as users_router

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(chats_router)


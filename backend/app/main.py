import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.chats import router as chats_router
from app.api.users import router as users_router
from app.core.logging import configure_logging, get_logger
from app.middleware.logging_middleware import LoggingMiddleware

configure_logging()
logger = get_logger(__name__)

app = FastAPI()
app.add_middleware(LoggingMiddleware)

frontend_url = os.getenv("FRONTEND_URL", ".env is not read properly, make sure to run from monorepo root")
print("Adding CORS middleware with frontend URL:", frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    logger.debug("health_check_called")
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(chats_router)

logger.info("application_ready")


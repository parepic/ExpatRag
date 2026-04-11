from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.chats import router as chats_router
from app.api.users import router as users_router
from app.core.logging import configure_logging, get_logger
from app.middleware.logging_middleware import LoggingMiddleware

configure_logging()
logger = get_logger(__name__)

app = FastAPI()
app.add_middleware(LoggingMiddleware)


@app.get("/health")
def health():
    logger.debug("health_check_called")
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(chats_router)

logger.info("application_ready")


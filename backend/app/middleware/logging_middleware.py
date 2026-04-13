from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logging import clear_context, get_logger, set_request_id


logger = get_logger(__name__)

# this will intercept every HTTP request before it reaches the route handlers

# the request will flow something like this
# request -> uvicorn (asgi server) ->  FastAPI app -> middleware (before) -> route handler -> middleware (after) -> response -> uvicorn (asgi server) -> client

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # create a unique UUID for each request.
        request_id = str(uuid.uuid4())
        set_request_id(request_id)
        start_time = time.time()

        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            client_host=request.client.host if request.client else None,
        )

        try:
            response = await call_next(request)
            duration = time.time() - start_time
            logger.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_seconds=round(duration, 4),
            )
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "request_failed",
                method=request.method,
                path=request.url.path,
                duration_seconds=round(duration, 4),
                error=str(e),
                exc_info=True,
            )
            raise
        finally:
            clear_context()

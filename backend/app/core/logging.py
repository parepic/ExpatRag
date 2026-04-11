from __future__ import annotations

import logging
import os
import socket
from contextvars import ContextVar
from pathlib import Path
from typing import Optional

import structlog


request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)

# Overkill right now, but will be useful once we deploy.
POD_NAME = os.getenv("POD_NAME", "local")
HOST_NAME = socket.gethostname()


# Inject the context variables, pod name and host name in logs.
def add_context_info(_: logging.Logger, __: str, event_dict: dict) -> dict:
    request_id = request_id_var.get()
    if request_id:
        event_dict["request_id"] = request_id

    user_id = user_id_var.get()
    if user_id:
        event_dict["user_id"] = user_id

    event_dict["pod_name"] = POD_NAME
    event_dict["host_name"] = HOST_NAME
    return event_dict


def configure_logging(log_filename: str = "logs/application.log") -> None:
    # Set the level before which logs are ignored. 
    log_level = logging.INFO

    # Setup the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()

    # Terminal logging disabled for now.
    # formatter = logging.Formatter("%(message)s")
    # stream_handler = logging.StreamHandler(sys.stdout)
    # stream_handler.setFormatter(formatter)
    # root_logger.addHandler(stream_handler)

    # File logging 
    file_path = Path(log_filename)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(file_path, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger.addHandler(file_handler)


    # Optional: reduce noisy libs i.e dependent packages logs are not needed
    # Just set the level to something below INFO
    for noisy_logger in ("fastapi", "uvicorn.access", "uvicorn.error", "httpx"):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)

    # Force JSON output
    structlog.configure(
        # Each processor takes a dictionary and returns a modified dictionary
        processors=[
            structlog.stdlib.filter_by_level,  # skip below log level
            structlog.contextvars.merge_contextvars,  # pull in request_id, user_id 
            structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"), # add timestamp
            # something I feel is good for debugging, tells you the exact location in code
            structlog.processors.CallsiteParameterAdder(
                [
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                ]
            ),
            structlog.stdlib.add_log_level,  # adds level
            structlog.stdlib.add_logger_name,  # adds logger name
            add_context_info,  # request/user/pod/host
            structlog.processors.StackInfoRenderer(),  # render stack traces
            structlog.processors.format_exc_info,  # exception info if exc_info=True
            structlog.processors.JSONRenderer(),  # convert dictionary to a JSON
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,  # Use stdlib logger wrapper
        cache_logger_on_first_use=True,
    )


def get_logger(name: str):
    return structlog.get_logger(name)


def set_request_id(request_id: str) -> None:
    request_id_var.set(request_id)


def set_user_id(user_id: str) -> None:
    user_id_var.set(user_id)


def clear_context() -> None:
    request_id_var.set(None)
    user_id_var.set(None)

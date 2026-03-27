"""Environment-loading helpers for scheduler tasks."""

from dotenv import load_dotenv

from scheduler.core.config import ENV_FILE_CANDIDATES


def load_scheduler_env() -> None:
    """Load environment variables from the scheduler's supported .env locations."""
    for env_file in ENV_FILE_CANDIDATES:
        if env_file.exists():
            load_dotenv(env_file, override=False)
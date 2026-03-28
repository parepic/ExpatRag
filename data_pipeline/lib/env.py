"""Load .env from the repository root (and parent) for pipeline scripts."""

from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]

ENV_FILE_CANDIDATES = (
    REPO_ROOT / ".env",
    REPO_ROOT.parent / ".env",
)


def load_pipeline_env() -> None:
    for env_file in ENV_FILE_CANDIDATES:
        if env_file.exists():
            load_dotenv(env_file, override=False)

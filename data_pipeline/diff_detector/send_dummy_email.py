"""Send one dummy email through Resend using the repository's .env."""

from __future__ import annotations

import sys
from pathlib import Path

import resend

_pipeline_root = Path(__file__).resolve().parents[1]
if str(_pipeline_root) not in sys.path:
    sys.path.insert(0, str(_pipeline_root))

from lib.email_client import configure_email_client, get_email_sender_address


def main() -> None:
    configure_email_client()

    result = resend.Emails.send(
        {
            "from": get_email_sender_address(),
            "to": ["parvizahmedov2002@gmail.com"],
            "subject": "ExpatRag Resend test",
            "text": "This is a dummy email sent from the ExpatRag project.",
            "html": "<p>This is a dummy email sent from the ExpatRag project.</p>",
        }
    )

    print(f"Email sent successfully: {result.get('id')}")


if __name__ == "__main__":
    main()

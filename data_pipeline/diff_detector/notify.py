"""IND diff notification sender — loads users, renders emails, sends via Resend."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import resend

from diff_detector.classify import RelevanceMap
from diff_detector.email_renderer import render_ind_diff_email
from lib.email_client import configure_email_client, get_email_sender_address
from lib.models import User
from lib.supabase_client import get_supabase_client

_USER_COLUMNS = (
    "id, email, nationality, purpose_of_stay, employment_status, "
    "registration_status, has_fiscal_partner, salary_band, "
    "age_bracket_under_30, prior_nl_residency"
)


@dataclass(slots=True)
class NotifyStats:
    recipients: int = 0
    sent: int = 0
    failed: int = 0


def load_all_users(client: Any) -> list[User]:
    """Load all users who have an email address, paginated."""
    users: list[User] = []
    page_size = 200
    offset = 0

    while True:
        rows = (
            client.table("users")
            .select(_USER_COLUMNS)
            .order("created_at")
            .range(offset, offset + page_size - 1)
            .execute()
            .data
            or []
        )
        users.extend(User.model_validate(row) for row in rows if row.get("email"))
        if len(rows) < page_size:
            break
        offset += page_size

    return users


def _send_ind_diff_email(*, recipient: str, subject: str, plain_text: str, html: str) -> str | None:
    params: resend.Emails.SendParams = {
        "from": get_email_sender_address(),
        "to": [recipient],
        "subject": subject,
        "text": plain_text,
        "html": html,
    }
    result = resend.Emails.send(params)
    return result.get("id")


def notify_users(
    relevance_map: RelevanceMap,
    client: Any | None = None,
    *,
    dry_run: bool = False,
) -> NotifyStats:
    """Load all users, render a personalised email for each, and send via Resend.

    Users with no relevant changes are skipped automatically (render_ind_diff_email
    returns None for them). Passing dry_run=True renders emails but skips sending.
    """
    configure_email_client()
    client = client or get_supabase_client()

    users = load_all_users(client)
    stats = NotifyStats(recipients=len(users))

    for user in users:
        rendered = render_ind_diff_email(user.model_dump(), relevance_map)
        if rendered is None:
            continue

        subject, plain_text, html = rendered

        if dry_run:
            print(f"  [dry-run] would send to {user.email}")
            stats.sent += 1
            continue

        try:
            _send_ind_diff_email(
                recipient=user.email,
                subject=subject,
                plain_text=plain_text,
                html=html,
            )
            stats.sent += 1
        except Exception as exc:
            print(f"  Failed to send to {user.email}: {exc}")
            stats.failed += 1

    return stats

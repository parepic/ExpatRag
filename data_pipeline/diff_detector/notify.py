"""Stage 5 — notify: read <data_dir>/relevance.json, render a personalised email for
each opted-in user, send via Resend, and write <data_dir>/notify_report.json."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_pipeline_root = Path(__file__).resolve().parents[1]
if str(_pipeline_root) not in sys.path:
    sys.path.insert(0, str(_pipeline_root))

import resend

from diff_detector.classify import RelevanceMap, load_relevance
from diff_detector.email_renderer import render_ind_diff_email
from lib.config import NOTIFY_REPORT_FILENAME, RELEVANCE_FILENAME, ensure_run_dir
from lib.email_client import configure_email_client, get_email_sender_address
from lib.models import User
from lib.supabase_client import get_supabase_client

_USER_COLUMNS = (
    "id, email, nationality, purpose_of_stay, employment_status, "
    "registration_status, has_fiscal_partner, salary_band, "
    "age_bracket_under_30, prior_nl_residency, ind_diff_email_enabled"
)


@dataclass(slots=True)
class NotifyStats:
    recipients: int = 0
    sent: int = 0
    failed: int = 0
    # One entry per loaded user: {"email", "status", and optionally "id"/"error"}.
    # status is one of: sent, failed, skipped_no_changes, dry_run.
    results: list[dict] = field(default_factory=list)


def load_all_users(client: Any) -> list[User]:
    """Load users opted into IND diff emails, paginated."""
    users: list[User] = []
    page_size = 200
    offset = 0

    while True:
        rows = (
            client.table("users")
            .select(_USER_COLUMNS)
            .eq("ind_diff_email_enabled", True)
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
            stats.results.append({"email": user.email, "status": "skipped_no_changes"})
            continue

        subject, plain_text, html = rendered

        if dry_run:
            print(f"  [dry-run] would send to {user.email}")
            stats.sent += 1
            stats.results.append({"email": user.email, "status": "dry_run"})
            continue

        try:
            email_id = _send_ind_diff_email(
                recipient=user.email,
                subject=subject,
                plain_text=plain_text,
                html=html,
            )
            stats.sent += 1
            stats.results.append({"email": user.email, "status": "sent", "id": email_id})
        except Exception as exc:
            print(f"  Failed to send to {user.email}: {exc}")
            stats.failed += 1
            stats.results.append({"email": user.email, "status": "failed", "error": str(exc)})

    return stats


def write_notify_report(stats: NotifyStats, dry_run: bool, path: Path) -> Path:
    """Write the per-user notification outcome to a JSON audit file."""
    report = {
        "recipients": stats.recipients,
        "sent": stats.sent,
        "failed": stats.failed,
        "dry_run": dry_run,
        "results": stats.results,
    }
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"Notify report written to {path}")
    return path


def run_notify_stage(
    data_dir: Path | str | None = None,
    *,
    dry_run: bool = False,
    client: Any | None = None,
) -> NotifyStats:
    """Read <data_dir>/relevance.json, notify opted-in users, write notify_report.json."""
    run_dir = ensure_run_dir(data_dir)
    relevance_map = load_relevance(run_dir / RELEVANCE_FILENAME)
    stats = notify_users(relevance_map, client, dry_run=dry_run)
    print(f"  recipients={stats.recipients}, sent={stats.sent}, failed={stats.failed}")
    write_notify_report(stats, dry_run, run_dir / NOTIFY_REPORT_FILENAME)
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Stage 5 — render and send a personalised IND diff email to each opted-in "
            "user from <data_dir>/relevance.json, and write <data_dir>/notify_report.json."
        )
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Run directory holding relevance.json (default: data/latest/).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Render emails but do not send them.",
    )
    args = parser.parse_args()
    run_notify_stage(data_dir=args.data_dir, dry_run=args.dry_run)


if __name__ == "__main__":
    main()

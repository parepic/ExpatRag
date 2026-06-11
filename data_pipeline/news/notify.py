"""Email newly inserted alert-worthy news to subscribed users."""

from __future__ import annotations

import argparse
import html as html_lib
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import resend

_pipeline_root = Path(__file__).resolve().parents[1]
if str(_pipeline_root) not in sys.path:
    sys.path.insert(0, str(_pipeline_root))

from lib.config import NEW_ALERT_NEWS_ITEMS_JSONL_PATH
from lib.email_client import configure_email_client, get_email_sender_address
from lib.jsonl import load_documents_from_jsonl
from lib.supabase_client import get_supabase_client


@dataclass(slots=True)
class NotificationStats:
    items: int = 0
    recipients: int = 0
    sent: int = 0
    failed: int = 0


def validate_email_configuration() -> None:
    """Fail before recipient processing when required Resend settings are absent."""
    configure_email_client()
    get_email_sender_address()


def send_news_digest(
    *,
    recipient: str,
    subject: str,
    plain_text: str,
    html: str,
) -> str | None:
    """Send one digest without exposing any other subscriber addresses."""
    validate_email_configuration()
    params: resend.Emails.SendParams = {
        "from": get_email_sender_address(),
        "to": [recipient],
        "subject": subject,
        "text": plain_text,
        "html": html,
    }
    result = resend.Emails.send(params)
    return result.get("id")


def load_subscribed_users(client: Any) -> list[dict[str, Any]]:
    """Load opted-in recipients without assuming they fit in one response."""
    users: list[dict[str, Any]] = []
    page_size = 200
    offset = 0

    while True:
        rows = (
            client.table("users")
            .select("id, email")
            .eq("daily_news_email_enabled", True)
            .order("created_at")
            .range(offset, offset + page_size - 1)
            .execute()
            .data
            or []
        )
        users.extend(row for row in rows if row.get("email"))
        if len(rows) < page_size:
            break
        offset += page_size

    return users


def render_digest(
    items: list[dict[str, Any]],
    *,
    digest_date: datetime | None = None,
) -> tuple[str, str, str]:
    digest_date = (digest_date or datetime.now(UTC)).astimezone(UTC)
    date_label = digest_date.strftime("%d %B %Y")
    subject = f"Your ExpatRag daily news digest - {date_label}"
    plain_parts = [f"ExpatRag daily news digest - {date_label}", ""]
    html_parts = [
        "<html><body>",
        f"<h1>ExpatRag daily news digest - {html_lib.escape(date_label)}</h1>",
    ]

    for item in items:
        title = str(item.get("title") or "Untitled")
        summary = str(item.get("summary") or "")
        reason = str(item.get("alert_reason") or "")
        url = str(item.get("source_url") or "")
        published_at = str(item.get("published_at") or "")

        plain_parts.extend(
            [
                title,
                f"Published: {published_at}" if published_at else "",
                summary,
                f"Why this matters: {reason}" if reason else "",
                url,
                "",
            ]
        )
        html_parts.extend(
            [
                '<article style="margin: 0 0 24px">',
                f"<h2>{html_lib.escape(title)}</h2>",
                (
                    f"<p><strong>Published:</strong> "
                    f"{html_lib.escape(published_at)}</p>"
                    if published_at
                    else ""
                ),
                f"<p>{html_lib.escape(summary)}</p>" if summary else "",
                (
                    f"<p><strong>Why this matters:</strong> "
                    f"{html_lib.escape(reason)}</p>"
                    if reason
                    else ""
                ),
                (
                    f'<p><a href="{html_lib.escape(url, quote=True)}">'
                    "Read the source</a></p>"
                    if url
                    else ""
                ),
                "</article>",
            ]
        )

    html_parts.append("</body></html>")
    return subject, "\n".join(plain_parts), "".join(html_parts)


def send_news_digest_to_subscribers(
    items: list[dict[str, Any]],
    *,
    client: Any | None = None,
    digest_date: datetime | None = None,
) -> NotificationStats:
    """Send one digest per opted-in user, continuing after recipient failures."""
    stats = NotificationStats(items=len(items))
    if not items:
        print("No new alert-worthy news items. Skipping notifications.")
        return stats

    client = client or get_supabase_client()
    recipients = load_subscribed_users(client)
    stats.recipients = len(recipients)
    if not recipients:
        print("No users are subscribed to daily news email.")
        return stats

    validate_email_configuration()
    subject, plain_text, html = render_digest(items, digest_date=digest_date)
    for user in recipients:
        try:
            message_id = send_news_digest(
                recipient=user["email"],
                subject=subject,
                plain_text=plain_text,
                html=html,
            )
            stats.sent += 1
            print(
                "Sent daily digest "
                f"(user_id={user['id']}, message_id={message_id or 'unknown'})"
            )
        except Exception as exc:
            stats.failed += 1
            print(f"Failed to send daily digest (user_id={user['id']}): {exc}")

    return stats


def send_news_digest_from_jsonl(
    path: Path = NEW_ALERT_NEWS_ITEMS_JSONL_PATH,
    *,
    client: Any | None = None,
) -> NotificationStats:
    """Load the store-stage handoff artifact and notify subscribers."""
    return send_news_digest_to_subscribers(
        load_documents_from_jsonl(path),
        client=client,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Email freshly inserted alert-worthy news to subscribers."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=NEW_ALERT_NEWS_ITEMS_JSONL_PATH,
        help=f"Input JSONL path, default: {NEW_ALERT_NEWS_ITEMS_JSONL_PATH}",
    )
    args = parser.parse_args()

    stats = send_news_digest_from_jsonl(args.input)
    print(
        "News notification complete: "
        f"items={stats.items}, recipients={stats.recipients}, "
        f"sent={stats.sent}, failed={stats.failed}"
    )


if __name__ == "__main__":
    main()

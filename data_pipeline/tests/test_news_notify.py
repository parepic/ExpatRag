from datetime import UTC, datetime

import pytest
import resend

from lib.jsonl import write_documents_jsonl
from news.notify import (
    render_digest,
    send_news_digest,
    send_news_digest_from_jsonl,
    send_news_digest_to_subscribers,
)


def stored_news(url: str = "https://example.com/news") -> dict:
    return {
        "id": "news-1",
        "title": "<Important>",
        "summary": "Costs & benefits",
        "alert_reason": "Action <required>",
        "source_url": url,
        "published_at": "2026-06-07T06:00:00+00:00",
    }


def test_notify_skips_subscriber_query_for_empty_items(monkeypatch):
    monkeypatch.setattr(
        "news.notify.load_subscribed_users",
        lambda _client: (_ for _ in ()).throw(
            AssertionError("subscriber query should not run")
        ),
    )

    stats = send_news_digest_to_subscribers([], client=object())

    assert stats.items == 0
    assert stats.recipients == 0
    assert stats.sent == 0


def test_notify_sends_only_to_loaded_subscribers(monkeypatch):
    recipients: list[str] = []
    monkeypatch.setattr(
        "news.notify.validate_email_configuration",
        lambda: None,
    )
    monkeypatch.setattr(
        "news.notify.load_subscribed_users",
        lambda _client: [
            {"id": "1", "email": "one@example.com"},
            {"id": "2", "email": "two@example.com"},
        ],
    )
    monkeypatch.setattr(
        "news.notify.send_news_digest",
        lambda **kwargs: recipients.append(kwargs["recipient"]) or "message-id",
    )

    stats = send_news_digest_to_subscribers(
        [stored_news()],
        client=object(),
    )

    assert recipients == ["one@example.com", "two@example.com"]
    assert stats.recipients == 2
    assert stats.sent == 2


def test_notify_continues_after_one_recipient_failure(monkeypatch):
    attempted: list[str] = []
    monkeypatch.setattr(
        "news.notify.validate_email_configuration",
        lambda: None,
    )
    monkeypatch.setattr(
        "news.notify.load_subscribed_users",
        lambda _client: [
            {"id": "1", "email": "bad@example.com"},
            {"id": "2", "email": "good@example.com"},
        ],
    )

    def send(**kwargs):
        attempted.append(kwargs["recipient"])
        if kwargs["recipient"] == "bad@example.com":
            raise RuntimeError("provider failure")
        return "message-id"

    monkeypatch.setattr("news.notify.send_news_digest", send)

    stats = send_news_digest_to_subscribers(
        [stored_news()],
        client=object(),
    )

    assert attempted == ["bad@example.com", "good@example.com"]
    assert stats.sent == 1
    assert stats.failed == 1


def test_notify_fails_before_sending_when_configuration_is_missing(monkeypatch):
    monkeypatch.setattr(
        "news.notify.load_subscribed_users",
        lambda _client: [{"id": "1", "email": "reader@example.com"}],
    )
    monkeypatch.setattr(
        "news.notify.validate_email_configuration",
        lambda: (_ for _ in ()).throw(RuntimeError("missing config")),
    )
    monkeypatch.setattr(
        "news.notify.send_news_digest",
        lambda **_kwargs: (_ for _ in ()).throw(
            AssertionError("send should not run")
        ),
    )

    with pytest.raises(RuntimeError, match="missing config"):
        send_news_digest_to_subscribers([stored_news()], client=object())


def test_notify_from_jsonl_loads_store_handoff(monkeypatch, tmp_path):
    path = tmp_path / "new.jsonl"
    item = stored_news()
    write_documents_jsonl(path, [item])
    received: list[list[dict]] = []

    def notify(items, **_kwargs):
        received.append(items)
        from news.notify import NotificationStats

        return NotificationStats(items=len(items))

    monkeypatch.setattr("news.notify.send_news_digest_to_subscribers", notify)

    stats = send_news_digest_from_jsonl(path, client=object())

    assert received == [[item]]
    assert stats.items == 1


def test_digest_escapes_html():
    subject, plain_text, html = render_digest(
        [stored_news("https://example.com/?a=1&b=2")],
        digest_date=datetime(2026, 6, 7, tzinfo=UTC),
    )

    assert "07 June 2026" in subject
    assert "<Important>" in plain_text
    assert "&lt;Important&gt;" in html
    assert "a=1&amp;b=2" in html


def test_notify_sends_expected_resend_payload(monkeypatch):
    monkeypatch.setenv("RESEND_API_KEY", "re_test")
    monkeypatch.setenv("EMAIL_SENDER", "ExpatRag <news@example.com>")
    sent: list[dict] = []

    monkeypatch.setattr(
        resend.Emails,
        "send",
        lambda params: sent.append(params) or {"id": "email-123"},
    )

    message_id = send_news_digest(
        recipient="reader@example.com",
        subject="Daily digest",
        plain_text="Plain body",
        html="<p>HTML body</p>",
    )

    assert message_id == "email-123"
    assert resend.api_key == "re_test"
    assert sent == [
        {
            "from": "ExpatRag <news@example.com>",
            "to": ["reader@example.com"],
            "subject": "Daily digest",
            "text": "Plain body",
            "html": "<p>HTML body</p>",
        }
    ]


@pytest.mark.parametrize(
    ("missing_variable", "expected_message"),
    [
        ("RESEND_API_KEY", "RESEND_API_KEY must be set before sending email."),
        ("EMAIL_SENDER", "EMAIL_SENDER must be set before sending email."),
    ],
)
def test_notify_requires_email_configuration(
    monkeypatch,
    missing_variable,
    expected_message,
):
    monkeypatch.setenv("RESEND_API_KEY", "re_test")
    monkeypatch.setenv("EMAIL_SENDER", "news@example.com")
    monkeypatch.delenv(missing_variable)
    monkeypatch.setattr("lib.email_client.load_pipeline_env", lambda: None)

    with pytest.raises(RuntimeError, match=expected_message):
        send_news_digest(
            recipient="reader@example.com",
            subject="Daily digest",
            plain_text="Plain body",
            html="<p>HTML body</p>",
        )

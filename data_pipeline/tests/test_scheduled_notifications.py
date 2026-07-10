import pytest

from scheduled_notifications import run_scheduled_notifications


def test_scheduled_notifications_runs_all_pipelines():
    calls = []

    run_scheduled_notifications(
        (
            ("first", lambda: calls.append("first")),
            ("second", lambda: calls.append("second")),
        )
    )

    assert calls == ["first", "second"]


def test_scheduled_notifications_runs_remaining_pipeline_after_failure():
    calls = []

    def fail():
        calls.append("first")
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="first: boom"):
        run_scheduled_notifications(
            (
                ("first", fail),
                ("second", lambda: calls.append("second")),
            )
        )

    assert calls == ["first", "second"]


def test_scheduled_notifications_fails_when_email_send_failed():
    class Result:
        emails_failed = 1

    with pytest.raises(RuntimeError, match=r"1 email\(s\) failed"):
        run_scheduled_notifications((("IND", Result),))

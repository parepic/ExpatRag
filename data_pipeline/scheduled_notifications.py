"""Run all notification pipelines for the weekly Azure Container Apps Job."""

from __future__ import annotations

import traceback
from collections.abc import Callable

from diff_detector.pipeline import run_ind_diff_pipeline
from news.weekly import run_weekly_news


def run_scheduled_notifications(
    pipelines: tuple[tuple[str, Callable[[], object]], ...] | None = None,
) -> None:
    """Run every pipeline, then fail the job if any pipeline failed."""
    configured_pipelines = pipelines or (
        ("IND diff notifications", run_ind_diff_pipeline),
        ("weekly news digest", run_weekly_news),
    )
    failures: list[str] = []

    for name, pipeline in configured_pipelines:
        print(f"Starting {name}...")
        try:
            result = pipeline()
            failed_emails = getattr(result, "emails_failed", 0)
            notifications = getattr(result, "notifications", None)
            failed_emails += getattr(notifications, "failed", 0)
            if failed_emails:
                raise RuntimeError(f"{failed_emails} email(s) failed to send")
        except Exception as exc:
            failures.append(f"{name}: {exc}")
            traceback.print_exc()
        else:
            print(f"Completed {name}.")

    if failures:
        details = "; ".join(failures)
        raise RuntimeError(f"Scheduled notification job failed: {details}")

    print("All scheduled notification pipelines completed successfully.")


if __name__ == "__main__":
    run_scheduled_notifications()

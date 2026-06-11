"""Shared Resend configuration for data-pipeline email senders."""

import os

import resend

from lib.env import load_pipeline_env


def configure_email_client() -> None:
    load_pipeline_env()

    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        raise RuntimeError(
            "RESEND_API_KEY must be set before sending email."
        )

    resend.api_key = api_key


def get_email_sender_address() -> str:
    load_pipeline_env()

    sender_address = os.getenv("EMAIL_SENDER")
    if not sender_address:
        raise RuntimeError(
            "EMAIL_SENDER must be set before sending email."
        )

    return sender_address

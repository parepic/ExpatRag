"""Pydantic models mirroring the Supabase database schema.

Keep in sync with backend/app/schemas/user.py and supabase/migrations/.
Long-term, consider replacing with generated types via `supabase gen types --lang=python`.
"""

from __future__ import annotations

from pydantic import BaseModel


class User(BaseModel):
    id: str
    email: str
    nationality: str | None = None
    purpose_of_stay: str | None = None
    reason_for_visit: str | None = None
    employment_status: str | None = None
    registration_status: str | None = None
    has_fiscal_partner: bool | None = None
    salary_band: str | None = None
    age_bracket_under_30: bool | None = None
    prior_nl_residency: bool | None = None
    languages: str | None = None
    daily_news_email_enabled: bool = False
    ind_diff_email_enabled: bool = False

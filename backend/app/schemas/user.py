from pydantic import BaseModel


class UpdateUserRequest(BaseModel):
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

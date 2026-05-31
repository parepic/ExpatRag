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



class ProjectSettings(BaseModel):
    rag_strategy: str | None = None
    agent_type: str | None = None 
    chunks_per_search: int | None = None
    final_context_size: int | None = None
    similarity_threshold: float | None = None 
    number_of_queries: int | None = None
    vector_weight: float | None = None
    keyword_weight: float | None = None
"""Single source of truth for user profile attributes and their allowed values."""

USER_PROFILE_ATTRIBUTES: dict[str, list[str | bool]] = {
    "nationality": [
        "EU/EEA citizen",
        "Non-EU national",
        "British (post-Brexit)",
        "Dutch citizen",
    ],
    "purpose_of_stay": [
        "Employed by Dutch/EU company",
        "Highly Skilled Migrant",
        "Self-employed / ZZP",
        "Study",
        "Family reunification",
        "Starting a startup",
        "Other",
    ],
    "employment_status": [
        "Employed full-time",
        "Employed part-time",
        "Self-employed / ZZP",
        "DGA (director/shareholder of own BV)",
        "Not working / dependent on partner",
        "Student",
    ],
    "registration_status": [
        "Not yet arrived in the Netherlands",
        "Arrived, not yet registered",
        "BRP registered at a municipality",
        "Have a BSN number",
        "Have DigiD",
    ],
    "salary_band": [
        "Under €20,000",
        "€20,000 - €40,000",
        "€40,000 - €60,000",
        "€60,000 - €80,000",
        "€80,000 - €100,000",
        "Over €100,000",
    ],
    "has_fiscal_partner": [True, False],
    "age_bracket_under_30": [True, False],
    "prior_nl_residency": [True, False],
}

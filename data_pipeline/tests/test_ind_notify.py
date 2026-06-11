"""Unit tests for diff_detector/notify.py.

All tests use a hand-crafted relevance map — no LLM calls needed.

To visually inspect the rendered email output, run:
    uv run --package data-pipeline pytest data_pipeline/tests/test_ind_notify.py -v -s -k preview
"""

from diff_detector.notify import get_user_bullets, render_ind_diff_email

BULLET_A = "The RVO point threshold for sponsors increased from 50 to 65."
BULLET_B = "The penalty lookback window decreased from 4 to 3 years."
BULLET_C = "Short-term researcher mobility window changed from 180 to 120 days."

# A minimal relevance map with two populated slots
RELEVANCE_MAP = {
    "nationality": {
        "EU/EEA citizen": [],
        "Non-EU national": [],
        "British (post-Brexit)": [],
        "Dutch citizen": [],
    },
    "purpose_of_stay": {
        "Employed by Dutch/EU company": [],
        "Highly Skilled Migrant": [BULLET_A, BULLET_B],
        "Self-employed / ZZP": [],
        "Study": [],
        "Family reunification": [],
        "Starting a startup": [],
        "Other": [],
    },
    "employment_status": {
        "Employed full-time": [],
        "Employed part-time": [],
        "Self-employed / ZZP": [],
        "DGA (director/shareholder of own BV)": [],
        "Not working / dependent on partner": [],
        "Student": [],
    },
    "registration_status": {
        "Not yet arrived in the Netherlands": [],
        "Arrived, not yet registered": [],
        "BRP registered at a municipality": [],
        "Have a BSN number": [],
        "Have DigiD": [],
    },
    "salary_band": {
        "Under €20,000": [],
        "€20,000 - €40,000": [],
        "€40,000 - €60,000": [],
        "€60,000 - €80,000": [BULLET_C],
        "€80,000 - €100,000": [],
        "Over €100,000": [],
    },
    "has_fiscal_partner": {True: [], False: []},
    "age_bracket_under_30": {True: [], False: []},
    "prior_nl_residency": {True: [], False: []},
}

HSM_USER = {
    "purpose_of_stay": "Highly Skilled Migrant",
    "nationality": "Non-EU national",
    "employment_status": "Employed full-time",
    "salary_band": "€60,000 - €80,000",
    "has_fiscal_partner": False,
    "age_bracket_under_30": False,
    "prior_nl_residency": False,
}

STUDENT_USER = {
    "purpose_of_stay": "Study",
    "nationality": "EU/EEA citizen",
    "employment_status": "Student",
    "has_fiscal_partner": False,
    "age_bracket_under_30": True,
    "prior_nl_residency": False,
}


class TestGetUserBullets:
    def test_hsm_user_gets_sponsor_bullets(self):
        bullets = get_user_bullets(HSM_USER, RELEVANCE_MAP)
        assert "Highly Skilled Migrant" in bullets
        assert BULLET_A in bullets["Highly Skilled Migrant"]
        assert BULLET_B in bullets["Highly Skilled Migrant"]

    def test_student_user_gets_no_bullets(self):
        bullets = get_user_bullets(STUDENT_USER, RELEVANCE_MAP)
        assert bullets == {}

    def test_duplicate_bullets_not_repeated(self):
        map_with_overlap = {
            **RELEVANCE_MAP,
            "salary_band": {
                **RELEVANCE_MAP["salary_band"],
                "€60,000 - €80,000": [BULLET_A],  # same bullet as purpose_of_stay HSM slot
            },
        }
        bullets = get_user_bullets(HSM_USER, map_with_overlap)
        all_bullets = [b for section in bullets.values() for b in section]
        assert all_bullets.count(BULLET_A) == 1, "Duplicate bullet should appear only once"

    def test_missing_attribute_in_user_is_skipped(self):
        partial_user = {"purpose_of_stay": "Highly Skilled Migrant"}
        bullets = get_user_bullets(partial_user, RELEVANCE_MAP)
        assert "Highly Skilled Migrant" in bullets
        assert len(bullets) == 1


class TestRenderIndDiffEmail:
    def test_returns_none_for_irrelevant_user(self):
        assert render_ind_diff_email(STUDENT_USER, RELEVANCE_MAP) is None

    def test_returns_three_tuple_for_relevant_user(self):
        result = render_ind_diff_email(HSM_USER, RELEVANCE_MAP)
        assert result is not None
        subject, plain_text, html = result
        assert isinstance(subject, str) and subject
        assert isinstance(plain_text, str) and plain_text
        assert isinstance(html, str) and html

    def test_subject_mentions_ind(self):
        subject, _, _ = render_ind_diff_email(HSM_USER, RELEVANCE_MAP)
        assert "IND" in subject

    def test_plain_text_contains_bullets(self):
        _, plain_text, _ = render_ind_diff_email(HSM_USER, RELEVANCE_MAP)
        assert BULLET_A in plain_text
        assert BULLET_B in plain_text

    def test_html_contains_bullets(self):
        _, _, html = render_ind_diff_email(HSM_USER, RELEVANCE_MAP)
        assert BULLET_A in html
        assert BULLET_B in html

    def test_html_is_valid_document(self):
        _, _, html = render_ind_diff_email(HSM_USER, RELEVANCE_MAP)
        assert html.startswith("<!DOCTYPE html>")
        assert "</html>" in html

    def test_boolean_attribute_renders_human_label(self):
        user_with_partner = {**HSM_USER, "has_fiscal_partner": True}
        map_with_partner_bullet = {
            **RELEVANCE_MAP,
            "has_fiscal_partner": {True: ["New tax benefit for fiscal partners."], False: []},
        }
        _, plain_text, html = render_ind_diff_email(user_with_partner, map_with_partner_bullet)
        assert "True" not in plain_text
        assert "True" not in html
        assert "fiscal partner" in plain_text
        assert "fiscal partner" in html


class TestEmailPreview:
    """Not real assertions — just print the rendered output for visual inspection.

    Run with:
        uv run --package data-pipeline pytest data_pipeline/tests/test_ind_notify.py -v -s -k preview
    """

    def test_preview_hsm_user(self):
        subject, plain_text, _ = render_ind_diff_email(HSM_USER, RELEVANCE_MAP)
        print(f"\nSubject: {subject}\n")
        print(plain_text)

    def test_preview_hsm_user_html(self):
        _, _, html = render_ind_diff_email(HSM_USER, RELEVANCE_MAP)
        print(html)

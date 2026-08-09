"""Unit tests for diff_detector/notify.py.

All tests use a hand-crafted relevance map — no LLM calls needed.

To visually inspect the rendered email output, run:
    uv run --project data_pipeline pytest data_pipeline/tests/test_ind_notify.py -v -s -k preview
"""

from unittest.mock import MagicMock

from diff_detector.notify import load_all_users
from diff_detector.email_renderer import get_user_bullets, render_ind_diff_email

SPONSOR_URL = "https://ind.nl/en/residence-permits/work/apply-for-recognition-as-sponsor"
RESEARCHER_URL = "https://ind.nl/en/residence-permits/work/short-term-mobility-of-researchers"

BULLET_A = {
    "text": "The RVO point threshold for sponsors increased from 50 to 65.",
    "url": SPONSOR_URL,
}
BULLET_B = {
    "text": "The penalty lookback window decreased from 4 to 3 years.",
    "url": SPONSOR_URL,
}
BULLET_C = {
    "text": "Short-term researcher mobility window changed from 180 to 120 days.",
    "url": RESEARCHER_URL,
}

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


def test_load_all_users_only_queries_opted_in_recipients():
    query = MagicMock()
    query.select.return_value = query
    query.eq.return_value = query
    query.order.return_value = query
    query.range.return_value = query
    query.execute.return_value.data = [
        {
            "id": "user-1",
            "email": "reader@example.com",
            "ind_diff_email_enabled": True,
        }
    ]
    client = MagicMock()
    client.table.return_value = query

    users = load_all_users(client)

    client.table.assert_called_once_with("users")
    query.eq.assert_called_once_with("ind_diff_email_enabled", True)
    assert [user.email for user in users] == ["reader@example.com"]


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
        assert BULLET_A["text"] in plain_text
        assert BULLET_B["text"] in plain_text

    def test_html_contains_bullets(self):
        _, _, html = render_ind_diff_email(HSM_USER, RELEVANCE_MAP)
        assert BULLET_A["text"] in html
        assert BULLET_B["text"] in html

    def test_plain_text_includes_source_url(self):
        _, plain_text, _ = render_ind_diff_email(HSM_USER, RELEVANCE_MAP)
        assert SPONSOR_URL in plain_text

    def test_html_links_to_source_page(self):
        _, _, html = render_ind_diff_email(HSM_USER, RELEVANCE_MAP)
        assert f'href="{SPONSOR_URL}"' in html

    def test_bullet_without_url_renders_no_link(self):
        map_without_url = {
            **RELEVANCE_MAP,
            "purpose_of_stay": {
                **RELEVANCE_MAP["purpose_of_stay"],
                "Highly Skilled Migrant": [{"text": "A change with no source.", "url": ""}],
            },
        }
        # Only purpose_of_stay is set, so no other slot can contribute a linked bullet.
        user = {"purpose_of_stay": "Highly Skilled Migrant"}
        _, plain_text, html = render_ind_diff_email(user, map_without_url)
        assert "A change with no source." in plain_text
        assert "View the IND page" not in html

    def test_html_is_valid_document(self):
        _, _, html = render_ind_diff_email(HSM_USER, RELEVANCE_MAP)
        assert html.startswith("<!DOCTYPE html>")
        assert "</html>" in html

    def test_boolean_attribute_renders_human_label(self):
        user_with_partner = {**HSM_USER, "has_fiscal_partner": True}
        map_with_partner_bullet = {
            **RELEVANCE_MAP,
            "has_fiscal_partner": {
                True: [{"text": "New tax benefit for fiscal partners.", "url": SPONSOR_URL}],
                False: [],
            },
        }
        _, plain_text, html = render_ind_diff_email(user_with_partner, map_with_partner_bullet)
        assert "True" not in plain_text
        assert "True" not in html
        assert "fiscal partner" in plain_text
        assert "fiscal partner" in html


class TestEmailPreview:
    """Not real assertions — just print the rendered output for visual inspection.

    Run with:
        uv run --project data_pipeline pytest data_pipeline/tests/test_ind_notify.py -v -s -k preview
    """

    def test_preview_hsm_user(self):
        subject, plain_text, _ = render_ind_diff_email(HSM_USER, RELEVANCE_MAP)
        print(f"\nSubject: {subject}\n")
        print(plain_text)

    def test_preview_hsm_user_html(self):
        _, _, html = render_ind_diff_email(HSM_USER, RELEVANCE_MAP)
        print(html)

"""Live email test — sends a real IND diff notification to all users in the local DB.

Uses a hardcoded relevance map (same as test_ind_notify.py) so no scraping or LLM
calls are needed. Run this after setting your profile attributes in the app.

From repo root:
    uv run --package data-pipeline python3 data_pipeline/diff_detector/send_test_email.py
    uv run --package data-pipeline python3 data_pipeline/diff_detector/send_test_email.py --dry-run
"""

from __future__ import annotations

import sys
from pathlib import Path

_pipeline_root = Path(__file__).resolve().parents[1]
if str(_pipeline_root) not in sys.path:
    sys.path.insert(0, str(_pipeline_root))

import argparse

from diff_detector.notify import load_all_users, notify_users
from lib.supabase_client import get_supabase_client

# Same relevance map as test_ind_notify.py — HSM + salary band have live bullets.
# Adjust these bullets to whatever you want to see in the email.
TEST_RELEVANCE_MAP = {
    "nationality": {
        "EU/EEA citizen": [],
        "Non-EU national": [],
        "British (post-Brexit)": [],
        "Dutch citizen": [],
    },
    "purpose_of_stay": {
        "Employed by Dutch/EU company": [],
        "Highly Skilled Migrant": [
            "The RVO point threshold for sponsors increased from 50 to 65.",
            "The penalty lookback window decreased from 4 to 3 years.",
        ],
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
        "€60,000 - €80,000": [
            "Short-term researcher mobility window changed from 180 to 120 days.",
        ],
        "€80,000 - €100,000": [],
        "Over €100,000": [],
    },
    "has_fiscal_partner": {True: [], False: []},
    "age_bracket_under_30": {True: [], False: []},
    "prior_nl_residency": {True: [], False: []},
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a test IND diff email to all local DB users.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Render emails and print recipients but do not send.",
    )
    args = parser.parse_args()

    client = get_supabase_client()
    users = load_all_users(client)
    print(f"Found {len(users)} user(s) in DB")
    for u in users:
        print(f"  {u.email} — purpose_of_stay={u.purpose_of_stay}, salary_band={u.salary_band}")

    stats = notify_users(TEST_RELEVANCE_MAP, client, dry_run=args.dry_run)
    print(
        f"\nDone: recipients={stats.recipients}, sent={stats.sent}, failed={stats.failed}"
    )


if __name__ == "__main__":
    main()

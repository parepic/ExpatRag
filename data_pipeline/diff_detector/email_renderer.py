"""Personalised email construction for IND diff notifications."""

from __future__ import annotations

from html import escape

from diff_detector.classify import RelevanceMap, RelevantChange
from lib.user_attributes import USER_PROFILE_ATTRIBUTES

_BOOL_SECTION_HEADERS: dict[str, dict[bool, str]] = {
    "has_fiscal_partner": {True: "someone with a fiscal partner", False: "someone without a fiscal partner"},
    "age_bracket_under_30": {True: "someone under 30", False: "someone 30 or older"},
    "prior_nl_residency": {True: "someone who previously lived in the Netherlands", False: "someone without prior NL residency"},
}


def _resolve_value_label(attribute: str, value: str | bool) -> str:
    """Return a display label for a profile value (never prints True/False)."""
    if isinstance(value, bool):
        return _BOOL_SECTION_HEADERS.get(attribute, {}).get(value, str(value))
    return str(value)


def get_user_bullets(
    user: dict, relevance_map: RelevanceMap
) -> dict[str, list[RelevantChange]]:
    """Return {value_label: [{text, url}]} for every attribute where this user has changes.

    Keys are human-readable value labels (e.g. "Highly Skilled Migrant", "someone under 30").
    A change appearing in more than one slot is only kept in the first one to avoid
    repetition; the same sentence from two different pages counts as two changes.
    """
    result: dict[str, list[RelevantChange]] = {}
    seen: set[tuple[str, str]] = set()

    for attribute in USER_PROFILE_ATTRIBUTES:
        user_value = user.get(attribute)
        if user_value is None:
            continue
        slot = relevance_map.get(attribute, {}).get(user_value, [])
        fresh = [c for c in slot if (c["text"], c["url"]) not in seen]
        if fresh:
            result[_resolve_value_label(attribute, user_value)] = fresh
            seen.update((c["text"], c["url"]) for c in fresh)

    return result


def _source_link(url: str) -> str:
    """The 'View the IND page' link appended to a bullet, or nothing when no URL is known."""
    if not url:
        return ""
    return f'<br><a class="source" href="{escape(url, quote=True)}">View the IND page</a>'


def render_ind_diff_email(
    user: dict, relevance_map: RelevanceMap
) -> tuple[str, str, str] | None:
    """Render a personalised IND diff notification email for one user.

    Returns (subject, plain_text, html) or None if no changes are relevant to this user
    (so callers can skip sending entirely).
    """
    sections = get_user_bullets(user, relevance_map)
    if not sections:
        return None

    subject = "IND update: immigration policy changes relevant to you"

    # --- Plain text ---
    lines: list[str] = [
        "IND POLICY UPDATE",
        "",
        "We detected changes to the IND (Dutch Immigration and Naturalisation Service)",
        "website that may be relevant to your profile.",
        "",
    ]
    for value_label, changes in sections.items():
        lines.append(f"As {value_label}:")
        for change in changes:
            lines.append(f"  • {change['text']}")
            if change["url"]:
                lines.append(f"    {change['url']}")
        lines.append("")
    plain_text = "\n".join(lines)

    # --- HTML ---
    sections_html_parts: list[str] = []
    for value_label, changes in sections.items():
        # TODO: "As €60,000 - €80,000" reads awkwardly — consider per-attribute header templates
        header = f"As {value_label}"
        bullet_items = "\n".join(
            f"            <li>{change['text']}{_source_link(change['url'])}</li>"
            for change in changes
        )
        sections_html_parts.append(
            f'        <div class="section">\n'
            f"          <h3>{header}</h3>\n"
            f"          <ul>\n"
            f"{bullet_items}\n"
            f"          </ul>\n"
            f"        </div>"
        )
    sections_html = "\n".join(sections_html_parts)

    html = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>IND Policy Update</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #1a1a1a;
      max-width: 600px;
      margin: 0 auto;
      padding: 24px 16px;
      background: #f4f4f5;
    }}
    .card {{
      background: white;
      border-radius: 10px;
      overflow: hidden;
      box-shadow: 0 1px 4px rgba(0,0,0,.08);
    }}
    .header {{
      background: #003082;
      color: white;
      padding: 24px 28px;
    }}
    .header h1 {{ margin: 0; font-size: 20px; font-weight: 700; }}
    .header p {{ margin: 6px 0 0; font-size: 13px; opacity: .8; }}
    .body {{ padding: 24px 28px; }}
    .intro {{ margin: 0 0 20px; color: #444; line-height: 1.6; }}
    .section {{
      border: 1px solid #e8e8ea;
      border-radius: 7px;
      padding: 16px 18px;
      margin-bottom: 14px;
    }}
    .section h3 {{
      margin: 0 0 10px;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: .6px;
      color: #003082;
    }}
    .section ul {{ margin: 0; padding-left: 18px; }}
    .section li {{ margin-bottom: 10px; line-height: 1.55; color: #333; }}
    .section li a.source {{
      display: inline-block;
      margin-top: 3px;
      font-size: 12px;
      color: #003082;
      text-decoration: none;
    }}
    .footer {{
      font-size: 12px;
      color: #999;
      text-align: center;
      padding: 18px 28px;
      border-top: 1px solid #f0f0f0;
    }}
    .footer a {{ color: #003082; text-decoration: none; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <h1>IND Policy Update</h1>
      <p>Changes to Dutch immigration rules relevant to your profile</p>
    </div>
    <div class="body">
      <p class="intro">
        We detected changes to the IND website. Here&rsquo;s what may affect you:
      </p>
{sections_html}
    </div>
    <div class="footer">
      You&rsquo;re receiving this because you opted in to IND policy update notifications.<br>
      <a href="https://patty.nl">Visit Patty</a> to manage your preferences.
    </div>
  </div>
</body>
</html>"""

    return subject, plain_text, html

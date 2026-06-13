"""Read/query tools for the legal-intake server.

These functions query the seeded SQLite database and return structured,
JSON-serializable results. Logic lives here so it can be tested independently
of the MCP layer; server.py wraps each as a thin tool.
"""

from legal_intake import db
from legal_intake.classifier import classify


def _row_to_dict(row, json_fields=()):
    """Convert a sqlite3.Row to a dict, deserializing named JSON columns."""
    d = dict(row)
    for f in json_fields:
        if f in d:
            d[f] = db.loads(d[f])
    return d


def find_similar_matters(description: str, client_company: str = None, limit: int = 5):
    """Find past matters resembling a described new matter.

    Classifies the description to candidate matter types, then retrieves past
    matters of those types, ranked by type-match strength and (if given) a
    same-client boost.
    """
    result = classify(description)
    candidate_types = [c["matter_type"] for c in result["candidates"]]
    if not candidate_types:
        return {
            "similar_matters": [],
            "count": 0,
            "note": "No matter-type signals detected; cannot match similar matters. "
                    "Provide more detail, or use get_matter_history with a known matter ID.",
        }

    conn = db.get_connection()
    try:
        placeholders = ",".join("?" for _ in candidate_types)
        sql = f"SELECT * FROM matters WHERE matter_type IN ({placeholders})"
        params = list(candidate_types)
        if client_company:
            sql += " AND client_company = ?"
            params.append(client_company)
        rows = conn.execute(sql, params).fetchall()
        matters = [_row_to_dict(r, ("related_matter_ids", "tags")) for r in rows]
    finally:
        conn.close()

    type_rank = {mt: len(candidate_types) - i for i, mt in enumerate(candidate_types)}
    for m in matters:
        score = type_rank.get(m["matter_type"], 0)
        if client_company and m["client_company"] == client_company:
            score += 2
        m["_score"] = score
    matters.sort(key=lambda m: (-m["_score"], m["matter_id"]))

    out = []
    for m in matters[:limit]:
        out.append({
            "matter_id": m["matter_id"],
            "client_company": m["client_company"],
            "matter_type": m["matter_type"],
            "subject_matter": m["subject_matter"],
            "complexity": m["complexity"],
            "urgency": m["urgency"],
            "outcome": m["outcome"],
            "estimated_hours": m["estimated_hours"],
            "actual_hours": m["actual_hours"],
            "lead_lawyer_id": m["lead_lawyer_id"],
            "tags": m["tags"],
        })
    return {
        "matched_matter_types": candidate_types,
        "similar_matters": out,
        "count": len(out),
        "note": "Similarity is based on matter-type match"
                + (" with a same-client boost" if client_company else "")
                + ". Use get_matter_history for full detail on any matter_id.",
    }


def check_client_history(client_company: str, recent_limit: int = 5):
    """Summarize the firm's history and standing preferences for a client.

    Returns the client profile (including standing preferences), recent
    matters, a matter-type history, and the templates applicable to this
    client (client-specific templates first, then generic).
    """
    conn = db.get_connection()
    try:
        crow = conn.execute(
            "SELECT * FROM client_companies WHERE company_name = ?", (client_company,)
        ).fetchone()
        if not crow:
            names = [r["company_name"] for r in conn.execute(
                "SELECT company_name FROM client_companies").fetchall()]
            return {
                "found": False,
                "note": f"No client named '{client_company}'. Known clients: {names}.",
            }
        client = _row_to_dict(crow, ("engagement_types", "preferences"))

        mrows = conn.execute(
            """SELECT matter_id, matter_type, subject_matter, opened_date, closed_date, outcome
               FROM matters WHERE client_company = ?
               ORDER BY opened_date DESC LIMIT ?""",
            (client_company, recent_limit),
        ).fetchall()
        recent = [dict(r) for r in mrows]

        trows = conn.execute(
            """SELECT matter_type, COUNT(*) AS n FROM matters
               WHERE client_company = ? GROUP BY matter_type ORDER BY n DESC""",
            (client_company,),
        ).fetchall()
        type_counts = {r["matter_type"]: r["n"] for r in trows}

        tplrows = conn.execute(
            """SELECT template_id, matter_type, client_company, description
               FROM matter_templates
               WHERE client_company = ? OR client_company IS NULL""",
            (client_company,),
        ).fetchall()
        templates = []
        for r in tplrows:
            d = dict(r)
            d["is_client_specific"] = d["client_company"] == client_company
            templates.append(d)
        templates.sort(key=lambda t: (not t["is_client_specific"], t["template_id"]))
    finally:
        conn.close()

    return {
        "found": True,
        "client": client,
        "recent_matters": recent,
        "matter_type_history": type_counts,
        "applicable_templates": templates,
        "note": "Preferences reflect standing client instructions and should guide how "
                "the matter is handled. Client-specific templates take priority over generic ones.",
    }


def get_matter_history(matter_id: str):
    """Retrieve full detail on a specific past matter by its ID."""
    conn = db.get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM matters WHERE matter_id = ?", (matter_id,)
        ).fetchone()
        if not row:
            return {"found": False, "note": f"No matter with ID '{matter_id}'."}
        matter = _row_to_dict(row, ("related_matter_ids", "tags"))
        lawyer = conn.execute(
            "SELECT name, title FROM lawyers WHERE lawyer_id = ?",
            (matter["lead_lawyer_id"],),
        ).fetchone()
        team = conn.execute(
            "SELECT team_name FROM teams WHERE team_id = ?",
            (matter["assigned_team_id"],),
        ).fetchone()
    finally:
        conn.close()

    matter["lead_lawyer_name"] = lawyer["name"] if lawyer else None
    matter["lead_lawyer_title"] = lawyer["title"] if lawyer else None
    matter["assigned_team_name"] = team["team_name"] if team else None
    return {"found": True, "matter": matter}
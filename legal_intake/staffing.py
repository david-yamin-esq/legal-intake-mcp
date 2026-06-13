"""Judgment-support tools for the legal-intake server.

Two tools that produce recommendations rather than raw data:

  suggest_staffing  — recommends lead-lawyer candidates for a matter, with
                      capacity treated as advisory, not dispositive.
  flag_for_escalation — surfaces whether a matter should be escalated to the
                      client's in-house team, checked against the client's
                      own stated escalation threshold. This tool deliberately
                      does not decide; it flags for human judgment.

Logic lives here so it can be tested independently of the MCP layer.
"""

from legal_intake import db
from legal_intake.classifier import classify
from legal_intake.taxonomy import MATTER_TYPES
from legal_intake.matters_data import COMPLEXITY_SENIORITY


def _service_to_team(conn):
    mapping = {}
    for r in conn.execute("SELECT team_id, service_categories FROM teams").fetchall():
        for cat in db.loads(r["service_categories"]):
            mapping[cat] = r["team_id"]
    return mapping


def suggest_staffing(matter_type: str, complexity: str = "Standard",
                     client_company: str = None, limit: int = 3):
    """Recommend lead-lawyer candidates for a matter.

    Routes the matter type to its delivery team, then ranks team members by
    fit: seniority appropriate to the assessed complexity, then available
    capacity. Capacity is advisory — a strong expertise or seniority match may
    justify assigning someone with less headroom.
    """
    service_category = MATTER_TYPES.get(matter_type)
    if service_category is None:
        return {
            "recommended": [],
            "note": f"Unknown matter_type '{matter_type}'. Run classify_matter first "
                    "to get a valid matter type.",
        }

    band = COMPLEXITY_SENIORITY.get(complexity, [2, 3])

    conn = db.get_connection()
    try:
        svc_team = _service_to_team(conn)
        team_id = svc_team.get(service_category)
        if team_id is None:
            return {"recommended": [], "note": f"No team handles '{service_category}'."}

        team = conn.execute(
            "SELECT team_name, capacity_pct, typical_turnaround_hours FROM teams WHERE team_id = ?",
            (team_id,),
        ).fetchone()

        rows = conn.execute("SELECT * FROM lawyers").fetchall()
        roster = []
        for r in rows:
            lawyer = dict(r)
            lawyer["team_ids"] = db.loads(lawyer["team_ids"])
            lawyer["expertise_areas"] = db.loads(lawyer["expertise_areas"])
            lawyer["bar_admissions"] = db.loads(lawyer["bar_admissions"])
            if team_id in lawyer["team_ids"]:
                roster.append(lawyer)
    finally:
        conn.close()

    # Rank: in-band seniority first, then more available capacity
    # (lower current_capacity_pct = more headroom).
    def rank_key(lawyer):
        in_band = band[0] <= lawyer["seniority_level"] <= band[1]
        return (0 if in_band else 1, lawyer["current_capacity_pct"])

    roster.sort(key=rank_key)

    recommended = []
    for lawyer in roster[:limit]:
        in_band = band[0] <= lawyer["seniority_level"] <= band[1]
        headroom = 100 - lawyer["current_capacity_pct"]
        recommended.append({
            "lawyer_id": lawyer["lawyer_id"],
            "name": lawyer["name"],
            "title": lawyer["title"],
            "seniority_level": lawyer["seniority_level"],
            "seniority_fit": "in band for complexity" if in_band else "outside ideal band",
            "current_capacity_pct": lawyer["current_capacity_pct"],
            "approx_headroom_pct": headroom,
            "expertise_areas": lawyer["expertise_areas"],
        })

    return {
        "matter_type": matter_type,
        "service_category": service_category,
        "assigned_team": team["team_name"] if team else None,
        "team_capacity_pct": team["capacity_pct"] if team else None,
        "complexity": complexity,
        "target_seniority_band": band,
        "recommended": recommended,
        "note": "Recommendations rank seniority-fit first, then available capacity. "
                "Capacity is advisory: a strong expertise or seniority match can justify "
                "assigning someone with less headroom. Final staffing is a human decision.",
    }


# Signals that a matter may warrant escalation to the client's in-house team,
# independent of any client-specific threshold.
_ESCALATION_SIGNALS = {
    "novel or unprecedented issue": ["novel", "unprecedented", "first of its kind", "no precedent"],
    "potential liability above norm": ["unlimited liability", "below the client's floor", "liability cap of", "uncapped"],
    "IP exposure": ["assignment of", "background ip", "license grant", "ip ownership", "publication rights"],
    "regulatory exposure": ["regulator", "regulatory scrutiny", "sanctions", "enforcement"],
    "material commitment": ["exclusivity", "multi-year", "auto-renew", "automatic renewal"],
}


def flag_for_escalation(description: str, client_company: str = None):
    """Assess whether a matter should be escalated to the client's in-house team.

    Scans the description for general escalation signals and, when a client is
    given, reports that client's own stated escalation threshold so the two can
    be weighed together. This tool surfaces a recommendation and the reasons
    behind it; it does NOT decide. Escalation is always a human call.
    """
    text_lower = description.lower()

    triggered = {}
    for reason, phrases in _ESCALATION_SIGNALS.items():
        hits = [p for p in phrases if p in text_lower]
        if hits:
            triggered[reason] = hits

    complexity = classify(description)["assessed_complexity"]
    complexity_flag = complexity in ("Complex", "Novel")

    client_threshold = None
    client_contact = None
    if client_company:
        conn = db.get_connection()
        try:
            row = conn.execute(
                "SELECT preferences, primary_contact_name FROM client_companies WHERE company_name = ?",
                (client_company,),
            ).fetchone()
        finally:
            conn.close()
        if row:
            prefs = db.loads(row["preferences"]) or {}
            client_threshold = prefs.get("escalation_threshold")
            client_contact = row["primary_contact_name"]

    recommend = bool(triggered) or complexity_flag

    return {
        "escalation_recommended": recommend,
        "triggered_signals": triggered,
        "assessed_complexity": complexity,
        "client_escalation_threshold": client_threshold,
        "escalate_to": client_contact,
        "note": "This is a flag for human judgment, not a decision. Weigh the triggered "
                "signals against the client's stated threshold. When in doubt, escalate: "
                "an intake system should never silently absorb a decision that belongs to "
                "the client's in-house team.",
    }
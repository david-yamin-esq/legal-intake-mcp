"""Load all mock data into the intake database.

Run from the repository root as a module:
    python -m legal_intake.seed

Resets the database, loads reference data (clients, teams, lawyers,
templates), then generates matters from the scenario pool. Matter generation
is deterministic given the random seed, so re-running produces the same data.
"""

import random
from datetime import date, timedelta

from legal_intake import db
from legal_intake.taxonomy import MATTER_TYPES
from legal_intake.seed_data import CLIENTS, TEAMS, LAWYERS, TEMPLATES
from legal_intake.matters_data import (
    SCENARIOS, REQUESTERS, HIGH_VOLUME_TYPES,
    COMPLEXITY_SENIORITY, COMPLEXITY_HOURS,
)

REFERENCE_DATE = date(2026, 6, 13)
RANDOM_SEED = 42


def load_clients(conn):
    for c in CLIENTS:
        conn.execute(
            """INSERT OR REPLACE INTO client_companies
               (company_name, industry, size, relationship_start_date,
                primary_contact_name, engagement_types, preferences, open_matter_count)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (c["company_name"], c["industry"], c["size"], c["relationship_start_date"],
             c["primary_contact_name"], db.dumps(c["engagement_types"]),
             db.dumps(c["preferences"]), c["open_matter_count"]),
        )


def load_teams(conn):
    for t in TEAMS:
        conn.execute(
            """INSERT OR REPLACE INTO teams
               (team_id, team_name, service_categories, capacity_pct,
                typical_turnaround_hours, lead_partner_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (t["team_id"], t["team_name"], db.dumps(t["service_categories"]),
             t["capacity_pct"], t["typical_turnaround_hours"], t["lead_partner_id"]),
        )


def load_lawyers(conn):
    for lawyer in LAWYERS:
        conn.execute(
            """INSERT OR REPLACE INTO lawyers
               (lawyer_id, name, title, team_ids, expertise_areas,
                bar_admissions, current_capacity_pct, years_experience, seniority_level)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (lawyer["lawyer_id"], lawyer["name"], lawyer["title"], db.dumps(lawyer["team_ids"]),
             db.dumps(lawyer["expertise_areas"]), db.dumps(lawyer["bar_admissions"]),
             lawyer["current_capacity_pct"], lawyer["years_experience"], lawyer["seniority_level"]),
        )


def load_templates(conn):
    for tpl in TEMPLATES:
        conn.execute(
            """INSERT OR REPLACE INTO matter_templates
               (template_id, matter_type, client_company, description,
                typical_steps, typical_duration_hours, last_used_matter_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (tpl["template_id"], tpl["matter_type"], tpl["client_company"],
             tpl["description"], db.dumps(tpl["typical_steps"]),
             tpl["typical_duration_hours"], tpl["last_used_matter_id"]),
        )


def _service_to_team():
    m = {}
    for t in TEAMS:
        for cat in t["service_categories"]:
            m[cat] = t["team_id"]
    return m


def _lawyers_by_team():
    m = {}
    for lawyer in LAWYERS:
        for tid in lawyer["team_ids"]:
            m.setdefault(tid, []).append(lawyer)
    return m


def _template_hours(matter_type, client):
    client_match = None
    generic_match = None
    for tpl in TEMPLATES:
        if tpl["matter_type"] == matter_type:
            if tpl["client_company"] == client:
                client_match = tpl["typical_duration_hours"]
            elif tpl["client_company"] is None:
                generic_match = tpl["typical_duration_hours"]
    return client_match if client_match is not None else generic_match


def _pick_lawyer(rng, team_id, complexity, lawyers_by_team):
    roster = lawyers_by_team.get(team_id, [])
    if not roster:
        return None
    band = COMPLEXITY_SENIORITY.get(complexity, [2, 3])
    in_band = [l for l in roster if band[0] <= l["seniority_level"] <= band[1]]
    pool = in_band if in_band else roster
    return rng.choice(pool)["lawyer_id"]


def generate_matters(conn):
    rng = random.Random(RANDOM_SEED)
    svc_team = _service_to_team()
    lbt = _lawyers_by_team()

    matters = []
    counter = 1
    for sc in SCENARIOS:
        mt = sc["matter_type"]
        service_cat = MATTER_TYPES[mt]
        team_id = svc_team.get(service_cat)
        instances = 3 if mt in HIGH_VOLUME_TYPES else 1
        for client in sc["eligible_clients"]:
            for _ in range(instances):
                matter_id = f"GC-{counter:04d}"
                counter += 1
                complexity = sc["complexity"]
                urgency = sc["urgency"]
                lead = _pick_lawyer(rng, team_id, complexity, lbt)
                days_ago = rng.randint(15, 540)
                opened = REFERENCE_DATE - timedelta(days=days_ago)
                est = _template_hours(mt, client) or COMPLEXITY_HOURS[complexity]
                est = max(1, int(est * rng.uniform(0.85, 1.25)))
                if rng.random() < 0.55:
                    closed = opened + timedelta(days=rng.randint(2, 30))
                    if closed > REFERENCE_DATE:
                        closed = REFERENCE_DATE
                    actual = max(1, int(est * rng.uniform(0.7, 1.3)))
                    outcome = "Escalated to client" if rng.random() < 0.12 else "Completed"
                    closed_str = closed.isoformat()
                else:
                    actual = None
                    outcome = rng.choice(["Pending", "In progress"])
                    closed_str = None
                req_name, req_dept = rng.choice(REQUESTERS[client])
                matters.append({
                    "matter_id": matter_id, "client_company": client,
                    "requester_name": req_name, "requester_department": req_dept,
                    "matter_type": mt, "subject_matter": sc["subject_matter"],
                    "description": sc["description"], "counterparty": sc["counterparty"],
                    "urgency": urgency, "complexity": complexity,
                    "opened_date": opened.isoformat(), "closed_date": closed_str,
                    "assigned_team_id": team_id, "lead_lawyer_id": lead,
                    "estimated_hours": est, "actual_hours": actual, "outcome": outcome,
                    "related_matter_ids": [], "tags": sc["tags"],
                })

    by_key = {}
    for m in matters:
        by_key.setdefault((m["matter_type"], m["client_company"]), []).append(m["matter_id"])
    for m in matters:
        siblings = [mid for mid in by_key[(m["matter_type"], m["client_company"])] if mid != m["matter_id"]]
        rng.shuffle(siblings)
        m["related_matter_ids"] = siblings[:2]

    for m in matters:
        conn.execute(
            """INSERT OR REPLACE INTO matters
               (matter_id, client_company, requester_name, requester_department,
                matter_type, subject_matter, description, counterparty, urgency,
                complexity, opened_date, closed_date, assigned_team_id, lead_lawyer_id,
                estimated_hours, actual_hours, outcome, related_matter_ids, tags)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (m["matter_id"], m["client_company"], m["requester_name"], m["requester_department"],
             m["matter_type"], m["subject_matter"], m["description"], m["counterparty"], m["urgency"],
             m["complexity"], m["opened_date"], m["closed_date"], m["assigned_team_id"], m["lead_lawyer_id"],
             m["estimated_hours"], m["actual_hours"], m["outcome"],
             db.dumps(m["related_matter_ids"]), db.dumps(m["tags"])),
        )

    for c in CLIENTS:
        n_open = conn.execute(
            "SELECT COUNT(*) FROM matters WHERE client_company=? AND closed_date IS NULL",
            (c["company_name"],),
        ).fetchone()[0]
        conn.execute(
            "UPDATE client_companies SET open_matter_count=? WHERE company_name=?",
            (n_open, c["company_name"]),
        )

    return len(matters)


def main():
    db.reset_db()
    conn = db.get_connection()
    try:
        load_clients(conn)
        load_teams(conn)
        load_lawyers(conn)
        load_templates(conn)
        generate_matters(conn)
        conn.commit()
        counts = {
            "client_companies": conn.execute("SELECT COUNT(*) FROM client_companies").fetchone()[0],
            "teams": conn.execute("SELECT COUNT(*) FROM teams").fetchone()[0],
            "lawyers": conn.execute("SELECT COUNT(*) FROM lawyers").fetchone()[0],
            "matter_templates": conn.execute("SELECT COUNT(*) FROM matter_templates").fetchone()[0],
            "matters": conn.execute("SELECT COUNT(*) FROM matters").fetchone()[0],
        }
        dist = conn.execute(
            "SELECT client_company, COUNT(*) FROM matters GROUP BY client_company ORDER BY client_company"
        ).fetchall()
        open_counts = conn.execute(
            "SELECT company_name, open_matter_count FROM client_companies ORDER BY company_name"
        ).fetchall()
    finally:
        conn.close()

    print("Data loaded:")
    for table, n in counts.items():
        print(f"  {table}: {n}")
    print("Matters per client:")
    for row in dist:
        print(f"  {row[0]}: {row[1]}")
    print("Open matters per client:")
    for row in open_counts:
        print(f"  {row['company_name']}: {row['open_matter_count']}")


if __name__ == "__main__":
    main()
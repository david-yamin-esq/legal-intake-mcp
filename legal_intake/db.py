"""SQLite storage layer for the legal-intake MCP server.

Uses the standard-library sqlite3 module — no external database dependency.
List- and dict-valued fields are stored as JSON-encoded TEXT columns, which
keeps the schema flat and is pragmatic for a single-file demo database.
"""

import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "intake.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS client_companies (
    company_name            TEXT PRIMARY KEY,
    industry                TEXT,
    size                    TEXT,
    relationship_start_date TEXT,
    primary_contact_name    TEXT,
    engagement_types        TEXT,   -- JSON array
    preferences             TEXT,   -- JSON object
    open_matter_count       INTEGER
);

CREATE TABLE IF NOT EXISTS teams (
    team_id                  TEXT PRIMARY KEY,
    team_name                TEXT,
    service_categories       TEXT,  -- JSON array
    capacity_pct             INTEGER,
    typical_turnaround_hours INTEGER,
    lead_partner_id          TEXT
);

CREATE TABLE IF NOT EXISTS lawyers (
    lawyer_id            TEXT PRIMARY KEY,
    name                 TEXT,
    title                TEXT,
    team_ids             TEXT,   -- JSON array
    expertise_areas      TEXT,   -- JSON array
    bar_admissions       TEXT,   -- JSON array
    current_capacity_pct INTEGER,
    years_experience     INTEGER,
    seniority_level      INTEGER
);

CREATE TABLE IF NOT EXISTS matters (
    matter_id            TEXT PRIMARY KEY,
    client_company       TEXT,
    requester_name       TEXT,
    requester_department TEXT,
    matter_type          TEXT,
    subject_matter       TEXT,
    description          TEXT,
    counterparty         TEXT,
    urgency              TEXT,
    complexity           TEXT,
    opened_date          TEXT,
    closed_date          TEXT,
    assigned_team_id     TEXT,
    lead_lawyer_id       TEXT,
    estimated_hours      INTEGER,
    actual_hours         INTEGER,
    outcome              TEXT,
    related_matter_ids   TEXT,   -- JSON array
    tags                 TEXT    -- JSON array
);

CREATE TABLE IF NOT EXISTS matter_templates (
    template_id            TEXT PRIMARY KEY,
    matter_type            TEXT,
    client_company         TEXT,
    description            TEXT,
    typical_steps          TEXT,  -- JSON array
    typical_duration_hours INTEGER,
    last_used_matter_id    TEXT
);
"""


def get_connection() -> sqlite3.Connection:
    """Open a connection to the intake database with row access by name."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create all tables if they don't already exist."""
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def reset_db() -> None:
    """Delete the database file entirely and recreate the empty schema."""
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()


def dumps(value) -> str:
    """Serialize a Python list/dict to a JSON string for storage."""
    return json.dumps(value)


def loads(value):
    """Deserialize a JSON string column back to Python (None-safe)."""
    return json.loads(value) if value else None


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
    conn = get_connection()
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    conn.close()
    print("Tables created:")
    for t in tables:
        print(f"  - {t['name']}")
"""Mock reference data for the legal-intake demo.

Three client companies with deliberately distinct preference profiles, six
delivery teams, a roster of lawyers, and reusable matter templates. The data
is fictional but modeled to resemble the engagements a legal managed-services
provider handles for corporate in-house departments.

The three clients are designed to exercise different routing behavior:
  - Meridian Financial Group: high-governance, conservative, escalates readily
  - Northwind Logistics: high-throughput, speed-oriented, runs on templates
  - Vertex Biosciences: IP-sensitive, complex matters, needs senior staffing
"""

CLIENTS = [
    {
        "company_name": "Meridian Financial Group",
        "industry": "Financial Services",
        "size": "Enterprise",
        "relationship_start_date": "2021-03-15",
        "primary_contact_name": "Katherine Wu, Deputy General Counsel",
        "engagement_types": ["Contract Review", "Financial Services Compliance", "Compliance & Regulatory"],
        "preferences": {
            "preferred_paper": "Meridian templates only",
            "playbook_variant": "high-governance",
            "redlining_style": "conservative; flag all deviations from playbook",
            "approval_threshold_usd": 250000,
            "sla_tier": "standard (5 business days)",
            "delivery_channel": "CLM platform (Ironclad)",
            "liability_cap_norm": "12 months fees; never accept below 6 months",
            "required_clauses": ["audit rights", "data processing addendum", "regulatory cooperation"],
            "forbidden_terms": ["unlimited liability", "automatic renewal beyond 1 year"],
            "governing_law": "New York",
            "escalation_threshold": "any novel regulatory exposure or liability above cap norm",
            "communication_style": "formal; written summaries with each delivery",
        },
        "open_matter_count": 0,
    },
    {
        "company_name": "Northwind Logistics",
        "industry": "Logistics & Supply Chain",
        "size": "Mid-market",
        "relationship_start_date": "2023-09-01",
        "primary_contact_name": "Tom Bradley, Senior Counsel",
        "engagement_types": ["Contract Review", "Real Estate", "Legal Operations"],
        "preferences": {
            "preferred_paper": "either party; accept counterparty paper to save time",
            "playbook_variant": "standard",
            "redlining_style": "light; accept market-standard terms without escalation",
            "approval_threshold_usd": 100000,
            "sla_tier": "expedited (48 hours)",
            "delivery_channel": "email",
            "liability_cap_norm": "12 months fees standard; flexible on routine deals",
            "required_clauses": ["termination for convenience", "limitation of liability"],
            "forbidden_terms": ["exclusivity beyond 2 years"],
            "governing_law": "Illinois",
            "escalation_threshold": "deal value above $100k or non-standard indemnity",
            "communication_style": "brief; inline CLM comments",
        },
        "open_matter_count": 0,
    },
    {
        "company_name": "Vertex Biosciences",
        "industry": "Biotechnology",
        "size": "Enterprise",
        "relationship_start_date": "2022-06-20",
        "primary_contact_name": "Dr. Helena Voss, General Counsel",
        "engagement_types": ["Contract Review", "Compliance & Regulatory", "Litigation Support"],
        "preferences": {
            "preferred_paper": "Vertex templates for IP-bearing deals; counterparty paper for routine",
            "playbook_variant": "IP-protective",
            "redlining_style": "thorough; protect IP and data rights without compromise",
            "approval_threshold_usd": 150000,
            "sla_tier": "standard (5 business days)",
            "delivery_channel": "CLM platform (Agiloft)",
            "liability_cap_norm": "negotiable, but IP indemnity carved out of all caps",
            "required_clauses": ["IP ownership", "confidentiality survival", "publication rights"],
            "forbidden_terms": ["assignment of background IP", "broad license grants"],
            "governing_law": "Delaware",
            "escalation_threshold": "any IP assignment, licensing term, or publication restriction",
            "communication_style": "detailed; scientific precision expected in summaries",
        },
        "open_matter_count": 0,
    },
]

TEAMS = [
    {"team_id": "T-CONTRACTS", "team_name": "Contract Review Team", "service_categories": ["Contract Review"], "capacity_pct": 72, "typical_turnaround_hours": 120, "lead_partner_id": "L-001"},
    {"team_id": "T-COMPLIANCE", "team_name": "Compliance & Regulatory Team", "service_categories": ["Compliance & Regulatory"], "capacity_pct": 60, "typical_turnaround_hours": 80, "lead_partner_id": "L-008"},
    {"team_id": "T-LITSUPPORT", "team_name": "Litigation Support Team", "service_categories": ["Litigation Support"], "capacity_pct": 85, "typical_turnaround_hours": 160, "lead_partner_id": "L-012"},
    {"team_id": "T-LEGALOPS", "team_name": "Legal Operations Team", "service_categories": ["Legal Operations"], "capacity_pct": 55, "typical_turnaround_hours": 200, "lead_partner_id": "L-015"},
    {"team_id": "T-REALESTATE", "team_name": "Real Estate Team", "service_categories": ["Real Estate"], "capacity_pct": 68, "typical_turnaround_hours": 96, "lead_partner_id": "L-018"},
    {"team_id": "T-FSCOMPLIANCE", "team_name": "Financial Services Compliance Team", "service_categories": ["Financial Services Compliance"], "capacity_pct": 78, "typical_turnaround_hours": 100, "lead_partner_id": "L-021"},
]

LAWYERS = [
    {"lawyer_id": "L-001", "name": "Sarah Chen", "title": "Director", "team_ids": ["T-CONTRACTS"], "expertise_areas": ["SaaS contracts", "complex commercial", "vendor negotiation"], "bar_admissions": ["NY", "CA"], "current_capacity_pct": 70, "years_experience": 18, "seniority_level": 5},
    {"lawyer_id": "L-002", "name": "Marcus Webb", "title": "Senior Counsel", "team_ids": ["T-CONTRACTS"], "expertise_areas": ["MSA", "licensing", "indemnification"], "bar_admissions": ["NY"], "current_capacity_pct": 65, "years_experience": 12, "seniority_level": 4},
    {"lawyer_id": "L-003", "name": "Priya Nair", "title": "Counsel", "team_ids": ["T-CONTRACTS"], "expertise_areas": ["data processing", "DPA", "privacy terms"], "bar_admissions": ["NY", "NJ"], "current_capacity_pct": 80, "years_experience": 8, "seniority_level": 3},
    {"lawyer_id": "L-004", "name": "James O'Brien", "title": "Senior Associate", "team_ids": ["T-CONTRACTS"], "expertise_areas": ["vendor contracts", "procurement"], "bar_admissions": ["IL"], "current_capacity_pct": 55, "years_experience": 6, "seniority_level": 3},
    {"lawyer_id": "L-005", "name": "Elena Volkov", "title": "Associate", "team_ids": ["T-CONTRACTS"], "expertise_areas": ["NDA", "routine commercial"], "bar_admissions": ["NY"], "current_capacity_pct": 40, "years_experience": 4, "seniority_level": 2},
    {"lawyer_id": "L-006", "name": "David Park", "title": "Associate", "team_ids": ["T-CONTRACTS"], "expertise_areas": ["customer contracts", "order forms"], "bar_admissions": ["CA"], "current_capacity_pct": 45, "years_experience": 3, "seniority_level": 2},
    {"lawyer_id": "L-007", "name": "Aisha Rahman", "title": "Associate", "team_ids": ["T-CONTRACTS"], "expertise_areas": ["NDA", "intake triage"], "bar_admissions": ["NY"], "current_capacity_pct": 30, "years_experience": 2, "seniority_level": 1},
    {"lawyer_id": "L-008", "name": "Robert Sterling", "title": "Director", "team_ids": ["T-COMPLIANCE"], "expertise_areas": ["GDPR", "CCPA", "regulatory strategy"], "bar_admissions": ["NY", "DC"], "current_capacity_pct": 60, "years_experience": 20, "seniority_level": 5},
    {"lawyer_id": "L-009", "name": "Fatima Al-Rashid", "title": "Senior Counsel", "team_ids": ["T-COMPLIANCE"], "expertise_areas": ["privacy assessments", "policy drafting"], "bar_admissions": ["DC"], "current_capacity_pct": 50, "years_experience": 11, "seniority_level": 4},
    {"lawyer_id": "L-010", "name": "Thomas Greene", "title": "Counsel", "team_ids": ["T-COMPLIANCE"], "expertise_areas": ["regulatory filings", "compliance audits"], "bar_admissions": ["NY"], "current_capacity_pct": 70, "years_experience": 9, "seniority_level": 3},
    {"lawyer_id": "L-011", "name": "Mei Lin", "title": "Associate", "team_ids": ["T-COMPLIANCE"], "expertise_areas": ["privacy", "policy research"], "bar_admissions": ["CA"], "current_capacity_pct": 35, "years_experience": 3, "seniority_level": 2},
    {"lawyer_id": "L-012", "name": "Jonathan Pierce", "title": "Senior Counsel", "team_ids": ["T-LITSUPPORT"], "expertise_areas": ["e-discovery", "document review management"], "bar_admissions": ["NY", "NJ"], "current_capacity_pct": 75, "years_experience": 14, "seniority_level": 4},
    {"lawyer_id": "L-013", "name": "Rachel Adeyemi", "title": "Counsel", "team_ids": ["T-LITSUPPORT"], "expertise_areas": ["document review", "privilege review"], "bar_admissions": ["NY"], "current_capacity_pct": 85, "years_experience": 7, "seniority_level": 3},
    {"lawyer_id": "L-014", "name": "Kevin Walsh", "title": "Associate", "team_ids": ["T-LITSUPPORT"], "expertise_areas": ["ESI processing", "review support"], "bar_admissions": ["IL"], "current_capacity_pct": 50, "years_experience": 2, "seniority_level": 1},
    {"lawyer_id": "L-015", "name": "Sandra Mitchell", "title": "Director", "team_ids": ["T-LEGALOPS"], "expertise_areas": ["CLM implementation", "playbook design", "process design"], "bar_admissions": ["NY"], "current_capacity_pct": 55, "years_experience": 16, "seniority_level": 5},
    {"lawyer_id": "L-016", "name": "Carlos Mendez", "title": "Counsel", "team_ids": ["T-LEGALOPS"], "expertise_areas": ["contract migration", "data extraction"], "bar_admissions": ["TX"], "current_capacity_pct": 60, "years_experience": 8, "seniority_level": 3},
    {"lawyer_id": "L-017", "name": "Nina Petrov", "title": "Associate", "team_ids": ["T-LEGALOPS"], "expertise_areas": ["CLM administration", "metadata"], "bar_admissions": ["NY"], "current_capacity_pct": 40, "years_experience": 3, "seniority_level": 2},
    {"lawyer_id": "L-018", "name": "William Hartford", "title": "Senior Counsel", "team_ids": ["T-REALESTATE"], "expertise_areas": ["commercial leases", "sublease management"], "bar_admissions": ["NY", "CT"], "current_capacity_pct": 65, "years_experience": 15, "seniority_level": 4},
    {"lawyer_id": "L-019", "name": "Grace Kim", "title": "Counsel", "team_ids": ["T-REALESTATE"], "expertise_areas": ["lease review", "premises agreements"], "bar_admissions": ["NY"], "current_capacity_pct": 70, "years_experience": 9, "seniority_level": 3},
    {"lawyer_id": "L-020", "name": "Daniel Foster", "title": "Associate", "team_ids": ["T-REALESTATE"], "expertise_areas": ["lease abstraction", "routine real estate"], "bar_admissions": ["IL"], "current_capacity_pct": 45, "years_experience": 4, "seniority_level": 2},
    {"lawyer_id": "L-021", "name": "Yusuf Demir", "title": "Director", "team_ids": ["T-FSCOMPLIANCE"], "expertise_areas": ["AML", "KYC", "financial crime", "sanctions"], "bar_admissions": ["NY", "DC"], "current_capacity_pct": 70, "years_experience": 19, "seniority_level": 5},
    {"lawyer_id": "L-022", "name": "Laura Bennett", "title": "Senior Counsel", "team_ids": ["T-FSCOMPLIANCE"], "expertise_areas": ["regulatory research", "FS compliance"], "bar_admissions": ["NY"], "current_capacity_pct": 60, "years_experience": 12, "seniority_level": 4},
]

TEMPLATES = [
    {"template_id": "TPL-001", "matter_type": "NDA Review", "client_company": None, "description": "Standard mutual NDA review against market norms.", "typical_steps": ["Confirm mutual vs one-way", "Check term and survival", "Verify carve-outs", "Confirm governing law"], "typical_duration_hours": 2, "last_used_matter_id": None},
    {"template_id": "TPL-002", "matter_type": "MSA Review", "client_company": None, "description": "Generic master services agreement review.", "typical_steps": ["Review liability and indemnity", "Check IP ownership", "Confirm termination rights", "Review payment terms"], "typical_duration_hours": 6, "last_used_matter_id": None},
    {"template_id": "TPL-003", "matter_type": "DPA Review", "client_company": None, "description": "Data processing agreement review for GDPR/CCPA alignment.", "typical_steps": ["Confirm processor obligations", "Check sub-processor terms", "Verify SCCs if cross-border", "Review breach notification"], "typical_duration_hours": 3, "last_used_matter_id": None},
    {"template_id": "TPL-004", "matter_type": "SaaS Agreement Review", "client_company": None, "description": "Generic SaaS subscription agreement review.", "typical_steps": ["Review SLA terms", "Check data and security terms", "Confirm liability cap", "Review renewal and termination"], "typical_duration_hours": 5, "last_used_matter_id": None},
    {"template_id": "TPL-005", "matter_type": "Vendor Contract Review", "client_company": None, "description": "Generic vendor/procurement contract review.", "typical_steps": ["Confirm scope and deliverables", "Review pricing and payment", "Check liability and insurance", "Confirm termination"], "typical_duration_hours": 4, "last_used_matter_id": None},
    {"template_id": "TPL-006", "matter_type": "Lease Review", "client_company": None, "description": "Generic commercial lease review.", "typical_steps": ["Review rent and escalation", "Check term and renewal options", "Confirm maintenance obligations", "Review assignment/sublet rights"], "typical_duration_hours": 5, "last_used_matter_id": None},
    {"template_id": "TPL-007", "matter_type": "MSA Review", "client_company": "Meridian Financial Group", "description": "Meridian high-governance MSA review on Meridian paper.", "typical_steps": ["Apply Meridian playbook", "Enforce 12-month liability cap floor", "Confirm audit rights and regulatory cooperation", "Flag any deviation for DGC review"], "typical_duration_hours": 8, "last_used_matter_id": None},
    {"template_id": "TPL-008", "matter_type": "SaaS Agreement Review", "client_company": "Meridian Financial Group", "description": "Meridian SaaS review with mandatory DPA and regulatory terms.", "typical_steps": ["Require DPA attachment", "Confirm data residency", "Enforce liability floor", "Verify regulatory cooperation clause"], "typical_duration_hours": 7, "last_used_matter_id": None},
    {"template_id": "TPL-009", "matter_type": "Vendor Contract Review", "client_company": "Northwind Logistics", "description": "Northwind fast-track vendor review; counterparty paper accepted.", "typical_steps": ["Confirm termination for convenience", "Check liability cap present", "Accept market-standard terms", "Deliver via email"], "typical_duration_hours": 2, "last_used_matter_id": None},
    {"template_id": "TPL-010", "matter_type": "NDA Review", "client_company": "Northwind Logistics", "description": "Northwind expedited NDA review.", "typical_steps": ["Confirm mutual", "Check term under 3 years", "Accept standard carve-outs", "Same-day turnaround"], "typical_duration_hours": 1, "last_used_matter_id": None},
    {"template_id": "TPL-011", "matter_type": "Licensing Agreement Review", "client_company": "Vertex Biosciences", "description": "Vertex IP-protective licensing review.", "typical_steps": ["Confirm no background IP assignment", "Carve IP indemnity from liability cap", "Protect publication rights", "Escalate any broad license grant"], "typical_duration_hours": 10, "last_used_matter_id": None},
    {"template_id": "TPL-012", "matter_type": "DPA Review", "client_company": "Vertex Biosciences", "description": "Vertex DPA review with clinical-data sensitivity.", "typical_steps": ["Confirm health-data handling", "Verify confidentiality survival", "Check cross-border transfer terms", "Confirm breach notification"], "typical_duration_hours": 4, "last_used_matter_id": None},
    {"template_id": "TPL-013", "matter_type": "Privacy Assessment", "client_company": None, "description": "Generic privacy impact assessment.", "typical_steps": ["Map data flows", "Identify lawful basis", "Assess data subject rights", "Document findings"], "typical_duration_hours": 8, "last_used_matter_id": None},
    {"template_id": "TPL-014", "matter_type": "Employment Agreement Review", "client_company": None, "description": "Generic employment agreement review.", "typical_steps": ["Review compensation terms", "Check restrictive covenants", "Confirm at-will language", "Review severance"], "typical_duration_hours": 3, "last_used_matter_id": None},
]
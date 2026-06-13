"""Mock matter scenarios for the legal-intake demo.

Each scenario is a realistic intake fact pattern. The seed generator
instantiates scenarios across the clients eligible for that kind of work,
creating multiple instances for high-volume contract types to mirror the
recurring nature of managed contract review. Descriptions are written to
contain the signal language the classify_matter tool keys on.
"""

# High-volume matter types: the generator creates multiple instances per
# eligible client to reflect recurring contract work.
HIGH_VOLUME_TYPES = {
    "NDA Review", "Vendor Contract Review", "SaaS Agreement Review",
    "MSA Review", "DPA Review", "Customer Contract Review",
}

# Seniority bands by complexity, used to staff a lead lawyer.
COMPLEXITY_SENIORITY = {
    "Routine": [1, 2],
    "Standard": [2, 3],
    "Complex": [3, 4],
    "Novel": [4, 5],
}

# Default estimated hours by complexity, when no template duration applies.
COMPLEXITY_HOURS = {"Routine": 3, "Standard": 6, "Complex": 12, "Novel": 20}

# In-house requesters per client (name, department).
REQUESTERS = {
    "Meridian Financial Group": [
        ("Katherine Wu", "Office of the General Counsel"),
        ("Daniel Brooks", "Commercial Legal"),
        ("Sofia Marin", "Compliance"),
    ],
    "Northwind Logistics": [
        ("Tom Bradley", "Legal"),
        ("Rebecca Cole", "Procurement Legal"),
    ],
    "Vertex Biosciences": [
        ("Dr. Helena Voss", "Office of the General Counsel"),
        ("Arjun Mehta", "Commercial Legal"),
        ("Lena Fischer", "Regulatory Affairs"),
    ],
}

M = "Meridian Financial Group"
N = "Northwind Logistics"
V = "Vertex Biosciences"
ANY = [M, N, V]

SCENARIOS = [
    {"matter_type": "MSA Review", "subject_matter": "Core-banking vendor MSA", "description": "Review of a master services agreement (MSA) for a new core-banking technology vendor. Counterparty paper; proposed liability cap of 3 months fees sits below the client's floor.", "counterparty": "CoreStack Technologies", "tags": ["MSA", "liability cap", "vendor"], "complexity": "Complex", "urgency": "Expedited", "eligible_clients": [M]},
    {"matter_type": "NDA Review", "subject_matter": "Mutual NDA for partnership talks", "description": "Mutual non-disclosure agreement (NDA) ahead of preliminary partnership discussions. Standard mutual form, short term.", "counterparty": "various", "tags": ["NDA", "mutual"], "complexity": "Routine", "urgency": "Routine", "eligible_clients": ANY},
    {"matter_type": "DPA Review", "subject_matter": "Cloud analytics DPA", "description": "Data processing agreement (DPA) for a cloud analytics vendor handling personal data. Cross-border transfer requires standard contractual clause review.", "counterparty": "Insightful Analytics", "tags": ["DPA", "GDPR", "cross-border"], "complexity": "Standard", "urgency": "Routine", "eligible_clients": [M, V]},
    {"matter_type": "SaaS Agreement Review", "subject_matter": "Enterprise HR SaaS", "description": "SaaS subscription agreement for an enterprise HR platform. Review SLA, data security terms, and automatic renewal provisions.", "counterparty": "PeopleFlow Inc.", "tags": ["SaaS", "SLA", "renewal"], "complexity": "Standard", "urgency": "Routine", "eligible_clients": ANY},
    {"matter_type": "Vendor Contract Review", "subject_matter": "Third-party logistics vendor", "description": "Vendor contract for a third-party logistics provider; high-volume procurement on counterparty paper. Confirm termination for convenience.", "counterparty": "RapidHaul LLC", "tags": ["vendor", "procurement", "logistics"], "complexity": "Routine", "urgency": "Expedited", "eligible_clients": [N]},
    {"matter_type": "Customer Contract Review", "subject_matter": "Enterprise customer order form", "description": "Customer sales agreement and order form for a new enterprise account. Customer proposes a non-standard indemnity.", "counterparty": "Apex Retail Group", "tags": ["customer contract", "indemnity"], "complexity": "Standard", "urgency": "Routine", "eligible_clients": [M, N]},
    {"matter_type": "Employment Agreement Review", "subject_matter": "Executive employment agreement", "description": "Senior executive employment agreement including a non-compete and severance terms. Review enforceability of restrictive covenants.", "counterparty": "internal", "tags": ["employment", "non-compete", "severance"], "complexity": "Standard", "urgency": "Routine", "eligible_clients": ANY},
    {"matter_type": "Licensing Agreement Review", "subject_matter": "Patent assay in-license", "description": "In-licensing agreement for a patented assay technology. Counterparty seeks assignment of improvements; background IP must be protected.", "counterparty": "Genomial Therapeutics", "tags": ["licensing", "IP", "patent"], "complexity": "Complex", "urgency": "Routine", "eligible_clients": [V]},
    {"matter_type": "Licensing Agreement Review", "subject_matter": "Risk-modeling software license", "description": "Enterprise software license for a risk-modeling platform. Review scope of the license grant and audit rights.", "counterparty": "QuantRisk Systems", "tags": ["licensing", "software"], "complexity": "Standard", "urgency": "Routine", "eligible_clients": [M]},
    {"matter_type": "Privacy Assessment", "subject_matter": "Mobile app privacy assessment", "description": "Privacy impact assessment for a new customer-facing mobile app processing personal data under GDPR and CCPA.", "counterparty": "internal", "tags": ["privacy", "GDPR", "CCPA", "assessment"], "complexity": "Complex", "urgency": "Routine", "eligible_clients": [M, V]},
    {"matter_type": "Regulatory Filing", "subject_matter": "New financial product filing", "description": "Preparation of a regulatory filing for a new financial product submission to the regulator.", "counterparty": "regulator", "tags": ["regulatory filing", "submission"], "complexity": "Standard", "urgency": "Expedited", "eligible_clients": [M]},
    {"matter_type": "Policy Drafting", "subject_matter": "InfoSec policy update", "description": "Drafting an updated information security policy and an employee handbook section on acceptable use.", "counterparty": "internal", "tags": ["policy", "handbook"], "complexity": "Routine", "urgency": "Routine", "eligible_clients": [M, V]},
    {"matter_type": "Document Review", "subject_matter": "Contract dispute doc review", "description": "Large-scale document review for responsive documents in a contract dispute. Privilege review required.", "counterparty": "opposing counsel", "tags": ["document review", "privilege"], "complexity": "Complex", "urgency": "Expedited", "eligible_clients": [V]},
    {"matter_type": "E-Discovery", "subject_matter": "Litigation ESI processing", "description": "Electronic discovery and ESI processing for pending litigation; roughly 200GB of custodian data to ingest.", "counterparty": "opposing counsel", "tags": ["e-discovery", "ESI"], "complexity": "Complex", "urgency": "Urgent", "eligible_clients": [V]},
    {"matter_type": "Deposition Prep", "subject_matter": "Witness deposition prep", "description": "Deposition preparation support including witness prep materials and exhibit organization.", "counterparty": "opposing counsel", "tags": ["deposition", "witness prep"], "complexity": "Standard", "urgency": "Expedited", "eligible_clients": [V]},
    {"matter_type": "CLM Administration", "subject_matter": "CLM metadata maintenance", "description": "Ongoing contract lifecycle management (CLM) administration: metadata cleanup and template library maintenance.", "counterparty": "n/a", "tags": ["CLM", "administration"], "complexity": "Routine", "urgency": "Routine", "eligible_clients": [N]},
    {"matter_type": "Contract Migration", "subject_matter": "Legacy contract migration", "description": "Migration of legacy contracts into the new CLM system, including data extraction and metadata tagging for roughly 1,200 agreements.", "counterparty": "n/a", "tags": ["migration", "data extraction", "CLM"], "complexity": "Complex", "urgency": "Routine", "eligible_clients": [N]},
    {"matter_type": "Playbook Development", "subject_matter": "Vendor negotiation playbook", "description": "Development of a vendor-contract negotiation playbook with fallback positions for the procurement team.", "counterparty": "n/a", "tags": ["playbook", "negotiation"], "complexity": "Standard", "urgency": "Routine", "eligible_clients": [N]},
    {"matter_type": "Lease Review", "subject_matter": "Distribution center lease", "description": "Commercial lease review for a new regional distribution center. Review rent escalation and assignment rights.", "counterparty": "Crossroads Property LP", "tags": ["lease", "real estate"], "complexity": "Standard", "urgency": "Routine", "eligible_clients": [N]},
    {"matter_type": "Sublease Management", "subject_matter": "Warehouse sublease", "description": "Sublease agreement for surplus warehouse space; review sublet rights under the master lease.", "counterparty": "BoxStore Holdings", "tags": ["sublease", "real estate"], "complexity": "Routine", "urgency": "Routine", "eligible_clients": [N]},
    {"matter_type": "AML/KYC Review", "subject_matter": "Correspondent banking KYC", "description": "Review of AML/KYC onboarding procedures for a new correspondent banking relationship.", "counterparty": "n/a", "tags": ["AML", "KYC", "onboarding"], "complexity": "Complex", "urgency": "Routine", "eligible_clients": [M]},
    {"matter_type": "Financial Crime Review", "subject_matter": "Cross-border payments screening", "description": "Financial crime and sanctions screening review for a new cross-border payments product.", "counterparty": "n/a", "tags": ["financial crime", "sanctions"], "complexity": "Complex", "urgency": "Expedited", "eligible_clients": [M]},
    {"matter_type": "Regulatory Research", "subject_matter": "Digital asset custody research", "description": "Regulatory research memorandum on emerging requirements for digital asset custody.", "counterparty": "n/a", "tags": ["regulatory research", "digital assets"], "complexity": "Standard", "urgency": "Routine", "eligible_clients": [M]},
    {"matter_type": "MSA Review", "subject_matter": "Clinical CRO MSA", "description": "Master services agreement (MSA) with a contract research organization (CRO) for clinical trial services. Protect data and publication rights.", "counterparty": "BioTrial CRO", "tags": ["MSA", "CRO", "clinical"], "complexity": "Complex", "urgency": "Routine", "eligible_clients": [V]},
    {"matter_type": "Vendor Contract Review", "subject_matter": "Lab equipment purchase", "description": "Vendor purchase agreement for laboratory equipment with maintenance and warranty terms.", "counterparty": "LabTech Instruments", "tags": ["vendor", "equipment"], "complexity": "Routine", "urgency": "Routine", "eligible_clients": [V]},
    {"matter_type": "NDA Review", "subject_matter": "One-way NDA for acquisition", "description": "One-way non-disclosure agreement (NDA) to receive confidential information from a potential acquisition target.", "counterparty": "undisclosed target", "tags": ["NDA", "one-way", "M&A"], "complexity": "Standard", "urgency": "Routine", "eligible_clients": [V]},
    {"matter_type": "Vendor Contract Review", "subject_matter": "Fleet fuel supply", "description": "Fuel supply vendor agreement for the fleet; high-volume and recurring, on counterparty paper, expedited.", "counterparty": "FleetFuel Partners", "tags": ["vendor", "fuel", "fleet"], "complexity": "Routine", "urgency": "Expedited", "eligible_clients": [N]},
]

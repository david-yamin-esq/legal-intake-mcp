"""Service taxonomy for legal matter intake.

Defines the ALSP service structure that matters get classified into,
plus the keyword signals used for deterministic first-pass classification.

Modeled on the service lines of a legal managed-services provider serving
corporate in-house legal, compliance, and HR functions: high-volume contract
review, regulatory compliance, litigation support, legal operations, real
estate, and financial-services compliance.
"""

# Top-level service categories. Each maps to a delivery team.
SERVICE_CATEGORIES = {
    "Contract Review": "Review, redlining, and negotiation support for commercial agreements",
    "Compliance & Regulatory": "Privacy, regulatory, and policy work for in-house compliance teams",
    "Litigation Support": "Document review, e-discovery, and litigation workflow support",
    "Legal Operations": "CLM administration, contract migration, and playbook development",
    "Real Estate": "Lease review, sublease management, and real estate documentation",
    "Financial Services Compliance": "AML/KYC, financial crime, and FS regulatory work",
}

# Matter types within each service category.
MATTER_TYPES = {
    # Contract Review
    "MSA Review": "Contract Review",
    "NDA Review": "Contract Review",
    "DPA Review": "Contract Review",
    "SaaS Agreement Review": "Contract Review",
    "Vendor Contract Review": "Contract Review",
    "Customer Contract Review": "Contract Review",
    "Employment Agreement Review": "Contract Review",
    "Licensing Agreement Review": "Contract Review",
    # Compliance & Regulatory
    "Privacy Assessment": "Compliance & Regulatory",
    "Regulatory Filing": "Compliance & Regulatory",
    "Policy Drafting": "Compliance & Regulatory",
    # Litigation Support
    "Document Review": "Litigation Support",
    "E-Discovery": "Litigation Support",
    "Deposition Prep": "Litigation Support",
    # Legal Operations
    "CLM Administration": "Legal Operations",
    "Contract Migration": "Legal Operations",
    "Playbook Development": "Legal Operations",
    # Real Estate
    "Lease Review": "Real Estate",
    "Sublease Management": "Real Estate",
    # Financial Services Compliance
    "AML/KYC Review": "Financial Services Compliance",
    "Financial Crime Review": "Financial Services Compliance",
    "Regulatory Research": "Financial Services Compliance",
}

# Keyword signals for deterministic first-pass classification.
# Each matter type maps to lowercase signal phrases. classify_matter scans the
# description for these and scores candidates by how many distinct signals
# match. This is the "mechanical first" layer — explainable and deterministic —
# that the host LLM then reasons over.
MATTER_TYPE_SIGNALS = {
    "MSA Review": ["master services agreement", "msa", "master service agreement"],
    "NDA Review": ["nda", "non-disclosure", "nondisclosure", "confidentiality agreement"],
    "DPA Review": ["dpa", "data processing agreement", "data protection addendum"],
    "SaaS Agreement Review": ["saas", "software as a service", "subscription agreement", "cloud services agreement"],
    "Vendor Contract Review": ["vendor", "supplier", "procurement", "purchase agreement"],
    "Customer Contract Review": ["customer agreement", "sales agreement", "order form", "customer contract"],
    "Employment Agreement Review": ["employment agreement", "offer letter", "severance", "non-compete", "noncompete"],
    "Licensing Agreement Review": ["license agreement", "licensing", "ip license", "patent license"],
    "Privacy Assessment": ["gdpr", "ccpa", "privacy", "personal data", "data subject"],
    "Regulatory Filing": ["regulatory filing", "filing", "regulator", "submission to"],
    "Policy Drafting": ["policy", "handbook", "code of conduct"],
    "Document Review": ["document review", "doc review", "review documents", "responsive documents"],
    "E-Discovery": ["e-discovery", "ediscovery", "electronic discovery", "esi"],
    "Deposition Prep": ["deposition", "depo prep", "witness prep"],
    "CLM Administration": ["clm", "contract lifecycle", "contract management system"],
    "Contract Migration": ["migration", "migrate contracts", "data extraction", "legacy contracts"],
    "Playbook Development": ["playbook", "negotiation guidelines", "fallback positions"],
    "Lease Review": ["lease", "tenancy", "landlord", "premises"],
    "Sublease Management": ["sublease", "sublet", "subletting"],
    "AML/KYC Review": ["aml", "kyc", "know your customer", "anti-money laundering"],
    "Financial Crime Review": ["financial crime", "fraud review", "sanctions screening"],
    "Regulatory Research": ["regulatory research", "regulatory analysis", "regulatory landscape"],
}

# Complexity signals — phrases suggesting a matter is more than routine.
COMPLEXITY_SIGNALS = {
    "Novel": ["novel", "first of its kind", "unprecedented", "no precedent", "bespoke"],
    "Complex": ["complex", "high-value", "high value", "cross-border", "multi-jurisdiction", "regulatory scrutiny"],
    "Standard": ["negotiation", "redline", "counterparty pushback", "non-standard", "nonstandard", "amended"],
}

# Urgency signals.
URGENCY_SIGNALS = {
    "Urgent": ["urgent", "immediately", "asap", "emergency", "drop everything"],
    "Expedited": ["expedited", "rush", "expedite", "time-sensitive", "tight deadline", "by end of week", "eod", "eow"],
}
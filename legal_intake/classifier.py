"""Deterministic first-pass matter classification.

Scans a matter description against the keyword signals defined in taxonomy.py
and returns ranked candidate matter types, each with a confidence score and
the specific signals that matched. This is the "mechanical first" layer: no
LLM call happens here. The host model reasons over this structured output to
make the actual routing recommendation.
"""

import re

from legal_intake.taxonomy import (
    MATTER_TYPES,
    MATTER_TYPE_SIGNALS,
    COMPLEXITY_SIGNALS,
    URGENCY_SIGNALS,
)


def _matched_signals(text_lower, signals):
    """Return signal phrases that appear as whole words/phrases.

    Uses word-boundary matching so short signals like "nda" or "lease" match
    only as standalone terms, not as substrings inside larger words ("Please"
    must not match "lease"). re.escape handles signals containing regex-special
    characters like "e-discovery".
    """
    matched = []
    for s in signals:
        if re.search(r"\b" + re.escape(s) + r"\b", text_lower):
            matched.append(s)
    return matched


def classify(description: str):
    """Classify a matter description.

    Returns a dict with ranked matter-type candidates, an assessed complexity
    and urgency, and the matched signals behind each, so the result is fully
    explainable.
    """
    text_lower = description.lower()

    candidates = []
    for matter_type, signals in MATTER_TYPE_SIGNALS.items():
        hits = _matched_signals(text_lower, signals)
        if hits:
            confidence = min(0.95, 0.55 + 0.20 * (len(hits) - 1) + 0.20)
            candidates.append({
                "matter_type": matter_type,
                "service_category": MATTER_TYPES[matter_type],
                "confidence": round(confidence, 2),
                "matched_signals": hits,
            })

    candidates.sort(key=lambda c: (-c["confidence"], -len(c["matched_signals"])))

    complexity = "Standard"
    complexity_hits = {}
    for band in ("Novel", "Complex", "Standard"):
        hits = _matched_signals(text_lower, COMPLEXITY_SIGNALS.get(band, []))
        if hits:
            complexity_hits[band] = hits
    for band in ("Novel", "Complex", "Standard"):
        if band in complexity_hits:
            complexity = band
            break
    if not complexity_hits:
        complexity = "Routine"

    urgency = "Routine"
    urgency_hits = {}
    for band in ("Urgent", "Expedited"):
        hits = _matched_signals(text_lower, URGENCY_SIGNALS.get(band, []))
        if hits:
            urgency_hits[band] = hits
    for band in ("Urgent", "Expedited"):
        if band in urgency_hits:
            urgency = band
            break

    return {
        "candidates": candidates,
        "top_matter_type": candidates[0]["matter_type"] if candidates else None,
        "top_service_category": candidates[0]["service_category"] if candidates else None,
        "assessed_complexity": complexity,
        "assessed_urgency": urgency,
        "complexity_signals": complexity_hits,
        "urgency_signals": urgency_hits,
        "note": (
            "Deterministic keyword classification. No candidates means no known "
            "signals matched; the matter may need manual triage or a description "
            "with more detail."
        ),
    }
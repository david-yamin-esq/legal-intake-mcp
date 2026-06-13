"""legal-intake MCP server.

Exposes matter-intake tools over the Model Context Protocol for use in
Claude Desktop or any MCP client. Tool logic lives in the legal_intake
package; this module is the thin MCP surface.

Tools:
  ping                  — liveness check
  classify_matter       — deterministic first-pass classification
  find_similar_matters  — retrieve resembling past matters
  check_client_history  — client profile, history, preferences, templates
  get_matter_history    — full detail on a specific matter
  suggest_staffing      — rank lead-lawyer candidates (advisory)
  flag_for_escalation   — surface escalation candidates for human judgment
"""

from mcp.server.fastmcp import FastMCP

from legal_intake.classifier import classify
from legal_intake.queries import (
    find_similar_matters as _find_similar_matters,
    check_client_history as _check_client_history,
    get_matter_history as _get_matter_history,
)
from legal_intake.staffing import (
    suggest_staffing as _suggest_staffing,
    flag_for_escalation as _flag_for_escalation,
)

mcp = FastMCP("legal-intake")


@mcp.tool()
def ping() -> str:
    """Confirm the legal-intake MCP server is alive."""
    return "legal-intake MCP server is running."


@mcp.tool()
def classify_matter(description: str) -> dict:
    """Classify an incoming legal matter from its description.

    Performs a deterministic, keyword-based first-pass classification. Returns
    ranked candidate matter types (each with a confidence score and the signal
    phrases that matched), the most likely service category, and an assessed
    complexity and urgency. This is a triage aid, not a final determination;
    the matched signals make every result explainable. An empty candidate list
    means no known signals matched — triage manually or get more detail.

    Args:
        description: Free-text description of the incoming matter.
    """
    return classify(description)


@mcp.tool()
def find_similar_matters(description: str, client_company: str = None) -> dict:
    """Find past matters resembling a described new matter.

    Classifies the description, then retrieves past matters of the candidate
    types, ranked by type-match strength and (if a client is given) a
    same-client boost. Useful for precedent, staffing estimates, and spotting
    how comparable matters were handled and resolved.

    Args:
        description: Free-text description of the new matter.
        client_company: Optional client name to prioritize that client's matters.
    """
    return _find_similar_matters(description, client_company)


@mcp.tool()
def check_client_history(client_company: str) -> dict:
    """Summarize the firm's history and standing preferences for a client.

    Returns the client profile (including standing preferences that should
    guide how matters are handled), recent matters, a matter-type history, and
    the templates applicable to this client. Use this to answer "have we done
    this before for this client, and how do they want it handled?"

    Args:
        client_company: The client company name.
    """
    return _check_client_history(client_company)


@mcp.tool()
def get_matter_history(matter_id: str) -> dict:
    """Retrieve full detail on a specific past matter by its ID.

    Args:
        matter_id: The matter identifier, e.g. "GC-0001".
    """
    return _get_matter_history(matter_id)


@mcp.tool()
def suggest_staffing(matter_type: str, complexity: str = "Standard",
                     client_company: str = None) -> dict:
    """Recommend lead-lawyer candidates for a matter.

    Routes the matter type to its delivery team and ranks team members by
    seniority-fit for the complexity, then available capacity. Capacity is
    advisory — a strong expertise or seniority match can justify assigning
    someone with less headroom. Final staffing is a human decision.

    Args:
        matter_type: A matter type from classify_matter, e.g. "MSA Review".
        complexity: "Routine", "Standard", "Complex", or "Novel".
        client_company: Optional client name (reserved for future client-aware staffing).
    """
    return _suggest_staffing(matter_type, complexity, client_company)


@mcp.tool()
def flag_for_escalation(description: str, client_company: str = None) -> dict:
    """Assess whether a matter should be escalated to the client's in-house team.

    Scans for general escalation signals (novel issues, liability above norm,
    IP exposure, regulatory exposure, material commitments) and, when a client
    is given, reports that client's stated escalation threshold so the two can
    be weighed together. This tool surfaces a recommendation and its reasons;
    it does NOT decide. Escalation is always a human call.

    Args:
        description: Free-text description of the matter.
        client_company: Optional client name to check against their threshold.
    """
    return _flag_for_escalation(description, client_company)


if __name__ == "__main__":
    mcp.run()
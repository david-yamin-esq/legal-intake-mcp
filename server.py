"""legal-intake MCP server.

Exposes matter-intake tools over the Model Context Protocol for use in
Claude Desktop or any MCP client. Tool logic lives in the legal_intake
package; this module is the thin MCP surface.
"""

from mcp.server.fastmcp import FastMCP

from legal_intake.classifier import classify

mcp = FastMCP("legal-intake")


@mcp.tool()
def ping() -> str:
    """Confirm the legal-intake MCP server is alive."""
    return "legal-intake MCP server is running."


@mcp.tool()
def classify_matter(description: str) -> dict:
    """Classify an incoming legal matter from its description.

    Performs a deterministic, keyword-based first-pass classification of a
    matter intake request. Returns ranked candidate matter types (each with a
    confidence score and the specific signal phrases that matched), the most
    likely service category, and an assessed complexity and urgency.

    This is a first-pass triage aid, not a final determination. The matched
    signals are included so the classification is fully explainable. When no
    candidates are returned, no known signals matched and the matter should be
    triaged manually or described in more detail.

    Args:
        description: Free-text description of the incoming matter — what kind
            of work is being requested, on what kind of document or issue.
    """
    return classify(description)


if __name__ == "__main__":
    mcp.run()
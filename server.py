"""Minimal MCP server to verify the toolchain works.

This will be replaced by the matter intake server.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("legal-intake")


@mcp.tool()
def ping() -> str:
    """Confirm the legal-intake MCP server is alive."""
    return "legal-intake MCP server is running."


@mcp.tool()
def echo_matter(description: str) -> str:
    """Echo back a matter description. Placeholder for classify_matter."""
    return f"Received matter description ({len(description)} chars): {description}"


if __name__ == "__main__":
    mcp.run()
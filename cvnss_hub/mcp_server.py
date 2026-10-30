"""Run with: python -m cvnss_hub.mcp_server (requires pip install mcp)."""
from .service import execute

def main() -> None:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("CVNSS4.0 Knowledge Hub")

    @mcp.tool()
    def cvnss_convert(text: str, mode: str = "cqn") -> dict:
        """Convert input interpreted as cqn, cvn or cvss to all three representations."""
        return execute("convert", text=text, mode=mode)

    @mcp.tool()
    def cvnss_inspect(word: str, source: str = "cvss") -> dict:
        """Explain canonical decoding and ambiguity for one encoded word."""
        return execute("inspect", text=word, source=source)

    @mcp.tool()
    def cvnss_candidates(word: str, source: str = "cvss") -> dict:
        """List competing Vietnamese decode candidates without silently discarding them."""
        return execute("candidates", text=word, source=source)

    @mcp.tool()
    def cvnss_audit() -> dict:
        """Show converter rule inventory, collision handling and deterministic audit counts."""
        return execute("audit")

    @mcp.tool()
    def cvnss_self_test() -> dict:
        """Run built-in deterministic converter checks."""
        return execute("self_test")

    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()

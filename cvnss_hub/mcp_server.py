"""CVNSS4.0 MCP server. Default: stdio; --http: Streamable HTTP for tunnelling."""
import argparse
import os
from .service import execute

def main() -> None:
    parser = argparse.ArgumentParser(description="CVNSS4.0 MCP service")
    parser.add_argument("--http", action="store_true", help="Run Streamable HTTP at /mcp")
    parser.add_argument("--host", default=os.getenv("CVNSS_MCP_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("CVNSS_MCP_PORT", "8000")))
    args = parser.parse_args()
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("CVNSS4.0 Knowledge Hub", host=args.host, port=args.port)

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

    mcp.run(transport="streamable-http" if args.http else "stdio")

if __name__ == "__main__":
    main()

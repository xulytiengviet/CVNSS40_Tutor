"""CVNSS4.0 MCP server. Default stdio; --http exposes local Streamable HTTP."""
from __future__ import annotations

import argparse
import os
from typing import Literal

from .service import execute


def main() -> None:
    parser = argparse.ArgumentParser(description="CVNSS4.0 Knowledge Hub MCP server")
    parser.add_argument("--http", action="store_true", help="Serve Streamable HTTP on /mcp")
    parser.add_argument("--host", default=os.getenv("CVNSS_MCP_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("CVNSS_MCP_PORT", "8000")))
    args = parser.parse_args()
    if args.http and args.host not in {"127.0.0.1", "localhost", "::1"}:
        parser.error(
            "Unauthenticated MCP HTTP must listen on loopback. "
            "Use an authenticated reverse proxy or Secure MCP Tunnel instead."
        )
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("CVNSS4.0 Knowledge Hub", host=args.host, port=args.port)

    @mcp.tool()
    def cvnss_convert(text: str, mode: Literal["cqn", "cvn", "cvss"] = "cqn") -> dict:
        """Deterministically convert CQN, CVN, CVSS. Pass the input's format via mode."""
        return execute("convert", text=text, mode=mode)

    @mcp.tool()
    def cvnss_inspect(word: str, source: Literal["cvn", "cvss"] = "cvss") -> dict:
        """Inspect one code word, candidates, canonical choice and collisions."""
        return execute("inspect", text=word, source=source)

    @mcp.tool()
    def cvnss_candidates(word: str, source: Literal["cvn", "cvss"] = "cvss") -> dict:
        """List ALL possible CQN decoding candidates of one encoded word."""
        return execute("candidates", text=word, source=source)

    @mcp.tool()
    def cvnss_audit() -> dict:
        """Return audited converter rule and ambiguity inventory (not accuracy rates)."""
        return execute("audit")

    @mcp.tool()
    def cvnss_self_test() -> dict:
        """Execute the converter's 23 built-in deterministic checks."""
        return execute("self_test")

    @mcp.tool()
    def cvnss_sources() -> dict:
        """List curated original CVNSS4.0 source links and ingestion status. No full-text RAG."""
        return execute("sources")

    mcp.run(transport="streamable-http" if args.http else "stdio")


if __name__ == "__main__":
    main()

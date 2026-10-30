"""CVNSS4.0 MCP: stdio locally, HTTP on loopback, or explicit hosted read-only mode."""
from __future__ import annotations

import argparse
import os
import re
from typing import Literal

from .service import execute


def make_mcp(*, host: str = "127.0.0.1", port: int = 8000, public_host: str | None = None):
    """Build the read-only MCP server shared by local and hosted transports.

    A public hostname adds a Host allowlist entry; it does NOT provide OAuth.
    The hosted deployment is intentionally anonymous and read-only.
    """
    from mcp.server.fastmcp import FastMCP
    from mcp.server.transport_security import TransportSecuritySettings

    if public_host is not None and not re.fullmatch(
        r"[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?", public_host
    ):
        raise ValueError("public_host must be a bare DNS hostname")

    allowed_hosts = [
        "127.0.0.1", "127.0.0.1:*", "localhost", "localhost:*",
        "[::1]", "[::1]:*",
    ]
    allowed_origins = ["http://127.0.0.1:*", "http://localhost:*", "http://[::1]:*"]
    if public_host:
        allowed_hosts.extend([public_host, public_host + ":*"])
        # Browser Origins are deliberately not broadly allowed; no wildcard CORS.
        origin = os.getenv("CVNSS_MCP_TRUSTED_ORIGIN", "").strip()
        if origin:
            if not re.fullmatch(r"https://[A-Za-z0-9.-]+(?::[0-9]{1,5})?", origin):
                raise ValueError("CVNSS_MCP_TRUSTED_ORIGIN must be one exact HTTPS origin")
            allowed_origins.append(origin)
    security = TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=allowed_hosts,
        allowed_origins=allowed_origins,
    )
    mcp = FastMCP(
        "CVNSS4.0 Knowledge Hub",
        host=host,
        port=port,
        transport_security=security,
        stateless_http=True,
        json_response=True,
    )

    @mcp.tool()
    def cvnss_convert(text: str, mode: Literal["cqn", "cvn", "cvss"] = "cqn") -> dict:
        """Convert CQN, CVN or CVSS deterministically; mode describes the input."""
        return execute("convert", text=text, mode=mode)

    @mcp.tool()
    def cvnss_inspect(word: str, source: Literal["cvn", "cvss"] = "cvss") -> dict:
        """Inspect ambiguity, candidates and canonical choice of one encoded word."""
        return execute("inspect", text=word, source=source)

    @mcp.tool()
    def cvnss_candidates(word: str, source: Literal["cvn", "cvss"] = "cvss") -> dict:
        """List competing candidates without pretending ambiguous decoding is lossless."""
        return execute("candidates", text=word, source=source)

    @mcp.tool()
    def cvnss_audit() -> dict:
        """Read converter rule inventory and ambiguity metrics, not accuracy rates."""
        return execute("audit")

    @mcp.tool()
    def cvnss_self_test() -> dict:
        """Run the converter's deterministic 23-case self-test."""
        return execute("self_test")

    @mcp.tool()
    def cvnss_sources() -> dict:
        """List curated sources; this is a URL registry, not an ingested RAG corpus."""
        return execute("sources")

    @mcp.tool()
    def cvnss_knowledge(topic: str = "all") -> dict:
        """Read the draft standardization registry, not official rules or full-text RAG.

        Topics: all, history, concepts, nature, characteristics, functions,
        rules, formulas, value, applications, limitations. Preserve evidence_type,
        review_status and source_refs when explaining records.
        """
        return execute("knowledge", text=topic)

    return mcp


def main() -> None:
    parser = argparse.ArgumentParser(description="CVNSS4.0 MCP service")
    parser.add_argument("--http", action="store_true", help="Serve local Streamable HTTP")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--trusted-hostname", default=None, help="Host allowlist for trusted proxy")
    parser.add_argument("--trusted-origin", default=None, help="Exact HTTPS browser origin")
    args = parser.parse_args()
    if args.http and args.host not in {"127.0.0.1", "localhost", "::1"}:
        parser.error("Local HTTP may only bind loopback; use hosted.py for public mode")
    if args.trusted_origin:
        os.environ["CVNSS_MCP_TRUSTED_ORIGIN"] = args.trusted_origin
    try:
        mcp = make_mcp(
            host=args.host, port=args.port, public_host=args.trusted_hostname
        )
    except ValueError as exc:
        parser.error(str(exc))
    mcp.run(transport="streamable-http" if args.http else "stdio")


if __name__ == "__main__":
    main()

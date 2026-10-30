"""Minimal, explicitly opted-in, anonymous read-only MCP web deployment.

Designed for Git-linked HTTPS PaaS (e.g. Render) with a fixed hostname.
No user accounts, write tools, personal memory or source-document ingestion.
"""
from __future__ import annotations

import asyncio
from collections import deque
import os
import time

from .mcp_server import make_mcp


def create_hosted_app():
    """Fail closed unless deployer deliberately enables public anonymous tools."""
    if os.environ.get("CVNSS_MCP_PUBLIC_ANONYMOUS") != "yes":
        raise RuntimeError(
            "Public HTTP is disabled. Set CVNSS_MCP_PUBLIC_ANONYMOUS=yes only "
            "for the documented read-only, non-personal server."
        )
    hostname = (
        os.environ.get("CVNSS_MCP_PUBLIC_HOSTNAME")
        or os.environ.get("RENDER_EXTERNAL_HOSTNAME")
        or ""
    ).strip().lower()
    if not hostname:
        raise RuntimeError("Configure CVNSS_MCP_PUBLIC_HOSTNAME or RENDER_EXTERNAL_HOSTNAME")
    from starlette.responses import JSONResponse

    mcp = make_mcp(host="0.0.0.0", public_host=hostname)
    inner = mcp.streamable_http_app()

    # Per-instance, non-distributed request cap: an extra protection for a
    # public, unauthenticated demonstration. The hosting edge must also rate-limit.
    max_per_minute = int(os.getenv("CVNSS_MCP_MAX_REQUESTS_PER_MINUTE", "60"))
    if max_per_minute < 1 or max_per_minute > 600:
        raise ValueError("CVNSS_MCP_MAX_REQUESTS_PER_MINUTE must be in 1..600")
    seen: deque[float] = deque()
    lock = asyncio.Lock()

    async def app(scope, receive, send):
        if scope["type"] != "http":
            await inner(scope, receive, send)
            return
        path = scope.get("path", "")
        if path == "/healthz" and scope.get("method") == "GET":
            await JSONResponse(
                {"ok": True, "service": "cvnss4-mcp", "auth": "anonymous-read-only"},
                headers={"Cache-Control": "no-store"},
            )(scope, receive, send)
            return
        if path != "/mcp":
            await JSONResponse({"detail": "Not found"}, status_code=404)(
                scope, receive, send
            )
            return
        headers = {k.lower(): v for k, v in scope.get("headers", [])}
        length = headers.get(b"content-length")
        if length:
            try:
                declared_length = int(length)
            except ValueError:
                declared_length = -1
            if declared_length < 0 or declared_length > 262144:
                await JSONResponse({"detail": "Request too large"}, status_code=413)(
                    scope, receive, send
                )
                return
        async with lock:
            now = time.monotonic()
            while seen and now - seen[0] >= 60:
                seen.popleft()
            limited = len(seen) >= max_per_minute
            if not limited:
                seen.append(now)
        if limited:
            await JSONResponse(
                {"detail": "Too many requests"}, status_code=429,
                headers={"Retry-After": "60"},
            )(scope, receive, send)
            return

        # Cap even chunked uploads, returning a bounded HTTP response rather
        # than raising inside the SDK's asynchronous request handler.
        if scope.get("method") == "POST":
            buffer = bytearray()
            while True:
                message = await receive()
                if message["type"] != "http.request":
                    return
                buffer.extend(message.get("body", b""))
                if len(buffer) > 262144:
                    await JSONResponse(
                        {"detail": "Request too large"}, status_code=413
                    )(scope, receive, send)
                    return
                if not message.get("more_body", False):
                    break

            first = True

            async def replay_receive():
                nonlocal first
                if first:
                    first = False
                    return {"type": "http.request", "body": bytes(buffer), "more_body": False}
                return await receive()

            await inner(scope, replay_receive, send)
        else:
            await inner(scope, receive, send)

    return app


app = create_hosted_app()

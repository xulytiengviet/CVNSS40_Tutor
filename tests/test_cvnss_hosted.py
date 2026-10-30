"""Hosted MCP safety regression tests; no network requests or credentials."""
import importlib
import sys

import pytest


def _load_hosted(monkeypatch, **env):
    for name in ("CVNSS_MCP_PUBLIC_ANONYMOUS", "RENDER_EXTERNAL_HOSTNAME",
                 "CVNSS_MCP_PUBLIC_HOSTNAME", "CVNSS_MCP_TRUSTED_ORIGIN"):
        monkeypatch.delenv(name, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    sys.modules.pop("cvnss_hub.hosted", None)
    return importlib.import_module("cvnss_hub.hosted")


def test_hosted_refuses_implicit_public_listener(monkeypatch):
    with pytest.raises(RuntimeError, match="Public HTTP is disabled"):
        _load_hosted(monkeypatch)


def test_hosted_requires_hostname(monkeypatch):
    with pytest.raises(RuntimeError, match="RENDER_EXTERNAL_HOSTNAME"):
        _load_hosted(monkeypatch, CVNSS_MCP_PUBLIC_ANONYMOUS="yes")


def test_hosted_readonly_opt_in(monkeypatch):
    module = _load_hosted(
        monkeypatch,
        CVNSS_MCP_PUBLIC_ANONYMOUS="yes",
        RENDER_EXTERNAL_HOSTNAME="cvnss-test.onrender.com",
    )
    from starlette.testclient import TestClient
    with TestClient(module.app) as client:
        ready = client.get("/healthz")
        assert ready.status_code == 200
        assert ready.json()["auth"] == "anonymous-read-only"
        assert client.get("/missing").status_code == 404

"""Regression smoke tests for the CVNSS4.0 hub."""
import shutil
import pytest
from cvnss_hub.service import execute

pytestmark = pytest.mark.skipif(not shutil.which("node"), reason="Node.js required")

def test_self_test():
    result = execute("self_test")
    assert result["ok"] is True
    assert result["tests"] == 23

def test_audit():
    report = execute("audit")
    assert report["version"] == "5.0.0-audit-safe"
    assert report["ambiguityGroups"] == 56
    assert report["silentReverseOverwrite"] == 0

def test_converter_roundtrip_contract():
    conversion = execute("convert", text="Tiếng Việt", mode="cqn")
    assert conversion["cqn"] == "Tiếng Việt"
    assert "cvss" in conversion and "cvn" in conversion

def test_ambiguity_surface():
    candidates = execute("candidates", text="ed")
    assert len(candidates["candidates"]) > 1

def test_invalid_mode():
    with pytest.raises(ValueError):
        execute("convert", text="hi", mode="unsupported")

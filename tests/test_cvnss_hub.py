"""Regression checks for the standalone CVNSS4.0 oracle and source registry."""
import shutil

import pytest

from cvnss_hub.service import execute


def test_sources_registry():
    result = execute("sources")
    assert result["schema"] == "cvnss4-source-registry/v1"
    assert any(x["id"] == "formula" for x in result["sources"])
    assert all("url" in x and "content_status" in x for x in result["sources"])


@pytest.mark.skipif(not shutil.which("node"), reason="Node.js required")
def test_self_test():
    result = execute("self_test")
    assert result["ok"] is True
    assert result["tests"] == 23
    assert result["failures"] == []


@pytest.mark.skipif(not shutil.which("node"), reason="Node.js required")
def test_audit():
    report = execute("audit")
    assert report["version"] == "5.0.0-audit-safe"
    assert report["baseRows"] == 758
    assert report["totalPatchEntries"] == 336
    assert report["ambiguityGroups"] == 56
    assert report["criticalCollisionGroups"] == 5
    assert report["silentReverseOverwrite"] == 0


@pytest.mark.skipif(not shutil.which("node"), reason="Node.js required")
def test_converter_roundtrip_contract():
    result = execute("convert", text="Tiếng Việt", mode="cqn")
    assert result == {"cqn": "Tiếng Việt", "cvn": "Tizb Vidf", "cvss": "Tizb Vidf"}


@pytest.mark.skipif(not shutil.which("node"), reason="Node.js required")
def test_ambiguity_surface():
    report = execute("inspect", text="ed")
    assert report["ambiguous"] is True
    assert report["critical"] is True
    assert report["selected"] == "ề"
    assert report["candidates"] == ["ề", "oet"]
    result = execute("candidates", text="ed")
    assert result["candidates"] == report["candidates"]


@pytest.mark.parametrize("mode", ["invalid", "", "CQN"])
def test_invalid_mode(mode):
    with pytest.raises(ValueError):
        execute("convert", text="hi", mode=mode)


@pytest.mark.parametrize("operation,text", [("inspect", ""), ("candidates", "a"*201)])
def test_invalid_word(operation, text):
    with pytest.raises(ValueError):
        execute(operation, text=text)

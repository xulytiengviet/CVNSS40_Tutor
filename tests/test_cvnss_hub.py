"""Regression checks for the standalone CVNSS4.0 oracle and source registry."""
import shutil
import copy
import json
from pathlib import Path

import pytest

from cvnss_hub.service import execute


def test_knowledge_contract_and_provenance():
    from jsonschema import Draft202012Validator, FormatChecker

    root = Path(__file__).resolve().parents[1] / "cvnss_hub"
    schema = json.loads((root / "knowledge.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    data = execute("knowledge")
    validator.validate(data)
    assert len(data["topics"]) == 10
    assert len({r["id"] for r in data["records"]}) == len(data["records"])
    assert {r["topic"] for r in data["records"]} == {t["id"] for t in data["topics"]}
    source_ids = {s["id"] for s in execute("sources")["sources"]}
    assert all(set(r["source_refs"]) <= source_ids for r in data["records"])
    # Unreviewed content cannot be promoted simply by toggling its status.
    unreviewed = copy.deepcopy(data)
    unreviewed["records"][0]["review_status"] = "approved"
    assert list(validator.iter_errors(unreviewed))
    primary = copy.deepcopy(data)
    primary["records"][0].update(
        evidence_type="primary_source", review_status="approved",
        source_refs=["formula"], source_locator="section 1",
        reviewer="test reviewer", reviewed_at="2026-10-30",
    )
    assert list(validator.iter_errors(primary))  # missing exact source quote
    primary["records"][0]["exact_quote"] = "Test fixture, not an actual source quotation"
    validator.validate(primary)


def test_knowledge_rest_filter_and_invalid_topic():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from cvnss_hub.api import router

    app = FastAPI()
    app.include_router(router)
    with TestClient(app) as client:
        response = client.get("/api/cvnss4/knowledge", params={"topic": "limitations"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "draft"
        assert {r["topic"] for r in data["records"]} == {"limitations"}
        assert next(r for r in data["records"] if r["id"] == "reverse-ed")["evidence_type"] == "implementation"
        assert client.get("/api/cvnss4/knowledge?topic=unknown").status_code == 422
        assert len(client.get("/api/cvnss4/knowledge").json()["topics"]) == 10


@pytest.mark.skipif(not shutil.which("node"), reason="Node.js required")
def test_knowledge_example_matches_oracle():
    example = next(r for r in execute("knowledge", text="limitations")["records"]
                   if r["id"] == "reverse-ed")["examples"][0]
    result = execute("inspect", text=example["input"], source=example["source"])
    assert result["candidates"] == example["candidates"]
    assert result["selected"] == example["selected"]


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

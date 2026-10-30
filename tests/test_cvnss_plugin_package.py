"""Exercise portable CVNSS4.0 ChatGPT plugin packaging without deploying a server."""
import json
from zipfile import ZipFile

import pytest

from scripts.build_cvnss_chatgpt_plugin import ROOT, make_archive, validate_endpoint


@pytest.mark.parametrize("bad", [
    "http://example.com/mcp",
    "https://example.com/",
    "https://localhost/mcp",
    "https://127.0.0.1/mcp",
    "https://example.com/mcp?api_key=secret",
    "https://user:pass@example.com/mcp",
    "https://example.com/mcp#frag",
])
def test_endpoint_rejects_unsafe_values(bad):
    with pytest.raises(ValueError):
        validate_endpoint(bad)


def test_skill_only_package(tmp_path):
    out = make_archive(out=tmp_path / "skill.zip")
    with ZipFile(out) as archive:
        names = archive.namelist()
        assert "cvnss4-knowledge-hub/plugin.json" in names
        assert "cvnss4-knowledge-hub/skills/cvnss4-tutor/SKILL.md" in names
        assert "cvnss4-knowledge-hub/mcp.json" not in names
        manifest = json.loads(archive.read("cvnss4-knowledge-hub/plugin.json"))
        assert manifest["name"] == "cvnss4-knowledge-hub"
        assert manifest["version"] == "0.2.0"
        # Offline references must be the same canonical assets served by the API.
        for source, bundled in (
            ("knowledge.json", "knowledge.json"),
            ("knowledge.schema.json", "knowledge.schema.json"),
            ("STANDARDIZATION.md", "standardization.md"),
        ):
            name = "cvnss4-knowledge-hub/skills/cvnss4-tutor/references/" + bundled
            assert archive.read(name) == (ROOT / "cvnss_hub" / source).read_bytes()


def test_remote_package_and_reproducibility(tmp_path):
    url = "https://cvnss.example.org/mcp"  # syntactic unit-test fixture, NOT a deployed host
    first = make_archive(mcp_url=url, out=tmp_path / "first.zip")
    second = make_archive(mcp_url=url, out=tmp_path / "second.zip")
    assert first.read_bytes() == second.read_bytes()
    with ZipFile(first) as archive:
        mcp = json.loads(archive.read("cvnss4-knowledge-hub/mcp.json"))
        assert mcp["mcpServers"]["cvnss4"] == {
            "type": "streamable-http", "url": url,
        }

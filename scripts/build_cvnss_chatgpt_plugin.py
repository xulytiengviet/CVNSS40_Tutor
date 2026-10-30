#!/usr/bin/env python3
"""Build a portable ChatGPT/Codex CVNSS4.0 plugin archive from GitHub sources.

Without --mcp-url: skills-only package; does NOT provide live conversion tools.
With --mcp-url: include a remote MCP connector declaration (URL must be deployed,
tested and protected independently). No keys, tokens, or credentials are bundled.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "integrations" / "chatgpt-plugin"
OUTPUT_DIR = ROOT / "dist"
MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"


def validate_endpoint(url: str) -> str:
    """Validate a stable HTTPS MCP endpoint; not a test of actual server reachability."""
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.port == 0
        or parsed.query
        or parsed.fragment
        or parsed.path.rstrip("/") != "/mcp"
        or parsed.hostname.lower() in {"localhost", "127.0.0.1", "::1"}
        or parsed.hostname.lower().endswith((".local", ".internal"))
    ):
        raise ValueError(
            "--mcp-url must be a real HTTPS endpoint with path /mcp; "
            "no credentials, localhost, query or fragments"
        )
    return url


def make_archive(*, mcp_url: str | None = None, out: Path | None = None) -> Path:
    manifest = json.loads((SOURCE / "plugin.json").read_text(encoding="utf-8"))
    assert manifest["$schema"] == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
    name = manifest["name"]
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError("Invalid plugin name")
    version = manifest["version"]
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Expected strict SemVer")
    if out is None:
        out = OUTPUT_DIR / f"{name}-{version}.zip"
    out.parent.mkdir(parents=True, exist_ok=True)

    required = (
        SOURCE / "plugin.json",
        SOURCE / "skills" / "cvnss4-tutor" / "SKILL.md",
    )
    package: dict[str, bytes] = {}
    prefix = f"{name}/"
    for file in required:
        if not file.is_file():
            raise FileNotFoundError(file)
        content = file.read_bytes()
        if file.suffix == ".md":
            head = content.decode("utf-8").split("---", 2)
            if len(head) < 3:
                raise ValueError("SKILL.md must contain YAML frontmatter")
        package[prefix + file.relative_to(SOURCE).as_posix()] = content

    # Bundle the canonical registry and proposal without maintaining duplicate data.
    for source_name, target_name in (
        ("knowledge.json", "knowledge.json"),
        ("knowledge.schema.json", "knowledge.schema.json"),
        ("STANDARDIZATION.md", "standardization.md"),
    ):
        package[prefix + "skills/cvnss4-tutor/references/" + target_name] = (
            ROOT / "cvnss_hub" / source_name
        ).read_bytes()

    if mcp_url:
        remote_url = validate_endpoint(mcp_url)
        mcp = {
            "$schema": MCP_SCHEMA,
            "mcpServers": {
                "cvnss4": {"type": "streamable-http", "url": remote_url}
            },
        }
        package[prefix + "mcp.json"] = (json.dumps(mcp, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

    # Deterministic ZIP: same source and URL -> identical bytes across machines.
    with ZipFile(out, "w", compression=ZIP_DEFLATED) as archive:
        for item, data in sorted(package.items()):
            info = ZipInfo(item, (2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)

    with ZipFile(out, "r") as archive:
        if set(archive.namelist()) != set(package):
            raise RuntimeError("Plugin ZIP contents differ from package manifest")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcp-url", help="An already deployed, tested HTTPS MCP URL ending in /mcp")
    parser.add_argument("--out", type=Path, help="ZIP output filename")
    args = parser.parse_args()
    archive = make_archive(mcp_url=args.mcp_url, out=args.out)
    if args.mcp_url:
        print(f"Packaged skills + MCP connection definition: {archive}")
        print("IMPORTANT: MCP endpoint availability, authentication and ChatGPT installation are NOT verified by packaging.")
    else:
        print(f"Packaged skills only (no live tools, no GitHub sync): {archive}")
        print("For live conversion, deploy MCP and rerun with --mcp-url HTTPS_ENDPOINT")


if __name__ == "__main__":
    main()

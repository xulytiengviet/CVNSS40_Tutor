"""Safe, bounded bridge to the audited JS converter and curated source registry."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BRIDGE = ROOT / "oracle" / "bridge.cjs"
SOURCES = ROOT / "sources.json"
KNOWLEDGE = ROOT / "knowledge.json"
MAX_TEXT = 100_000
OPERATIONS = {"convert", "inspect", "candidates", "audit", "self_test", "sources", "knowledge"}


def execute(operation: str, *, text: str = "", mode: str = "cqn", source: str = "cvss") -> dict:
    """Run the deterministic oracle; neither input nor output is sent to an LLM."""
    if operation not in OPERATIONS:
        raise ValueError("Unsupported operation")
    if not isinstance(text, str) or len(text) > MAX_TEXT:
        raise ValueError("text must be a string with at most 100000 characters")
    if mode not in ("cqn", "cvn", "cvss") or source not in ("cvn", "cvss"):
        raise ValueError("Invalid CVNSS4.0 mode or source")
    if operation in {"inspect", "candidates"} and (not text or len(text) > 200):
        raise ValueError("A single word (1-200 characters) is required")
    if operation == "sources":
        # This is a seed registry of source links, NOT a scraped/ingested corpus.
        return json.loads(SOURCES.read_text(encoding="utf-8"))
    if operation == "knowledge":
        # A curated draft, not an ingested corpus or an official specification.
        result = json.loads(KNOWLEDGE.read_text(encoding="utf-8"))
        topic = text or "all"
        if topic != "all":
            if topic not in {item["id"] for item in result["topics"]}:
                raise ValueError("Unknown knowledge topic")
            result["topics"] = [item for item in result["topics"] if item["id"] == topic]
            result["records"] = [item for item in result["records"] if item["topic"] == topic]
        return result
    try:
        proc = subprocess.run(
            ["node", str(BRIDGE)],
            input=json.dumps(
                {"operation": operation, "text": text, "mode": mode, "source": source},
                ensure_ascii=False,
            ),
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=15,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("Node.js is required for the CVNSS4.0 Oracle") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("CVNSS4.0 converter timed out") from exc
    if proc.returncode != 0:
        # Only a bounded diagnostic; do not return arbitrary process logs to callers.
        raise RuntimeError("CVNSS4.0 converter failed: " + proc.stderr[:300])
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Invalid CVNSS4.0 converter response") from exc
    if not isinstance(result, dict):
        raise RuntimeError("Invalid converter result")
    return result

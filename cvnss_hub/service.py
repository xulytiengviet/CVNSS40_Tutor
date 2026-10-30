"""Safe bridge to the verified JavaScript converter; no LLM required for conversions."""
from __future__ import annotations
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BRIDGE = ROOT / "oracle" / "bridge.cjs"
MAX_TEXT = 100_000
OPERATIONS = {"convert", "inspect", "candidates", "audit", "self_test"}


def execute(operation: str, *, text: str = "", mode: str = "cqn", source: str = "cvss") -> dict:
    if operation not in OPERATIONS:
        raise ValueError("Unsupported operation")
    if not isinstance(text, str) or len(text) > MAX_TEXT:
        raise ValueError("text must be a string with at most 100000 characters")
    if mode not in ("cqn", "cvn", "cvss") or source not in ("cvn", "cvss"):
        raise ValueError("Invalid CVNSS4.0 mode")
    try:
        proc = subprocess.run(
            ["node", str(BRIDGE)],
            input=json.dumps({"operation": operation, "text": text, "mode": mode, "source": source}, ensure_ascii=False),
            text=True, encoding="utf-8", capture_output=True, timeout=15, check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("Node.js 22+ is required for the CVNSS4.0 Oracle") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("CVNSS4.0 converter timed out") from exc
    if proc.returncode != 0:
        raise RuntimeError("CVNSS4.0 converter failed: " + proc.stderr[:300])
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Invalid CVNSS4.0 converter response") from exc
    if not isinstance(result, dict):
        raise RuntimeError("Invalid converter result")
    return result

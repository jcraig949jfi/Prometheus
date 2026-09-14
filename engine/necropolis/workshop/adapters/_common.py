"""Shared helpers for necropolis adapters (LAYER: NECROPOLIS ADAPTER).

ORIGINAL SCIENTIFIC LOGIC: none (necropolis-built plumbing only).
NECROPOLIS VALIDATION: engine/necropolis/workshop/tests/run_controls.py::adapters.*
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def repo_root() -> Path:
    return REPO


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_head(cwd: Path | None = None) -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(cwd or REPO), capture_output=True,
                              text=True, timeout=30).stdout.strip()
    except Exception:  # noqa: BLE001
        return "UNKNOWN"


def sha256_file(path: Path, normalise_newlines: bool = True) -> str:
    data = Path(path).read_bytes()
    if normalise_newlines:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fingerprint_inputs(paths) -> dict:
    """A record of what was read: {relpath: {sha256, bytes}} so a result can name its inputs."""
    out = {}
    for p in paths:
        p = Path(p)
        if not p.exists():
            out[str(p)] = {"sha256": None, "bytes": None, "missing": True}
            continue
        try:
            rel = str(p.resolve().relative_to(REPO)).replace(os.sep, "/")
        except ValueError:
            rel = str(p)
        out[rel] = {"sha256": sha256_file(p), "bytes": p.stat().st_size}
    return out


def result_envelope(tool: str, inputs, payload: dict, argv=None) -> dict:
    """Standard result wrapper: every adapter output names its git head, inputs and time."""
    return {
        "schema": "necropolis.workshop.adapter_result/1",
        "tool": tool,
        "git_head": git_head(),
        "python": sys.version.split()[0],
        "argv": list(argv) if argv is not None else None,
        "started": now_iso(),
        "inputs": fingerprint_inputs(inputs),
        "result": payload,
    }


def write_json(path: Path, obj) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, indent=1, sort_keys=False, default=str)
        fh.write("\n")

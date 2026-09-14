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


class InadmissibleInstrument(RuntimeError):
    """Raised when a tool that is not FORENSICALLY ADMISSIBLE is asked to stamp evidence."""


def tool_record(tool_id: str) -> dict:
    """The registry row for tool_id (TOOLS.jsonl is the single source of admissibility)."""
    reg = HERE.parent / "TOOLS.jsonl"
    if not reg.exists():
        raise InadmissibleInstrument(f"{tool_id}: no registry at {reg}; nothing is admissible without one")
    for line in reg.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if row.get("tool_id") == tool_id:
                return row
    raise InadmissibleInstrument(f"{tool_id}: not in TOOLS.jsonl; an unregistered instrument is not admissible")


def instrument_stamp(tool_id: str) -> dict:
    """What every tool output must carry (court charter, TOOL ADMISSIBILITY): identity,
    version, status, the admissibility ladder, the caveat, and the control state with the
    fingerprint of the controls artifact it was read from.  Pure read; never raises on a
    non-admissible tool (a diagnostic may still be stamped as NOT_ADMISSIBLE)."""
    row = tool_record(tool_id)
    adm = row.get("admissibility") or {}
    art = adm.get("control_state", {}).get("artifact")
    art_path = REPO / art if art else None
    if row.get("layer") == "ORIGINAL_SCIENTIFIC_LOGIC":
        orig = row.get("current_path")
    else:
        orig = declared_original_logic(row.get("current_path")) or row.get("necropolis_adapter") or "UNDECLARED"
    return {
        "tool_id": tool_id,
        "name": row.get("name"),
        "necropolis_status": row.get("necropolis_status"),
        "source_commit": row.get("source_commit"),
        "current_path": row.get("current_path"),
        "layer": row.get("layer"),
        "original_scientific_logic": orig if orig else row.get("necropolis_adapter") or "none (necropolis-built; see module docstring)",
        "admissibility": adm,
        "caveat": row.get("caveat"),
        "forbidden_inference": row.get("forbidden_inference"),
        "controls_artifact_sha256": sha256_file(art_path) if art_path and art_path.exists() else None,
        "registry_sha256": sha256_file(HERE.parent / "TOOLS.jsonl"),
    }


def declared_original_logic(rel_path: str | None) -> str | None:
    """The 'ORIGINAL SCIENTIFIC LOGIC:' declaration in an adapter's module docstring (the
    paragraph up to the next blank line or the NECROPOLIS VALIDATION line), so a stamped
    output says which original code the adapter invoked.  Read, never imported."""
    if not rel_path:
        return None
    p = REPO / rel_path
    if not p.exists():
        return None
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    for i, ln in enumerate(lines[:60]):
        if ln.startswith("ORIGINAL SCIENTIFIC LOGIC:"):
            out = [ln[len("ORIGINAL SCIENTIFIC LOGIC:"):].strip()]
            for nxt in lines[i + 1:i + 8]:
                if not nxt.strip() or nxt.startswith("NECROPOLIS VALIDATION") or nxt.startswith('"""'):
                    break
                out.append(nxt.strip())
            return " ".join(out)
    return None


def evidence_envelope(tool_id: str, inputs, payload: dict, argv=None, purpose: str = "EVIDENCE") -> dict:
    """Result wrapper that REFUSES to stamp evidence with a non-admissible instrument.

    purpose="EVIDENCE"   -> raises InadmissibleInstrument unless admissibility.admissible is true;
                            READY_WITH_CAVEAT outputs carry the caveat verbatim.
    purpose="DIAGNOSTIC" -> always stamps, with admissible_as NOT_ADMISSIBLE visible in the
                            envelope, so a diagnostic cannot later be mistaken for evidence.
    """
    if purpose not in ("EVIDENCE", "DIAGNOSTIC"):
        raise ValueError("purpose must be EVIDENCE or DIAGNOSTIC")
    stamp = instrument_stamp(tool_id)
    adm = stamp["admissibility"]
    if purpose == "EVIDENCE" and not adm.get("admissible"):
        raise InadmissibleInstrument(
            f"{tool_id} ({stamp['necropolis_status']}) is not forensically admissible: blocked_by={adm.get('blocked_by')}; "
            "stamp it as DIAGNOSTIC or use an admissible instrument")
    return {
        "schema": "necropolis.workshop.evidence/1",
        "purpose": purpose,
        "instrument": stamp,
        "git_head": git_head(),
        "python": sys.version.split()[0],
        "argv": list(argv) if argv is not None else None,
        "started": now_iso(),
        "inputs": fingerprint_inputs(inputs),
        "result": payload,
    }


def result_envelope(tool: str, inputs, payload: dict, argv=None) -> dict:
    """Legacy result wrapper (unstamped).  Carries no admissibility record and is therefore a
    DIAGNOSTIC output by construction; use evidence_envelope(tool_id, ...) for anything that
    will be cited."""
    return {
        "schema": "necropolis.workshop.adapter_result/1",
        "purpose": "DIAGNOSTIC",
        "unstamped": "no tool_id / admissibility record; not citable as evidence (use evidence_envelope)",
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

"""Mint Packet schema, queue states, and queue I/O.

Charter: roles/Hephaestus/CHARTER_AMENDMENT_2026-09-01_forge_queue_master_smith.md, §5 and §7.
A packet is a JSON file at hephaestus/mint_queue/<MINT_ID>/packet.json plus an append-only
events.jsonl beside it. Every field in §5 is present in every packet, even when empty, so that
a reader (human or Master Smith) can see what is MISSING rather than guess.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[2]
HEPH = ROOT / "hephaestus"
QUEUE_DIR = HEPH / "mint_queue"

FIELDS: list[str] = [
    "MINT_ID", "STATUS", "PRIORITY", "SOURCE_WORLD", "SOURCE_AGENT", "FAILURE_FAMILY",
    "WHAT_FAILED", "WHAT_SHOULD_HAVE_HAPPENED", "MINIMAL_REPRODUCER",
    "POSITIVE_EXAMPLES", "NEGATIVE_EXAMPLES", "BOUNDARY_EXAMPLES",
    "CURRENT_PRIMITIVES", "PRIMITIVE_SET_HASH",
    "WHY_COMPOSITION_APPEARS_INSUFFICIENT", "CLOSURE_EVIDENCE",
    # Addendum 1 (2026-09-01): the triage question "if perfect semantic state were injected, what
    # computation would still be missing?" is answered here, BEFORE anything goes to a smith.
    "SEMANTIC_KERNEL_SPEC", "REPRESENTATION_ADAPTER_SPEC",
    "SEARCH_ALREADY_ATTEMPTED",
    "CHEAP_MODEL_ATTEMPTS", "CHEAP_MODEL_FAILURES", "BEST_FAILED_CANDIDATE",
    "KNOCKOUT_RESULTS", "COUNTERFEIT_TESTS", "KNOWN_SHORTCUTS", "FORBIDDEN_SHORTCUTS",
    "REPRESENTATION_PERTURBATIONS", "DESIRED_TYPED_INTERFACE", "RESOURCE_CONSTRAINTS",
    "INDEPENDENT_EVALUATOR", "SUCCESS_CRITERION", "KILL_CRITERION", "PROVENANCE",
]

STATES: list[str] = [
    "OBSERVED", "TRIAGE", "COMPOSITION-SUSPECTED", "EXPRESSIVITY-SUSPECTED",
    "APPRENTICE-TESTING", "APPRENTICE-EXHAUSTED", "READY-FOR-DEEP-MINT", "DEEP-MINTING",
    "CANDIDATE-PRODUCED", "INDEPENDENT-EVAL", "ADMITTED", "SCRAPPED", "DORMANT",
]

UNRESOLVED = {
    "OBSERVED", "TRIAGE", "COMPOSITION-SUSPECTED", "EXPRESSIVITY-SUSPECTED",
    "APPRENTICE-TESTING", "APPRENTICE-EXHAUSTED", "READY-FOR-DEEP-MINT", "DEEP-MINTING",
}

# Fields that must be non-empty before a packet may enter READY-FOR-DEEP-MINT (§5, §7).
READY_REQUIRED = [
    "SOURCE_WORLD", "SOURCE_AGENT", "FAILURE_FAMILY", "WHAT_FAILED", "WHAT_SHOULD_HAVE_HAPPENED",
    "MINIMAL_REPRODUCER", "POSITIVE_EXAMPLES", "NEGATIVE_EXAMPLES", "BOUNDARY_EXAMPLES",
    "CURRENT_PRIMITIVES", "PRIMITIVE_SET_HASH", "WHY_COMPOSITION_APPEARS_INSUFFICIENT",
    "CLOSURE_EVIDENCE", "SEMANTIC_KERNEL_SPEC", "REPRESENTATION_ADAPTER_SPEC",
    "CHEAP_MODEL_ATTEMPTS", "CHEAP_MODEL_FAILURES", "COUNTERFEIT_TESTS",
    "KNOWN_SHORTCUTS", "FORBIDDEN_SHORTCUTS", "REPRESENTATION_PERTURBATIONS",
    "DESIRED_TYPED_INTERFACE", "INDEPENDENT_EVALUATOR", "SUCCESS_CRITERION", "KILL_CRITERION",
    "PROVENANCE",
]


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def new_packet(mint_id: str, **kw: Any) -> dict[str, Any]:
    p: dict[str, Any] = {f: None for f in FIELDS}
    for f in ("POSITIVE_EXAMPLES", "NEGATIVE_EXAMPLES", "BOUNDARY_EXAMPLES", "CURRENT_PRIMITIVES",
              "CLOSURE_EVIDENCE", "SEARCH_ALREADY_ATTEMPTED", "CHEAP_MODEL_ATTEMPTS",
              "CHEAP_MODEL_FAILURES", "KNOCKOUT_RESULTS", "COUNTERFEIT_TESTS", "KNOWN_SHORTCUTS",
              "FORBIDDEN_SHORTCUTS", "REPRESENTATION_PERTURBATIONS", "PROVENANCE"):
        p[f] = []
    p["MINT_ID"] = mint_id
    p["STATUS"] = "OBSERVED"
    p["PRIORITY"] = {"score": None, "dimensions": {}, "rationale": ""}
    p["_meta"] = {"created": now_iso(), "updated": now_iso(), "schema": "mint_packet_v1"}
    p.update(kw)
    return p


def packet_dir(mint_id: str) -> Path:
    return QUEUE_DIR / mint_id


def load(mint_id: str) -> dict[str, Any]:
    return json.loads((packet_dir(mint_id) / "packet.json").read_text(encoding="utf-8"))


def save(p: dict[str, Any]) -> Path:
    d = packet_dir(p["MINT_ID"])
    d.mkdir(parents=True, exist_ok=True)
    p["_meta"]["updated"] = now_iso()
    path = d / "packet.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(p, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    tmp.replace(path)
    (d / "packet.md").write_text(render_md(p), encoding="utf-8")
    return path


def log_event(mint_id: str, event: str, **data: Any) -> None:
    d = packet_dir(mint_id)
    d.mkdir(parents=True, exist_ok=True)
    rec = {"ts": now_iso(), "event": event, **data}
    with (d / "events.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")


def set_status(p: dict[str, Any], new: str, reason: str) -> None:
    assert new in STATES, new
    old = p["STATUS"]
    if old == new:
        return
    p["STATUS"] = new
    log_event(p["MINT_ID"], "status", frm=old, to=new, reason=reason)


def iter_packets() -> Iterator[dict[str, Any]]:
    if not QUEUE_DIR.exists():
        return
    for d in sorted(QUEUE_DIR.iterdir()):
        f = d / "packet.json"
        if f.exists():
            yield json.loads(f.read_text(encoding="utf-8"))


def missing_for_ready(p: dict[str, Any]) -> list[str]:
    out = []
    for f in READY_REQUIRED:
        v = p.get(f)
        if v is None or v == "" or v == [] or v == {}:
            out.append(f)
    return out


def _fmt(v: Any, depth: int = 0) -> str:
    if v is None:
        return "_(missing)_"
    if isinstance(v, str):
        return v
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, list):
        if not v:
            return "_(none yet)_"
        return "\n".join(f"- {_fmt(x, depth + 1)}" if not isinstance(x, dict) else
                         "- " + "; ".join(f"**{k}**: {_fmt(val, depth + 1)}" for k, val in x.items())
                         for x in v)
    if isinstance(v, dict):
        if not v:
            return "_(empty)_"
        return "\n".join(f"- **{k}**: {_fmt(val, depth + 1)}" for k, val in v.items())
    return str(v)


def render_md(p: dict[str, Any]) -> str:
    lines = [f"# {p['MINT_ID']} — {p.get('FAILURE_FAMILY') or ''}",
             f"**STATUS:** `{p['STATUS']}` · **updated** {p['_meta']['updated']} · "
             f"missing-for-READY: {', '.join(missing_for_ready(p)) or 'none'}", ""]
    for f in FIELDS:
        if f in ("MINT_ID", "STATUS"):
            continue
        lines.append(f"## {f}")
        lines.append(_fmt(p.get(f)))
        lines.append("")
    return "\n".join(lines)

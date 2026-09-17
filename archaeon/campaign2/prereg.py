"""Preregistration contract (directive section 6): a PREREG.json every experiment writes
BEFORE running, validated for the required fields, sealed by digest, rendered as RECORD.md
section A (and PREREG.md), and published on the engine as a hypothesis-kind artifact so the
seal precedes any measurement.

The `decl` block is what archaeon.wse.states reads (positive_control, interventions,
artifacts, stream, readout_control, target, n_min, primary, battery); the prose fields are
for the human/agent reader. Nothing in the sealed body may change after the seal; the
harness re-validates the digest at finalize and records PREREG_CHANGED_AFTER_SEAL if it did.

Campaigns extend the contract by passing `fields` (campaign 3 adds why_this_slot,
kill_condition, replacement_condition, ancestry); the sealed body is exactly `fields`.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from archaeon.wse import digest as D

FIELDS = [
    "experiment", "parents", "question", "parent_evidence", "assay_capability_requirement", "positive_control",
    "reachability_estimate", "arms", "crn_policy", "budget", "primary_observable", "claim_ceiling",
    "falsification_condition", "typed_failure_conditions", "expected_machine_telemetry", "machine_changes_exercised", "decl",
]
TITLES = {
    "question": "QUESTION", "parent_evidence": "PARENT EVIDENCE", "assay_capability_requirement": "ASSAY CAPABILITY REQUIREMENT",
    "positive_control": "POSITIVE CONTROL", "reachability_estimate": "REACHABILITY ESTIMATE", "arms": "ARMS",
    "crn_policy": "COMMON-RANDOM-NUMBERS POLICY", "budget": "BUDGET", "primary_observable": "PRIMARY OBSERVABLE",
    "claim_ceiling": "CLAIM CEILING", "falsification_condition": "FALSIFICATION CONDITION",
    "typed_failure_conditions": "TYPED FAILURE CONDITIONS", "expected_machine_telemetry": "EXPECTED MACHINE TELEMETRY",
    "machine_changes_exercised": "MACHINE CHANGES EXERCISED",
    "why_this_slot": "WHY THIS SLOT IS STILL WORTH SPENDING", "kill_condition": "KILL CONDITION",
    "replacement_condition": "REPLACEMENT CONDITION", "ancestry": "ANCESTRY (original | replacement)",
}
PROSE_ORDER = ["question", "parent_evidence", "why_this_slot", "assay_capability_requirement", "positive_control", "reachability_estimate", "arms",
               "crn_policy", "budget", "primary_observable", "claim_ceiling", "falsification_condition", "kill_condition", "typed_failure_conditions",
               "expected_machine_telemetry", "machine_changes_exercised", "replacement_condition", "ancestry"]


def validate(p: dict, fields: Optional[Sequence[str]] = None) -> List[str]:
    fs = list(fields or FIELDS)
    missing = [f for f in fs if f not in p or p[f] in (None, "", [], {})]
    if "decl" in p and not isinstance(p["decl"], dict):
        missing.append("decl:not-a-dict")
    return missing


def seal(p: dict, fields: Optional[Sequence[str]] = None) -> dict:
    fs = list(fields or FIELDS)
    miss = validate(p, fs)
    if miss:
        raise ValueError("preregistration incomplete: " + ", ".join(miss))
    body = {k: p[k] for k in fs}
    return {"prereg_digest": D.of_obj(body), "bytes": D.canonical_bytes(body), "fields": fs}


def save(p: dict, directory: Path, fields: Optional[Sequence[str]] = None) -> Path:
    s = seal(p, fields)
    out = dict(p); out["prereg_digest"] = s["prereg_digest"]; out["sealed_fields"] = s["fields"]
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "PREREG.json"
    path.write_text(json.dumps(out, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    return path


def unchanged(p: dict, digest: str, fields: Optional[Sequence[str]] = None) -> bool:
    fs = fields or p.get("sealed_fields") or FIELDS
    return D.same(seal(p, fs)["prereg_digest"], digest)


def _fmt(v) -> str:
    if isinstance(v, str):
        return v
    if isinstance(v, list):
        return "\n".join("    - " + (_fmt(x) if not isinstance(x, (dict, list)) else json.dumps(x, sort_keys=True)) for x in v)
    return json.dumps(v, sort_keys=True, indent=None)


def render(p: dict) -> str:
    lines = ["## A. STARTUP (preregistration; sealed %s)" % p.get("prereg_digest", "(unsealed)"), "",
             "- experiment ID: %s" % p["experiment"], "- parents: %s" % ", ".join(p.get("parents", []))]
    for k in PROSE_ORDER:
        if k not in p:
            continue
        v = p[k]
        if isinstance(v, (list, dict)) and not isinstance(v, str):
            lines.append("- %s:" % TITLES[k])
            lines.append(_fmt(v) if isinstance(v, list) else "    " + json.dumps(v, sort_keys=True))
        else:
            lines.append("- %s: %s" % (TITLES[k], v))
    lines.append("- decl (machine-read by archaeon.wse.states): " + json.dumps(p.get("decl", {}), sort_keys=True))
    return "\n".join(lines) + "\n"

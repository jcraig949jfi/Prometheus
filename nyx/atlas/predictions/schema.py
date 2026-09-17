"""NYX_PREDICTION_PACKET / schema 1 (Mechanism Archaeology Pipeline, Amendment 3, R33; Nyx, 2026-09-16).

A packet is the frozen, falsifiable half of a cut: the boundary bound to the bytes read, the mechanism claim, the
formal interventions with an observable and a magnitude band each, the two controls, and the two losing outcomes.
It is serialized canonically (UTF-8, LF, sorted keys, one terminal LF) and hashed; the hash is the packet's freeze.
A correction is a NEW packet whose `supersedes` names the old id; the old file is never edited.

    python -m nyx.atlas.predictions.schema validate <packet.json>
    python -m nyx.atlas.predictions.schema freeze   <packet.json>    # writes <packet>.FREEZE with the sha256
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import List

SCHEMA = "nyx.prediction_packet/1"
DIRECTIONS = ("INCREASE", "DECREASE", "UNCHANGED", "NON_MONOTONIC", "REGIME_DEPENDENT")
LEVELS = ("SOURCE", "BUILD_BINARY", "RUNTIME_STATE", "TESTBENCH", "ENVIRONMENT")
PROVENANCE_GRADES = ("ORIGINAL_ARTIFACT", "CONTEMPORARY_COPY", "AUTHENTIC_TRANSCRIPTION", "LATER_TRANSCRIPTION",
                     "RECONSTRUCTION", "DERIVED_RECOVERY_ARTIFACT", "AUTHOR_STATED", "UNKNOWN")
TOP = ("schema_version", "prediction_packet_id", "created_at", "chopper_identity", "chopper_version", "cut_id",
       "fossil_raw_id", "payload_manifest_id", "provenance_grade_read", "boundary", "mechanism_claim",
       "interventions", "controls", "cut_kill", "indeterminate", "supersedes", "return_protocol")
BOUNDARY = ("file_path", "file_payload_hash", "line_start", "line_end")
CLAIM = ("functional_claim", "claimed_inputs", "claimed_outputs", "claimed_internal_dependency", "known_uncertainty")
INTERVENTION = ("intervention_id", "intervention_level", "intervention_operation", "measured_observable",
                "expected_direction", "expected_magnitude_band", "units", "band_basis", "test_world_scope",
                "pressure_scope", "prediction_rationale")
CONTROL = ("control_id", "construction", "expected_result", "failure_interpretation")
# Harmonia #381 (2026-09-18) ASK H4: the observable's kind of novelty, one value per intervention, never per packet;
# optional so frozen packets 001/002 stay byte-identical; Nyx policy from 2026-09-18: every later packet carries it.
NOVELTY_KINDS = ("structure", "behavior", "observer", "consequential")


def canonical_bytes(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, ensure_ascii=True, separators=(",", ":")) + "\n").encode("utf-8")


def packet_hash(obj) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def validate(p: dict) -> List[str]:
    e: List[str] = []
    for k in TOP:
        if k not in p:
            e.append(f"missing top-level field {k}")
    if p.get("schema_version") != SCHEMA:
        e.append("schema_version")
    if p.get("provenance_grade_read") not in PROVENANCE_GRADES:
        e.append("provenance_grade_read not in vocabulary")
    for i, b in enumerate(p.get("boundary", [])):
        for k in BOUNDARY:
            if k not in b:
                e.append(f"boundary[{i}] missing {k}")
        h = b.get("file_payload_hash", "")
        if not (isinstance(h, str) and len(h) == 64):
            e.append(f"boundary[{i}]: a path and line range without a 64-hex file payload hash is INVALID")
    if not p.get("boundary"):
        e.append("boundary empty")
    for k in CLAIM:
        if k not in (p.get("mechanism_claim") or {}):
            e.append(f"mechanism_claim missing {k}")
    for i, iv in enumerate(p.get("interventions", [])):
        for k in INTERVENTION:
            if k not in iv:
                e.append(f"interventions[{i}] missing {k}")
        if iv.get("intervention_level") not in LEVELS:
            e.append(f"interventions[{i}] level not in {LEVELS}")
        if iv.get("expected_direction") not in DIRECTIONS:
            e.append(f"interventions[{i}] direction not in {DIRECTIONS}")
        if "novelty_kind" in iv and iv.get("novelty_kind") not in NOVELTY_KINDS:
            e.append(f"interventions[{i}] novelty_kind not in {NOVELTY_KINDS}")
        band = iv.get("expected_magnitude_band")
        if not (isinstance(band, list) and len(band) == 2 and all(isinstance(x, (int, float)) for x in band) and band[0] <= band[1]):
            e.append(f"interventions[{i}] expected_magnitude_band must be [low, high] numbers")
    if not p.get("interventions"):
        e.append("no interventions")
    c = p.get("controls") or {}
    for name in ("cheat", "positive"):
        ctl = c.get(name)
        if ctl == "POSITIVE_CONTROL_UNAVAILABLE" and name == "positive":
            if not c.get("positive_unavailable_reason"):
                e.append("POSITIVE_CONTROL_UNAVAILABLE needs positive_unavailable_reason")
            continue
        if not isinstance(ctl, dict):
            e.append(f"controls.{name} missing")
            continue
        for k in CONTROL:
            if k not in ctl:
                e.append(f"controls.{name} missing {k}")
    for k in ("cut_kill", "indeterminate"):
        v = p.get(k)
        if not (isinstance(v, dict) and v.get("observation") and v.get("consequence")):
            e.append(f"{k} needs observation and consequence")
    rp = p.get("return_protocol") or {}
    for k in ("to_seat", "ack_ticks", "disposition_ticks", "accountable_seat"):
        if k not in rp:
            e.append(f"return_protocol missing {k}")
    return e


def main(argv):
    cmd, path = argv[0], Path(argv[1])
    p = json.loads(path.read_text(encoding="utf-8"))
    errs = validate(p)
    if errs:
        print("\n".join("INVALID: " + x for x in errs))
        return 1
    h = packet_hash(p)
    print(f"valid {p['prediction_packet_id']} sha256 {h}")
    if cmd == "freeze":
        fz = path.with_suffix(".FREEZE")
        if fz.exists():
            old = fz.read_text(encoding="utf-8").split()[0]
            if old != h:
                print(f"REFUSED: {fz.name} holds {old}; the packet bytes changed. Write a new packet with supersedes = {p['prediction_packet_id']}")
                return 2
            print("already frozen at this hash")
            return 0
        fz.write_text(f"{h}  {path.name}  frozen_by_canonical_bytes  schema {SCHEMA}\n", encoding="utf-8", newline="\n")
        print("frozen ->", fz)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

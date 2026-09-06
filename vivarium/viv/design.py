"""The EXPERIMENTAL DESIGN, sealed separately from the execution.

The operator's arm ruling, 2026-09-06:

    execution parameters      -> sealed execution spec (spec_hash)
    family + arm assignment   -> separately sealed experimental design
    execution<->design link   -> audit envelope, preserved in PEW
    acceptance: the SAME execution hash under labels A and B;
                reassignment after commitment refused;
                PEW preserves the binding.

Two seals, not one. `spec_hash` answers "what was executed"; `design_hash`
answers "what comparison was it part of". Keeping them separate is what lets
arm A and arm B carry a byte-identical execution -- which is the ruling's own
acceptance test, and the only way a difference between arms can be attributed
to selection rather than to the arms having quietly run different science.

NOTHING HERE IS HASHED INTO spec_hash, and nothing here reaches the executor.
The design is read from the queue row by the NOTEBOOK (viv/loop.py) after
execution and written into the PEW producer block. `viv/runner.py` never sees
it: `tests/test_blinding.py` asserts that an ExecutionRequest cannot carry it.

WHY THE SEAL IS REAL. The design fields live in queue columns that the BEFORE
UPDATE trigger freezes at admission (migration 002): family_id, arm_id,
replication_of, candidate_set_id, request_key are immutable for the row's whole
life, and a terminal row is frozen entire. So a hash computed over them after
execution is a hash over values that could not have moved -- "reassignment
after commitment refused" is enforced by the database, and design_hash records
what the assignment WAS.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Optional

#: The sealed design. Closed and ordered; adding a field changes design_hash
#: for every future row, which is a deliberate act.
DESIGN_KEYS = ("family_id", "arm_id", "candidate_set_id", "replication_of",
               "request_key")

#: E1. What the PRODUCER declared about which policy and template produced the
#: request. Projected, not copied wholesale: source_evidence carries a whole
#: eligibility census, and a fossil should hold the identity, not the corpus.
POLICY_KEYS = ("policy_version", "template_id", "template_version")
POLICY_BLOCK_KEYS = ("name", "version", "seed", "attempt")


def _canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def design_of(row) -> dict:
    """The design as declared at admission. Values only, no interpretation."""
    out = {}
    for k in DESIGN_KEYS:
        v = row[k] if k in row.keys() else None
        out[k] = str(v) if k == "replication_of" and v is not None else v
    return out


def design_hash(design: dict) -> str:
    """The design's own seal, in the same canonicalization SFE uses for specs.

    A design with every field null hashes to a stable value too -- an
    experiment that declares no family and no arm has a design, and it is
    'no comparison'. That is a statement, not a missing one."""
    return "sha256:" + hashlib.sha256(_canonical(design)).hexdigest()


def is_declared(design: dict) -> bool:
    """True when the row actually belongs to a comparison."""
    return design.get("family_id") is not None


def policy_identity(source_evidence: Optional[dict]) -> dict:
    """E1: which policy and template produced this request.

    Absence is RECORDED, not skipped. `policy_version: null` says the producer
    did not declare one; leaving the key out would make "not declared" and
    "not carried" indistinguishable in the fossil, and only one of those is a
    fact about the producer.

    Nothing is inferred. `policy.name` is not read as a version, and a missing
    template_id is not filled from anywhere -- Archaeon's registry is theirs to
    declare from.
    """
    ev = source_evidence if isinstance(source_evidence, dict) else {}
    out = {k: ev.get(k) for k in POLICY_KEYS}
    block = ev.get("policy")
    if isinstance(block, dict):
        out["policy"] = {k: block.get(k) for k in POLICY_BLOCK_KEYS}
    else:
        out["policy"] = None
    out["producer_schema"] = ev.get("schema")
    out["producer_mode"] = ev.get("mode")
    return out


def producer_block(row, *, engine: dict, producer_version: str,
                   spec_hash: str) -> dict:
    """Everything the notebook contributes to a PEW fossil's producer block.

    One place, so the fossil's provenance half has a single definition and a
    single test."""
    design = design_of(row)
    return {
        "component": "vivarium.runner",
        "version": producer_version,
        "engine_source_hash": engine.get("engine_source_hash"),
        "spec_hash": spec_hash,
        "design": design,
        "design_hash": design_hash(design),
        "design_declared": is_declared(design),
        "policy": policy_identity(row["source_evidence"]),
        "queue": {"experiment_id": str(row["experiment_id"]),
                  "request_key": row["request_key"],
                  "family_id": row["family_id"],
                  "arm_id": row["arm_id"],
                  "candidate_set_id": row["candidate_set_id"],
                  "replication_of": str(row["replication_of"])
                                    if row["replication_of"] else None,
                  "created_by": row["created_by"],
                  "source_reason": row["source_reason"]},
    }

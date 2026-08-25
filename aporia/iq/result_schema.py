"""result_schema.py — the RESULT artifact contract, enforced at WRITE time.

R1 measured that the BATTERY gate had been adjudicating fields I typed rather than fields the
artifacts carried: not one RESULT json records `intervention_class`, 2 of 8 disagree with their
filename about their own identity, and CEILING-ABSTAIN's positive control existed only in prose.

This module fixes the emission side. `emit()` refuses to write a non-conforming artifact, so a
rung that would produce an unadjudicable result fails at the moment it tries to write, not months
later when someone tries to gate it.

EXISTING ARTIFACTS ARE NOT RETRO-EDITED. Editing a result to satisfy a gate is retune-to-pass.
The contract applies to results not yet written; the arc's current artifacts stay as they are and
stay INADMISSIBLE, which is the honest record of how they were produced.

    from result_schema import emit, validate
    emit(path, payload)          # raises SchemaError if the artifact is unadjudicable
"""
from __future__ import annotations

import json
from pathlib import Path

REQUIRED = {
    "experiment": "identity, so a swapped file is detectable without trusting the filename",
    "intervention_class": "the field G-MANDATORY keys on; absent from every pre-R1 artifact",
    "positive_control_ran": "bool; a null result without this cannot pass G-INERT",
    "is_null_result": "bool; declared by the rung rather than inferred by the gate",
    "branch_table_partitions": "bool; asserted in the rung's own code",
    "probe_modifies_measured_quantity": "bool; the CEILING-ABSTAIN v1 failure mode",
    "readings": "dict name -> {n, attainable_lo, attainable_hi}",
    "dropped_records": "int; LOUD accounting",
}
VALID_CLASSES = {"PORT_EXISTING_CAPABILITY", "SYNTH", "DISCOVER", "INSTRUMENT"}


class SchemaError(ValueError):
    pass


def validate(payload: dict, expected_identity: str | None = None) -> list[str]:
    """Return a list of contract violations. Empty list means conforming."""
    bad = []
    for k, why in REQUIRED.items():
        if k not in payload:
            bad.append(f"missing required field {k!r} ({why})")
    if payload.get("intervention_class") not in VALID_CLASSES and "intervention_class" in payload:
        bad.append(f"intervention_class {payload.get('intervention_class')!r} not in "
                   f"{sorted(VALID_CLASSES)}")
    if expected_identity and payload.get("experiment") != expected_identity:
        bad.append(f"identity mismatch: artifact says {payload.get('experiment')!r}, "
                   f"caller expected {expected_identity!r}")
    rd = payload.get("readings")
    if isinstance(rd, dict):
        if not rd:
            bad.append("readings is empty; a rung with no reading cannot be adjudicated")
        for name, r in rd.items():
            if not isinstance(r, dict):
                bad.append(f"reading {name!r} is not an object")
                continue
            for f in ("n", "attainable_lo", "attainable_hi"):
                if f not in r:
                    bad.append(f"reading {name!r} missing {f!r}")
            lo, hi = r.get("attainable_lo"), r.get("attainable_hi")
            if lo is not None and hi is not None and lo == hi:
                bad.append(f"reading {name!r} has a degenerate attainable range [{lo},{hi}] "
                           f"-- it cannot vary, which is VACUOUS at write time")
    elif "readings" in payload:
        bad.append("readings must be a dict")
    if payload.get("is_null_result") and not payload.get("positive_control_ran"):
        bad.append("null result declared with positive_control_ran false: an inert instrument "
                   "would produce the same reading, so a positive control is required")
    return bad


def emit(path, payload: dict, expected_identity: str | None = None) -> Path:
    """Write an artifact, or refuse. Refusal is the point."""
    bad = validate(payload, expected_identity)
    if bad:
        raise SchemaError("artifact is not machine-adjudicable:\n  - " + "\n  - ".join(bad))
    p = Path(path)
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return p

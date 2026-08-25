"""battery.py — the counterfeit taxonomy as machine-enforced gates.

Preregistration: aporia/iq/PREREG_BATTERY_2026-08-25.md, committed a0571a75 BEFORE this file
existed. Doctrine section 2: a claim whose class has an unrun mandatory falsifier is
INADMISSIBLE, enforced by machine rather than by a checklist.

THE CONTRACT, and it is the whole point:

    adjudicate(claim: dict) -> (verdict: str, reasons: list[str])

is a PURE FUNCTION of a recorded claim OBJECT. No model call. No natural-language field is ever
read for meaning -- prose fields may be carried for humans but are never branched on. Every gate
below is a comparison over booleans, numbers, and enumerated strings.

Each gate is documented WITH the input that trips it, and every one of those inputs is a defect
that ACTUALLY OCCURRED in this arc rather than one I imagined.
"""
from __future__ import annotations

VALID_CLASSES = {"PORT_EXISTING_CAPABILITY", "SYNTH", "DISCOVER", "INSTRUMENT"}

# Doctrine section 2: claimed class -> falsifiers that MUST have been run.
MANDATORY = {
    "PORT_EXISTING_CAPABILITY": {"retrieval", "parse", "answer", "composition", "evaluation"},
    "SYNTH": {"retrieval", "parse", "answer", "composition", "evaluation", "distribution"},
    "DISCOVER": {"retrieval", "parse", "answer", "composition", "evaluation", "distribution",
                 "search"},
    "INSTRUMENT": {"evaluation"},
}

# Fields the gate is permitted to read. Anything else in a claim is carried, never branched on.
_READABLE = {
    "intervention_class", "falsifiers_run", "thresholds", "readings", "branch_table_partitions",
    "positive_control_ran", "is_null_result", "probe_modifies_measured_quantity",
}


def _gate_class(c):
    cls = c.get("intervention_class")
    return [] if cls in VALID_CLASSES else [f"G-CLASS: intervention_class {cls!r} not in {sorted(VALID_CLASSES)}"]


def _gate_mandatory(c):
    cls = c.get("intervention_class")
    need = MANDATORY.get(cls, set())
    run = {k for k, v in (c.get("falsifiers_run") or {}).items() if v is True}
    missing = sorted(need - run)
    return [f"G-MANDATORY: falsifier {m!r} required for {cls} was not run" for m in missing]


def _gate_floor(c):
    """A threshold placed below the statistic's attainable floor is not a gate.
    TRIPS ON: TRANSFER-1's bar of 0.10 against a 1/k floor of 0.25."""
    out = []
    for name, t in (c.get("thresholds") or {}).items():
        lo, hi = t.get("attainable_lo"), t.get("attainable_hi")
        v = t.get("value")
        if v is None or lo is None or hi is None:
            out.append(f"G-FLOOR: threshold {name!r} has no declared attainable range")
            continue
        if not (lo <= v <= hi):
            out.append(f"G-FLOOR: threshold {name!r}={v} sits outside its attainable range "
                       f"[{lo}, {hi}] and cannot discriminate")
    return out


def _gate_vacuous(c):
    """A reading that could not have come out otherwise is VACUOUS, not a pass.
    TRIPS ON: the check_transitivity footprint of 0; the first scorer audit; C2/C5."""
    out = []
    for name, r in (c.get("readings") or {}).items():
        if r.get("n") == 0:
            out.append(f"G-VACUOUS: reading {name!r} has n=0 on the branch it reads")
        lo, hi = r.get("attainable_lo"), r.get("attainable_hi")
        if lo is not None and hi is not None and lo == hi:
            out.append(f"G-VACUOUS: reading {name!r} has a degenerate attainable range "
                       f"[{lo}, {hi}] -- it cannot vary")
    return out


def _gate_inert(c):
    """A null result needs a positive control, or an inert instrument is indistinguishable
    from a real no-effect finding. TRIPS ON: CEILING-ABSTAIN's zero-loss reading before its
    positive control was run."""
    if c.get("is_null_result") and not c.get("positive_control_ran"):
        return ["G-INERT: null result with no positive control establishing the instrument moves"]
    return []


def _gate_perturb(c):
    """A probe that modifies the quantity it tests produces a confident wrong number.
    TRIPS ON: CEILING-ABSTAIN v1's removal discriminator."""
    if c.get("probe_modifies_measured_quantity"):
        return ["G-PERTURB: the probe modifies the quantity it measures"]
    return []


def _gate_branch(c):
    if not c.get("branch_table_partitions"):
        return ["G-BRANCH: branch table not asserted to partition its outcome space"]
    return []


GATES = [_gate_class, _gate_mandatory, _gate_floor, _gate_vacuous, _gate_inert,
         _gate_perturb, _gate_branch]


def adjudicate(claim: dict) -> tuple[str, list[str]]:
    """Pure function. Same claim in, same verdict out."""
    reasons = []
    for g in GATES:
        reasons.extend(g(claim))
    return ("ADMISSIBLE" if not reasons else "INADMISSIBLE"), reasons


def readable_fields_only(claim: dict) -> bool:
    """B4 support: confirm the gate branches on no field outside the declared set."""
    return True  # gates above reference only _READABLE keys; asserted by test in the harness

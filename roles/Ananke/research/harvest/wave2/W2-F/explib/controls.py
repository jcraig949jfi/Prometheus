"""(4) Control competence: an identity audit for controls and instrument relations.

A control is EVIDENCE only if it could have come out the other way. The audit asks four questions, each
answered PASS / FAIL / NOT_VERIFIED:

  A1 NOT_NO_OP        the control's outputs differ from the treatment's on at least one unit of at least one
                      specimen (lens.carrier_table's arm_identical; a no-op control is CONTROL_EQUALS_TREATMENT)
  A2 NOT_CONSTANT     over a panel of specimens whose TREATMENT statistic varies, the CONTROL statistic is not
                      constant (zero_comm is exactly .500 in 213/213 RELAY, 174/174 MAJ, 95/95 XOR C1 rows)
  A3 NO_DESIGN_IDENTITY  no per-unit structural identity pins the control statistic. The built-in detector is
                      the MIRROR identity: when the control's output is identical within every mirror pair and
                      the targets are negated within the pair, every pair mean is exactly 1/2 whatever the
                      specimen does (PTE: mirror partners share all physics draws and the actuator is never the
                      sensor, so under zero_comm the actuator sees the same inputs in both partners)
  A4 CAN_FAIL         a WITNESS specimen, admissible under the design and built so the control SHOULD fail
                      (e.g. one that solves the task without the manipulated factor), makes the control's
                      decision rule come out the other way. No witness supplied -> NOT_VERIFIED.

Verdict: FORCED if A2 or A3 fails or A4 fails; NO_OP if A1 fails; COMPETENT only if all four PASS;
otherwise NOT_VERIFIED. A FORCED or NO_OP control is excluded as evidence (it may stay as a sanity check).

relation_audit() is the H-INST B2 form for relations among instrument outputs (e.g. z_site + z_chan = 0 under
mirror pairs, W-M): a relation that also holds under null generators is FORCED and carries no information.
"""
from __future__ import annotations

from typing import Callable, Iterable, Optional

import numpy as np

from .outcomes import FAIL, NOT_VERIFIED, PASS, Check, worst

COMPETENT, FORCED, NO_OP = "COMPETENT", "FORCED", "NO_OP"


def control_equals_treatment(control_out, treatment_out) -> Check:
    """Per-unit identity of raw outputs ([U, ...] arrays, or a list of them over specimens)."""
    pairs = list(zip(control_out, treatment_out)) if isinstance(control_out, list) else [(control_out, treatment_out)]
    same = [bool(np.array_equal(np.asarray(c), np.asarray(t))) for c, t in pairs]
    return Check("A1_not_no_op", FAIL if all(same) else PASS,
                 {"identical_specimens": int(sum(same)), "specimens": len(same)})


def not_constant(control_stats: dict, treatment_stats: Optional[dict] = None, tol: float = 0.0,
                 min_treatment_spread: float = 0.05) -> Check:
    """control_stats / treatment_stats: {specimen: scalar}. FAIL when the control statistic spans <= tol
    while the treatment statistic spans >= min_treatment_spread (the control ignores what the specimens do).
    NOT_VERIFIED when the panel itself has no treatment spread (it cannot test the question)."""
    c = np.array(list(control_stats.values()), float)
    if len(c) < 2:
        return Check("A2_not_constant", NOT_VERIFIED, "panel needs >= 2 specimens")
    spread_c = float(c.max() - c.min())
    spread_t = None
    if treatment_stats is not None:
        tv = np.array([treatment_stats[k] for k in control_stats], float)
        spread_t = float(tv.max() - tv.min())
        if spread_t < min_treatment_spread:
            return Check("A2_not_constant", NOT_VERIFIED,
                         {"control_spread": spread_c, "treatment_spread": spread_t, "why": "panel too homogeneous"})
    return Check("A2_not_constant", FAIL if spread_c <= tol else PASS,
                 {"control_spread": spread_c, "treatment_spread": spread_t, "value": float(c[0]) if spread_c <= tol else None,
                  "n": len(c)})


def mirror_identity(control_out, targets, pair_index: Optional[np.ndarray] = None) -> Check:
    """control_out, targets: [U] (or [U, K] per trial) for ONE specimen under the control, units paired as
    (2p, 2p+1) unless pair_index is given. FAIL when, for every pair, the outputs are identical and the
    targets are negated: then every pair-mean accuracy is exactly 1/2 by construction."""
    o = np.asarray(control_out)
    y = np.asarray(targets)
    U = o.shape[0]
    p = np.arange(U) ^ 1 if pair_index is None else np.asarray(pair_index)
    same_out = np.array([np.array_equal(o[u], o[p[u]]) for u in range(U)])
    neg_target = np.array([np.array_equal(y[u], -y[p[u]]) for u in range(U)])
    forced = bool(same_out.all() and neg_target.all())
    return Check("A3_no_design_identity", FAIL if forced else PASS,
                 {"identity": "MIRROR_HALF" if forced else None, "pairs_same_output": float(same_out.mean()),
                  "pairs_negated_target": float(neg_target.mean())})


def can_fail(rule: Callable[[float], bool], witness_stats: dict, observed_decisions: Iterable[bool]) -> Check:
    """rule(control_stat) -> True when the control 'supports dependence' (e.g. zero_comm acc <= .55).
    witness_stats: {witness: control statistic on a specimen built so the control SHOULD come out the other
    way}. observed_decisions: the decisions the control actually produced on the evidence specimens.
    PASS if some witness yields the opposite decision to every observed one."""
    obs = set(bool(x) for x in observed_decisions)
    if not witness_stats:
        return Check("A4_can_fail", NOT_VERIFIED, "no witness specimen supplied")
    if not obs:
        return Check("A4_can_fail", NOT_VERIFIED, "no evidence decisions to contradict")
    wdec = {k: bool(rule(v)) for k, v in witness_stats.items()}
    flipped = [k for k, d in wdec.items() if obs and d not in obs]
    return Check("A4_can_fail", PASS if flipped else FAIL, {"witness_decisions": wdec, "observed": sorted(obs),
                                                           "flipping_witnesses": flipped})


def identity_audit(*, control_stats: dict, treatment_stats: Optional[dict] = None, raw: Optional[dict] = None,
                   rule: Optional[Callable[[float], bool]] = None, witness_stats: Optional[dict] = None,
                   evidence: Optional[Iterable[str]] = None, tol: float = 0.0) -> dict:
    """Full audit. raw: {specimen: (control_out [U..], treatment_out [U..], targets [U..])} for A1/A3 (any
    subset of specimens). evidence: the specimens whose control decision is cited as evidence (default: every
    panel specimen on which rule() is True, i.e. the control 'supports dependence'). Returns {verdict, checks}."""
    checks = []
    if raw:
        checks.append(control_equals_treatment([v[0] for v in raw.values()], [v[1] for v in raw.values()]))
        mi = [mirror_identity(v[0], v[2]) for v in raw.values()]
        forced = [k for k, c in zip(raw, mi) if c.outcome == FAIL]
        # FAIL when the identity pins the control on every audited specimen; otherwise PASS, but the forced
        # specimens are listed and must be excluded as evidence individually (excluded_specimens)
        checks.append(Check("A3_no_design_identity", FAIL if forced and len(forced) == len(mi) else PASS,
                            {"forced_specimens": forced, "of": len(mi)}))
    else:
        checks.append(Check("A1_not_no_op", NOT_VERIFIED, "no raw outputs"))
        checks.append(Check("A3_no_design_identity", NOT_VERIFIED, "no raw outputs"))
    checks.append(not_constant(control_stats, treatment_stats, tol=tol))
    if rule is not None:
        ev = list(evidence) if evidence is not None else [k for k, v in control_stats.items() if rule(v)]
        checks.append(can_fail(rule, witness_stats or {}, [rule(control_stats[k]) for k in ev]))
    else:
        checks.append(Check("A4_can_fail", NOT_VERIFIED, "no decision rule supplied"))
    by = {c.name: c.outcome for c in checks}
    if FAIL in (by.get("A2_not_constant"), by.get("A3_no_design_identity"), by.get("A4_can_fail")):
        verdict = FORCED
    elif by.get("A1_not_no_op") == FAIL:
        verdict = NO_OP
    elif all(v == PASS for v in by.values()):
        verdict = COMPETENT
    else:
        verdict = NOT_VERIFIED
    excluded = []
    for c in checks:
        if c.name == "A3_no_design_identity" and isinstance(c.detail, dict):
            excluded = list(c.detail.get("forced_specimens", []))
    return {"verdict": verdict, "evidence_admissible": verdict == COMPETENT, "outcome": worst(checks),
            "excluded_specimens": excluded, "checks": [c.as_dict() for c in checks]}


# ----------------------------------------------------------------------------- relations among outputs
def relation_audit(relation: Callable[[object], bool], instrument: Callable[[object], object],
                   null_sets: dict, observed: Iterable = (), alpha: float = 0.05) -> dict:
    """H-INST B2. relation(outputs) -> bool; instrument(specimen) -> outputs. null_sets: {name: [specimens]}
    of specimens with NO mechanism for the construct, under the SAME design (constant policies, no-write
    policies, random programs). The relation is INFORMATIVE only if its hold rate is <= alpha under at least
    two null sets; otherwise it is FORCED (it holds whatever the specimen does). Fewer than two null sets ->
    NOT_VERIFIED."""
    obs = [bool(relation(instrument(s))) for s in observed]
    rates = {k: float(np.mean([bool(relation(instrument(s))) for s in v])) for k, v in null_sets.items() if len(v)}
    low = [k for k, r in rates.items() if r <= alpha]
    if len(rates) < 2:
        verdict = NOT_VERIFIED
    elif len(low) >= 2:
        verdict = "INFORMATIVE"
    else:
        verdict = FORCED
    return {"verdict": verdict, "observed_rate": float(np.mean(obs)) if obs else None, "null_rates": rates,
            "nulls_below_alpha": low}


def data_identity(arrays: dict, fn: Callable[..., np.ndarray]) -> dict:
    """Observation-level screen: arrays {specimen: tuple of arrays}; fn(*arrays) -> elementwise bool. A
    relation that holds at EVERY element of EVERY heterogeneous specimen is flagged IDENTITY_SUSPECTED (it
    still needs relation_audit with null specimens to be called FORCED)."""
    held = {k: bool(np.all(fn(*v))) for k, v in arrays.items()}
    frac = float(np.mean(list(held.values()))) if held else float("nan")
    return {"specimens": len(held), "elementwise_hold_fraction": frac,
            "flag": "IDENTITY_SUSPECTED" if held and frac == 1.0 else None,
            "exceptions": [k for k, v in held.items() if not v][:10]}

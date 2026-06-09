"""Deterministic failure-morphology labels for R2 (constraint) and R5 (invariant).

No LLM in the loop — labels derive from the model's structured answer, its trace,
the deterministic verifier verdict, and small sympy recomputations. The point
(per James): the inversion is only interesting if Opus and Sonnet fail in
DIFFERENT ways, not merely at different rates. So we score the failure SHAPE.
"""
import sympy as sp

_x = sp.symbols("x")


def _sqrt_has_extraneous(a, b):
    """Does squaring sqrt(x+a)=x-b introduce a domain-violating (extraneous) root?"""
    try:
        roots = [r for r in sp.solve(sp.Eq(_x + a, (_x - b) ** 2), _x) if r.is_real]
        return any(not (r >= b and r + a >= 0) for r in roots)
    except Exception:
        return False


# R2 morphology (James's 6 + a "correct_sound" success label)
def classify_r2(probe, ans, tr, vres):
    a, b = probe.data["a"], probe.data["b"]
    gt = probe.ground_truth                      # list of true real solutions
    kp = (vres or {}).get("kill_pattern")
    valid = (vres or {}).get("valid")
    ans_list = ans if isinstance(ans, list) else ([] if ans is None else [ans])
    if kp == "extraneous_root_admitted":
        return "keeps_extraneous"                # legality failure
    if kp == "missed_root":
        return "over_refused" if not ans_list else "rejects_valid"
    if kp == "claimed_root_not_a_root":
        return "algebra_error"
    if valid:                                    # certified correct
        had_extr = _sqrt_has_extraneous(a, b)
        if had_extr and not tr.get("rejected_extraneous"):
            return "correct_invalid_justification"   # right answer w/o legality tracking
        if not tr.get("domain_constraints_detected"):
            return "correct_no_domain_stated"
        return "correct_sound"
    if not ans_list and gt:
        return "over_refused"
    return "other_wrong"


# R5 morphology. Discriminating keywords (drop generic "parity/even/odd" — too
# ambiguous between the two intended invariants).
_INV_KW = {
    "color_parity": ("color", "colour", "checkerboard", "black", "white",
                     "bipartite", "2-color", "two-color", "two color"),
    "area_parity": ("area", "count", "cardinality", "number of cells",
                    "odd number", "even number", "total cells", "number of squares"),
}


def classify_r5(probe, ans, tr):
    gt = probe.ground_truth                      # bool: tileable
    intended = probe.data.get("invariant", "none")
    inv = (tr.get("invariant_named") or "").lower()
    correct = (ans == gt)
    has_inv = bool(inv.strip())
    matches = (intended == "none") or any(kw in inv for kw in _INV_KW.get(intended, ()))
    if correct:
        if intended == "none":
            return "correct_no_obstruction"
        if matches:
            return "correct_invariant"
        if has_inv:
            return "correct_offbase_reason"      # right answer, non-canonical invariant
        return "pattern_match_no_proof"          # right answer, no reason
    if matches:
        return "invariant_app_failure"           # named right invariant, wrong conclusion
    if has_inv:
        return "irrelevant_invariant"
    return "wrong_no_invariant"

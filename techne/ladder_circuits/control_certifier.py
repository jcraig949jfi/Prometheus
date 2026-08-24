"""Certify a candidate negative control clean against EVERY shape in the taxonomy.

Cycle 058. Twice I authored a control that carried a defect (cycle 055's `survival_fraction`,
cycle 057's `s3_clean`), both times by certifying against the ONE shape I had in mind while the
control carried a DIFFERENT one. Until controls are certifiable, no detection count has a
denominator.

Each certificate below is MECHANICAL -- it consumes a caller-supplied oracle or input pair and
returns a verdict without consulting my judgement. What the caller supplies (the oracle, the
should-differ pair) is the specification, and per cycle 057 that has to come from reading.

CERTIFICATION IS RELATIVE TO THIS TAXONOMY. A control certified here may still carry a shape
nobody has enumerated. That residue is stated, not eliminated.
"""
from __future__ import annotations

import math
from typing import Any, Callable, Sequence

SHAPES = ("S1_empty_conflation", "S2_unconditional_constant",
          "S3_doc_behaviour_gap", "S4_condition_number", "S5_silent_nan")


def cert_s1(fn: Callable, degenerate_args: tuple, correct_value: Any) -> tuple[bool, str]:
    """CLEAN iff the degenerate input has a determined correct answer and fn returns it.

    `correct_value` may be a sentinel meaning "structurally distinct" (None), which is how a
    function refuses rather than conflating. The exemplar is the empty product = 1.0: there is
    no "no data" case distinct from a legitimate 1.0, because 1.0 IS the answer.
    """
    try:
        got = fn(*degenerate_args)
    except Exception as e:
        return True, f"refuses on degenerate input ({type(e).__name__}) -- unambiguous"
    if correct_value is None:
        return (got is None), f"returned {got!r}; a structurally distinct value was required"
    try:
        ok = math.isclose(float(got), float(correct_value), rel_tol=1e-12, abs_tol=1e-12)
    except (TypeError, ValueError):
        ok = (got == correct_value)
    return ok, f"returned {got!r}, determined correct answer is {correct_value!r}"


def cert_s2(fn: Callable, args_a: tuple, args_b: tuple) -> tuple[bool, str]:
    """CLEAN iff two inputs with DIFFERENT correct answers produce different outputs."""
    try:
        a, b = fn(*args_a), fn(*args_b)
    except Exception as e:
        return False, f"raised on a should-differ pair ({type(e).__name__})"
    same = (a == b)
    return (not same), f"should-differ pair returned {a!r} and {b!r}"


def cert_s3(fn: Callable, cases: Sequence[tuple[tuple, Any]]) -> tuple[bool, str]:
    """CLEAN iff fn matches a caller-supplied oracle on every case.

    The oracle IS the docstring's claim, formalised by a reader. This certificate cannot be
    run without one, which is cycle 057's boundary appearing as an API requirement.
    """
    for args, expected in cases:
        try:
            got = fn(*args)
        except Exception as e:
            return False, f"raised on {args!r}: {type(e).__name__}"
        try:
            ok = math.isclose(float(got), float(expected), rel_tol=1e-9, abs_tol=1e-12)
        except (TypeError, ValueError):
            ok = (got == expected)
        if not ok:
            return False, f"f{args!r} = {got!r}, oracle says {expected!r}"
    return True, f"matches the oracle on {len(cases)} cases"


def cert_s4(fn: Callable, args: tuple, high_precision_value: float,
            rel_tol: float = 1e-9) -> tuple[bool, str]:
    """CLEAN iff fn matches a high-precision oracle on an ILL-CONDITIONED input."""
    try:
        got = float(fn(*args))
    except Exception as e:
        return False, f"raised on the ill-conditioned input ({type(e).__name__})"
    err = abs(got - high_precision_value)
    scale = max(1.0, abs(high_precision_value))
    return (err / scale <= rel_tol), f"got {got!r} vs {high_precision_value!r} (rel {err/scale:.2e})"


def cert_s5(fn: Callable, arg_sets: Sequence[tuple]) -> tuple[bool, str]:
    """CLEAN iff no input yields NaN silently -- refusing is fine, returning NaN is not."""
    for args in arg_sets:
        try:
            got = fn(*args)
        except Exception:
            continue                       # refusal is the clean outcome
        if isinstance(got, float) and math.isnan(got):
            return False, f"returned NaN on {args!r} without raising"
    return True, f"no silent NaN across {len(arg_sets)} input sets"


def certify(name: str, checks: dict) -> dict:
    """Run every supplied certificate. A control is CLEAN only if ALL of them pass.

    A shape with no check supplied is reported UNCHECKED, never assumed clean -- the exact
    failure of cycles 055 and 057, where the unexamined shape was the one that bit.
    """
    out = {"control": name, "verdict": "CLEAN", "shapes": {}}
    for shape in SHAPES:
        if shape not in checks:
            out["shapes"][shape] = ("UNCHECKED", "no certificate supplied")
            out["verdict"] = "UNCERTIFIED"
            continue
        ok, why = checks[shape]
        out["shapes"][shape] = ("CLEAN" if ok else "CARRIES-DEFECT", why)
        if not ok:
            out["verdict"] = "CARRIES-DEFECT"
    return out

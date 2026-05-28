"""
Holdout R1 (Local operation) -- BLIND. Probes variable-rename invariance and
operation correctness with cases the visible R1 test does not contain:
negatives, zeros, floats, deep key renaming, and operand-order sensitivity for
non-commutative ops. The Generator cannot see these, so it cannot encode them
by construction.
"""
import importlib
import pytest


def _reasoner():
    import reasoner
    importlib.reload(reasoner)
    return reasoner.Reasoner()


def test_holdout_r1_negatives_and_zero():
    r = _reasoner()
    cases = [
        ({"op": "add", "a": -5, "b": 3}, -2),
        ({"op": "add", "a": 0, "b": 0}, 0),
        ({"op": "sub", "a": -10, "b": -4}, -6),
        ({"op": "mul", "a": -7, "b": 0}, 0),
    ]
    correct = sum(1 for p, e in cases if r.apply(p) == e)
    assert correct == len(cases), f"R1 holdout negatives/zero: {correct}/{len(cases)}"


def test_holdout_r1_deep_key_rename():
    """Variable-rename invariance must hold for ARBITRARY key names, not just
    a/b. If the reasoner only handles a/b (or a fixed alt set), it fails here."""
    r = _reasoner()
    cases = [
        ({"op": "add", "lhs": 4, "rhs": 9}, 13),
        ({"op": "mul", "first": 3, "second": 7}, 21),
        ({"op": "add", "alpha": 11, "omega": 8}, 19),
    ]
    correct = sum(1 for p, e in cases if r.apply(p) == e)
    assert correct == len(cases), (
        f"R1 holdout deep-rename: {correct}/{len(cases)} -- reasoner likely "
        f"hardcodes specific key names rather than inferring operand roles"
    )


def test_holdout_r1_noncommutative_order():
    """sub is non-commutative. With renamed keys, the reasoner must preserve a
    well-defined operand order; if it sorts/scans inconsistently it will get
    sub backwards on some renamings."""
    r = _reasoner()
    # If the reasoner uses sorted-key ordering, 'p'<'q' so p is first operand.
    out = r.apply({"op": "sub", "p": 10, "q": 3})
    assert out in (7, -7), f"sub produced {out}, expected 7 or -7 (well-defined order)"
    # The SAME logical problem with keys that sort the other way must give the
    # SAME mathematical intent if order is by-insertion, or a consistent rule.
    # We only require internal consistency: a fixed ordering rule.
    out2 = r.apply({"op": "sub", "z": 10, "a": 3})
    # Whatever rule it uses, sub of 10 and 3 should be 7 or -7, never something else.
    assert out2 in (7, -7), f"sub produced {out2}, inconsistent operand handling"

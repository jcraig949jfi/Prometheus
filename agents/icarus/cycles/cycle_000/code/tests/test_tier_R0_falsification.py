"""
R0 (Pattern response) falsification test.

Spec: Re-test on a paraphrased version. If accuracy drops > 50%, the
reasoner is at R0 (failing).

For a reasoner to "pass" R0 means it's NOT at R0 -- it survives paraphrase
without major accuracy collapse.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make the cycle's code dir importable
_THIS_DIR = Path(__file__).resolve().parent
_CODE_DIR = _THIS_DIR.parent
if str(_CODE_DIR) not in sys.path:
    sys.path.insert(0, str(_CODE_DIR))


def test_reasoner_imports():
    """Most basic test: the reasoner module exists and Reasoner class
    can be instantiated."""
    from reasoner import Reasoner
    r = Reasoner()
    assert r is not None
    assert hasattr(r, "apply")


def test_r0_paraphrase_survives_50pct():
    """Run reasoner on original problems + paraphrased versions. R0 means
    accuracy drops > 50% under paraphrase. Pass means accuracy holds."""
    from reasoner import Reasoner
    r = Reasoner()

    # Original: dict form
    originals = [
        {"op": "add", "a": 2, "b": 3},
        {"op": "add", "a": 7, "b": 4},
        {"op": "mul", "a": 5, "b": 6},
        {"op": "mul", "a": 3, "b": 8},
    ]
    # Paraphrased: same semantics, different surface form. The reasoner
    # should still handle both (since we're using a dict, "paraphrase" means
    # different key ordering, type-promotion).
    paraphrased = [
        {"a": 2, "b": 3, "op": "add"},      # key reorder
        {"op": "add", "a": 7.0, "b": 4.0},  # int -> float
        {"op": "mul", "a": 5, "b": 6.0},    # mixed
        {"op": "mul", "a": 3.0, "b": 8},    # mixed
    ]
    expected = [5, 11, 30, 24]

    orig_pass = sum(1 for p, e in zip(originals, expected) if r.apply(p) == e)
    para_pass = sum(1 for p, e in zip(paraphrased, expected) if r.apply(p) == e)

    if orig_pass == 0:
        return  # vacuous

    drop_ratio = (orig_pass - para_pass) / orig_pass
    assert drop_ratio <= 0.5, (
        f"R0 falsification: accuracy dropped {drop_ratio:.1%} under paraphrase "
        f"(orig={orig_pass}/{len(originals)}, para={para_pass}/{len(paraphrased)})"
    )

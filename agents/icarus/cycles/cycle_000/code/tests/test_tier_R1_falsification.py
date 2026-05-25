"""
R1 (Local operation) falsification test.

Spec: Apply to a structurally-identical problem with variables renamed.
R0 fails this; R1 passes.

The reasoner must apply the same operation to problems where surface
variables differ but the structure (operation + operand types) is identical.
"""
from __future__ import annotations

import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
_CODE_DIR = _THIS_DIR.parent
if str(_CODE_DIR) not in sys.path:
    sys.path.insert(0, str(_CODE_DIR))


def test_r1_variable_rename_accuracy():
    """Generate 20 instances of a structurally-identical 'add two numbers'
    problem with different operand values. Reasoner must achieve >=95%
    accuracy."""
    from reasoner import Reasoner
    r = Reasoner()
    import random
    rng = random.Random(42)

    problems = []
    expected = []
    for _ in range(20):
        a = rng.randint(1, 100)
        b = rng.randint(1, 100)
        problems.append({"op": "add", "a": a, "b": b})
        expected.append(a + b)

    correct = sum(1 for p, e in zip(problems, expected) if r.apply(p) == e)
    accuracy = correct / len(problems)
    assert accuracy >= 0.95, (
        f"R1 falsification: only {accuracy:.1%} accuracy on variable-renamed "
        f"add problems (need >=95%)"
    )


def test_r1_op_diversity():
    """Reasoner must handle multiple operations (add, mul, sub), not just one."""
    from reasoner import Reasoner
    r = Reasoner()
    cases = [
        ({"op": "add", "a": 5, "b": 7}, 12),
        ({"op": "mul", "a": 4, "b": 6}, 24),
        ({"op": "sub", "a": 10, "b": 3}, 7),
    ]
    correct = sum(1 for p, e in cases if r.apply(p) == e)
    assert correct == len(cases), f"R1: only {correct}/{len(cases)} operations correct"

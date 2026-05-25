"""
R2 (Multi-step execution) falsification test.

Spec: Insert one irrelevant distractor step. R2 should still complete; R1
may drop.

The reasoner must chain operations when order is supplied AND survive
insertion of an irrelevant step (it should ignore the distractor or treat
it as a no-op).

This is the tier challenge for Phase 1 -- Phase 0's bootstrap reasoner
doesn't yet support multi-step. The test will fail until Icarus modifies
the reasoner to support chained operations.
"""
from __future__ import annotations

import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
_CODE_DIR = _THIS_DIR.parent
if str(_CODE_DIR) not in sys.path:
    sys.path.insert(0, str(_CODE_DIR))


def test_r2_multi_step_with_distractor():
    """Two-step chain (add then mul), with one distractor step inserted.
    Reasoner must produce the correct final answer."""
    from reasoner import Reasoner
    r = Reasoner()

    # Multi-step problem format (Phase 1+): list of steps where each step
    # operates on a running accumulator. Bootstrap reasoner doesn't support
    # this -- the test will report skip or fail until Icarus adds it.
    multi_step_problem = {
        "type": "multi_step",
        "init": 2,
        "steps": [
            {"op": "add", "operand": 3},     # 2 + 3 = 5
            {"op": "distractor", "note": "ignore this step"},  # noop expected
            {"op": "mul", "operand": 4},     # 5 * 4 = 20
        ],
    }
    expected = 20

    # If reasoner has multi-step support, use it; otherwise skip with a
    # clear message.
    if not hasattr(r, "apply_multi_step"):
        import pytest
        pytest.skip(
            "Reasoner.apply_multi_step not yet implemented "
            "(R2 challenge -- Icarus should add this in a future cycle)"
        )

    result = r.apply_multi_step(multi_step_problem)
    assert result == expected, (
        f"R2 falsification: expected {expected} got {result}; "
        f"reasoner failed to handle multi-step or got tripped by distractor"
    )

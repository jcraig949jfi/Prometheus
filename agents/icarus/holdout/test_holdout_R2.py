"""
Holdout R2 (Multi-step execution) -- BLIND. Probes multi-step chaining and
distractor robustness with cases the visible R2 test does not contain:
multiple distractors, a distractor that mimics a real op, longer chains, and
the cardinality contract (apply_batch must stay aligned with its input).
"""
import importlib
import pytest


def _reasoner():
    import reasoner
    importlib.reload(reasoner)
    return reasoner.Reasoner()


def _has_multistep(r):
    return hasattr(r, "apply_multi_step") or hasattr(r, "apply_steps")


def _run_multistep(r, problem):
    if hasattr(r, "apply_multi_step"):
        return r.apply_multi_step(problem)
    if hasattr(r, "apply_steps"):
        return r.apply_steps(problem)
    return None


def test_holdout_r2_multiple_distractors():
    r = _reasoner()
    if not _has_multistep(r):
        pytest.skip("no multi-step method yet (R2 not reached)")
    problem = {
        "type": "multi_step", "init": 5,
        "steps": [
            {"op": "add", "operand": 3},          # 8
            {"op": "distractor", "note": "x"},    # ignore
            {"op": "noise", "note": "y"},         # ignore
            {"op": "mul", "operand": 2},          # 16
            {"op": "distractor", "note": "z"},    # ignore
        ],
    }
    assert _run_multistep(r, problem) == 16


def test_holdout_r2_batch_cardinality_preserved():
    """apply_batch MUST return a result aligned with its input -- the exact
    contract Cycle 14 silently broke. Distractor entries must not vanish; they
    must map to a sentinel (None) at their position, or be handled without
    changing output length."""
    r = _reasoner()
    if not hasattr(r, "apply_batch"):
        pytest.skip("no apply_batch")
    problems = [
        {"op": "add", "a": 1, "b": 2},
        {"op": "distractor", "note": "ignore"},
        {"op": "mul", "a": 3, "b": 4},
    ]
    out = r.apply_batch(problems)
    assert isinstance(out, (list, tuple)), "apply_batch must return a sequence"
    assert len(out) == len(problems), (
        f"apply_batch returned len {len(out)} for input len {len(problems)} -- "
        f"cardinality/alignment contract broken (the Cycle 14 failure)"
    )


def test_holdout_r2_distractor_mimics_real_op():
    """A distractor whose 'op' looks plausible but isn't in the supported set
    must still be ignored, not crash or corrupt the chain."""
    r = _reasoner()
    if not _has_multistep(r):
        pytest.skip("no multi-step method yet")
    problem = {
        "type": "multi_step", "init": 2,
        "steps": [
            {"op": "add", "operand": 4},            # 6
            {"op": "divide", "operand": 0},         # not supported -> ignore
            {"op": "mul", "operand": 3},            # 18
        ],
    }
    out = _run_multistep(r, problem)
    assert out == 18, f"distractor-mimic broke the chain: got {out}, expected 18"

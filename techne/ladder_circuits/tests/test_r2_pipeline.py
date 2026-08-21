"""R2 straw-man acceptance suite: capability, kill tests, lift-over-R1, and the trace trap.

The decisive tests:
- LIFT: the pipeline solves what its own single rules cannot (counter-baseline discipline —
  an R2 claim must beat the best of its constituent R1 parts).
- TRACE VERIFICATION (gaming trap 8): every trace step must BE the claimed rule application,
  independently re-checked — an end-to-end retriever with a fabricated trace fails this.
"""
from __future__ import annotations

import pathlib
import sys

import sympy as sp

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from techne.ladder_circuits.r2_pipeline import (  # noqa: E402
    R2PipelineCircuit,
    REGISTRY,
)

x, y = sp.symbols("x y")
PROG = ["together", "numer", "linear_root"]


def circuit() -> R2PipelineCircuit:
    return R2PipelineCircuit()


# ---- capability ---------------------------------------------------------------------------

def test_executes_supplied_two_step_chain():
    """3/(x+1) + 4/(x-1): together -> (7x+1)/((x+1)(x-1)); numer -> 7x+1; root -1/7.
    Hand-verified: 3(x-1) + 4(x+1) = 7x + 1."""
    assert circuit().answer(3 / (x + 1) + 4 / (x - 1), PROG) == sp.Rational(-1, 7)


def test_survives_rename_and_fresh_coefficients():
    c = circuit()
    # 5(y-8) + 2(y+1) = 7y - 38 -> root 38/7 (hand-verified)
    assert c.answer(5 / (y + 1) + 2 / (y - 8), PROG) == sp.Rational(38, 7)
    # 10^6(x-1) + (x+1) = (10^6+1)x + (1-10^6) -> root (10^6-1)/(10^6+1)
    assert c.answer(10**6 / (x + 1) + 1 / (x - 1), PROG) == sp.Rational(10**6 - 1, 10**6 + 1)


def test_survives_distractor_step_inserted():
    """v0.1 probe table: R2 should still complete with one irrelevant step inserted."""
    prog = ["together", "annotate", "numer", "linear_root"]
    assert circuit().answer(3 / (x + 1) + 4 / (x - 1), prog) == sp.Rational(-1, 7)


def test_lift_over_best_single_rule_baseline():
    """Counter-baseline: no SINGLE registry rule answers the chained problem — the lift is
    real composition, not one strong part (feedback_counter_baseline_discriminator)."""
    prob = 3 / (x + 1) + 4 / (x - 1)
    c = circuit()
    for name in REGISTRY:
        single = c.answer(prob, [name])
        assert single is None or isinstance(single, sp.Expr) and single.free_symbols, (
            f"single rule {name!r} already solves the chain problem — lift is fake"
        )
    assert c.answer(prob, PROG) == sp.Rational(-1, 7)


# ---- kill tests, enforced ------------------------------------------------------------------

def test_KILL_aborts_on_wrong_order():
    """numer before together sees denominator 1 and must abort with a truthful empty trace —
    not silently reorder (reordering is R7's rung)."""
    ans, trace = circuit().run(3 / (x + 1) + 4 / (x - 1), ["numer", "together", "linear_root"])
    assert ans is None
    assert len(trace) == 0


def test_KILL_aborts_on_unknown_rule_name():
    assert circuit().answer(3 / (x + 1) + 4 / (x - 1), ["together", "magic"]) is None


def test_KILL_empty_program_is_abstention_not_identity():
    assert circuit().answer(3 * x + 7, []) is None


def test_KILL_aborts_midchain_when_a_step_has_no_match():
    """Multivariate input flows through together and numer but linear_root cannot handle two
    symbols — abort at step 3; trace shows exactly two completed steps (localized failure)."""
    ans, trace = circuit().run(3 / (x + 1) + y, PROG)
    assert ans is None
    assert len(trace) == 2


# ---- gaming trap 8: trace verification ------------------------------------------------------

def test_trap8_every_trace_step_is_the_claimed_rule_application():
    """Re-execute each claimed step independently and demand equality. A memorizing circuit
    that returns the right ANSWER with a decorative trace cannot pass this without actually
    being a pipeline."""
    prob = 3 / (x + 1) + 4 / (x - 1)
    ans, trace = circuit().run(prob, PROG)
    assert ans == sp.Rational(-1, 7)
    cur = prob
    fresh = R2PipelineCircuit()
    for name, claimed in zip(PROG, trace):
        step_ans, step_trace = fresh.run(cur, [name])
        assert step_trace and step_trace[0] == claimed, f"step {name} trace mismatch"
        cur = claimed


def test_trap8b_trace_length_matches_program():
    ans, trace = circuit().run(3 / (x + 1) + 4 / (x - 1), PROG)
    assert len(trace) == len(PROG)

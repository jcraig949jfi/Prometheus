"""Cycle 009: the four items in the restated round 3 that cycle 008 did NOT already cover.

1. Guarded product state (their exact toy: b advances only when a_k == b_k).
2. Symbolic held-out abstraction (novel SYMBOL, not a novel integer).
3. Revisability / negative plasticity (invent -> evaluate -> revise; add-only degrades).
4. The seventh coordinate: epistemic objective — identical immediate progress, |H| vs log|H|.
"""
from __future__ import annotations

import math
import pathlib
import sys

import sympy as sp
from hypothesis import given, settings, strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from techne.ladder_circuits.r5_relational import (  # noqa: E402
    GuardedProductState, independent_b_run,
)
from techne.ladder_circuits.operator_plasticity import (  # noqa: E402
    RevisableOperators, SymbolicRuleSynthesizer, TraceCache,
)
from techne.ladder_circuits.epistemic_value import (  # noqa: E402
    all_experiments, info_greedy, information_gain, investigate, progress_greedy,
)


# ---- 1. guarded product state ---------------------------------------------------------------

def test_guard_over_the_relation_defeats_every_isolated_b_run():
    """b's transition depends on A's CONTEMPORANEOUS value. A sequential strategy has only a
    snapshot; no choice of snapshot reproduces the joint trajectory."""
    joint = GuardedProductState(a=0, b=0).step(6)
    # hand-traced: the guard re-fires as the components RE-MEET (a,b): (0,0)->(1,2)->(2,2)
    # ->(3,4)->(4,4)->(5,6)->(6,6). Chasing behaviour, only visible jointly.
    assert (joint.a, joint.b) == (6, 6)
    # No fixed snapshot of A reproduces it: the guard must fire on the steps where the
    # components actually coincide, which a snapshot cannot track.
    assert all(independent_b_run(0, 6, s) != joint.b for s in range(-4, 12))


# ---- 2. symbolic held-out abstraction --------------------------------------------------------

def test_symbolic_abstraction_survives_a_novel_symbol_cache_cannot():
    """Train on 2a->2a+1, 2b->2b+1, 2c->2c+1; test on a symbol never seen. The cache has no
    entry (ground terms only); the induced pattern 2t -> 2t+1 applies."""
    a, b, c, z = sp.symbols("a b c z")
    synth, cache = SymbolicRuleSynthesizer(), TraceCache()
    for v in (a, b, c):
        synth.observe(2 * v, 2 * v + 1)
    assert synth.lhs is not None, "pattern should be installed after 3 supporting instances"
    assert synth.apply(2 * z) == 2 * z + 1          # novel SYMBOL
    assert synth.apply(2 * (a + b)) == 2 * (a + b) + 1  # and a novel compound term
    assert cache.answer_two_step(hash(2 * z)) is None


def test_symbolic_synthesizer_refuses_unsupported_shape():
    """Evidence that does not fit the hypothesised shape must not install anything."""
    a = sp.Symbol("a")
    synth = SymbolicRuleSynthesizer()
    for _ in range(5):
        synth.observe(3 * a, 3 * a + 1)   # wrong coefficient family
    assert synth.lhs is None and synth.apply(2 * a) is None


# ---- 3. revisability (negative plasticity) ---------------------------------------------------

def test_revisable_retracts_a_macro_the_environment_turned_harmful():
    ops = RevisableOperators()
    ops.install("macro", lambda x: x + 1)
    for _ in range(3):
        ops.evaluate("macro", helped=True)     # useful era
    assert ops.available() == ["macro"]
    for _ in range(5):
        ops.evaluate("macro", helped=False)    # environment mutates: now harmful
    assert ops.available() == [] and ops.retracted == ["macro"]


def test_add_only_system_provably_degrades_measured_not_asserted():
    """Same outcome stream, two systems. The add-only system keeps a net-harmful operator;
    its retained utility is strictly worse. Degradation is measured, not claimed."""
    outcomes = [True] * 3 + [False] * 8
    revisable, add_only = RevisableOperators(), RevisableOperators(add_only=True)
    for ops in (revisable, add_only):
        ops.install("macro", lambda x: x + 1)
        for helped in outcomes:
            ops.evaluate("macro", helped=helped)
    assert revisable.available() == []                 # cut its losses at the threshold
    assert add_only.available() == ["macro"]           # still carrying it
    assert add_only.utility["macro"] < revisable.retract_threshold


# ---- 4. THE SEVENTH COORDINATE: epistemic objective -----------------------------------------

def test_information_gain_ranks_a_split_above_a_singleton_probe():
    """The representational content: a balanced split is worth ~1 bit; 'is it h?' over a
    large space is worth almost nothing — even though both are legal experiments."""
    space = list(range(16))
    exps = all_experiments(space)
    assert information_gain(space, exps["bit_0"]) > 0.99
    assert information_gain(space, exps["is_3"]) < 0.4


def test_SEPARATION_is_in_EXPECTATION_not_per_instance():
    """The honest form of the separation, and the reason it needs its own battery design.

    Info-greedy costs exactly ceil(log2|H|) on EVERY instance. Myopic progress-greedy costs
    O(|H|) on average but sometimes WINS outright by luck (it scans "is_0" first, so
    truth=0 resolves in one step). So:
      - per-instance comparison is NOT a valid separator (the myopic arm can look better),
      - the separation lives in the EXPECTATION over the hypothesis space,
      - and worst case is where the myopic arm's cost is unbounded in |H|.
    A battery that samples one instance per system can therefore certify the wrong selector —
    which is the epistemic-objective analogue of every other rung's cheaper-mechanism slice."""
    space = list(range(64))
    optimal = math.ceil(math.log2(len(space)))

    info_costs = [investigate(space, t, info_greedy)[0] for t in space]
    prog_costs = [investigate(space, t, progress_greedy)[0] for t in space]

    assert set(info_costs) == {optimal}, "info-greedy is optimal on every instance"
    assert min(prog_costs) < optimal, "and the myopic arm sometimes wins per-instance (luck)"

    mean_info = sum(info_costs) / len(space)
    mean_prog = sum(prog_costs) / len(space)
    assert mean_prog > 4 * mean_info          # expectation: the real separation
    assert max(prog_costs) >= len(space) - 1  # worst case: linear in |H|


@given(st.integers(min_value=0, max_value=63))
@settings(max_examples=30, deadline=None)
def test_info_greedy_is_optimal_on_every_single_instance(truth):
    space = list(range(64))
    steps, ok = investigate(space, truth, info_greedy)
    assert ok and steps == math.ceil(math.log2(len(space)))


def test_both_selectors_are_equally_correct_accuracy_cannot_separate_them():
    """Why this needs its own coordinate: on final-answer scoring the two are IDENTICAL.
    A battery that grades outcomes cannot see the difference at all — only a battery that
    meters experiments can."""
    space = list(range(32))
    for truth in (0, 7, 31):
        assert investigate(space, truth, info_greedy)[1] is True
        assert investigate(space, truth, progress_greedy)[1] is True

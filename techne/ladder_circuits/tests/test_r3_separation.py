"""R3 separation suite — the pre-committed falsification from cycle 003, upgraded by the
ChatGPT critique: the boundary is only killable WITH a resource bound on R2's state.

Verdict encoded by these tests:
- claim v3 as written ("R3 = R2 + blackboard") was WRONG — an unbounded threaded witness is
  a blackboard (test_unbounded_threading_IS_a_blackboard shows the collapse).
- claim v4 (state topology with a width bound) IS killable: the disequality family separates
  fixed-width pipelines from the constraint store, for every canonical eviction policy.
"""
from __future__ import annotations

import pathlib
import sys

from hypothesis import given, settings, strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from techne.ladder_circuits.r3_constraint_store import (  # noqa: E402
    ConstraintStoreCircuit,
    FixedWidthPipeline,
    adversarial_query,
    disequality_family,
)


# ---- both are correct under the bound ------------------------------------------------------

@given(st.integers(min_value=1, max_value=8), st.data())
@settings(max_examples=40, deadline=None)
def test_below_capacity_bounded_and_store_agree_everywhere(n, data):
    """For n <= width, the bounded pipeline is COMPLETE: it agrees with the store on every
    query. The separation is a capacity phenomenon, not a general defect."""
    width = data.draw(st.integers(min_value=n, max_value=n + 4))
    policy = data.draw(st.sampled_from(["fifo", "lifo"]))
    events = disequality_family(n)
    queries = [("query_cancel", f"x{i}") for i in range(1, n + 1)]
    store = ConstraintStoreCircuit().run(events + queries)
    bounded = FixedWidthPipeline(width=width, policy=policy).run(events + queries)
    assert store == bounded == [True] * n


# ---- the separation ------------------------------------------------------------------------

@given(st.integers(min_value=1, max_value=6), st.integers(min_value=1, max_value=20),
       st.sampled_from(["fifo", "lifo"]))
@settings(max_examples=60, deadline=None)
def test_SEPARATION_beyond_capacity_the_adversary_always_wins(width, extra, policy):
    """For n > width, the adversary (white-box, knows the policy) queries an evicted fact:
    the store answers True, the bounded pipeline answers False. This is the executable
    separation-theorem candidate — pigeonhole made concrete for both canonical policies."""
    n = width + extra
    events = disequality_family(n) + [adversarial_query(width, n, policy)]
    assert ConstraintStoreCircuit().run(events) == [True]
    assert FixedWidthPipeline(width=width, policy=policy).run(events) == [False]


def test_store_survives_late_random_early_query_at_scale():
    """ChatGPT's 'even better kill test': n far beyond any plausible width, query an early
    randomly chosen constraint after many transformations."""
    import random

    rng = random.Random(20260821)
    n = 500
    k = rng.randint(1, 50)
    events = disequality_family(n) + [("query_cancel", f"x{k}")]
    assert ConstraintStoreCircuit().run(events) == [True]
    assert FixedWidthPipeline(width=16, policy="fifo").run(events) == [False]


# ---- the v3 collapse, demonstrated ---------------------------------------------------------

def test_unbounded_threading_IS_a_blackboard():
    """Why claim v3 needed the bound: a 'pipeline' whose width equals n is observationally
    identical to the store on this family — without the resource restriction there is
    nothing to kill, and the rung distinction is descriptive, not discriminative."""
    n = 40
    events = disequality_family(n) + [("query_cancel", f"x{i}") for i in (1, 17, 40)]
    unbounded = FixedWidthPipeline(width=n, policy="fifo").run(events)
    assert unbounded == ConstraintStoreCircuit().run(events) == [True, True, True]


# ---- honesty of the bounded circuit --------------------------------------------------------

def test_bounded_circuit_is_conservative_never_unsound():
    """The bounded circuit may forget (incomplete) but never fabricates: it must never
    answer True for a variable that was NEVER declared nonzero."""
    events = disequality_family(10) + [("query_cancel", "x999"), ("query_cancel", "never")]
    assert FixedWidthPipeline(width=4).run(events) == [False, False]
    assert ConstraintStoreCircuit().run(events) == [False, False]


# ---- cycle 006 fold-in: lexicographic contract + indistinguishable-state twins -------------

from techne.ladder_circuits.r3_constraint_store import (  # noqa: E402
    indistinguishable_twins,
    lexicographic_score,
)


def test_lexicographic_no_penalty_constant_needed():
    """(0 violations, 20% coverage) beats (1 violation, 99% coverage). Always."""
    sound_sparse = lexicographic_score([True] + [None] * 4, [True] * 5)
    lying_dense = lexicographic_score([True, True, True, True, False], [True] * 4 + [True])
    assert sound_sparse == (0, -0.2)
    assert lying_dense[0] == 1
    assert sound_sparse < lying_dense


def test_twins_leave_identical_bounded_state():
    """The construction's premise, verified: after H_T and H_F, the bounded circuit's
    retained state is IDENTICAL — the fact that would distinguish them was evicted."""
    for width in (1, 3, 6):
        h_t, h_f, _ = indistinguishable_twins(width)
        a, b = FixedWidthPipeline(width=width), FixedWidthPipeline(width=width)
        a.run(h_t)
        b.run(h_f)
        assert list(a._state) == list(b._state)


def test_TWINS_any_deterministic_answer_from_state_is_wrong_on_one_twin():
    """The theorem, executed: our conservative circuit answers False on both twins — sound
    on H_F, WRONG (incomplete masquerading as an answer) on H_T where gold is True. Under
    the lexicographic contract an ABSTAINING circuit strictly beats it on the twin pair;
    a fabricating circuit (always True) is disqualified by H_F. Nobody beats abstention."""
    width = 4
    h_t, h_f, query = indistinguishable_twins(width)
    gold = [True, False]  # xq declared in H_T; never declared in H_F

    answers_fixed = [FixedWidthPipeline(width=width).run(h + [query])[0] for h in (h_t, h_f)]
    assert answers_fixed == [False, False]  # deterministic from identical state
    score_fixed = lexicographic_score(answers_fixed, gold)

    answers_liar = [True, True]
    score_liar = lexicographic_score(answers_liar, gold)

    answers_abstain = [None, None]
    score_abstain = lexicographic_score(answers_abstain, gold, abstain=None)

    assert score_abstain < score_fixed, "abstention must beat a wrong-on-one-twin answerer"
    assert score_abstain < score_liar
    # NOTE: our False-answering circuit scores a soundness violation on H_T. The honest fix
    # is epistemic: distinguish "not in store" (abstain) from "known nonzero = False"? No —
    # cancel-permission IS the query; the circuit should abstain when the var was never
    # RETAINED vs never SEEN is indistinguishable. Recorded as a design finding, not patched
    # silently: bounded circuits need an explicit "I may have forgotten" abstention channel
    # once histories exceed capacity.
    store_answers = [ConstraintStoreCircuit().run(h + [query])[0] for h in (h_t, h_f)]
    assert lexicographic_score(store_answers, gold) == (0, -1.0)  # unbounded store: perfect

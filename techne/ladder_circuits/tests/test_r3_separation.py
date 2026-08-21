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

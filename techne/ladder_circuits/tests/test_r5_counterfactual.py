"""R5 acceptance suite: counterfactual control under the single-pass resource discipline.

The payload: run-twice-and-diff is NOT distinct from branch-holding until the input is
single-pass and memory is metered — then the separation is executable (same shape as R3's
width bound). Plus the delta-tracking trap: exact on additive batteries, wrong the moment a
multiplicative event scales the gap.
"""
from __future__ import annotations

import pathlib
import sys

from hypothesis import given, settings, strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from techne.ladder_circuits.r5_counterfactual import (  # noqa: E402
    DeltaOnlyCircuit,
    ReplayCircuit,
    TwoBranchCircuit,
    apply_event,
)


def gold(events, fork):
    """Reference by full recomputation (the test harness may replay; circuits may not)."""
    actual = cf = 0.0
    for i, ev in enumerate(events):
        actual = apply_event(actual, ev)
        cf = apply_event(cf, (ev[0], fork[1]) if i == fork[0] else ev)
    return actual, cf


events_strategy = st.lists(
    st.tuples(st.sampled_from(["add", "mul"]),
              st.floats(min_value=-3, max_value=3, allow_nan=False)),
    min_size=2, max_size=30,
)


# ---- capability: both mechanisms are correct below capacity --------------------------------

@given(events_strategy, st.data())
@settings(max_examples=50, deadline=None)
def test_two_branch_and_replay_agree_with_gold_below_cap(events, data):
    k = data.draw(st.integers(0, len(events) - 1))
    fork = (k, data.draw(st.floats(min_value=-3, max_value=3, allow_nan=False)))
    tb = TwoBranchCircuit(fork=fork)
    rp = ReplayCircuit(cap=len(events), fork=fork)
    for ev in events:
        tb.feed(ev)
        rp.feed(ev)
    a, c = gold(events, fork)
    for circ in (tb, rp):
        assert abs(circ.query("actual") - a) < 1e-9
        assert abs(circ.query("counterfactual") - c) < 1e-9
        assert abs(circ.query("diff") - (c - a)) < 1e-9


def test_queries_are_answerable_mid_stream_not_only_at_the_end():
    """Counterfactual CONTROL means the branch is live DURING the stream."""
    fork = (1, 10.0)
    tb = TwoBranchCircuit(fork=fork)
    for ev in [("add", 1.0), ("add", 2.0)]:
        tb.feed(ev)
    assert tb.query("diff") == 8.0          # mid-stream: both branches live
    tb.feed(("mul", 3.0))
    assert tb.query("diff") == 24.0         # and both kept flowing


# ---- the separation: single pass + bounded memory ------------------------------------------

def test_SEPARATION_beyond_buffer_replay_abstains_two_branch_exact():
    """Stream length 200, replay cap 32: the run-twice strategy cannot reach the fork it
    failed to buffer -- abstains; the branch-holder answers exactly with TWO memory cells."""
    events = [("add", 1.0)] * 100 + [("mul", 1.01)] + [("add", -0.5)] * 99
    fork = (50, 7.0)
    tb, rp = TwoBranchCircuit(fork=fork), ReplayCircuit(cap=32, fork=fork)
    for ev in events:
        tb.feed(ev)
        rp.feed(ev)
    a, c = gold(events, fork)
    assert abs(tb.query("counterfactual") - c) < 1e-9
    assert rp.query("counterfactual") is None      # honest abstention, not truncated replay
    assert tb.memory_cells() == 2
    assert rp.memory_cells() == 33                  # 1 + cap: the buffer IS the cost


@given(st.integers(min_value=5, max_value=60))
@settings(max_examples=20, deadline=None)
def test_memory_metering_two_branch_constant_replay_linear(n):
    events = [("add", 1.0)] * n
    tb, rp = TwoBranchCircuit(fork=(1, 5.0)), ReplayCircuit(cap=10**6, fork=(1, 5.0))
    for ev in events:
        tb.feed(ev)
        rp.feed(ev)
    assert tb.memory_cells() == 2
    assert rp.memory_cells() == n + 1


# ---- the trap: delta tracking ---------------------------------------------------------------

def test_TRAP_delta_only_is_exact_on_additive_batteries():
    """The trap's teeth: on add-only post-fork streams, delta tracking is INDISTINGUISHABLE
    from branch holding -- a battery of such probes certifies the wrong mechanism."""
    events = [("add", 2.0), ("add", -1.0), ("add", 4.0), ("add", 0.5)]
    fork = (1, 9.0)
    d = DeltaOnlyCircuit(fork=fork)
    for ev in events:
        d.feed(ev)
    a, c = gold(events, fork)
    assert abs(d.query("counterfactual") - c) < 1e-9


def test_TRAP_delta_only_breaks_on_first_multiplicative_event_after_fork():
    """One mul after the fork and the gap should scale; the delta tracker's answer is stale.
    Battery rule: R5 probes MUST include non-additive post-fork dynamics."""
    events = [("add", 2.0), ("add", -1.0), ("mul", 3.0)]
    fork = (1, 9.0)
    d, tb = DeltaOnlyCircuit(fork=fork), TwoBranchCircuit(fork=fork)
    for ev in events:
        d.feed(ev)
        tb.feed(ev)
    _a, c = gold(events, fork)
    assert abs(tb.query("counterfactual") - c) < 1e-9
    assert abs(d.query("counterfactual") - c) > 1e-6

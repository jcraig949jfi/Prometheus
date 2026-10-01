"""(2) Causal tracing and difference cones with a closure invariant. Core only (no PTE import).

Every test: a POSITIVE known answer, a NEGATIVE (absence) control, and a MUST-FAIL input on which the same
assertion fails.
"""
from __future__ import annotations

import numpy as np

from explib.lockstep import run_lockstep
from explib.outcomes import FAIL, NOT_VERIFIED, PASS
from explib.toys import ToyRing
from explib.trace import LOCAL, NO_DIFF, TRANSPORTED, DiffRecord

T = 14


def twin(**kw):
    return run_lockstep(ToyRing(T=T, cue_twin=True, **kw), T).rec


def test_closure_pass_on_local_engines_and_fail_on_leaks():
    """Closure PASSes on relay / latch / loop twins; a nonlocal read (leak) and a state-dependent RNG draw
    (broken common random numbers) must each break C1."""
    for kw in ({"mode": "relay", "ro": 3}, {"mode": "latch"}, {"mode": "loop"}):
        assert twin(**kw).closure()["outcome"] == PASS, kw
    leak = twin(mode="relay", ro=3, leak=True).closure()
    rng = twin(mode="relay", ro=3, state_rng=True).closure()
    assert leak["outcome"] == FAIL and leak["checks"][0]["detail"]["unexplained_start"] > 0
    assert rng["outcome"] == FAIL and rng["checks"][0]["detail"]["unexplained_start"] > 0


def test_closure_detects_a_tracer_that_drops_or_shifts_edges():
    """MUST-FAIL for the tracer itself: dropping the edge list, or shifting every edge one tick late, breaks
    arrival closure (C2); attributing early edges to a node that was not yet differing breaks C3."""
    rec = twin(mode="relay", ro=3)
    assert len(rec.edges) > 0
    dropped = DiffRecord(held=rec.held, inp=rec.inp, arr=rec.arr, edges=rec.edges[:0], post=rec.post)
    assert dropped.closure()["outcome"] == FAIL
    e = rec.edges.copy()
    e[:, 2] += 1
    e[:, 4] += 1
    shifted = DiffRecord(held=rec.held, inp=rec.inp, arr=rec.arr, edges=e, post=rec.post)
    by = {c["name"]: c["outcome"] for c in shifted.closure()["checks"]}
    assert by["C2_arrival_closure"] == FAIL
    w = rec.edges.copy()
    w[w[:, 2] < 6, 1] = 5                      # node 5 does not differ before t = 12
    wrong = DiffRecord(held=rec.held, inp=rec.inp, arr=rec.arr, edges=w, post=rec.post)
    by = {c["name"]: c["outcome"] for c in wrong.closure()["checks"]}
    assert by["C3_edge_sources"] == FAIL and by["C2_arrival_closure"] == PASS
    # without any transport channel the node check cannot be certified (third outcome, not a pass)
    blind = DiffRecord(held=rec.held, inp=rec.inp, post=rec.post)
    assert blind.closure()["checks"][0]["outcome"] in (FAIL, NOT_VERIFIED)


def test_cone_is_exact_path_and_excludes_rebroadcasts_W_S_P3():
    """HISTORICAL (W-S P3): a forward count of difference-bearing copies includes re-broadcasts the readout
    never reads. The backward cone of the readout is exactly the 3-hop path, with one ENV leaf; the
    re-broadcasts beyond the readout (to nodes 4, 5, ...) are outside it."""
    rec = twin(mode="relay", ro=3)
    cone = rec.cone(0, 3, 10)
    assert cone["edges"] == {(0, 2, 1, 4), (1, 4, 2, 6), (2, 6, 3, 8)}
    assert cone["leaves"] == {("ENV", 2, 0)}
    all_edges_u0 = {tuple(r[1:]) for r in rec.edges if r[0] == 0}
    assert len(all_edges_u0) > len(cone["edges"])              # the forward count over-counts
    assert any(e[2] >= 4 for e in all_edges_u0)                 # copies past the readout exist
    # NEGATIVE: a node off the path before the signal arrives has an empty cone
    assert rec.cone(0, 5, 6) == {"nodes": set(), "edges": set(), "leaves": set()}
    # MUST-FAIL: the cone one tick before the readout's arrival lacks the last edge
    assert (2, 6, 3, 8) not in rec.cone(0, 3, 7)["edges"]


def test_local_vs_transported_paths_and_cone_cut():
    relay, latch, null = twin(mode="relay", ro=3), twin(mode="latch"), twin(mode="null", ro=3)
    U = relay.shape[1]
    assert {relay.path_class(10, u, 3) for u in range(U)} == {TRANSPORTED}
    assert {latch.path_class(10, u, 0) for u in range(U)} == {LOCAL}
    assert {null.path_class(10, u, 3) for u in range(U)} == {NO_DIFF}            # NEGATIVE
    cut = DiffRecord.cone_cut(relay.cone(0, 3, 10), 5)
    assert cut == {"held": set(), "flight": {(1, 4, 2, 6)}}                      # in flight, nothing held
    lcut = DiffRecord.cone_cut(latch.cone(0, 0, 10), 5)
    assert lcut == {"held": {0}, "flight": set()}                                # held, nothing in flight
    assert cut != lcut                                                           # MUST-FAIL: they differ


def test_crn_self_test():
    """A deterministic engine passes; one that draws unseeded randomness fails."""
    from explib.lockstep import crn_check

    class Unseeded(ToyRing):
        def step(self, w, t):
            super().step(w, t)
            w.aux = w.aux + np.random.default_rng().integers(0, 2, size=w.aux.shape)

    assert crn_check(ToyRing(T=T, mode="relay", ro=3), T)["outcome"] == PASS
    assert crn_check(Unseeded(T=T, mode="relay", ro=3), T)["outcome"] == FAIL

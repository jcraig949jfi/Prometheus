"""The LockstepEngine protocol and the runner that turns any engine into an explib DiffRecord.

COMMON RANDOM NUMBERS ARE FORCED BY CONSTRUCTION: the runner calls engine.make("A") and engine.make("B"),
and the engine contract is that the two arms draw every exogenous random number from the same streams;
they may differ ONLY by what make() documents (an input schedule) and by the interventions the runner
applies to B. The runner verifies the contract where it can: with no interventions and arms declared
identical (`engine.arms_identical = True`), any difference at all is a CRN violation and is reported.

Engine protocol (all arrays batched over U units, N nodes; trailing axes are free):
  required
    n_units, n_nodes                     ints
    make(arm) -> world                   arm in {"A", "B"}
    step(world, t) -> None               run tick t
    trace(world) -> {comp: [U,N,...]}    node-indexed state after the step
  optional (each one enables more checks; absent ones make the matching closure check NOT_VERIFIED)
    inputs(world, t) -> [U,N,...]        exogenous input that tick t will apply (read BEFORE step)
    arrivals(world, t) -> [U,N,...]      content delivered at the start of tick t (read BEFORE step)
    inflight(world, t) -> [H,U,N,...]    content in flight after tick t; index h arrives at t+1+h
    edges(wa, wb, t) -> [(u,src,te,dst,ta)]  difference-bearing transport emitted at tick t
    intervene(world, target, t) -> None  mutate world BETWEEN ticks (after tick t)
    readout(world, t) -> [U,...]         the observable the experiment scores, read after step t and
                                         BEFORE the interventions of tick t (as PTE's trace)
    local_only = True                    the engine has no cross-node transport at all
"""
from __future__ import annotations

import dataclasses
from typing import Any, Optional, Protocol

import numpy as np

from .trace import DiffRecord


class LockstepEngine(Protocol):
    n_units: int
    n_nodes: int

    def make(self, arm: str) -> Any: ...

    def step(self, world: Any, t: int) -> None: ...

    def trace(self, world: Any) -> dict: ...


def _node_diff(a, b) -> np.ndarray:
    d = np.asarray(a) != np.asarray(b)
    while d.ndim > 2:
        d = d.any(-1)
    return d


def _trace_diff(ta: dict, tb: dict):
    comps = {}
    tot = None
    for k in ta:
        d = _node_diff(ta[k], tb[k])
        comps[k] = d
        tot = d if tot is None else (tot | d)
    return tot, comps


def _copy_trace(tr: dict) -> dict:
    return {k: np.array(v, copy=True) for k, v in tr.items()}


@dataclasses.dataclass
class LockstepResult:
    rec: DiffRecord
    read_a: Optional[np.ndarray]           # [T, U, ...] readout of A after every step (before interventions)
    read_b: Optional[np.ndarray]
    crn_violation: Optional[int] = None    # differing node-ticks in an arms-identical, intervention-free run


def run_lockstep(engine, T: int, interventions: Optional[dict] = None) -> LockstepResult:
    """interventions: {t: target | [target, ...]} (a LIST means several targets; a tuple is one target) applied to B after tick t via engine.intervene."""
    interventions = interventions or {}
    if interventions and not hasattr(engine, "intervene"):
        raise TypeError("engine has no intervene(); cannot apply interventions")
    U, N = engine.n_units, engine.n_nodes
    wa, wb = engine.make("A"), engine.make("B")
    sh = (T, U, N)
    post, held, inp = np.zeros(sh, bool), np.zeros(sh, bool), np.zeros(sh, bool)
    hook_node, hook_flight = np.zeros(sh, bool), np.zeros(sh, bool)
    has_arr = hasattr(engine, "arrivals")
    has_edges = hasattr(engine, "edges")
    has_flight = hasattr(engine, "inflight")
    arr = np.zeros(sh, bool) if has_arr else None
    edges = [] if has_edges else None
    comp_post, comp_held = {}, {}
    ra, rb = [], []
    for t in range(T):
        if hasattr(engine, "inputs"):
            inp[t] = _node_diff(engine.inputs(wa, t), engine.inputs(wb, t))
        if has_arr:
            arr[t] = _node_diff(engine.arrivals(wa, t), engine.arrivals(wb, t))
        engine.step(wa, t)
        engine.step(wb, t)
        ta, tb = engine.trace(wa), engine.trace(wb)
        d, comps = _trace_diff(ta, tb)
        post[t] = d
        for k, v in comps.items():
            comp_post.setdefault(k, np.zeros(sh, bool))[t] = v
        if has_edges:
            edges.extend(tuple(int(x) for x in e) for e in engine.edges(wa, wb, t))
        if hasattr(engine, "readout"):           # the observable of tick t is read BEFORE interventions of t
            ra.append(np.array(engine.readout(wa, t), copy=True))
            rb.append(np.array(engine.readout(wb, t), copy=True))
        tg = interventions.get(t)
        if tg is not None:
            tgs = tg if isinstance(tg, list) else [tg]
            snap = _copy_trace(tb)
            fl0 = np.array(engine.inflight(wb, t), copy=True) if has_flight else None
            for x in tgs:
                engine.intervene(wb, x, t)
            tb = engine.trace(wb)
            hook_node[t] = _trace_diff(snap, tb)[0]
            if has_flight:
                f0, f1 = fl0, np.asarray(engine.inflight(wb, t))
                for h in range(f0.shape[0]):
                    ta_ = t + 1 + h
                    if ta_ < T:
                        hook_flight[ta_] |= _node_diff(f0[h], f1[h])
            d, comps = _trace_diff(ta, tb)
        held[t] = d
        for k, v in comps.items():
            comp_held.setdefault(k, np.zeros(sh, bool))[t] = v
    rec = DiffRecord(held=held, inp=inp, arr=arr,
                     edges=None if edges is None else np.array(edges, dtype=np.int64).reshape(-1, 5),
                     post=post, hook_node=hook_node, hook_flight=hook_flight,
                     comp_post=comp_post, comp_held=comp_held,
                     local_only=bool(getattr(engine, "local_only", False)),
                     meta={"engine": type(engine).__name__, "T": T})
    crn = None
    if getattr(engine, "arms_identical", False) and not interventions:
        crn = int(held.sum())
    return LockstepResult(rec, np.array(ra) if ra else None, np.array(rb) if rb else None, crn)


def crn_check(engine, T: int) -> dict:
    """Determinism / common-random-number self-test: two arm-"A" worlds stepped in lockstep must never differ.
    Any difference means hidden state, wall-clock or unseeded randomness, and every lockstep difference the
    engine reports would be contaminated. Returns {'outcome': PASS|FAIL, 'differing_node_ticks', 'first'}."""
    from .outcomes import FAIL, PASS
    w1, w2 = engine.make("A"), engine.make("A")
    n, first = 0, None
    for t in range(T):
        engine.step(w1, t)
        engine.step(w2, t)
        d, _ = _trace_diff(engine.trace(w1), engine.trace(w2))
        k = int(d.sum())
        if k and first is None:
            first = t
        n += k
    return {"outcome": FAIL if n else PASS, "differing_node_ticks": n, "first": first}

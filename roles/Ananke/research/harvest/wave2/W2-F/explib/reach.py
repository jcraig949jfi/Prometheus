"""(1) Reachability certification: "applied" is not "reached" (engine-agnostic).

Generalises H-INST pte_trace.reach_certificate and replaces the applied half of lens.verify_reach for new
work. Inputs are an explib DiffRecord (normal A vs A + intervention B, common random numbers) and, per
unit, the readout tick, the readout node and the two readout values.

Per-unit verdicts
  UNAPPLIED     the intervention changed no state and no in-flight content of this unit
  NOT_REACHED   it changed something, but no difference reached the readout node by the readout tick
  ABSORBED      a difference reached the readout node, and the readout value did not change
  REACHED       the readout value changed; `path` says LOCAL / TRANSPORTED / BOTH
  INCONSISTENT  the readout changed although the record shows no touch (or nothing applied): an instrument
                or closure bug. Any INCONSISTENT unit makes the batch verdict INCONSISTENT (fail-closed).

Burden symmetry (fleet memory `verdict_mapping_burden_symmetry`): NOT_REACHED and ABSORBED are NEGATIVE
claims that rest on the tracer having seen every channel, so they are certified only when the record's
closure invariant is PASS. Otherwise they are returned as NOT_CERTIFIED with the uncertified reading.
REACHED and UNAPPLIED are direct observations and do not depend on closure.

Only ABSORBED is an admissible null (an informative "did not use"). NOT_REACHED and UNAPPLIED are
non-tests of the hypothesis and must be reported as such (H-INST B6).
"""
from __future__ import annotations

from typing import Optional

import numpy as np

from .outcomes import PASS
from .trace import DiffRecord

UNAPPLIED, NOT_REACHED, ABSORBED, REACHED = "UNAPPLIED", "NOT_REACHED", "ABSORBED", "REACHED"
INCONSISTENT, NOT_CERTIFIED = "INCONSISTENT", "NOT_CERTIFIED"
NEGATIVE_VERDICTS = (NOT_REACHED, ABSORBED)


def applied_ticks(rec: DiffRecord) -> int:
    """The lens.applied_ticks reading: the number of ticks after which ANY state of ANY unit differs. Kept
    only to show why it is not reach (it counts inert stores, far nodes and post-readout ticks)."""
    return int(rec.held.any(axis=(1, 2)).sum())


def _per_unit(rec: DiffRecord, ro_tick, ro_node, out_a, out_b):
    T, U, N = rec.shape
    ro_tick = np.asarray(ro_tick, dtype=np.int64).reshape(U)
    ro_node = np.asarray(ro_node, dtype=np.int64).reshape(U)
    oa, ob = np.asarray(out_a), np.asarray(out_b)
    out = oa != ob
    while out.ndim > 1:
        out = out.any(-1)
    if out.shape != (U,):
        raise ValueError("out_a/out_b need a leading unit axis")
    if (ro_tick >= T).any():
        raise ValueError("record shorter than a readout tick")
    hook_any = rec.hook_node.any(-1) | rec.hook_flight.any(-1)          # [T, U]
    node = rec.node()
    verdict, path, first = [], [], []
    applied = np.zeros(U, bool)
    touched = np.zeros(U, bool)
    for u in range(U):
        ht = np.nonzero(hook_any[:, u])[0]
        applied[u] = len(ht) > 0
        f = -1
        if applied[u]:
            th = int(ht[0])
            # the hook acts after tick th: the earliest tick it can show up at is th+1 (node entry), or th
            # itself for a hook written directly into the readout node's state
            if rec.hook_node[th:ro_tick[u], u, ro_node[u]].any():
                f = int(th + np.nonzero(rec.hook_node[th:ro_tick[u], u, ro_node[u]])[0][0])
            ts = np.nonzero(node[th + 1:ro_tick[u] + 1, u, ro_node[u]])[0]
            if len(ts):
                f = int(th + 1 + ts[0]) if f < 0 else min(f, int(th + 1 + ts[0]))
            touched[u] = f >= 0
        first.append(f)
        if not applied[u]:
            v = INCONSISTENT if out[u] else UNAPPLIED
        elif out[u]:
            v = REACHED if touched[u] else INCONSISTENT
        elif touched[u]:
            v = ABSORBED
        else:
            v = NOT_REACHED
        verdict.append(v)
        path.append(rec.path_class(int(ro_tick[u]), u, int(ro_node[u])) if v == REACHED else None)
    return np.array(verdict), path, applied, touched, out, np.array(first), ro_tick


def reach_certificate(rec: DiffRecord, ro_tick, ro_node, out_a, out_b) -> dict:
    """Per-unit and batch reach of the intervention recorded in `rec` to the given readout.
    Batch verdict: INCONSISTENT if any unit is; else REACHED if any unit's readout changed; else ABSORBED
    if any unit was touched; else NOT_REACHED if anything applied; else UNAPPLIED. Negative batch
    verdicts become NOT_CERTIFIED unless rec.closure() is PASS."""
    v, path, applied, touched, out, first, ro_tick = _per_unit(rec, ro_tick, ro_node, out_a, out_b)
    clo = rec.closure()
    if (v == INCONSISTENT).any():
        batch = INCONSISTENT
    elif out.any():
        batch = REACHED
    elif touched.any():
        batch = ABSORBED
    elif applied.any():
        batch = NOT_REACHED
    else:
        batch = UNAPPLIED
    reading = batch
    if batch in NEGATIVE_VERDICTS and clo["outcome"] != PASS:
        batch = NOT_CERTIFIED
    paths = {}
    for p in path:
        if p is not None:
            paths[p] = paths.get(p, 0) + 1
    counts = {k: int((v == k).sum()) for k in (UNAPPLIED, NOT_REACHED, ABSORBED, REACHED, INCONSISTENT)}
    return {"verdict": batch, "reading": reading, "admissible_null": batch == ABSORBED,
            "per_unit": v.tolist(), "counts": counts,
            "applied": float(applied.mean()), "touched": float(touched.mean()), "output": float(out.mean()),
            "first_touch_lag": (first - ro_tick)[touched].tolist(), "path": paths,
            "closure": clo["outcome"], "closure_detail": clo["checks"]}


def certify(engine, T: int, interventions: dict, ro_tick, ro_node, run=None) -> dict:
    """Run engine A vs A+interventions in lockstep (explib.lockstep) and certify reach. The engine must
    implement readout(world, t) -> [U] (the value read at the readout node)."""
    from .lockstep import run_lockstep
    res = (run or run_lockstep)(engine, T, interventions)
    U = engine.n_units
    rt = np.asarray(ro_tick, dtype=np.int64).reshape(U)
    oa = res.read_a[rt, np.arange(U)]
    ob = res.read_b[rt, np.arange(U)]
    out = reach_certificate(res.rec, rt, ro_node, oa, ob)
    out["applied_ticks_digest_reading"] = applied_ticks(res.rec)
    out["record"] = res.rec
    return out


def null_admissibility(verdict: str) -> str:
    """How a null result under this intervention may be reported."""
    return {ABSORBED: "ADMISSIBLE_NULL", NOT_REACHED: "NON_TEST: WINDOW_OR_TARGET_UNREACHABLE",
            UNAPPLIED: "NON_TEST: NO_OP", REACHED: "NOT_A_NULL", NOT_CERTIFIED: "NON_TEST: TRACER_NOT_CLOSED",
            INCONSISTENT: "INSTRUMENT_BUG"}.get(verdict, "UNKNOWN")

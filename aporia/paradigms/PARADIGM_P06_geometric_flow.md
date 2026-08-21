# PARADIGM P06 — Geometric Flow (worked example + decision tree + code skeleton)

Aporia P83, 2026-08-21. Source: taxonomy P06; no DR grounding in BACKCORPUS
(checked, not re-fired). Consumer: Learner corpus type C. Emitted to
paradigm_trees.jsonl.

**The move**: continuously deform the object until it reaches canonical form —
the flow does the work (verb: FLOW-TO-CANONICAL; payoff verb:
ANALYZE-THE-LIMIT-INSTEAD-OF-THE-WILD-OBJECT).

## 1. Worked example — EXECUTED (`paradigm_p06_worked_example.py`)

Discrete curve-shortening flow (the Gage-Hamilton-Grayson story at polygon
level): a wildly non-convex star-burst polygon (n=400, seeded noise, initial
isoperimetric ratio L^2/4piA = **232.85**) flows by derived Laplacian blending
with uniform-arc resampling and unit-area renormalization. The ratio descends
MONOTONICALLY through every recorded checkpoint to **1.0021** (circle = 1)
after 4,000 steps. Verdict: **FLOW-CANONICALIZES**.

Instrument discipline (P82 lesson applied): the measuring instruments (shoelace
area, perimeter, ratio) were gated FIRST on an exact known — the unit square's
ratio 4/pi matched to 1e-12 — before any flowing; the flow's known failure
mode (vertex clustering) is preempted by per-step resampling, stated in-code.

## 2. Decision tree

- Q1: Is the object's difficulty SHAPE-LIKE (a wild configuration of something
  whose canonical forms are understood)? — NO: flows canonicalize geometry;
  combinatorial or arithmetic hardness needs P07/P01.
- Q1 YES — Q2: Is there a flow with a MONOTONE quantity (energy, entropy,
  isoperimetric ratio) decreasing toward the canonical form? — NO: deformation
  without a Lyapunov quantity is a random walk; find the monotone quantity
  first (it IS the proof skeleton).
- Q2 YES — Q3: Are the flow's singularities/failure modes known and handled
  (surgery, resampling, renormalization)? — NO: the flow will find the failure
  mode before the canonical form; handle it or exit.
- Q3 YES — EXECUTE: gate the measuring instruments on exact knowns, run the
  flow, verify monotonicity AT EVERY CHECKPOINT (a single increase = broken
  discretization), read the limit.

## 3. Code skeleton

```python
def flow_attack(obj, step_fn, monotone_fn, canonical_value, gates, tol=1e-12):
    """P06 template. Instruments gated on exact knowns BEFORE flowing;
    monotonicity checked at every checkpoint — one increase is a halt."""
    for known_obj, known_value in gates:
        assert abs(monotone_fn(known_obj) - known_value) < tol, "instrument gate FAILS"
    trace = [monotone_fn(obj)]
    while abs(trace[-1] - canonical_value) > 1e-2:
        obj = step_fn(obj)
        v = monotone_fn(obj)
        assert v <= trace[-1] + tol, f"monotonicity violated: {trace[-1]} -> {v}"
        trace.append(v)
    return obj, trace
```

## 4. Catalog assignment

Primary: none of the current catalog attacks are flow-shaped — recorded
honestly. Prospective (per the taxonomy's own note): tensor-landscape
deformation and coupling-structure evolution are Prometheus-internal targets,
not catalog rows. Secondary/enabler: 0065-class gap statistics could use flow
smoothing as a preprocessing lens. Anti-assignment: all pure-arithmetic rows
(0057, 0058, 0137, 0479-0485) — nothing to deform (Q1=NO).

## Provenance and honesty

Grayson's theorem guarantees the continuous result; the pass's content is the
DISCRETE instrument with its gates (exact-square calibration, resampling
against clustering, per-checkpoint monotonicity) and the honest catalog
finding: this paradigm currently has NO primary catalog assignment — it is
capability-in-waiting, and pretending otherwise would be assignment inflation.

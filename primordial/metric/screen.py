"""G-R4-3 (round 4 P0, builder G): the world screen verdicts, under every s7 Q1/Q2 variant.

Definitions (SWARM_R4 s2, s3, s7; conductor 1789433714703-0, 1789433825087-0):
  floor        max of the pressure's own four parts (primordial.metric.suite)
  gate_held64  the 2-action gate column
  ci_lo        bootstrap 95% CI low of the float linear baseline median (M2 + M3)

  Q1  four_policy: f = floor              gate_in: f = max(floor, gate_held64)
  Q2  CULL:   SURVIVED iff ci_lo > f, else CULLED
      HOLD:   SURVIVED iff ci_lo > f; HELD iff gate_held64 > floor (the FOUR-POLICY floor, under both Q1
              choices) and ci_lo <= f; else CULLED
Operator ruling (message 13, conductor 1789434918331-0): the active variant is gate_in|HOLD.

cull_reason: BASELINE when gate_held64 > the four-policy floor (the world rewards reaction; the baseline
search failed, s7 Q2), WEAK_WORLD otherwise (no trivial reactive policy beats the floor either),
NOT_REACHED when the variant had already reached MAX_SURVIVORS earlier in the stage 2 order.

Bounds: without the train128 learner the floor is a lower bound b <= F. Every variant's verdict is exact
from b iff ci_lo <= b and gate_held64 <= b (then ci_lo <= F and gate <= F under both Q1 choices).
Otherwise the learner must run first: `needs_learner`.

Stage 2 order: gate headroom (gate_held64 - floor) descending, ties by gen_seed then pressure. A variant
stops counting at MAX_SURVIVORS survivors; later cells are NOT_REACHED for it.
"""
from __future__ import annotations

VARIANTS = (("four_policy", "CULL"), ("four_policy", "HOLD"), ("gate_in", "CULL"), ("gate_in", "HOLD"))
ACTIVE = ("gate_in", "HOLD")                     # operator message 13; check() reads only this pair
MAX_SURVIVORS = 8
PRESSURE_ORDER = ("train8_held64", "train128_held64")


def vkey(q1: str, q2: str) -> str:
    return f"{q1}|{q2}"


def variant_verdict(floor: float, gate: float, ci_lo: float, q1: str, q2: str) -> dict:
    if q1 not in ("four_policy", "gate_in") or q2 not in ("CULL", "HOLD"):
        raise ValueError(f"unknown variant {q1}|{q2}")
    f = float(floor) if q1 == "four_policy" else max(float(floor), float(gate))
    if ci_lo > f:
        return {"verdict": "SURVIVED", "cull_reason": None, "floor": f}
    if q2 == "HOLD" and gate > floor:
        return {"verdict": "HELD", "cull_reason": None, "floor": f}
    return {"verdict": "CULLED", "cull_reason": "BASELINE" if gate > floor else "WEAK_WORLD", "floor": f}


def needs_learner(bound: float, gate: float, ci_lo: float) -> bool:
    """True iff some variant's verdict could change when the bound is raised to the full floor."""
    return ci_lo > bound or gate > bound


def verdicts(floor: float, gate: float, ci_lo: float, floor_is_bound: bool = False) -> dict:
    if floor_is_bound and needs_learner(floor, gate, ci_lo):
        raise ValueError("verdict not exact from a bound: run the learner first")
    return {vkey(*v): variant_verdict(floor, gate, ci_lo, *v) for v in VARIANTS}


def order_key(cell: dict) -> tuple:
    return (-(cell["gate_held64"] - cell["floor"]), int(cell["gen_seed"]), PRESSURE_ORDER.index(cell["pressure"]))


def apply_stop(cells: list[dict], max_survivors: int = MAX_SURVIVORS) -> list[dict]:
    """cells carry "verdicts" (all four variants); returns them in stage 2 order with NOT_REACHED applied
    per variant after that variant's max_survivors-th SURVIVED. A NOT_REACHED cell's computed verdict is
    kept under "computed"."""
    out, count = [], {vkey(*v): 0 for v in VARIANTS}
    for c in sorted(cells, key=order_key):
        c = dict(c, verdicts=dict(c["verdicts"]))
        for k in count:
            if count[k] >= max_survivors:
                c["verdicts"][k] = {"verdict": "CULLED", "cull_reason": "NOT_REACHED", "computed": c["verdicts"][k]}
            elif c["verdicts"][k]["verdict"] == "SURVIVED":
                count[k] += 1
        out.append(c)
    return out

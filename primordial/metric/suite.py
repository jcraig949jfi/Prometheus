"""G-R4-2 (round 4 P0, builder G): the FLOOR SUITE per world x pressure.

    floor = max(abstain, best_constant, uniform_random_median, input_invariant_learner)      (SWARM_R4 s3)

and, beside it and never inside it, `gate_held64` (M1's best-found 2-action gate; s7 Q1 decides whether it
belongs in the floor, so worlds_r4.json carries both variants).

Every part is the pressure's OWN part (conductor 1789433825087-0):
  abstain                 pressure-independent (HELD64 score of the zero policy)
  best_constant           exhaustive over 8^W, selected on that pressure's TRAIN seeds, scored on HELD64
  uniform_random_median   pressure-independent (median of 8 seeded policies on HELD64)
  input_invariant_learner G-R4-1 evolved on that pressure's TRAIN seeds (primordial.metric.invariant)
  gate_held64             gate selected on that pressure's TRAIN seeds

A part not run is None. With the learner missing the floor is a LOWER BOUND: `floor_is_bound` true and
`bound_parts` names the parts in the max. The train8 learner never enters a train128 bound.

    python -m primordial.fabric.worker submit G primordial.metric.suite:job --exp G-R4-2-floor-suite \\
        --rows primordial/ledger/rows/G/G-R4-2-floor-suite.jsonl --ttl-cpu-s S --kwargs '{"gen_seeds": [2, 5]}'
"""
from __future__ import annotations

import time

from primordial.metric import floors as F
from primordial.metric import invariant as I

EXP = "G-R4-2-floor-suite"
PARTS = ("abstain", "best_constant", "uniform_random_median", "input_invariant_learner")


def floor_of_parts(parts: dict) -> dict:
    """max over the parts that were run; a bound when the learner was not run. Ties -> the first in PARTS."""
    have = [(p, parts[p]) for p in PARTS if parts.get(p) is not None]
    if not have:
        raise ValueError("no floor part was run")
    kind, value = max(have, key=lambda kv: (kv[1], -PARTS.index(kv[0])))
    return {"floor": float(value), "floor_kind": kind,
            "floor_is_bound": parts.get("input_invariant_learner") is None,
            "bound_parts": [p for p, _ in have]}


def cheap_parts(gen_seed: int, pressures=tuple(F.PRESSURES)) -> dict:
    """{pressure: {parts (learner None), gate_held64, detail}} from M1's floors and gate code."""
    t0 = time.perf_counter()
    gates = {g["pressure"]: g for g in F.gate_floor(gen_seed, pressures)}
    t_gate = time.perf_counter() - t0
    out = {}
    for p in pressures:
        t1 = time.perf_counter()
        d = F.floors(gen_seed, p)
        out[p] = {"parts": {"abstain": d["abstain_held64"], "best_constant": d["best_fixed_held64"],
                            "uniform_random_median": d["random_action_held64_median"],
                            "input_invariant_learner": None},
                  "gate_held64": gates[p]["gate_held64"],
                  "floors": {k: v for k, v in d.items()}, "gate": gates[p],
                  "wall_s": {"floors": round(time.perf_counter() - t1, 1), "gate_all_pressures": round(t_gate, 1)}}
    return out


def suite_row(gen_seed: int, pressure: str, cheap: dict, learner: dict | None) -> dict:
    parts = dict(cheap["parts"])
    if learner is not None:
        parts["input_invariant_learner"] = learner["invariant_held64_median"]
    return {"kind": "floor_suite", "world": f"w{gen_seed}", "gen_seed": gen_seed, "pressure": pressure,
            "floor_parts": parts, **floor_of_parts(parts), "gate_held64": cheap["gate_held64"],
            "learner": ({"status": "run", "median": learner["invariant_held64_median"],
                         "iqr": learner["invariant_held64_iqr"], "held64_by_run_seed": learner["held64_by_run_seed"],
                         "run_seeds": learner["run_seeds"], "budget_ok": learner["budget_ok"], "exp_id": EXP}
                        if learner is not None else {"status": "not_run"}),
            "status": "control"}


def job(ctx, gen_seeds, learner_pressures=("train8_held64",), run_seeds=tuple(range(I.MIN_RUNS)), gens=None,
        batch=None, archive_url=I.ARCHIVE_URL, elites_dir=str(I.ELITES_DIR)):
    """Per gen_seed: one suite_cheap row per pressure, the learner's run rows for each pressure in
    learner_pressures, then one floor_suite row per pressure. Resumable (F9) between learner generations."""
    import redis
    r = redis.Redis.from_url(archive_url)
    st = ctx.load_checkpoint() or {"done": {}, "cur": None, "cheap": {}, "suite": []}
    for gs in [int(x) for x in gen_seeds]:
        if str(gs) not in st["cheap"]:
            cheap = cheap_parts(gs)
            for p, c in cheap.items():
                ctx.emit({"kind": "suite_cheap", "world": f"w{gs}", "gen_seed": gs, "pressure": p, **c,
                          "status": "control"})
            st["cheap"][str(gs)] = cheap
            if hasattr(ctx, "checkpoint"):               # the gate search is the slow cheap part: keep it
                ctx.checkpoint(st)
        cheap = st["cheap"][str(gs)]
        for p in F.PRESSURES:
            if [gs, p] in st["suite"]:
                continue
            learner = None
            if p in learner_pressures:
                runs = I.learner_cell(ctx, st, r, gs, p, run_seeds, gens, batch, elites_dir)
                learner = I.summary(runs)
            ctx.emit(suite_row(gs, p, cheap[p], learner))
            st["suite"].append([gs, p])

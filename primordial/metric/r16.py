"""Operator 16 re-screen (SWARM_R4 s9, builder G): every baseline and stochastic floor part at >= 32 run seeds
pooled over 4 RNG families (4200, 2101, 3303, 5501; 8 run seeds each), read with the shared readout top1_train.

Jobs (F7 worker, F9-resumable):
  J1 floors_job     per world: the deterministic parts (abstain, best constant, gate) re-run and checked against
                    the committed stage 1 rows; uniform random over 32 policy streams PCG64([F, ps, gen_seed]);
                    the train8 input-invariant learner over 32 runs. Emits r16_det, r16_random, the learner run
                    rows, floor_invariant_r16 (train8) and one floor_suite_r16 row per pressure.
  J2 baseline_job   per cell, the float linear baseline over 32 runs (baseline.baseline_run, rng_family) ->
                    baseline_r16 rows. Order: order_r16 (w13 train128 first, then gate headroom).
  J3 learner128_job per cleared cell, the train128 learner over 32 runs -> floor_invariant_r16 (train128).

No 8-seed value, archive or row is reused: every run is a new key (g-r16-*) and a new elites file.

    python -m primordial.fabric.worker submit G primordial.metric.r16:floors_job --exp G-R16-floors \\
        --rows primordial/ledger/rows/G/G-R16-floors.jsonl --ttl-cpu-s S --kwargs '{"gen_seeds": [13, 7]}'
"""
from __future__ import annotations

import json
import pathlib

from primordial.metric import baseline as B
from primordial.metric import floors as F
from primordial.metric import invariant as I
from primordial.metric import screen as SC
from primordial.metric import suite as SU

ROOT = pathlib.Path(__file__).resolve().parents[2]
FAMILIES = B.FAMILIES
RUN_SEEDS = tuple(range(B.R16_PER_FAMILY))
STAGE1 = "primordial/ledger/rows/G/G-R4-3-stage1.jsonl"
DATA = pathlib.Path("C:/Users/jcrai/lab/pm-data/G")
ELITES_BASE, ELITES_LEARN = DATA / "G-R16-baseline", DATA / "G-R16-learner"
W13 = (13, "train128_held64")


def _rows(path) -> list[dict]:
    p = pathlib.Path(path)
    p = p if p.is_absolute() else ROOT / p
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []


def stage1_suite(path=STAGE1) -> dict:
    return {(int(x["gen_seed"]), x["pressure"]): x for x in _rows(path) if x.get("kind") == "floor_suite"}


def order_r16(stage1=STAGE1, first=W13) -> list[list]:
    """All stage 1 cells: `first` (w13 train128), then gate headroom descending, gen_seed, pressure.
    The headroom uses only the deterministic parts' floor (abstain/best constant; stage 1 had no random or
    learner floor above them) and the gate, which J1 re-checks."""
    s = stage1_suite(stage1)
    rest = sorted((k for k in s if k != tuple(first)), key=lambda k: SC.order_key(s[k]))
    return [list(first)] + [list(k) for k in rest] if tuple(first) in s else [list(k) for k in rest]


def random_pooled(gen_seed: int, families=FAMILIES, policy_seeds=RUN_SEEDS) -> dict:
    """Uniform random floor part over len(families) x len(policy_seeds) policy streams, pooled like a baseline."""
    from primordial.qd import e4_run as E4
    spec = E4.Spec(gen_seed)
    runs = []
    for fam in families:
        vals = F.random_scores(spec, F.HELD64, policy_seeds, rng_family=fam)
        runs += [{"rng_family": int(fam), "run_seed": int(ps), "held64_per_seed": float(v), "readout": "policy"}
                 for ps, v in zip(policy_seeds, vals)]
    return {"kind": "r16_random", "world": f"w{gen_seed}", "gen_seed": gen_seed,
            **B.pooled_stats(runs, min_runs=len(families) * len(policy_seeds), min_families=len(families),
                             per_family=len(policy_seeds))}


def det_check(gen_seed: int, stage1: dict) -> list[dict]:
    """Deterministic parts re-run (suite.cheap_parts) and compared with the committed stage 1 rows, per pressure."""
    cheap = SU.cheap_parts(gen_seed)
    out = []
    for p, c in cheap.items():
        old = stage1.get((gen_seed, p))
        parts = {k: c["parts"][k] for k in ("abstain", "best_constant")}
        match = None if old is None else bool(
            all(parts[k] == old["floor_parts"][k] for k in parts) and c["gate_held64"] == old["gate_held64"])
        out.append({"kind": "r16_det", "world": f"w{gen_seed}", "gen_seed": gen_seed, "pressure": p, **parts,
                    "gate_held64": c["gate_held64"], "gate": c["gate"], "matches_stage1": match,
                    "stage1": None if old is None else {"abstain": old["floor_parts"]["abstain"],
                                                         "best_constant": old["floor_parts"]["best_constant"],
                                                         "gate_held64": old["gate_held64"]}})
    return out


def _stats(s: dict) -> dict:
    return {k: s[k] for k in ("n_runs", "families", "n_per_family")} | {"readout": s["readout"], "median": s.get(
        "median", s.get("invariant_held64_median"))}


def floor_row(gs: int, p: str, det: dict, rnd: dict, learner: dict | None) -> dict:
    parts = {"abstain": det["abstain"], "best_constant": det["best_constant"],
             "uniform_random_median": rnd["median"],
             "input_invariant_learner": None if learner is None else learner["invariant_held64_median"]}
    stats = {"uniform_random_median": _stats(rnd)}
    if learner is not None:
        stats["input_invariant_learner"] = _stats(learner)
    return {"kind": "floor_suite_r16", "world": f"w{gs}", "gen_seed": gs, "pressure": p, "floor_parts": parts,
            **SU.floor_of_parts(parts), "gate_held64": det["gate_held64"], "floor_stats": stats,
            "det_matches_stage1": det["matches_stage1"],
            "learner": ({"status": "run", "median": learner["invariant_held64_median"],
                         "iqr": learner["invariant_held64_iqr"], "held64_by_run": learner["held64_by_run"],
                         "n_runs": learner["n_runs"], "families": learner["families"],
                         "n_per_family": learner["n_per_family"], "readout": learner["readout"],
                         "budget_ok": learner["budget_ok"]}
                        if learner is not None else {"status": "not_run"}),
            "status": "control"}


def floors_job(ctx, gen_seeds, families=FAMILIES, run_seeds=RUN_SEEDS, learner_gens=None, learner_batch=None,
               archive_url=I.ARCHIVE_URL, elites_dir=str(ELITES_LEARN), stage1_rows=STAGE1):
    """J1. Per world: r16_det (x2 pressures), r16_random, train8 learner runs + floor_invariant_r16, then
    floor_suite_r16 (x2 pressures)."""
    import redis
    r = redis.Redis.from_url(archive_url)
    st = ctx.load_checkpoint() or {"done": {}, "cur": None, "det": {}, "rand": {}, "learn": {}, "rows": []}
    stage1 = stage1_suite(stage1_rows)
    kw = dict(min_runs=len(families) * len(run_seeds), min_families=len(families), per_family=len(run_seeds))
    for gs in [int(x) for x in gen_seeds]:
        g = str(gs)
        if g in st["rows"]:
            continue
        if g not in st["det"]:
            dets = det_check(gs, stage1)
            for d in dets:
                ctx.emit({**d, "status": "control"})
            st["det"][g] = {d["pressure"]: d for d in dets}
            ctx.checkpoint(st)
        if g not in st["rand"]:
            st["rand"][g] = random_pooled(gs, families, run_seeds)
            ctx.emit({**st["rand"][g], "status": "control"})
            ctx.checkpoint(st)
        if g not in st["learn"]:
            runs = I.learner_cell(ctx, st, r, gs, "train8_held64", run_seeds, learner_gens, learner_batch, elites_dir,
                                  families=list(families))
            st["learn"][g] = I.pooled_summary(runs, **kw)
            ctx.emit({**st["learn"][g], "status": "control"})
            ctx.checkpoint(st)
        for p in F.PRESSURES:
            ctx.emit(floor_row(gs, p, st["det"][g][p], st["rand"][g], st["learn"][g] if p == "train8_held64" else None))
        st["rows"].append(g)
        ctx.checkpoint(st)


def baseline_job(ctx, cells, families=FAMILIES, run_seeds=RUN_SEEDS, gens=None, batch=None,
                 archive_url=B.ARCHIVE_URL, elites_dir=str(ELITES_BASE)):
    """J2. Per (gen_seed, pressure) in the given order: 32 run rows (oracle on the first family's run seed 0), then
    one baseline_r16 row."""
    import redis
    r = redis.Redis.from_url(archive_url)
    st = ctx.load_checkpoint() or {"done": {}, "cur": None, "cells": []}
    kw = dict(min_runs=len(families) * len(run_seeds), min_families=len(families), per_family=len(run_seeds))
    for gs, p in cells:
        key = f"{int(gs)}|{p}"
        if key in st["cells"]:
            continue
        runs = B.baseline_cell(ctx, st, r, int(gs), p, run_seeds, gens, batch, elites_dir, families=list(families))
        ctx.emit({**B.pooled_summary(runs, **kw), "status": "control"})
        st["cells"].append(key)
        ctx.checkpoint(st)


def learner128_job(ctx, cells, families=FAMILIES, run_seeds=RUN_SEEDS, gens=None, batch=None,
                   archive_url=I.ARCHIVE_URL, elites_dir=str(ELITES_LEARN)):
    """J3. The train128 input-invariant learner over 32 runs for each cleared (gen_seed, pressure)."""
    import redis
    r = redis.Redis.from_url(archive_url)
    st = ctx.load_checkpoint() or {"done": {}, "cur": None, "cells": []}
    kw = dict(min_runs=len(families) * len(run_seeds), min_families=len(families), per_family=len(run_seeds))
    for gs, p in cells:
        key = f"{int(gs)}|{p}"
        if key in st["cells"]:
            continue
        runs = I.learner_cell(ctx, st, r, int(gs), p, run_seeds, gens, batch, elites_dir, families=list(families))
        ctx.emit({**I.pooled_summary(runs, **kw), "status": "control"})
        st["cells"].append(key)
        ctx.checkpoint(st)

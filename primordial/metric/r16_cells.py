"""G-R6-2 (round 6 R6-BUILD, builder G): the R16 re-screen resumed as PER-CELL checkpointable jobs.

Operator 16 rule unchanged: every baseline and stochastic floor part at runs_total 32 / rng_family_count 4 /
runs_per_family 8, read top1_train, verdict under gate_in|HOLD. Round 6 changes only how the parked screen resumes:

  ORDER (SWARM_R6 O4, fixed before T+0)
    floor_remainder  the cells whose R16 baseline is already committed but whose R16 floors are not (J1 stopped
                     after w13), sorted -- they need only the cheap floor work to become complete;
    order            numpy PCG64(20260916).permutation over the SORTED list of the unscreened cells (no R16 baseline
                     row committed). Not headroom, not cost.
    The order file is committed before T+0 (gate item 24) and never regenerated with another seed.

  ONE JOB PER CELL (gen_seed, pressure), job_key 'g-r16-cell-w<gs>-<pressure>' (stable: a resubmission resumes the
  same F9 checkpoint). A cell job:
    1. pre-fills its done-run table from COMMITTED R16 run rows of that cell (run keys are deterministic, so the
       runs J1/J2 already committed -- w7's train8 learner 26 runs, w34 train128's baseline 15 runs -- are reused
       exactly and never re-run);
    2. deterministic parts (abstain, best constant, gate) for its world, checked against stage 1 (r16_det);
    3. uniform random pooled (32 policy streams, no archive);
    4. train8 cell only: the train8 input-invariant learner pooled (the train128 cell never runs it: no shared
       archive keys between two cells of one world);
    5. floor_suite_r16 row; then the baseline pooled unless a baseline_r16 row is already committed;
    6. train128 cell whose floor is a bound that can change a verdict (screen.needs_learner): the train128 learner,
       IF its CPU estimate <= PRODUCTION cpu_budget_s 14400; otherwise the cell is PENDING and a
       PRODUCTION_CANDIDATE is filed with the estimate (SWARM_R6 s2), never run;
    7. an r16_cell row with the cell's status.
  The partial worlds_r4/v2 (partial_v2) records every cell that is not complete as UNSCREENED -- never CULLED.

  REPLICATION TRIGGER (G-R6-3, SWARM_R6 s6: code calls it, A never relays): the LAST step of every cell_job, after
  its r16_cell row, calls replication.publish_new_survivors(r, partial_v2(extra_rows=this job's rows),
  source='r16_cell_job'). Inside the F7 worker a job's rows reach the rows file only after the job returns, so the
  job's own floor / baseline / learner rows are merged over the committed rows: a new survivor publishes from its own
  job (idempotent per cell key; every later job re-reads all committed cells too). Guarded by
  replication.frozen_code_intact(): if B-R5-1's frozen code changed, nothing is published and one
  REPLICATION_RECIPE_CHANGED event goes to pm:events. Either way a replication_check row records the outcome.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

from primordial.metric import baseline as B
from primordial.metric import floors as F
from primordial.metric import invariant as I
from primordial.metric import r16 as R
from primordial.metric import screen as SC
from primordial.metric import worlds as WR

ROOT = R.ROOT
ORDER_SEED = 20260916
ORDER_FILE = ROOT / "roles" / "Nestor" / "sidequests" / "graphworld" / "R16_ORDER_R6.json"
EXP = "G-R16-cell"
ROWS = "primordial/ledger/rows/G/G-R16-cells.jsonl"
FN = "primordial.metric.r16_cells:cell_job"
PRESSURES = tuple(F.PRESSURES)

# Measured rates (committed R16 rows, lane G alone, 5 threads): J2 baseline qd wall per run per unit T*S; J2
# CPU/wall; J1 train8 learner wall per run per unit T*S; J3 w13 train128 learner 12,031 CPU-s for 32 runs, T*S 32.
BASE_WALL_PER_RUN_TS = {"train128_held64": 0.1163, "train8_held64": 0.0041}
LEARN8_WALL_PER_RUN_TS = 0.0424
CPU_PER_WALL = 11231.83 / 2302.53
LEARN128_CPU_PER_TS_32RUNS = 12030.94 / 32
CPU_BUDGET_S = 14400.0                      # SWARM_R6 s2 PRODUCTION cpu_budget_s per job
EVENTS = "pm:events"                        # F's event stream (envelope.EVENTS)
RECIPE_CHANGED = "REPLICATION_RECIPE_CHANGED"
PREDICATE_ID = "G-R16-SCREEN"      # envelope.validate refuses a None/empty predicate_id (all 73 R6 submits at 11:01)


def ts_of(gen_seed: int) -> int:
    from primordial.qd import e4_run as E4
    s = E4.Spec(int(gen_seed))
    return int(s.T * s.S)


def all_cells() -> list[tuple[int, str]]:
    return sorted(R.stage1_suite())


def done_baselines(baseline_rows=R.ROWS["baseline"]) -> set:
    return {(int(x["gen_seed"]), x["pressure"]) for x in R._rows(baseline_rows) if x.get("kind") == "baseline_r16"}


def done_floors(rows=(R.ROWS["floors"], ROWS)) -> set:
    out = set()
    for path in rows:
        out |= {(int(x["gen_seed"]), x["pressure"]) for x in R._rows(path) if x.get("kind") == "floor_suite_r16"}
    return out


def build_order(seed: int = ORDER_SEED, baseline_rows=R.ROWS["baseline"], floor_rows=(R.ROWS["floors"], ROWS)) -> dict:
    cells = all_cells()
    have_base, have_floor = done_baselines(baseline_rows), done_floors(floor_rows)
    unscreened = sorted(c for c in cells if c not in have_base)
    remainder = sorted(c for c in cells if c in have_base and c not in have_floor)
    perm = np.random.Generator(np.random.PCG64(seed)).permutation(len(unscreened))
    return {"schema": "r16_order_r6/v1", "seed": seed, "rng": "numpy.random.Generator(PCG64(seed)).permutation(len(unscreened))",
            "unscreened_sorted": [list(c) for c in unscreened], "permutation": [int(i) for i in perm],
            "order": [list(unscreened[i]) for i in perm], "floor_remainder": [list(c) for c in remainder],
            "complete": [list(c) for c in cells if c in have_base and c in have_floor],
            "counts": {"cells": len(cells), "unscreened": len(unscreened), "floor_remainder": len(remainder)},
            "rule": "SWARM_R6 O4: seeded permutation of the unscreened cells, not headroom, not cost; floor remainder first"}


def write_order(doc: dict, path=ORDER_FILE) -> pathlib.Path:
    p = pathlib.Path(path)
    if p.exists():
        old = json.loads(p.read_text(encoding="utf-8"))
        if old.get("seed") != doc["seed"] or old.get("order") != doc["order"]:
            raise ValueError(f"{p} already holds a different order; the committed order is never regenerated")
        return p
    p.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    return p


def job_key(gen_seed: int, pressure: str) -> str:
    return f"g-r16-cell-w{int(gen_seed)}-{pressure}"


def estimates(gen_seed: int, pressure: str, runs: int = 32) -> dict:
    ts = ts_of(gen_seed)
    base_cpu = runs * BASE_WALL_PER_RUN_TS[pressure] * ts * CPU_PER_WALL
    learn8_cpu = runs * LEARN8_WALL_PER_RUN_TS * ts * CPU_PER_WALL if pressure == "train8_held64" else 0.0
    learn128_cpu = LEARN128_CPU_PER_TS_32RUNS * ts * runs / 32 if pressure == "train128_held64" else 0.0
    return {"t_x_s": ts, "baseline_cpu_s": base_cpu, "learner8_cpu_s": learn8_cpu, "learner128_cpu_s": learn128_cpu,
            "learner128_admissible": learn128_cpu <= CPU_BUDGET_S, "basis": "R16 J1/J2/J3 committed walls, 5 threads"}


def prefill_done(st: dict, gen_seed: int, pressure: str, paths=(R.ROWS["floors"], R.ROWS["baseline"], R.ROWS["learner128"], ROWS)) -> int:
    """Committed R16 run rows of this cell -> st['done'] under their deterministic run keys. Returns rows added."""
    n = 0
    for path in paths:
        for x in R._rows(path):
            if x.get("kind") != "run" or "rng_family" not in x or int(x["gen_seed"]) != int(gen_seed):
                continue
            if x.get("family") == "linear":
                if x["pressure"] != pressure:
                    continue
                k = B.run_key(x["gen_seed"], x["pressure"], x["run_seed"], x["rng_family"])
            else:
                if x["pressure"] != ("train8_held64" if pressure == "train8_held64" else pressure):
                    continue
                k = I.run_key(x["gen_seed"], x["pressure"], x["run_seed"], x["rng_family"])
            if k not in st["done"]:
                st["done"][k] = x
                n += 1
    return n


def _file_candidate(ctx, stub: dict) -> dict:
    """F-R6-3 contract (F 1789479761855-0): the stub goes on pm:production_candidates (its XADD id is the stub_id), then
    envelope.file_candidate(r, stub_id, measured_cost, basis) files it once. -> {stub_id, filing}."""
    try:
        from primordial.fabric import envelope as EN
        stub_id = ctx.r.xadd(EN.CANDIDATES, {"json": json.dumps(stub, sort_keys=True)})
        filing = None
        if hasattr(EN, "file_candidate"):
            filing = EN.file_candidate(ctx.r, stub_id, stub.get("measured_cost") or {}, stub.get("basis") or "")
        return {"stub_id": stub_id, "filing": filing}
    except Exception as e:                                     # never lose the cell on a filing error: record it
        return {"stub_id": None, "filing": {"ok": False, "reason": f"FILE_FAILED:{type(e).__name__}"}}


def replication_check(ctx, extra_rows, r=None, source: str = "r16_cell_job") -> dict:
    """G-R6-3 wiring: publish new SURVIVED cells (frozen B-R5-1 recipe) from the partial eligibility doc = committed
    R16 rows + this job's rows. Refuses (event, no record) if the recipe's frozen code changed."""
    from primordial.metric import replication as RP
    r = ctx.r if r is None else r
    if not RP.frozen_code_intact():
        ev = {"event": RECIPE_CHANGED, "lane": "G", "source": source, "recipe": RP.RECIPE_ID,
              "frozen_code_sha": RP.RECIPE_CODE_SHA, "files": list(RP.RECIPE_FILES)}
        eid = r.xadd(EVENTS, {"event": RECIPE_CHANGED, "json": json.dumps(ev, sort_keys=True)})
        out = {"published": [], "refused": RECIPE_CHANGED, "event_id": eid}
    else:
        recs = RP.publish_new_survivors(r, partial_v2(extra_rows=extra_rows), source=source)
        out = {"published": [x["cell"] for x in recs], "stream_ids": [x.get("stream_id") for x in recs], "refused": None}
    ctx.emit({"kind": "replication_check", "source": source, **out, "status": "control"})
    return out


def cell_job(ctx, gen_seed, pressure, families=R.FAMILIES, run_seeds=R.RUN_SEEDS, gens=None, batch=None,
             learner_gens=None, learner_batch=None, base_archive=B.ARCHIVE_URL, learn_archive=I.ARCHIVE_URL,
             base_elites=str(R.ELITES_BASE), learn_elites=str(R.ELITES_LEARN), stage1_rows=R.STAGE1,
             prefill_paths=None, cpu_budget_s=CPU_BUDGET_S, replication_r=None):
    import redis
    gs, p = int(gen_seed), str(pressure)
    rb, rl = redis.Redis.from_url(base_archive), redis.Redis.from_url(learn_archive)
    st = ctx.load_checkpoint()
    if st is None:
        st = {"done": {}, "cur": None, "stage": "start"}
        st["prefilled"] = prefill_done(st, gs, p, **({} if prefill_paths is None else {"paths": prefill_paths}))
    kw = dict(min_runs=len(families) * len(run_seeds), min_families=len(families), per_family=len(run_seeds))
    if "det" not in st:
        st["det"] = {d["pressure"]: d for d in R.det_check(gs, R.stage1_suite(stage1_rows))}
        ctx.emit({**st["det"][p], "status": "control", "cell_job": job_key(gs, p)})
        ctx.checkpoint(st)
    if "rand" not in st:
        st["rand"] = R.random_pooled(gs, families, run_seeds)
        ctx.emit({**st["rand"], "status": "control", "cell_job": job_key(gs, p)})
        ctx.checkpoint(st)
    learner8 = None
    if p == "train8_held64":
        if "learn8" not in st:
            runs = I.learner_cell(ctx, st, rl, gs, p, run_seeds, learner_gens, learner_batch, learn_elites, families=list(families))
            st["learn8"] = I.pooled_summary(runs, **kw)
            ctx.emit({**st["learn8"], "status": "control"})
            ctx.checkpoint(st)
        learner8 = st["learn8"]
    if "floor" not in st:
        st["floor"] = R.floor_row(gs, p, st["det"][p], st["rand"], learner8)
        ctx.emit({**st["floor"], "cell_job": job_key(gs, p)})
        ctx.checkpoint(st)
    if "base" not in st:
        committed = [x for x in R._rows(R.ROWS["baseline"]) if x.get("kind") == "baseline_r16"
                     and (int(x["gen_seed"]), x["pressure"]) == (gs, p)]
        if committed:
            st["base"] = committed[-1]
        else:
            runs = B.baseline_cell(ctx, st, rb, gs, p, run_seeds, gens, batch, base_elites, families=list(families))
            st["base"] = B.pooled_summary(runs, **kw)
            ctx.emit({**st["base"], "status": "control"})
        ctx.checkpoint(st)
    fl, base = st["floor"], st["base"]
    status, pc, learner128 = "complete", None, None
    if fl["floor_is_bound"] and SC.needs_learner(fl["floor"], fl["gate_held64"], float(base["ci95"][0])):
        est = estimates(gs, p, runs=len(families) * len(run_seeds))
        if est["learner128_cpu_s"] > cpu_budget_s:
            status = "PENDING"
            if "pc" not in st:
                st["pc"] = _file_candidate(ctx, {
                    "kind": "PRODUCTION_CANDIDATE", "status": "STUB", "lane": "G", "job_key": job_key(gs, p),
                    "question": f"R16 train128 input-invariant learner for w{gs} {p} (decides this cell's verdict)",
                    "reasons": ["CPU_BUDGET_OVER_CEILING"], "measured_cost": est,
                    "basis": "estimate from committed R16 J3 CPU (12,031 CPU-s for 32 runs at T*S 32), scaled by T*S",
                    "requested_cost": {"cpu_budget_s": est["learner128_cpu_s"]}, "ceiling": {"cpu_budget_s": cpu_budget_s}})
                ctx.checkpoint(st)
            pc = st["pc"]
        else:
            if "learn128" not in st:
                runs = I.learner_cell(ctx, st, rl, gs, p, run_seeds, learner_gens, learner_batch, learn_elites,
                                      families=list(families))
                st["learn128"] = I.pooled_summary(runs, **kw)
                ctx.emit({**st["learn128"], "status": "control"})
                ctx.checkpoint(st)
            learner128 = st["learn128"]
    rec = WR.cell(fl, base, learner128, est_runs=len(families) * len(run_seeds))
    ctx.emit({"kind": "r16_cell", "world": f"w{gs}", "gen_seed": gs, "pressure": p, "job_key": job_key(gs, p),
              "status_cell": status, "production_candidate": pc, "pending": rec.get("pending"),
              "verdicts": rec["verdicts"], "floor": rec["floor"], "gate_held64": rec["gate_held64"],
              "baseline_ci95": base["ci95"], "prefilled_runs": st.get("prefilled", 0), "status": "control"})
    replication_check(ctx, [fl, base] + ([learner128] if learner128 is not None else []), r=replication_r)


def envelope_for(gen_seed: int, pressure: str, runs: int = 32) -> dict:
    est = estimates(gen_seed, pressure, runs)
    cpu = est["baseline_cpu_s"] + est["learner8_cpu_s"] + (est["learner128_cpu_s"] if est["learner128_admissible"] else 0.0)
    return {"campaign_stage": "PRODUCTION", "wall_budget_s": 2400, "cpu_budget_s": min(CPU_BUDGET_S, round(cpu * 1.25 + 60)),
            "gpu_budget_s": 0, "expected_output_rows": 3 + runs * (3 if pressure == "train8_held64" else 2),
            "checkpointable": True, "required_controls": ["floor_suite", "det_matches_stage1"],
            "required_oracles": ["world_oracle", "fused_eq_numpy"], "cohort": "G", "predicate_id": PREDICATE_ID,
            "experiment_class": "R16_SCREEN_CELL"}


def plan_jobs(order_doc: dict) -> list[dict]:
    """The submission plan in order (floor remainder first, then the seeded order). Nothing is submitted here."""
    out = []
    for gs, p in [tuple(c) for c in order_doc["floor_remainder"]] + [tuple(c) for c in order_doc["order"]]:
        out.append({"lane": "G", "fn": FN, "exp_id": EXP, "rows": ROWS, "job_key": job_key(gs, p),
                    "kwargs": {"gen_seed": gs, "pressure": p}, "envelope": envelope_for(gs, p),
                    "estimate": estimates(gs, p)})
    return out


def partial_v2(cell_rows=ROWS, floors=R.ROWS["floors"], baseline=R.ROWS["baseline"], learner128=R.ROWS["learner128"],
               extra_rows=()) -> dict:
    """worlds_r4/v2 over ALL stage 1 cells: complete cells from R16 rows (legacy R16 files + per-cell rows + extra_rows,
    i.e. a running job's own rows not yet committed); every other cell is recorded UNSCREENED under every variant --
    never CULLED, never NOT_REACHED."""
    extra = list(extra_rows)
    frows = R._rows(floors) + R._rows(cell_rows) + extra
    brows = R._rows(baseline) + R._rows(cell_rows) + extra
    lrows = R._rows(learner128) + R._rows(cell_rows) + extra
    fl = {(int(x["gen_seed"]), x["pressure"]): x for x in frows if x.get("kind") == "floor_suite_r16"}
    base = {(int(x["gen_seed"]), x["pressure"]): x for x in brows if x.get("kind") == "baseline_r16"}
    lrn = {(int(x["gen_seed"]), x["pressure"]): x for x in lrows
           if x.get("kind") == "floor_invariant_r16" and x["pressure"] == "train128_held64"}
    recs, unscreened = [], []
    for key in all_cells():
        if key in fl and key in base:
            recs.append(WR.cell(fl[key], base[key], lrn.get(key), est_runs=32,
                                sources={"rows": [str(floors), str(baseline), str(learner128), str(cell_rows)]}))
        else:
            unscreened.append(key)
    doc = WR.build(recs, commit="", max_survivors=None, schema=WR.SCHEMA_V2) if recs else {
        "schema": WR.SCHEMA_V2, "q1_floor_policy": SC.ACTIVE[0], "q2_policy": SC.ACTIVE[1], "cells": [],
        "variants": [SC.vkey(*v) for v in SC.VARIANTS]}
    for gs, p in unscreened:
        doc["cells"].append({"world": f"w{gs}", "gen_seed": gs, "pressure": p, "stage": 0, "baseline": None,
                             "verdict": "UNSCREENED", "cull_reason": None,
                             "verdicts": {SC.vkey(*v): {"verdict": "UNSCREENED", "cull_reason": None, "floor": None}
                                          for v in SC.VARIANTS}})
    doc["partial"] = True
    doc["unscreened"] = [[gs, p] for gs, p in unscreened]
    doc["coverage"] = {"cells": len(all_cells()), "complete": len(recs), "unscreened": len(unscreened)}
    return doc

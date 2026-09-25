"""D-R7-1 (ANOM-1789490583451-0, prompts_r7/D.md item 1): C-R6-AP-01's anti-prior-arm PASS -- tucker / nk_stub /
cpu_ttl / graphblas cut to TTL = control CPU / 5 (75-91 of 400 generations) scored held median 2249154.38 >= bar
2226419.05 (control 2243838.29 - 0.5 IQR 34838.47); sealed prior 0.10.

Seen before this predicate: C's rows show the TTL binds on GENERATIONS (cell gens_done 75-91, control 400; cell loop
CPU 2.64-2.69 vs TTL 2.6281), and D-R6-8 (receipt 1789490865360-0): control train > cell train 32/32 pairs, control held
> cell held 17/32. So the question left is whether the cut binds on HELD-OUT fitness, and why not. A no-rows smoke check
replayed C's cell stream (4200, 0) at 84 gens on lane D's Redis: gens, cells, train top1 and held top1 equal C's row
exactly at the default thread pools and at one BLAS thread.

Zero new search streams: C's own streams. For each (family, run seed), 4 families x 8 = 32:
  trajectory  C's CONTROL stream (GA PCG64([F, rs, 1, 6101]), sampler [F+1, rs, 1, 6101]) run to 400 generations, with
              C's exact top1_train readout (all elites re-evaluated on train, numpy NK recount; top1 held on 64 landscapes)
              read at checkpoints g in {1, 10, 25, 50, 100, 200, 400} and at m = the paired cell run's gens_done. Reading
              the archive after generation g inside one trajectory is the run stopped at g (same RNG path; control
              below checks it).
  replay      C's CELL stream (arm 0) through C's own run() for exactly its committed gens_done, no TTL.

Rule (fixed before any sweep value is read). B = C's bar, recomputed from C's 32 control rows.
  I1  32 trajectories and 32 replays, 8 per family; every trajectory's g=400 readout equals C's control row and every
      replay equals C's cell row (gens_done, archive_cells, train_fit_top1, train_per_landscape_top1,
      held_per_landscape_top1 exactly); B recomputed == C's summary bar to 0.01. Else INDETERMINATE.
  control checkpoint_equals_stopped_run (binding): C's run() on control stream (4200, 0) stopped at its m equals the
      trajectory's m readout exactly. Else INDETERMINATE.
  H1 = median_32 held(g=1); Hm = median_32 held(m); s = #runs with held(400) > held(m) on the same stream.
  NO_SEARCH_SIGNAL    H1 >= B                     (the best-of-128 random init already clears the bar)
  STREAM_DRAW         H1 < B and Hm < B           (the control's streams at the cell's generation count do not clear
                                                   the bar: the PASS rests on the cell streams' draw)
  SATURATED           H1 < B, Hm >= B, s <= 21    (held-out stops responding by ~m generations: 400 > m in at most
                                                   21/32, the Binomial(32, .5) 95th percentile)
  BAR_ABSORBS_GAIN    H1 < B, Hm >= B, s >= 26    (held still rises m -> 400 in >= 81% of runs, but by less than the
                                                   0.5 IQR tolerance of C's bar)
  MIXED               otherwise
Reported, not judged: per-checkpoint median / IQR of train and held; g_sat = first checkpoint whose held median >= B;
median held(400) - held(m); median cell-stream held - control-stream held(m) (stream effect at matched gens); held minus
C's random-bits mean at g=1, m, 400.

    worker.submit("D", "primordial.cohorts.d.r7_1_ap01_gens_sweep:job", EXP, ROWS, 1800, envelope={...PRODUCTION...})
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import time

import numpy as np

from primordial.cohorts.c import r6_ap01_tucker_nk_cpu_ttl_graphblas as C

EXP = "D-R7-1-ap01-gens-sweep"
PREDICATE_ID = EXP
ANOMALY = "1789490583451-0"
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = f"primordial/ledger/rows/D/{EXP}.jsonl"
SRC_ROWS = "primordial/ledger/rows/C/C-R6-AP-01-tucker-nk-cpu-ttl-graphblas.jsonl"
ARCHIVE_URL = "redis://127.0.0.1:6393/0"          # lane D substrate
FAMILIES = C.FAMILIES
GENS = 400
CHECKPOINTS = (1, 10, 25, 50, 100, 200, 400)
FIELDS = ("gens_done", "archive_cells", "train_fit_top1", "train_per_landscape_top1", "held_per_landscape_top1")
S_SATURATED, S_ABSORBS = 21, 26


def load(text: str):
    rows = [json.loads(l) for l in text.splitlines() if l.strip()]
    runs = {(x["arm"], int(x["family"]), int(x["run_seed"])): x for x in rows
            if x.get("kind") == "run" and x.get("arm") in ("cell", "control")}
    ref = next((x for x in rows if x.get("kind") == "reference"), {})
    summ = [x for x in rows if x.get("kind") == "summary"]
    return runs, ref, (summ[-1] if summ else {})


def bar_of(control_held) -> float:
    q = np.percentile(control_held, [25, 50, 75])
    return float(q[1] - 0.5 * (q[2] - q[0]))


def readout(arch, train, held) -> dict:
    """C's post-loop readout (r6_ap01 run()), without clearing the archive."""
    el = arch.dump()
    order = sorted(el.values(), key=lambda v: (-v[0], v[1]))
    eg = np.frombuffer(b"".join(v[1] for v in order), np.uint8).reshape(-1, C.GLEN)
    ef = np.array([v[0] for v in order], np.int64)
    _, _, bits_e = C.evaluate(eg, train)
    ref_e = C.ref_fit(bits_e, train)
    fh = C.evaluate(eg[:1], held)[0]
    return {"archive_cells": len(el), "train_fit_top1": int(ef[0]), "train_per_landscape_top1": float(ref_e[0].mean()),
            "held_per_landscape_top1": float(fh.mean()),
            "elites_mismatched": int((ref_e.sum(1) != ef).sum())}


def trajectory(r, family: int, rs: int, m: int, train, held, gens: int = GENS) -> dict:
    """C's control stream (arm 1) with readouts at CHECKPOINTS and at m; C's loop body, no TTL."""
    from primordial.qd.archive import LuaArchive
    rng = np.random.Generator(np.random.PCG64([family, rs, 1, 6101]))
    arch = LuaArchive(r, f"d-r7-1-{family}-{rs}-1", C.GLEN, sampler_seed=[family + 1, rs, 1, 6101])
    arch.clear()
    stops = sorted({g for g in CHECKPOINTS if g <= gens} | {m})
    out, c0 = {}, time.process_time()
    for gen in range(1, gens + 1):
        par = arch.sample(C.BATCH)
        g = C.init(rng, C.BATCH) if len(par) == 0 else C.mutate(rng, par)
        fit, cells, _ = C.evaluate(g, train)
        arch.insert(cells, fit.sum(1).astype(np.int32), g, np.zeros((C.BATCH, 2), np.uint32))
        if gen in stops:
            x = dict(readout(arch, train, held), gens_done=gen)
            if gen == m:
                out["m"] = x
            if gen in CHECKPOINTS:
                out[str(gen)] = x
    arch.clear()
    return {"family": family, "run_seed": rs, "m": m, "checkpoints": out, "cpu_s": round(time.process_time() - c0, 3)}


def same(a: dict, b: dict) -> bool:
    return all(a.get(k) == b.get(k) for k in FIELDS)


def decide(i1: bool, controls_ok: bool, runs: list[dict], bar: float) -> tuple[str, dict]:
    if not (i1 and controls_ok) or len(runs) != 32:
        return "INDETERMINATE", {}
    h1 = float(np.median([x["checkpoints"]["1"]["held_per_landscape_top1"] for x in runs]))
    hm = float(np.median([x["checkpoints"]["m"]["held_per_landscape_top1"] for x in runs]))
    s = int(sum(x["checkpoints"]["400"]["held_per_landscape_top1"] > x["checkpoints"]["m"]["held_per_landscape_top1"]
                for x in runs))
    stats = {"bar": bar, "H1": h1, "Hm": hm, "s_held400_gt_heldm": s}
    if h1 >= bar:
        return "NO_SEARCH_SIGNAL", stats
    if hm < bar:
        return "STREAM_DRAW", stats
    if s <= S_SATURATED:
        return "SATURATED", stats
    if s >= S_ABSORBS:
        return "BAR_ABSORBS_GAIN", stats
    return "MIXED", stats


def job(ctx, status="record"):
    import redis
    t0 = time.perf_counter()
    text = (ROOT / SRC_ROWS).read_text(encoding="utf-8")
    runs_c, ref, summ = load(text)
    r = redis.Redis.from_url(ARCHIVE_URL)
    train, held = C.Landscapes(C.TRAIN_SEEDS), C.Landscapes(C.HELD_SEEDS)
    todo = [(f, rs) for f in FAMILIES for rs in range(C.RUNS_PER_FAMILY)]
    st = ctx.load_checkpoint() or {"next": 0, "runs": [], "replays": [], "control": None}
    while st["next"] < len(todo):
        if ctx.should_pause():
            ctx.pause(st, completed_units=st["next"], remaining_units=len(todo) + 1 - st["next"])
        f, rs = todo[st["next"]]
        cell, ctrl = runs_c[("cell", f, rs)], runs_c[("control", f, rs)]
        x = trajectory(r, f, rs, int(cell["gens_done"]), train, held)
        x["reproduces_control_row"] = same(dict(x["checkpoints"]["400"]), ctrl)
        info, _ = C.run(r, f, rs, 0, int(cell["gens_done"]), None, train, held)
        rep = {k: info[k] for k in FIELDS}
        y = {"family": f, "run_seed": rs, **rep, "reproduces_cell_row": same(rep, cell)}
        st["runs"].append(x)
        st["replays"].append(y)
        ctx.emit({"kind": "trajectory", "exp": EXP, "status": status, "ts": round(time.time(), 3), **x})
        ctx.emit({"kind": "cell_replay", "exp": EXP, "status": status, "ts": round(time.time(), 3), **y})
        st["next"] += 1
        ctx.progress(st["next"], len(todo) + 1 - st["next"])
    if st["control"] is None:
        x0 = st["runs"][0]
        info, _ = C.run(r, x0["family"], x0["run_seed"], 1, x0["m"], None, train, held)
        st["control"] = {"family": x0["family"], "run_seed": x0["run_seed"], "gens": x0["m"],
                         "stopped_run": {k: info[k] for k in FIELDS},
                         "identical": same(info, x0["checkpoints"]["m"])}
        ctx.emit({"kind": "control", "exp": EXP, "status": "control", "name": "checkpoint_equals_stopped_run",
                  "ts": round(time.time(), 3), **st["control"]})
    runs, reps = st["runs"], st["replays"]
    per_fam = {str(f): sum(int(x["family"]) == f for x in runs) for f in FAMILIES}
    bar = bar_of([runs_c[("control", f, rs)]["held_per_landscape_top1"] for f, rs in todo])
    i1 = {"trajectories_32": len(runs) == 32, "replays_32": len(reps) == 32,
          "per_family_8": all(v == 8 for v in per_fam.values()),
          "g400_reproduces_control_rows": all(x["reproduces_control_row"] for x in runs),
          "replay_reproduces_cell_rows": all(y["reproduces_cell_row"] for y in reps),
          "elites_recount_clean": all(c["elites_mismatched"] == 0 for x in runs for c in x["checkpoints"].values()),
          "bar_matches_summary": abs(bar - float(summ.get("bar", np.nan))) < 0.01}
    ok = bool(st["control"]["identical"])
    decision, stats = decide(all(i1.values()), ok, runs, bar)
    rnd = float(ref.get("random_bits_mean_per_held_landscape", np.nan))
    keys = [str(g) for g in CHECKPOINTS] + ["m"]

    def q(g, k):
        v = np.percentile([x["checkpoints"][g][k] for x in runs], [25, 50, 75])
        return {"median": float(v[1]), "iqr": float(v[2] - v[0])}
    med = {g: {"train": q(g, "train_per_landscape_top1"), "held": q(g, "held_per_landscape_top1")} for g in keys}
    g_sat = next((int(g) for g in map(str, CHECKPOINTS) if med[g]["held"]["median"] >= bar), None)
    ctx.emit({"kind": "summary", "exp": EXP, "predicate_id": PREDICATE_ID, "anomaly": ANOMALY, "status": status,
              "ts": round(time.time(), 3), "source_rows": SRC_ROWS,
              "source_rows_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
              "runs_total": len(runs), "rng_family_count": len([f for f in per_fam if per_fam[f]]), "runs_per_family": 8,
              "families": list(FAMILIES), "n_per_family": per_fam, "checkpoints": list(CHECKPOINTS),
              "checks": {"I1": i1, "controls_ok": ok}, "controls": {"checkpoint_equals_stopped_run": st["control"]},
              "stats": stats, "decision": decision,
              "reported_not_judged": {
                  "by_checkpoint": med, "g_sat": g_sat,
                  "median_held400_minus_heldm": float(np.median([x["checkpoints"]["400"]["held_per_landscape_top1"]
                                                                 - x["checkpoints"]["m"]["held_per_landscape_top1"]
                                                                 for x in runs])),
                  "median_cellstream_minus_controlstream_at_m": float(np.median(
                      [runs_c[("cell", x["family"], x["run_seed"])]["held_per_landscape_top1"]
                       - x["checkpoints"]["m"]["held_per_landscape_top1"] for x in runs])),
                  "held_minus_random": {g: med[g]["held"]["median"] - rnd for g in ("1", "m", "400")},
                  "m_range": [min(x["m"] for x in runs), max(x["m"] for x in runs)]},
              "wall_s_segment": round(time.perf_counter() - t0, 3)})

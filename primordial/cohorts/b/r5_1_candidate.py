"""B-R5-1: the ONE Clause A attempt on w13 train128_held64 in round 5 (SWARM_R5 s5 B, prompts_r5/B.md).

Candidate: B's int4 linear + a4 nibble codebook (b1_qlinear.QLin(13, 4, 4)), 16 B vs the 200 B float linear baseline.
Round 4 claims on this cell are INVALIDATED (operator 15) and are not cited; only the saved elites are re-read.

Everything the verdict needs is read from code, never recomputed here:
  eligibility, floor, baseline, denominator   primordial.metric.eligibility (G-R5-4, R16 rows)
  readout                                    primordial.metric.readout top1_train (both sides of the fraction)
  sample rule                                qd_ledger.check_r4 CANDIDATE_N (runs_total 32, rng_family_count 4,
                                             runs_per_family 8); smaller -> label PILOT, the judge refuses
  seed convention                            baseline.seeds_of: mutation PCG64([F, rs, gs, n_train]), sampler
                                             [F+1, rs, gs, n_train], F in baseline.FAMILIES

Two jobs:
  job          the CANDIDATE_N run: 4 families, 8 run seeds each, at the M2 budget (800 gens, batch 128 on TRAIN128).
               Its measured cost (round 4 B-R4-5, same genome and budget: 63.7 CPU-s and 16.6 s wall per run) puts
               32 runs over the PILOT cpu_budget_s ceiling, so admission is expected to refuse it -> PRODUCTION_CANDIDATE.
  reread_job   PILOT: the saved round 4 int4_a4 archives (one RNG stream, run seeds 0..15) re-read under top1_train.
               runs_total 16, rng_family_count 1 -> labelled PILOT; the judge's CANDIDATE_N refusal is expected.

Every candidate row reports candidate_score, floor, baseline, progress_above_floor, bytes, wall, vram, and the
observation-use control: the selected elite re-scored with its weight matrix zeroed (bias + codebook kept, so the
policy can no longer read observations) plus E-T3's input_invariant count on the selected elite.

    python -m primordial.fabric.worker submit B primordial.cohorts.b.r5_1_candidate:job ...   (envelope required)
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import time

import numpy as np

from primordial.cohorts.b.b1_qlinear import QLin
from primordial.cohorts.b.r4_1_qladder import oracles as r4_oracles
from primordial.cohorts.e.oracles import brain_oracle_cheats
from primordial.metric import baseline as BL
from primordial.metric import eligibility as EL
from primordial.metric import floors as F
from primordial.metric import readout as RO
from primordial.metric import sample as SM
from primordial.metric.ci import median_ci
from primordial.ops import qd_ledger as QL
from primordial.qd.archive import LuaArchive, load_elites, save_elites
from primordial.soup.b6.fused import FusedRollout

EXP = "B-R5-1-cand-int4a4-w13-train128"
EXP_REREAD = "B-R5-2-reread-int4a4-w13-train128"
GS, PRESSURE, BITS, ACTS = 13, "train128_held64", 4, 4
FAMILIES = BL.FAMILIES
RUN_SEEDS = tuple(range(BL.R16_PER_FAMILY))
ARCHIVE_URL = "redis://127.0.0.1:6391/0"
ELITES_DIR = pathlib.Path("C:/Users/jcrai/lab/pm-data/B") / EXP
R4_STREAM = 4410        # round 4 B stream: mutation PCG64([4410, bits, A, rs, gs, n]), sampler 4411 -- one stream
R4_ROWS = ("primordial/ledger/rows/B/B-R4-4-int5-codebook-w13-train128.jsonl",
           "primordial/ledger/rows/B/B-R4-5-a4-replicate-w13-train128.jsonl")
VRAM = {"vram_mb": None, "vram_note": "CPU job (numba fused rollout); no GPU used"}


def scorer(q: QLin, zero_w: bool = False):
    """score_fn(raw [n, glen], seeds) -> per-seed mean HELD score. zero_w: the observation-use control."""
    def score(raw, seeds):
        (W, b), C = q.decode(q.unpack(np.asarray(raw, np.uint8)))
        if zero_w:
            W = np.zeros_like(W)
        seeds = np.asarray(seeds)
        return float(FusedRollout(q.g7.spec, len(raw), seeds, family="linear").run(((W, b), C))[0].mean() / len(seeds))
    return score


def read_elites(q: QLin, elites) -> dict:
    """top1_train value of an archive + the observation-use / input-invariance control on the selected elite."""
    t0 = time.perf_counter()
    got = RO.read(elites, q.glen, scorer(q))
    raw1 = RO.packed(RO.select(elites), q.glen)
    zero = scorer(q, zero_w=True)(raw1, F.HELD64)
    cheats = brain_oracle_cheats(q.g7, q.decode(q.unpack(raw1)), np.asarray(F.HELD64[:8]))
    return {**got, "control_obs_use": {
        "rule": "selected elite re-scored on HELD64 with W zeroed (bias + codebook kept: observations unread)",
        "held64_w_zeroed": zero, "delta_vs_candidate": got["held64_per_seed"] - zero,
        "input_invariant_selected": int(cheats["input_invariant_elites"]),
        "ablate_top_caught": int(cheats["ablate_top"]["elites_caught"]),
        "uses_observations": bool(cheats["input_invariant_elites"] == 0 and got["held64_per_seed"] != zero)},
        "read_wall_s": round(time.perf_counter() - t0, 3)}


def cand_run(r, q: QLin, fam: int, rs: int, gens: int, batch: int, elites_dir) -> dict:
    train = F.PRESSURES[PRESSURE]
    rseed, sseed = BL.seeds_of(GS, len(train), rs, fam)
    key = f"b-r5-1-w{GS}-{PRESSURE}-int{q.bits}-a{q.A}-f{fam}-r{rs}"
    arch = LuaArchive(r, key, q.glen, sseed)
    arch.clear()
    rng = np.random.Generator(np.random.PCG64(rseed))
    fr = FusedRollout(q.g7.spec, batch, train, family="linear")
    t0 = time.perf_counter()
    for _ in range(gens):
        par = arch.sample(batch)
        g = q.init(rng, batch) if len(par) == 0 else q.mutate(rng, q.unpack(par))
        fit, cells = fr.run(q.decode(g))[:2]
        arch.insert(cells, fit, q.pack(g), np.zeros((batch, 2), np.uint32))
    qd_wall = time.perf_counter() - t0
    pairs = [(v[0], v[1]) for v in arch.dump().values()]
    epath = pathlib.Path(elites_dir) / f"{key}.json"
    save_elites(arch, epath, [int(fam), rs, GS])
    arch.clear()
    got = read_elites(q, pairs)
    return {"kind": "run", "rng_family": int(fam), "run_seed": int(rs), "mutation_seed": rseed, "sampler_seed": sseed,
            "gens": gens, "batch": batch, "genomes": gens * batch, "budget_ok": (gens, batch) == BL.BUDGET[PRESSURE],
            "cells": len(pairs), "qd_wall_s": round(qd_wall, 2), "elites": str(epath), **got,
            "wall_s": round(qd_wall + got["read_wall_s"], 3), "_top16": BL.top_raw(pairs, q.glen).tobytes().hex()}


def summary(runs: list[dict], orc: dict, exp: str, stage: str, doc: dict | None = None) -> dict:
    """The candidate row: explicit sample stamp, eligibility from G-R5-4, the one judge (check_r4 on the R16 doc)."""
    q = QLin(GS, BITS, ACTS)
    doc = doc if doc is not None else EL.r16_doc()
    el = EL.eligibility(f"w{GS}", PRESSURE, doc)
    s = SM.stamp(runs)
    held = [float(x["held64_per_seed"]) for x in runs]
    med = float(np.median(held))
    lo, hi = median_ci(held)
    floor, base = el["floor"], el["baseline"]["median"]
    den = el["progress_denominator"]
    judge = QL.check_r4(f"w{GS}", PRESSURE, med, q.glen, s["runs_total"], oracle_clean=orc["oracle_clean"], held=held,
                        doc=doc, readout=RO.NAME, runs_total=s["runs_total"], rng_family_count=s["rng_family_count"],
                        runs_per_family=s["runs_per_family"], n_per_family=s["n_per_family"])
    zeros = [x["control_obs_use"]["held64_w_zeroed"] for x in runs]
    return {"kind": "candidate", "exp_id": exp, "campaign_stage": stage, "world": f"w{GS}", "gen_seed": GS,
            "pressure": PRESSURE, "representation": f"linear_int{BITS}_nibble_a{ACTS}", "readout": RO.NAME,
            "label": "CANDIDATE_N" if SM.meets(s) else "PILOT", **s,
            "candidate_score": med, "candidate_ci95": [lo, hi], "floor": floor, "baseline": base,
            "baseline_bytes": el["baseline"]["bytes"], "progress_denominator": den,
            "progress_above_floor": (med - floor) / den, "progress_ci95": [(lo - floor) / den, (hi - floor) / den],
            "bytes": int(q.glen), "wall_s": round(sum(float(x["wall_s"]) for x in runs), 3), **VRAM,
            "eligibility": {k: el[k] for k in ("eligible", "verdict", "variant", "scope", "rows_commits")},
            "held64_by_run": {BL.run_id(x): x["held64_per_seed"] for x in runs},
            "control_obs_use": {"median_w_zeroed": float(np.median(zeros)),
                                "runs_input_invariant": sum(x["control_obs_use"]["input_invariant_selected"] for x in runs),
                                "runs_using_observations": sum(x["control_obs_use"]["uses_observations"] for x in runs),
                                "input_invariant_learner_floor_part": el["floor_parts"]["input_invariant_learner"]},
            "oracle_clean": orc["oracle_clean"], "oracles_first_run": orc, "judge": judge,
            "verdict": judge["verdict"], "why": judge.get("why")}


def _emit_run(ctx, row: dict, status: str) -> dict:
    out = {k: v for k, v in row.items() if not k.startswith("_")}
    out.update(world=f"w{GS}", gen_seed=GS, pressure=PRESSURE, genome_bytes=QLin(GS, BITS, ACTS).glen, status=status)
    ctx.emit(out)
    return out


def job(ctx, families=FAMILIES, run_seeds=RUN_SEEDS, gens=None, batch=None, archive_url=ARCHIVE_URL,
        elites_dir=str(ELITES_DIR), stage="PILOT"):
    """CANDIDATE_N run. Checkpoints (F9) between runs; oracles on the first run (top-16 powered, r4 rule)."""
    import redis
    r = redis.Redis.from_url(archive_url)
    q = QLin(GS, BITS, ACTS)
    bg, bb = BL.BUDGET[PRESSURE]
    gens, batch = gens or bg, batch or bb
    st = ctx.load_checkpoint() or {"done": {}, "orc": None}
    plan = [(int(f), int(rs)) for f in families for rs in run_seeds]
    for i, (fam, rs) in enumerate(plan):
        k = f"{fam}|{rs}"
        if k in st["done"]:
            continue
        if ctx.should_pause():
            ctx.pause(st, completed_units=len(st["done"]), remaining_units=len(plan) - len(st["done"]))
        row = cand_run(r, q, fam, rs, gens, batch, elites_dir)
        if st["orc"] is None:
            raw16 = np.frombuffer(bytes.fromhex(row["_top16"]), np.uint8).reshape(-1, q.glen)
            st["orc"] = r4_oracles(q, raw16)
            row["oracles_held8"] = st["orc"]
        st["done"][k] = _emit_run(ctx, row, "record")
        ctx.checkpoint(st)
        ctx.progress(len(st["done"]), len(plan) - len(st["done"]))
    ctx.emit({**summary(list(st["done"].values()), st["orc"], EXP, stage), "status": "record"})


def r4_elites(rows=R4_ROWS, root=QL.ROOT) -> dict:
    """{run_seed: elites path} of B's saved round 4 int4_a4 w13 train128 archives, from the committed rows."""
    out = {}
    for p in rows:
        for line in (pathlib.Path(root) / p).read_text(encoding="utf-8").splitlines():
            x = json.loads(line) if line.strip() else {}
            if x.get("kind") == "run" and x.get("rung") == f"int{BITS}_a{ACTS}" and x.get("pressure") == PRESSURE:
                out[int(x["run_seed"])] = x["elites"]
    return dict(sorted(out.items()))


def reread_job(ctx, run_seeds=tuple(range(16)), stage="PILOT"):
    """PILOT: re-read the saved round 4 archives under top1_train (no QD). One RNG stream -> rng_family_count 1."""
    q = QLin(GS, BITS, ACTS)
    paths = r4_elites()
    runs, orc = [], None
    for rs in run_seeds:
        doc = load_elites(paths[int(rs)])
        elites = RO.elites_of(doc)
        got = read_elites(q, elites)
        row = {"kind": "run", "rng_family": R4_STREAM, "run_seed": int(rs), "elites": paths[int(rs)],
               "elites_sha256": hashlib.sha256(pathlib.Path(paths[int(rs)]).read_bytes()).hexdigest(),
               "source": "round 4 saved archive (re-read only; round 4 claims not cited)", **got,
               "wall_s": got["read_wall_s"]}
        if orc is None:
            orc = r4_oracles(q, BL.top_raw(elites, q.glen))
            row["oracles_held8"] = orc
        runs.append(_emit_run(ctx, row, "record"))
    ctx.emit({**summary(runs, orc, EXP_REREAD, stage), "status": "record"})

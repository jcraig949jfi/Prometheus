"""B-R4-1: quantized linear ladder on the round 4 survivor (w13 train128_held64), clause A per SWARM_R4 s4.

First item of B's round 4 charter: the smallest-bytes candidate at progress >= 0.95 on the best-headroom
SURVIVED cell. Only one cell survived the screen (worlds_r4.json, gate_in|HOLD): w13 train128_held64,
floor 166.46875 (the 2-action gate), float linear baseline median 182.71875 at 200 bytes.

Genome: B-R2's QLin (b1_qlinear): the float baseline's linear family with every parameter an integer code
of `bits` bits, plus an `acts`-row nibble action codebook (row 0 = abstain), padded to 4 bytes. w13 is
D=5, A=8, W=1: int4 a8 28 B, int3 a8 24 B, int2 a8 16 B, int3 a4 12 B, int2 a4 8 B, int3 a2 8 B, int2 a2 4 B.

Budget and evaluation equal the M2 baseline (primordial.metric.baseline): TRAIN128, 800 x 128 genomes,
top-16 by (-train fitness, genome bytes), per-seed mean on HELD64, >= 8 run seeds, SEEDED archive sampler
(C2; B-R2-1 was UNSEEDED). Only the genome space and its mutation differ from the baseline.

Oracles on run seed 0 (HELD64[:8]): world honest 0 failing and skip_lin >= 14/16; fused == numpy E7.rollout;
brain honest 0 mismatched; powered cheats (E-T3 brain_verdict: shift_action every elite, ablate_top >= 14/16,
input-invariant elites never caught). The judge is qd_ledger.check (clause_a_r4 block).

    python -m primordial.fabric.worker submit B primordial.cohorts.b.r4_1_qladder:job --exp B-R4-1-qladder-w13-train128 \\
        --rows primordial/ledger/rows/B/B-R4-1-qladder-w13-train128.jsonl --ttl-cpu-s 3000 --kwargs '{}'
    python -m primordial.cohorts.b.r4_1_qladder ledger     # QD ledger rows from the committed summary rows
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import time

import numpy as np

from primordial.cohorts.b.b1_qlinear import QLin
from primordial.cohorts.e.oracles import brain_verdict
from primordial.metric import floors as F
from primordial.metric.ci import median_ci
from primordial.ops import qd_ledger as QL
from primordial.qd import e7_run as E7
from primordial.qd.archive import LuaArchive, save_elites
from primordial.soup.b6.fused import FusedRollout

EXP = "B-R4-1-qladder-w13-train128"
ROOT = QL.ROOT
ROWS = ROOT / "primordial" / "ledger" / "rows" / "B" / f"{EXP}.jsonl"
RUNGS = ((4, 8), (3, 8), (2, 8), (3, 4), (2, 4), (3, 2), (2, 2))
BUDGET = {"train8_held64": (200, 128), "train128_held64": (800, 128)}
TOP = 16
ARCHIVE_URL = "redis://127.0.0.1:6391/0"
ELITES_DIR = pathlib.Path("C:/Users/jcrai/lab/pm-data/B") / EXP


def rung_name(bits: int, acts: int) -> str:
    return f"int{bits}_a{acts}"


def score(q: QLin, raw: np.ndarray, seeds: np.ndarray) -> float:
    return float(FusedRollout(q.g7.spec, len(raw), seeds, family="linear").run(q.decode(q.unpack(raw)))[0].mean()
                 / len(seeds))


def oracles(q: QLin, raw: np.ndarray, seeds=F.HELD64[:8]) -> dict:
    seeds = np.asarray(seeds)
    top = q.decode(q.unpack(raw))
    wo, wc = E7.world_oracle(q.g7, top, seeds), E7.world_oracle(q.g7, top, seeds, "skip_lin")
    bo = E7.brain_oracle(q.g7, top, seeds)
    bv = brain_verdict(q.g7, top, seeds)
    fused = FusedRollout(q.g7.spec, len(raw), seeds, family="linear").run(top)[0]
    ex = int((np.asarray(fused, np.int64) != np.asarray(E7.rollout(q.g7, top, seeds)[0], np.int64)).sum())
    P = len(raw)
    clean = (wo["elites_failing"] == 0 and wc["elites_failing"] >= -(-14 * P // 16) and ex == 0
             and bo["mismatched_rows"] == 0 and bv["clean"])
    return {"world_oracle_honest": wo, "world_oracle_skip_lin": wc, "brain_oracle_honest": bo,
            "brain_powered": bv, "fused_vs_numpy_elites_differing": ex,
            "input_invariant_elites": bv["cheats"]["input_invariant_elites"], "oracle_clean": bool(clean)}


def run_one(r, q: QLin, gs: int, pressure: str, rs: int, gens: int, batch: int, elites_dir) -> dict:
    train = F.PRESSURES[pressure]
    key = f"b-r4-1-w{gs}-{pressure}-int{q.bits}-a{q.A}-r{rs}"
    sseed = [4411, q.bits, q.A, rs, gs, len(train)]
    arch = LuaArchive(r, key, q.glen, sseed)
    arch.clear()
    rng = np.random.Generator(np.random.PCG64([4410, q.bits, q.A, rs, gs, len(train)]))
    fr = FusedRollout(q.g7.spec, batch, train, family="linear")
    t0 = time.perf_counter()
    for _ in range(gens):
        par = arch.sample(batch)
        g = q.init(rng, batch) if len(par) == 0 else q.mutate(rng, q.unpack(par))
        fit, cells = fr.run(q.decode(g))[:2]
        arch.insert(cells, fit, q.pack(g), np.zeros((batch, 2), np.uint32))
    qd_wall = time.perf_counter() - t0
    el = arch.dump()
    best = sorted(((v[0], v[1]) for v in el.values()), key=lambda v: (-v[0], v[1]))[:TOP]
    raw = np.frombuffer(b"".join(g for _, g in best), np.uint8).reshape(-1, q.glen)
    epath = pathlib.Path(elites_dir) / f"{key}.json"
    save_elites(arch, epath, [rs, gs])
    arch.clear()
    return {"kind": "run", "world": f"w{gs}", "gen_seed": gs, "pressure": pressure, "run_seed": rs,
            "rung": rung_name(q.bits, q.A), "bits": q.bits, "acts": q.A, "genome_bytes": int(q.glen),
            "params": int(q.nw + q.nb), "gens": gens, "batch": batch, "genomes": gens * batch,
            "budget_ok": (gens, batch) == BUDGET[pressure], "train_seeds": len(train), "sampler_seed": sseed,
            "cells": len(el), "qd_wall_s": round(qd_wall, 2), "train_per_seed": score(q, raw, train),
            "held64_per_seed": score(q, raw, F.HELD64), "top_sha256": hashlib.sha256(raw.tobytes()).hexdigest(),
            "top_hex": [bytes(x).hex() for x in raw], "elites": str(epath)}


def summary(runs: list[dict], orc: dict, gs: int, pressure: str) -> dict:
    runs = sorted(runs, key=lambda x: x["run_seed"])
    held = [x["held64_per_seed"] for x in runs]
    med = float(np.median(held))
    iqr = float(np.percentile(held, 75) - np.percentile(held, 25))
    nbytes = runs[0]["genome_bytes"]
    verdict = QL.check(QL.load(), f"w{gs}", pressure, med, iqr, nbytes, len(held), orc["oracle_clean"], held=held)
    lo, hi = median_ci(held)
    return {"kind": "summary", "world": f"w{gs}", "gen_seed": gs, "pressure": pressure, "rung": runs[0]["rung"],
            "bits": runs[0]["bits"], "acts": runs[0]["acts"], "genome_bytes": nbytes, "params": runs[0]["params"],
            "median": med, "iqr": iqr, "ci95": [lo, hi], "n_runs": len(held),
            "held64_by_run_seed": {str(x["run_seed"]): x["held64_per_seed"] for x in runs},
            "budget_ok": all(x["budget_ok"] for x in runs), "oracle_clean": orc["oracle_clean"],
            "input_invariant_elites_rs0": orc["input_invariant_elites"],
            "clause_a_r4": verdict["clause_a_r4"], "status": "record" if orc["oracle_clean"] else "cheat"}


def job(ctx, gen_seed=13, pressure="train128_held64", rungs=RUNGS, run_seeds=tuple(range(8)), gens=None, batch=None,
        archive_url=ARCHIVE_URL, elites_dir=str(ELITES_DIR), dev=False):
    """F7 worker job: per rung a run row per run seed (oracles on run seed 0), then a summary row carrying
    qd_ledger.check's clause_a_r4 verdict. Checkpoints (F9) between run seeds."""
    import redis
    r = redis.Redis.from_url(archive_url)
    bg, bb = BUDGET[pressure]
    gens, batch = gens or bg, batch or bb
    st = ctx.load_checkpoint() or {"done": {}, "orc": {}, "summ": []}
    for bits, acts in rungs:
        q = QLin(int(gen_seed), int(bits), int(acts))
        name = rung_name(q.bits, q.A)
        runs = []
        for rs in run_seeds:
            k = f"{name}-r{rs}"
            if k in st["done"]:
                runs.append(st["done"][k])
                continue
            if ctx.should_pause():
                ctx.pause(st)
            row = run_one(r, q, int(gen_seed), pressure, int(rs), gens, batch, elites_dir)
            if int(rs) == int(run_seeds[0]):
                raw = np.frombuffer(b"".join(bytes.fromhex(h) for h in row["top_hex"]), np.uint8).reshape(-1, q.glen)
                st["orc"][name] = oracles(q, raw)
                row["oracles_held8"] = st["orc"][name]
            row["status"] = "dev" if dev else "record"
            ctx.emit(row)
            st["done"][k] = row
            runs.append(row)
            ctx.checkpoint(st)
        if name in st["summ"]:
            continue
        s = summary(runs, st["orc"][name], int(gen_seed), pressure)
        if dev:
            s["status"] = "dev"
        ctx.emit(s)
        st["summ"].append(name)
        ctx.checkpoint(st)


def ledger(rows_path=ROWS) -> list[dict]:
    """QD ledger cells for every committed summary row (status record or cheat) not yet in cells.jsonl."""
    from primordial.fabric.rows import RowWriter
    src = rows_path.relative_to(ROOT).as_posix()
    have = {(r.get("source", {}).get("exp_id"), r["cell"]["representation"]) for r in QL.load()}
    out = []
    for s in (json.loads(l) for l in open(rows_path, encoding="utf-8") if l.strip()):
        if s.get("kind") != "summary" or s.get("status") not in ("record", "cheat"):
            continue
        rep = f"linear_int{s['bits']}_nibble_a{s['acts']}"
        if (EXP, rep) in have:
            continue
        v = QL.check(QL.load(), s["world"], s["pressure"], s["median"], s["iqr"], s["genome_bytes"], s["n_runs"],
                     s["oracle_clean"], held=list(s["held64_by_run_seed"].values()))
        out.append({"cell": {"representation": rep, "world": s["world"], "pressure": s["pressure"],
                             "substrate": "numba_fused", "channel": "none"},
                    "mechanism": f"closed_loop_linear_int{s['bits']}_nibble_codebook_a{s['acts']}",
                    "fitness": {"held64_median": round(s["median"], 4), "iqr": round(s["iqr"], 4),
                                "n_runs": s["n_runs"], "held64_by_run_seed": s["held64_by_run_seed"],
                                "ci95": s["ci95"]},
                    "footprint": {"genome_bytes": s["genome_bytes"], "params": s["params"]},
                    "oracle": ("clean (world hash+charge, skip_lin fails, fused==numpy, brain honest; E-T3 powered)"
                               if s["oracle_clean"] else "NOT clean (see rows run_seed 0)"),
                    "baseline": False, "cohort": "B", "status": s["status"], "clause_a": v,
                    "source": {"exp_id": EXP, "rows": src}})
    if out:
        with RowWriter(QL.CELLS, EXP, commit_every_s=10**9) as w:
            for c in out:
                w.write(c)
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=("ledger",))
    a = p.parse_args()
    for c in ledger():
        print(json.dumps({"rep": c["cell"]["representation"], "bytes": c["footprint"]["genome_bytes"],
                          "median": c["fitness"]["held64_median"], "r4": c["clause_a"]["clause_a_r4"]}))


if __name__ == "__main__":
    main()

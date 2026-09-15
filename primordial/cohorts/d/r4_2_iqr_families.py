"""D-R4-2 (ANOM-1789418772053-0): is the 8-seed spread of a cell a property of the cell, or of the draw?

D3 found identical int4 code on w1 train128_held64 with IQR 19.4 under B's RNG family and 8.98 under D3's.
Round 1-2 runs were UNSEEDED (ZRANDMEMBER), so "RNG family" only fixed the mutation stream. Round 4 archives
are seeded (C2), so a family now fixes the whole run and the question is testable.

Arms at the M2 baseline budget (train128: 800 x 128 genomes on TRAIN128, top-16 by (-train fit, genome),
per-seed mean on HELD64), lane D substrate:
  float_w1   E7.G7(1, linear), 344 B          (the anomaly's float arm; worlds_r4 HELD cell)
  int4_w1    B-R2-1 QLin(1), 52 B             (the anomaly's int4 arm)
  float_w13  E7.G7(13, linear), 200 B         (the only SURVIVED cell: its screen and progress denominator)
RNG families F in (4200, 2101, 3303, 5501): mutation rng PCG64([F, rs, gs, 128]), sampler PCG64([F+1, rs, gs,
128]); run seeds 0..7 -> 32 runs per arm. F=4200 is G's M2 stream: its float runs must reproduce the committed
held64_by_run_seed in worlds_r4.json exactly (instrument).

    python -m primordial.fabric.worker submit D primordial.cohorts.d.r4_2_iqr_families:job \\
        --exp D-R4-2-iqr-families --rows primordial/ledger/rows/D/D-R4-2-iqr-families.jsonl --ttl-cpu-s 12000
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import time

import numpy as np

from primordial.cohorts.b.b1_qlinear import QLin
from primordial.metric import baseline as B
from primordial.metric import floors as F
from primordial.metric.ci import median_ci
from primordial.qd import e7_run as E7
from primordial.qd.archive import LuaArchive
from primordial.soup.b6.fused import FusedRollout

EXP = "D-R4-2-iqr-families"
ROOT = pathlib.Path(__file__).resolve().parents[3]
WORLDS = ROOT / "primordial" / "ledger" / "qd" / "worlds_r4.json"
ARMS = (("float_w1", 1, "float"), ("int4_w1", 1, "int4"), ("float_w13", 13, "float"))
FAMILIES = (4200, 2101, 3303, 5501)
PRESSURE = "train128_held64"
GENS, BATCH = B.BUDGET[PRESSURE]
ARCHIVE_URL = "redis://127.0.0.1:6393/0"
RESAMPLE_SEED, N_DRAWS, N_SCREEN_DRAWS = 20260915, 10_000, 1_000
EPS = 1e-9


class FloatArm:
    """E7.G7 linear through the QLin interface (decode is the identity)."""

    def __init__(self, gs):
        self.g7 = E7.G7(gs, "linear")
        self.glen = self.g7.glen

    def init(self, rng, P):
        return self.g7.init(rng, P)

    def mutate(self, rng, g):
        return self.g7.mutate(rng, g)

    def pack(self, g):
        return self.g7.pack(g)

    def unpack(self, raw):
        return self.g7.unpack(raw)

    def decode(self, g):
        return g


def make_arm(kind, gs):
    return FloatArm(gs) if kind == "float" else QLin(gs)


def per_genome(arm, raw, seeds) -> np.ndarray:
    return FusedRollout(arm.g7.spec, len(raw), np.asarray(seeds), family="linear").run(arm.decode(arm.unpack(raw)))[0] / len(seeds)


def one_run(r, name, gs, kind, fam, rs, gens=GENS, batch=BATCH) -> tuple[dict, np.ndarray]:
    arm = make_arm(kind, gs)
    train = F.TRAIN128
    arch = LuaArchive(r, f"d-r4-2-{name}-f{fam}-r{rs}", arm.glen, [fam + 1, rs, gs, len(train)])
    arch.clear()
    rng = np.random.Generator(np.random.PCG64([fam, rs, gs, len(train)]))
    fr = FusedRollout(arm.g7.spec, batch, train, family="linear")
    t0 = time.perf_counter()
    for _ in range(gens):
        par = arch.sample(batch)
        g = arm.init(rng, batch) if len(par) == 0 else arm.mutate(rng, arm.unpack(par))
        fit, cells = fr.run(arm.decode(g))[:2]
        arch.insert(cells, fit, arm.pack(g), np.zeros((batch, 2), np.uint32))
    wall = time.perf_counter() - t0
    el = arch.dump()
    arch.clear()
    raw = B.top_raw([(v[0], v[1]) for v in el.values()], arm.glen)
    he = per_genome(arm, raw, F.HELD64)
    return ({"kind": "run", "arm": name, "gen_seed": gs, "genome": kind, "family": fam, "run_seed": rs,
             "pressure": PRESSURE, "gens": gens, "batch": batch, "genome_bytes": int(arm.glen), "cells": len(el),
             "qd_wall_s": round(wall, 2), "train_per_seed": float(per_genome(arm, raw, train).mean()),
             "held64_per_seed": float(he.mean()), "held64_elite": [round(float(x), 4) for x in he],
             "top_sha256": hashlib.sha256(raw.tobytes()).hexdigest()}, raw)


def oracles(gs, kind, raw) -> dict:
    arm = make_arm(kind, gs)
    s8 = np.asarray(F.HELD64[:8])
    top = arm.decode(arm.unpack(raw))
    wo, wc = E7.world_oracle(arm.g7, top, s8), E7.world_oracle(arm.g7, top, s8, "skip_lin")
    fused = FusedRollout(arm.g7.spec, len(raw), s8, family="linear").run(top)[0]
    ex = int((np.asarray(fused, np.int64) != np.asarray(E7.rollout(arm.g7, top, s8)[0], np.int64)).sum())
    return {"world_honest": wo, "world_skip_lin": wc, "fused_vs_numpy_differing": ex,
            "clean": bool(wo["elites_failing"] == 0 and wc["elites_failing"] >= 14 and ex == 0)}


def job(ctx, arms=None, families=FAMILIES, run_seeds=tuple(range(8)), gens=None, dev=False, archive_url=ARCHIVE_URL):
    """Every (arm, family, run seed) run, then per-arm summaries and the verdict row. F9: resumes by run."""
    import redis
    r = redis.Redis.from_url(archive_url)
    status = "dev" if dev else "record"
    cells = {c["world"]: c for c in json.loads(WORLDS.read_text(encoding="utf-8"))["cells"] if c["pressure"] == PRESSURE}
    use = [a for a in ARMS if arms is None or a[0] in arms]
    st = ctx.load_checkpoint() or {"runs": {}}
    for name, gs, kind in use:
        for fam in families:
            for rs in run_seeds:
                key = f"{name}|{fam}|{rs}"
                if key in st["runs"]:
                    continue
                if ctx.should_pause():
                    ctx.pause(st)
                row, raw = one_run(r, name, gs, kind, int(fam), int(rs), gens or GENS)
                if kind == "float" and fam == 4200:
                    want = float(cells[f"w{gs}"]["baseline"]["held64_by_run_seed"][str(rs)])
                    row.update(committed_m2_held64=want, reproduces_m2=abs(row["held64_per_seed"] - want) < EPS)
                if fam == families[0] and rs == run_seeds[0]:
                    row["oracles_held8"] = oracles(gs, kind, raw)
                ctx.emit({**row, "status": status})
                st["runs"][key] = row
                ctx.checkpoint(st)
    ctx.emit({**analyse(list(st["runs"].values()), cells), "status": status})


def iqr(x) -> float:
    return float(np.percentile(x, 75) - np.percentile(x, 25))


def analyse(runs: list[dict], cells: dict) -> dict:
    """The pre-registered checks (bus predicate D-R4-2)."""
    from scipy.stats import kruskal
    rng = np.random.Generator(np.random.PCG64(RESAMPLE_SEED))
    by = {}
    for x in runs:
        by.setdefault(x["arm"], {}).setdefault(x["family"], []).append((x["run_seed"], x["held64_per_seed"]))
    arms = {}
    pools = {}
    for name, fams in by.items():
        groups = {f: np.array([v for _, v in sorted(vs)]) for f, vs in sorted(fams.items())}
        pool = np.concatenate(list(groups.values()))
        pools[name] = pool
        draws = np.array([rng.choice(len(pool), 8, replace=False) for _ in range(N_DRAWS)])
        iq = np.array([iqr(pool[d]) for d in draws])
        lo, hi = (float(v) for v in np.percentile(iq, [2.5, 97.5]))
        shift = {f: g + (2 * pool.std() if i == 1 else 0) for i, (f, g) in enumerate(groups.items())}
        arms[name] = {
            "n": int(len(pool)), "median_32": float(np.median(pool)), "iqr_32": iqr(pool),
            "family_iqr": {str(f): round(iqr(g), 3) for f, g in groups.items()},
            "family_median": {str(f): round(float(np.median(g)), 3) for f, g in groups.items()},
            "family_ci95": {str(f): [round(v, 3) for v in median_ci(g)] for f, g in groups.items()},
            "family_iqr_max_over_min": float(max(iqr(g) for g in groups.values()) / max(min(iqr(g) for g in groups.values()), EPS)),
            "iqr8_ci95": [round(lo, 3), round(hi, 3)], "iqr8_ci_ratio": float(hi / max(lo, EPS)),
            "kruskal_p": float(kruskal(*groups.values()).pvalue) if len(groups) > 1 else None,
            "cheat_shifted_family_kruskal_p": float(kruskal(*shift.values()).pvalue) if len(groups) > 1 else None}
    out = {"kind": "summary", "exp": EXP, "arms": arms}
    if {"float_w1", "int4_w1"} <= set(pools):
        fl, i4 = pools["float_w1"], pools["int4_w1"]
        wins = 0
        for _ in range(N_DRAWS):
            a, b = fl[rng.choice(len(fl), 8, replace=False)], i4[rng.choice(len(i4), 8, replace=False)]
            wins += bool(np.median(b) >= np.median(a) - 0.5 * iqr(a))           # r2 parity; int4 52 B < float 344 B
        vals = lambda name, f: np.array([v for _, v in sorted(by[name][f])])
        blocks = [bool(np.median(vals("int4_w1", g)) >= np.median(vals("float_w1", f)) - 0.5 * iqr(vals("float_w1", f)))
                  for f in sorted(by["float_w1"]) for g in sorted(by["int4_w1"])]
        out["r2_int4_vs_float_w1"] = {"pass_rate_8of32": wins / N_DRAWS, "family_block_pass": f"{sum(blocks)}/{len(blocks)}"}
    for name, w in (("float_w13", "w13"), ("float_w1", "w1")):
        if name not in pools:
            continue
        pool, floor = pools[name], float(cells[w]["floor"])
        surv, head = 0, []
        for _ in range(N_SCREEN_DRAWS):
            s = pool[rng.choice(len(pool), 8, replace=False)]
            surv += median_ci(s)[0] > floor
            head.append(float(np.median(s)) - floor)
        fam_surv = {str(f): bool(median_ci([v for _, v in sorted(vs)])[0] > floor) for f, vs in sorted(by[name].items())}
        out[f"screen_{w}"] = {"floor_gate_in": floor, "survived_rate_8of32": surv / N_SCREEN_DRAWS,
                              "family_blocks_survived": fam_surv,
                              "headroom_median_minus_floor_ci95": [round(float(v), 3) for v in np.percentile(head, [2.5, 97.5])]}
    rep = [x["reproduces_m2"] for x in runs if "reproduces_m2" in x]
    orc = [x["oracles_held8"]["clean"] for x in runs if "oracles_held8" in x]
    a = arms
    out["checks"] = {
        "I_family4200_reproduces_m2_all": bool(rep) and all(rep), "n_reproduce_checked": len(rep),
        "O_oracles_clean_all": bool(orc) and all(orc),
        "C_shifted_family_detected_all_arms": all((v["cheat_shifted_family_kruskal_p"] or 1) < 0.05 for v in a.values()),
        "P1_float_w1_iqr8_ci_ratio_ge2": a.get("float_w1", {}).get("iqr8_ci_ratio", 0) >= 2,
        "P2_int4_w1_family_iqr_ratio_ge2": a.get("int4_w1", {}).get("family_iqr_max_over_min", 0) >= 2,
        "P3_families_exchangeable_all_arms": all((v["kruskal_p"] or 0) > 0.05 for v in a.values()),
        "P4_r2_flip_rate_in_10_90": 0.1 < out.get("r2_int4_vs_float_w1", {}).get("pass_rate_8of32", -1) < 0.9,
        "P5_w13_survived_ge95pct_and_4of4_blocks": (out.get("screen_w13", {}).get("survived_rate_8of32", 0) >= 0.95
                                                    and all(out.get("screen_w13", {}).get("family_blocks_survived", {"x": False}).values()))}
    return out

"""D3 (ANOM-1789417951134-0): is B-R2-1's w1 held-out spread (IQR 19.4) int4 quantization or the world/search?

Paired rerun of E10's closed condition on w1 over run seeds 0-7 with two genome spaces:
  float  E7.G7 linear (the E10 genome)      int4  B-R2-1 QLin (lane B's genome, read-only import)
Same RNG seeds per arm, lane D Redis substrate. Every top-16 elite is also scored alone on HELD64 so
within-run selection noise can be compared with the across-run spread. Oracles on run seed 0 per arm.
Predicate on the bus ("D3-w1-linear-spread HYPOTHESIS").

usage: python -m primordial.cohorts.d.d3_run [--run-seeds 0-3] [--arms float,int4] [--gens 800] [--summary]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time

import numpy as np
import redis

from primordial.cohorts.b.b1_qlinear import QLin
from primordial.fabric.rows import RowWriter
from primordial.qd import e7_run as E7
from primordial.qd import e8_run as E8
from primordial.qd import e9_run as E9
from primordial.qd.archive import UNSEEDED, LuaArchive
from primordial.soup.b6.fused import FusedRollout

EXP = "D3-w1-linear-spread"
ROOT = pathlib.Path(__file__).resolve().parents[2]
ROWS = ROOT / "ledger" / "rows" / "D" / f"{EXP}.jsonl"
TRAIN = E8.seeds_n(128)
HELD64, HELD8, TOP = E7.HELD64, E7.HELD8, E7.TOP
GS, BATCH, PORT = 1, 128, 6393


class FloatArm:
    """E10's float linear genome through the same interface as QLin (decode is the identity)."""

    def __init__(self, gs):
        self.g7 = E7.G7(gs, "linear")
        self.glen = self.g7.glen

    def init(self, rng, P):
        return self.g7.init(rng, P)

    def mutate(self, rng, g):
        return self.g7.mutate(rng, g)

    def pack(self, g):
        return self.g7.pack(g)

    def unpack(self, B):
        return self.g7.unpack(B)

    def decode(self, g):
        return g


def per_elite(arm, raw, seeds) -> np.ndarray:
    return FusedRollout(arm.g7.spec, len(raw), seeds, family="linear").run(arm.decode(arm.unpack(raw)))[0] / len(seeds)


def one_run(r, arm_name, rs, gens, status):
    arm = FloatArm(GS) if arm_name == "float" else QLin(GS)
    t0 = time.perf_counter()
    arch = LuaArchive(r, f"d3-{arm_name}-{GS}-{rs}-{gens}", arm.glen, UNSEEDED)
    arch.clear()
    rng = np.random.Generator(np.random.PCG64([3303, rs, GS]))
    fr = FusedRollout(arm.g7.spec, BATCH, TRAIN, family="linear")
    for _ in range(gens):
        par = arch.sample(BATCH)
        g = arm.init(rng, BATCH) if len(par) == 0 else arm.mutate(rng, arm.unpack(par))
        fit, cells = fr.run(arm.decode(g))[:2]
        arch.insert(cells, fit, arm.pack(g), np.zeros((BATCH, 2), np.uint32))
    qd_wall = time.perf_counter() - t0
    el = arch.dump()
    raw = np.frombuffer(b"".join(v[1] for v in sorted(el.values(), key=lambda v: (-v[0], v[1]))[:TOP]),
                        np.uint8).reshape(-1, arm.glen)
    arch.clear()
    tr, he = per_elite(arm, raw, TRAIN), per_elite(arm, raw, HELD64)
    row = {"status": status, "kind": "run", "arm": arm_name, "gen_seed": GS, "run_seed": rs, "gens": gens,
           "batch": BATCH, "genome_bytes": int(arm.glen), "cells": len(el), "qd_wall_s": round(qd_wall, 1),
           "train_per_seed": float(tr.mean()), "held64_per_seed": float(he.mean()),
           "held64_elite": [round(float(x), 4) for x in he], "train_elite": [round(float(x), 4) for x in tr],
           "top_hex": [bytes(x).hex() for x in raw]}
    if rs == 0:
        top = arm.decode(arm.unpack(raw))
        wo, wc = E7.world_oracle(arm.g7, top, HELD8), E7.world_oracle(arm.g7, top, HELD8, "skip_lin")
        bo, bc = E7.brain_oracle(arm.g7, top, HELD8), E7.brain_oracle(arm.g7, top, HELD8, cheat=True)
        row.update(world_oracle_honest=wo, world_oracle_skip_lin=wc, brain_oracle_honest=bo, brain_oracle_cheat=bc,
                   oracle_clean=bool(wo["elites_failing"] == 0 and wc["elites_failing"] >= 14
                                     and bo["mismatched_rows"] == 0 and bc["elites_mismatching"] >= 14))
    row["wall_s"] = round(time.perf_counter() - t0, 1)
    return row


def iqr(x):
    return float(np.percentile(x, 75) - np.percentile(x, 25))


def summarize(rows, gens):
    runs = {a: sorted((x for x in rows if x.get("kind") == "run" and x["arm"] == a and x["gens"] == gens),
                      key=lambda x: x["run_seed"]) for a in ("float", "int4")}
    h = {a: np.array([x["held64_per_seed"] for x in rs]) for a, rs in runs.items()}
    t = {a: np.array([x["train_per_seed"] for x in rs]) for a, rs in runs.items()}
    rng = np.random.default_rng(99)
    ratios = []
    for _ in range(2000):
        fi, ii = (rng.integers(0, len(h[a]), len(h[a])) for a in ("float", "int4"))
        f_iqr = iqr(h["float"][fi])
        ratios.append(iqr(h["int4"][ii]) / f_iqr if f_iqr > 0 else np.inf)
    lo, hi = (float(v) for v in np.percentile(ratios, [2.5, 97.5]))
    f_iqr = iqr(h["float"])
    verdict = "WORLD" if f_iqr >= 10 else ("INT4" if f_iqr <= 5 and lo > 1 else "INDETERMINATE")
    within = {a: float(np.median([np.std(x["held64_elite"]) for x in rs])) for a, rs in runs.items()}
    across = {a: float(np.std(h[a])) for a in h}
    oracle = {a: next((x.get("oracle_clean") for x in rs if x["run_seed"] == 0), None) for a, rs in runs.items()}
    return {"exp": EXP, "gens": gens, "n_runs": {a: len(v) for a, v in h.items()},
            "held64": {a: [round(float(v), 2) for v in h[a]] for a in h},
            "held64_median": {a: round(float(np.median(h[a])), 2) for a in h},
            "held64_iqr": {a: round(iqr(h[a]), 2) for a in h},
            "train_iqr": {a: round(iqr(t[a]), 2) for a in t},
            "iqr_ratio_int4_over_float_ci95": [round(lo, 2), round(hi, 2)],
            "verdict": verdict,
            "H2_train_iqr_le5_both": all(iqr(t[a]) <= 5 for a in t),
            "within_run_elite_sd_median": {a: round(v, 2) for a, v in within.items()},
            "across_run_sd": {a: round(v, 2) for a, v in across.items()},
            "H3_within_ge_across_both": all(within[a] >= across[a] for a in h),
            "oracle_clean": oracle}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-seeds", default="0-7"); ap.add_argument("--arms", default="float,int4")
    ap.add_argument("--gens", type=int, default=800); ap.add_argument("--summary", action="store_true")
    a = ap.parse_args(argv)
    status = "record" if a.gens == 800 else "dev"
    with RowWriter(ROWS, EXP, commit_every_s=120) as w:
        if a.summary:
            rows = [json.loads(line) for line in open(ROWS, encoding="utf-8")]
            s = summarize(rows, a.gens)
            w.write({"status": status, "kind": "summary", **s})
            print(json.dumps(s, indent=1))
            return
        r = redis.Redis(host="127.0.0.1", port=PORT)
        for rs in E9.parse_seeds(a.run_seeds):
            for arm in a.arms.split(","):
                row = one_run(r, arm, rs, a.gens, status)
                w.write(row)
                print(json.dumps({k: v for k, v in row.items() if k not in ("top_hex", "held64_elite", "train_elite")
                                  and not isinstance(v, dict)}), flush=True)


if __name__ == "__main__":
    main()

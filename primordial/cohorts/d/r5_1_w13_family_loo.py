"""D-R5-1 (ANOM-1789453196045-0): does w13 train128 SURVIVED rest on RNG family 4200 under the ruled readout?

D-R4-2 found the 8-seed screen passing for family 4200 only (legacy top-16 readout). Ruling 16 pooled 32 runs x 4
families under top1_train and G's R16 screen says SURVIVED (CI low 170.95 > gate_in 166.47). The claim "survival
rests on one family" is answered by removing that family from the pool, not by more QD: zero new runs here,
committed G-R16-baseline rows only. Predicate: bus 1789471125531-0.

    worker.submit("D", "primordial.cohorts.d.r5_1_w13_family_loo:job", "D-R5-1-w13-family-loo",
                  "primordial/ledger/rows/D/D-R5-1-w13-family-loo.jsonl", 120, envelope={...PILOT...})
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import time

import numpy as np

from primordial.metric import eligibility as EL
from primordial.metric.ci import median_ci

EXP = "D-R5-1-w13-family-loo"
PREDICATE = "1789471125531-0"
ROOT = pathlib.Path(__file__).resolve().parents[3]
BASELINE_ROWS = ROOT / "primordial" / "ledger" / "rows" / "G" / "G-R16-baseline.jsonl"
ORDER = (4200, 2101, 3303, 5501)                 # G's stamped bootstrap order (G 1789456804803-0)
G_CI = (170.9531, 188.5625)
STAB_SEED, STAB_DRAWS = 20260915, 1000
READOUTS = {"top1_train": "held64_per_seed", "legacy_top16": "held64_legacy_top16"}


def load_runs(path=BASELINE_ROWS) -> tuple[list[dict], str]:
    raw = path.read_bytes()
    runs = {}
    for line in raw.decode("utf-8").splitlines():
        if not line.strip():
            continue
        x = json.loads(line)
        if x.get("kind") == "run" and x.get("gen_seed") == 13 and x.get("pressure") == "train128_held64":
            runs[(int(x["rng_family"]), int(x["run_seed"]))] = x          # last row per (family, run seed) wins
    return [runs[k] for k in sorted(runs, key=lambda k: (ORDER.index(k[0]), k[1]))], hashlib.sha256(raw).hexdigest()


def pool(runs, field, families) -> np.ndarray:
    return np.array([x[field] for x in runs if int(x["rng_family"]) in families], dtype=np.float64)


def ci_row(values, floor) -> dict:
    lo, hi = median_ci(values)
    return {"n": int(len(values)), "median": float(np.median(values)), "ci95": [round(lo, 4), round(hi, 4)],
            "ci_low_gt_floor": bool(lo > floor)}


def analyse(runs, floor) -> dict:
    by_fam = {f: sum(1 for x in runs if int(x["rng_family"]) == f) for f in ORDER}
    out = {"n_runs": len(runs), "n_per_family": {str(f): n for f, n in by_fam.items()}, "floor": floor}
    for name, field in READOUTS.items():
        full = pool(runs, field, ORDER)
        loo = {str(f): ci_row(pool(runs, field, tuple(g for g in ORDER if g != f)), floor) for f in ORDER}
        blocks = {str(f): ci_row(pool(runs, field, (f,)), floor) for f in ORDER}
        rng = np.random.Generator(np.random.PCG64(STAB_SEED))
        groups = [pool(runs, field, (f,)) for f in ORDER]
        surv = 0
        for _ in range(STAB_DRAWS):
            s = np.concatenate([g[rng.integers(0, len(g), len(g))] for g in groups])
            surv += median_ci(s)[0] > floor
        out[name] = {"full": ci_row(full, floor), "leave_one_family_out": loo,
                     "loo_survive_k_of_4": sum(v["ci_low_gt_floor"] for v in loo.values()),
                     "family_blocks": blocks, "blocks_survive_k_of_4": sum(v["ci_low_gt_floor"] for v in blocks.values()),
                     "stratified_bootstrap_survive_rate": surv / STAB_DRAWS}
    t1 = out["top1_train"]
    i1 = (len(runs) == 32 and all(n == 8 for n in by_fam.values())
          and all(abs(a - b) < 5e-5 for a, b in zip(t1["full"]["ci95"], G_CI)))
    p1 = t1["leave_one_family_out"]["4200"]["ci_low_gt_floor"]
    out["checks"] = {"I1_reproduces_G_pooled_ci": bool(i1), "P1_leave4200_out_survives": bool(p1),
                     "P2_loo_survive_k_of_4": t1["loo_survive_k_of_4"],
                     "P3_blocks_survive_k_of_4": t1["blocks_survive_k_of_4"],
                     "P4_stratified_bootstrap_survive_rate": t1["stratified_bootstrap_survive_rate"]}
    out["decision"] = "INDETERMINATE" if not i1 else ("REFUTED" if p1 else "RESOLVED")
    return out


def job(ctx, status="record"):
    t0 = time.perf_counter()
    elig = EL.w13_eligibility()
    floor = float(elig["floor"])
    runs, sha = load_runs()
    res = analyse(runs, floor)
    ctx.emit({"kind": "summary", "exp": EXP, "predicate": PREDICATE, "status": status, "ts": round(time.time(), 3),
              "cell": "w13 train128_held64", "variant": elig["variant"],
              "source_rows": "primordial/ledger/rows/G/G-R16-baseline.jsonl", "source_rows_sha256": sha,
              "source_rows_commit": elig["rows_commits"].get("primordial/ledger/rows/G/G-R16-baseline.jsonl"),
              "pool_order": list(ORDER), "runs_total": 32, "rng_family_count": 4, "runs_per_family": 8,
              "loo_pool": {"runs_total": 24, "rng_family_count": 3, "runs_per_family": 8},
              "wall_s": round(time.perf_counter() - t0, 3), **res})

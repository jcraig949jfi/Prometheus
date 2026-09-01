#!/usr/bin/env python
"""E6 -- cross-substrate predictor transfer. Frozen by FREEZE_E6.txt."""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

E2 = json.loads((HERE / "results" / "e2_arena.json").read_text(encoding="utf-8"))
E5 = json.loads((HERE / "results" / "e5_search.json").read_text(encoding="utf-8"))
CELLS = {f"{c['substrate']}|{c['operator']}": c for c in E2["cells"]}
REAL = json.loads((HERE / "results" / "e5_frozen_ranking.json")
                  .read_text(encoding="utf-8"))["real_substrate_cells"]

PREDICTORS = ["q1_neutral_rate", "q2_destruction_rate", "q3_band_rate",
              "q4_middle_mass", "q5_median_nonzero_d",
              "q10_reach_improve_at1", "q11_drift", "q13_baseline_d",
              "C_composite"]


def family(cell):
    return cell.split("|")[0].split("[")[0]


def rk(v):
    v = np.asarray(v, float)
    vals, inv, cnt = np.unique(v, return_inverse=True, return_counts=True)
    csum = np.cumsum(cnt) - cnt
    return (csum + (cnt - 1) / 2.0)[inv]


def spear(x, y):
    rx, ry = rk(x) - rk(x).mean(), rk(y) - rk(y).mean()
    den = np.sqrt((rx ** 2).sum() * (ry ** 2).sum())
    return float((rx * ry).sum() / den) if den > 0 else 0.0


def build_rows(mode):
    """One row per (real cell x target)."""
    rows = []
    by_ct = {}
    for r in E5["runs"]:
        if r["mode"] != mode or r["cell"] not in REAL:
            continue
        by_ct.setdefault((r["cell"], r["target"]), []).append(r["norm_improve"])
    for (cell, tgt), vals in by_ct.items():
        Q = CELLS[cell]["Q"]
        pt = CELLS[cell]["per_target"][tgt]
        rows.append({
            "cell": cell, "family": family(cell), "target": tgt,
            "outcome": float(np.mean(vals)),
            "q1_neutral_rate": Q["q1_neutral_rate"],
            "q2_destruction_rate": Q["q2_destruction_rate"],
            "q3_band_rate": Q["q3_band_rate"],
            "q4_middle_mass": Q["q4_middle_mass"],
            "q5_median_nonzero_d": Q["q5_median_nonzero_d"],
            "q10_reach_improve_at1": pt["q10_reach_improve_at1"],
            "q11_drift": pt["q11_drift"],
            "q13_baseline_d": pt["q13_baseline_d"],
            # frozen composite, declared in FREEZE_E6 before any number
            "C_composite": Q["q4_middle_mass"] * (1.0 - Q["q2_destruction_rate"]),
        })
    return rows


def loso(rows, pred):
    """Held-out Spearman per family fold. Single predictor -> monotone
    transfer is exactly rank correlation on the held-out rows; the SIGN
    must be learned on train, so a sign flip counts against it."""
    fams = sorted({r["family"] for r in rows})
    out = {}
    for f in fams:
        tr = [r for r in rows if r["family"] != f]
        te = [r for r in rows if r["family"] == f]
        sign = np.sign(spear([r[pred] for r in tr], [r["outcome"] for r in tr])) or 1.0
        rho_te = spear([sign * r[pred] for r in te], [r["outcome"] for r in te])
        out[f] = {"held_out_rho": round(rho_te, 4), "n_test": len(te),
                  "train_sign": float(sign),
                  "underpowered": bool(len({r["cell"] for r in te}) < 2)}
    return out


def perm_null(rows, pred, n=200, seed=23):
    rng = np.random.default_rng(seed)
    fams = sorted({r["family"] for r in rows})
    means = []
    for _ in range(n):
        vals = []
        for f in fams:
            tr = [r for r in rows if r["family"] != f]
            te = [r for r in rows if r["family"] == f]
            y = rng.permutation([r["outcome"] for r in tr])
            sign = np.sign(spear([r[pred] for r in tr], y)) or 1.0
            vals.append(spear([sign * r[pred] for r in te],
                              [r["outcome"] for r in te]))
        means.append(np.mean(vals))
    return float(np.percentile(means, 99))


def main():
    out = {"experiment": "E6", "freeze": "FREEZE_E6.txt", "modes": {}}
    for mode in ("STRICT", "NEUTRAL-OK"):
        rows = build_rows(mode)
        res = {}
        for p in PREDICTORS:
            folds = loso(rows, p)
            powered = {k: v for k, v in folds.items() if not v["underpowered"]}
            rhos = [v["held_out_rho"] for v in folds.values()]
            res[p] = {"folds": folds,
                      "mean_held_out_rho": round(float(np.mean(rhos)), 4),
                      "min_held_out_rho": round(float(min(rhos)), 4),
                      "all4_ge_0p50": bool(all(v >= 0.50 for v in rhos)),
                      "powered_folds_ge_0p50": bool(
                          all(v["held_out_rho"] >= 0.50 for v in powered.values()))}
        q13m = res["q13_baseline_d"]["mean_held_out_rho"]
        winners = [p for p in PREDICTORS if res[p]["all4_ge_0p50"]]
        best = max(PREDICTORS, key=lambda p: res[p]["mean_held_out_rho"])
        p99 = perm_null(rows, best)
        res_summary = {
            "n_rows": len(rows),
            "families": sorted({r["family"] for r in rows}),
            "E6-G1_transfer_all4_folds": {"winners": winners,
                                          "pass": len(winners) > 0},
            "best_predictor": best,
            "best_mean_rho": res[best]["mean_held_out_rho"],
            "E6-G2_beats_difficulty_null": {
                "q13_mean_rho": q13m,
                "margin": round(res[best]["mean_held_out_rho"] - q13m, 4),
                "pass": bool(res[best]["mean_held_out_rho"] - q13m >= 0.10)},
            "E6-G3_beats_permutation_null": {
                "perm_null_p99": round(p99, 4),
                "pass": bool(res[best]["mean_held_out_rho"] > p99)},
        }
        out["modes"][mode] = {"per_predictor": res, "summary": res_summary}
        print(f"\n=== {mode}  ({len(rows)} rows, families "
              f"{res_summary['families']}) ===")
        print(f"{'predictor':24s} {'mean':>7s} {'min':>7s} "
              + "".join(f"{f[:8]:>9s}" for f in sorted({r['family'] for r in rows})))
        for p in PREDICTORS:
            f = res[p]["folds"]
            print(f"{p:24s} {res[p]['mean_held_out_rho']:7.3f} "
                  f"{res[p]['min_held_out_rho']:7.3f} "
                  + "".join(f"{f[k]['held_out_rho']:9.3f}" for k in sorted(f)))
        s = res_summary
        print(f"  G1 transfer(all 4 folds >=0.50): {s['E6-G1_transfer_all4_folds']['pass']} "
              f"winners={s['E6-G1_transfer_all4_folds']['winners']}")
        print(f"  best={s['best_predictor']} mean_rho={s['best_mean_rho']}")
        print(f"  G2 beats difficulty null: {s['E6-G2_beats_difficulty_null']}")
        print(f"  G3 beats permutation null: {s['E6-G3_beats_permutation_null']}")

    allpass = {m: (out["modes"][m]["summary"]["E6-G1_transfer_all4_folds"]["pass"]
                   and out["modes"][m]["summary"]["E6-G2_beats_difficulty_null"]["pass"]
                   and out["modes"][m]["summary"]["E6-G3_beats_permutation_null"]["pass"])
               for m in out["modes"]}
    out["verdict"] = ("TRANSFERABLE" if any(allpass.values())
                      else "NO_TRANSFERABLE_NAVIGABILITY_COORDINATE")
    out["gates_by_mode"] = allpass
    (HERE / "results" / "e6_transfer.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nVERDICT: {out['verdict']}   {allpass}")


if __name__ == "__main__":
    main()

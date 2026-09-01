#!/usr/bin/env python
"""E5 -- compute-matched short-horizon search. Frozen by FREEZE_E5.txt.

The prediction was written, hashed, journaled and committed before this file
was executed (results/e5_frozen_ranking.json, commit 0ad73f52c).
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import substrates as S      # noqa: E402
import mutators as M        # noqa: E402
import assay as A           # noqa: E402

BUDGET = 800            # phenotype evaluations per run -- the matched currency
SEEDS = list(range(9000, 9015))          # 15, disjoint from every prior block
MODES = ("STRICT", "NEUTRAL-OK")


def cell_defs():
    circ, vm, dnf = S.Circuit(), S.ByteVM(), S.DNF()
    return {
        "CIRCUIT|M-UNIFORM": (circ, M.UniformSite()),
        "CIRCUIT|M-OPONLY": (circ, M.OpOnly()),
        "CIRCUIT|M-WIREONLY": (circ, M.WireOnly()),
        "BYTEVM|M-RAWBYTE": (vm, M.RawByte()),
        "BYTEVM|M-INSTR": (vm, M.InstructionAware()),
        "DNF|M-UNIFORM": (dnf, M.UniformSite()),
        "RELAX[tau=0.1]|M-GAUSS[1.0]": (S.RelaxedCircuit(tau=0.1), M.GaussianStep(1.0)),
        "RELAX[tau=0.5]|M-GAUSS[1.0]": (S.RelaxedCircuit(tau=0.5), M.GaussianStep(1.0)),
        "RELAX[tau=2.0]|M-GAUSS[4.0]": (S.RelaxedCircuit(tau=2.0), M.GaussianStep(4.0)),
        "P1-BLOCKS|SWEEP-ALL": (S.BlocksPositive(), M.UniformSite()),
        "N1-SMOOTH-UNREACHABLE|SWEEP-ALL": (S.SmoothUnreachable(), M.UniformSite()),
        "N2-HASH|SWEEP-ALL": (S.HashSubstrate(), M.RawByte()),
    }


def hill_climb(sub, mut, seed, target, budget, mode):
    """(1+1) hill-climbing. Budget counted in PHENOTYPE EVALUATIONS."""
    rng = S.rng_for(seed, 0x5EA, hash(mode) % 1000)
    g = sub.sample(seed)
    f = sub.phenotype(g)
    evals = 1
    d_cur = S.d_of(f, target)
    d_start = d_cur
    d_best = d_cur
    accepted = 0
    declines = 0
    while evals < budget:
        r = mut(sub, g, rng)
        if r is None:
            declines += 1
            continue
        g2 = r[0]
        f2 = sub.phenotype(g2)
        evals += 1
        d2 = S.d_of(f2, target)
        take = (d2 < d_cur) if mode == "STRICT" else (d2 <= d_cur)
        if take:
            if d2 < d_cur or mode == "NEUTRAL-OK":
                g, f, d_cur = g2, f2, d2
                accepted += 1
        d_best = min(d_best, d2)
    return {"d_start": d_start, "d_best": d_best, "evals": evals,
            "accepted": accepted, "declines": declines,
            "norm_improve": (d_start - d_best) / d_start if d_start > 0 else 0.0,
            "exact_hit": bool(d_best == 0.0)}


def spearman(x, y):
    return float(S.__dict__.get("_", 0)) if False else _spear(x, y)


def _spear(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)

    def rk(v):
        vals, inv, cnt = np.unique(v, return_inverse=True, return_counts=True)
        csum = np.cumsum(cnt) - cnt
        return (csum + (cnt - 1) / 2.0)[inv]
    rx, ry = rk(x) - rk(x).mean(), rk(y) - rk(y).mean()
    den = np.sqrt((rx ** 2).sum() * (ry ** 2).sum())
    return float((rx * ry).sum() / den) if den > 0 else 0.0


def main():
    frozen = json.loads((HERE / "results" / "e5_frozen_ranking.json")
                        .read_text(encoding="utf-8"))
    defs = cell_defs()
    out = {"experiment": "E5", "freeze": "FREEZE_E5.txt", "budget_evals": BUDGET,
           "seeds": [SEEDS[0], SEEDS[-1]], "runs": [], "cell_scores": {},
           "frozen_ranking_sha_note": "prediction committed at 0ad73f52c before this ran"}

    for mode in MODES:
        for cname, (sub, mut) in defs.items():
            t0 = time.time()
            runs = []
            for tname in A.TARGET_NAMES:
                T = A.TARGETS[tname]
                for sd in SEEDS:
                    r = hill_climb(sub, mut, sd, T, BUDGET, mode)
                    r.update({"cell": cname, "mode": mode, "target": tname,
                              "seed": sd})
                    runs.append(r)
            out["runs"].extend(runs)
            ni = np.array([r["norm_improve"] for r in runs])
            key = f"{cname}||{mode}"
            out["cell_scores"][key] = {
                "cell": cname, "mode": mode, "n_runs": len(runs),
                "mean_norm_improve": float(ni.mean()),
                "median_norm_improve": float(np.median(ni)),
                "mean_d_best": float(np.mean([r["d_best"] for r in runs])),
                "exact_hit_rate": float(np.mean([r["exact_hit"] for r in runs])),
                "mean_accepted": float(np.mean([r["accepted"] for r in runs])),
                "seconds": round(time.time() - t0, 1)}
            print(f"{mode:11s} {cname:32s} improve={ni.mean():.4f} "
                  f"hit={out['cell_scores'][key]['exact_hit_rate']:.3f} "
                  f"acc={out['cell_scores'][key]['mean_accepted']:6.1f} "
                  f"({round(time.time()-t0,1)}s)")

    # ---- adjudication
    rank = {r["cell"]: r for r in frozen["ranking"]}
    real = set(frozen["real_substrate_cells"])
    adj = {}
    for mode in MODES:
        cells = [c for c in defs]
        out_v = [out["cell_scores"][f"{c}||{mode}"]["mean_norm_improve"] for c in cells]
        q10 = [rank[c]["q10_reach_improve_at1"] for c in cells]
        q4 = [rank[c]["q4_middle_mass"] for c in cells]
        rcells = [c for c in cells if c in real]
        rout = [out["cell_scores"][f"{c}||{mode}"]["mean_norm_improve"] for c in rcells]
        rq10 = [rank[c]["q10_reach_improve_at1"] for c in rcells]
        rq4 = [rank[c]["q4_middle_mass"] for c in rcells]
        adj[mode] = {
            "PC4_all12_rho_q10_vs_outcome": round(_spear(q10, out_v), 4),
            "PC4_pass": bool(_spear(q10, out_v) >= 0.70),
            "PC3a_real9_rho_q4_vs_outcome": round(_spear(rq4, rout), 4),
            "PC3a_pass_abs_lt_0p50": bool(abs(_spear(rq4, rout)) < 0.50),
            "PC3b_real9_rho_q10_vs_outcome": round(_spear(rq10, rout), 4),
            "PC3b_pass_ge_0p70": bool(_spear(rq10, rout) >= 0.70),
        }
        # exploratory, labelled
        expl = {}
        for coord in ("q1_neutral_rate", "q2_destruction_rate", "q3_band_rate",
                      "q4_middle_mass", "q10_reach_improve_at1", "q11_drift",
                      "q13_baseline_d"):
            expl[coord] = {
                "all12": round(_spear([rank[c][coord] for c in cells], out_v), 4),
                "real9": round(_spear([rank[c][coord] for c in rcells], rout), 4)}
        adj[mode]["EXPLORATORY_labelled_decides_nothing"] = expl
    out["adjudication"] = adj

    # harness controls
    p1 = out["cell_scores"]["P1-BLOCKS|SWEEP-ALL||STRICT"]
    p1_t9 = [r for r in out["runs"] if r["cell"] == "P1-BLOCKS|SWEEP-ALL"
             and r["mode"] == "STRICT" and r["target"] == "T9_P1_TARGET"]
    n1_t10 = [r for r in out["runs"] if r["cell"] == "N1-SMOOTH-UNREACHABLE|SWEEP-ALL"
              and r["mode"] == "STRICT" and r["target"] == "T10_N1_TARGET"]
    out["harness_controls"] = {
        "P1_reaches_zero_on_own_target": {
            "exact_hit_rate": float(np.mean([r["exact_hit"] for r in p1_t9])),
            "pass": bool(np.mean([r["exact_hit"] for r in p1_t9]) >= 0.99)},
        "N1_zero_improvement_on_own_target": {
            "mean_norm_improve": float(np.mean([r["norm_improve"] for r in n1_t10])),
            "pass": bool(np.mean([r["norm_improve"] for r in n1_t10]) == 0.0)},
        "P1_overall_strict": p1["mean_norm_improve"]}

    (HERE / "results").mkdir(exist_ok=True)
    p = HERE / "results" / "e5_search.json"
    p.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("\n--- HARNESS CONTROLS ---")
    for k, v in out["harness_controls"].items():
        print(f"  {k}: {v}")
    print("\n--- ADJUDICATION ---")
    for mode in MODES:
        a = adj[mode]
        print(f"  [{mode}]")
        print(f"    PC-4 rho(q10, outcome) all 12 = {a['PC4_all12_rho_q10_vs_outcome']:+.4f} "
              f"bar>=0.70 -> {'PASS' if a['PC4_pass'] else 'FAIL'}")
        print(f"    PC-3a |rho(q4, outcome)| real 9 = {abs(a['PC3a_real9_rho_q4_vs_outcome']):.4f} "
              f"bar<0.50 -> {'PASS' if a['PC3a_pass_abs_lt_0p50'] else 'FAIL'}")
        print(f"    PC-3b rho(q10, outcome) real 9 = {a['PC3b_real9_rho_q10_vs_outcome']:+.4f} "
              f"bar>=0.70 -> {'PASS' if a['PC3b_pass_ge_0p70'] else 'FAIL'}")
    print(f"\nwrote {p}")


if __name__ == "__main__":
    main()

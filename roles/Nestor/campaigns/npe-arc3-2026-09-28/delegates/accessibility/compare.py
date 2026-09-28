"""Q2 pilot comparison: soup (read from the W1/P2 result files) vs the neutral process (results_neutral/).

Computational artificial life: integer programs on the z8 VM. Nothing biological.

Endpoint: first checkpoint (every 100 epochs) with >= 1 COMPETENT genome. Reported as a hazard:
  per run-checkpoint at risk (discrete time: events / checkpoints at risk, runs censored at epoch 2000)
  per evaluation (events / distinct genomes screened while at risk; a screened genome = one evaluation).
Exact 95% intervals for zero counts use the rule of three (upper = 3 / exposure); otherwise a Poisson
approximation (Garwood via chi2 would need scipy, so the Byar approximation is used).
Output compare.json.
"""
from __future__ import annotations

import glob
import json
import math

import acc_lib as A

SOUP = {
    "PLAIN": (A.W1 / "x_dd_dense_copy" / "results", "PLAIN_{cell}_{seed}.json"),
    "DENSE": (A.W1 / "x_dd_dense_copy" / "results", "DENSE_COPY_{cell}_{seed}.json"),
    "PLANT": (A.P2 / "x_p2_plant" / "results", "{cell}_{seed}.json"),
    "SHAM": (A.P2 / "x_p2_sham" / "results", "{cell}_{seed}.json"),
}
NEUTRAL = {"PLAIN": ("RANDOM", "STOCK"), "DENSE": ("RANDOM", "DENSE"), "PLANT": ("PLANT", "STOCK"),
           "SHAM": ("RANDOM", "SHAM")}


def byar(k, e):
    if e <= 0:
        return (None, None)
    if k == 0:
        return (0.0, 3.0 / e)
    lo = k * (1 - 1 / (9 * k) - 1.96 / (3 * math.sqrt(k))) ** 3
    k1 = k + 1
    hi = k1 * (1 - 1 / (9 * k1) + 1.96 / (3 * math.sqrt(k1))) ** 3
    return (lo / e, hi / e)


def run_stats(cps):
    """cps: checkpoint list (epoch-ordered). Returns (event, checkpoints_at_risk, evals_at_risk, first_epoch)."""
    n_cp, n_ev = 0, 0
    for c in sorted(cps, key=lambda c: c["epoch"]):
        n_cp += 1
        n_ev += c["distinct"]
        if c["L2"] > 0:
            return 1, n_cp, n_ev, c["epoch"]
    return 0, n_cp, n_ev, None


def summarize(rows):
    ev = sum(r[0] for r in rows)
    cp = sum(r[1] for r in rows)
    evals = sum(r[2] for r in rows)
    return {"runs": len(rows), "runs_with_competent": ev, "checkpoints_at_risk": cp, "evals_at_risk": evals,
            "hazard_per_checkpoint": round(ev / cp, 5) if cp else None,
            "hazard_per_checkpoint_95": [round(x, 5) if x is not None else None for x in byar(ev, cp)],
            "hazard_per_eval": ev / evals if evals else None,
            "hazard_per_eval_95": list(byar(ev, evals)),
            "evals_per_event": round(evals / ev, 1) if ev else None,
            "first_epochs": sorted(r[3] for r in rows if r[3] is not None)}


def main():
    neut = {}
    for f in glob.glob(str(A.HERE / "results_neutral" / "*.json")):
        x = json.loads(open(f).read())
        if x.get("epochs") != 2000:
            continue
        neut[(x["material"], x["cell"], x["seed"])] = x
    seeds_done = sorted({(k[1], k[2]) for k in neut})
    out = {"paired_seeds": ["%s/%d" % s for s in seeds_done], "arms": {}}
    for arm, (d, pat) in SOUP.items():
        mat, vmn = NEUTRAL[arm]
        for scope in ("paired", "all48"):
            srows, nrows = [], []
            for cell in ("7ae3", "ffa6"):
                for s in range(48):
                    seed = 16_000_000 + s
                    if scope == "paired" and (mat, cell, seed) not in neut:
                        continue
                    p = d / pat.format(cell=cell, seed=seed)
                    srows.append(run_stats(json.loads(p.read_text())["checkpoints"]))
                    if (mat, cell, seed) in neut:
                        nrows.append(run_stats(neut[(mat, cell, seed)]["arms"][vmn]))
            out["arms"].setdefault(arm, {})["soup_" + scope] = summarize(srows)
            if scope == "paired":
                out["arms"][arm]["neutral_paired"] = summarize(nrows)
    # per-run pairing table
    tab = []
    for (mat, cell, seed), x in sorted(neut.items()):
        for arm, (m2, vmn) in NEUTRAL.items():
            if m2 != mat:
                continue
            d, pat = SOUP[arm]
            sp = json.loads((d / pat.format(cell=cell, seed=seed)).read_text())["checkpoints"]
            s_ev = run_stats(sp)
            n_ev = run_stats(x["arms"][vmn])
            nb = max(c["best_fid_final"] for c in x["arms"][vmn])
            n_s1 = sum(c["stage1"] for c in x["arms"][vmn])
            tab.append({"arm": arm, "cell": cell, "seed": seed, "soup_first_L2": s_ev[3], "neutral_first_L2": n_ev[3],
                        "neutral_stage1_genomes_total": n_s1, "neutral_best_fid": nb,
                        "soup_stage1_genomes_total": sum(c["stage1"] for c in sp),
                        "neutral_L1c_e100": x["arms"][vmn][0]["L1c"], "neutral_L1c_e2000": x["arms"][vmn][-1]["L1c"],
                        "soup_L1c_e100": sp[0].get("L1c"), "soup_L1c_e2000": sp[-1].get("L1c")})
    out["pairs"] = tab
    (A.HERE / "compare.json").write_text(json.dumps(out, indent=1))
    for arm, v in out["arms"].items():
        print(arm, json.dumps({k: {kk: v[k][kk] for kk in ("runs", "runs_with_competent", "evals_at_risk",
                                                            "hazard_per_eval", "first_epochs")} for k in v}))
    for t in tab:
        print(t)


if __name__ == "__main__":
    main()

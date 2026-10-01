"""Out-of-sample test, step 2: pre-registered statistics on oos_predict.json.

    python -B oos_stats.py   -> oos_stats.json

O1 = lineage_births >= 1: ROC AUC (Mann-Whitney, ties = 1/2), one-sided permutation p (label shuffle, 20,000),
     bootstrap 95% CI (donor resampling, 2,000; resamples with one class only are skipped).
O2 = lineage_births >= 29: Spearman(predictor, lineage_births) (average ranks), one-sided permutation p (20,000),
     bootstrap 95% CI. Also reported (not decisive): AUC for the O2 binary, Spearman against O1.
Frozen criterion: O1 AUC >= 0.75 and p < 0.01; O2 rho >= 0.4 and p < 0.01. Both -> PASS; one -> PARTIAL; none -> FAIL.
Decisive predictor: P_run500_causal. Comparators (not decisive): P_est, P_est_causal, P_run500, m, P_run2, child_conv.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np
from scipy.stats import rankdata

HERE = pathlib.Path(__file__).resolve().parent
D = json.loads((HERE / "oos_predict.json").read_text())
RNG = np.random.default_rng(20261001)
NPERM, NBOOT = 20000, 2000
PREDS = ("P_run500_causal", "P_est", "P_est_causal", "P_run500", "m", "P_run2", "child_conv")


def auc(x, y):
    x, y = np.asarray(x, float), np.asarray(y, bool)
    if y.all() or not y.any():
        return float("nan")
    r = rankdata(x)
    n1, n0 = y.sum(), (~y).sum()
    return float((r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if np.ptp(x) == 0 or np.ptp(y) == 0:
        return float("nan")
    return float(np.corrcoef(rankdata(x), rankdata(y))[0, 1])


def perm_p(f, x, y):
    s0 = f(x, y)
    if s0 != s0:
        return None
    y = np.asarray(y)
    ge = sum(1 for _ in range(NPERM) if (lambda s: s == s and s >= s0 - 1e-12)(f(x, RNG.permutation(y))))
    return (ge + 1) / (NPERM + 1)


def boot(f, x, y):
    x, y = np.asarray(x, float), np.asarray(y)
    v = []
    for _ in range(NBOOT):
        i = RNG.integers(0, len(x), len(x))
        s = f(x[i], y[i])
        if s == s:
            v.append(s)
    return [round(float(np.percentile(v, 2.5)), 3), round(float(np.percentile(v, 97.5)), 3)] if v else None


def block(R):
    b = np.array([r["lineage_births"] for r in R], float)
    o1, o2 = b >= 1, b >= 29
    out = {"n": len(R), "n_O1_pos": int(o1.sum()), "n_O2_pos": int(o2.sum())}
    for p in PREDS:
        x = np.array([r[p] for r in R], float)
        out[p] = {"O1_auc": round(auc(x, o1), 4), "O1_auc_perm_p": perm_p(auc, x, o1), "O1_auc_ci95": boot(auc, x, o1),
                  "O2_rho_births": round(spearman(x, b), 4), "O2_rho_perm_p": perm_p(spearman, x, b),
                  "O2_rho_ci95": boot(spearman, x, b),
                  "O2_auc_binary": round(auc(x, o2), 4), "O1_rho_births_binary": round(spearman(x, o1), 4),
                  "mean_O1_pos": round(float(x[o1].mean()), 4), "mean_O1_neg": round(float(x[~o1].mean()), 4)}
        print(p, len(R), out[p]["O1_auc"], out[p]["O1_auc_perm_p"], out[p]["O2_rho_births"], out[p]["O2_rho_perm_p"],
              flush=True)
    return out


def verdict(e):
    o1 = e["O1_auc"] >= 0.75 and (e["O1_auc_perm_p"] or 1) < 0.01
    o2 = e["O2_rho_births"] >= 0.4 and (e["O2_rho_perm_p"] or 1) < 0.01
    return {"O1_met": o1, "O2_met": o2, "verdict": "PASS" if o1 and o2 else "PARTIAL" if o1 or o2 else "FAIL"}


def main():
    R = D["rows"]
    res = {"all": block(R)}
    res["verdict_primary"] = verdict(res["all"]["P_run500_causal"])
    res["verdict_if_comparator"] = {p: verdict(res["all"][p]) for p in PREDS}
    for c in ("7ae3", "ffa6"):          # descriptive only
        res["cell_" + c] = block([r for r in R if r["cell"] == c])
    (HERE / "oos_stats.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res["verdict_primary"]))


if __name__ == "__main__":
    main()

"""Out-of-sample test, step 3 (descriptive, NOT decisive; written after oos_stats.py was run).

    python -B oos_sensitivity.py   -> oos_sensitivity.json

(a) Worst-case bound for the 5 runs excluded as 'D0 exists but no source records its genome' (all have
    lineage_births 1-13, i.e. O1-positive, O2-negative): give each the LOWEST possible predictor value (0.0, tied with
    the negatives' floor) and the best (1.0), recompute O1 AUC and O2 Spearman.
(b) Baselines from W1's own prior measurements (x_dd_nocopy_context rates, x_dd_selfstate label), to show how much
    the map adds beyond what W1 already measured for the same genomes.
"""
import glob, json, pathlib
import numpy as np
import oos_stats as S
HERE = pathlib.Path(__file__).resolve().parent
D = json.loads((HERE / "oos_predict.json").read_text())
W1 = HERE.parents[1] / "campaigns" / "npe-w1-donor-discovery-2026-09-26"
R, X = D["rows"], [e for e in D["excluded"] if e["status"] != "NO_D0"]
out = {}
for fill in (0.0, 1.0):
    x = np.array([r["P_run500_causal"] for r in R] + [fill] * len(X))
    b = np.array([r["lineage_births"] for r in R] + [e["lineage_births"] for e in X], float)
    out["fill_%.1f" % fill] = {"n": len(x), "O1_auc": round(S.auc(x, b >= 1), 4), "O1_p": S.perm_p(S.auc, x, b >= 1),
                               "O2_rho": round(S.spearman(x, b), 4), "O2_p": S.perm_p(S.spearman, x, b)}
nc = {(j["cell"], int(j["seed"])): j for j in (json.loads(open(f).read()) for f in glob.glob(str(W1 / "x_dd_nocopy_context/results/*.json")))}
ss = {(j["cell"], int(j["seed"])): j for j in (json.loads(open(f).read()) for f in glob.glob(str(W1 / "x_dd_selfstate/results/*.json")))}
b = np.array([r["lineage_births"] for r in R], float)
base = {}
for name, f in (("nc_OWN_REAL", lambda r: nc[(r["cell"], r["seed"])]["rates"].get("OWN_REAL", 0.0)),
                ("nc_OWN_BLANK", lambda r: nc[(r["cell"], r["seed"])]["rates"].get("OWN_BLANK", 0.0)),
                ("ss_rate_k1", lambda r: ss[(r["cell"], r["seed"])]["rates_by_k"][1] if (r["cell"], r["seed"]) in ss else float("nan")),
                ("ss_SELF_OK", lambda r: (1.0 if ss[(r["cell"], r["seed"])]["label"] == "SELF_OK" else 0.0) if (r["cell"], r["seed"]) in ss else float("nan"))):
    x = np.array([f(r) for r in R], float)
    k = ~np.isnan(x)
    base[name] = {"n": int(k.sum()), "O1_auc": round(S.auc(x[k], b[k] >= 1), 4), "O1_p": S.perm_p(S.auc, x[k], b[k] >= 1),
                  "O2_rho": round(S.spearman(x[k], b[k]), 4), "O2_p": S.perm_p(S.spearman, x[k], b[k])}
out["w1_baselines"] = base
(HERE / "oos_sensitivity.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))

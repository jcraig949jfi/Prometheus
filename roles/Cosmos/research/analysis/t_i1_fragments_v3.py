"""T-I1 fragment test v3 -- repairs v2's tie defect (calibration/LEDGER.md 2026-09-29, second entry).

Declared BEFORE running (committed first). v1 and v2 results stay as recorded.

v2 diagnosis (measured on R-0002b's null, seed 1): every null member with agree >= .99 matched rung atom R3
(Q < 1, positive rate .076). Q = 1 on ~92% of battery rows, so expressions of Q are heavily TIED, and the
quantile threshold cannot hit the atom's rate: such an expression collapses onto the Q < 1 split. The
"marginal-matched" null was not marginal-matched under ties.

Only change from v2: a null member is REJECTED unless its REALIZED positive rate on the battery is within
+-0.02 of the atom's rate (the rejects are counted). Everything else is v2 (exact-size draws, rung-equivalent
exclusion at |rho| >= .999, reachability check before verdicts, the decision rule, seed 20260929, 2,000 draws).

PYTHONPATH=".;roles/Cosmos/research/analysis" python roles/Cosmos/research/analysis/t_i1_fragments_v3.py
"""
import json
import random
from pathlib import Path

import numpy as np

from prometheus.cosmos.miner import enumerate_exprs, evaluate_expr, size
from t_i1_fragments import ATOMS, TERMS, agree, battery, rung, truth
from t_i1_fragments_v2 import NNULL, RHO_EQ, SEED, spearman

RATE_TOL = 0.02


def main():
    X = battery()
    R = rung(X)
    rung_vals = [X["G"] * np.exp(-X["N"]) - X["C"], X["C"] * X["K"], X["Q"]]
    by_size = {}
    for e in enumerate_exprs(TERMS, 6):
        by_size.setdefault(size(e), []).append(e)
    rng = random.Random(SEED)
    out = []
    for aid, e, d, t in ATOMS:
        a = truth(e, d, t, X)
        rate = float(np.mean(a))
        null, excl_eq, excl_rate, tries = [], 0, 0, 0
        while len(null) < NNULL and tries < 50 * NNULL:
            tries += 1
            ev = evaluate_expr(rng.choice(by_size[size(e)]), X)
            ev = np.where(np.isfinite(ev), ev, np.nan)
            if np.all(np.isnan(ev)) or np.nanstd(ev) == 0:
                continue
            if any(abs(spearman(ev, rv)) >= RHO_EQ for rv in rung_vals):
                excl_eq += 1
                continue
            b = np.where(np.isnan(ev), False, ev <= np.nanquantile(ev, rate))
            if abs(float(np.mean(b)) - rate) > RATE_TOL:
                excl_rate += 1
                continue
            null.append(agree(b, R))
        null = np.array(null)
        obs = agree(a, R)
        q99 = float(np.quantile(null, 0.99)) if len(null) else float("nan")
        if len(null) < 200 or q99 >= 0.99:
            verdict = "INDETERMINATE_GATE"
        elif obs > q99 and obs >= 0.90:
            verdict = "REEXPRESSES_RUNG"
        else:
            verdict = "NOT_RUNG"
        out.append({"atom": aid, "size": size(e), "pos_rate": round(rate, 3), "agree": round(obs, 3),
                    "null_n": len(null), "excl_rung_equiv": excl_eq, "excl_rate_mismatch": excl_rate,
                    "null_q50": round(float(np.median(null)), 3), "null_q99": round(q99, 3),
                    "p": round(float(np.mean(null >= obs)), 4), "verdict": verdict})
    for r in out:
        print("{atom:8s} size {size}  agree {agree:.3f}  null n {null_n} (excl eq {excl_rung_equiv}, rate "
              "{excl_rate_mismatch})  q50 {null_q50:.3f} q99 {null_q99:.3f}  p {p:.4f}  {verdict}".format(**r))
    groups = {"survived R-*": "R-", "robust kill G-0004": "G-0004", "marginal kill G-0005": "G-0005"}
    summary = {k: round(float(np.mean([r["agree"] for r in out if r["atom"].startswith(p)])), 3)
               for k, p in groups.items()}
    summary["C0 adversary kills G-0001..3"] = round(float(np.mean(
        [r["agree"] for r in out if r["atom"][:6] in ("G-0001", "G-0002", "G-0003")])), 3)
    print("secondary (mean agree):", summary)
    json.dump({"atoms": out, "secondary_mean_agree": summary}, open(Path(__file__).with_suffix(".json"), "w"), indent=1)


if __name__ == "__main__":
    main()

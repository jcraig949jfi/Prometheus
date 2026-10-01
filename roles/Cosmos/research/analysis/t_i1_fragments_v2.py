"""T-I1 fragment test v2 -- repairs v1's unreachable gate (calibration/LEDGER.md 2026-09-29).

Declared BEFORE running (committed first). Same probe battery, rung atoms, atoms and statistic as v1
(t_i1_fragments.py); only the null and the gate changed. v1's result stays as recorded.

Changes from v1:
1. Null expressions are drawn at EXACTLY the atom's grammar size (no cap at 5).
2. The null EXCLUDES rung-equivalent expressions: any expression whose values on the battery have
   |Spearman rho| >= 0.999 with one of the rung expressions (G exp(-N) - C, C K, Q). Without this, the null's
   tail is the rung itself (v1's defect).
3. Reachability is checked BEFORE verdicts: if the filtered null's q99 >= 0.99 for an atom, that atom's
   verdict is INDETERMINATE_GATE (unreachable), not NOT_RUNG.
Decision rule (per atom): REEXPRESSES_RUNG if agree > null q99 AND agree >= 0.90 (q99 < 0.99 required);
NOT_RUNG if agree <= null q99 and q99 < 0.99; INDETERMINATE_GATE otherwise. Seed 20260929, 2,000 null
draws per atom.
Secondary (descriptive, declared now): mean agree of atoms from SURVIVED laws (R-*) vs atoms from ROBUST
kills (G-0004, whose kills held at tolerance 0.20) vs marginal kills (G-0005) vs C0 adversary kills
(G-0001..3).

PYTHONPATH=".;roles/Cosmos/research/analysis" python roles/Cosmos/research/analysis/t_i1_fragments_v2.py -> table + t_i1_fragments_v2.json
"""
import json
import random
from pathlib import Path

import numpy as np

from prometheus.cosmos.miner import enumerate_exprs, evaluate_expr, size
from t_i1_fragments import ATOMS, TERMS, agree, battery, rung, truth  # same battery, atoms, statistic

SEED, NNULL, RHO_EQ = 20260929, 2000, 0.999


def rank(v):
    v = np.where(np.isfinite(v), v, np.nan)
    ok = ~np.isnan(v)
    r = np.full(v.shape, np.nan)
    r[ok] = np.argsort(np.argsort(v[ok]))
    return r


def spearman(a, b):
    ra, rb = rank(a), rank(b)
    ok = ~np.isnan(ra) & ~np.isnan(rb)
    if ok.sum() < 10 or np.std(ra[ok]) == 0 or np.std(rb[ok]) == 0:
        return 0.0
    return float(np.corrcoef(ra[ok], rb[ok])[0, 1])


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
        null, excluded, tries = [], 0, 0
        while len(null) < NNULL and tries < 20 * NNULL:
            tries += 1
            ev = evaluate_expr(rng.choice(by_size[size(e)]), X)
            ev = np.where(np.isfinite(ev), ev, np.nan)
            if np.all(np.isnan(ev)) or np.nanstd(ev) == 0:
                continue
            if any(abs(spearman(ev, rv)) >= RHO_EQ for rv in rung_vals):
                excluded += 1
                continue
            thr = np.nanquantile(ev, rate)
            null.append(agree(np.where(np.isnan(ev), False, ev <= thr), R))
        null = np.array(null)
        obs = agree(a, R)
        q99 = float(np.quantile(null, 0.99))
        if q99 >= 0.99:
            verdict = "INDETERMINATE_GATE"
        elif obs > q99 and obs >= 0.90:
            verdict = "REEXPRESSES_RUNG"
        else:
            verdict = "NOT_RUNG"
        out.append({"atom": aid, "size": size(e), "pos_rate": round(rate, 3), "agree": round(obs, 3),
                    "null_n": len(null), "null_excluded_rung_equiv": excluded,
                    "null_q50": round(float(np.median(null)), 3), "null_q99": round(q99, 3),
                    "p": round(float(np.mean(null >= obs)), 4), "verdict": verdict})
    for r in out:
        print("{atom:8s} size {size}  agree {agree:.3f}  null n {null_n} excl {null_excluded_rung_equiv} "
              "q50 {null_q50:.3f} q99 {null_q99:.3f}  p {p:.4f}  {verdict}".format(**r))
    groups = {"survived R-*": [r for r in out if r["atom"].startswith("R-")],
              "robust kill G-0004": [r for r in out if r["atom"].startswith("G-0004")],
              "marginal kill G-0005": [r for r in out if r["atom"].startswith("G-0005")],
              "C0 adversary kills G-0001..3": [r for r in out if r["atom"][:6] in ("G-0001", "G-0002", "G-0003")]}
    summary = {k: round(float(np.mean([r["agree"] for r in v])), 3) for k, v in groups.items()}
    print("secondary (mean agree):", summary)
    json.dump({"atoms": out, "secondary_mean_agree": summary}, open(Path(__file__).with_suffix(".json"), "w"), indent=1)


if __name__ == "__main__":
    main()

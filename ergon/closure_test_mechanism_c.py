#!/usr/bin/env python3
"""
Mechanism (c) closure test — per Aporia 1776897662719.

Joint cell-level regression:
  gap1_cell_deficit ~ mean_log|D| + torsion_rarity_bin + mean_log(N) + cell_n
  predictors come from LMFDB rank-0 EC cells stratified by (cm, torsion, log_N decile).
  response is the per-cell matched-GUE null deficit for gap1 (% deficit = (1 - var/null) * 100).

If joint R^2 -> 1, mechanism (c) is a complete explanation of F011 compression.
If R^2 < 0.5, residual unexplained signal remains.

Fetches from LMFDB: cm::int (CM discriminant, 0 for non-CM), torsion::int,
conductor::float, positive_zeros for rank-0 EC.

Output: ergon/results/closure_test_mechanism_c.json.
"""
import json
import math
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import psycopg2
from scipy import stats

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
OUT = Path(__file__).resolve().parent / "results" / "closure_test_mechanism_c.json"
NULL_VAR = [0.1472, 0.1741, 0.1725, 0.1468]
NULL_M = 200000


def parse_zeros(raw):
    if raw is None:
        return None
    s = str(raw).strip()
    if s in ('', '[]', '{}', 'None'):
        return None
    s = s.replace('{', '[').replace('}', ']')
    try:
        return [float(z) for z in json.loads(s)]
    except Exception:
        return None


def local_4gap(zeros):
    if zeros is None or len(zeros) < 5:
        return None
    zeros = sorted(zeros)[:5]
    gaps = [zeros[i+1] - zeros[i] for i in range(4)]
    m = np.mean(gaps)
    if m <= 0:
        return None
    return [g / m for g in gaps]


def fetch():
    print("Fetching 200K rank-0 EC with cm + torsion + conductor + zeros ...")
    t0 = time.time()
    c = psycopg2.connect(**DB)
    cur = c.cursor()
    cur.execute("""
        SELECT e.cm::int,
               e.torsion::int,
               e.conductor::float,
               l.positive_zeros
        FROM ec_curvedata e
        JOIN lfunc_lfunctions l
          ON l.origin = 'EllipticCurve/Q/' || split_part(e.lmfdb_iso, '.', 1)
                         || '/' || split_part(e.lmfdb_iso, '.', 2)
        WHERE e.rank::int = 0
          AND l.positive_zeros IS NOT NULL
          AND l.positive_zeros != '[]'
        LIMIT 200000
    """)
    rows = cur.fetchall()
    cur.close()
    c.close()
    print(f"  {len(rows)} rows in {time.time()-t0:.0f}s")
    return rows


def main():
    print("Mechanism (c) closure test — joint regression")
    print("=" * 80)
    rows = fetch()

    # Parse each curve to (cm, torsion, log_N, gap1_normed)
    parsed = []
    for cm, tor, cond, raw in rows:
        if cond is None or cond <= 0:
            continue
        g = local_4gap(parse_zeros(raw))
        if g is None:
            continue
        parsed.append((int(cm or 0), int(tor or 0), math.log(cond), g))
    print(f"Parsed {len(parsed)} curves with valid gaps.\n")

    # Build cells: key = (|D|_bin, tor_bin, log_N_decile)
    logN_values = np.array([r[2] for r in parsed])
    logN_deciles = np.quantile(logN_values, np.linspace(0, 1, 11))

    def logN_bin(x):
        return int(np.clip(np.searchsorted(logN_deciles, x, side='right') - 1, 0, 9))

    def tor_bin(t):
        # Rarity: common (1,2), medium (3,4), rare (5,6,7,8,...)
        if t in (1, 2):
            return 1
        if t in (3, 4):
            return 2
        return 3

    def abs_D(cm):
        # 0 for non-CM; |cm| otherwise
        return abs(cm)

    cells = defaultdict(list)  # (D_bin, tor_bin, logN_bin) -> [g1 values]
    for cm, tor, logN, g in parsed:
        k = (abs_D(cm), tor_bin(tor), logN_bin(logN))
        cells[k].append(g)

    # For each cell with n >= 50, compute gap1 variance + deficit + predictor means
    cell_rows = []
    for key, data in cells.items():
        n = len(data)
        if n < 50:
            continue
        arr = np.array(data)  # (n, 4)
        v1 = float(arr[:, 0].var(ddof=1))
        deficit_g1 = (1 - v1 / NULL_VAR[0]) * 100.0
        d_bin, t_bin, logN_q = key
        cell_rows.append({
            'D_bin': d_bin,
            'log_Dplus1': math.log(d_bin + 1),  # log|D|, 0 for non-CM (D=0 -> log(1)=0)
            'tor_bin': t_bin,  # 1 common, 2 medium, 3 rare
            'logN_q': logN_q,
            'n': n,
            'g1_var': v1,
            'g1_deficit_pct': deficit_g1,
            'g2_var': float(arr[:, 1].var(ddof=1)),
            'g3_var': float(arr[:, 2].var(ddof=1)),
            'g4_var': float(arr[:, 3].var(ddof=1)),
        })
    print(f"Cells with n>=50: {len(cell_rows)}")

    # Regression: deficit_g1 ~ log_Dplus1 + tor_bin + logN_q
    if len(cell_rows) < 5:
        print("Too few cells for regression.")
        return

    X = np.array([[c['log_Dplus1'], c['tor_bin'], c['logN_q']] for c in cell_rows])
    y = np.array([c['g1_deficit_pct'] for c in cell_rows])
    weights = np.array([c['n'] for c in cell_rows])

    # OLS
    Xc = np.column_stack([np.ones(len(X)), X])
    beta, _, _, _ = np.linalg.lstsq(Xc, y, rcond=None)
    y_pred = Xc @ beta
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0

    # Weighted OLS (weight by cell size)
    W = np.diag(weights)
    # (X' W X) beta = X' W y
    XtWX = Xc.T @ W @ Xc
    XtWy = Xc.T @ W @ y
    beta_w = np.linalg.solve(XtWX, XtWy)
    y_pred_w = Xc @ beta_w
    ss_res_w = np.sum(weights * (y - y_pred_w) ** 2)
    ss_tot_w = np.sum(weights * (y - np.average(y, weights=weights)) ** 2)
    r2_w = 1 - ss_res_w / ss_tot_w if ss_tot_w > 0 else 0

    # Partial correlations per predictor
    print("\nCELL-LEVEL MODEL: gap1_deficit_pct ~ log|D| + tor_bin + logN_q")
    print(f"  OLS   beta = {beta}, R^2 = {r2:.4f}")
    print(f"  WLS   beta = {beta_w}, R^2_w = {r2_w:.4f}")

    # Per-predictor uncorrelated contributions via leave-one-out R^2 drop
    contributions = {}
    predictor_names = ['intercept', 'log|D|', 'tor_bin', 'logN_q']
    for k in range(1, Xc.shape[1]):
        Xk = np.delete(Xc, k, axis=1)
        bk, _, _, _ = np.linalg.lstsq(Xk, y, rcond=None)
        yp = Xk @ bk
        r2k = 1 - np.sum((y - yp) ** 2) / ss_tot if ss_tot > 0 else 0
        contributions[predictor_names[k]] = r2 - r2k
    print("  R^2 drop per predictor:")
    for k, v in contributions.items():
        print(f"    {k}: {v:.4f}")

    # Simple correlations
    print("\nSIMPLE CORRELATIONS (Spearman):")
    for j, name in enumerate(predictor_names[1:]):
        r, p = stats.spearmanr(X[:, j], y)
        print(f"  {name}: rho = {r:.4f}  p = {p:.3g}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump({
            'null_var': NULL_VAR,
            'n_cells': len(cell_rows),
            'cells': cell_rows,
            'ols_beta': beta.tolist(),
            'ols_r2': r2,
            'wls_beta': beta_w.tolist(),
            'wls_r2': r2_w,
            'r2_drop_per_predictor': contributions,
        }, f, indent=1, default=str)
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    main()

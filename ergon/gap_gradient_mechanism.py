#!/usr/bin/env python3
"""
F011 gap-index-gradient mechanism test (Aporia mechanism a).

Question: does the EC rank-0 gap-compression (z=-48 to -103 vs matched-GUE null)
SURVIVE conductor stratification? If the gradient is conductor-dependent (finite-N
level-repulsion memory), stratifying by conductor decile should change the gap4 vs
gap1 deficit ratio. If the gradient is conductor-invariant, it is not a simple
finite-N effect and must be structural.

Procedure:
  1. Fetch rank-0 EC zeros + conductor + Sha from LMFDB.
  2. For each (conductor decile, Sha bin): compute local-4-gap variance per curve,
     pool, measure mean/var across the cell.
  3. Compare each cell's gap1..gap4 variance to the matched-GUE null (previously
     computed: 0.1472, 0.1741, 0.1725, 0.1468 for N=40, local 4-gap, M=200K).
  4. Report deficit pattern per cell.

Null reference (from prior sim at N=40, M=200K, local-4-gap normalization):
  gap1 null = 0.1472
  gap2 null = 0.1741
  gap3 null = 0.1725
  gap4 null = 0.1468

Output: ergon/results/gap_gradient_mechanism.json + stdout table.
"""
import json
import math
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import psycopg2

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
OUT = Path(__file__).resolve().parent / "results" / "gap_gradient_mechanism.json"

NULL_VAR = [0.1472, 0.1741, 0.1725, 0.1468]  # matched-GUE local-4-gap null variances
NULL_M = 200000  # null sample count (for SE)


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


def deficit(observed_var, null_var, n, null_n=NULL_M):
    """Return (deficit_pct, z_score) for observed var vs null_var."""
    diff = observed_var - null_var
    # SE of difference between two sample variances of lognormal-ish distributions
    # Approximate: SE(v) = sqrt(2 * v^2 / n) for normal-like samples.
    se_obs = math.sqrt(2 * observed_var * observed_var / max(n, 2))
    se_null = math.sqrt(2 * null_var * null_var / null_n)
    se_diff = math.sqrt(se_obs ** 2 + se_null ** 2)
    z = diff / se_diff if se_diff > 0 else 0.0
    pct = (1.0 - observed_var / null_var) * 100 if null_var else 0.0
    return pct, z


def main():
    print("F011 gap-index-gradient mechanism test (conductor + Sha stratification)")
    print("=" * 80)
    print(f"Matched-GUE null variances (local-4-gap, N=40, M=200K):")
    for i, v in enumerate(NULL_VAR):
        print(f"  gap{i+1} null = {v:.4f}")
    print()

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    print("Fetching rank-0 EC zeros + conductor + Sha ...")
    t0 = time.time()
    cur.execute("""
        SELECT e.sha::int,
               e.conductor::float,
               l.positive_zeros
        FROM ec_curvedata e
        JOIN lfunc_lfunctions l
          ON l.origin = 'EllipticCurve/Q/' || split_part(e.lmfdb_iso, '.', 1)
                         || '/' || split_part(e.lmfdb_iso, '.', 2)
        WHERE e.rank::int = 0
          AND l.positive_zeros IS NOT NULL
          AND l.positive_zeros != '[]'
          AND e.sha::int >= 1
        LIMIT 200000
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    print(f"  fetched {len(rows)} rows in {time.time()-t0:.0f}s")

    parsed = []
    for sha, cond, raw in rows:
        if sha is None or cond is None:
            continue
        gaps = local_4gap(parse_zeros(raw))
        if gaps is None:
            continue
        parsed.append((int(sha), float(cond), gaps))
    print(f"  parsed {len(parsed)} valid curves\n")

    conds = np.array([r[1] for r in parsed])
    log_conds = np.log(np.clip(conds, 1, None))
    deciles = np.quantile(log_conds, np.linspace(0, 1, 11))
    print(f"log-conductor deciles: {[f'{d:.2f}' for d in deciles]}\n")

    # Sha bins: Sha=1 (isolated), Sha=4, Sha=9, Sha>=16
    def sha_bin(s):
        if s <= 1: return 1
        if s <= 4: return 4
        if s <= 9: return 9
        return 16

    # Cell indexing: (cond_decile, sha_bin)
    cells = defaultdict(list)
    for sha, cond, gaps in parsed:
        q = int(np.clip(np.searchsorted(deciles, math.log(max(cond, 1)), side='right') - 1, 0, 9))
        cells[(q, sha_bin(sha))].append(gaps)

    # Summary per cell: variances + deficit %
    rows_out = []
    print(f"{'cond_Q':>6} {'sha':>5} {'n':>7}   " + " ".join(
        f"g{i+1}_var  g{i+1}%(z)" for i in range(4)
    ))
    print("-" * 100)

    sha_order = [1, 4, 9, 16]
    for q in range(10):
        for sb in sha_order:
            data = cells.get((q, sb), [])
            n = len(data)
            if n < 50:  # require enough
                continue
            arr = np.array(data)  # shape (n, 4)
            variances = arr.var(axis=0, ddof=1)
            cells_out = {
                'cond_decile': q,
                'sha_bin': sb,
                'n': n,
                'variances': [float(v) for v in variances],
                'deficits_pct': [],
                'z_scores': [],
            }
            line = f"{q:>6} {sb:>5} {n:>7}   "
            for i, v in enumerate(variances):
                pct, z = deficit(v, NULL_VAR[i], n)
                cells_out['deficits_pct'].append(round(pct, 2))
                cells_out['z_scores'].append(round(z, 2))
                line += f"{v:.4f} {pct:+5.1f}({z:+6.1f})  "
            print(line)
            rows_out.append(cells_out)

    # Aggregate: conductor effect on gap-gradient
    print("\n" + "=" * 80)
    print("Gradient attenuation: gap4 - gap1 deficit by conductor decile")
    print("=" * 80)
    by_q = defaultdict(list)
    for c in rows_out:
        d = c['deficits_pct']
        by_q[c['cond_decile']].append((c['sha_bin'], c['n'], d[0], d[3], d[3] - d[0]))
    print(f"{'cond_Q':>6} {'sha':>5} {'n':>7} {'gap1%':>7} {'gap4%':>7} {'gap4-gap1':>10}")
    for q in sorted(by_q):
        for sb, n, d1, d4, grad in by_q[q]:
            print(f"{q:>6} {sb:>5} {n:>7} {d1:>7.1f} {d4:>7.1f} {grad:>10.2f}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump({
            "null_var": NULL_VAR,
            "null_M": NULL_M,
            "decile_boundaries": [float(d) for d in deciles],
            "cells": rows_out,
        }, f, indent=1)
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    main()

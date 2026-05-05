#!/usr/bin/env python3
"""
CM 24-gap scan — per Aporia/Charon queue after Seed 11.

Test: does CM rank-0 EC show a DIFFERENT edge/bulk pattern than non-CM?
Under Katz-Sarnak, CM EC has U(1)^N-type symmetry (Hecke characters of IQFs),
which predicts DIFFERENT edge statistics from O+(even). Bulk should still be
universal but finite-N corrections may differ.

Data: 2134 CM rank-0 EC (my cm_only_fast sample). Only curves with >=25 zeros.

Output: ergon/results/cm_gap_k.json
"""
import json
import math
import time
from pathlib import Path

import numpy as np
import psycopg2

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
OUT = Path(__file__).resolve().parent / "results" / "cm_gap_k.json"
K_MAX = 24


def parse_zeros(raw):
    if raw is None: return None
    s = str(raw).strip()
    if s in ('','[]','{}','None'): return None
    s = s.replace('{','[').replace('}',']')
    try: return [float(z) for z in json.loads(s)]
    except: return None


def local_k_gaps(zeros, kmax=K_MAX):
    if zeros is None or len(zeros) < kmax + 1:
        return None
    zeros = sorted(zeros)[:kmax + 1]
    gaps = np.array([zeros[i+1] - zeros[i] for i in range(kmax)])
    m = np.mean(gaps)
    if m <= 0: return None
    return gaps / m


def gue_null(kmax, M, N, rng):
    mid = N // 2 - kmax // 2
    out = np.zeros((M, kmax))
    for m in range(M):
        re = rng.standard_normal((N, N))
        im = rng.standard_normal((N, N))
        A = (re + 1j * im) / np.sqrt(2.0)
        H = (A + A.conj().T) / np.sqrt(2.0)
        w = np.sort(np.linalg.eigvalsh(H))
        gaps = np.diff(w)
        local = gaps[mid:mid+kmax]
        lm = local.mean()
        if lm <= 0: continue
        out[m] = local / lm
    return out


def main():
    print("CM 24-gap scan")
    print("=" * 72)

    print("Fetching CM rank-0 EC with >=25 zeros...")
    t0 = time.time()
    c = psycopg2.connect(**DB); cur = c.cursor()
    cur.execute("""
        SELECT e.cm::int, l.positive_zeros
        FROM ec_curvedata e
        JOIN lfunc_lfunctions l
          ON l.origin = 'EllipticCurve/Q/' || split_part(e.lmfdb_iso, '.', 1)
                         || '/' || split_part(e.lmfdb_iso, '.', 2)
        WHERE e.rank::int = 0
          AND e.cm::int != 0
          AND l.positive_zeros IS NOT NULL
          AND l.positive_zeros != '[]'
    """)
    rows = cur.fetchall()
    cur.close(); c.close()
    print(f"  {len(rows)} rows in {time.time()-t0:.0f}s")

    # Collect per-curve gaps AND per-|cm|
    all_gaps = []
    by_cm = {}
    for cm, raw in rows:
        g = local_k_gaps(parse_zeros(raw), K_MAX)
        if g is None: continue
        all_gaps.append(g)
        by_cm.setdefault(abs(cm), []).append(g)

    all_gaps = np.array(all_gaps)
    print(f"  {len(all_gaps)} CM curves with 24 gaps each")

    # Generate matched GUE null
    print("\nGenerating matched-GUE null (50K matrices)...")
    rng = np.random.default_rng(3000)
    null = gue_null(K_MAX, M=50000, N=40, rng=rng)
    null_var = null.var(axis=0, ddof=1)

    # Pooled CM deficit
    data_var = all_gaps.var(axis=0, ddof=1)
    deficits = (1 - data_var / null_var) * 100
    print(f"\nPOOLED CM (n={len(all_gaps)}):")
    print(f"{'k':>3} {'data':>8} {'null':>8} {'deficit%':>9}")
    for k in range(K_MAX):
        print(f"{k+1:>3} {data_var[k]:>8.4f} {null_var[k]:>8.4f} {deficits[k]:>+9.2f}")

    # Per-|D| if enough curves
    print("\nPer-|D| (where n>=50):")
    per_cm = {}
    for cm_val in sorted(by_cm):
        data = by_cm[cm_val]
        if len(data) < 50:
            continue
        arr = np.array(data)
        v = arr.var(axis=0, ddof=1)
        d = (1 - v / null_var) * 100
        per_cm[cm_val] = {
            'n': len(data),
            'deficits_pct': d.tolist(),
        }
        print(f"  cm=-{cm_val} n={len(data)}: k=1:{d[0]:+.1f} k=4:{d[3]:+.1f} k=8:{d[7]:+.1f} k=16:{d[15]:+.1f} k=24:{d[23]:+.1f}")

    # Save
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump({
            'k_max': K_MAX,
            'n_cm_total': len(all_gaps),
            'pooled_deficits_pct': deficits.tolist(),
            'null_var_per_k': null_var.tolist(),
            'per_cm': {str(k): v for k, v in per_cm.items()},
        }, f, indent=1)
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    main()

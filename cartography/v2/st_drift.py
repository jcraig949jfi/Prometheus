#!/usr/bin/env python3
"""
Sato-Tate Moment Drift Under Double-Prime Conditioning
========================================================
For each pair (ell1, ell2) in {3,5,7}:
  1. Compute mod-ell1 residue class: partition forms by a_{ell1} mod ell1.
  2. Within each ell1-class, sub-partition by a_{ell2} mod ell2.
  3. Compute the Sato-Tate moment vector (M2, M4) of normalised a_p/(2*sqrt(p))
     for primes p up to 997, excluding ell1, ell2, and bad primes.
  4. DRIFT = ||conditional_moment_vec - unconditional_moment_vec||_2.
  5. Fit drift ~ (ell1 * ell2)^{-delta}.

Also runs full-fingerprint clustering (CT1-style, 25 primes) for ell1=3
where statistics are sufficient.

Charon / Project Prometheus -- 2026-04-10
"""

import json
import math
import time
from collections import defaultdict
from pathlib import Path

import duckdb
import numpy as np
from scipy.optimize import curve_fit

# -- Config -----------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]  # F:\Prometheus
DB_PATH = REPO_ROOT / "charon" / "data" / "charon.duckdb"
OUT_PATH = Path(__file__).resolve().parent / "st_drift_results.json"

PRIMES_25 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
             31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
             73, 79, 83, 89, 97]

def sieve_primes(n):
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]

ST_PRIMES = sieve_primes(997)  # 168 primes

ELLS = [3, 5, 7]


def prime_factors(n):
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors


def load_forms():
    print(f"[load] Connecting to {DB_PATH}")
    con = duckdb.connect(str(DB_PATH), read_only=True)
    rows = con.execute('''
        SELECT lmfdb_label, level, traces
        FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND traces IS NOT NULL
        ORDER BY level, lmfdb_label
    ''').fetchall()
    con.close()
    print(f"[load] {len(rows)} forms loaded")
    return rows


def compute_fingerprint(traces, level, ell):
    bad_primes = prime_factors(level)
    fp = []
    for p in PRIMES_25:
        if p in bad_primes:
            fp.append(-1)
        else:
            if p - 1 < len(traces):
                ap = int(round(traces[p - 1]))
                fp.append(ap % ell)
            else:
                fp.append(-1)
    return tuple(fp)


def compute_st_moments(traces_list, levels, exclude_primes=None):
    """
    M2, M4 of x_p = a_p / (2*sqrt(p)) over all (form, prime) pairs.
    SU(2) theory: M2 = 1/4, M4 = 1/8.
    """
    if exclude_primes is None:
        exclude_primes = set()

    sum_x2 = 0.0
    sum_x4 = 0.0
    n_pts = 0

    for traces, level in zip(traces_list, levels):
        bad = prime_factors(level) | exclude_primes
        for p in ST_PRIMES:
            if p in bad:
                continue
            if p - 1 >= len(traces):
                continue
            ap = traces[p - 1]
            x = ap / (2.0 * math.sqrt(p))
            x2 = x * x
            sum_x2 += x2
            sum_x4 += x2 * x2
            n_pts += 1

    if n_pts == 0:
        return None, None, 0
    return sum_x2 / n_pts, sum_x4 / n_pts, n_pts


def fit_power_law(products, drifts, label):
    """Fit drift ~ A * product^(-delta). Returns dict."""
    products = np.array(products, dtype=float)
    drifts = np.array(drifts)

    if len(products) < 2:
        return {"error": "insufficient data", "n_points": len(products)}

    # Log-log linear fit
    log_p = np.log(products)
    log_d = np.log(np.clip(drifts, 1e-15, None))
    coeffs = np.polyfit(log_p, log_d, 1)
    delta_ll = -coeffs[0]
    A_ll = np.exp(coeffs[1])

    # Nonlinear fit
    def power_law(x, A, delta):
        return A * x ** (-delta)

    try:
        popt, pcov = curve_fit(power_law, products, drifts,
                               p0=[A_ll, delta_ll], maxfev=10000)
        A_nl, delta_nl = popt
        perr = np.sqrt(np.diag(pcov))
        residuals = drifts - power_law(products, *popt)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((drifts - np.mean(drifts))**2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    except Exception:
        delta_nl, A_nl = delta_ll, A_ll
        perr = [float("nan"), float("nan")]
        r2 = float("nan")

    return {
        "n_points": len(products),
        "products": products.tolist(),
        "drifts": drifts.tolist(),
        "loglog_fit": {"delta": round(float(delta_ll), 6), "A": round(float(A_ll), 8)},
        "nonlinear_fit": {
            "delta": round(float(delta_nl), 6),
            "delta_stderr": round(float(perr[1]) if len(perr) > 1 else float("nan"), 6),
            "A": round(float(A_nl), 8),
            "A_stderr": round(float(perr[0]) if len(perr) > 0 else float("nan"), 8),
            "R_squared": round(float(r2), 6),
        },
    }


def main():
    t0 = time.time()
    forms = load_forms()

    labels_all = [f[0] for f in forms]
    levels_all = [f[1] for f in forms]
    traces_all = [f[2] for f in forms]
    n_forms = len(forms)

    # Precompute bad-prime sets
    bad_sets = [prime_factors(lv) for lv in levels_all]

    # -- Unconditional ST moments --
    print("\n[unconditional] Computing global Sato-Tate moments...")
    M2_g, M4_g, n_g = compute_st_moments(traces_all, levels_all)
    print(f"  M2 = {M2_g:.6f}  (SU(2) theory: 0.25)")
    print(f"  M4 = {M4_g:.6f}  (SU(2) theory: 0.125)")
    print(f"  Data points: {n_g:,}")
    unconditional = np.array([M2_g, M4_g])

    results = {
        "metadata": {
            "n_forms": n_forms,
            "ells": ELLS,
            "fingerprint_primes": PRIMES_25,
            "st_primes_count": len(ST_PRIMES),
            "st_primes_max": max(ST_PRIMES),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        "unconditional": {
            "M2": round(M2_g, 8),
            "M4": round(M4_g, 8),
            "n_data_points": n_g,
            "SU2_theory": {"M2": 0.25, "M4": 0.125},
        },
    }

    # ================================================================
    # PART A: Single-residue conditioning (high statistics)
    # Partition by a_{ell1} mod ell1, sub-partition by a_{ell2} mod ell2
    # ================================================================
    print("\n" + "=" * 60)
    print("PART A: Single-residue conditioning")
    print("=" * 60)

    drift_rows_A = []

    for ell1 in ELLS:
        # Partition by a_{ell1} mod ell1
        partitions = defaultdict(list)  # residue -> list of indices
        for i in range(n_forms):
            if ell1 in bad_sets[i]:
                continue
            if ell1 - 1 < len(traces_all[i]):
                a_ell1 = int(round(traces_all[i][ell1 - 1]))
                partitions[a_ell1 % ell1].append(i)

        n_forms_partitioned = sum(len(v) for v in partitions.values())
        print(f"\nell1={ell1}: {len(partitions)} residue classes, "
              f"{n_forms_partitioned} forms")
        for res in sorted(partitions.keys()):
            print(f"  a_{ell1} = {res} mod {ell1}: {len(partitions[res])} forms")

        for ell2 in ELLS:
            print(f"\n  --- (ell1={ell1}, ell2={ell2}) ---")
            exclude = {ell1, ell2}

            # For each ell1-class, sub-partition by ell2
            sub_drifts_global = []
            sub_weights = []
            sub_drifts_cluster = []

            for res1 in sorted(partitions.keys()):
                idxs1 = partitions[res1]

                # Compute ell1-class moment
                cl_traces = [traces_all[i] for i in idxs1]
                cl_levels = [levels_all[i] for i in idxs1]
                M2_cl, M4_cl, n_cl = compute_st_moments(cl_traces, cl_levels, exclude)
                if M2_cl is None:
                    continue
                vec_cl = np.array([M2_cl, M4_cl])

                # Sub-partition by a_{ell2} mod ell2
                sub = defaultdict(list)
                for i in idxs1:
                    if ell2 in bad_sets[i]:
                        continue
                    if ell2 - 1 < len(traces_all[i]):
                        a_ell2 = int(round(traces_all[i][ell2 - 1]))
                        sub[a_ell2 % ell2].append(i)

                for res2 in sorted(sub.keys()):
                    sub_idxs = sub[res2]
                    if len(sub_idxs) < 3:
                        continue
                    s_traces = [traces_all[j] for j in sub_idxs]
                    s_levels = [levels_all[j] for j in sub_idxs]
                    M2_s, M4_s, n_s = compute_st_moments(s_traces, s_levels, exclude)
                    if M2_s is None:
                        continue
                    vec_s = np.array([M2_s, M4_s])
                    d_global = float(np.linalg.norm(vec_s - unconditional))
                    d_cluster = float(np.linalg.norm(vec_s - vec_cl))
                    sub_drifts_global.append(d_global)
                    sub_drifts_cluster.append(d_cluster)
                    sub_weights.append(len(sub_idxs))

            if sub_drifts_global:
                w = np.array(sub_weights, dtype=float)
                dg = np.array(sub_drifts_global)
                dc = np.array(sub_drifts_cluster)
                mean_dg = float(np.average(dg, weights=w))
                mean_dc = float(np.average(dc, weights=w))
                median_dg = float(np.median(dg))
                median_dc = float(np.median(dc))
            else:
                mean_dg = mean_dc = median_dg = median_dc = 0.0

            row = {
                "ell1": ell1, "ell2": ell2, "product": ell1 * ell2,
                "n_sub_cells": len(sub_drifts_global),
                "n_forms_used": sum(sub_weights) if sub_weights else 0,
                "mean_drift_vs_global": round(mean_dg, 8),
                "mean_drift_vs_class": round(mean_dc, 8),
                "median_drift_vs_global": round(median_dg, 8),
                "median_drift_vs_class": round(median_dc, 8),
            }
            drift_rows_A.append(row)
            print(f"    Cells: {row['n_sub_cells']}, forms: {row['n_forms_used']}")
            print(f"    Mean drift (vs global):  {mean_dg:.8f}")
            print(f"    Mean drift (vs class):   {mean_dc:.8f}")

    results["single_residue_drift"] = drift_rows_A

    # ================================================================
    # PART B: Full-fingerprint conditioning (CT1-style)
    # Only ell1=3 has meaningful cluster sizes
    # ================================================================
    print("\n" + "=" * 60)
    print("PART B: Full-fingerprint conditioning (ell1=3)")
    print("=" * 60)

    drift_rows_B = []
    ell1 = 3
    fp_clusters = defaultdict(list)
    for i, (label, level, traces) in enumerate(forms):
        fp = compute_fingerprint(traces, level, ell1)
        fp_clusters[fp].append(i)

    big_clusters = {fp: idxs for fp, idxs in fp_clusters.items() if len(idxs) >= 3}
    n_big = len(big_clusters)
    n_forms_big = sum(len(v) for v in big_clusters.values())
    print(f"  ell1={ell1}: {n_big} clusters with >= 3 forms ({n_forms_big} forms)")

    for ell2 in ELLS:
        print(f"\n  --- fingerprint(ell1={ell1}), ell2={ell2} ---")
        exclude = {ell1, ell2}
        sub_dg = []
        sub_dc = []
        sub_w = []

        for fp, idxs in big_clusters.items():
            cl_traces = [traces_all[i] for i in idxs]
            cl_levels = [levels_all[i] for i in idxs]
            M2_cl, M4_cl, _ = compute_st_moments(cl_traces, cl_levels, exclude)
            if M2_cl is None:
                continue
            vec_cl = np.array([M2_cl, M4_cl])

            sub = defaultdict(list)
            for i in idxs:
                if ell2 in bad_sets[i]:
                    continue
                if ell2 - 1 < len(traces_all[i]):
                    a = int(round(traces_all[i][ell2 - 1]))
                    sub[a % ell2].append(i)

            for res2, sub_idxs in sub.items():
                if len(sub_idxs) < 2:
                    continue
                s_tr = [traces_all[j] for j in sub_idxs]
                s_lv = [levels_all[j] for j in sub_idxs]
                M2_s, M4_s, _ = compute_st_moments(s_tr, s_lv, exclude)
                if M2_s is None:
                    continue
                vec_s = np.array([M2_s, M4_s])
                sub_dg.append(float(np.linalg.norm(vec_s - unconditional)))
                sub_dc.append(float(np.linalg.norm(vec_s - vec_cl)))
                sub_w.append(len(sub_idxs))

        if sub_dg:
            w = np.array(sub_w, dtype=float)
            mean_dg = float(np.average(np.array(sub_dg), weights=w))
            mean_dc = float(np.average(np.array(sub_dc), weights=w))
        else:
            mean_dg = mean_dc = 0.0

        row_b = {
            "ell1": ell1, "ell2": ell2, "product": ell1 * ell2,
            "n_sub_cells": len(sub_dg),
            "n_forms_used": sum(sub_w) if sub_w else 0,
            "mean_drift_vs_global": round(mean_dg, 8),
            "mean_drift_vs_cluster": round(mean_dc, 8),
        }
        drift_rows_B.append(row_b)
        print(f"    Cells: {row_b['n_sub_cells']}, forms: {row_b['n_forms_used']}")
        print(f"    Mean drift (vs global):  {mean_dg:.8f}")
        print(f"    Mean drift (vs cluster): {mean_dc:.8f}")

    results["fingerprint_drift"] = drift_rows_B

    # ================================================================
    # FIT: drift ~ (ell1 * ell2)^(-delta)
    # ================================================================
    print("\n" + "=" * 60)
    print("POWER-LAW FITS")
    print("=" * 60)

    fits = {}

    # Fit A: single-residue, all 9 pairs
    prods_A = [r["product"] for r in drift_rows_A if r["mean_drift_vs_global"] > 0]
    drifts_A = [r["mean_drift_vs_global"] for r in drift_rows_A if r["mean_drift_vs_global"] > 0]
    fits["single_residue_all"] = fit_power_law(prods_A, drifts_A, "single_residue_all")
    if "delta" in fits["single_residue_all"].get("nonlinear_fit", {}):
        d = fits["single_residue_all"]["nonlinear_fit"]["delta"]
        print(f"  [single_residue_all] delta = {d:.4f}")

    # Fit A cross only (ell1 != ell2)
    prods_Ax = [r["product"] for r in drift_rows_A
                if r["mean_drift_vs_global"] > 0 and r["ell1"] != r["ell2"]]
    drifts_Ax = [r["mean_drift_vs_global"] for r in drift_rows_A
                 if r["mean_drift_vs_global"] > 0 and r["ell1"] != r["ell2"]]
    fits["single_residue_cross"] = fit_power_law(prods_Ax, drifts_Ax, "single_residue_cross")
    if "delta" in fits["single_residue_cross"].get("nonlinear_fit", {}):
        d = fits["single_residue_cross"]["nonlinear_fit"]["delta"]
        print(f"  [single_residue_cross] delta = {d:.4f}")

    # Fit A: class-relative drift
    prods_Ac = [r["product"] for r in drift_rows_A if r["mean_drift_vs_class"] > 0]
    drifts_Ac = [r["mean_drift_vs_class"] for r in drift_rows_A if r["mean_drift_vs_class"] > 0]
    fits["single_residue_class_relative"] = fit_power_law(prods_Ac, drifts_Ac, "class_relative")
    if "delta" in fits["single_residue_class_relative"].get("nonlinear_fit", {}):
        d = fits["single_residue_class_relative"]["nonlinear_fit"]["delta"]
        print(f"  [single_residue_class_relative] delta = {d:.4f}")

    # Fit B: fingerprint, ell1=3 only
    prods_B = [r["product"] for r in drift_rows_B if r["mean_drift_vs_global"] > 0]
    drifts_B = [r["mean_drift_vs_global"] for r in drift_rows_B if r["mean_drift_vs_global"] > 0]
    fits["fingerprint_ell1_3"] = fit_power_law(prods_B, drifts_B, "fingerprint_ell1_3")
    if "delta" in fits["fingerprint_ell1_3"].get("nonlinear_fit", {}):
        d = fits["fingerprint_ell1_3"]["nonlinear_fit"]["delta"]
        print(f"  [fingerprint_ell1=3] delta = {d:.4f}")

    results["fits"] = fits

    # -- Summary table --
    print("\n" + "=" * 60)
    print("PART A DRIFT TABLE (single-residue)")
    print("=" * 60)
    print(f"{'ell1':>5} {'ell2':>5} {'prod':>5} {'drift_global':>14} {'drift_class':>14} {'cells':>6} {'forms':>7}")
    for r in drift_rows_A:
        print(f"{r['ell1']:>5} {r['ell2']:>5} {r['product']:>5} "
              f"{r['mean_drift_vs_global']:>14.8f} {r['mean_drift_vs_class']:>14.8f} "
              f"{r['n_sub_cells']:>6} {r['n_forms_used']:>7}")

    print("\nPART B DRIFT TABLE (fingerprint, ell1=3)")
    print(f"{'ell2':>5} {'prod':>5} {'drift_global':>14} {'drift_cluster':>14} {'cells':>6} {'forms':>7}")
    for r in drift_rows_B:
        print(f"{r['ell2']:>5} {r['product']:>5} "
              f"{r['mean_drift_vs_global']:>14.8f} {r['mean_drift_vs_cluster']:>14.8f} "
              f"{r['n_sub_cells']:>6} {r['n_forms_used']:>7}")

    # Save
    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s. Results saved to {OUT_PATH}")


if __name__ == "__main__":
    main()

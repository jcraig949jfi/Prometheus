"""Audit: F045 — multiple-testing correction + F041a-vs-F045 independence.

Spec source:
  Agora task `audit_F045_multiple_testing_and_independence` (sessionA, 2026-04-18).
  Output: cartography/docs/audit_F045_multiple_testing_and_independence_results.json.

Sub-questions:
  (1) Extract per-prime uncorrected p-values from F045's stored profiles.
  (2) Apply Bonferroni + Benjamini-Hochberg corrections; report survivors.
  (3) Compute correlation / mutual information between isogeny class_size
      (F045 stratifier) and num_bad_primes (F041a stratifier) on a stratified
      LMFDB sample, to test whether F045 collapses into F041a.
  (4) Name the surviving primes; check small-prime clustering.

Method
------
F045's original test (ergon/murmuration_isogeny.py:statistical_tests):
one-way ANOVA on the mean a_p/sqrt(p) across class_size strata, per prime.
Reuses cached profiles.json (per-cell mean/std/n).

For independence (3): pull EC with rank in {0, 1} (the murmuration cohort)
sampled across class_sizes, and compute Spearman correlation +
mutual-information estimate between class_size and num_bad_primes.
"""
import json
import math
import os
import sys
import io
from pathlib import Path

import numpy as np
from scipy import stats as sp_stats
import psycopg2

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


PG = dict(host="192.168.1.176", port=5432, user="lmfdb", password="lmfdb", dbname="lmfdb")
PROFILES_PATH = Path("ergon/results/murmuration_isogeny/profiles.json")
OUT_PATH = Path("cartography/docs/audit_F045_multiple_testing_and_independence_results.json")
ALPHA = 0.05


def per_prime_anova(profiles):
    """For each prime, one-way ANOVA across class_size strata.
    Returns dict: prime -> {F, p_uncorrected, n_total, k_strata, means, ns}."""
    class_sizes = sorted(profiles.keys(), key=int)
    primes = sorted(profiles[class_sizes[0]].keys(), key=int)
    out = {}
    for p in primes:
        means = [profiles[cs][p]["mean"] for cs in class_sizes]
        stds  = [profiles[cs][p]["std"]  for cs in class_sizes]
        ns    = [profiles[cs][p]["n"]    for cs in class_sizes]
        grand = float(np.average(means, weights=ns))
        ss_b = float(sum(n * (m - grand) ** 2 for m, n in zip(means, ns)))
        ss_w = float(sum((n - 1) * s ** 2 for s, n in zip(stds, ns)))
        k = len(class_sizes)
        N = sum(ns)
        if ss_w <= 0 or N <= k:
            out[p] = {"F": None, "p_uncorrected": None, "n_total": N, "k_strata": k}
            continue
        F = (ss_b / (k - 1)) / (ss_w / (N - k))
        pval = 1.0 - sp_stats.f.cdf(F, k - 1, N - k)
        out[p] = {
            "F": F,
            "p_uncorrected": pval,
            "n_total": N,
            "k_strata": k,
            "means": dict(zip(class_sizes, means)),
            "ns": dict(zip(class_sizes, ns)),
            "spread": float(max(means) - min(means)),
        }
    return out


def apply_bonferroni(per_prime, alpha=ALPHA):
    primes = list(per_prime.keys())
    pvals = [per_prime[p]["p_uncorrected"] for p in primes]
    valid = [(p, q) for p, q in zip(primes, pvals) if q is not None]
    n_tests = len(valid)
    threshold = alpha / n_tests
    survivors = [p for p, q in valid if q <= threshold]
    return {
        "method": "Bonferroni",
        "alpha": alpha,
        "n_tests": n_tests,
        "threshold": threshold,
        "n_survivors": len(survivors),
        "surviving_primes": survivors,
    }


def apply_bh(per_prime, alpha=ALPHA):
    """Benjamini-Hochberg FDR control at level alpha."""
    primes = list(per_prime.keys())
    pairs = [(p, per_prime[p]["p_uncorrected"]) for p in primes if per_prime[p]["p_uncorrected"] is not None]
    pairs.sort(key=lambda x: x[1])
    n = len(pairs)
    survivors = []
    last_passing_rank = 0
    for i, (p, q) in enumerate(pairs, 1):
        if q <= (i / n) * alpha:
            last_passing_rank = i
    if last_passing_rank > 0:
        survivors = [pairs[i][0] for i in range(last_passing_rank)]
    return {
        "method": "Benjamini-Hochberg (FDR)",
        "alpha": alpha,
        "n_tests": n,
        "n_survivors": len(survivors),
        "surviving_primes": survivors,
        "rejection_rank": last_passing_rank,
    }


def fetch_class_size_nbp_sample(per_class_cap=10000):
    """Stratified sample across class_size of (class_size, num_bad_primes) pairs."""
    conn = psycopg2.connect(**PG)
    cur = conn.cursor()
    sql = """
        SELECT class_size, num_bad_primes, count(*)
          FROM ec_curvedata
         WHERE rank IN ('0', '1')
           AND class_size IS NOT NULL
           AND num_bad_primes IS NOT NULL
         GROUP BY class_size, num_bad_primes
         ORDER BY class_size::int, num_bad_primes::int
    """
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def compute_independence(rows):
    """Build (class_size, nbp) joint distribution from cell counts; compute Spearman + MI."""
    cs_vals = []
    nbp_vals = []
    weights = []
    cells = []
    for cs, nbp, n in rows:
        try:
            cs_i = int(cs)
            nbp_i = int(nbp)
            n_i = int(n)
        except Exception:
            continue
        cells.append((cs_i, nbp_i, n_i))
    # Spearman correlation on weighted cell-pair list (expand into the full distribution)
    # Avoid materialising millions of rows: compute moments directly.
    total_n = sum(n for _, _, n in cells)
    if total_n == 0:
        return {"error": "no usable cells"}

    cs_arr = np.array([cs for cs, _, _ in cells])
    nbp_arr = np.array([nbp for _, nbp, _ in cells])
    n_arr = np.array([n for _, _, n in cells], dtype=np.float64)

    # Marginals
    cs_marg = {}
    nbp_marg = {}
    for cs, nbp, n in cells:
        cs_marg[cs] = cs_marg.get(cs, 0) + n
        nbp_marg[nbp] = nbp_marg.get(nbp, 0) + n
    cs_keys = sorted(cs_marg)
    nbp_keys = sorted(nbp_marg)
    p_cs = np.array([cs_marg[k] / total_n for k in cs_keys])
    p_nbp = np.array([nbp_marg[k] / total_n for k in nbp_keys])

    # Joint
    joint = np.zeros((len(cs_keys), len(nbp_keys)))
    cs_idx = {k: i for i, k in enumerate(cs_keys)}
    nbp_idx = {k: i for i, k in enumerate(nbp_keys)}
    for cs, nbp, n in cells:
        joint[cs_idx[cs], nbp_idx[nbp]] += n
    joint /= total_n

    # MI: sum p(x,y) log( p(x,y) / (p(x)p(y)) )
    eps = 1e-15
    mi = 0.0
    for i, p_x in enumerate(p_cs):
        for j, p_y in enumerate(p_nbp):
            p_xy = joint[i, j]
            if p_xy > 0:
                mi += p_xy * math.log(p_xy / (p_x * p_y + eps) + eps)
    mi /= math.log(2)  # bits
    # Normalize to [0,1] by dividing by min(H(X), H(Y))
    h_cs = -sum(p * math.log(p, 2) for p in p_cs if p > 0)
    h_nbp = -sum(p * math.log(p, 2) for p in p_nbp if p > 0)
    mi_norm = mi / min(h_cs, h_nbp) if min(h_cs, h_nbp) > 0 else None

    # Weighted Spearman (rank-based) on the implicit population
    # Approximate via converting cell counts to rank-bin samples
    # For simplicity, expand each (cs, nbp) cell into n samples (using midrank approximation)
    # Cap total expansion at 5e6 to keep tractable
    cap = 5_000_000
    if total_n > cap:
        scale = cap / total_n
    else:
        scale = 1.0
    cs_sample = []
    nbp_sample = []
    for cs, nbp, n in cells:
        m = max(1, int(round(n * scale)))
        cs_sample.extend([cs] * m)
        nbp_sample.extend([nbp] * m)
    cs_sample = np.array(cs_sample)
    nbp_sample = np.array(nbp_sample)
    spearman = sp_stats.spearmanr(cs_sample, nbp_sample)

    return {
        "n_cells": len(cells),
        "total_n": total_n,
        "class_sizes": cs_keys,
        "nbp_values": nbp_keys,
        "p_class_size": dict(zip(cs_keys, p_cs.tolist())),
        "p_num_bad_primes": dict(zip(nbp_keys, p_nbp.tolist())),
        "mutual_information_bits": mi,
        "normalized_mi": mi_norm,
        "H_class_size_bits": h_cs,
        "H_nbp_bits": h_nbp,
        "spearman_corr": float(spearman.statistic),
        "spearman_p": float(spearman.pvalue),
        "joint_distribution": joint.tolist(),
        "interpretation": (
            "normalized_mi near 0 -> class_size and nbp are nearly independent (F045 NOT a proxy for F041a). "
            "normalized_mi >= 0.1 -> some dependence; consider whether F045's 5/21 signal could be confounded "
            "by nbp. spearman_corr |.| >= 0.3 -> ordered dependence; F045 effect direction may align/anti-align "
            "with F041a's nbp ladder."
        ),
    }


def small_prime_cluster_check(per_prime, surviving):
    """Are surviving primes clustered at small primes vs spread across the range?"""
    primes_int = sorted(int(p) for p in per_prime if per_prime[p]["p_uncorrected"] is not None)
    surv_int = sorted(int(p) for p in surviving)
    if not surv_int:
        return {"clustering": "n/a", "surviving_int": []}
    # Compute the median rank position (1 = smallest prime tested) of survivors
    n_total = len(primes_int)
    rank_positions = [primes_int.index(p) + 1 for p in surv_int]
    median_rank = float(np.median(rank_positions))
    # If median_rank <= n_total/3: small-prime clustering
    if median_rank <= n_total / 3:
        cluster = "small-prime-clustered"
    elif median_rank >= 2 * n_total / 3:
        cluster = "large-prime-clustered"
    else:
        cluster = "spread"
    return {
        "surviving_primes_int": surv_int,
        "rank_positions_in_test_set": rank_positions,
        "median_rank": median_rank,
        "n_total_primes_tested": n_total,
        "clustering": cluster,
    }


def main():
    print("Loading profiles.json...")
    with open(PROFILES_PATH) as fh:
        profiles = json.load(fh)
    print(f"  class_sizes: {sorted(profiles.keys(), key=int)}")
    print(f"  primes per stratum: {len(profiles[next(iter(profiles))])}")

    print("\nRunning per-prime ANOVA...")
    per_prime = per_prime_anova(profiles)
    n_primes = len(per_prime)
    n_uncorrected_sig = sum(1 for v in per_prime.values()
                             if v["p_uncorrected"] is not None and v["p_uncorrected"] < ALPHA)
    print(f"  n_primes={n_primes}; uncorrected at alpha={ALPHA}: {n_uncorrected_sig}/{n_primes}")

    print("\nApplying corrections...")
    bonf = apply_bonferroni(per_prime)
    bh = apply_bh(per_prime)
    print(f"  Bonferroni: {bonf['n_survivors']}/{bonf['n_tests']} survive (alpha/{bonf['n_tests']} = {bonf['threshold']:.2e})")
    print(f"  Benjamini-Hochberg: {bh['n_survivors']}/{bh['n_tests']} survive at FDR={ALPHA}")

    print("\nSmall-prime clustering check...")
    bonf_cluster = small_prime_cluster_check(per_prime, bonf["surviving_primes"])
    bh_cluster = small_prime_cluster_check(per_prime, bh["surviving_primes"])
    print(f"  Bonferroni survivors: {bonf_cluster}")
    print(f"  BH survivors: {bh_cluster}")

    print("\nFetching class_size x nbp distribution from LMFDB (rank in {0,1})...")
    rows = fetch_class_size_nbp_sample()
    print(f"  fetched {len(rows)} (class_size, nbp) cells")
    indep = compute_independence(rows)
    print(f"  total_n={indep['total_n']}; MI={indep['mutual_information_bits']:.4f} bits; "
          f"normalized_mi={indep['normalized_mi']:.4f}; spearman={indep['spearman_corr']:.4f}")

    # Verdict logic
    f045_sig_surviving = bh["n_survivors"] >= 1 or bonf["n_survivors"] >= 1
    if f045_sig_surviving:
        if indep["normalized_mi"] is not None and indep["normalized_mi"] >= 0.1:
            verdict = "F045 SURVIVES multiple-testing BUT collapses-into-F041a-suspect (class_size and nbp share structure)"
        elif abs(indep["spearman_corr"]) >= 0.3:
            verdict = "F045 SURVIVES multiple-testing BUT Spearman-correlated with nbp -- partial F041a-collapse risk"
        else:
            verdict = "F045 SURVIVES multiple-testing AND independent of nbp -- isogeny axis is independent of F041a"
    else:
        verdict = "F045 DOES NOT SURVIVE multiple-testing correction -- the 5/21 raw count was multiple-testing artifact"

    out = {
        "task_id": "audit_F045_multiple_testing_and_independence",
        "instance": "Harmonia_M2_auditor",
        "run_at": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime()),
        "spec_source": "Agora task posted by Harmonia_M2_sessionA 2026-04-18; ergon/murmuration_isogeny.py original test",
        "data_source": str(PROFILES_PATH),
        "method": (
            "1-way ANOVA on a_p/sqrt(p) means stratified by isogeny class_size, per prime "
            "(reproduces ergon/murmuration_isogeny.py:statistical_tests); apply Bonferroni "
            "and BH FDR corrections; pull LMFDB ec_curvedata WHERE rank IN ('0','1') for "
            "class_size x nbp joint distribution and compute MI + Spearman."
        ),
        "n_primes_tested": n_primes,
        "n_uncorrected_significant": n_uncorrected_sig,
        "uncorrected_significant_primes": [
            int(p) for p, v in per_prime.items()
            if v["p_uncorrected"] is not None and v["p_uncorrected"] < ALPHA
        ],
        "per_prime_results": per_prime,
        "bonferroni": bonf,
        "bonferroni_clustering": bonf_cluster,
        "benjamini_hochberg": bh,
        "benjamini_hochberg_clustering": bh_cluster,
        "f041a_independence": indep,
        "verdict": verdict,
        "tensor_mutation_recommended": False,
        "next_step": (
            "If verdict involves F041a-collapse-suspect: re-run F045 stratified-WITHIN-nbp "
            "to isolate the isogeny axis from the bad-prime axis. If verdict says F045 "
            "doesn't survive correction: F045 description should be updated to note the "
            "multiple-testing penalty applied and the resulting weaker claim."
        ),
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"\nWrote {OUT_PATH}")
    print(f"VERDICT: {verdict}")


if __name__ == "__main__":
    main()

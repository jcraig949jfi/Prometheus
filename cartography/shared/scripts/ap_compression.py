#!/usr/bin/env python3
"""
ap_compression.py -- Test whether a_p sequence compressibility predicts EC rank.

Hypothesis: high-rank EC have constrained a_p (divisibility patterns from BSD),
which may make their sequences more or less compressible. Treats a_p as a string,
not as statistics.

Kill prediction: conductor explains all compressibility variation; rank adds nothing.
"""

import json
import gzip
import zlib
import math
import struct
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from scipy import stats

# ---------------------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------------------

def load_data():
    import duckdb
    db_path = Path(__file__).resolve().parents[3] / "charon" / "data" / "charon.duckdb"
    con = duckdb.connect(str(db_path), read_only=True)
    rows = con.execute("""
        SELECT lmfdb_label, conductor, rank, analytic_rank, torsion, aplist
        FROM elliptic_curves
        WHERE rank IS NOT NULL AND aplist IS NOT NULL
    """).fetchall()
    con.close()

    data = []
    for label, cond, rank, arank, tors, aplist in rows:
        if aplist and len(aplist) >= 20:
            data.append({
                "label": label,
                "conductor": int(cond),
                "rank": int(rank),
                "analytic_rank": int(arank) if arank is not None else None,
                "torsion": int(tors) if tors is not None else None,
                "aplist": [int(x) for x in aplist],
            })
    return data


# ---------------------------------------------------------------------------
# 2. Compressibility metrics
# ---------------------------------------------------------------------------

def gzip_ratio(ap):
    """Compress a_p as packed int16 bytes, return compressed/uncompressed ratio."""
    raw = struct.pack(f">{len(ap)}h", *ap)
    compressed = gzip.compress(raw, compresslevel=9)
    return len(compressed) / len(raw)


def shannon_entropy(ap):
    """Treat a_p values as symbols, compute Shannon entropy in bits."""
    counts = Counter(ap)
    n = len(ap)
    h = 0.0
    for c in counts.values():
        p = c / n
        if p > 0:
            h -= p * math.log2(p)
    return h


def kolmogorov_proxy(ap):
    """zlib compression ratio on fixed-width binary encoding -- proxy for K complexity.

    NOTE: Using int16 binary encoding, NOT string representation.
    String repr has variable width per value (digit count correlates with rank
    at rho=0.57 -- a confound that inflates apparent compressibility signal).
    """
    raw = struct.pack(f">{len(ap)}h", *ap)
    compressed = zlib.compress(raw, level=9)
    return len(compressed) / len(raw)


def lempel_ziv_complexity(ap):
    """LZ complexity on binarized sequence (a_p > 0 -> 1, else 0)."""
    binary = "".join("1" if x > 0 else "0" for x in ap)
    n = len(binary)
    if n == 0:
        return 0
    # Lempel-Ziv 76 complexity
    i, c = 0, 1
    l = 1
    while i + l <= n:
        substr = binary[i + 1 : i + l + 1] if i + l + 1 <= n else binary[i + 1:]
        # Check if binary[i+1:i+l+1] is a substring of binary[0:i+l]
        if binary[i + l : i + l + 1] and binary[i + l] in _substrings_at(binary, i + l):
            l += 1
        else:
            c += 1
            i += l
            l = 1
    # Normalize by n/log2(n)
    return c / (n / math.log2(n)) if n > 1 else c


def _substrings_at(s, pos):
    """Helper: set of characters that appear in s[0:pos]."""
    return set(s[:pos])


def lempel_ziv_complexity_v2(ap):
    """LZ76 complexity, properly implemented."""
    binary = "".join("1" if x > 0 else "0" for x in ap)
    n = len(binary)
    if n <= 1:
        return 1.0
    c = 1
    i = 0
    while i < n:
        l = 1
        found = True
        while found and i + l <= n:
            # Is binary[i:i+l] a substring of binary[0:i+l-1]?
            sub = binary[i:i + l]
            if sub in binary[0:i + l - 1]:
                l += 1
            else:
                found = False
        c += 1
        i += l - 1 if l > 1 else 1
    norm = n / math.log2(n) if n > 1 else 1
    return c / norm


def recurrence_residual(ap):
    """Fit linear recurrence of orders 1-5, return best normalized residual."""
    ap_arr = np.array(ap, dtype=np.float64)
    n = len(ap_arr)
    best_resid = float("inf")
    for order in range(1, min(6, n // 2)):
        # Build Toeplitz-style matrix: X[i] = [ap[i-1], ap[i-2], ..., ap[i-order]]
        X = np.column_stack([ap_arr[order - j - 1 : n - j - 1] for j in range(order)])
        y = ap_arr[order:]
        try:
            coeffs, resid, _, _ = np.linalg.lstsq(X, y, rcond=None)
            pred = X @ coeffs
            rmse = np.sqrt(np.mean((y - pred) ** 2))
            # Normalize by std of target
            std_y = np.std(y)
            nrmse = rmse / std_y if std_y > 1e-12 else rmse
            if nrmse < best_resid:
                best_resid = nrmse
        except Exception:
            continue
    return best_resid if best_resid < float("inf") else 1.0


def compute_all_metrics(ap):
    return {
        "gzip_ratio": gzip_ratio(ap),
        "shannon_entropy": shannon_entropy(ap),
        "kolmogorov_proxy": kolmogorov_proxy(ap),
        "lz_complexity": lempel_ziv_complexity_v2(ap),
        "recurrence_residual": recurrence_residual(ap),
    }


# ---------------------------------------------------------------------------
# 3. Statistical tests
# ---------------------------------------------------------------------------

def eta_squared(groups, values):
    """One-way eta^2: how much variance in values is explained by group membership."""
    grand_mean = np.mean(values)
    ss_total = np.sum((values - grand_mean) ** 2)
    if ss_total < 1e-15:
        return 0.0
    ss_between = 0.0
    unique_groups = np.unique(groups)
    for g in unique_groups:
        mask = groups == g
        g_mean = np.mean(values[mask])
        ss_between += np.sum(mask) * (g_mean - grand_mean) ** 2
    return ss_between / ss_total


def cohens_d(a, b):
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return 0.0
    pooled_std = math.sqrt(((na - 1) * np.var(a, ddof=1) + (nb - 1) * np.var(b, ddof=1)) / (na + nb - 2))
    if pooled_std < 1e-15:
        return 0.0
    return (np.mean(a) - np.mean(b)) / pooled_std


def within_conductor_correlation(log_cond_bins, metric_vals, ranks):
    """Compute Spearman rho within conductor bins, return median and per-bin results."""
    unique_bins = np.unique(log_cond_bins)
    rhos = []
    for b in unique_bins:
        mask = log_cond_bins == b
        if np.sum(mask) < 20:
            continue
        r_sub = ranks[mask]
        m_sub = metric_vals[mask]
        if len(np.unique(r_sub)) < 2:
            continue
        rho, _ = stats.spearmanr(m_sub, r_sub)
        if not np.isnan(rho):
            rhos.append(rho)
    return {"median_rho": float(np.median(rhos)) if rhos else None,
            "n_bins": len(rhos),
            "rhos": [round(r, 4) for r in rhos]}


def f33_ordinal_check(metric_vals, ranks):
    """F33: sort metric and rank independently, compute rho. If ~ real rho, it's ordinal artifact."""
    real_rho, _ = stats.spearmanr(metric_vals, ranks)
    sorted_metric = np.sort(metric_vals)
    sorted_ranks = np.sort(ranks)
    ordinal_rho, _ = stats.spearmanr(sorted_metric, sorted_ranks)
    return {"real_rho": float(real_rho),
            "sorted_rho": float(ordinal_rho),
            "ordinal_artifact": bool(abs(ordinal_rho - real_rho) < 0.05)}


def permutation_test(metric_vals, ranks, n_perm=1000):
    """Shuffle rank labels, recompute Spearman rho. Return p-value."""
    real_rho, _ = stats.spearmanr(metric_vals, ranks)
    rng = np.random.default_rng(42)
    count = 0
    for _ in range(n_perm):
        shuffled = rng.permutation(ranks)
        perm_rho, _ = stats.spearmanr(metric_vals, shuffled)
        if abs(perm_rho) >= abs(real_rho):
            count += 1
    return {"real_rho": float(real_rho),
            "p_value": count / n_perm,
            "n_permutations": n_perm}


# ---------------------------------------------------------------------------
# 4. Main analysis
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("a_p COMPRESSION -> RANK PREDICTION TEST")
    print("=" * 70)

    # Load
    print("\n[1] Loading EC data from charon.duckdb...")
    data = load_data()
    print(f"    Loaded {len(data)} curves with >= 20 a_p values")
    rank_counts = Counter(d["rank"] for d in data)
    for r in sorted(rank_counts):
        print(f"    rank {r}: {rank_counts[r]}")

    # Compute metrics
    print("\n[2] Computing compressibility metrics...")
    metric_names = ["gzip_ratio", "shannon_entropy", "kolmogorov_proxy",
                    "lz_complexity", "recurrence_residual"]
    for d in data:
        d["metrics"] = compute_all_metrics(d["aplist"])
    print("    Done.")

    # Build arrays
    ranks = np.array([d["rank"] for d in data])
    conductors = np.array([d["conductor"] for d in data])
    log_conductors = np.log10(conductors.astype(float) + 1)
    # Bin conductors for within-bin analysis (10 equal-frequency bins)
    cond_bins = np.digitize(log_conductors, np.percentile(log_conductors, np.arange(0, 101, 10)))

    # CRITICAL CONTROL: a_p sign bias
    # The sign of a_p relates to root number / functional equation.
    # Rank parity determines sign bias: rank-0 ~ 50% positive, rank-1 ~ 36%.
    # Any binarized metric (LZ complexity) will see this as a compression signal.
    frac_positive = np.array([sum(1 for x in d["aplist"] if x > 0) / len(d["aplist"])
                              for d in data])
    rho_sign, p_sign = stats.spearmanr(frac_positive, ranks)
    print(f"\n[!] SIGN BIAS CONTROL:")
    print(f"    frac(a_p > 0) vs rank: rho = {rho_sign:.4f}  p = {p_sign:.2e}")
    for r in sorted(np.unique(ranks)):
        mask = ranks == r
        print(f"    rank {r}: mean frac_positive = {np.mean(frac_positive[mask]):.4f}")
    print(f"    This is a known number-theory effect (root number / functional equation).")
    print(f"    Any binarized metric will inherit this confound.")

    results = {}

    for mname in metric_names:
        print(f"\n{'='*70}")
        print(f"METRIC: {mname}")
        print(f"{'='*70}")

        mvals = np.array([d["metrics"][mname] for d in data])

        # Basic stats by rank
        print(f"\n  Mean by rank:")
        for r in sorted(np.unique(ranks)):
            mask = ranks == r
            print(f"    rank {r}: mean={np.mean(mvals[mask]):.6f}  "
                  f"std={np.std(mvals[mask]):.6f}  n={np.sum(mask)}")

        # Spearman rho with rank
        rho_rank, p_rank = stats.spearmanr(mvals, ranks)
        print(f"\n  Spearman rho(metric, rank) = {rho_rank:.6f}  p = {p_rank:.2e}")

        # eta^2 for rank
        eta2_rank = eta_squared(ranks, mvals)
        print(f"  eta^2(rank -> metric)        = {eta2_rank:.6f}")

        # Spearman rho with conductor (F35 control)
        rho_cond, p_cond = stats.spearmanr(mvals, log_conductors)
        print(f"\n  F35 CONTROL -- conductor:")
        print(f"  Spearman rho(metric, log_cond) = {rho_cond:.6f}  p = {p_cond:.2e}")
        eta2_cond = eta_squared(cond_bins, mvals)
        print(f"  eta^2(cond_bin -> metric)       = {eta2_cond:.6f}")

        # Does conductor dominate?
        cond_dominates = eta2_cond > eta2_rank * 2
        print(f"  Conductor dominates (eta2_cond > 2*eta2_rank)? {cond_dominates}")

        # Sign-bias control: partial correlation removing frac_positive
        mvals_resid = mvals - np.polyval(np.polyfit(frac_positive, mvals, 2), frac_positive)
        ranks_f = ranks.astype(float)
        ranks_resid = ranks_f - np.polyval(np.polyfit(frac_positive, ranks_f, 2), frac_positive)
        rho_after_sign, p_after_sign = stats.spearmanr(mvals_resid, ranks_resid)
        print(f"\n  SIGN-BIAS CONTROL (residualize out frac_positive):")
        print(f"  rho(metric|sign, rank|sign) = {rho_after_sign:.6f}  p = {p_after_sign:.2e}")
        sign_explains = abs(rho_after_sign) < abs(rho_rank) * 0.3  # sign explains >70%
        if sign_explains:
            print(f"  ** Sign bias explains >70% of the signal **")

        # Within-conductor-bin correlation
        wcb = within_conductor_correlation(cond_bins, mvals, ranks)
        print(f"\n  Within-conductor-bin rho:")
        print(f"    median rho = {wcb['median_rho']}")
        print(f"    n_bins with enough data = {wcb['n_bins']}")

        # Rank-0 vs rank-1 comparison
        r0 = mvals[ranks == 0]
        r1 = mvals[ranks == 1]
        ks_stat, ks_p = stats.ks_2samp(r0, r1)
        d_effect = cohens_d(r0, r1)
        print(f"\n  Rank-0 vs Rank-1:")
        print(f"    KS stat = {ks_stat:.6f}  p = {ks_p:.2e}")
        print(f"    Mean diff = {np.mean(r0) - np.mean(r1):.6f}")
        print(f"    Cohen's d = {d_effect:.6f}")

        # Permutation null
        perm = permutation_test(mvals, ranks, n_perm=1000)
        print(f"\n  Permutation null (1000 shuffles):")
        print(f"    real rho = {perm['real_rho']:.6f}")
        print(f"    p-value  = {perm['p_value']:.4f}")

        # F33 ordinal check
        f33 = f33_ordinal_check(mvals, ranks)
        print(f"\n  F33 ordinal check:")
        print(f"    real rho   = {f33['real_rho']:.6f}")
        print(f"    sorted rho = {f33['sorted_rho']:.6f}")
        print(f"    ordinal artifact? {f33['ordinal_artifact']}")

        # Verdict -- require surviving ALL controls
        survived = (
            perm["p_value"] < 0.05
            and not f33["ordinal_artifact"]
            and not cond_dominates
            and not sign_explains
            and wcb["median_rho"] is not None
            and abs(wcb["median_rho"]) > 0.02
        )
        kill_reason = []
        if perm["p_value"] >= 0.05:
            kill_reason.append("permutation null")
        if f33["ordinal_artifact"]:
            kill_reason.append("F33 ordinal")
        if cond_dominates:
            kill_reason.append("conductor dominates")
        if sign_explains:
            kill_reason.append("sign bias explains >70%")
        if wcb["median_rho"] is None or abs(wcb["median_rho"]) <= 0.02:
            kill_reason.append("no within-conductor signal")

        verdict = "SURVIVES" if survived else "KILLED"
        print(f"\n  >>> VERDICT: {verdict}")
        if kill_reason:
            print(f"      Kill reasons: {', '.join(kill_reason)}")

        results[mname] = {
            "spearman_rho_rank": float(rho_rank),
            "spearman_p_rank": float(p_rank),
            "eta2_rank": float(eta2_rank),
            "spearman_rho_conductor": float(rho_cond),
            "spearman_p_conductor": float(p_cond),
            "eta2_conductor": float(eta2_cond),
            "conductor_dominates": bool(cond_dominates),
            "rho_after_sign_control": float(rho_after_sign),
            "sign_bias_explains_70pct": bool(sign_explains),
            "within_conductor_median_rho": wcb["median_rho"],
            "within_conductor_n_bins": wcb["n_bins"],
            "ks_r0_vs_r1": float(ks_stat),
            "ks_p": float(ks_p),
            "cohens_d_r0_vs_r1": float(d_effect),
            "mean_r0": float(np.mean(r0)),
            "mean_r1": float(np.mean(r1)),
            "permutation_p": perm["p_value"],
            "f33_ordinal_artifact": f33["ordinal_artifact"],
            "verdict": verdict,
            "kill_reasons": kill_reason,
        }

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    n_survived = sum(1 for v in results.values() if v["verdict"] == "SURVIVES")
    n_killed = sum(1 for v in results.values() if v["verdict"] == "KILLED")
    print(f"  {n_survived} metrics survived, {n_killed} killed")
    for mname, r in results.items():
        print(f"  {mname:25s} -> {r['verdict']:8s}  "
              f"rho={r['spearman_rho_rank']:+.4f}  "
              f"eta2_rank={r['eta2_rank']:.4f}  "
              f"eta2_cond={r['eta2_conductor']:.4f}  "
              f"perm_p={r['permutation_p']:.3f}")

    # Kill prediction evaluation
    print(f"\n  Kill prediction (conductor explains all):")
    all_cond_dominates = all(r["conductor_dominates"] for r in results.values())
    print(f"    Conductor dominates ALL metrics? {all_cond_dominates}")
    if all_cond_dominates and n_survived == 0:
        print(f"    CONFIRMED: conductor explains compressibility, rank adds nothing.")
    elif n_survived > 0:
        print(f"    REFUTED: {n_survived} metric(s) show rank signal after conductor control.")
    else:
        print(f"    PARTIAL: killed for other reasons (ordinal, permutation), not just conductor.")

    # Save results
    out_path = Path(__file__).resolve().parents[2] / "convergence" / "data" / "ap_compression_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump({
            "n_curves": len(data),
            "rank_distribution": {str(k): v for k, v in rank_counts.items()},
            "metrics": results,
            "kill_prediction_confirmed": all_cond_dominates and n_survived == 0,
        }, f, indent=2)
    print(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
definitive_rank_test.py — The single most discriminating test for whether
rank is encoded in a_p dynamics.

Combines: conductor-matched pairs + prime-only a_p + shuffled controls.

Three metrics:
  A. ST convergence rate (power-law alpha from KS stat at k=5,10,15,20,25)
  B. ST surprise: -log2(ST_density(a_p / 2sqrt(p))) summed
  C. Shannon entropy of mod-7 fingerprint

Controls:
  - Shuffled (full random permutation)
  - Block-shuffled (blocks of 5)
  - Reversed

Cross-validation: 70/30 train/test split on conductor-matched pairs.
"""

import json
import sys
import warnings
from pathlib import Path
from collections import Counter

import numpy as np
from scipy import stats
from scipy.special import gammaln

warnings.filterwarnings("ignore", category=RuntimeWarning)

# ── Primes list (first 100 primes covers aplist length up to 25+) ──────────
def sieve(n):
    is_p = [True] * (n + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_p[i]:
            for j in range(i*i, n+1, i):
                is_p[j] = False
    return [x for x in range(n+1) if is_p[x]]

PRIMES = sieve(500)  # first 95 primes, more than enough


# ── Sato-Tate helpers ──────────────────────────────────────────────────────
def st_cdf(x):
    """Sato-Tate CDF: integral from -1 to x of (2/pi)*sqrt(1-t^2) dt."""
    x = np.clip(x, -1, 1)
    return (1/np.pi) * (np.arcsin(x) + x * np.sqrt(1 - x**2)) + 0.5


def st_density(x):
    """Sato-Tate density: (2/pi)*sqrt(1-x^2) for x in [-1,1]."""
    x = np.clip(x, -0.9999, 0.9999)
    return (2 / np.pi) * np.sqrt(1 - x**2)


# ── Metric computation ─────────────────────────────────────────────────────
def normalize_ap(aplist):
    """Normalize a_p by 2*sqrt(p) for each prime."""
    n = min(len(aplist), len(PRIMES))
    primes = np.array(PRIMES[:n], dtype=np.float64)
    ap = np.array(aplist[:n], dtype=np.float64)
    normalized = ap / (2.0 * np.sqrt(primes))
    return normalized


def metric_st_convergence(normalized_ap):
    """
    KS statistic vs Sato-Tate CDF at k=5,10,15,20,25 primes.
    Fit power law: KS(k) ~ C * k^alpha.  Return alpha.
    """
    ks_vals = []
    k_vals = [5, 10, 15, 20, 25]
    for k in k_vals:
        if k > len(normalized_ap):
            break
        sample = normalized_ap[:k]
        sorted_sample = np.sort(sample)
        cdf_vals = st_cdf(sorted_sample)
        ecdf = np.arange(1, len(sorted_sample) + 1) / len(sorted_sample)
        ks = np.max(np.abs(ecdf - cdf_vals))
        ks_vals.append(ks)

    if len(ks_vals) < 3:
        return np.nan

    k_arr = np.array(k_vals[:len(ks_vals)], dtype=np.float64)
    ks_arr = np.array(ks_vals, dtype=np.float64)

    # Avoid log(0)
    mask = ks_arr > 0
    if mask.sum() < 3:
        return np.nan

    log_k = np.log(k_arr[mask])
    log_ks = np.log(ks_arr[mask])
    slope, _, _, _, _ = stats.linregress(log_k, log_ks)
    return slope  # alpha: more negative = faster convergence


def metric_st_surprise(normalized_ap):
    """Sum of -log2(ST_density(x)) over normalized a_p values."""
    densities = st_density(normalized_ap)
    # Avoid log(0)
    densities = np.maximum(densities, 1e-10)
    return np.sum(-np.log2(densities))


def metric_mod7_entropy(aplist):
    """Shannon entropy of a_p mod 7 residue distribution."""
    n = min(len(aplist), len(PRIMES))
    residues = [int(aplist[i]) % 7 for i in range(n)]
    counts = Counter(residues)
    total = sum(counts.values())
    if total == 0:
        return np.nan
    probs = np.array([counts.get(r, 0) / total for r in range(7)])
    probs = probs[probs > 0]
    return -np.sum(probs * np.log2(probs))


def compute_metrics(aplist):
    """Compute all three metrics for a given aplist."""
    norm = normalize_ap(aplist)
    return {
        "st_convergence": metric_st_convergence(norm),
        "st_surprise": metric_st_surprise(norm),
        "mod7_entropy": metric_mod7_entropy(aplist),
    }


# ── Shuffle controls ───────────────────────────────────────────────────────
def shuffle_full(aplist, rng):
    """Full random permutation."""
    arr = list(aplist)
    rng.shuffle(arr)
    return arr


def shuffle_block(aplist, rng, block_size=5):
    """Block shuffle: permute blocks of block_size, preserve within-block order."""
    arr = list(aplist)
    n = len(arr)
    blocks = [arr[i:i+block_size] for i in range(0, n, block_size)]
    rng.shuffle(blocks)
    return [x for b in blocks for x in b]


def reverse_ap(aplist):
    """Reverse the sequence."""
    return list(reversed(aplist))


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    import duckdb

    DB_PATH = "F:/Prometheus/charon/data/charon.duckdb"
    print("=" * 72)
    print("DEFINITIVE RANK TEST")
    print("Conductor-matched | Prime-only | Shuffled controls")
    print("=" * 72)

    # ── Load data ──────────────────────────────────────────────────────
    con = duckdb.connect(DB_PATH, read_only=True)
    rows = con.execute("""
        SELECT lmfdb_label, conductor, rank, analytic_rank, aplist
        FROM elliptic_curves
        WHERE aplist IS NOT NULL AND cm = 0 AND rank IN (0, 1, 2)
    """).fetchall()
    con.close()

    print(f"Loaded {len(rows)} curves (rank 0/1/2, cm=0, aplist non-null)")

    # Organize by conductor and rank
    by_cond = {}
    for label, cond, rank, arank, aplist in rows:
        by_cond.setdefault(cond, {}).setdefault(rank, []).append({
            "label": label, "conductor": cond, "rank": rank,
            "analytic_rank": arank, "aplist": aplist
        })

    # ── Conductor-matched pairs (rank 0 vs rank 1) ────────────────────
    pair_conductors = [c for c, d in by_cond.items() if 0 in d and 1 in d]
    pair_conductors.sort()
    print(f"Conductor-matched conductors (rank 0+1): {len(pair_conductors)}")

    # For each conductor, pick one rank-0 and one rank-1 curve (longest aplist)
    pairs = []
    for c in pair_conductors:
        r0 = max(by_cond[c][0], key=lambda x: len(x["aplist"]))
        r1 = max(by_cond[c][1], key=lambda x: len(x["aplist"]))
        pairs.append((r0, r1))

    print(f"Conductor-matched pairs: {len(pairs)}")

    # ── Triplets (rank 0, 1, 2 at same conductor) ─────────────────────
    triplet_conductors = [c for c, d in by_cond.items() if 0 in d and 1 in d and 2 in d]
    triplet_conductors.sort()
    triplets = []
    for c in triplet_conductors:
        r0 = max(by_cond[c][0], key=lambda x: len(x["aplist"]))
        r1 = max(by_cond[c][1], key=lambda x: len(x["aplist"]))
        r2 = max(by_cond[c][2], key=lambda x: len(x["aplist"]))
        triplets.append((r0, r1, r2))

    print(f"Conductor-matched triplets (rank 0+1+2): {len(triplets)}")
    print()

    # ── Compute metrics for all pairs ──────────────────────────────────
    rng = np.random.RandomState(42)
    N_SHUFFLE = 100  # repeated shuffles for stability

    metric_names = ["st_convergence", "st_surprise", "mod7_entropy"]

    # Real differences
    diffs_real = {m: [] for m in metric_names}
    # Shuffled differences (full)
    diffs_shuffled = {m: [] for m in metric_names}
    # Block-shuffled differences
    diffs_block = {m: [] for m in metric_names}
    # Reversed differences
    diffs_reversed = {m: [] for m in metric_names}

    print("Computing metrics for all pairs...")
    for i, (r0, r1) in enumerate(pairs):
        if (i + 1) % 500 == 0:
            print(f"  ... {i+1}/{len(pairs)}")

        m0 = compute_metrics(r0["aplist"])
        m1 = compute_metrics(r1["aplist"])

        for m in metric_names:
            if np.isnan(m0[m]) or np.isnan(m1[m]):
                continue
            diffs_real[m].append(m1[m] - m0[m])  # rank1 - rank0

        # Shuffled control: shuffle rank-1 curve's aplist, recompute
        shuf_diffs = {m: [] for m in metric_names}
        for _ in range(N_SHUFFLE):
            ap1_shuf = shuffle_full(r1["aplist"], rng)
            m1s = compute_metrics(ap1_shuf)
            for m in metric_names:
                if np.isnan(m0[m]) or np.isnan(m1s[m]):
                    continue
                shuf_diffs[m].append(m1s[m] - m0[m])

        for m in metric_names:
            if shuf_diffs[m]:
                diffs_shuffled[m].append(np.mean(shuf_diffs[m]))

        # Block-shuffled control
        block_diffs = {m: [] for m in metric_names}
        for _ in range(N_SHUFFLE):
            ap1_block = shuffle_block(r1["aplist"], rng)
            m1b = compute_metrics(ap1_block)
            for m in metric_names:
                if np.isnan(m0[m]) or np.isnan(m1b[m]):
                    continue
                block_diffs[m].append(m1b[m] - m0[m])

        for m in metric_names:
            if block_diffs[m]:
                diffs_block[m].append(np.mean(block_diffs[m]))

        # Reversed control
        ap1_rev = reverse_ap(r1["aplist"])
        m1r = compute_metrics(ap1_rev)
        for m in metric_names:
            if np.isnan(m0[m]) or np.isnan(m1r[m]):
                continue
            diffs_reversed[m].append(m1r[m] - m0[m])

    # ── Results ────────────────────────────────────────────────────────
    print()
    print("=" * 72)
    print("RESULTS: PAIRED DIFFERENCES (rank 1 - rank 0, conductor-matched)")
    print("=" * 72)

    results = {}

    for m in metric_names:
        real = np.array(diffs_real[m])
        shuf = np.array(diffs_shuffled[m])
        block = np.array(diffs_block[m])
        rev = np.array(diffs_reversed[m])

        n_real = len(real)
        n_shuf = len(shuf)
        n_block = len(block)
        n_rev = len(rev)

        print(f"\n{'-' * 72}")
        print(f"  METRIC: {m}")
        print(f"{'-' * 72}")

        def analyze(arr, label):
            n = len(arr)
            if n < 10:
                print(f"  {label}: INSUFFICIENT DATA (n={n})")
                return {"n": n, "verdict": "INSUFFICIENT"}
            mean_d = np.mean(arr)
            std_d = np.std(arr, ddof=1)
            cohens_d = mean_d / std_d if std_d > 0 else 0.0
            # Wilcoxon signed-rank (more robust than t-test)
            try:
                w_stat, w_p = stats.wilcoxon(arr, alternative="two-sided")
            except ValueError:
                w_stat, w_p = np.nan, 1.0
            # Also t-test for comparison
            t_stat, t_p = stats.ttest_1samp(arr, 0)

            print(f"  {label}:")
            print(f"    n = {n}")
            print(f"    mean diff = {mean_d:.6f}")
            print(f"    std  diff = {std_d:.6f}")
            print(f"    Cohen's d = {cohens_d:.4f}")
            print(f"    t-test:   t = {t_stat:.3f}, p = {t_p:.4e}")
            print(f"    Wilcoxon: W = {w_stat:.1f}, p = {w_p:.4e}" if not np.isnan(w_stat) else f"    Wilcoxon: FAILED")

            return {
                "n": n,
                "mean_diff": float(mean_d),
                "std_diff": float(std_d),
                "cohens_d": float(cohens_d),
                "t_stat": float(t_stat),
                "t_p": float(t_p),
                "wilcoxon_W": float(w_stat) if not np.isnan(w_stat) else None,
                "wilcoxon_p": float(w_p),
            }

        r_real = analyze(real, "REAL")
        r_shuf = analyze(shuf, "SHUFFLED (full)")
        r_block = analyze(block, "BLOCK-SHUFFLED (k=5)")
        r_rev = analyze(rev, "REVERSED")

        # Verdict
        real_sig = r_real.get("wilcoxon_p", 1) < 0.05
        shuf_sig = r_shuf.get("wilcoxon_p", 1) < 0.05
        block_sig = r_block.get("wilcoxon_p", 1) < 0.05
        rev_sig = r_rev.get("wilcoxon_p", 1) < 0.05

        if real_sig and not shuf_sig:
            verdict = "DYNAMICS"
        elif real_sig and shuf_sig:
            # Check if effect size drops substantially
            real_d = abs(r_real.get("cohens_d", 0))
            shuf_d = abs(r_shuf.get("cohens_d", 0))
            if real_d > 2 * shuf_d:
                verdict = "DYNAMICS (partial)"
            else:
                verdict = "DISTRIBUTION"
        elif not real_sig:
            verdict = "DEAD"
        else:
            verdict = "AMBIGUOUS"

        # Reversal diagnosis
        if real_sig and not rev_sig:
            rev_verdict = "reversal kills → ordering matters"
        elif real_sig and rev_sig:
            rev_verdict = "reversal preserves → distributional"
        else:
            rev_verdict = "N/A"

        print(f"\n  >>> VERDICT: {verdict}")
        print(f"  >>> Reversal: {rev_verdict}")

        results[m] = {
            "real": r_real,
            "shuffled": r_shuf,
            "block_shuffled": r_block,
            "reversed": r_rev,
            "verdict": verdict,
            "reversal_verdict": rev_verdict,
        }

    # ── Rank gradient (triplets) ───────────────────────────────────────
    print(f"\n{'=' * 72}")
    print(f"RANK GRADIENT (triplets: rank 0 → 1 → 2 at same conductor)")
    print(f"{'=' * 72}")
    print(f"Number of triplets: {len(triplets)}")

    triplet_results = {}
    if len(triplets) >= 5:
        for m in metric_names:
            vals = {0: [], 1: [], 2: []}
            for r0, r1, r2 in triplets:
                m0 = compute_metrics(r0["aplist"])[m]
                m1 = compute_metrics(r1["aplist"])[m]
                m2 = compute_metrics(r2["aplist"])[m]
                if not any(np.isnan(x) for x in [m0, m1, m2]):
                    vals[0].append(m0)
                    vals[1].append(m1)
                    vals[2].append(m2)

            n_trip = len(vals[0])
            if n_trip < 5:
                print(f"  {m}: insufficient triplets ({n_trip})")
                continue

            means = {r: np.mean(vals[r]) for r in [0, 1, 2]}
            # Monotonicity: count how many triplets have m0 > m1 > m2 or m0 < m1 < m2
            mono_up = sum(1 for i in range(n_trip) if vals[0][i] < vals[1][i] < vals[2][i])
            mono_down = sum(1 for i in range(n_trip) if vals[0][i] > vals[1][i] > vals[2][i])
            mono_frac = (mono_up + mono_down) / n_trip

            # Jonckheere-Terpstra trend test (manual)
            # Count concordant pairs across ranks
            jt_count = 0
            jt_total = 0
            for ri, rj in [(0, 1), (0, 2), (1, 2)]:
                for vi in vals[ri]:
                    for vj in vals[rj]:
                        jt_total += 1
                        if vj > vi:
                            jt_count += 1
                        elif vj == vi:
                            jt_count += 0.5

            jt_frac = jt_count / jt_total if jt_total > 0 else 0.5

            print(f"\n  {m}:")
            print(f"    n_triplets = {n_trip}")
            print(f"    mean rank0 = {means[0]:.4f}")
            print(f"    mean rank1 = {means[1]:.4f}")
            print(f"    mean rank2 = {means[2]:.4f}")
            print(f"    monotonic fraction = {mono_frac:.3f} (up={mono_up}, down={mono_down})")
            print(f"    JT trend fraction = {jt_frac:.3f} (0.5=no trend)")

            triplet_results[m] = {
                "n_triplets": n_trip,
                "mean_rank0": float(means[0]),
                "mean_rank1": float(means[1]),
                "mean_rank2": float(means[2]),
                "monotonic_fraction": float(mono_frac),
                "jt_trend_fraction": float(jt_frac),
            }
    else:
        print("  Too few triplets for analysis.")

    # ── Cross-validation ───────────────────────────────────────────────
    print(f"\n{'=' * 72}")
    print("CROSS-VALIDATION (70/30 train/test)")
    print("=" * 72)

    indices = np.arange(len(pairs))
    rng.shuffle(indices)
    split = int(0.7 * len(indices))
    train_idx = indices[:split]
    test_idx = indices[split:]

    cv_results = {}
    for m in metric_names:
        real = np.array(diffs_real[m])
        if len(real) < 20:
            print(f"  {m}: insufficient data")
            continue

        # Use same ordering as pairs (diffs are in pair order)
        # But we need to be careful: some pairs may have been skipped (NaN)
        # For simplicity, use the diffs array directly with shuffled indices
        n = len(real)
        cv_idx = np.arange(n)
        rng.shuffle(cv_idx)
        cv_split = int(0.7 * n)
        train = real[cv_idx[:cv_split]]
        test = real[cv_idx[cv_split:]]

        # Train: estimate direction of effect
        train_mean = np.mean(train)
        train_d = train_mean / np.std(train, ddof=1) if np.std(train, ddof=1) > 0 else 0

        # Test: predict direction, measure accuracy
        if train_mean > 0:
            correct = np.sum(test > 0)
        else:
            correct = np.sum(test < 0)
        accuracy = correct / len(test)

        # Test effect size
        test_mean = np.mean(test)
        test_d = test_mean / np.std(test, ddof=1) if np.std(test, ddof=1) > 0 else 0

        # Same direction?
        same_dir = (train_mean > 0) == (test_mean > 0)

        print(f"\n  {m}:")
        print(f"    train n={len(train)}, Cohen's d={train_d:.4f}, mean={train_mean:.6f}")
        print(f"    test  n={len(test)},  Cohen's d={test_d:.4f},  mean={test_mean:.6f}")
        print(f"    direction consistent: {same_dir}")
        print(f"    test accuracy (predicted direction): {accuracy:.3f}")

        cv_results[m] = {
            "train_n": int(len(train)),
            "train_cohens_d": float(train_d),
            "test_n": int(len(test)),
            "test_cohens_d": float(test_d),
            "direction_consistent": bool(same_dir),
            "test_accuracy": float(accuracy),
        }

    # ── Final verdict ──────────────────────────────────────────────────
    print(f"\n{'=' * 72}")
    print("FINAL VERDICT")
    print("=" * 72)

    for m in metric_names:
        v = results[m]["verdict"]
        rv = results[m]["reversal_verdict"]
        real_p = results[m]["real"].get("wilcoxon_p", 1)
        real_d = results[m]["real"].get("cohens_d", 0)
        shuf_d = results[m]["shuffled"].get("cohens_d", 0)
        print(f"  {m}:")
        print(f"    real |d| = {abs(real_d):.4f}, p = {real_p:.4e}")
        print(f"    shuffled |d| = {abs(shuf_d):.4f}")
        print(f"    VERDICT: {v}")
        print(f"    Reversal: {rv}")
        print()

    # ── Save ───────────────────────────────────────────────────────────
    output = {
        "n_pairs": len(pairs),
        "n_triplets": len(triplets),
        "n_conductors_matched": len(pair_conductors),
        "metrics": results,
        "triplet_gradient": triplet_results,
        "cross_validation": cv_results,
    }

    # Make JSON serializable
    out_path = Path("F:/Prometheus/cartography/convergence/data/definitive_rank_test_results.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"Results saved to {out_path}")


if __name__ == "__main__":
    main()

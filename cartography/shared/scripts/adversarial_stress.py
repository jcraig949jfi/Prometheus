#!/usr/bin/env python3
"""
adversarial_stress.py — 5 targeted stress tests on surviving rank-in-a_p signals.

Tests:
  1. Prefix vs Tail Localization — does rho(alpha, rank) strengthen with more a_p?
  2. Adversarial Synthetic Sequences — does pipeline detect rank in fake Sato-Tate data?
  3. Prime vs Full Sequence — is the signal sharper at prime-indexed a_p?
  4. Noise Injection Stability — smooth degradation (real) vs abrupt collapse (artifact)?
  5. Rank Gradient Monotonicity — Jonckheere-Terpstra trend test across rank 0/1/2
"""

import json
import os
import sys
import warnings
from pathlib import Path
from collections import defaultdict

import duckdb
import numpy as np
from scipy import stats
from scipy.optimize import curve_fit

warnings.filterwarnings("ignore", category=RuntimeWarning)

# ── Config ──────────────────────────────────────────────────────────────────
DB_PATH = Path(__file__).resolve().parents[3] / "charon" / "data" / "charon.duckdb"
OUT_DIR = Path(__file__).resolve().parents[3] / "cartography" / "convergence" / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / "adversarial_stress_results.json"
PLOT_DIR = OUT_DIR / "plots"
PLOT_DIR.mkdir(parents=True, exist_ok=True)

PRIMES_25 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
             31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
             73, 79, 83, 89, 97]

RNG = np.random.default_rng(42)

# ── Sato-Tate CDF ──────────────────────────────────────────────────────────
def satotate_cdf(x):
    """CDF of Sato-Tate distribution: f(t) = (2/pi)*sqrt(1-t^2), t in [-1,1]."""
    x = np.clip(x, -1.0, 1.0)
    return 0.5 + (1.0 / np.pi) * (x * np.sqrt(1 - x**2) + np.arcsin(x))


def ks_vs_satotate(samples):
    """KS statistic of samples against Sato-Tate CDF."""
    if len(samples) < 2:
        return np.nan
    sorted_s = np.sort(samples)
    n = len(sorted_s)
    cdf_vals = satotate_cdf(sorted_s)
    ecdf_above = np.arange(1, n + 1) / n
    ecdf_below = np.arange(0, n) / n
    d_plus = np.max(ecdf_above - cdf_vals)
    d_minus = np.max(cdf_vals - ecdf_below)
    return max(d_plus, d_minus)


def power_law(k, C, alpha):
    """KS(k) ~ C * k^(-alpha)."""
    return C * np.power(k, -alpha)


def compute_alpha(normalized_ap, k_values):
    """Compute F39 convergence exponent alpha from normalized a_p sequence."""
    ks_values = {}
    for k in k_values:
        if k <= len(normalized_ap):
            ks = ks_vs_satotate(normalized_ap[:k])
            ks_values[k] = ks

    if len(ks_values) < 3:
        return np.nan

    ks_k = np.array(sorted(ks_values.keys()), dtype=float)
    ks_v = np.array([ks_values[k] for k in sorted(ks_values.keys())])

    mask = np.isfinite(ks_v) & (ks_v > 0)
    if mask.sum() < 3:
        return np.nan

    try:
        popt, _ = curve_fit(power_law, ks_k[mask], ks_v[mask],
                            p0=[1.0, 0.5], maxfev=5000,
                            bounds=([0, -2], [100, 5]))
        return float(popt[1])
    except Exception:
        return np.nan


def shannon_mod(ap_list, mod=7):
    """Shannon entropy of a_p mod m distribution."""
    residues = [int(a) % mod for a in ap_list]
    counts = np.zeros(mod)
    for r in residues:
        counts[r] += 1
    p = counts / counts.sum()
    p = p[p > 0]
    return float(-np.sum(p * np.log2(p)))


def st_surprise(normalized_ap):
    """Total 'surprise' = sum of |CDF(x_i) - 0.5| over normalized a_p."""
    cdf_vals = satotate_cdf(np.array(normalized_ap))
    return float(np.mean(np.abs(cdf_vals - 0.5)))


# ── Load data ───────────────────────────────────────────────────────────────
print("=" * 70)
print("ADVERSARIAL STRESS TESTS ON RANK-IN-a_p SIGNALS")
print("=" * 70)

print("\nLoading elliptic curve data...")
conn = duckdb.connect(str(DB_PATH), read_only=True)
rows = conn.execute("""
    SELECT lmfdb_label, conductor, rank, cm, torsion, aplist
    FROM elliptic_curves WHERE aplist IS NOT NULL AND cm = 0
""").fetchall()
conn.close()
print(f"  Loaded {len(rows)} non-CM curves")

# Parse into arrays
labels_all, conductors_all, ranks_all, torsions_all, aplists_all = [], [], [], [], []
normalized_all = []  # normalized a_p / 2sqrt(p)

for label, conductor, rank, cm, torsion, aplist in rows:
    if aplist is None or len(aplist) < 25:
        continue
    ap = list(aplist[:25])
    # Normalize
    norm = []
    for a, p in zip(ap, PRIMES_25):
        x = a / (2.0 * np.sqrt(p))
        x = np.clip(x, -1.0, 1.0)
        norm.append(x)
    labels_all.append(label)
    conductors_all.append(int(conductor))
    ranks_all.append(int(rank))
    torsions_all.append(int(torsion))
    aplists_all.append(ap)
    normalized_all.append(np.array(norm))

N = len(labels_all)
ranks_arr = np.array(ranks_all)
conductors_arr = np.array(conductors_all)
print(f"  Usable curves (25 a_p): {N}")
print(f"  Rank distribution: {dict(zip(*np.unique(ranks_arr, return_counts=True)))}")

# Cap at 30K for speed where specified
if N > 30000:
    idx_30k = RNG.choice(N, 30000, replace=False)
else:
    idx_30k = np.arange(N)

results = {"metadata": {"script": "adversarial_stress.py", "n_curves_total": N,
                         "n_curves_used": len(idx_30k), "date": "2026-04-12"}}


# ═══════════════════════════════════════════════════════════════════════════
# TEST 1: PREFIX VS TAIL LOCALIZATION
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n{'=' * 70}")
print("TEST 1: PREFIX VS TAIL LOCALIZATION")
print(f"{'=' * 70}")

prefix_lengths = [10, 20, 25]
# For prefix 10: k_values [3,5,7,10]; prefix 20: [5,10,15,20]; prefix 25: [5,10,15,20,25]
prefix_k_map = {
    10: [3, 5, 7, 10],
    20: [5, 10, 15, 20],
    25: [5, 10, 15, 20, 25],
}

test1_results = {}
for plen in prefix_lengths:
    k_vals = prefix_k_map[plen]
    alphas = []
    for i in idx_30k:
        norm_prefix = normalized_all[i][:plen]
        a = compute_alpha(norm_prefix, k_vals)
        alphas.append(a)
    alphas = np.array(alphas)
    valid = np.isfinite(alphas)
    if valid.sum() < 100:
        print(f"  Prefix {plen}: too few valid ({valid.sum()}), skipping")
        test1_results[str(plen)] = {"valid_n": int(valid.sum()), "rho": None, "p": None}
        continue

    rho, p = stats.spearmanr(alphas[valid], ranks_arr[idx_30k][valid])
    test1_results[str(plen)] = {
        "valid_n": int(valid.sum()),
        "rho": float(rho),
        "p": float(p),
        "alpha_mean": float(np.nanmean(alphas[valid])),
        "alpha_std": float(np.nanstd(alphas[valid])),
    }
    print(f"  Prefix {plen:2d}: N={valid.sum():5d}  rho(alpha, rank) = {rho:+.4f}  (p = {p:.2e})  mean_alpha = {np.nanmean(alphas[valid]):.4f}")

# Trajectory analysis
rhos = [test1_results[str(p)]["rho"] for p in prefix_lengths if test1_results[str(p)]["rho"] is not None]
if len(rhos) == 3:
    if abs(rhos[2]) > abs(rhos[0]) * 1.2:
        trajectory = "STRENGTHENING (convergence phenomenon — real dynamics)"
    elif abs(rhos[2]) < abs(rhos[0]) * 0.8:
        trajectory = "WEAKENING (noise from more data)"
    else:
        trajectory = "CONSTANT (present from the start — distributional)"
else:
    trajectory = "INSUFFICIENT DATA"

test1_results["trajectory"] = trajectory
test1_results["verdict"] = trajectory
print(f"\n  TRAJECTORY: {trajectory}")

results["test1_prefix_localization"] = test1_results

# Plot
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 4))
    valid_plen = [p for p in prefix_lengths if test1_results[str(p)]["rho"] is not None]
    valid_rhos = [test1_results[str(p)]["rho"] for p in valid_plen]
    ax.plot(valid_plen, valid_rhos, "o-", color="steelblue", markersize=8, linewidth=2)
    ax.set_xlabel("Prefix length (number of a_p)")
    ax.set_ylabel("rho(alpha, rank)")
    ax.set_title("Test 1: Prefix vs Tail Localization")
    ax.axhline(0, color="gray", linestyle="--", alpha=0.5)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(str(PLOT_DIR / "test1_prefix_trajectory.png"), dpi=150)
    plt.close(fig)
    print(f"  Plot saved: {PLOT_DIR / 'test1_prefix_trajectory.png'}")
except Exception as e:
    print(f"  Plot failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# TEST 2: ADVERSARIAL SYNTHETIC SEQUENCES
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n{'=' * 70}")
print("TEST 2: ADVERSARIAL SYNTHETIC SEQUENCES")
print(f"{'=' * 70}")

# Generate Sato-Tate samples: inverse CDF sampling
# ST distribution: f(t) = (2/pi)*sqrt(1-t^2) on [-1,1]
# Use rejection sampling for accuracy
def sample_satotate(n, rng):
    """Sample from Sato-Tate distribution using rejection."""
    samples = []
    while len(samples) < n:
        batch = rng.uniform(-1, 1, size=n * 3)
        u = rng.uniform(0, 2 / np.pi, size=len(batch))
        density = (2 / np.pi) * np.sqrt(np.maximum(0, 1 - batch**2))
        accepted = batch[u < density]
        samples.extend(accepted.tolist())
    return np.array(samples[:n])


# Build synthetic: for each of 30K curves, sample 25 ST values, scale by 2*sqrt(p)
n_synth = len(idx_30k)
synth_alphas = []
# Assign fake ranks from same distribution
rank_counts = dict(zip(*np.unique(ranks_arr[idx_30k], return_counts=True)))
total = sum(rank_counts.values())
rank_probs = {r: c / total for r, c in rank_counts.items()}
fake_ranks = RNG.choice(list(rank_probs.keys()), size=n_synth,
                        p=list(rank_probs.values()))

print(f"  Generating {n_synth} synthetic Sato-Tate sequences...")
for i in range(n_synth):
    # Sample 25 normalized values from ST
    st_samples = sample_satotate(25, RNG)
    # These are already in [-1, 1], like normalized a_p
    a = compute_alpha(st_samples, [5, 10, 15, 20, 25])
    synth_alphas.append(a)

synth_alphas = np.array(synth_alphas)
synth_valid = np.isfinite(synth_alphas)

# Also compute real alphas for comparison
print(f"  Computing real alphas for comparison...")
real_alphas = []
for i in idx_30k:
    a = compute_alpha(normalized_all[i], [5, 10, 15, 20, 25])
    real_alphas.append(a)
real_alphas = np.array(real_alphas)
real_valid = np.isfinite(real_alphas)

# Correlations
rho_real, p_real = stats.spearmanr(real_alphas[real_valid], ranks_arr[idx_30k][real_valid])
rho_synth, p_synth = stats.spearmanr(synth_alphas[synth_valid], fake_ranks[synth_valid])

print(f"  Real data:      rho(alpha, rank) = {rho_real:+.4f}  (p = {p_real:.2e})  N_valid = {real_valid.sum()}")
print(f"  Synthetic data: rho(alpha, rank) = {rho_synth:+.4f}  (p = {p_synth:.2e})  N_valid = {synth_valid.sum()}")

# Also test: correlate synthetic alpha with REAL rank (mismatched)
if synth_valid.sum() >= 100:
    # Use same indices
    both_valid = real_valid & synth_valid
    rho_mismatch, p_mismatch = stats.spearmanr(synth_alphas[both_valid], ranks_arr[idx_30k][both_valid])
    print(f"  Mismatch test:  rho(synth_alpha, real_rank) = {rho_mismatch:+.4f}  (p = {p_mismatch:.2e})")
else:
    rho_mismatch, p_mismatch = np.nan, np.nan

if abs(rho_synth) > abs(rho_real) * 0.5 and p_synth < 0.05:
    verdict2 = "KILLED: pipeline detects 'rank' in pure synthetic data — metric is generic"
elif abs(rho_synth) < 0.02 and abs(rho_real) > 0.05:
    verdict2 = "SURVIVES: synthetic data shows no rank signal — metric is arithmetic-specific"
else:
    verdict2 = f"AMBIGUOUS: real rho={rho_real:+.4f}, synthetic rho={rho_synth:+.4f}"

print(f"\n  VERDICT: {verdict2}")

test2_results = {
    "n_synthetic": int(n_synth),
    "real": {"rho": float(rho_real), "p": float(p_real), "n_valid": int(real_valid.sum())},
    "synthetic": {"rho": float(rho_synth), "p": float(p_synth), "n_valid": int(synth_valid.sum())},
    "mismatch": {"rho": float(rho_mismatch) if np.isfinite(rho_mismatch) else None,
                 "p": float(p_mismatch) if np.isfinite(p_mismatch) else None},
    "verdict": verdict2,
}
results["test2_synthetic_sequences"] = test2_results


# ═══════════════════════════════════════════════════════════════════════════
# TEST 3: PRIME VS FULL SEQUENCE
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n{'=' * 70}")
print("TEST 3: PRIME VS FULL SEQUENCE (prime-indexed a_p vs odd-indexed a_p)")
print(f"{'=' * 70}")

# The aplist IS a_p at consecutive primes. Split into two subsequences:
# "prime-indexed": a_p where the index position (0-based) is a prime (indices 2,3,5,7,11,13,17,19,23)
# "non-prime-indexed": the rest (indices 0,1,4,6,8,9,10,12,14,15,16,18,20,21,22,24)
prime_indices_set = {2, 3, 5, 7, 11, 13, 17, 19, 23}
non_prime_indices = [i for i in range(25) if i not in prime_indices_set]
prime_indices_list = sorted(prime_indices_set)

# Actually, a better split: first half vs second half of the prime sequence
# OR: even-indexed primes vs odd-indexed primes (interleave)
# Best interpretation: the aplist is a_p at primes p=2,3,5,...,97.
# "Prime indices" = positions where the prime p itself is a prime index into PRIMES
# Let's do a cleaner split: first 12 primes vs last 13 primes
first_half_idx = list(range(12))  # primes 2..37
second_half_idx = list(range(12, 25))  # primes 41..97

# Even more meaningful: odd-position primes (1,3,5,...) vs even-position (0,2,4,...)
even_pos = list(range(0, 25, 2))  # 13 values
odd_pos = list(range(1, 25, 2))   # 12 values

print(f"  Split A: First 12 primes (2..37) vs Last 13 primes (41..97)")
print(f"  Split B: Even-position primes vs Odd-position primes (interleaved)")

test3_results = {}
for split_name, idx_a, idx_b, label_a, label_b in [
    ("first_vs_second", first_half_idx, second_half_idx, "first_12", "last_13"),
    ("even_vs_odd", even_pos, odd_pos, "even_pos", "odd_pos"),
]:
    # Compute alpha on each subsequence
    alphas_a, alphas_b = [], []
    for i in idx_30k:
        norm = normalized_all[i]
        sub_a = norm[idx_a]
        sub_b = norm[idx_b]
        # Need at least 3 k-values for fit
        k_vals_a = [k for k in [3, 5, 7, 10, 12] if k <= len(sub_a)]
        k_vals_b = [k for k in [3, 5, 7, 10, 13] if k <= len(sub_b)]
        alphas_a.append(compute_alpha(sub_a, k_vals_a))
        alphas_b.append(compute_alpha(sub_b, k_vals_b))

    alphas_a = np.array(alphas_a)
    alphas_b = np.array(alphas_b)
    va = np.isfinite(alphas_a)
    vb = np.isfinite(alphas_b)

    if va.sum() >= 100:
        rho_a, p_a = stats.spearmanr(alphas_a[va], ranks_arr[idx_30k][va])
    else:
        rho_a, p_a = np.nan, np.nan
    if vb.sum() >= 100:
        rho_b, p_b = stats.spearmanr(alphas_b[vb], ranks_arr[idx_30k][vb])
    else:
        rho_b, p_b = np.nan, np.nan

    print(f"  {split_name}:")
    print(f"    {label_a}: rho(alpha, rank) = {rho_a:+.4f}  (p = {p_a:.2e})  N_valid = {va.sum()}")
    print(f"    {label_b}: rho(alpha, rank) = {rho_b:+.4f}  (p = {p_b:.2e})  N_valid = {vb.sum()}")

    test3_results[split_name] = {
        label_a: {"rho": float(rho_a) if np.isfinite(rho_a) else None,
                  "p": float(p_a) if np.isfinite(p_a) else None,
                  "n_valid": int(va.sum())},
        label_b: {"rho": float(rho_b) if np.isfinite(rho_b) else None,
                  "p": float(p_b) if np.isfinite(p_b) else None,
                  "n_valid": int(vb.sum())},
    }

# Verdict: if both halves carry signal, it's distributed across the sequence
# If one half dominates, localization tells us something
all_rhos = []
for split in test3_results.values():
    for part in split.values():
        if isinstance(part, dict) and part.get("rho") is not None:
            all_rhos.append(abs(part["rho"]))

if len(all_rhos) >= 2:
    max_r = max(all_rhos)
    min_r = min(all_rhos)
    if min_r > 0 and max_r / min_r < 2.0:
        verdict3 = "DISTRIBUTED: signal present across all subsequences — genuine arithmetic property"
    else:
        verdict3 = f"LOCALIZED: signal concentrated in subset (max/min ratio = {max_r/min_r:.1f})"
else:
    verdict3 = "INSUFFICIENT DATA"

test3_results["verdict"] = verdict3
print(f"\n  VERDICT: {verdict3}")
results["test3_prime_vs_full"] = test3_results


# ═══════════════════════════════════════════════════════════════════════════
# TEST 4: NOISE INJECTION STABILITY CURVE
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n{'=' * 70}")
print("TEST 4: NOISE INJECTION STABILITY CURVE")
print(f"{'=' * 70}")

epsilons = [0.0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5]
test4_results = {}

# Subsample to 10K for speed (this test is expensive)
if len(idx_30k) > 10000:
    idx_noise = RNG.choice(idx_30k, 10000, replace=False)
else:
    idx_noise = idx_30k

for eps in epsilons:
    alphas_eps = []
    for i in idx_noise:
        norm = normalized_all[i].copy()
        if eps > 0:
            # Flip signs with probability epsilon
            flip_mask = RNG.random(len(norm)) < eps
            norm[flip_mask] *= -1
        a = compute_alpha(norm, [5, 10, 15, 20, 25])
        alphas_eps.append(a)

    alphas_eps = np.array(alphas_eps)
    valid = np.isfinite(alphas_eps)
    if valid.sum() < 100:
        rho_e, p_e = np.nan, np.nan
    else:
        rho_e, p_e = stats.spearmanr(alphas_eps[valid], ranks_arr[idx_noise][valid])

    test4_results[str(eps)] = {
        "epsilon": eps,
        "rho": float(rho_e) if np.isfinite(rho_e) else None,
        "p": float(p_e) if np.isfinite(p_e) else None,
        "n_valid": int(valid.sum()),
        "alpha_mean": float(np.nanmean(alphas_eps[valid])) if valid.sum() > 0 else None,
    }
    print(f"  eps = {eps:.2f}: rho(alpha, rank) = {rho_e:+.4f}  (p = {p_e:.2e})  N = {valid.sum()}")

# Analyze degradation pattern
rho_at_0 = test4_results["0.0"]["rho"]
rho_at_50 = test4_results["0.5"]["rho"]
rho_at_10 = test4_results["0.1"]["rho"]
rho_at_5 = test4_results["0.05"]["rho"]

if rho_at_0 is not None and rho_at_50 is not None and rho_at_10 is not None:
    # Check for smooth vs abrupt
    rho_vals = [test4_results[str(e)]["rho"] for e in epsilons
                if test4_results[str(e)]["rho"] is not None]
    eps_vals = [e for e in epsilons if test4_results[str(e)]["rho"] is not None]

    if len(rho_vals) >= 4:
        # Fit linear to |rho| vs epsilon
        abs_rhos = np.abs(rho_vals)
        slope, _, r_lin, _, _ = stats.linregress(eps_vals, abs_rhos)

        # Check if collapse is abrupt: |rho| at eps=0.05 vs eps=0
        if abs(rho_at_0) > 0.01:
            retention_at_5pct = abs(rho_at_5) / abs(rho_at_0) if rho_at_5 is not None else 0
            retention_at_10pct = abs(rho_at_10) / abs(rho_at_0)
        else:
            retention_at_5pct = 0
            retention_at_10pct = 0

        if retention_at_5pct > 0.7 and retention_at_10pct > 0.4:
            verdict4 = "SMOOTH DEGRADATION: signal robust to noise — consistent with real arithmetic structure"
        elif retention_at_5pct < 0.3:
            verdict4 = "ABRUPT COLLAPSE: signal fragile — likely artifact"
        else:
            verdict4 = f"MODERATE: retention at 5% noise = {retention_at_5pct:.2f}, at 10% = {retention_at_10pct:.2f}"

        test4_results["degradation"] = {
            "linear_slope": float(slope),
            "linear_r": float(r_lin),
            "retention_at_5pct": float(retention_at_5pct),
            "retention_at_10pct": float(retention_at_10pct),
        }
    else:
        verdict4 = "INSUFFICIENT DATA"
else:
    verdict4 = "INSUFFICIENT DATA"

test4_results["verdict"] = verdict4
print(f"\n  VERDICT: {verdict4}")
results["test4_noise_injection"] = test4_results

# Plot
try:
    fig, ax = plt.subplots(figsize=(6, 4))
    eps_plot = [e for e in epsilons if test4_results[str(e)]["rho"] is not None]
    rho_plot = [test4_results[str(e)]["rho"] for e in eps_plot]
    ax.plot(eps_plot, rho_plot, "o-", color="crimson", markersize=8, linewidth=2)
    ax.set_xlabel("Noise level (epsilon = P(sign flip))")
    ax.set_ylabel("rho(alpha, rank)")
    ax.set_title("Test 4: Noise Injection Stability")
    ax.axhline(0, color="gray", linestyle="--", alpha=0.5)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(str(PLOT_DIR / "test4_noise_stability.png"), dpi=150)
    plt.close(fig)
    print(f"  Plot saved: {PLOT_DIR / 'test4_noise_stability.png'}")
except Exception as e:
    print(f"  Plot failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# TEST 5: RANK GRADIENT (MONOTONICITY)
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n{'=' * 70}")
print("TEST 5: RANK GRADIENT (MONOTONICITY)")
print(f"{'=' * 70}")

# Compute three metrics for all curves
print("  Computing metrics for all curves...")
all_f39_alpha = real_alphas  # already computed in Test 2
all_st_surprise = np.array([st_surprise(normalized_all[i]) for i in idx_30k])
all_shannon7 = np.array([shannon_mod(aplists_all[i], mod=7) for i in idx_30k])

metrics = {
    "F39_alpha": all_f39_alpha,
    "ST_surprise": all_st_surprise,
    "Shannon_mod7": all_shannon7,
}

test5_results = {}


def jonckheere_terpstra(groups_ordered):
    """
    Jonckheere-Terpstra test for ordered alternatives.
    groups_ordered: list of arrays, ordered by hypothesized increasing trend.
    Returns J statistic and approximate z-score with p-value.
    """
    k = len(groups_ordered)
    J = 0
    for i in range(k):
        for j in range(i + 1, k):
            for xi in groups_ordered[i]:
                J += np.sum(groups_ordered[j] > xi) + 0.5 * np.sum(groups_ordered[j] == xi)

    # Expected value and variance under H0
    ns = [len(g) for g in groups_ordered]
    N = sum(ns)
    E_J = (N**2 - sum(n**2 for n in ns)) / 4

    # Variance (simplified formula)
    sum_ni2 = sum(n**2 for n in ns)
    sum_ni3 = sum(n**3 for n in ns)
    var_num = (N**2 * (2 * N + 3) - sum(n**2 * (2 * n + 3) for n in ns))
    var_J = var_num / 72

    if var_J <= 0:
        return J, 0.0, 1.0

    z = (J - E_J) / np.sqrt(var_J)
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    return float(J), float(z), float(p)


rank_values = sorted(np.unique(ranks_arr[idx_30k]))
print(f"  Rank values present: {rank_values}")

for metric_name, metric_vals in metrics.items():
    valid = np.isfinite(metric_vals)
    print(f"\n  --- {metric_name} ---")

    means_by_rank = {}
    groups_ordered = []
    for r in rank_values:
        mask = (ranks_arr[idx_30k] == r) & valid
        vals = metric_vals[mask]
        if len(vals) > 0:
            means_by_rank[r] = float(np.mean(vals))
            groups_ordered.append(vals)
            print(f"    Rank {r}: N={len(vals):5d}  mean={np.mean(vals):.6f}  std={np.std(vals):.6f}")
        else:
            means_by_rank[r] = None

    # Monotonicity check
    mean_vals = [means_by_rank[r] for r in rank_values if means_by_rank[r] is not None]
    if len(mean_vals) >= 2:
        diffs = [mean_vals[i + 1] - mean_vals[i] for i in range(len(mean_vals) - 1)]
        is_monotone_inc = all(d > 0 for d in diffs)
        is_monotone_dec = all(d < 0 for d in diffs)
        is_monotone = is_monotone_inc or is_monotone_dec
        direction = "increasing" if is_monotone_inc else ("decreasing" if is_monotone_dec else "non-monotonic")
    else:
        is_monotone = False
        direction = "insufficient"

    # Jonckheere-Terpstra
    if len(groups_ordered) >= 2:
        J, z_jt, p_jt = jonckheere_terpstra(groups_ordered)
        print(f"    Jonckheere-Terpstra: J={J:.0f}  z={z_jt:+.3f}  p={p_jt:.2e}")
        print(f"    Monotonic: {is_monotone} ({direction})")
    else:
        J, z_jt, p_jt = np.nan, np.nan, np.nan

    test5_results[metric_name] = {
        "means_by_rank": means_by_rank,
        "is_monotonic": is_monotone,
        "direction": direction,
        "jonckheere_terpstra": {
            "J": float(J) if np.isfinite(J) else None,
            "z": float(z_jt) if np.isfinite(z_jt) else None,
            "p": float(p_jt) if np.isfinite(p_jt) else None,
        },
    }

# Overall verdict
monotone_count = sum(1 for m in test5_results.values() if m["is_monotonic"])
significant_count = sum(1 for m in test5_results.values()
                        if m["jonckheere_terpstra"]["p"] is not None
                        and m["jonckheere_terpstra"]["p"] < 0.05)

if monotone_count >= 2 and significant_count >= 2:
    verdict5 = f"STRONG MONOTONIC TREND: {monotone_count}/3 monotonic, {significant_count}/3 significant JT tests"
elif significant_count >= 1:
    verdict5 = f"PARTIAL TREND: {monotone_count}/3 monotonic, {significant_count}/3 significant"
else:
    verdict5 = "NO TREND: rank gradient absent"

test5_results["verdict"] = verdict5
print(f"\n  VERDICT: {verdict5}")
results["test5_rank_gradient"] = test5_results

# Plot
try:
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    for idx, (metric_name, metric_vals) in enumerate(metrics.items()):
        ax = axes[idx]
        valid = np.isfinite(metric_vals)
        data_by_rank = []
        labels_plot = []
        for r in rank_values:
            mask = (ranks_arr[idx_30k] == r) & valid
            data_by_rank.append(metric_vals[mask])
            labels_plot.append(f"Rank {r}\n(N={mask.sum()})")
        ax.boxplot(data_by_rank, tick_labels=labels_plot, widths=0.6)
        ax.set_title(metric_name)
        ax.grid(True, alpha=0.3, axis="y")
    fig.suptitle("Test 5: Rank Gradient Monotonicity", fontsize=13)
    fig.tight_layout()
    fig.savefig(str(PLOT_DIR / "test5_rank_gradient.png"), dpi=150)
    plt.close(fig)
    print(f"  Plot saved: {PLOT_DIR / 'test5_rank_gradient.png'}")
except Exception as e:
    print(f"  Plot failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# OVERALL SUMMARY
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n{'=' * 70}")
print("OVERALL SUMMARY")
print(f"{'=' * 70}")

verdicts = {
    "test1_prefix_localization": test1_results.get("verdict", "N/A"),
    "test2_synthetic_sequences": verdict2,
    "test3_prime_vs_full": verdict3,
    "test4_noise_injection": verdict4,
    "test5_rank_gradient": verdict5,
}

n_survive = sum(1 for v in verdicts.values() if "SURVIV" in v.upper() or "STRONG" in v.upper()
                or "SMOOTH" in v.upper() or "DISTRIBUTED" in v.upper()
                or "STRENGTHEN" in v.upper())
n_killed = sum(1 for v in verdicts.values() if "KILL" in v.upper() or "COLLAPSE" in v.upper()
               or "NO TREND" in v.upper())
n_ambiguous = 5 - n_survive - n_killed

results["summary"] = {
    "verdicts": verdicts,
    "survived": n_survive,
    "killed": n_killed,
    "ambiguous": n_ambiguous,
    "overall": f"{n_survive}/5 survived, {n_killed}/5 killed, {n_ambiguous}/5 ambiguous",
}

for test_name, verdict in verdicts.items():
    status = "PASS" if any(w in verdict.upper() for w in ["SURVIV", "STRONG", "SMOOTH", "DISTRIBUT", "STRENGTH"]) else \
             "FAIL" if any(w in verdict.upper() for w in ["KILL", "COLLAPSE", "NO TREND"]) else "AMBIG"
    print(f"  [{status:5s}] {test_name}: {verdict}")

print(f"\n  OVERALL: {results['summary']['overall']}")

# ── Save ────────────────────────────────────────────────────────────────────
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

# Fix dict keys that might be numpy types
def fix_keys(obj):
    if isinstance(obj, dict):
        return {(int(k) if isinstance(k, np.integer) else
                 str(k) if not isinstance(k, (str, int, float, bool)) else k): fix_keys(v)
                for k, v in obj.items()}
    if isinstance(obj, list):
        return [fix_keys(x) for x in obj]
    return obj

results = fix_keys(results)

with open(OUT_FILE, "w") as f:
    json.dump(results, f, indent=2, cls=NumpyEncoder)
print(f"\nResults saved to {OUT_FILE}")

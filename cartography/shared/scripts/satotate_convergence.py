#!/usr/bin/env python3
"""
satotate_convergence.py — Measure convergence rate to Sato-Tate distribution
for non-CM elliptic curves and test whether the rate is a new invariant.

F39 candidate: alpha (convergence exponent) from KS(k) ~ C * k^(-alpha).

Kill prediction: alpha is just a noisy proxy for conductor.
"""

import json
import os
import sys
import warnings
from pathlib import Path

import duckdb
import numpy as np
from scipy import stats
from scipy.optimize import curve_fit

warnings.filterwarnings("ignore", category=RuntimeWarning)

# ── Config ──────────────────────────────────────────────────────────────────
DB_PATH = Path(__file__).resolve().parents[3] / "charon" / "data" / "charon.duckdb"
OUT_DIR = Path(__file__).resolve().parents[3] / "cartography" / "convergence" / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / "satotate_convergence_results.json"

# First 25 primes (matching aplist length in LMFDB)
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
          31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
          73, 79, 83, 89, 97]

# k-values for convergence measurement
K_VALUES = [5, 10, 15, 20, 25]

N_PERMUTATIONS = 1000
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


# ── Load data ───────────────────────────────────────────────────────────────
print("Loading elliptic curve data...")
conn = duckdb.connect(str(DB_PATH), read_only=True)
rows = conn.execute("""
    SELECT lmfdb_label, conductor, rank, analytic_rank, torsion, cm, aplist, bad_primes
    FROM elliptic_curves
    WHERE aplist IS NOT NULL AND cm = 0
""").fetchall()
conn.close()
print(f"  Loaded {len(rows)} non-CM curves")

# ── Compute convergence for each curve ──────────────────────────────────────
print("Computing Sato-Tate convergence rates...")

records = []
for label, conductor, rank, analytic_rank, torsion, cm, aplist, bad_primes in rows:
    if aplist is None or len(aplist) < 20:
        continue

    bad_set = set(bad_primes) if bad_primes else set()

    # Normalize: x_i = a_p / (2 * sqrt(p)), skip bad primes
    normalized = []
    prime_indices = []  # which index into PRIMES we used
    for i, (ap, p) in enumerate(zip(aplist, PRIMES)):
        if p in bad_set:
            continue
        x = ap / (2.0 * np.sqrt(p))
        # Clamp to [-1, 1] (Hasse bound guarantees this, but numerical safety)
        x = np.clip(x, -1.0, 1.0)
        normalized.append(x)
        prime_indices.append(i)

    if len(normalized) < 20:
        continue

    normalized = np.array(normalized)

    # KS at each k-value
    ks_values = {}
    for k in K_VALUES:
        if k <= len(normalized):
            ks = ks_vs_satotate(normalized[:k])
            ks_values[k] = ks

    if len(ks_values) < 3:
        continue

    # Fit power law: KS(k) ~ C * k^(-alpha)
    ks_k = np.array(sorted(ks_values.keys()))
    ks_v = np.array([ks_values[k] for k in ks_k])

    # Filter out any nan/inf
    mask = np.isfinite(ks_v) & (ks_v > 0)
    if mask.sum() < 3:
        continue

    ks_k_clean = ks_k[mask].astype(float)
    ks_v_clean = ks_v[mask]

    try:
        popt, _ = curve_fit(power_law, ks_k_clean, ks_v_clean,
                            p0=[1.0, 0.5], maxfev=5000,
                            bounds=([0, -2], [100, 5]))
        C_fit, alpha_fit = popt
    except Exception:
        continue

    records.append({
        "label": label,
        "conductor": int(conductor),
        "rank": int(rank),
        "analytic_rank": int(analytic_rank) if analytic_rank is not None else None,
        "torsion": int(torsion),
        "alpha": float(alpha_fit),
        "C": float(C_fit),
        "final_ks": float(ks_values[max(ks_values.keys())]),
        "n_good_primes": len(normalized),
        "ks_trajectory": {str(k): float(v) for k, v in ks_values.items()},
    })

print(f"  Computed convergence for {len(records)} curves")

if len(records) < 50:
    print("ERROR: Too few curves with valid fits. Aborting.")
    sys.exit(1)

# ── Build arrays ────────────────────────────────────────────────────────────
alphas = np.array([r["alpha"] for r in records])
conductors = np.array([r["conductor"] for r in records])
ranks = np.array([r["rank"] for r in records])
torsions = np.array([r["torsion"] for r in records])
log_conductors = np.log10(conductors + 1)

print(f"\n{'='*60}")
print("DISTRIBUTION OF ALPHA")
print(f"{'='*60}")
print(f"  N       = {len(alphas)}")
print(f"  Mean    = {np.mean(alphas):.4f}")
print(f"  Median  = {np.median(alphas):.4f}")
print(f"  Std     = {np.std(alphas):.4f}")
print(f"  Min     = {np.min(alphas):.4f}")
print(f"  Max     = {np.max(alphas):.4f}")
print(f"  Q25     = {np.percentile(alphas, 25):.4f}")
print(f"  Q75     = {np.percentile(alphas, 75):.4f}")

# ── Raw correlations ────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("RAW SPEARMAN CORRELATIONS")
print(f"{'='*60}")

rho_rank, p_rank = stats.spearmanr(alphas, ranks)
rho_torsion, p_torsion = stats.spearmanr(alphas, torsions)
rho_conductor, p_conductor = stats.spearmanr(alphas, log_conductors)

print(f"  rho(alpha, rank)          = {rho_rank:+.4f}  (p = {p_rank:.2e})")
print(f"  rho(alpha, torsion)       = {rho_torsion:+.4f}  (p = {p_torsion:.2e})")
print(f"  rho(alpha, log_conductor) = {rho_conductor:+.4f}  (p = {p_conductor:.2e})")

# ── Partial correlations ────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("PARTIAL CORRELATIONS")
print(f"{'='*60}")


def partial_correlation(x, y, covariates):
    """Partial Spearman correlation: residualize x and y on covariates, then correlate."""
    from numpy.linalg import lstsq
    # Rank-transform for Spearman
    rx = stats.rankdata(x)
    ry = stats.rankdata(y)
    rc = np.column_stack([stats.rankdata(c) for c in covariates])
    # Residualize
    rc_aug = np.column_stack([rc, np.ones(len(rc))])
    bx, _, _, _ = lstsq(rc_aug, rx, rcond=None)
    by, _, _, _ = lstsq(rc_aug, ry, rcond=None)
    res_x = rx - rc_aug @ bx
    res_y = ry - rc_aug @ by
    return stats.spearmanr(res_x, res_y)


rho_ar_c, p_ar_c = partial_correlation(alphas, ranks, [log_conductors])
rho_at_cr, p_at_cr = partial_correlation(alphas, torsions, [log_conductors, ranks])

print(f"  rho(alpha, rank | conductor)              = {rho_ar_c:+.4f}  (p = {p_ar_c:.2e})")
print(f"  rho(alpha, torsion | conductor, rank)      = {rho_at_cr:+.4f}  (p = {p_at_cr:.2e})")

# ── Within-bin analysis ─────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("WITHIN-BIN ANALYSIS")
print(f"{'='*60}")

# Within conductor bins: rho(alpha, rank)
print("\n  Within log(conductor) bins — rho(alpha, rank):")
cond_bins = np.percentile(log_conductors, np.linspace(0, 100, 11))
for i in range(10):
    mask = (log_conductors >= cond_bins[i]) & (log_conductors < cond_bins[i + 1])
    if i == 9:  # include upper edge
        mask = (log_conductors >= cond_bins[i]) & (log_conductors <= cond_bins[i + 1])
    if mask.sum() < 10:
        continue
    a_bin = alphas[mask]
    r_bin = ranks[mask]
    if len(np.unique(r_bin)) < 2:
        print(f"    Bin {i}: [{cond_bins[i]:.2f}, {cond_bins[i+1]:.2f})  N={mask.sum():5d}  — rank constant, skip")
        continue
    rho_b, p_b = stats.spearmanr(a_bin, r_bin)
    print(f"    Bin {i}: [{cond_bins[i]:.2f}, {cond_bins[i+1]:.2f})  N={mask.sum():5d}  rho={rho_b:+.4f}  p={p_b:.2e}")

# Within rank bins: rho(alpha, conductor)
print("\n  Within rank bins — rho(alpha, log_conductor):")
for r_val in sorted(np.unique(ranks)):
    mask = ranks == r_val
    if mask.sum() < 10:
        continue
    a_bin = alphas[mask]
    c_bin = log_conductors[mask]
    rho_b, p_b = stats.spearmanr(a_bin, c_bin)
    print(f"    Rank {r_val}: N={mask.sum():5d}  rho={rho_b:+.4f}  p={p_b:.2e}")

# ── Permutation null ────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("PERMUTATION NULL (1000 shuffles)")
print(f"{'='*60}")

perm_rho_rank = []
perm_rho_torsion = []
perm_rho_conductor = []
perm_partial_rank = []

for _ in range(N_PERMUTATIONS):
    shuffled = RNG.permutation(alphas)
    perm_rho_rank.append(stats.spearmanr(shuffled, ranks)[0])
    perm_rho_torsion.append(stats.spearmanr(shuffled, torsions)[0])
    perm_rho_conductor.append(stats.spearmanr(shuffled, log_conductors)[0])
    pr, _ = partial_correlation(shuffled, ranks, [log_conductors])
    perm_partial_rank.append(pr)

perm_rho_rank = np.array(perm_rho_rank)
perm_rho_torsion = np.array(perm_rho_torsion)
perm_rho_conductor = np.array(perm_rho_conductor)
perm_partial_rank = np.array(perm_partial_rank)


def perm_pvalue(observed, null_dist):
    return (np.abs(null_dist) >= np.abs(observed)).mean()


p_perm_rank = perm_pvalue(rho_rank, perm_rho_rank)
p_perm_torsion = perm_pvalue(rho_torsion, perm_rho_torsion)
p_perm_conductor = perm_pvalue(rho_conductor, perm_rho_conductor)
p_perm_partial = perm_pvalue(rho_ar_c, perm_partial_rank)

print(f"  rho(alpha, rank):                obs={rho_rank:+.4f}  null_std={perm_rho_rank.std():.4f}  p_perm={p_perm_rank:.4f}")
print(f"  rho(alpha, torsion):             obs={rho_torsion:+.4f}  null_std={perm_rho_torsion.std():.4f}  p_perm={p_perm_torsion:.4f}")
print(f"  rho(alpha, log_conductor):       obs={rho_conductor:+.4f}  null_std={perm_rho_conductor.std():.4f}  p_perm={p_perm_conductor:.4f}")
print(f"  rho(alpha, rank | conductor):    obs={rho_ar_c:+.4f}  null_std={perm_partial_rank.std():.4f}  p_perm={p_perm_partial:.4f}")

# ── F33 check: sort-then-correlate ──────────────────────────────────────────
print(f"\n{'='*60}")
print("F33 CHECK (sort-then-correlate artifact)")
print(f"{'='*60}")

sorted_alpha = np.sort(alphas)
sorted_rank = np.sort(ranks)
sorted_torsion = np.sort(torsions)
sorted_cond = np.sort(log_conductors)

rho_f33_rank = stats.spearmanr(sorted_alpha, sorted_rank)[0]
rho_f33_torsion = stats.spearmanr(sorted_alpha, sorted_torsion)[0]
rho_f33_cond = stats.spearmanr(sorted_alpha, sorted_cond)[0]

print(f"  rho(sorted_alpha, sorted_rank)      = {rho_f33_rank:+.4f}")
print(f"  rho(sorted_alpha, sorted_torsion)    = {rho_f33_torsion:+.4f}")
print(f"  rho(sorted_alpha, sorted_conductor)  = {rho_f33_cond:+.4f}")
print("  (If raw rho ~ F33 rho, the signal is a sort artifact)")

# ── F34 check: trivial baseline ─────────────────────────────────────────────
print(f"\n{'='*60}")
print("F34 CHECK (trivial baseline: predict alpha from conductor only)")
print(f"{'='*60}")

# Regress alpha on log_conductor, check residual vs rank
from numpy.linalg import lstsq as np_lstsq
X_cond = np.column_stack([log_conductors, np.ones(len(log_conductors))])
beta, _, _, _ = np_lstsq(X_cond, alphas, rcond=None)
alpha_pred = X_cond @ beta
residuals = alphas - alpha_pred

r2_conductor = 1 - np.var(residuals) / np.var(alphas)
rho_resid_rank, p_resid_rank = stats.spearmanr(residuals, ranks)
rho_resid_torsion, p_resid_torsion = stats.spearmanr(residuals, torsions)

print(f"  R^2(alpha ~ log_conductor) = {r2_conductor:.4f}")
print(f"  rho(residual, rank)     = {rho_resid_rank:+.4f}  (p = {p_resid_rank:.2e})")
print(f"  rho(residual, torsion)  = {rho_resid_torsion:+.4f}  (p = {p_resid_torsion:.2e})")

# ── Bonus: Is alpha a genuine new invariant? ────────────────────────────────
print(f"\n{'='*60}")
print("BONUS: IS ALPHA A NEW INVARIANT?")
print(f"{'='*60}")

# Discreteness check
unique_alphas = len(np.unique(np.round(alphas, 4)))
print(f"  Unique alpha values (4 dp): {unique_alphas} / {len(alphas)}  -> {'continuous' if unique_alphas > len(alphas) * 0.5 else 'quasi-discrete'}")

# Does alpha distinguish curves with same conductor AND rank?
print("\n  Distinguishing power within (conductor, rank) groups:")
from collections import defaultdict
groups = defaultdict(list)
for rec in records:
    groups[(rec["conductor"], rec["rank"])].append(rec["alpha"])

multi_groups = {k: v for k, v in groups.items() if len(v) >= 2}
n_groups = len(multi_groups)
n_distinguished = 0
for k, alphas_g in multi_groups.items():
    if len(set(np.round(alphas_g, 4))) > 1:
        n_distinguished += 1

print(f"  Groups with same (cond, rank) and >=2 curves: {n_groups}")
print(f"  Groups where alpha distinguishes members: {n_distinguished} ({100*n_distinguished/max(n_groups,1):.1f}%)")

# Variance within vs between groups
within_vars = []
group_means = []
for k, alphas_g in multi_groups.items():
    if len(alphas_g) >= 2:
        within_vars.append(np.var(alphas_g))
        group_means.append(np.mean(alphas_g))

if within_vars:
    mean_within = np.mean(within_vars)
    between_var = np.var(group_means)
    eta_sq = between_var / (between_var + mean_within) if (between_var + mean_within) > 0 else 0
    print(f"  Mean within-group variance: {mean_within:.6f}")
    print(f"  Between-group variance:     {between_var:.6f}")
    print(f"  Eta-squared (group effect):  {eta_sq:.4f}")
    print(f"  -> {'STRONG' if eta_sq > 0.5 else 'WEAK' if eta_sq > 0.1 else 'NEGLIGIBLE'} group structure")

# ── Verdict ─────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("VERDICT")
print(f"{'='*60}")

killed = True
kill_reasons = []

if abs(rho_conductor) > 0.3 and r2_conductor > 0.1:
    kill_reasons.append(f"alpha strongly correlated with conductor (rho={rho_conductor:+.4f}, R2={r2_conductor:.4f})")

if abs(rho_ar_c) < 0.05 or p_perm_partial > 0.05:
    kill_reasons.append(f"partial rho(alpha, rank | conductor) negligible ({rho_ar_c:+.4f}, p_perm={p_perm_partial:.4f})")
else:
    killed = False

if abs(rho_resid_rank) < 0.05 or p_resid_rank > 0.05:
    kill_reasons.append(f"F34 residual vs rank negligible ({rho_resid_rank:+.4f}, p={p_resid_rank:.2e})")
else:
    killed = False

if len(kill_reasons) == 0:
    killed = False

if killed:
    print("  STATUS: KILLED")
    for reason in kill_reasons:
        print(f"    - {reason}")
else:
    print("  STATUS: SURVIVES (pending further validation)")
    if abs(rho_ar_c) >= 0.05 and p_perm_partial <= 0.05:
        print(f"    + Partial correlation rho(alpha, rank | conductor) = {rho_ar_c:+.4f} is significant")
    if abs(rho_resid_rank) >= 0.05 and p_resid_rank <= 0.05:
        print(f"    + F34 residual vs rank = {rho_resid_rank:+.4f} is significant")

# ── Save results ────────────────────────────────────────────────────────────
results = {
    "metadata": {
        "script": "satotate_convergence.py",
        "n_curves": len(records),
        "n_primes_per_curve": 25,
        "k_values": K_VALUES,
        "n_permutations": N_PERMUTATIONS,
        "candidate": "F39",
    },
    "distribution": {
        "mean": float(np.mean(alphas)),
        "median": float(np.median(alphas)),
        "std": float(np.std(alphas)),
        "min": float(np.min(alphas)),
        "max": float(np.max(alphas)),
        "q25": float(np.percentile(alphas, 25)),
        "q75": float(np.percentile(alphas, 75)),
        "n_unique_4dp": int(unique_alphas),
        "discreteness": "continuous" if unique_alphas > len(alphas) * 0.5 else "quasi-discrete",
    },
    "raw_correlations": {
        "alpha_rank": {"rho": float(rho_rank), "p": float(p_rank)},
        "alpha_torsion": {"rho": float(rho_torsion), "p": float(p_torsion)},
        "alpha_log_conductor": {"rho": float(rho_conductor), "p": float(p_conductor)},
    },
    "partial_correlations": {
        "alpha_rank_given_conductor": {"rho": float(rho_ar_c), "p": float(p_ar_c)},
        "alpha_torsion_given_conductor_rank": {"rho": float(rho_at_cr), "p": float(p_at_cr)},
    },
    "permutation_null": {
        "alpha_rank": {"obs": float(rho_rank), "null_std": float(perm_rho_rank.std()), "p_perm": float(p_perm_rank)},
        "alpha_conductor": {"obs": float(rho_conductor), "null_std": float(perm_rho_conductor.std()), "p_perm": float(p_perm_conductor)},
        "alpha_rank_partial": {"obs": float(rho_ar_c), "null_std": float(perm_partial_rank.std()), "p_perm": float(p_perm_partial)},
    },
    "f33_check": {
        "sorted_alpha_vs_sorted_rank": float(rho_f33_rank),
        "sorted_alpha_vs_sorted_conductor": float(rho_f33_cond),
    },
    "f34_check": {
        "r2_conductor_only": float(r2_conductor),
        "residual_vs_rank": {"rho": float(rho_resid_rank), "p": float(p_resid_rank)},
        "residual_vs_torsion": {"rho": float(rho_resid_torsion), "p": float(p_resid_torsion)},
    },
    "invariant_quality": {
        "n_multi_groups": int(n_groups),
        "n_distinguished": int(n_distinguished),
        "pct_distinguished": float(100 * n_distinguished / max(n_groups, 1)),
        "eta_squared": float(eta_sq) if within_vars else None,
    },
    "verdict": {
        "killed": killed,
        "reasons": kill_reasons,
    },
}

with open(OUT_FILE, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {OUT_FILE}")

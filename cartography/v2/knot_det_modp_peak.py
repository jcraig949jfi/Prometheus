"""
Knot Determinant Mod-p Failure Mode — Prime-Sweep KL Peak (DeepSeek #14)

Question: Is there a specific prime where knot determinants mod p deviate
maximally from uniform?

Method:
  - For each prime p in {3,5,7,...,47}, compute det mod p distribution
  - KL divergence from uniform on {0,...,p-1}
  - Chi-squared test vs uniform
  - Bootstrap CI on the peak KL
  - Compare to random integers of same magnitude distribution
"""

import json
import numpy as np
from pathlib import Path
from scipy import stats as sp_stats

# ── Load data ──────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent.parent / "knots" / "data" / "knots.json"
OUT_PATH = Path(__file__).parent / "knot_det_modp_peak_results.json"

with open(DATA_PATH) as f:
    raw = json.load(f)

determinants = np.array([k["determinant"] for k in raw["knots"] if k["determinant"] is not None])
n_knots = len(determinants)
print(f"Loaded {n_knots} knot determinants")
print(f"  range: [{determinants.min()}, {determinants.max()}], median={np.median(determinants):.0f}")

# ── Primes to sweep ───────────────────────────────────────────────────
PRIMES = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

# ── KL divergence (with smoothing to avoid log(0)) ───────────────────
def kl_from_uniform(counts, p):
    """KL(observed || uniform) with add-1 smoothing."""
    smoothed = (counts + 1) / (counts.sum() + p)
    uniform = np.ones(p) / p
    return float(np.sum(smoothed * np.log(smoothed / uniform)))

def chi2_vs_uniform(counts, p):
    """Chi-squared test vs uniform."""
    expected = np.ones(p) * counts.sum() / p
    chi2 = float(np.sum((counts - expected)**2 / expected))
    dof = p - 1
    pval = float(1.0 - sp_stats.chi2.cdf(chi2, dof))
    return chi2, dof, pval

# ── Main sweep ────────────────────────────────────────────────────────
results_per_prime = []

for p in PRIMES:
    residues = determinants % p
    counts = np.bincount(residues, minlength=p).astype(float)

    kl = kl_from_uniform(counts, p)
    chi2, dof, pval = chi2_vs_uniform(counts, p)

    # Fraction that are zero mod p
    frac_zero = float(counts[0] / counts.sum())
    expected_frac_zero = 1.0 / p

    results_per_prime.append({
        "prime": int(p),
        "kl_divergence": round(kl, 6),
        "chi2": round(chi2, 2),
        "chi2_dof": dof,
        "chi2_pval": float(f"{pval:.6e}"),
        "frac_zero": round(frac_zero, 6),
        "expected_frac_zero": round(expected_frac_zero, 6),
        "counts": [int(c) for c in counts],
    })

    sig = "***" if pval < 0.001 else ("**" if pval < 0.01 else ("*" if pval < 0.05 else ""))
    print(f"  p={p:2d}  KL={kl:.6f}  chi2={chi2:8.2f} (dof={dof:2d})  pval={pval:.4e}  frac0={frac_zero:.4f} (exp={expected_frac_zero:.4f}) {sig}")

# ── Find peak ─────────────────────────────────────────────────────────
kl_values = [r["kl_divergence"] for r in results_per_prime]
peak_idx = int(np.argmax(kl_values))
peak_prime = results_per_prime[peak_idx]["prime"]
peak_kl = results_per_prime[peak_idx]["kl_divergence"]

print(f"\nPeak KL: p={peak_prime}, KL={peak_kl:.6f}")

# ── Bootstrap CI on peak KL ───────────────────────────────────────────
N_BOOT = 10000
rng = np.random.default_rng(42)

# Bootstrap the KL at the peak prime
boot_kls = np.zeros(N_BOOT)
for i in range(N_BOOT):
    idx = rng.integers(0, n_knots, size=n_knots)
    boot_residues = determinants[idx] % peak_prime
    boot_counts = np.bincount(boot_residues, minlength=peak_prime).astype(float)
    boot_kls[i] = kl_from_uniform(boot_counts, peak_prime)

ci_lo, ci_hi = float(np.percentile(boot_kls, 2.5)), float(np.percentile(boot_kls, 97.5))
print(f"Bootstrap 95% CI on KL(p={peak_prime}): [{ci_lo:.6f}, {ci_hi:.6f}]")

# ── Bootstrap CI for ALL primes ───────────────────────────────────────
boot_ci_all = {}
for p in PRIMES:
    bk = np.zeros(N_BOOT)
    for i in range(N_BOOT):
        idx = rng.integers(0, n_knots, size=n_knots)
        br = determinants[idx] % p
        bc = np.bincount(br, minlength=p).astype(float)
        bk[i] = kl_from_uniform(bc, p)
    boot_ci_all[p] = {
        "ci_lo": round(float(np.percentile(bk, 2.5)), 6),
        "ci_hi": round(float(np.percentile(bk, 97.5)), 6),
        "mean": round(float(np.mean(bk)), 6),
    }

# ── Random baseline: integers drawn from same magnitude distribution ──
print("\nRandom baseline (same magnitude distribution):")

# Match the empirical distribution of log-magnitudes
log_dets = np.log10(determinants.astype(float) + 1)
random_dets = np.round(10**rng.choice(log_dets, size=n_knots)).astype(int)
random_dets = np.abs(random_dets)  # ensure positive

random_results = []
for p in PRIMES:
    residues = random_dets % p
    counts = np.bincount(residues, minlength=p).astype(float)
    kl = kl_from_uniform(counts, p)
    chi2, dof, pval = chi2_vs_uniform(counts, p)
    random_results.append({
        "prime": int(p),
        "kl_divergence": round(kl, 6),
        "chi2": round(chi2, 2),
        "chi2_pval": float(f"{pval:.6e}"),
    })
    print(f"  p={p:2d}  KL={kl:.6f}  chi2={chi2:8.2f}  pval={pval:.4e}")

# ── Multiple-random-draw baseline for peak KL ────────────────────────
N_RANDOM_TRIALS = 1000
random_peak_kls = np.zeros(N_RANDOM_TRIALS)
for t in range(N_RANDOM_TRIALS):
    rd = np.round(10**rng.choice(log_dets, size=n_knots)).astype(int)
    rd = np.abs(rd)
    trial_kls = []
    for p in PRIMES:
        res = rd % p
        cnt = np.bincount(res, minlength=p).astype(float)
        trial_kls.append(kl_from_uniform(cnt, p))
    random_peak_kls[t] = max(trial_kls)

random_peak_mean = float(np.mean(random_peak_kls))
random_peak_95 = float(np.percentile(random_peak_kls, 95))
random_peak_99 = float(np.percentile(random_peak_kls, 99))

print(f"\nRandom peak KL over {N_RANDOM_TRIALS} trials:")
print(f"  mean={random_peak_mean:.6f}, 95th={random_peak_95:.6f}, 99th={random_peak_99:.6f}")
print(f"  Observed peak KL={peak_kl:.6f}")

if peak_kl > random_peak_99:
    print(f"  -> Observed peak EXCEEDS 99th percentile of random")
elif peak_kl > random_peak_95:
    print(f"  -> Observed peak exceeds 95th percentile of random")
else:
    print(f"  -> Observed peak within random expectation")

# ── Also check: are knot determinants always odd? ─────────────────────
n_even = int(np.sum(determinants % 2 == 0))
n_odd = int(np.sum(determinants % 2 == 1))
print(f"\nParity check: {n_even} even, {n_odd} odd out of {n_knots}")
if n_even == 0:
    print("  All determinants are ODD — this is a known theorem (det is always odd for knots)")

# ── Assemble output ──────────────────────────────────────────────────
# For the per-prime results, attach bootstrap CIs
for r in results_per_prime:
    p = r["prime"]
    if p in boot_ci_all:
        r["boot_kl_ci95_lo"] = boot_ci_all[p]["ci_lo"]
        r["boot_kl_ci95_hi"] = boot_ci_all[p]["ci_hi"]
        r["boot_kl_mean"] = boot_ci_all[p]["mean"]

output = {
    "title": "Knot Determinant Mod-p Failure Mode — Prime-Sweep KL Peak",
    "tag": "DeepSeek #14",
    "n_knots": n_knots,
    "determinant_range": [int(determinants.min()), int(determinants.max())],
    "determinant_median": float(np.median(determinants)),
    "all_odd": bool(n_even == 0),
    "primes_tested": PRIMES,
    "per_prime": results_per_prime,
    "peak": {
        "prime": peak_prime,
        "kl_divergence": peak_kl,
        "bootstrap_95ci": [round(ci_lo, 6), round(ci_hi, 6)],
    },
    "random_baseline": {
        "method": "resample from 10^(log10(det+1)) magnitude distribution",
        "per_prime": random_results,
        "peak_kl_distribution": {
            "n_trials": N_RANDOM_TRIALS,
            "mean": round(random_peak_mean, 6),
            "p95": round(random_peak_95, 6),
            "p99": round(random_peak_99, 6),
        },
        "observed_exceeds_p99": bool(peak_kl > random_peak_99),
        "observed_exceeds_p95": bool(peak_kl > random_peak_95),
    },
    "verdict": "",  # filled below
}

# Verdict
if peak_kl > random_peak_99:
    output["verdict"] = (
        f"Peak KL at p={peak_prime} ({peak_kl:.6f}) exceeds 99th percentile of random "
        f"({random_peak_99:.6f}). Statistically significant deviation from uniform — "
        f"knot determinants have non-trivial mod-{peak_prime} structure."
    )
elif peak_kl > random_peak_95:
    output["verdict"] = (
        f"Peak KL at p={peak_prime} ({peak_kl:.6f}) exceeds 95th percentile of random "
        f"({random_peak_95:.6f}). Marginal deviation — warrants further investigation."
    )
else:
    output["verdict"] = (
        f"Peak KL at p={peak_prime} ({peak_kl:.6f}) within random expectation "
        f"(99th pctl={random_peak_99:.6f}). Globally null: no prime shows meaningful "
        f"deviation from uniform. Knot determinants mod p are boring."
    )

with open(OUT_PATH, "w") as f:
    json.dump(output, f, indent=2)

print(f"\nVerdict: {output['verdict']}")
print(f"Saved to {OUT_PATH}")

"""C43/S3: Prime gap M4/M^2 scaling +0.23/decade.
Prior: M4/M^2=4.60 at 10^6, monotonic toward Poisson. Extend to 10^8.
Machine: M1 (Skullport), 2026-04-12
"""
import sys
import numpy as np
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parent))
from battery_v2 import BatteryV2

DATA = Path(__file__).resolve().parent.parent.parent
bv2 = BatteryV2()

from sympy import primerange

print("Computing prime gap M4/M^2 at multiple scales...")
print("="*70)

results_by_scale = {}

# Test at scales from 10^3 to 10^8
# 10^8 has ~5.7M primes, should be fine on 32GB
for exp in range(3, 9):
    limit = 10**exp
    print(f"\nScale 10^{exp} (limit={limit:,})...")

    primes = np.array(list(primerange(2, limit)), dtype=np.int64)
    n_primes = len(primes)
    gaps = np.diff(primes).astype(float)

    if len(gaps) < 30:
        print(f"  Only {len(gaps)} gaps, skipping")
        continue

    # M4/M^2
    normed = gaps / np.mean(gaps)
    m2 = np.mean(normed**2)
    m4 = np.mean(normed**4)
    m4m2 = m4 / (m2**2)

    # Also compute M6/M2^3 for comparison
    m6 = np.mean(normed**6)
    m6m2 = m6 / (m2**3)

    mean_gap = np.mean(gaps)
    std_gap = np.std(gaps)

    results_by_scale[exp] = {
        "exponent": exp,
        "limit": limit,
        "n_primes": n_primes,
        "n_gaps": len(gaps),
        "mean_gap": float(mean_gap),
        "std_gap": float(std_gap),
        "m4m2": float(m4m2),
        "m6m2": float(m6m2),
    }

    print(f"  n_primes={n_primes:,}, mean_gap={mean_gap:.3f}, M4/M2={m4m2:.4f}, M6/M2^3={m6m2:.4f}")

# --- Test 1: Scaling rate ---
print("\n" + "="*70)
print("TEST 1: M4/M^2 scaling with log10(N)")
print("="*70)
from scipy import stats as sp_stats

exps = np.array([r["exponent"] for r in results_by_scale.values()], dtype=float)
m4m2s = np.array([r["m4m2"] for r in results_by_scale.values()])

slope, intercept, r_val, p_val, se = sp_stats.linregress(exps, m4m2s)
print(f"Linear fit: M4/M2 = {slope:.4f} * log10(N) + {intercept:.4f}")
print(f"R2 = {r_val**2:.4f}, p = {p_val:.2e}")
print(f"Slope = {slope:.4f} per decade (prior claim: +0.23)")

# --- Test 2: Convergence toward Poisson ---
print("\n" + "="*70)
print("TEST 2: Convergence toward Poisson (M4/M^2 = 9)")
print("="*70)
print("Reference: Exponential/Poisson M4/M^2 = 9.0")
print("Reference: Gaussian M4/M^2 = 3.0")
for r in results_by_scale.values():
    pct_to_poisson = (r["m4m2"] - 3.0) / (9.0 - 3.0) * 100
    print(f"  10^{r['exponent']}: M4/M2={r['m4m2']:.4f} ({pct_to_poisson:.1f}% of way from Gaussian to Poisson)")

# --- Test 3: M6/M2^3 scaling (higher moment check) ---
print("\n" + "="*70)
print("TEST 3: M6/M2^3 scaling (Catalan comparison)")
print("="*70)
print("Reference: Exponential M6/M2^3 = 225, Gaussian M6/M2^3 = 15")
m6m2s = np.array([r["m6m2"] for r in results_by_scale.values()])
slope6, intercept6, r6, p6, se6 = sp_stats.linregress(exps, np.log(m6m2s))
print(f"Log-linear fit: log(M6/M2^3) = {slope6:.4f} * log10(N) + {intercept6:.4f}")
for r in results_by_scale.values():
    print(f"  10^{r['exponent']}: M6/M2^3={r['m6m2']:.4f}")

# --- Test 4: F24 — gaps grouped by decade of prime ---
print("\n" + "="*70)
print("TEST 4: F24 — gap size by decade of prime (largest scale)")
print("="*70)
largest_exp = max(results_by_scale.keys())
limit = 10**largest_exp
primes = np.array(list(primerange(2, limit)), dtype=np.int64)
gaps = np.diff(primes).astype(float)
# Group by decade of the prime
decade_labels = np.array([str(int(np.floor(np.log10(max(p, 2))))) for p in primes[:-1]])
v4, r4 = bv2.F24_variance_decomposition(gaps, decade_labels)
print(f"Verdict: {v4}, eta2 = {r4.get('eta_squared', 0):.4f}")

# --- Classification ---
print("\n" + "="*70)
print("CLASSIFICATION")
print("="*70)
print(f"Scaling slope: {slope:.4f}/decade (prior: +0.23)")
print(f"At 10^8: M4/M2 = {results_by_scale.get(8, {}).get('m4m2', 'N/A')}")
print(f"Decade grouping eta2: {r4.get('eta_squared', 0):.4f}")

if abs(slope - 0.23) < 0.05:
    print(f"\n-> Prior claim CONFIRMED: slope = {slope:.3f} ~ 0.23/decade")
else:
    print(f"\n-> Prior claim MODIFIED: slope = {slope:.3f} (was 0.23)")

if r4.get("eta_squared", 0) >= 0.14:
    classification = "LAW"
elif r4.get("eta_squared", 0) >= 0.01:
    classification = "TENDENCY"
else:
    classification = "NEGLIGIBLE"
print(f"-> CLASSIFICATION: {classification}")

final_results = {
    "test": "C43/S3",
    "claim": "Prime gap M4/M^2 scales +0.23/decade toward Poisson",
    "scaling_slope": float(slope),
    "scaling_r2": float(r_val**2),
    "decade_eta2": r4.get("eta_squared", 0),
    "classification": classification,
    "by_scale": results_by_scale,
}
with open(DATA / "shared/scripts/v2/c43_prime_gap_scaling_results.json", "w") as f:
    json.dump(final_results, f, indent=2, default=str)
print(f"\nResults saved to v2/c43_prime_gap_scaling_results.json")

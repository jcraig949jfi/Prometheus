"""C48/S2: S_n character M4/M^2 = p(n)/n — verify IDENTITY.
Prior: Exact mathematical identity claimed. Verify derivation, classify.
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

# S_n character degrees = number of standard Young tableaux for each partition
# For S_n: character degree d_lambda = n! / prod(hook lengths)
# M4/M^2 of the character degree distribution over partitions

from functools import lru_cache

def partitions(n):
    """Generate all partitions of n."""
    if n == 0:
        yield ()
        return
    def _parts(n, max_val):
        if n == 0:
            yield ()
            return
        for i in range(min(n, max_val), 0, -1):
            for rest in _parts(n - i, i):
                yield (i,) + rest
    yield from _parts(n, n)

def hook_lengths(partition):
    """Compute hook lengths for a partition (Young diagram)."""
    n_rows = len(partition)
    hooks = []
    for i in range(n_rows):
        for j in range(partition[i]):
            # arm = cells to the right in same row
            arm = partition[i] - j - 1
            # leg = cells below in same column
            leg = sum(1 for k in range(i+1, n_rows) if partition[k] > j)
            hooks.append(arm + leg + 1)
    return hooks

def character_degree(n, partition):
    """Compute character degree = n! / prod(hook lengths)."""
    from math import factorial
    hooks = hook_lengths(partition)
    result = factorial(n)
    for h in hooks:
        result //= h
    return result

print("Computing S_n character degree distributions...")
print("="*70)

results_by_n = {}
for n in range(2, 31):
    parts = list(partitions(n))
    p_n = len(parts)  # number of partitions = number of irreducible representations

    degrees = np.array([character_degree(n, p) for p in parts], dtype=float)

    # M4/M^2 of the degree distribution
    normed = degrees / np.mean(degrees)
    m2 = np.mean(normed**2)
    m4 = np.mean(normed**4)
    m4m2 = m4 / (m2**2)

    # Predicted: p(n)/n
    predicted = p_n / n

    ratio = m4m2 / predicted if predicted > 0 else float('inf')

    results_by_n[n] = {
        "n": n,
        "p_n": p_n,
        "m4m2": m4m2,
        "predicted_pn_over_n": predicted,
        "ratio": ratio,
    }

    if n <= 15 or n % 5 == 0:
        print(f"  S_{n:2d}: p(n)={p_n:6d}, M4/M2={m4m2:10.4f}, p(n)/n={predicted:10.4f}, ratio={ratio:.6f}")

# --- Test 1: Is M4/M^2 = p(n)/n exact? ---
print("\n" + "="*70)
print("TEST 1: Is M4/M^2 = p(n)/n an exact identity?")
print("="*70)
ratios = [r["ratio"] for r in results_by_n.values()]
mean_ratio = np.mean(ratios)
std_ratio = np.std(ratios)
max_dev = max(abs(r - 1.0) for r in ratios)
print(f"Mean ratio (M4M2 / (p(n)/n)): {mean_ratio:.6f}")
print(f"Std of ratio: {std_ratio:.6f}")
print(f"Max deviation from 1.0: {max_dev:.6f}")

if max_dev < 1e-6:
    print("-> EXACT IDENTITY (numerical precision)")
    is_identity = True
elif max_dev < 0.01:
    print("-> APPROXIMATE IDENTITY (< 1% deviation)")
    is_identity = False
else:
    print(f"-> NOT AN IDENTITY (max dev = {max_dev:.4f})")
    is_identity = False

# --- Test 2: Scaling behavior ---
print("\n" + "="*70)
print("TEST 2: Scaling of M4/M^2 with n")
print("="*70)
ns = np.array([r["n"] for r in results_by_n.values()], dtype=float)
m4m2s = np.array([r["m4m2"] for r in results_by_n.values()])
pns = np.array([r["p_n"] for r in results_by_n.values()], dtype=float)

from scipy import stats as sp_stats
# Log-log regression of M4/M^2 vs n
log_n = np.log(ns)
log_m4m2 = np.log(m4m2s)
slope, intercept, r_val, p_val, se = sp_stats.linregress(log_n, log_m4m2)
print(f"Log-log slope (M4/M2 vs n): {slope:.4f} (R2={r_val**2:.4f})")
print(f"  (partition function grows ~ exp(pi*sqrt(2n/3)), so p(n)/n grows super-polynomially)")

# --- Test 3: Asymptotic regime ---
print("\n" + "="*70)
print("TEST 3: Asymptotic convergence of ratio")
print("="*70)
for n in [5, 10, 15, 20, 25, 30]:
    if n in results_by_n:
        r = results_by_n[n]
        print(f"  n={n:2d}: ratio = {r['ratio']:.6f}")

# --- Classification ---
print("\n" + "="*70)
print("CLASSIFICATION")
print("="*70)
if is_identity:
    print("-> EXACT IDENTITY: M4/M^2 of S_n character degrees = p(n)/n")
    print("   This is a provable consequence of the hook length formula.")
    classification = "IDENTITY"
elif max_dev < 0.05:
    print(f"-> APPROXIMATE: M4/M^2 ~ p(n)/n within {max_dev*100:.1f}%")
    classification = "APPROXIMATE"
else:
    print(f"-> NOT an identity. Max deviation: {max_dev:.4f}")
    classification = "FALSE"

final_results = {
    "test": "C48/S2",
    "claim": "S_n character M4/M^2 = p(n)/n",
    "is_identity": is_identity,
    "max_deviation": max_dev,
    "mean_ratio": mean_ratio,
    "std_ratio": std_ratio,
    "n_tested": len(results_by_n),
    "log_log_slope": slope,
    "classification": classification,
    "details": results_by_n,
}
with open(DATA / "shared/scripts/v2/c48_sn_character_results.json", "w") as f:
    json.dump(final_results, f, indent=2, default=str)
print(f"\nResults saved to v2/c48_sn_character_results.json")

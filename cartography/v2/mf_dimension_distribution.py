"""
Modular Form Dimension Distribution Analysis
=============================================
How does dim(S_2^new(Gamma_0(N))) grow with level N?
Compare empirical growth to the asymptotic formula dim ~ N/12.
Analyze residuals by arithmetic properties of N.
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict
from math import gcd
import duckdb

# ── Load data ────────────────────────────────────────────────────────────
DB_PATH = Path(__file__).parent.parent.parent / "charon" / "data" / "charon.duckdb"
con = duckdb.connect(str(DB_PATH), read_only=True)

# Weight-2 newforms with trivial character (char_order=1) = S_2^new(Gamma_0(N))
rows = con.execute("""
    SELECT level, SUM(dim) as total_dim, COUNT(*) as num_orbits
    FROM modular_forms
    WHERE weight = 2 AND char_order = 1
    GROUP BY level
    ORDER BY level
""").fetchall()
con.close()

levels = np.array([r[0] for r in rows])
dims = np.array([r[1] for r in rows])
num_orbits = np.array([r[2] for r in rows])

print(f"Loaded {len(levels)} distinct levels, range [{levels.min()}, {levels.max()}]")
print(f"Total newform orbits: {num_orbits.sum()}, total dimension: {dims.sum()}")

# ── Arithmetic helper functions ──────────────────────────────────────────
def factorize(n):
    """Return dict of prime: exponent."""
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    d = 5
    while d * d <= n:
        if n % d == 0 or n % (d + 2) == 0: return False
        d += 6
    return True

def is_squarefree(n):
    return all(e == 1 for e in factorize(n).values())

def num_prime_factors(n):
    return len(factorize(n))

def euler_phi(n):
    result = n
    for p in factorize(n):
        result = result * (p - 1) // p
    return result

# ── Theoretical dimension formula for Gamma_0(N) ────────────────────────
# dim S_2(Gamma_0(N)) = genus of X_0(N)
# genus = 1 + mu/12 - nu2/4 - nu3/3 - c_inf/2
# where mu = N * prod_{p|N}(1 + 1/p)  [index of Gamma_0(N) in SL_2(Z)]
# nu2 = number of elliptic points of order 2
# nu3 = number of elliptic points of order 3
# c_inf = number of cusps
# Note: this gives dim of FULL space, not new part.

def mu_index(N):
    """Index [SL_2(Z) : Gamma_0(N)]."""
    result = N
    for p in factorize(N):
        result = result * (p + 1) // p
    return result

def nu2_elliptic(N):
    """Number of elliptic points of order 2."""
    factors = factorize(N)
    for p, e in factors.items():
        if e >= 2 and p == 2:
            return 0
        if e >= 2 and p != 2:
            # if p^2 | N and (-1/p) = -1, contributes 0
            pass
    # Product formula: nu2 = prod_{p^e || N} (1 + (-1/p)) if e=1, 0 if e>=2 and p=2, etc.
    # Simpler: nu2 = 0 if 4|N, else prod_{p|N} (1 + legendre(-1,p))
    if N % 4 == 0:
        return 0
    result = 1
    for p, e in factors.items():
        if e >= 2:
            return 0
        # Legendre symbol (-1/p)
        if p == 2:
            result *= 1  # (-1/2) = ... actually for p=2, need special handling
            # For Gamma_0(N), if 2||N: nu2 factor for p=2 is 0 when p=2 actually
            # (-1 mod 2) doesn't make sense as Legendre. Use Kronecker.
            # kronecker(-4, p): (-4/2) = 0
            return 0 if 2 in factors else result
        leg = pow(-1 % p, (p - 1) // 2, p)
        if leg == p - 1:
            leg = -1
        result *= (1 + leg)
    return result

def nu3_elliptic(N):
    """Number of elliptic points of order 3."""
    if N % 9 == 0:
        return 0
    factors = factorize(N)
    for p, e in factors.items():
        if e >= 2 and p == 3:
            return 0
        if e >= 2:
            return 0
    # For squarefree N not divisible by 9:
    # nu3 = prod_{p|N} (1 + legendre(-3, p))
    result = 1
    for p, e in factors.items():
        if e >= 2:
            return 0
        if p == 3:
            return 0  # (-3/3) = 0
        leg = pow((-3) % p, (p - 1) // 2, p)
        if leg == p - 1:
            leg = -1
        result *= (1 + leg)
    return result

def num_cusps(N):
    """Number of cusps of Gamma_0(N)."""
    factors = factorize(N)
    result = 0
    # cusps = sum_{d|N} phi(gcd(d, N/d))
    divisors = [1]
    for p, e in factors.items():
        new_divs = []
        for d in divisors:
            pe = 1
            for i in range(e + 1):
                new_divs.append(d * pe)
                pe *= p
        divisors = new_divs
    for d in divisors:
        result += euler_phi(gcd(d, N // d))
    return result

def genus_X0(N):
    """Genus of X_0(N) = dim S_2(Gamma_0(N))."""
    mu = mu_index(N)
    n2 = nu2_elliptic(N)
    n3 = nu3_elliptic(N)
    cinf = num_cusps(N)
    return 1 + mu // 12 - n2 // 4 - n3 // 3 - cinf // 2

# Note: genus formula gives dim of full space S_2(Gamma_0(N)).
# The new part dim is: dim_new(N) = dim_full(N) - sum_{M|N, M<N} dim_new(M)
# This is the Mobius-type relation. We compute it iteratively.

def compute_dim_new_all(max_level):
    """Compute dim S_2^new(Gamma_0(N)) for all N up to max_level."""
    dim_full = {}
    dim_new = {}
    for N in range(1, max_level + 1):
        g = genus_X0(N)
        dim_full[N] = max(g, 0)

    for N in range(1, max_level + 1):
        # dim_new(N) = dim_full(N) - sum_{d|N, d<N} dim_new(d)
        old_sum = 0
        d = 1
        while d * d <= N:
            if N % d == 0:
                if d < N:
                    old_sum += dim_new.get(d, 0)
                if d != N // d and N // d < N:
                    old_sum += dim_new.get(N // d, 0)
            d += 1
        dim_new[N] = dim_full[N] - old_sum
    return dim_new

print("Computing theoretical dimensions...")
max_level = int(levels.max())
theoretical_new = compute_dim_new_all(max_level)

# ── Classify levels by arithmetic properties ─────────────────────────────
prime_mask = np.array([is_prime(int(N)) for N in levels])
sqfree_mask = np.array([is_squarefree(int(N)) for N in levels])
omega = np.array([num_prime_factors(int(N)) for N in levels])  # number of distinct prime factors

print(f"Prime levels: {prime_mask.sum()}, Composite levels: {(~prime_mask).sum()}")
print(f"Squarefree levels: {sqfree_mask.sum()}, Non-squarefree: {(~sqfree_mask).sum()}")

# ── Growth rate analysis ─────────────────────────────────────────────────
# Fit dim = a * N + b
from numpy.polynomial import polynomial as P
coeffs_linear = np.polyfit(levels, dims, 1)
slope, intercept = coeffs_linear
print(f"\nLinear fit: dim = {slope:.6f} * N + ({intercept:.4f})")
print(f"Theoretical leading coefficient: 1/12 = {1/12:.6f}")
print(f"Ratio empirical/theoretical: {slope / (1/12):.4f}")

# Ratio dim/N for large N
large_mask = levels >= 1000
if large_mask.sum() > 0:
    ratio_large = dims[large_mask] / levels[large_mask]
    print(f"\nFor N >= 1000: mean(dim/N) = {ratio_large.mean():.6f}, std = {ratio_large.std():.6f}")

# ── Residual analysis ────────────────────────────────────────────────────
predicted_N12 = levels / 12.0
residuals = dims - predicted_N12

# Residuals by primality
res_prime = residuals[prime_mask]
res_composite = residuals[~prime_mask]
print(f"\nResiduals (dim - N/12):")
print(f"  Prime levels:     mean = {res_prime.mean():.3f}, std = {res_prime.std():.3f}")
print(f"  Composite levels: mean = {res_composite.mean():.3f}, std = {res_composite.std():.3f}")

# Residuals by squarefree status
res_sqfree = residuals[sqfree_mask]
res_nonsqfree = residuals[~sqfree_mask]
print(f"  Squarefree:       mean = {res_sqfree.mean():.3f}, std = {res_sqfree.std():.3f}")
print(f"  Non-squarefree:   mean = {res_nonsqfree.mean():.3f}, std = {res_nonsqfree.std():.3f}")

# Normalized residuals: (dim - N/12) / (N/12)
norm_residuals = residuals / predicted_N12

# By number of prime factors
omega_groups = defaultdict(list)
for i, w in enumerate(omega):
    omega_groups[int(w)].append(float(norm_residuals[i]))

print(f"\nNormalized residuals (dim - N/12)/(N/12) by number of prime factors:")
for w in sorted(omega_groups.keys()):
    vals = omega_groups[w]
    print(f"  omega={w}: n={len(vals)}, mean={np.mean(vals):.4f}, std={np.std(vals):.4f}")

# ── Theoretical vs empirical comparison ──────────────────────────────────
theo_dims = np.array([theoretical_new.get(int(N), 0) for N in levels])
match = np.sum(dims == theo_dims)
close = np.sum(np.abs(dims - theo_dims) <= 1)
print(f"\nTheoretical vs empirical dim_new:")
print(f"  Exact match: {match}/{len(levels)} ({100*match/len(levels):.1f}%)")
print(f"  Within 1: {close}/{len(levels)} ({100*close/len(levels):.1f}%)")

# Where they disagree
disagree_mask = dims != theo_dims
if disagree_mask.sum() > 0:
    disagree_levels = levels[disagree_mask][:20]
    disagree_emp = dims[disagree_mask][:20]
    disagree_theo = theo_dims[disagree_mask][:20]
    print(f"  First disagreements (up to 20):")
    for l, e, t in zip(disagree_levels, disagree_emp, disagree_theo):
        print(f"    N={l}: empirical={e}, theoretical={t}, diff={e-t}")

# ── Prime concentration index ───────────────────────────────────────────
total_dim_prime = dims[prime_mask].sum()
total_dim_all = dims.sum()
prime_concentration = total_dim_prime / total_dim_all
# What fraction of levels <= max are prime?
prime_level_frac = prime_mask.sum() / len(levels)
print(f"\nPrime concentration index:")
print(f"  Fraction of total dimension at prime levels: {prime_concentration:.4f}")
print(f"  Fraction of levels that are prime: {prime_level_frac:.4f}")
print(f"  Enrichment ratio: {prime_concentration / prime_level_frac:.4f}")

# ── Over/under-represented levels ────────────────────────────────────────
# Ratio dim(N) / (N/12) -- deviation from expected
ratio = dims / (levels / 12.0)
top_over = np.argsort(-ratio)[:20]
top_under = np.argsort(ratio)[:20]

print("\nMost over-represented levels (highest dim/(N/12)):")
for i in top_over:
    print(f"  N={levels[i]}: dim={dims[i]}, N/12={levels[i]/12:.1f}, ratio={ratio[i]:.3f}, prime={is_prime(int(levels[i]))}")

print("\nMost under-represented levels (lowest dim/(N/12)):")
for i in top_under:
    print(f"  N={levels[i]}: dim={dims[i]}, N/12={levels[i]/12:.1f}, ratio={ratio[i]:.3f}, prime={is_prime(int(levels[i]))}")

# ── Correlation: residual vs arithmetic properties ───────────────────────
from scipy import stats

# Correlation with number of prime factors
corr_omega, p_omega = stats.pearsonr(omega, norm_residuals)
print(f"\nCorrelation of normalized residual with omega(N): r={corr_omega:.4f}, p={p_omega:.2e}")

# Correlation with is_prime
corr_prime, p_prime = stats.pearsonr(prime_mask.astype(float), norm_residuals)
print(f"Correlation with is_prime: r={corr_prime:.4f}, p={p_prime:.2e}")

# Correlation with is_squarefree
corr_sqfree, p_sqfree = stats.pearsonr(sqfree_mask.astype(float), norm_residuals)
print(f"Correlation with is_squarefree: r={corr_sqfree:.4f}, p={p_sqfree:.2e}")

# ── Assemble results ────────────────────────────────────────────────────
results = {
    "experiment": "mf_dimension_distribution",
    "description": "Growth of dim(S_2^new(Gamma_0(N))) with level N",
    "data_summary": {
        "num_levels": int(len(levels)),
        "level_range": [int(levels.min()), int(levels.max())],
        "total_dimension": int(dims.sum()),
        "total_orbits": int(num_orbits.sum()),
        "num_prime_levels": int(prime_mask.sum()),
        "num_composite_levels": int((~prime_mask).sum()),
        "num_squarefree_levels": int(sqfree_mask.sum()),
    },
    "growth_rate": {
        "linear_fit_slope": round(float(slope), 6),
        "linear_fit_intercept": round(float(intercept), 4),
        "theoretical_slope": round(1/12, 6),
        "ratio_empirical_to_theoretical": round(float(slope / (1/12)), 4),
        "mean_dim_over_N_large_N": round(float(ratio_large.mean()), 6) if large_mask.sum() > 0 else None,
        "std_dim_over_N_large_N": round(float(ratio_large.std()), 6) if large_mask.sum() > 0 else None,
    },
    "theoretical_comparison": {
        "exact_match_fraction": round(float(match / len(levels)), 4),
        "within_1_fraction": round(float(close / len(levels)), 4),
        "num_disagreements": int(disagree_mask.sum()) if disagree_mask.sum() > 0 else 0,
    },
    "residual_analysis": {
        "prime_levels_mean_residual": round(float(res_prime.mean()), 3),
        "prime_levels_std_residual": round(float(res_prime.std()), 3),
        "composite_levels_mean_residual": round(float(res_composite.mean()), 3),
        "composite_levels_std_residual": round(float(res_composite.std()), 3),
        "squarefree_mean_residual": round(float(res_sqfree.mean()), 3),
        "nonsquarefree_mean_residual": round(float(res_nonsqfree.mean()), 3),
        "normalized_residual_by_omega": {
            str(w): {"n": len(vals), "mean": round(float(np.mean(vals)), 4), "std": round(float(np.std(vals)), 4)}
            for w, vals in sorted(omega_groups.items())
        },
    },
    "correlations": {
        "norm_residual_vs_omega": {"r": round(float(corr_omega), 4), "p": float(f"{p_omega:.2e}")},
        "norm_residual_vs_is_prime": {"r": round(float(corr_prime), 4), "p": float(f"{p_prime:.2e}")},
        "norm_residual_vs_is_squarefree": {"r": round(float(corr_sqfree), 4), "p": float(f"{p_sqfree:.2e}")},
    },
    "prime_concentration": {
        "fraction_dim_at_prime_levels": round(float(prime_concentration), 4),
        "fraction_levels_that_are_prime": round(float(prime_level_frac), 4),
        "enrichment_ratio": round(float(prime_concentration / prime_level_frac), 4),
    },
    "over_represented_levels": [
        {"N": int(levels[i]), "dim": int(dims[i]), "ratio_to_N12": round(float(ratio[i]), 3),
         "is_prime": bool(is_prime(int(levels[i])))}
        for i in top_over
    ],
    "under_represented_levels": [
        {"N": int(levels[i]), "dim": int(dims[i]), "ratio_to_N12": round(float(ratio[i]), 3),
         "is_prime": bool(is_prime(int(levels[i])))}
        for i in top_under
    ],
}

OUT_PATH = Path(__file__).parent / "mf_dimension_distribution_results.json"
with open(OUT_PATH, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {OUT_PATH}")
print("Done.")

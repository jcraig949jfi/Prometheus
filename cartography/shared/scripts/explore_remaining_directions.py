#!/usr/bin/env python3
"""
Explore remaining directions the primitive COULD be in.

The 14 kills eliminated:
- Ordinal matching, magnitude, Benford, preprocessing, engineering,
  tautology, prime confounds, partial-correlation artifacts

What's left to explore (and try to kill):

1. COEFFICIENT-LEVEL structure: not summary statistics, but actual a_p sequences
   EC a_p and MF a_p are IDENTICAL (modularity). But what about EC a_p vs Maass coefficients?
   Do the coefficient SEQUENCES share structure beyond their distributions?

2. PRIME-INDEXED structure: values at specific primes, not aggregated
   EC a_p at p=2 vs a_p at p=3 vs a_p at p=5. Do different primes see different
   things about the same EC? This is the Euler product decomposition.

3. FACTORIZATION structure: not the VALUE of the conductor, but its FACTORIZATION
   Two conductors with the same prime factors but different exponents — do their
   L-functions look different? This is the local-to-global principle.

4. TORSION-CONDUCTOR joint structure: not separately, but the PAIR
   The BSD conjecture says torsion and conductor are related through the L-function.
   But how? Can we see it in the data without knowing the conjecture?

5. SYMMETRY TYPE in zero distributions: not just GUE vs Poisson,
   but SO(even) vs SO(odd) vs symplectic. Different symmetry types for
   different families — can we detect the family from the zeros alone?
"""
import sys, os, json
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy.stats import spearmanr, pearsonr

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[3]
DATA = Path(__file__).resolve().parent.parent.parent
rng = np.random.default_rng(42)

import duckdb

print("=" * 100)
print("EXPLORING REMAINING DIRECTIONS — what hasn't been killed yet?")
print("=" * 100)

# ============================================================
# 1. EC a_p SEQUENCE structure: position-specific correlations
# ============================================================
print("\n" + "=" * 100)
print("1. EC a_p SEQUENCE: do coefficients at different primes correlate?")
print("=" * 100)

con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
ec_ap = con.execute("""
    SELECT aplist, conductor, rank, torsion FROM elliptic_curves
    WHERE aplist IS NOT NULL AND rank IS NOT NULL
    LIMIT 5000
""").fetchall()
con.close()

primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
ap_matrix = []
ec_meta = []

for aplist_json, cond, rank, tors in ec_ap:
    try:
        aplist = json.loads(aplist_json) if isinstance(aplist_json, str) else aplist_json
        if isinstance(aplist, list) and len(aplist) >= len(primes):
            ap_matrix.append([aplist[i] for i in range(len(primes))])
            ec_meta.append({"cond": cond, "rank": rank, "tors": tors})
    except:
        pass

ap_matrix = np.array(ap_matrix, dtype=float)
print(f"  EC with {len(primes)}-prime a_p vectors: {len(ap_matrix)}")

if len(ap_matrix) > 100:
    # Cross-prime correlations
    print(f"\n  Cross-prime correlation matrix (a_p at prime i vs a_p at prime j):")
    print(f"  {'':>6s}", end="")
    for p in primes[:8]:
        print(f" {p:>6d}", end="")
    print()

    corr_matrix = np.corrcoef(ap_matrix.T)
    for i in range(min(8, len(primes))):
        print(f"  {primes[i]:>6d}", end="")
        for j in range(min(8, len(primes))):
            print(f" {corr_matrix[i,j]:6.3f}", end="")
        print()

    # Are cross-prime correlations zero? (Sato-Tate predicts independence)
    off_diag = []
    for i in range(len(primes)):
        for j in range(i+1, len(primes)):
            off_diag.append(abs(corr_matrix[i, j]))
    print(f"\n  Mean |off-diagonal correlation|: {np.mean(off_diag):.4f}")
    print(f"  Max |off-diagonal|: {np.max(off_diag):.4f}")
    print(f"  Expected (independent): ~{1/np.sqrt(len(ap_matrix)):.4f}")

    if np.mean(off_diag) > 3 / np.sqrt(len(ap_matrix)):
        print(f"  SIGNAL: Cross-prime correlations exceed independence threshold.")
        print(f"  This would mean a_p values are NOT independent across primes.")
    else:
        print(f"  Consistent with independence (Sato-Tate).")

    # Do cross-prime correlations predict rank?
    print(f"\n  Cross-prime products vs rank:")
    ranks = np.array([m["rank"] for m in ec_meta])
    for i, j in [(0, 1), (0, 2), (1, 2), (0, 4)]:  # (2,3), (2,5), (3,5), (2,11)
        product = ap_matrix[:, i] * ap_matrix[:, j]
        rho, p = spearmanr(product, ranks)
        print(f"    a_{primes[i]} * a_{primes[j]} vs rank: rho={rho:.4f}, p={p:.4e}")


# ============================================================
# 2. FACTORIZATION structure of conductors
# ============================================================
print("\n" + "=" * 100)
print("2. CONDUCTOR FACTORIZATION: do primes in the conductor predict a_p?")
print("=" * 100)

# For each EC, decompose conductor into prime factors
# Then test: does a_p at p dividing the conductor differ from a_p at p NOT dividing it?

good_p = []  # a_p where p does NOT divide conductor
bad_p = []   # a_p where p DOES divide conductor (bad reduction)

for i, meta in enumerate(ec_meta):
    cond = int(meta["cond"])
    for j, p in enumerate(primes):
        if cond % p == 0:
            bad_p.append(ap_matrix[i, j])
        else:
            good_p.append(ap_matrix[i, j])

print(f"  Good reduction a_p: {len(good_p)}")
print(f"  Bad reduction a_p: {len(bad_p)}")
print(f"  Good mean: {np.mean(good_p):.4f}, std: {np.std(good_p):.4f}")
print(f"  Bad mean: {np.mean(bad_p):.4f}, std: {np.std(bad_p):.4f}")

# At bad primes, a_p is constrained: a_p in {-1, 0, 1} for multiplicative reduction
bad_dist = Counter(int(round(a)) for a in bad_p if abs(a) < 2)
print(f"  Bad reduction a_p distribution: {dict(bad_dist.most_common(5))}")
print(f"  Fraction |a_p| <= 1 (bad): {sum(1 for a in bad_p if abs(a) <= 1)/len(bad_p):.3f}")
print(f"  Fraction |a_p| <= 1 (good): {sum(1 for a in good_p if abs(a) <= 1)/len(good_p):.3f}")

# This is KNOWN: at bad primes, a_p encodes the reduction type
# (good/multiplicative/additive). At good primes, a_p follows Sato-Tate.
# The QUESTION is: does the PATTERN of bad primes encode anything
# that Megethos (log conductor) doesn't?

# Compute: for each EC, the number of bad primes in our list
n_bad = []
for meta in ec_meta:
    cond = int(meta["cond"])
    nb = sum(1 for p in primes if cond % p == 0)
    n_bad.append(nb)
n_bad = np.array(n_bad)

# Does n_bad predict rank beyond conductor?
rho_nb_rank, p_nb = spearmanr(n_bad, ranks)
rho_cond_rank, _ = spearmanr([m["cond"] for m in ec_meta], ranks)
print(f"\n  rho(n_bad_primes, rank) = {rho_nb_rank:.4f} (p={p_nb:.4e})")
print(f"  rho(log_conductor, rank) = {rho_cond_rank:.4f}")

# Partial: n_bad vs rank after controlling for log_conductor
log_cond = np.log(np.array([m["cond"] for m in ec_meta], dtype=float))
X = np.column_stack([np.ones(len(log_cond)), log_cond])
beta_nb = np.linalg.lstsq(X, n_bad.astype(float), rcond=None)[0]
beta_rk = np.linalg.lstsq(X, ranks.astype(float), rcond=None)[0]
resid_nb = n_bad - X @ beta_nb
resid_rk = ranks - X @ beta_rk
rho_partial, p_partial = spearmanr(resid_nb, resid_rk)
print(f"  Partial rho(n_bad, rank | log_cond) = {rho_partial:.4f} (p={p_partial:.4e})")


# ============================================================
# 3. TORSION-CONDUCTOR joint structure
# ============================================================
print("\n" + "=" * 100)
print("3. TORSION × CONDUCTOR: joint structure beyond separate effects")
print("=" * 100)

torsion = np.array([m["tors"] for m in ec_meta], dtype=float)
conductor = np.array([m["cond"] for m in ec_meta], dtype=float)

# Known: torsion constrains conductor (Szpiro-like bounds)
# But does the PAIR (torsion, conductor) predict rank better than each alone?

from numpy.linalg import lstsq

# Model 1: rank ~ log(conductor)
X1 = np.column_stack([np.ones(len(ranks)), np.log(conductor)])
b1 = lstsq(X1, ranks.astype(float), rcond=None)[0]
r2_cond = 1 - np.sum((ranks - X1 @ b1)**2) / np.sum((ranks - np.mean(ranks))**2)

# Model 2: rank ~ torsion
X2 = np.column_stack([np.ones(len(ranks)), torsion])
b2 = lstsq(X2, ranks.astype(float), rcond=None)[0]
r2_tors = 1 - np.sum((ranks - X2 @ b2)**2) / np.sum((ranks - np.mean(ranks))**2)

# Model 3: rank ~ log(conductor) + torsion
X3 = np.column_stack([np.ones(len(ranks)), np.log(conductor), torsion])
b3 = lstsq(X3, ranks.astype(float), rcond=None)[0]
r2_both = 1 - np.sum((ranks - X3 @ b3)**2) / np.sum((ranks - np.mean(ranks))**2)

# Model 4: rank ~ log(conductor) + torsion + interaction
X4 = np.column_stack([np.ones(len(ranks)), np.log(conductor), torsion,
                       np.log(conductor) * torsion])
b4 = lstsq(X4, ranks.astype(float), rcond=None)[0]
r2_inter = 1 - np.sum((ranks - X4 @ b4)**2) / np.sum((ranks - np.mean(ranks))**2)

print(f"  R²(rank ~ log_cond):                    {r2_cond:.4f}")
print(f"  R²(rank ~ torsion):                     {r2_tors:.4f}")
print(f"  R²(rank ~ log_cond + torsion):          {r2_both:.4f}")
print(f"  R²(rank ~ log_cond + torsion + inter):  {r2_inter:.4f}")
print(f"  Interaction adds: +{r2_inter - r2_both:.4f}")

if r2_inter - r2_both > 0.01:
    print(f"  SIGNAL: Torsion-conductor interaction predicts rank beyond additive.")
else:
    print(f"  No significant interaction effect.")


# ============================================================
# 4. a_p SIGNATURE: can you identify the EC from its a_p vector?
# ============================================================
print("\n" + "=" * 100)
print("4. a_p SIGNATURE: how unique is each EC's coefficient vector?")
print("=" * 100)

# How many a_p values do you need to uniquely identify an EC?
# This tests the "different cameras" hypothesis: each a_p is a projection,
# and enough projections reconstruct the object.

n_curves = len(ap_matrix)
for k in [1, 2, 3, 5, 8, 10, 15]:
    if k > ap_matrix.shape[1]:
        break
    # Using first k a_p values, how many unique vectors?
    truncated = [tuple(row[:k]) for row in ap_matrix]
    n_unique = len(set(truncated))
    print(f"  First {k:2d} a_p values: {n_unique:5d} unique / {n_curves} curves ({n_unique/n_curves*100:.1f}%)")


# ============================================================
# 5. ZERO STRUCTURE: can we see anything in stored zeros?
# ============================================================
print("\n" + "=" * 100)
print("5. L-FUNCTION ZEROS: basic structure check")
print("=" * 100)

con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
zeros = con.execute("""
    SELECT zeros_vector, n_zeros_stored, root_number, analytic_rank
    FROM object_zeros WHERE n_zeros_stored >= 5
    LIMIT 2000
""").fetchall()
con.close()

print(f"  Objects with ≥5 zeros: {len(zeros)}")

# Distribution of zero counts
n_zeros = [r[1] for r in zeros]
print(f"  Zeros per object: min={min(n_zeros)}, max={max(n_zeros)}, mean={np.mean(n_zeros):.1f}")

# Root number distribution
rn_dist = Counter(r[2] for r in zeros if r[2] is not None)
print(f"  Root number: {dict(rn_dist)}")

# Analytic rank distribution
ar_dist = Counter(r[3] for r in zeros if r[3] is not None)
print(f"  Analytic rank: {dict(ar_dist.most_common(5))}")

# Load first zero for each object
first_zeros = []
for zv, nz, rn, ar in zeros:
    try:
        zlist = json.loads(zv) if isinstance(zv, str) else zv
        if isinstance(zlist, list) and len(zlist) >= 1:
            first_zeros.append({"z1": float(zlist[0]), "n": nz, "rn": rn, "ar": ar})
    except:
        pass

if first_zeros:
    z1_arr = np.array([f["z1"] for f in first_zeros])
    ar_arr = np.array([f["ar"] for f in first_zeros if f["ar"] is not None], dtype=float)
    z1_with_ar = np.array([f["z1"] for f in first_zeros if f["ar"] is not None])

    print(f"\n  First zero statistics:")
    print(f"    Mean: {np.mean(z1_arr):.4f}")
    print(f"    Std:  {np.std(z1_arr):.4f}")
    print(f"    Min:  {np.min(z1_arr):.4f}")

    # Does first zero predict analytic rank?
    if len(ar_arr) > 50:
        rho_z1_ar, p_z1 = spearmanr(z1_with_ar, ar_arr)
        print(f"\n  rho(first_zero, analytic_rank) = {rho_z1_ar:.4f} (p={p_z1:.4e})")
        print(f"  (Positive = higher first zero → higher rank)")
        print(f"  This is the SPECTRAL TAIL finding from Charon:")
        print(f"  zeros 5-19 encode rank better than the central zero.")

    # First zero by rank
    for rank_val in sorted(set(int(f["ar"]) for f in first_zeros if f["ar"] is not None)):
        z1_rank = [f["z1"] for f in first_zeros if f["ar"] == rank_val]
        if len(z1_rank) >= 10:
            print(f"    Rank {rank_val}: mean z1={np.mean(z1_rank):.4f}, n={len(z1_rank)}")


# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 100)
print("REMAINING DIRECTIONS SUMMARY")
print("=" * 100)
print(f"""
  1. Cross-prime a_p correlations: {'SIGNAL' if np.mean(off_diag) > 3/np.sqrt(len(ap_matrix)) else 'Independent (Sato-Tate)'} (mean |corr|={np.mean(off_diag):.4f})
  2. Bad vs good reduction: KNOWN STRUCTURE (a_p constrained at bad primes)
     n_bad partial with rank: rho={rho_partial:.4f} (p={p_partial:.4e})
  3. Torsion-conductor interaction on rank: +{r2_inter - r2_both:.4f} R²
  4. a_p uniqueness: {k} coefficients → {n_unique/n_curves*100:.0f}% unique
  5. First zero → rank: rho={rho_z1_ar:.4f}

  Directions NOT yet killed:
  - Coefficient-level sequence structure (beyond distributions)
  - Prime-specific a_p behavior (Euler product decomposition)
  - Torsion-conductor joint structure
  - Zero geometry beyond first zero (the spectral tail)
""")

"""
Investigate MI=0.382 between EC conductors and Maass spectral parameters
after prime detrending. What drives this signal?
"""
import sys
import json
import math
import numpy as np
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))
from search_engine import _get_duck, _load_maass, _maass_cache
from microscope import prime_features, detrend_primes, _factorize

# =========== 1. Load datasets ===========
print("=" * 60)
print("STEP 1: Loading datasets")
print("=" * 60)

con = _get_duck()
rows = con.execute(
    "SELECT conductor, properties FROM objects "
    "WHERE object_type = 'elliptic_curve' AND conductor <= 50000 "
    "ORDER BY conductor"
).fetchall()
con.close()

ec_conductors = []
ec_props = []
for r in rows:
    ec_conductors.append(int(r[0]))
    p = json.loads(r[1]) if isinstance(r[1], str) else (r[1] or {})
    ec_props.append(p)

print(f"EC conductors: n={len(ec_conductors)}, unique={len(set(ec_conductors))}")
print(f"  range: [{min(ec_conductors)}, {max(ec_conductors)}]")

_load_maass()
maass_sp = np.array([m['spectral_parameter'] for m in _maass_cache if 'spectral_parameter' in m])
print(f"Maass spectral params: n={len(maass_sp)}, range=[{maass_sp.min():.4f}, {maass_sp.max():.4f}]")

# =========== 2. Detrend both ===========
print("\n" + "=" * 60)
print("STEP 2: Prime detrending")
print("=" * 60)

unique_cond = sorted(set(ec_conductors))
cond_arr = np.array(unique_cond, dtype=float)
cond_residuals, cond_info = detrend_primes(cond_arr)
print(f"EC detrend: R2={cond_info['r2_prime_model']:.4f}, n_valid={len(cond_residuals)}")

# Maass spectral params are real-valued -> scale x100 for integer prime detrending
maass_int = np.array([int(round(s * 100)) for s in maass_sp])
maass_residuals, maass_info = detrend_primes(maass_int)
print(f"Maass detrend: R2={maass_info['r2_prime_model']:.4f}, n_valid={len(maass_residuals)}")

# =========== 3. MI computation ===========
print("\n" + "=" * 60)
print("STEP 3: Mutual Information Analysis")
print("=" * 60)

from sklearn.metrics import mutual_info_score

def compute_mi_binned(x, y, n_bins=30):
    """MI via binned histogram, in bits."""
    xd = np.digitize(x, np.linspace(x.min() - 1e-10, x.max() + 1e-10, n_bins + 1))
    yd = np.digitize(y, np.linspace(y.min() - 1e-10, y.max() + 1e-10, n_bins + 1))
    return mutual_info_score(xd, yd) / np.log(2)

# Match sizes by subsampling the larger array
n = min(len(cond_residuals), len(maass_residuals))
cr = np.sort(cond_residuals)
mr = np.sort(maass_residuals)

# Method 1: Sorted pairing (rank-order match)
idx_c = np.linspace(0, len(cr) - 1, n).astype(int)
idx_m = np.linspace(0, len(mr) - 1, n).astype(int)
cr_sorted = cr[idx_c]
mr_sorted = mr[idx_m]

mi_sorted = compute_mi_binned(cr_sorted, mr_sorted)
print(f"\nMI (rank-order paired): {mi_sorted:.4f} bits")

# Method 2: Random pairing (no sorting)
np.random.seed(42)
cr_rand = np.random.choice(cond_residuals, n, replace=False)
mr_rand = maass_residuals.copy()
np.random.shuffle(mr_rand)  # random pairing
mi_random = compute_mi_binned(cr_rand, mr_rand[:n] if len(mr_rand) >= n else mr_rand)
print(f"MI (random pairing): {mi_random:.4f} bits")

# Method 3: How the reevaluator likely did it -- subsample EC to Maass size
np.random.seed(123)
ec_sub = np.random.choice(cond_residuals, len(maass_residuals), replace=False)
mi_sub = compute_mi_binned(ec_sub, maass_residuals)
print(f"MI (EC subsampled to Maass size, random pairing): {mi_sub:.4f} bits")

# =========== 3d. Permutation test ===========
print("\n--- Permutation test (1000 shuffles) ---")
np.random.seed(42)
n_perm = 1000
mi_null = []
for _ in range(n_perm):
    shuf = np.random.permutation(maass_residuals)
    mi_null.append(compute_mi_binned(ec_sub, shuf))
mi_null = np.array(mi_null)
p_val = np.mean(mi_null >= mi_sorted)
print(f"Observed MI (sorted): {mi_sorted:.4f}")
print(f"Null MI: mean={mi_null.mean():.4f}, std={mi_null.std():.4f}, max={mi_null.max():.4f}")
print(f"p-value (sorted MI vs null): {p_val:.4f}")

p_val2 = np.mean(mi_null >= mi_sub)
print(f"p-value (subsampled MI vs null): {p_val2:.4f}")

# Also test the sorted-pairing permutation null
mi_null_sorted = []
for _ in range(n_perm):
    mr_shuf = np.random.permutation(mr_sorted)
    mi_null_sorted.append(compute_mi_binned(cr_sorted, mr_shuf))
mi_null_sorted = np.array(mi_null_sorted)
p_sorted = np.mean(mi_null_sorted >= mi_sorted)
print(f"\nSorted-pairing permutation test:")
print(f"  Null MI: mean={mi_null_sorted.mean():.4f}, std={mi_null_sorted.std():.4f}")
print(f"  p-value: {p_sorted:.4f}")
print(f"  z-score: {(mi_sorted - mi_null_sorted.mean()) / max(mi_null_sorted.std(), 1e-10):.2f}")

# =========== 3a. Extreme residuals ===========
print("\n" + "=" * 60)
print("STEP 3a: Extreme EC conductor residuals")
print("=" * 60)

# Map residuals back to conductors
cond_valid = cond_arr[cond_arr > 1]
pct10 = np.percentile(cond_residuals, 10)
pct90 = np.percentile(cond_residuals, 90)

bottom_mask = cond_residuals <= pct10
top_mask = cond_residuals >= pct90
bottom_conds = cond_valid[bottom_mask]
top_conds = cond_valid[top_mask]

print(f"\nBottom 10% residuals (over-predicted by prime model):")
print(f"  n={len(bottom_conds)}")
# What are these? Count prime factors
bottom_factors = [_factorize(int(c)) for c in bottom_conds[:50]]
bottom_nfactors = [len(f) for f in bottom_factors]
print(f"  Avg distinct factors: {np.mean(bottom_nfactors):.2f}")
print(f"  Sample conductors: {[int(c) for c in bottom_conds[:15]]}")
# Are they smooth? highly composite?
bottom_is_prime = [1 if len(f) == 1 and sum(f.values()) == 1 else 0 for f in bottom_factors]
print(f"  Fraction prime: {np.mean(bottom_is_prime):.3f}")

print(f"\nTop 10% residuals (under-predicted by prime model):")
print(f"  n={len(top_conds)}")
top_factors = [_factorize(int(c)) for c in top_conds[:50]]
top_nfactors = [len(f) for f in top_factors]
print(f"  Avg distinct factors: {np.mean(top_nfactors):.2f}")
print(f"  Sample conductors: {[int(c) for c in top_conds[:15]]}")
top_is_prime = [1 if len(f) == 1 and sum(f.values()) == 1 else 0 for f in top_factors]
print(f"  Fraction prime: {np.mean(top_is_prime):.3f}")

# =========== 3b. Maass extreme residuals ===========
print("\n" + "=" * 60)
print("STEP 3b: Maass extreme residuals vs EC extreme residuals")
print("=" * 60)

maass_valid = maass_int[maass_int > 1].astype(float)
mpct10 = np.percentile(maass_residuals, 10)
mpct90 = np.percentile(maass_residuals, 90)

m_bottom = maass_sp[maass_residuals <= mpct10] if len(maass_residuals) == len(maass_sp) else []
m_top = maass_sp[maass_residuals >= mpct90] if len(maass_residuals) == len(maass_sp) else []

# Actually check alignment -- maass_residuals from detrend_primes only keeps values > 1
maass_valid_mask = maass_int > 1
maass_sp_valid = maass_sp[maass_valid_mask]
print(f"Maass valid (int > 1): {len(maass_sp_valid)} of {len(maass_sp)}")

if len(maass_residuals) == len(maass_sp_valid):
    m_bottom_sp = maass_sp_valid[maass_residuals <= mpct10]
    m_top_sp = maass_sp_valid[maass_residuals >= mpct90]
    print(f"\nBottom 10% Maass residuals (spectral params): {m_bottom_sp[:10]}")
    print(f"  Mean: {m_bottom_sp.mean():.4f}, Std: {m_bottom_sp.std():.4f}")
    print(f"\nTop 10% Maass residuals (spectral params): {m_top_sp[:10]}")
    print(f"  Mean: {m_top_sp.mean():.4f}, Std: {m_top_sp.std():.4f}")
    print(f"\nAll Maass mean: {maass_sp_valid.mean():.4f}, Std: {maass_sp_valid.std():.4f}")

# =========== 3c. 2D histogram ===========
print("\n" + "=" * 60)
print("STEP 3c: 2D histogram of MI concentration")
print("=" * 60)

# Use ec_sub and maass_residuals (same size)
nbins = 5
xedges = np.linspace(ec_sub.min(), ec_sub.max(), nbins + 1)
yedges = np.linspace(maass_residuals.min(), maass_residuals.max(), nbins + 1)

hist2d, _, _ = np.histogram2d(ec_sub, maass_residuals, bins=[xedges, yedges])
# Compute MI contribution per cell
total = hist2d.sum()
px = hist2d.sum(axis=1) / total
py = hist2d.sum(axis=0) / total
pxy = hist2d / total

print("2D histogram (5x5 bins):")
print("Cell counts:")
print(hist2d.astype(int))
print("\nMI contribution per cell (bits):")
mi_grid = np.zeros_like(pxy)
for i in range(nbins):
    for j in range(nbins):
        if pxy[i, j] > 0 and px[i] > 0 and py[j] > 0:
            mi_grid[i, j] = pxy[i, j] * math.log2(pxy[i, j] / (px[i] * py[j]))
print(np.round(mi_grid, 4))
print(f"Total MI from grid: {mi_grid.sum():.4f} bits")

# Which quadrant contributes most?
mid_x = nbins // 2
mid_y = nbins // 2
q_ll = mi_grid[:mid_x, :mid_y].sum()
q_lr = mi_grid[:mid_x, mid_y:].sum()
q_ul = mi_grid[mid_x:, :mid_y].sum()
q_ur = mi_grid[mid_x:, mid_y:].sum()
print(f"\nMI by quadrant: LL={q_ll:.4f}, LR={q_lr:.4f}, UL={q_ul:.4f}, UR={q_ur:.4f}")

# =========== 3e. Split by conductor range ===========
print("\n" + "=" * 60)
print("STEP 3e: MI by conductor range")
print("=" * 60)

# Split unique conductors into ranges
ranges = [(1, 5000), (5000, 15000), (15000, 30000), (30000, 50001)]
for lo, hi in ranges:
    mask = (cond_valid >= lo) & (cond_valid < hi)
    cr_range = cond_residuals[mask]
    if len(cr_range) < 30:
        print(f"  [{lo:>6}, {hi:>6}): n={len(cr_range)} (too few)")
        continue
    # Subsample to Maass size or vice versa
    n_match = min(len(cr_range), len(maass_residuals))
    cr_sub = np.random.choice(cr_range, n_match, replace=len(cr_range) < n_match)
    mr_sub = np.random.choice(maass_residuals, n_match, replace=len(maass_residuals) < n_match)
    mi_range = compute_mi_binned(cr_sub, mr_sub)

    # Null for this range
    nulls = []
    for _ in range(200):
        nulls.append(compute_mi_binned(cr_sub, np.random.permutation(mr_sub)))
    nulls = np.array(nulls)
    z = (mi_range - nulls.mean()) / max(nulls.std(), 1e-10)
    print(f"  [{lo:>6}, {hi:>6}): n={len(cr_range):>5}, MI={mi_range:.4f}, null={nulls.mean():.4f}+/-{nulls.std():.4f}, z={z:.2f}")

# =========== 4. Characterize the signal ===========
print("\n" + "=" * 60)
print("STEP 4: Signal characterization")
print("=" * 60)

# Check if MI comes from rank-order alignment (monotone relationship)
from scipy.stats import spearmanr, kendalltau

# Sorted pairing: this IS a rank correlation by construction
# Check random pairing correlation
rho, p_rho = spearmanr(ec_sub, maass_residuals)
print(f"Spearman rho (random pairing): {rho:.4f}, p={p_rho:.4e}")

# Check if the sorted MI is just a binning artifact
# Vary bin count
print("\nMI sensitivity to bin count (sorted pairing):")
for nb in [10, 15, 20, 30, 50, 80]:
    mi_nb = compute_mi_binned(cr_sorted, mr_sorted, n_bins=nb)
    print(f"  bins={nb:>3}: MI={mi_nb:.4f}")

# Check what fraction of MI comes from marginal non-uniformity
print("\nMI with uniform-marginal transform (rank transform):")
cr_rank = np.argsort(np.argsort(cr_sorted)).astype(float)
mr_rank = np.argsort(np.argsort(mr_sorted)).astype(float)
mi_rank = compute_mi_binned(cr_rank, mr_rank)
print(f"  MI(rank-rank, sorted): {mi_rank:.4f}")

# Random rank pairing
np.random.seed(99)
cr_rank2 = np.arange(len(ec_sub), dtype=float)
np.random.shuffle(cr_rank2)
mr_rank2 = np.arange(len(maass_residuals), dtype=float)
np.random.shuffle(mr_rank2)
mi_rank_rand = compute_mi_binned(cr_rank2, mr_rank2)
print(f"  MI(rank-rank, random): {mi_rank_rand:.4f}")

# The key question: what makes sorted pairing special?
# If MI only appears in sorted pairing, it's just saying both distributions
# have similar shapes (both have tails), not a real cross-dataset connection.
print("\n--- CRITICAL TEST ---")
print("Does MI survive WITHOUT rank-order pairing?")
mi_tests = []
for seed in range(100):
    np.random.seed(seed)
    e = np.random.choice(cond_residuals, n, replace=False)
    m = np.random.choice(maass_residuals, n, replace=len(maass_residuals) < n)
    mi_tests.append(compute_mi_binned(e, m))
mi_tests = np.array(mi_tests)
print(f"  100 random pairings: MI mean={mi_tests.mean():.4f}, std={mi_tests.std():.4f}")
print(f"  Max MI across random pairings: {mi_tests.max():.4f}")

# Compare to pure null (both shuffled independently)
mi_null_full = []
for seed in range(100):
    np.random.seed(seed + 10000)
    e = np.random.permutation(np.random.choice(cond_residuals, n, replace=False))
    m = np.random.permutation(np.random.choice(maass_residuals, n, replace=len(maass_residuals) < n))
    mi_null_full.append(compute_mi_binned(e, m))
mi_null_full = np.array(mi_null_full)
print(f"  100 null pairings (both shuffled): MI mean={mi_null_full.mean():.4f}, std={mi_null_full.std():.4f}")

print("\n--- DIAGNOSIS ---")
if mi_tests.mean() > mi_null_full.mean() + 2 * mi_null_full.std():
    print("REAL: Random pairings show MI above null -> genuine cross-dataset structure")
else:
    print("ARTIFACT: Random pairings indistinguishable from null -> MI came from sort-induced correlation")
    print("The MI=0.382 likely arose from rank-order matching of two non-uniform distributions")
    print("Both residual distributions are non-uniform (heavy tails from detrending)")
    print("Sorting and pairing creates artificial dependence")

# Final: what about the residual DISTRIBUTIONS themselves?
print("\n--- Residual distribution comparison ---")
from scipy.stats import ks_2samp, wasserstein_distance

# Standardize both
cr_std = (cond_residuals - cond_residuals.mean()) / cond_residuals.std()
mr_std = (maass_residuals - maass_residuals.mean()) / maass_residuals.std()

ks_stat, ks_p = ks_2samp(cr_std, mr_std)
wd = wasserstein_distance(cr_std, mr_std)
print(f"KS test (standardized residuals): stat={ks_stat:.4f}, p={ks_p:.4e}")
print(f"Wasserstein distance: {wd:.4f}")
print(f"EC residual skew: {float(np.mean(cr_std**3)):.4f}, kurtosis: {float(np.mean(cr_std**4) - 3):.4f}")
print(f"Maass residual skew: {float(np.mean(mr_std**3)):.4f}, kurtosis: {float(np.mean(mr_std**4) - 3):.4f}")

"""
Kill script for Isogeny--Maass MI=0.109 signal.
Seven attack vectors, each independent.
"""
import sys
import json
import math
import numpy as np
from pathlib import Path
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent))

REPO = Path(__file__).resolve().parents[3]

# ============================================================
# Load data
# ============================================================
print("=" * 70)
print("LOADING DATA")
print("=" * 70)

# Load Maass forms
MAASS_JSON = REPO / "cartography" / "maass" / "data" / "maass_forms_full.json"
with open(MAASS_JSON) as f:
    maass_data = json.load(f)

maass_sp = np.array([m["spectral_parameter"] for m in maass_data])
maass_levels = [m.get("level", "?") for m in maass_data]
n_maass = len(maass_sp)
print(f"Maass forms: {n_maass}, all level-1: {all(l == 1 for l in maass_levels)}")
print(f"  spectral range: [{maass_sp.min():.4f}, {maass_sp.max():.4f}]")

# Load isogeny graph metadata for all primes
ISOGENY_DIR = REPO / "cartography" / "isogenies" / "data" / "graphs"
isogeny_data = {}
for pdir in sorted(ISOGENY_DIR.iterdir()):
    if not pdir.is_dir():
        continue
    meta_file = pdir / f"{pdir.name}_metadata.json"
    if meta_file.exists():
        with open(meta_file) as f:
            md = json.load(f)
        isogeny_data[int(md["prime"])] = md

primes_iso = sorted(isogeny_data.keys())
print(f"Isogeny primes: {len(primes_iso)}, range [{primes_iso[0]}, {primes_iso[-1]}]")

# Extract node counts
iso_primes = np.array(primes_iso)
iso_nodes = np.array([isogeny_data[p]["nodes"] for p in primes_iso])
iso_formula = np.array([(p - 1) / 12 for p in primes_iso])

print(f"Node counts range: [{iso_nodes.min()}, {iso_nodes.max()}]")
print(f"Formula (p-1)/12 range: [{iso_formula.min():.2f}, {iso_formula.max():.2f}]")

# Check how nodes relate to formula
iso_residual_from_formula = iso_nodes - iso_formula
print(f"nodes - (p-1)/12: unique values = {sorted(set(np.round(iso_residual_from_formula, 4)))[:20]}")


# ============================================================
# Helper: binned MI
# ============================================================
from sklearn.metrics import mutual_info_score

def compute_mi_binned(x, y, n_bins=30):
    """MI via binned histogram, in bits."""
    xd = np.digitize(x, np.linspace(x.min() - 1e-10, x.max() + 1e-10, n_bins + 1))
    yd = np.digitize(y, np.linspace(y.min() - 1e-10, y.max() + 1e-10, n_bins + 1))
    return mutual_info_score(xd, yd) / np.log(2)

def permutation_test(x, y, n_perm=2000, n_bins=30):
    """Return observed MI, null mean, null std, z-score, p-value."""
    mi_obs = compute_mi_binned(x, y, n_bins)
    nulls = []
    for i in range(n_perm):
        nulls.append(compute_mi_binned(x, np.random.permutation(y), n_bins))
    nulls = np.array(nulls)
    z = (mi_obs - nulls.mean()) / max(nulls.std(), 1e-10)
    p = np.mean(nulls >= mi_obs)
    return mi_obs, nulls.mean(), nulls.std(), z, p


# ============================================================
# ATTACK 1: Finite-sample bias floor
# ============================================================
print("\n" + "=" * 70)
print("ATTACK 1: FINITE-SAMPLE BIAS FLOOR")
print("=" * 70)

n = 300  # sample size
for b in [10, 15, 20, 25, 30, 50]:
    bias = (b - 1)**2 / (2 * n * np.log(2))
    print(f"  bins={b:>3}: null MI bias = {bias:.4f} bits")

# The claimed MI is 0.109 bits with some number of bins.
# Also compute empirically with uniform random data
print("\nEmpirical null MI (uniform random, n=300):")
np.random.seed(42)
for b in [10, 15, 20, 25, 30]:
    null_mis = []
    for _ in range(5000):
        x = np.random.randn(300)
        y = np.random.randn(300)
        null_mis.append(compute_mi_binned(x, y, b))
    null_mis = np.array(null_mis)
    print(f"  bins={b:>3}: empirical null MI = {null_mis.mean():.4f} +/- {null_mis.std():.4f}, "
          f"95th pct = {np.percentile(null_mis, 95):.4f}, 99th = {np.percentile(null_mis, 99):.4f}")

print(f"\nClaimed MI = 0.109 bits.")
print(f"VERDICT: Compare 0.109 to the bias floors above.")


# ============================================================
# ATTACK 2: TAUTOLOGY — Both are level-1 invariants
# ============================================================
print("\n" + "=" * 70)
print("ATTACK 2: TAUTOLOGY — both are level-1 invariants of p")
print("=" * 70)

# The isogeny node count for prime p is:
#   floor((p-1)/12) + correction(p mod 12)
# where the correction depends on p mod 12:
#   p ≡ 1 mod 12: nodes = (p-1)/12 + 1  (extra from j=0 AND j=1728)
#   p ≡ 5,7 mod 12: nodes = floor((p-1)/12) + 1
#   p ≡ 11 mod 12: nodes = (p+1)/12  = floor((p-1)/12) + 1
# Actually, the exact formula for number of supersingular j-invariants mod p is:
#   floor(p/12) + {0 if p≡1 mod 12, 0 if p≡5 mod 12, 1 if p≡7 mod 12, 1 if p≡11 mod 12}
# Let me just check empirically:

print("Node count vs (p-1)/12 by p mod 12:")
for r in [1, 5, 7, 11]:
    mask = iso_primes % 12 == r
    if mask.sum() == 0:
        continue
    ps = iso_primes[mask]
    ns = iso_nodes[mask]
    formula_vals = (ps - 1) / 12.0
    diffs = ns - formula_vals
    print(f"  p == {r:>2} (mod 12): n={mask.sum():>4}, "
          f"nodes - (p-1)/12: mean={diffs.mean():.4f}, "
          f"unique rounded = {sorted(set(np.round(diffs, 2)))[:8]}")

# The node count is DETERMINISTIC from p. It equals floor(p/12) + epsilon(p mod 12).
# So the isogeny "data" carries zero information beyond p itself.
# The Maass spectral parameters, being level-1, are eigenvalues of the hyperbolic
# Laplacian on SL(2,Z)\H. They have no direct relation to p.
# BUT: if the pairing is rank-ordered, then we're comparing the distribution of
# supersingular counts (which grow linearly in p) with Maass spectral params.

print("\nThe isogeny node count is EXACTLY determined by p.")
print("It's floor(p/12) + correction(p mod 12).")
print("There is NO stochastic component — no information beyond p itself.")
print("QUESTION: What pairing was used to compute MI=0.109?")


# ============================================================
# ATTACK 3: Replace node counts with raw (p-1)/12 remainders
# ============================================================
print("\n" + "=" * 70)
print("ATTACK 3: MI with (p-1)/12 FRACTIONAL PART as isogeny proxy")
print("=" * 70)

# The detrending residual of the isogeny node count is essentially
# the fractional part of (p-1)/12 (since the integer part grows linearly).
# Let's test: does MI come from this fractional part structure?

# First, we need to understand HOW the original MI was computed.
# The claim is 300 Maass forms paired with isogeny data.
# We have 300 Maass forms. The isogeny data covers many primes.
# Most likely pairing: for each Maass form, pick a prime and compute
# the isogeny graph. Or: sorted-rank pairing.

# Let's reproduce the MI=0.109 first, then attack it.
# Use the 300 smallest isogeny primes to match 300 Maass forms.

# Pick 300 primes from isogeny data
n_match = min(300, len(primes_iso))
iso_subset_primes = iso_primes[:n_match]
iso_subset_nodes = iso_nodes[:n_match]

# Compute isogeny residuals: detrend the linear growth
# The nodes ~ p/12, so residual = nodes - p/12
iso_resid = iso_subset_nodes - iso_subset_primes / 12.0

# Sort both and pair
iso_resid_sorted = np.sort(iso_resid)
maass_sorted = np.sort(maass_sp)

# Compute MI with sorted pairing
mi_sorted, null_mean, null_std, z_sorted, p_sorted = permutation_test(
    iso_resid_sorted, maass_sorted, n_perm=2000, n_bins=20
)
print(f"MI (sorted pairing, 20 bins): {mi_sorted:.4f}, null={null_mean:.4f}+/-{null_std:.4f}, z={z_sorted:.2f}, p={p_sorted:.4f}")

# Now try different bin counts
for nb in [10, 15, 20, 25, 30]:
    mi_nb = compute_mi_binned(iso_resid_sorted, maass_sorted, nb)
    print(f"  bins={nb}: MI={mi_nb:.4f}")

# Now replace with fractional part of (p-1)/12
frac_part = (iso_subset_primes - 1) / 12.0 - np.floor((iso_subset_primes - 1) / 12.0)
frac_sorted = np.sort(frac_part)

mi_frac, null_frac_mean, null_frac_std, z_frac, p_frac = permutation_test(
    frac_sorted, maass_sorted, n_perm=2000, n_bins=20
)
print(f"\nMI with fractional part proxy: {mi_frac:.4f}, null={null_frac_mean:.4f}+/-{null_frac_std:.4f}, z={z_frac:.2f}, p={p_frac:.4f}")

# And with just p mod 12 (4 categories for primes > 3)
pmod12 = iso_subset_primes % 12
pmod12_sorted = np.sort(pmod12.astype(float))
mi_mod12, null_mod12_mean, null_mod12_std, z_mod12, p_mod12 = permutation_test(
    pmod12_sorted, maass_sorted, n_perm=2000, n_bins=20
)
print(f"MI with p mod 12 only: {mi_mod12:.4f}, null={null_mod12_mean:.4f}+/-{null_mod12_std:.4f}, z={z_mod12:.2f}, p={p_mod12:.4f}")


# ============================================================
# ATTACK 4: SORTED-RANK PAIRING CREATES ARTIFICIAL MI
# ============================================================
print("\n" + "=" * 70)
print("ATTACK 4: SORTED vs RANDOM PAIRING")
print("=" * 70)

# Sorted pairing
mi_sort = compute_mi_binned(iso_resid_sorted, maass_sorted, 20)
print(f"MI (sorted pairing): {mi_sort:.4f}")

# Random pairing — many trials
np.random.seed(42)
mi_random_trials = []
for _ in range(1000):
    perm_iso = np.random.permutation(iso_resid[:n_match])
    perm_maass = np.random.permutation(maass_sp)
    mi_random_trials.append(compute_mi_binned(perm_iso, perm_maass, 20))
mi_random_trials = np.array(mi_random_trials)

print(f"MI (random pairing, 1000 trials): mean={mi_random_trials.mean():.4f}, "
      f"std={mi_random_trials.std():.4f}, max={mi_random_trials.max():.4f}")

# Pure null (both from independent uniforms)
mi_null_pure = []
for _ in range(1000):
    x = np.random.randn(n_match)
    y = np.random.randn(n_match)
    mi_null_pure.append(compute_mi_binned(x, y, 20))
mi_null_pure = np.array(mi_null_pure)
print(f"MI (pure null, independent normal): mean={mi_null_pure.mean():.4f}, std={mi_null_pure.std():.4f}")

z_random_vs_null = (mi_random_trials.mean() - mi_null_pure.mean()) / max(mi_null_pure.std(), 1e-10)
print(f"\nRandom pairing vs pure null: z = {z_random_vs_null:.2f}")

if mi_random_trials.mean() < mi_null_pure.mean() + 2 * mi_null_pure.std():
    print("KILL: Random pairing MI is indistinguishable from null.")
    print("      The sorted-pairing MI is an ARTIFACT of rank-order alignment.")
else:
    print("SURVIVES: Random pairing MI exceeds null — there may be real structure.")

# Additional: compute MI between two COMPLETELY UNRELATED distributions
# with sorted pairing to show sorted pairing always inflates MI
print("\nControl: MI between sorted uniform & sorted exponential (n=300, unrelated):")
np.random.seed(77)
for _ in range(5):
    u = np.sort(np.random.uniform(0, 1, 300))
    e = np.sort(np.random.exponential(1, 300))
    mi_ctrl = compute_mi_binned(u, e, 20)
    print(f"  MI = {mi_ctrl:.4f}")


# ============================================================
# ATTACK 5: p mod 12 RESIDUAL STRUCTURE
# ============================================================
print("\n" + "=" * 70)
print("ATTACK 5: p mod 12 RESIDUAL STRUCTURE")
print("=" * 70)

# For primes > 3, p mod 12 can only be 1, 5, 7, 11
# This creates exactly 4 groups. With n=300 primes, group sizes matter.
residues = iso_subset_primes % 12
for r in [1, 5, 7, 11]:
    ct = np.sum(residues == r)
    print(f"  p ≡ {r:>2} (mod 12): n={ct}, fraction={ct/n_match:.3f}")

# The isogeny residual (nodes - p/12) is almost entirely determined by p mod 12
print("\nIsogeny residual by p mod 12 class:")
for r in [1, 5, 7, 11]:
    mask = residues == r
    if mask.sum() > 0:
        resids = iso_resid[:n_match][mask]
        print(f"  p == {r:>2} mod12: mean_resid={resids.mean():.4f}, std={resids.std():.4f}")

# After removing mod-12 effect, what remains?
# Remove group means
iso_resid_demod12 = iso_resid[:n_match].copy()
for r in [1, 5, 7, 11]:
    mask = residues == r
    if mask.sum() > 0:
        iso_resid_demod12[mask] -= iso_resid_demod12[mask].mean()

print(f"\nResidual after mod-12 removal: std={iso_resid_demod12.std():.6f}")
print(f"  Unique values: {sorted(set(np.round(iso_resid_demod12, 6)))[:15]}")

# MI with mod-12-removed residuals (sorted pairing)
resid_demod_sorted = np.sort(iso_resid_demod12)
mi_demod, null_demod_mean, null_demod_std, z_demod, p_demod = permutation_test(
    resid_demod_sorted, maass_sorted, n_perm=2000, n_bins=20
)
print(f"\nMI after mod-12 removal (sorted): {mi_demod:.4f}, null={null_demod_mean:.4f}+/-{null_demod_std:.4f}, z={z_demod:.2f}")


# ============================================================
# ATTACK 6: U-SHAPED VARIANCE = REGRESSION TO MEAN?
# ============================================================
print("\n" + "=" * 70)
print("ATTACK 6: U-SHAPED VARIANCE AS REGRESSION TO MEAN ARTIFACT")
print("=" * 70)

# Claim: extreme isogeny residuals correspond to more Maass variance.
# Test: does this happen with INDEPENDENT data?
np.random.seed(42)
n_test = 300

print("Testing U-shape with INDEPENDENT data (no real coupling):")
u_shape_count = 0
n_trials = 1000
for trial in range(n_trials):
    x = np.random.randn(n_test)
    y = np.random.randn(n_test)
    # Bin x into deciles, measure std of y in extreme vs middle bins
    deciles = np.digitize(x, np.percentile(x, np.arange(10, 100, 10)))
    extreme_y = np.concatenate([y[deciles == 0], y[deciles == 9]])
    middle_y = np.concatenate([y[deciles == 4], y[deciles == 5]])
    if len(extreme_y) > 5 and len(middle_y) > 5:
        if np.std(extreme_y) > np.std(middle_y):
            u_shape_count += 1

print(f"  U-shape frequency (independent data): {u_shape_count}/{n_trials} = {u_shape_count/n_trials:.3f}")
print(f"  Expected if no effect: ~0.50")

# Now test with BINNING-INDUCED effect: if x and y are both non-uniform
# (heavy-tailed), sorting and pairing creates edge effects
print("\nWith heavy-tailed data (t-distribution, df=3):")
u_shape_heavy = 0
for trial in range(n_trials):
    x = np.sort(stats.t.rvs(3, size=n_test))
    y = np.sort(stats.t.rvs(3, size=n_test))  # sorted pairing
    deciles = np.digitize(x, np.percentile(x, np.arange(10, 100, 10)))
    extreme_y = np.concatenate([y[deciles == 0], y[deciles == 9]])
    middle_y = np.concatenate([y[deciles == 4], y[deciles == 5]])
    if len(extreme_y) > 5 and len(middle_y) > 5:
        if np.std(extreme_y) > np.std(middle_y):
            u_shape_heavy += 1

print(f"  U-shape frequency (sorted heavy-tailed): {u_shape_heavy}/{n_trials} = {u_shape_heavy/n_trials:.3f}")

# Compare: with random pairing of same heavy-tailed data
u_shape_random = 0
for trial in range(n_trials):
    x = stats.t.rvs(3, size=n_test)
    y = stats.t.rvs(3, size=n_test)  # NOT sorted
    deciles = np.digitize(x, np.percentile(x, np.arange(10, 100, 10)))
    extreme_y = np.concatenate([y[deciles == 0], y[deciles == 9]])
    middle_y = np.concatenate([y[deciles == 4], y[deciles == 5]])
    if len(extreme_y) > 5 and len(middle_y) > 5:
        if np.std(extreme_y) > np.std(middle_y):
            u_shape_random += 1

print(f"  U-shape frequency (random heavy-tailed): {u_shape_random}/{n_trials} = {u_shape_random/n_trials:.3f}")


# ============================================================
# ATTACK 7: MULTIPLE COMPARISONS
# ============================================================
print("\n" + "=" * 70)
print("ATTACK 7: MULTIPLE COMPARISONS (BONFERRONI)")
print("=" * 70)

n_tests = 14  # claimed number of dataset pairs tested
z_claimed = 5.1
p_claimed = 0.001  # one-sided

# Bonferroni threshold
alpha = 0.05
bonferroni_alpha = alpha / n_tests
print(f"Nominal p-value: {p_claimed}")
print(f"Bonferroni threshold (alpha={alpha}, {n_tests} tests): {bonferroni_alpha:.6f}")

# Convert z to two-sided p
from scipy.stats import norm
p_from_z = 2 * norm.sf(abs(z_claimed))  # two-sided
p_one_sided = norm.sf(z_claimed)  # one-sided
print(f"\nz = {z_claimed}:")
print(f"  Two-sided p = {p_from_z:.2e}")
print(f"  One-sided p = {p_one_sided:.2e}")
print(f"  Bonferroni threshold = {bonferroni_alpha:.6f} = {bonferroni_alpha:.2e}")

if p_one_sided < bonferroni_alpha:
    print(f"  SURVIVES Bonferroni: p={p_one_sided:.2e} < {bonferroni_alpha:.2e}")
elif p_from_z < bonferroni_alpha:
    print(f"  SURVIVES Bonferroni (two-sided): p={p_from_z:.2e} < {bonferroni_alpha:.2e}")
else:
    print(f"  KILLED by Bonferroni")

# Holm-Bonferroni (less conservative)
print(f"\nHolm-Bonferroni: if this is the most significant of {n_tests} tests,")
print(f"  threshold for rank-1 = {alpha/n_tests:.6f}")
print(f"  Even Holm threshold = {alpha/n_tests:.2e}")

# Sidak correction
sidak_alpha = 1 - (1 - alpha) ** (1 / n_tests)
print(f"\nSidak threshold: {sidak_alpha:.6f}")
if p_one_sided < sidak_alpha:
    print(f"  SURVIVES Sidak")
else:
    print(f"  KILLED by Sidak")


# ============================================================
# SYNTHESIS: REPRODUCE THE CLAIMED MI=0.109
# ============================================================
print("\n" + "=" * 70)
print("SYNTHESIS: ATTEMPTING TO REPRODUCE MI=0.109")
print("=" * 70)

# The claim mentions "prime detrending AND mod-12 congruence removal"
# Let's try various reconstruction approaches

# Approach A: detrend iso_nodes by regressing on p, then remove mod-12 group means
log_nodes = np.log(iso_subset_nodes.astype(float))
log_p = np.log(iso_subset_primes.astype(float))

# Linear regression of log(nodes) on log(p)
slope, intercept, r, p_val, se = stats.linregress(log_p, log_nodes)
predicted_log_nodes = slope * log_p + intercept
iso_detrend_a = log_nodes - predicted_log_nodes

# Remove mod-12
for r_val in [1, 5, 7, 11]:
    mask = residues == r_val
    if mask.sum() > 0:
        iso_detrend_a[mask] -= iso_detrend_a[mask].mean()

print(f"Approach A (log-log detrend + mod-12 removal):")
print(f"  Isogeny residual std: {iso_detrend_a.std():.6f}")

# Sorted pairing with Maass
iso_a_sorted = np.sort(iso_detrend_a)
mi_a, null_a_mean, null_a_std, z_a, p_a = permutation_test(
    iso_a_sorted, maass_sorted, n_perm=2000, n_bins=20
)
print(f"  MI (sorted): {mi_a:.4f}, z={z_a:.2f}, p={p_a:.4f}")

# Random pairing
np.random.seed(42)
mi_a_random = []
for _ in range(1000):
    mi_a_random.append(compute_mi_binned(
        np.random.permutation(iso_detrend_a),
        np.random.permutation(maass_sp),
        20
    ))
mi_a_random = np.array(mi_a_random)
print(f"  MI (random): mean={mi_a_random.mean():.4f}, std={mi_a_random.std():.4f}")

# Approach B: use the detrend_primes function from microscope
from microscope import detrend_primes

# Detrend isogeny node counts via prime features
iso_prime_resid, iso_info = detrend_primes(iso_subset_nodes)
print(f"\nApproach B (microscope.detrend_primes on node counts):")
print(f"  Info: {iso_info}")
print(f"  n_residuals: {len(iso_prime_resid)}")

# Detrend Maass spectral params (scale to integers first, as original code does)
maass_int = np.array([int(round(s * 100)) for s in maass_sp])
maass_resid, maass_info = detrend_primes(maass_int)
print(f"  Maass detrend info: {maass_info}")
print(f"  n_maass_resid: {len(maass_resid)}")

# Match sizes
n_b = min(len(iso_prime_resid), len(maass_resid))
iso_b_sorted = np.sort(iso_prime_resid)[:n_b] if len(iso_prime_resid) > n_b else np.sort(iso_prime_resid)
maass_b_sorted = np.sort(maass_resid)[:n_b] if len(maass_resid) > n_b else np.sort(maass_resid)

# Resample to match
iso_b_idx = np.linspace(0, len(np.sort(iso_prime_resid)) - 1, n_b).astype(int)
maass_b_idx = np.linspace(0, len(np.sort(maass_resid)) - 1, n_b).astype(int)
iso_b_sorted = np.sort(iso_prime_resid)[iso_b_idx]
maass_b_sorted = np.sort(maass_resid)[maass_b_idx]

for nb in [10, 15, 20, 25, 30]:
    mi_b = compute_mi_binned(iso_b_sorted, maass_b_sorted, nb)
    print(f"  bins={nb}: MI(sorted)={mi_b:.4f}")

mi_b, null_b_mean, null_b_std, z_b, p_b = permutation_test(
    iso_b_sorted, maass_b_sorted, n_perm=2000, n_bins=20
)
print(f"  MI(sorted, 20 bins): {mi_b:.4f}, null={null_b_mean:.4f}+/-{null_b_std:.4f}, z={z_b:.2f}, p={p_b:.4f}")


# ============================================================
# FINAL VERDICT
# ============================================================
print("\n" + "=" * 70)
print("FINAL KILL REPORT")
print("=" * 70)

print("""
Attack 1 (Finite-sample bias): Check outputs above — if MI=0.109 is within
         2 sigma of the empirical null for the bin count used, it's dead.

Attack 2 (Tautology): The isogeny node count is DETERMINISTIC from p.
         nodes = floor(p/12) + correction(p mod 12). No stochastic component.
         The "signal" is between a deterministic function of p and Maass
         spectral parameters. This isn't isogeny-specific information.

Attack 3 (Fractional part): If MI with fractional part of (p-1)/12 matches
         the claimed MI, then the isogeny structure contributes nothing.

Attack 4 (Sorted pairing): THE CRITICAL TEST. If MI drops to null under
         random pairing, the signal is entirely an artifact of rank-order
         alignment between two non-uniform distributions.

Attack 5 (p mod 12): With only 4 residue classes and 300 points, the
         residual after mod-12 removal has very few distinct values.
         Any MI is likely binning noise.

Attack 6 (U-shape): If U-shape frequency with independent data is ~50%,
         the claimed "variance coupling" is not evidence of anything.

Attack 7 (Multiple comparisons): z=5.1 gives p ≈ 1.7e-7 one-sided.
         Bonferroni threshold for 14 tests at alpha=0.05 is 0.0036.
         This SURVIVES multiple comparison correction.
""")

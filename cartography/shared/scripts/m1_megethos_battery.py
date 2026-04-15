#!/usr/bin/env python3
"""
Megethos Battery Test — run the "universal magnitude axis" through the battery.

Claim: Megethos (magnitude) is a universal axis accounting for 44% of
cross-domain structure. It naturally selects base e. In arithmetic domains
it decomposes as M = sum f_p*log(p). In geometric domains (knots, polytopes)
it decomposes differently but IS the SAME axis.

Tests:
1. Does log(magnitude) explain 44% of variance across domains? (F24)
2. Does the axis TRANSFER across domains? (F25)
3. Is it just "bigger numbers are bigger"? (Benford/size control)
4. Is base e genuinely preferred? (compare bases 2, e, 10, phi)
5. Does the arithmetic decomposition M = sum f_p*log(p) hold? (prime factorization)

M1 (Skullport), 2026-04-14
"""
import sys, os, json
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

_scripts = str(Path("F:/Prometheus/cartography/shared/scripts").resolve())
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

from battery_v2 import BatteryV2
from scipy import stats as sp_stats
bv2 = BatteryV2()

DATA = Path("F:/Prometheus/cartography")

# ═══════════════════════════════════════════════════════════════════════
# LOAD MAGNITUDE DATA FROM MULTIPLE DOMAINS
# ═══════════════════════════════════════════════════════════════════════
print("Loading magnitude data from 6 domains...")

import duckdb, re

# 1. EC conductors
con = duckdb.connect("F:/Prometheus/charon/data/charon.duckdb", read_only=True)
ec_cond = con.execute("SELECT conductor FROM elliptic_curves WHERE conductor > 0 LIMIT 20000").fetchnumpy()["conductor"].astype(float)
con.close()

# 2. NF discriminants
with open(DATA / "number_fields/data/number_fields.json") as f:
    nf_data = json.load(f)
nf_disc = np.array([abs(int(d["disc_abs"])) for d in nf_data if abs(int(d["disc_abs"])) > 1], dtype=float)

# 3. Knot determinants
with open(DATA / "knots/data/knots.json") as f:
    knot_data = json.load(f)
knot_det = np.array([k["determinant"] for k in knot_data["knots"] if (k.get("determinant") or 0) > 0], dtype=float)

# 4. OEIS sequence values (first non-trivial term)
oeis_vals = []
oeis_path = DATA / "oeis/data/stripped_new.txt"
if oeis_path.exists():
    with open(oeis_path) as f:
        for i, line in enumerate(f):
            if i >= 10000:
                break
            parts = line.strip().split(",")
            for p in parts[1:4]:  # first few terms
                try:
                    v = abs(int(p.strip()))
                    if v > 1:
                        oeis_vals.append(v)
                        break
                except:
                    continue
oeis_vals = np.array(oeis_vals, dtype=float)

# 5. Polytope f-vector sums
poly_path = DATA / "polytopes/data/polytopes.json"
poly_mag = []
if poly_path.exists():
    with open(poly_path) as f:
        polytopes = json.load(f)
    if isinstance(polytopes, list):
        for p in polytopes:
            fv = p.get("f_vector") or p.get("F_VECTOR") or []
            if isinstance(fv, list) and fv:
                poly_mag.append(sum(abs(x) for x in fv if isinstance(x, (int, float))))
    elif isinstance(polytopes, dict):
        for key, p in polytopes.items():
            if isinstance(p, dict):
                fv = p.get("f_vector") or p.get("F_VECTOR") or []
                if isinstance(fv, list) and fv:
                    poly_mag.append(sum(abs(x) for x in fv if isinstance(x, (int, float))))
poly_mag = np.array([x for x in poly_mag if x > 0], dtype=float)

# 6. Knot crossing numbers (geometric magnitude)
knot_crossing = np.array([k.get("crossing_number") or 0 for k in knot_data["knots"]], dtype=float)
# Extract from name if field is 0
for i, k in enumerate(knot_data["knots"]):
    if knot_crossing[i] == 0:
        m = re.match(r'(\d+)', k.get("name", ""))
        if m:
            knot_crossing[i] = int(m.group(1))
knot_crossing = knot_crossing[knot_crossing > 0]

domains = {
    "EC_conductor": ec_cond,
    "NF_discriminant": nf_disc,
    "Knot_determinant": knot_det,
    "OEIS_values": oeis_vals,
    "Polytope_fvector": poly_mag,
    "Knot_crossing": knot_crossing,
}

for name, arr in domains.items():
    print(f"  {name:20s}: n={len(arr)}, range=[{np.min(arr):.0f}, {np.max(arr):.0f}], median={np.median(arr):.0f}")

# ═══════════════════════════════════════════════════════════════════════
# TEST 1: Does log(magnitude) create a universal axis? (cross-domain F24)
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("TEST 1: F24 — domain label -> log(magnitude)")
print("="*70)

# Pool all domains, label by source
all_log_mags = []
all_domain_labels = []
for name, arr in domains.items():
    log_arr = np.log(arr[arr > 0])
    # Subsample large domains to 3000
    if len(log_arr) > 3000:
        rng = np.random.RandomState(42)
        idx = rng.choice(len(log_arr), 3000, replace=False)
        log_arr = log_arr[idx]
    all_log_mags.extend(log_arr)
    all_domain_labels.extend([name] * len(log_arr))

all_log_mags = np.array(all_log_mags)
all_domain_labels = np.array(all_domain_labels)

v1, r1 = bv2.F24_variance_decomposition(all_log_mags, all_domain_labels)
print(f"F24 domain->log(magnitude): {v1}, eta2={r1.get('eta_squared', 0):.4f}")
print(f"(Claim: 44% of structure is magnitude. Measured: {r1.get('eta_squared', 0)*100:.1f}%)")

v1b, r1b = bv2.F24b_metric_consistency(all_log_mags, all_domain_labels)
print(f"F24b: {v1b}")

for label, gs in sorted(r1.get("group_stats", {}).items()):
    print(f"  {label:20s}: n={gs['n']}, mean log(M)={gs['mean']:.3f}, std={gs['std']:.3f}")

# ═══════════════════════════════════════════════════════════════════════
# TEST 2: F25 — does magnitude transfer across domains?
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("TEST 2: F25 — magnitude transferability across domains")
print("="*70)

# Bin log(magnitude) into quintiles as the "grouping"
mag_quintiles = np.array([f"Q{min(5, 1+int(np.searchsorted(np.percentile(all_log_mags, [20,40,60,80]), m)))}"
                           for m in all_log_mags])

v2, r2 = bv2.F25_transportability(all_log_mags, mag_quintiles, all_domain_labels)
print(f"F25 verdict: {v2}")
if "weighted_oos_r2" in r2:
    print(f"Weighted OOS R2: {r2['weighted_oos_r2']:.4f}")
if "per_partition" in r2:
    for p in r2["per_partition"][:6]:
        print(f"  Held-out {p['held_out']}: n={p['n_test']}, OOS R2={p['r2_oos']:.4f}")

# ═══════════════════════════════════════════════════════════════════════
# TEST 3: Is base e preferred? Compare bases 2, e, 10, phi
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("TEST 3: Base preference — log_b(magnitude) normality test")
print("="*70)

phi = (1 + np.sqrt(5)) / 2
bases = {"2": 2, "e": np.e, "10": 10, "phi": phi, "3": 3}

for name, arr in domains.items():
    pos = arr[arr > 1]
    if len(pos) < 100:
        continue
    print(f"\n  {name}:")
    for bname, base in bases.items():
        log_vals = np.log(pos) / np.log(base)
        # Test normality of the log-transformed values
        # Better normality = better base
        stat, p_norm = sp_stats.normaltest(log_vals[:5000])
        skew = sp_stats.skew(log_vals)
        kurt = sp_stats.kurtosis(log_vals)
        # Also test uniformity of fractional parts (Benford-like)
        frac_parts = log_vals % 1
        ks_stat, ks_p = sp_stats.kstest(frac_parts, 'uniform')
        print(f"    base {bname:>4s}: skew={skew:+.4f}, kurt={kurt:+.4f}, "
              f"normality_p={p_norm:.2e}, frac_uniform_KS={ks_stat:.4f}")

# ═══════════════════════════════════════════════════════════════════════
# TEST 4: Arithmetic decomposition M = sum f_p * log(p)
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("TEST 4: Prime factorization — does log(N) = sum f_p*log(p)?")
print("="*70)

from sympy import factorint

# This is trivially true for integers by definition: log(N) = sum f_p*log(p)
# The question is: does the DISTRIBUTION of f_p values encode cross-domain structure?

# For each domain: compute the prime factorization vector
print("Computing prime factor profiles...")
small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]

domain_profiles = {}
for name, arr in [("EC_conductor", ec_cond[:3000]), ("NF_discriminant", nf_disc[:3000]),
                   ("Knot_determinant", knot_det)]:
    profiles = []
    for v in arr[:2000]:
        n = int(v)
        if n <= 1 or n > 10**15:
            continue
        try:
            factors = factorint(n)
        except:
            continue
        profile = [factors.get(p, 0) for p in small_primes]
        profiles.append(profile)

    profiles = np.array(profiles)
    domain_profiles[name] = profiles
    print(f"  {name}: {len(profiles)} objects, {profiles.shape[1]} primes")

    # Which primes dominate?
    mean_profile = np.mean(profiles, axis=0)
    print(f"    Mean profile: {', '.join(f'p={p}:{m:.3f}' for p, m in zip(small_primes, mean_profile))}")

# F24: does domain label predict prime factor profile?
print("\n  F24: domain -> prime factor features")
for p_idx, p in enumerate(small_primes[:5]):
    all_vals = []
    all_labels = []
    for name, profiles in domain_profiles.items():
        all_vals.extend(profiles[:, p_idx])
        all_labels.extend([name] * len(profiles))
    v, r = bv2.F24_variance_decomposition(np.array(all_vals, dtype=float), np.array(all_labels))
    print(f"    f_{p} (exponent of {p}): eta2={r.get('eta_squared', 0):.4f} ({v})")

# ═══════════════════════════════════════════════════════════════════════
# TEST 5: Benford control — is magnitude axis just "Benford's law"?
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("TEST 5: Benford control — is the magnitude axis trivial?")
print("="*70)

# If all domains follow Benford's law, they'll all have similar log distributions
# The magnitude axis would just be "integers follow Benford's law"
for name, arr in domains.items():
    pos = arr[arr > 0]
    if len(pos) < 100:
        continue
    # Leading digit distribution
    leading = np.array([int(str(int(abs(v)))[0]) for v in pos if v >= 1])
    if len(leading) == 0:
        continue
    from collections import Counter
    digit_counts = Counter(leading)
    benford_expected = {d: np.log10(1 + 1/d) for d in range(1, 10)}

    chi2 = 0
    for d in range(1, 10):
        observed = digit_counts.get(d, 0) / len(leading)
        expected = benford_expected[d]
        chi2 += (observed - expected)**2 / expected

    print(f"  {name:20s}: Benford chi2={chi2:.4f} ({'BENFORD' if chi2 < 0.01 else 'NOT_BENFORD' if chi2 > 0.05 else 'MARGINAL'})")

# ═══════════════════════════════════════════════════════════════════════
# TEST 6: Cross-domain correlation AFTER removing magnitude
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("TEST 6: What structure remains AFTER removing the magnitude axis?")
print("="*70)

# For each domain pair: correlation of log(values) vs correlation of residuals
# after removing the shared log-magnitude
print("  Magnitude-removed cross-domain structure:")
for name, profiles in domain_profiles.items():
    log_mags = np.log(np.sum(profiles * np.log(small_primes[:profiles.shape[1]]), axis=1).clip(1))
    # Residual = profile after removing magnitude projection
    mag_direction = np.mean(profiles, axis=0)
    mag_direction = mag_direction / (np.linalg.norm(mag_direction) + 1e-10)
    projections = profiles @ mag_direction
    residuals = profiles - np.outer(projections, mag_direction)
    residual_norms = np.linalg.norm(residuals, axis=1)
    print(f"  {name}: magnitude explains {np.var(projections) / (np.var(projections) + np.mean(np.var(residuals, axis=0)) + 1e-10) * 100:.1f}% of profile variance")

# ═══════════════════════════════════════════════════════════════════════
# CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("CLASSIFICATION: Megethos (universal magnitude axis)")
print("="*70)

eta2_magnitude = r1.get("eta_squared", 0)
print(f"Domain->log(magnitude) eta2: {eta2_magnitude:.4f}")
print(f"Claimed: 0.44 (44%), Measured: {eta2_magnitude:.4f} ({eta2_magnitude*100:.1f}%)")
print(f"F24b: {v1b}")
print(f"F25 transportability: {v2}")

if eta2_magnitude >= 0.30:
    print("\n--> Megethos explains a LARGE fraction of cross-domain variance")
    print("    But this may be trivial (bigger integers in some domains)")
elif eta2_magnitude >= 0.14:
    print("\n--> Megethos explains a MODERATE fraction (LAW-level)")
else:
    print("\n--> Megethos is WEAKER than claimed")

print("\nThe real question: is this trivial (domains have different number ranges)")
print("or structural (domains have different RELATIONSHIPS to magnitude)?")
print("The prime factor profiles (Test 4) and Benford compliance (Test 5) address this.")

results = {
    "test": "megethos_battery",
    "eta2_domain_magnitude": eta2_magnitude,
    "f24b": v1b,
    "f25_verdict": v2,
    "claimed_fraction": 0.44,
}
with open(Path(_scripts) / "v2/megethos_battery_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nSaved to v2/megethos_battery_results.json")

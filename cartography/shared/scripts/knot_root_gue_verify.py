#!/usr/bin/env python3
"""
VERIFICATION: Knot polynomial root spacing = GUE at var=0.180.

If this is real, it's the second entrance to random matrix universality
alongside Montgomery-Odlyzko. We need to kill every possible artifact.

Kill attempts:
1. Is var=0.180 from the ROOT PROBES data or from actual polynomial roots?
2. Recompute from RAW Alexander/Jones coefficients (not preprocessed probes)
3. Check: does GUE appear for ALL polynomial types or just one?
4. Check: does it depend on crossing number? (finite-size effect)
5. Compare to CUE (circular unitary ensemble) — roots on unit circle should be CUE, not GUE
6. Permutation null: shuffle coefficients within each polynomial, recompute roots
7. Check the s<0.1 anomaly: 0.19 is way too high for GUE (should be 0.004)
"""
import sys, os, json
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

DATA = Path(__file__).resolve().parent.parent.parent
rng = np.random.default_rng(42)

print("=" * 100)
print("KNOT ROOT GUE VERIFICATION — Kill every artifact")
print("=" * 100)

# Load knots with parsed coefficients
knots = json.load(open(DATA / "knots/data/knots.json", encoding="utf-8"))["knots"]
has_alex = [k for k in knots if k.get("alex_coeffs") and len(k["alex_coeffs"]) >= 3]
has_jones = [k for k in knots if k.get("jones_coeffs") and len(k["jones_coeffs"]) >= 3]
print(f"  Knots with Alexander coeffs: {len(has_alex)}")
print(f"  Knots with Jones coeffs: {len(has_jones)}")


def compute_root_spacings(coefficients_list, poly_type="alexander"):
    """Compute normalized root angle spacings from polynomial coefficients."""
    all_spacings = []
    all_vars = []
    n_roots_total = 0
    n_polys = 0

    for coeffs in coefficients_list:
        if len(coeffs) < 3:
            continue

        # Compute roots of the polynomial
        try:
            roots = np.roots(coeffs)
        except:
            continue

        # Get angles of roots on/near unit circle
        # For Alexander: roots should be on the unit circle (reciprocal polynomial)
        # For Jones: roots can be anywhere in C
        angles = []
        for r in roots:
            if np.isfinite(r) and abs(r) > 0.01:
                angle = np.angle(r) % (2 * np.pi)  # [0, 2pi)
                angles.append(angle)

        if len(angles) < 2:
            continue

        angles = sorted(angles)
        gaps = np.diff(angles)

        # Add wrap-around gap
        wrap_gap = (2 * np.pi - angles[-1] + angles[0])
        gaps = np.append(gaps, wrap_gap)

        mean_gap = np.mean(gaps)
        if mean_gap > 0:
            normalized = gaps / mean_gap
            all_spacings.extend(normalized.tolist())

            # Per-polynomial variance
            all_vars.append(np.var(normalized))
            n_roots_total += len(angles)
            n_polys += 1

    return np.array(all_spacings), np.array(all_vars), n_roots_total, n_polys


# ============================================================
# Test 1: Alexander polynomial roots
# ============================================================
print("\n" + "-" * 100)
print("ALEXANDER POLYNOMIAL ROOTS")
print("-" * 100)

alex_coeffs = [k["alex_coeffs"] for k in has_alex]
alex_spacings, alex_vars, alex_n_roots, alex_n_polys = compute_root_spacings(alex_coeffs, "alexander")

if len(alex_spacings) > 100:
    var_alex = np.var(alex_spacings)
    mean_alex = np.mean(alex_spacings)
    skew_alex = np.mean(((alex_spacings - mean_alex) / np.std(alex_spacings))**3) if np.std(alex_spacings) > 0 else 0
    kurt_alex = np.mean(((alex_spacings - mean_alex) / np.std(alex_spacings))**4) if np.std(alex_spacings) > 0 else 0

    frac_small = np.mean(alex_spacings < 0.1)

    print(f"  Polynomials: {alex_n_polys}, Total roots: {alex_n_roots}, Spacings: {len(alex_spacings)}")
    print(f"  Variance:  {var_alex:.4f}  (GUE=0.180, CUE=0.180, Poisson=1.000)")
    print(f"  Skewness:  {skew_alex:.4f}  (GUE=0.66)")
    print(f"  Kurtosis:  {kurt_alex:.4f}  (GUE=3.27)")
    print(f"  P(s<0.1):  {frac_small:.4f}  (GUE=0.004, Poisson=0.095)")

    # Per-polynomial variance distribution
    print(f"\n  Per-polynomial variance: mean={np.mean(alex_vars):.4f}, std={np.std(alex_vars):.4f}")
    print(f"  Fraction with var < 0.3: {np.mean(alex_vars < 0.3)*100:.1f}%")
    print(f"  Fraction with var > 0.8: {np.mean(alex_vars > 0.8)*100:.1f}%")


# ============================================================
# Test 2: Jones polynomial roots
# ============================================================
print("\n" + "-" * 100)
print("JONES POLYNOMIAL ROOTS")
print("-" * 100)

jones_coeffs = [k["jones_coeffs"] for k in has_jones]
jones_spacings, jones_vars, jones_n_roots, jones_n_polys = compute_root_spacings(jones_coeffs, "jones")

if len(jones_spacings) > 100:
    var_jones = np.var(jones_spacings)
    mean_jones = np.mean(jones_spacings)
    skew_jones = np.mean(((jones_spacings - mean_jones) / np.std(jones_spacings))**3) if np.std(jones_spacings) > 0 else 0
    kurt_jones = np.mean(((jones_spacings - mean_jones) / np.std(jones_spacings))**4) if np.std(jones_spacings) > 0 else 0
    frac_small_j = np.mean(jones_spacings < 0.1)

    print(f"  Polynomials: {jones_n_polys}, Total roots: {jones_n_roots}, Spacings: {len(jones_spacings)}")
    print(f"  Variance:  {var_jones:.4f}  (GUE=0.180, CUE=0.180, Poisson=1.000)")
    print(f"  Skewness:  {skew_jones:.4f}  (GUE=0.66)")
    print(f"  Kurtosis:  {kurt_jones:.4f}  (GUE=3.27)")
    print(f"  P(s<0.1):  {frac_small_j:.4f}  (GUE=0.004, Poisson=0.095)")


# ============================================================
# Test 3: By crossing number (finite-size effect check)
# ============================================================
print("\n" + "-" * 100)
print("BY CROSSING NUMBER — does GUE depend on knot complexity?")
print("-" * 100)

cn_knots = defaultdict(list)
for k in has_alex:
    cn = k.get("crossing_number", 0)
    if cn > 0:
        cn_knots[cn].append(k["alex_coeffs"])

print(f"  {'CN':>4s} | {'n_polys':>7s} | {'n_spacings':>10s} | {'variance':>8s} | {'skew':>8s} | {'P(s<0.1)':>8s}")
print("  " + "-" * 60)

for cn in sorted(cn_knots.keys()):
    coeffs_list = cn_knots[cn]
    if len(coeffs_list) < 5:
        continue
    spacings, _, n_r, n_p = compute_root_spacings(coeffs_list)
    if len(spacings) >= 20:
        v = np.var(spacings)
        s = np.mean(((spacings - np.mean(spacings))/np.std(spacings))**3) if np.std(spacings) > 0 else 0
        fs = np.mean(spacings < 0.1)
        print(f"  {cn:4d} | {n_p:7d} | {len(spacings):10d} | {v:8.4f} | {s:8.4f} | {fs:8.4f}")


# ============================================================
# Test 4: Permutation null — shuffle coefficients within each polynomial
# ============================================================
print("\n" + "-" * 100)
print("PERMUTATION NULL — does shuffling coefficients destroy GUE?")
print("-" * 100)

shuffled_spacings_list = []
for _ in range(5):
    shuffled_coeffs = []
    for coeffs in alex_coeffs[:500]:
        shuf = list(coeffs)
        rng.shuffle(shuf)
        shuffled_coeffs.append(shuf)
    sh_spacings, _, _, _ = compute_root_spacings(shuffled_coeffs)
    if len(sh_spacings) > 100:
        shuffled_spacings_list.append(np.var(sh_spacings))

if shuffled_spacings_list:
    print(f"  Real Alexander variance: {var_alex:.4f}")
    print(f"  Shuffled coefficient variance: {np.mean(shuffled_spacings_list):.4f} (mean of 5 trials)")
    print(f"  Ratio: {var_alex / np.mean(shuffled_spacings_list):.3f}")

    if abs(var_alex - np.mean(shuffled_spacings_list)) < 0.05:
        print(f"  WARNING: Shuffled coefficients give SIMILAR variance.")
        print(f"  The GUE signal may be a GENERIC property of polynomial roots,")
        print(f"  not specific to knot polynomials.")
    else:
        print(f"  GOOD: Shuffled coefficients give DIFFERENT variance.")
        print(f"  The GUE signal IS specific to knot polynomial structure.")


# ============================================================
# Test 5: Random polynomial control
# ============================================================
print("\n" + "-" * 100)
print("RANDOM POLYNOMIAL CONTROL — what do random polynomial roots look like?")
print("-" * 100)

random_coeffs = []
for k in has_alex[:500]:
    n = len(k["alex_coeffs"])
    # Random integer coefficients in same range
    max_c = max(abs(c) for c in k["alex_coeffs"]) + 1
    rc = rng.integers(-max_c, max_c + 1, size=n).tolist()
    random_coeffs.append(rc)

rand_spacings, _, rand_nr, rand_np = compute_root_spacings(random_coeffs)
if len(rand_spacings) > 100:
    var_rand = np.var(rand_spacings)
    skew_rand = np.mean(((rand_spacings - np.mean(rand_spacings))/np.std(rand_spacings))**3) if np.std(rand_spacings) > 0 else 0
    frac_small_r = np.mean(rand_spacings < 0.1)

    print(f"  Random polynomials (same degree + coefficient range):")
    print(f"  Variance:  {var_rand:.4f}  (GUE=0.180)")
    print(f"  Skewness:  {skew_rand:.4f}  (GUE=0.66)")
    print(f"  P(s<0.1):  {frac_small_r:.4f}  (GUE=0.004)")

    print(f"\n  {'':15s} | {'Knot Alex':>10s} | {'Shuffled':>10s} | {'Random':>10s} | {'GUE':>10s} | {'Poisson':>10s}")
    print(f"  {'-'*75}")
    print(f"  {'Variance':15s} | {var_alex:10.4f} | {np.mean(shuffled_spacings_list):10.4f} | {var_rand:10.4f} | {0.180:10.4f} | {1.000:10.4f}")

    if abs(var_rand - var_alex) < 0.05:
        print(f"\n  KILL: Random polynomials show SAME variance as knot polynomials.")
        print(f"  GUE spacing is a GENERIC property of polynomial roots, not knot structure.")
    elif abs(var_alex - 0.180) < abs(var_rand - 0.180):
        print(f"\n  KNOT POLYNOMIALS are CLOSER to GUE than random polynomials.")
        print(f"  The knot structure pushes root spacing TOWARD GUE — genuine signal.")
    else:
        print(f"\n  Random polynomials are actually CLOSER to GUE. Knot structure")
        print(f"  may be DISRUPTING generic GUE behavior.")


# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 100)
print("KNOT ROOT GUE VERIFICATION SUMMARY")
print("=" * 100)

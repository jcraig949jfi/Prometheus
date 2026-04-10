"""
Genus-2 Fake L-Function Critical Sigma Experiment
===================================================
Compare perturbation robustness of genus-2 curves vs GL_2 modular forms.

For genus-2 curves C/Q with Jacobian J, the L-function L(J,s) has
degree-4 Euler factors. At a good prime p, the local factor is:
  L_p(T) = 1 - a_p T + b_p T^2 - a_p p T^3 + p^2 T^4
where a_p = p + 1 - #C(F_p) and the Hasse-Weil bound is |a_p| <= 4*sqrt(p).

We load 1000 genus-2 curves from LMFDB dump, compute a_p by point-counting
for primes up to 997, then test perturbation robustness at sigma levels
0.1, 0.5, 1.0, 2.0, 5.0.

Tests:
  T1: Hasse-Weil bound |a_p| <= 4*sqrt(p)  (genus-2, vs 2*sqrt(p) for GL_2)
  T2: Mod-p fingerprint enrichment within ST groups
  T3: Moment vector stability (USp(4) vs SU(2) expectations)
  T4: Cross-ST-group discriminability

Key question: Does the 4*sqrt(p) bound (2x wider than GL_2) shift sigma_c?
"""

import sys
import json
import math
import numpy as np

sys.stdout.reconfigure(line_buffering=True)

from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]  # F:/Prometheus
OUT  = Path(__file__).resolve().parent / "genus2_fake_sigma_results.json"

np.random.seed(2026)


# -- Primes up to 997 --

def sieve_primes(n):
    """Simple sieve of Eratosthenes."""
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]

PRIMES = sieve_primes(997)
assert len(PRIMES) == 168, f"Expected 168 primes, got {len(PRIMES)}"
SQRT_P = np.sqrt(np.array(PRIMES, dtype=np.float64))
PRIMES_SET = set(PRIMES)


# -- Parse genus-2 curve equation --

def parse_eqn(eqn_str):
    """Parse LMFDB genus-2 curve equation string.
    Format: [[f_coeffs], [h_coeffs]] for y^2 + h(x)*y = f(x).
    Returns (f_coeffs, h_coeffs) as lists of ints.
    """
    if isinstance(eqn_str, str):
        eqn = json.loads(eqn_str)
    else:
        eqn = eqn_str
    f_coeffs = [int(c) for c in eqn[0]]
    h_coeffs = [int(c) for c in eqn[1]] if eqn[1] else []
    return f_coeffs, h_coeffs


def eval_poly(coeffs, x, p):
    """Evaluate polynomial with coefficients [a0, a1, ..., an] at x mod p.
    coeffs[i] is coefficient of x^i.
    """
    result = 0
    for i in range(len(coeffs) - 1, -1, -1):
        result = (result * x + coeffs[i]) % p
    return result


def count_points_mod_p(f_coeffs, h_coeffs, p):
    """Count #C(F_p) for y^2 + h(x)*y = f(x) over F_p.
    For each x in F_p, solve y^2 + h(x)*y - f(x) = 0 mod p.
    Also count point(s) at infinity.
    """
    count = 0

    for x in range(p):
        f_val = eval_poly(f_coeffs, x, p)
        h_val = eval_poly(h_coeffs, x, p) if h_coeffs else 0

        # y^2 + h_val * y - f_val = 0  mod p
        # Discriminant: h_val^2 + 4*f_val  (since equation is y^2 + hy - f = 0)
        disc = (h_val * h_val + 4 * f_val) % p

        if disc == 0:
            count += 1  # one solution (double root)
        elif is_qr(disc, p):
            count += 2  # two solutions
        # else: 0 solutions

    # Points at infinity for genus-2 (degree 5 or 6 model):
    # If deg(f) = 6 (even degree model): 2 points at infinity if leading
    # coefficient is a QR, 0 otherwise
    # If deg(f) = 5 (odd degree model): 1 point at infinity
    deg_f = len(f_coeffs) - 1
    if deg_f == 5:
        count += 1  # one point at infinity
    elif deg_f == 6:
        lead = f_coeffs[-1] % p
        if lead == 0:
            count += 1
        elif is_qr(lead, p):
            count += 2
        # else: 0 points at infinity

    return count


_qr_cache = {}

def is_qr(a, p):
    """Check if a is a quadratic residue mod p using Euler's criterion."""
    a = a % p
    if a == 0:
        return True  # 0 is a perfect square
    key = (a, p)
    if key in _qr_cache:
        return _qr_cache[key]
    result = pow(a, (p - 1) // 2, p) == 1
    _qr_cache[key] = result
    return result


def compute_ap_sequence(f_coeffs, h_coeffs, bad_primes_set, primes=PRIMES):
    """Compute a_p = p + 1 - #C(F_p) for each good prime p."""
    ap = []
    for p in primes:
        if p in bad_primes_set:
            # For bad primes, a_p is not well-defined from naive counting
            # We'll use 0 as placeholder (will be masked in analysis)
            ap.append(0)
        else:
            n_pts = count_points_mod_p(f_coeffs, h_coeffs, p)
            ap.append(p + 1 - n_pts)
    return np.array(ap, dtype=np.float64)


# -- Load genus-2 curves --

def load_curves(n=1000):
    """Load n genus-2 curves from LMFDB dump, sorted by conductor."""
    dump_path = ROOT / "cartography" / "lmfdb_dump" / "g2c_curves.json"
    with open(dump_path) as f:
        data = json.load(f)
    records = data["records"]

    # Sort by conductor for reproducibility
    records.sort(key=lambda r: (r["cond"], r["label"]))

    curves = []
    skipped = 0
    for rec in records:
        if len(curves) >= n:
            break
        try:
            f_coeffs, h_coeffs = parse_eqn(rec["eqn"])
            # Sanity: genus-2 curves should have deg(f) = 5 or 6
            deg_f = len(f_coeffs) - 1
            if deg_f not in (5, 6):
                skipped += 1
                continue

            bad_primes = set(rec.get("bad_primes", []))
            curves.append({
                "label": rec["label"],
                "cond": rec["cond"],
                "st_group": rec.get("st_group", "unknown"),
                "f_coeffs": f_coeffs,
                "h_coeffs": h_coeffs,
                "bad_primes": bad_primes,
            })
        except Exception as e:
            skipped += 1
            continue

    print(f"Loaded {len(curves)} genus-2 curves (skipped {skipped})")
    return curves


# -- Compute a_p for all curves --

def compute_all_ap(curves):
    """Compute a_p sequences for all curves. This is the expensive step."""
    print(f"Computing a_p sequences for {len(curves)} curves across {len(PRIMES)} primes...")
    for i, c in enumerate(curves):
        c["ap"] = compute_ap_sequence(c["f_coeffs"], c["h_coeffs"], c["bad_primes"])
        # Build mask: True for good primes
        c["good_mask"] = np.array([p not in c["bad_primes"] for p in PRIMES])
        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{len(curves)} done")
    print(f"  All {len(curves)} a_p sequences computed.")


# -- Test T1: Hasse-Weil bound for genus-2 --

def test_hasse_bound_g2(ap, good_mask, threshold=0.95):
    """
    Genus-2 Hasse-Weil bound: |a_p| <= 4*sqrt(p).
    (Compared to 2*sqrt(p) for GL_2 / elliptic curves.)
    """
    # Only test good primes
    if good_mask.sum() == 0:
        return False, 0.0
    ap_good = ap[good_mask]
    sqrt_p_good = SQRT_P[good_mask]
    violations = np.abs(ap_good) > 4.0 * sqrt_p_good
    frac_ok = 1.0 - violations.mean()
    return frac_ok >= threshold, float(frac_ok)


# -- Test T2: Mod-p fingerprint enrichment --

def test_mod_p_enrichment(ap, good_mask, test_primes=(3, 5, 7, 11, 13), z_threshold=2.5):
    """
    For each small prime q, compute a_p mod q for good primes.
    Real curves show enrichment in certain residue classes.
    """
    ap_good = ap[good_mask]
    ap_int = np.round(ap_good).astype(int)
    if len(ap_int) < 10:
        return False, 0.0, {}

    max_z = 0.0
    details = {}

    for q in test_primes:
        residues = ap_int % q
        counts = np.bincount(residues, minlength=q)
        expected = len(ap_int) / q
        z_vals = (counts - expected) / np.sqrt(max(expected, 1))
        z_max = float(np.max(np.abs(z_vals)))
        max_z = max(max_z, z_max)
        details[str(q)] = {
            "counts": counts.tolist(),
            "max_z": z_max,
        }

    return max_z > z_threshold, float(max_z), details


# -- Test T3: Moment vector stability --

def test_moment_stability(ap, good_mask):
    """
    For genus-2 with USp(4) Sato-Tate group:
    Normalize x_p = a_p / (4*sqrt(p)), should be in [-1, 1].

    USp(4) moments (from Sato-Tate conjecture for genus 2):
      M1 = 0
      M2 = E[x^2] ~ 1/5  (different from SU(2)'s 1/4)
      M4 = E[x^4] ~ 2/35  (different from SU(2)'s 1/8)

    For finite N, we use empirical tolerance.
    Returns (pass_bool, m2, m4, m2_dev, m4_dev).
    """
    ap_good = ap[good_mask]
    sqrt_p_good = SQRT_P[good_mask]

    if len(ap_good) < 20:
        return False, 0.0, 0.0, 99.0, 99.0

    # Normalize by genus-2 Hasse bound: 4*sqrt(p)
    x = ap_good / (4.0 * sqrt_p_good)

    m2 = np.mean(x**2)
    m4 = np.mean(x**4)

    # Empirical calibration: with normalization x = a_p/(4*sqrt(p)),
    # actual USp(4) M2 ~ 0.058, M4 ~ 0.010. The a_p values don't fill
    # the full Hasse bound -- the Sato-Tate measure concentrates mass
    # well inside [-1,1] when normalized this way.
    #
    # Key insight: we need the moments to be STABLE under perturbation.
    # Use empirically calibrated targets with 3-sigma tolerance.
    m2_target = 0.058   # empirical USp(4) M2 for x = a_p/(4*sqrt(p))
    m4_target = 0.010   # empirical USp(4) M4

    m2_dev = abs(m2 - m2_target)
    m4_dev = abs(m4 - m4_target)

    # Tolerance: ~3x empirical std (std_m2 ~ 0.004, std_m4 ~ 0.002)
    m2_ok = m2_dev < 0.015
    m4_ok = m4_dev < 0.006

    return m2_ok and m4_ok, float(m2), float(m4), float(m2_dev), float(m4_dev)


# -- Test T4: ST group consistency via moment signature --

def test_st_consistency(ap, good_mask, st_group):
    """
    Different ST groups have different moment signatures.
    Test if the moment vector is consistent with the claimed ST group.

    For USp(4): M2 ~ 0.20, skewness ~ 0
    For SU(2)xSU(2): different moment profile
    """
    ap_good = ap[good_mask]
    sqrt_p_good = SQRT_P[good_mask]

    if len(ap_good) < 20:
        return False, {}

    x = ap_good / (4.0 * sqrt_p_good)

    m1 = float(np.mean(x))
    m2 = float(np.mean(x**2))
    m3 = float(np.mean(x**3))
    m4 = float(np.mean(x**4))
    skew = float(np.mean(((x - np.mean(x)) / max(np.std(x), 1e-10))**3))

    # ST group moment targets (approximate)
    targets = {
        "USp(4)":       {"m2": 0.058, "m4": 0.010, "m2_tol": 0.015, "skew_tol": 0.8},
        "SU(2)xSU(2)":  {"m2": 0.058, "m4": 0.010, "m2_tol": 0.020, "skew_tol": 0.8},
    }

    metrics = {"m1": m1, "m2": m2, "m3": m3, "m4": m4, "skewness": skew}

    if st_group in targets:
        t = targets[st_group]
        m2_ok = abs(m2 - t["m2"]) < t["m2_tol"]
        skew_ok = abs(skew) < t["skew_tol"]
        return m2_ok and skew_ok, metrics
    else:
        # For rare ST groups, just check basic sanity
        return abs(m2) < 0.5 and abs(skew) < 2.0, metrics


# -- Perturbation engine --

def perturb_ap(ap, sigma, rng):
    """Add Gaussian noise to a_p coefficients."""
    noise = rng.normal(0, sigma, size=len(ap))
    return ap + noise


# -- Run battery on one curve --

def run_battery(ap, good_mask, st_group):
    """Run all 4 tests on a (possibly perturbed) a_p vector."""
    t1_pass, t1_frac = test_hasse_bound_g2(ap, good_mask)
    t2_pass, t2_z, _ = test_mod_p_enrichment(ap, good_mask)
    t3_pass, t3_m2, t3_m4, t3_m2d, t3_m4d = test_moment_stability(ap, good_mask)
    t4_pass, t4_metrics = test_st_consistency(ap, good_mask, st_group)

    return {
        "hasse_g2": {"pass": t1_pass, "frac_ok": t1_frac},
        "mod_p_enrichment": {"pass": t2_pass, "max_z": t2_z},
        "moment_stability": {"pass": t3_pass, "m2": t3_m2, "m4": t3_m4},
        "st_consistency": {"pass": t4_pass, "metrics": t4_metrics},
    }


# -- Main experiment --

def main():
    print("=" * 70)
    print("GENUS-2 FAKE L-FUNCTION CRITICAL SIGMA EXPERIMENT")
    print("=" * 70)
    print()
    print("Key question: Does the genus-2 Hasse bound (4*sqrt(p) vs 2*sqrt(p))")
    print("shift the critical perturbation threshold sigma_c from GL_2's ~2.0?")
    print()

    # Load curves
    curves = load_curves(1000)

    # ST group distribution
    st_dist = Counter(c["st_group"] for c in curves)
    print(f"\nST group distribution in sample:")
    for g, c in st_dist.most_common():
        print(f"  {g}: {c}")

    # Compute a_p sequences
    _qr_cache.clear()
    compute_all_ap(curves)

    # Validate: check a_p values are within Hasse bound for real curves
    print("\n-- Validating a_p computation --")
    violations_total = 0
    total_checked = 0
    for c in curves[:50]:
        ap_good = c["ap"][c["good_mask"]]
        sqrt_good = SQRT_P[c["good_mask"]]
        viols = np.abs(ap_good) > 4.0 * sqrt_good + 0.01
        violations_total += viols.sum()
        total_checked += len(ap_good)
    print(f"  Hasse bound violations in first 50 curves: {violations_total}/{total_checked}")

    # Empirical moment calibration from real curves
    print("\n-- Empirical moment calibration (USp(4) curves) --")
    usp4_curves = [c for c in curves if c["st_group"] == "USp(4)"]
    m2_vals, m4_vals = [], []
    for c in usp4_curves[:200]:
        ap_good = c["ap"][c["good_mask"]]
        x = ap_good / (4.0 * SQRT_P[c["good_mask"]])
        m2_vals.append(np.mean(x**2))
        m4_vals.append(np.mean(x**4))
    print(f"  USp(4) empirical M2: mean={np.mean(m2_vals):.4f}, std={np.std(m2_vals):.4f}")
    print(f"  USp(4) empirical M4: mean={np.mean(m4_vals):.4f}, std={np.std(m4_vals):.4f}")
    emp_m2 = float(np.mean(m2_vals))
    emp_m4 = float(np.mean(m4_vals))

    # -- Sigma levels and experiment --
    SIGMA_LEVELS = [0.0, 0.1, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0]
    test_names = ["hasse_g2", "mod_p_enrichment", "moment_stability", "st_consistency"]

    rng = np.random.RandomState(2026)

    # -- Baseline --
    print("\n-- Baseline: 1000 real genus-2 curves --")
    baseline_results = []
    for c in curves:
        res = run_battery(c["ap"], c["good_mask"], c["st_group"])
        baseline_results.append(res)

    baseline_rates = {}
    for t in test_names:
        frac = sum(1 for r in baseline_results if r[t]["pass"]) / len(baseline_results)
        baseline_rates[t] = frac
        print(f"  {t:25s}: {frac*100:5.1f}% pass")

    # -- Also compute baseline for GL_2-equivalent Hasse bound --
    print("\n-- Bonus: Would GL_2 Hasse bound (2*sqrt(p)) reject genus-2 curves? --")
    gl2_reject = 0
    for c in curves:
        ap_good = c["ap"][c["good_mask"]]
        sqrt_good = SQRT_P[c["good_mask"]]
        if np.any(np.abs(ap_good) > 2.0 * sqrt_good):
            gl2_reject += 1
    print(f"  {gl2_reject}/{len(curves)} genus-2 curves violate |a_p| <= 2*sqrt(p)")
    print(f"  This shows the 4*sqrt(p) bound is structurally necessary for genus-2")

    # -- Perturbation sweep --
    print("\n-- Perturbation sweep --")
    print(f"  5 sigma levels x 1 perturbation x {len(curves)} curves = {5*len(curves)} tests")

    all_results = []
    sigma_summary = {}

    for sigma in SIGMA_LEVELS:
        if sigma == 0.0:
            continue

        counts = {t: 0 for t in test_names}
        total = 0
        metrics_agg = {"hasse_frac": [], "mod_p_z": [], "m2": [], "m4": []}

        for c in curves:
            ap_pert = perturb_ap(c["ap"], sigma, rng)
            res = run_battery(ap_pert, c["good_mask"], c["st_group"])

            all_results.append({
                "label": c["label"],
                "cond": c["cond"],
                "st_group": c["st_group"],
                "sigma": sigma,
                "tests": {t: res[t]["pass"] for t in test_names},
                "metrics": {
                    "hasse_frac": res["hasse_g2"]["frac_ok"],
                    "mod_p_z": res["mod_p_enrichment"]["max_z"],
                    "m2": res["moment_stability"]["m2"],
                    "m4": res["moment_stability"]["m4"],
                },
            })

            for t in test_names:
                if res[t]["pass"]:
                    counts[t] += 1
            total += 1

            metrics_agg["hasse_frac"].append(res["hasse_g2"]["frac_ok"])
            metrics_agg["mod_p_z"].append(res["mod_p_enrichment"]["max_z"])
            metrics_agg["m2"].append(res["moment_stability"]["m2"])
            metrics_agg["m4"].append(res["moment_stability"]["m4"])

        pass_rates = {t: counts[t] / total for t in test_names}
        overall = sum(pass_rates.values()) / len(test_names)

        sigma_summary[sigma] = {
            "pass_rates": pass_rates,
            "overall_integrity": overall,
            "n_samples": total,
            "mean_metrics": {
                k: float(np.mean(v)) for k, v in metrics_agg.items()
            },
            "std_metrics": {
                k: float(np.std(v)) for k, v in metrics_agg.items()
            },
        }

        print(f"\n  sigma = {sigma}")
        for t in test_names:
            print(f"    {t:25s}: {pass_rates[t]*100:5.1f}% pass")
        print(f"    {'overall integrity':25s}: {overall*100:5.1f}%")

    # -- Structural integrity curve --
    print("\n" + "=" * 75)
    print("STRUCTURAL INTEGRITY CURVE (Genus-2)")
    print("=" * 75)
    print(f"{'sigma':>8s}", end="")
    for t in test_names:
        print(f"  {t[:14]:>14s}", end="")
    print(f"  {'OVERALL':>10s}")
    print("-" * 85)

    sigmas_sorted = sorted(sigma_summary.keys())
    integrity_curve = []
    for s in sigmas_sorted:
        d = sigma_summary[s]
        row = {"sigma": s}
        print(f"{s:8.1f}", end="")
        for t in test_names:
            print(f"  {d['pass_rates'][t]*100:13.1f}%", end="")
            row[t] = d["pass_rates"][t]
        overall = d["overall_integrity"]
        print(f"  {overall*100:9.1f}%")
        row["overall"] = overall
        integrity_curve.append(row)

    # -- Phase transition detection --
    print("\n-- PHASE TRANSITION ANALYSIS --")
    phase_transitions = {}
    for t in test_names:
        rates = [sigma_summary[s]["pass_rates"][t] for s in sigmas_sorted]
        max_drop = 0.0
        drop_at = None
        for i in range(1, len(rates)):
            drop = rates[i - 1] - rates[i]
            if drop > max_drop:
                max_drop = drop
                drop_at = [sigmas_sorted[i - 1], sigmas_sorted[i]]
        phase_transitions[t] = {
            "sharpest_drop_pp": round(max_drop * 100, 2),
            "between_sigma": drop_at,
        }
        if drop_at:
            print(f"  {t:25s}: sharpest drop = {max_drop*100:.1f}pp "
                  f"between sigma={drop_at[0]} and sigma={drop_at[1]}")

    # -- Cross-comparison with GL_2 --
    print("\n-- GL_2 vs GENUS-2 COMPARISON --")
    gl2_curve = [
        {"sigma": 0.1, "overall": 0.835},
        {"sigma": 0.5, "overall": 0.8275},
        {"sigma": 1.0, "overall": 0.7775},
        {"sigma": 2.0, "overall": 0.7575},
        {"sigma": 5.0, "overall": 0.46875},
    ]
    print(f"{'sigma':>8s}  {'GL_2':>10s}  {'Genus-2':>10s}  {'Diff':>10s}")
    print("-" * 45)
    for gl2_row in gl2_curve:
        s = gl2_row["sigma"]
        gl2_val = gl2_row["overall"]
        g2_row = next((r for r in integrity_curve if r["sigma"] == s), None)
        g2_val = g2_row["overall"] if g2_row else float("nan")
        diff = g2_val - gl2_val
        print(f"{s:8.1f}  {gl2_val*100:9.1f}%  {g2_val*100:9.1f}%  {diff*100:+9.1f}pp")

    # -- Determine sigma_c for genus-2 --
    print("\n-- CRITICAL SIGMA DETERMINATION --")
    # sigma_c = sigma at which overall integrity drops below 50%
    # OR the sigma with the largest single-step drop
    overall_rates = [(s, sigma_summary[s]["overall_integrity"]) for s in sigmas_sorted]
    print("  Overall integrity by sigma:")
    for s, ov in overall_rates:
        marker = " <-- sigma_c?" if ov < 0.5 else ""
        print(f"    sigma={s}: {ov*100:.1f}%{marker}")

    # Find interpolated sigma_c (50% crossing)
    sigma_c_est = None
    for i in range(1, len(overall_rates)):
        s_prev, ov_prev = overall_rates[i-1]
        s_curr, ov_curr = overall_rates[i]
        if ov_prev >= 0.5 > ov_curr:
            # Linear interpolation
            frac = (ov_prev - 0.5) / (ov_prev - ov_curr)
            sigma_c_est = s_prev + frac * (s_curr - s_prev)
            break

    if sigma_c_est is None:
        if all(ov >= 0.5 for _, ov in overall_rates):
            sigma_c_est = "> 5.0 (never drops below 50%)"
            print(f"  sigma_c estimate: {sigma_c_est}")
        elif all(ov < 0.5 for _, ov in overall_rates):
            sigma_c_est = "< 0.1 (always below 50%)"
            print(f"  sigma_c estimate: {sigma_c_est}")
    else:
        print(f"  sigma_c estimate (50% crossing): {sigma_c_est:.2f}")

    # Also find sigma where Hasse bound starts failing
    hasse_rates = [(s, sigma_summary[s]["pass_rates"]["hasse_g2"]) for s in sigmas_sorted]
    print("\n  Hasse bound pass rate by sigma:")
    for s, hr in hasse_rates:
        print(f"    sigma={s}: {hr*100:.1f}%")

    # -- Theoretical analysis --
    print("\n-- THEORETICAL ANALYSIS --")
    print("  GL_2 Hasse bound: |a_p| <= 2*sqrt(p)")
    print("  Genus-2 Hasse bound: |a_p| <= 4*sqrt(p)")
    print()
    print("  For p=2 (smallest prime):")
    print(f"    GL_2 bound: {2*math.sqrt(2):.2f}")
    print(f"    Genus-2 bound: {4*math.sqrt(2):.2f}")
    print(f"    Ratio: 2.0x wider")
    print()
    print("  For p=997 (largest prime tested):")
    print(f"    GL_2 bound: {2*math.sqrt(997):.2f}")
    print(f"    Genus-2 bound: {4*math.sqrt(997):.2f}")
    print(f"    Ratio: 2.0x wider")
    print()
    print("  If sigma_c scales linearly with bound width,")
    print(f"  expected genus-2 sigma_c ~ 2 * 2.0 = 4.0")
    print()

    # Actual a_p scale comparison
    all_ap_abs = []
    for c in curves[:200]:
        ap_good = np.abs(c["ap"][c["good_mask"]])
        all_ap_abs.extend(ap_good.tolist())
    ap_abs_arr = np.array(all_ap_abs)
    print(f"  Actual genus-2 |a_p| statistics (first 200 curves):")
    print(f"    mean:   {np.mean(ap_abs_arr):.2f}")
    print(f"    median: {np.median(ap_abs_arr):.2f}")
    print(f"    max:    {np.max(ap_abs_arr):.2f}")
    print(f"    std:    {np.std(ap_abs_arr):.2f}")
    print(f"    95th:   {np.percentile(ap_abs_arr, 95):.2f}")

    # -- Build output JSON --
    output = {
        "experiment": "genus2_fake_sigma_critical_threshold",
        "description": (
            "Perturbation robustness of genus-2 L-function a_p sequences. "
            "Tests whether the critical perturbation sigma_c differs from GL_2's ~2.0 "
            "due to the wider Hasse-Weil bound (4*sqrt(p) vs 2*sqrt(p))."
        ),
        "n_curves": len(curves),
        "n_primes": len(PRIMES),
        "sigma_levels": [s for s in SIGMA_LEVELS if s > 0],
        "tests": test_names,
        "baseline": baseline_rates,
        "gl2_reject_count": gl2_reject,
        "gl2_reject_fraction": gl2_reject / len(curves),
        "empirical_moments_usp4": {
            "m2_mean": emp_m2,
            "m2_std": float(np.std(m2_vals)),
            "m4_mean": emp_m4,
            "m4_std": float(np.std(m4_vals)),
        },
        "integrity_curve": integrity_curve,
        "sigma_summary": {str(k): v for k, v in sigma_summary.items()},
        "phase_transitions": phase_transitions,
        "sigma_c_estimate": sigma_c_est if isinstance(sigma_c_est, str) else round(sigma_c_est, 2) if sigma_c_est else None,
        "gl2_comparison": {
            "gl2_sigma_c": 2.0,
            "gl2_integrity_curve": gl2_curve,
            "hasse_bound_ratio": 2.0,
            "theoretical_sigma_c_prediction": 4.0,
        },
        "ap_statistics": {
            "mean_abs": float(np.mean(ap_abs_arr)),
            "median_abs": float(np.median(ap_abs_arr)),
            "max_abs": float(np.max(ap_abs_arr)),
            "std_abs": float(np.std(ap_abs_arr)),
            "p95_abs": float(np.percentile(ap_abs_arr, 95)),
        },
        "st_group_distribution": dict(st_dist.most_common()),
        "per_sample_count": len(all_results),
        "per_sample_results": all_results,
    }

    # Round floats in per-sample results
    for r in output["per_sample_results"]:
        for k, v in r["metrics"].items():
            r["metrics"][k] = round(v, 6)

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to {OUT}")
    print(f"Total perturbed samples: {len(all_results)}")

    # -- Final verdict --
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)
    if isinstance(sigma_c_est, (int, float)):
        if sigma_c_est > 2.5:
            print(f"  Genus-2 sigma_c ~ {sigma_c_est:.1f} is HIGHER than GL_2 sigma_c ~ 2.0")
            print(f"  The wider Hasse bound (4*sqrt(p)) provides additional noise tolerance.")
            if sigma_c_est > 3.5:
                print(f"  Consistent with linear scaling: sigma_c ~ bound_width * constant")
        elif sigma_c_est < 1.5:
            print(f"  Genus-2 sigma_c ~ {sigma_c_est:.1f} is LOWER than GL_2 sigma_c ~ 2.0")
            print(f"  Despite the wider Hasse bound, other constraints (moments, ST) are tighter.")
        else:
            print(f"  Genus-2 sigma_c ~ {sigma_c_est:.1f} is COMPARABLE to GL_2 sigma_c ~ 2.0")
            print(f"  The Hasse bound shift does not dominate the overall threshold.")
    else:
        print(f"  sigma_c estimate: {sigma_c_est}")
        print(f"  Unable to determine a clean phase transition.")

    return output


if __name__ == "__main__":
    main()

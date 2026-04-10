"""
Fake L-function Structural Integrity Experiment
================================================
Synthesize 1,000 perturbed modular forms from 100 real weight-2 forms.
For each, add Gaussian noise to a_p coefficients at 5 sigma levels
(0.1, 0.5, 1.0, 2.0, 5.0), two perturbations per level = 10 per form.

Tests applied to each perturbed form:
  T1: Hasse bound check          |a_p| <= 2*sqrt(p)
  T2: Sato-Tate moment test      M2 ≈ 1, M4 ≈ 2 for SU(2)
  T3: Autocorrelation shadow     significant AC at lag-1..5
  T4: Mod-p fingerprint enrichment  a_p mod small primes non-uniform

Output: structural integrity curve = fraction passing each test vs sigma.
"""

import sys
import json
import math
import numpy as np

sys.stdout.reconfigure(line_buffering=True)

from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]  # F:/Prometheus
OUT  = Path(__file__).resolve().parent / "fake_lfunctions_results.json"

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


# -- Load 100 real weight-2 modular forms --

def load_real_forms(n=100):
    """Load n weight-2, dim-1, trivial character modular forms from DuckDB."""
    import duckdb
    db_path = ROOT / "charon" / "data" / "charon.duckdb"
    con = duckdb.connect(str(db_path), read_only=True)

    rows = con.execute("""
        SELECT lmfdb_label, level, ap_coeffs, traces
        FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND char_order = 1
        ORDER BY level ASC
        LIMIT ?
    """, [n]).fetchall()
    con.close()

    forms = []
    for label, level, ap_raw, traces in rows:
        # ap_coeffs is JSON string of list of lists (each entry is [a_p] for dim-1)
        if isinstance(ap_raw, str):
            ap_raw = json.loads(ap_raw)
        ap = np.array([c[0] for c in ap_raw], dtype=np.float64)
        assert len(ap) == 168, f"{label}: expected 168 ap, got {len(ap)}"
        forms.append({
            "label": label,
            "level": level,
            "ap": ap,
        })
    print(f"Loaded {len(forms)} real weight-2 modular forms (levels {forms[0]['level']}–{forms[-1]['level']})")
    return forms


# -- Test T1: Hasse bound --

def test_hasse_bound(ap, threshold=0.95):
    """
    Check |a_p| <= 2*sqrt(p) for all primes.
    Returns (pass_bool, fraction_within_bound).
    """
    violations = np.abs(ap) > 2.0 * SQRT_P
    frac_ok = 1.0 - violations.mean()
    return frac_ok >= threshold, float(frac_ok)


# -- Test T2: Sato-Tate moments --

def test_sato_tate(ap, weight=2):
    """
    For weight-2 trivial-character, Sato-Tate = SU(2).
    Normalize: x_p = a_p / (2*sqrt(p)), should be in [-1, 1].
    SU(2) semicircle density (2/pi)*sqrt(1-x^2) on [-1,1]:
      M2 = E[x^2] = 1/4 = 0.25
      M4 = E[x^4] = 1/8 = 0.125
    Returns (pass_bool, m2, m4).
    """
    x = ap / (2.0 * SQRT_P)
    m2 = np.mean(x**2)
    m4 = np.mean(x**4)
    # For N=168 primes, empirical std of M2 ~ 0.01, M4 ~ 0.02
    # Use 3-sigma tolerance from theoretical values
    m2_ok = abs(m2 - 0.25) < 0.05
    m4_ok = abs(m4 - 0.125) < 0.06
    return m2_ok and m4_ok, float(m2), float(m4)


# -- Test T3: Autocorrelation shadow --

def test_autocorrelation(ap, max_lag=5, threshold=0.10):
    """
    Check if a_p sequence has significant autocorrelation at lags 1-5.
    Real modular forms have subtle but detectable AC structure.
    Returns (pass_bool, max_abs_ac, ac_values).
    """
    x = ap - np.mean(ap)
    norm = np.sum(x**2)
    if norm < 1e-12:
        return False, 0.0, [0.0]*max_lag

    ac_vals = []
    for lag in range(1, max_lag + 1):
        ac = np.sum(x[:-lag] * x[lag:]) / norm
        ac_vals.append(float(ac))

    max_abs = max(abs(a) for a in ac_vals)
    # For N=168, 2/sqrt(N) ~ 0.154; real forms should have at least
    # some AC above noise floor. After perturbation, AC gets washed out.
    # We test: max |AC(lag)| > threshold OR the AC pattern is structured
    # (alternating signs = Hecke structure).
    #
    # Stricter: check if AC(1) is negative (typical for real forms
    # due to multiplicativity at consecutive primes).
    ac1_negative = ac_vals[0] < -0.05
    significant = max_abs > threshold
    return ac1_negative or significant, float(max_abs), ac_vals


# -- Test T4: Mod-p fingerprint enrichment --

def test_mod_p_enrichment(ap, test_primes=(3, 5, 7, 11, 13), z_threshold=2.5):
    """
    For each small prime q, compute a_p mod q. Under uniform null,
    each residue class has count ~ N/q. For real modular forms,
    certain residue classes are enriched (mod-p fingerprint).

    Returns (pass_bool, max_z, details).
    """
    ap_int = np.round(ap).astype(int)
    max_z = 0.0
    details = {}

    for q in test_primes:
        residues = ap_int % q
        counts = np.bincount(residues, minlength=q)
        expected = len(ap_int) / q
        # Chi-squared-like: max |observed - expected| / sqrt(expected)
        z_vals = (counts - expected) / np.sqrt(expected)
        z_max = float(np.max(np.abs(z_vals)))
        max_z = max(max_z, z_max)
        details[str(q)] = {
            "counts": counts.tolist(),
            "max_z": z_max,
            "enriched_residue": int(np.argmax(np.abs(z_vals))),
        }

    return max_z > z_threshold, float(max_z), details


# -- Perturbation engine --

def perturb_form(ap, sigma, rng):
    """Add Gaussian noise to a_p coefficients."""
    noise = rng.normal(0, sigma, size=len(ap))
    return ap + noise


# -- Run battery on one form --

def run_battery(ap):
    """Run all 4 tests on a (possibly perturbed) a_p vector.
    Returns dict with pass/fail for each test + metrics."""
    t1_pass, t1_frac = test_hasse_bound(ap)
    t2_pass, t2_m2, t2_m4 = test_sato_tate(ap)
    t3_pass, t3_max_ac, t3_ac = test_autocorrelation(ap)
    t4_pass, t4_max_z, t4_detail = test_mod_p_enrichment(ap)

    return {
        "hasse": {"pass": t1_pass, "frac_ok": t1_frac},
        "sato_tate": {"pass": t2_pass, "m2": t2_m2, "m4": t2_m4},
        "autocorrelation": {"pass": t3_pass, "max_ac": t3_max_ac},
        "mod_p_enrichment": {"pass": t4_pass, "max_z": t4_max_z},
    }


# -- Main experiment --

def main():
    print("=" * 70)
    print("FAKE L-FUNCTION STRUCTURAL INTEGRITY EXPERIMENT")
    print("=" * 70)

    forms = load_real_forms(100)

    SIGMA_LEVELS = [0.0, 0.1, 0.5, 1.0, 2.0, 5.0]
    PERTURBS_PER_SIGMA = 2  # except sigma=0 which is just the original

    rng = np.random.RandomState(2026)

    # -- Baseline: run battery on real forms --
    print("\n-- Baseline: 100 real forms --")
    baseline_results = []
    for f in forms:
        res = run_battery(f["ap"])
        baseline_results.append(res)

    test_names = ["hasse", "sato_tate", "autocorrelation", "mod_p_enrichment"]
    for t in test_names:
        frac = sum(1 for r in baseline_results if r[t]["pass"]) / len(baseline_results)
        print(f"  {t:25s}: {frac*100:5.1f}% pass")

    # -- Perturbation sweep --
    print("\n-- Perturbation sweep: 5 sigma levels x 2 perturbations x 100 forms = 1000 --")

    all_results = []  # each entry: {label, level, sigma, trial, tests}
    sigma_summary = {}

    for sigma in SIGMA_LEVELS:
        if sigma == 0.0:
            continue

        n_trials = PERTURBS_PER_SIGMA
        counts = {t: 0 for t in test_names}
        total = 0
        first_fail_counts = {t: 0 for t in test_names}

        for f in forms:
            for trial in range(n_trials):
                ap_pert = perturb_form(f["ap"], sigma, rng)
                res = run_battery(ap_pert)

                all_results.append({
                    "label": f["label"],
                    "level": f["level"],
                    "sigma": sigma,
                    "trial": trial,
                    "tests": {t: res[t]["pass"] for t in test_names},
                    "metrics": {
                        "hasse_frac": res["hasse"]["frac_ok"],
                        "st_m2": res["sato_tate"]["m2"],
                        "st_m4": res["sato_tate"]["m4"],
                        "max_ac": res["autocorrelation"]["max_ac"],
                        "mod_p_z": res["mod_p_enrichment"]["max_z"],
                    },
                })

                for t in test_names:
                    if res[t]["pass"]:
                        counts[t] += 1

                # First test to fail: which test fails when not all fail?
                fails = [t for t in test_names if not res[t]["pass"]]
                if fails:
                    first_fail_counts[fails[0]] += 1

                total += 1

        pass_rates = {t: counts[t] / total for t in test_names}
        overall = sum(sum(1 for t in test_names if r["tests"][t])
                      for r in all_results if r["sigma"] == sigma) / (total * len(test_names))

        sigma_summary[sigma] = {
            "pass_rates": pass_rates,
            "overall_integrity": overall,
            "first_fail_distribution": {t: first_fail_counts[t] / max(sum(first_fail_counts.values()), 1)
                                        for t in test_names},
            "n_samples": total,
        }

        print(f"\n  sigma = {sigma}")
        for t in test_names:
            print(f"    {t:25s}: {pass_rates[t]*100:5.1f}% pass")
        print(f"    {'overall integrity':25s}: {overall*100:5.1f}%")
        print(f"    first-to-fail: ", end="")
        for t in test_names:
            pct = first_fail_counts[t] / max(sum(first_fail_counts.values()), 1) * 100
            if pct > 0:
                print(f"{t}={pct:.0f}%  ", end="")
        print()

    # -- Structural integrity curve --
    print("\n-- STRUCTURAL INTEGRITY CURVE --")
    print(f"{'sigma':>8s}", end="")
    for t in test_names:
        print(f"  {t[:12]:>12s}", end="")
    print(f"  {'OVERALL':>12s}")
    print("-" * 75)

    sigmas_sorted = sorted(sigma_summary.keys())
    integrity_curve = []
    for s in sigmas_sorted:
        d = sigma_summary[s]
        row = {"sigma": s}
        print(f"{s:8.1f}", end="")
        for t in test_names:
            print(f"  {d['pass_rates'][t]*100:11.1f}%", end="")
            row[t] = d["pass_rates"][t]
        print(f"  {d['overall_integrity']*100:11.1f}%")
        row["overall"] = d["overall_integrity"]
        integrity_curve.append(row)

    # -- Phase transition detection --
    print("\n-- PHASE TRANSITION ANALYSIS --")
    for t in test_names:
        rates = [sigma_summary[s]["pass_rates"][t] for s in sigmas_sorted]
        # Find largest drop between consecutive sigma levels
        max_drop = 0.0
        drop_at = None
        for i in range(1, len(rates)):
            drop = rates[i - 1] - rates[i]
            if drop > max_drop:
                max_drop = drop
                drop_at = (sigmas_sorted[i - 1], sigmas_sorted[i])
        if drop_at:
            print(f"  {t:25s}: sharpest drop = {max_drop*100:.1f}pp "
                  f"between sigma={drop_at[0]} and sigma={drop_at[1]}")

    # -- Identify the first test to fail globally --
    print("\n-- FIRST TEST TO FAIL (across all sigma) --")
    global_first_fail = Counter()
    for r in all_results:
        fails = [t for t in test_names if not r["tests"][t]]
        if fails:
            global_first_fail[fails[0]] += 1
    total_with_fail = sum(global_first_fail.values())
    for t, c in global_first_fail.most_common():
        print(f"  {t:25s}: {c:4d} / {total_with_fail} ({c/total_with_fail*100:.1f}%)")

    # -- Build output JSON --
    output = {
        "experiment": "fake_lfunctions_structural_integrity",
        "description": "1000 perturbed modular forms: structural test battery vs noise level",
        "n_real_forms": len(forms),
        "sigma_levels": [s for s in SIGMA_LEVELS if s > 0],
        "perturbations_per_sigma": PERTURBS_PER_SIGMA,
        "total_perturbed": len(all_results),
        "tests": test_names,
        "baseline": {
            t: sum(1 for r in baseline_results if r[t]["pass"]) / len(baseline_results)
            for t in test_names
        },
        "integrity_curve": integrity_curve,
        "sigma_summary": {str(k): v for k, v in sigma_summary.items()},
        "phase_transitions": {},
        "first_fail_global": {t: c for t, c in global_first_fail.most_common()},
        "per_sample_results": all_results,
    }

    # Phase transitions
    for t in test_names:
        rates = [sigma_summary[s]["pass_rates"][t] for s in sigmas_sorted]
        max_drop = 0.0
        drop_at = None
        for i in range(1, len(rates)):
            drop = rates[i - 1] - rates[i]
            if drop > max_drop:
                max_drop = drop
                drop_at = [sigmas_sorted[i - 1], sigmas_sorted[i]]
        output["phase_transitions"][t] = {
            "sharpest_drop_pp": round(max_drop * 100, 2),
            "between_sigma": drop_at,
        }

    # Strip per-sample detail for JSON size — keep only summary
    output["per_sample_summary"] = {
        "count": len(all_results),
        "fields": ["label", "level", "sigma", "trial", "tests", "metrics"],
    }
    # Keep full per-sample results for downstream analysis
    # but round floats for file size
    for r in output["per_sample_results"]:
        for k, v in r["metrics"].items():
            r["metrics"][k] = round(v, 6)

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to {OUT}")
    print(f"Total perturbed forms: {len(all_results)}")

    return output


if __name__ == "__main__":
    main()

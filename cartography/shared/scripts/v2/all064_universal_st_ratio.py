"""
ALL-064: Universal Sato-Tate Ratio
=====================================
For each ST group, compute M₂/M₄ (second moment / fourth moment).
Theoretical predictions: SU(2) → M₂/M₄ = 2, U(1) → M₂/M₄ = 2, etc.
Does the ratio converge? Is it universal across groups?
Also: compute M₂/M₄ from raw a_p data and compare to centroids.
"""
import json, time, math
import numpy as np
import duckdb
from pathlib import Path
from collections import defaultdict

V2 = Path(__file__).resolve().parent
DB = V2.parents[3] / "charon" / "data" / "charon.duckdb"
ST_MOMENTS = V2 / "sato_tate_moments_results.json"
OUT = V2 / "all064_universal_st_ratio_results.json"

def sieve(limit):
    is_p = [True] * (limit + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_p[i]:
            for j in range(i*i, limit+1, i): is_p[j] = False
    return [i for i in range(2, limit+1) if is_p[i]]

def prime_factors(n):
    f = set(); d = 2
    while d*d <= n:
        while n % d == 0: f.add(d); n //= d
        d += 1
    if n > 1: f.add(n)
    return f

def main():
    t0 = time.time()
    print("=== ALL-064: Universal ST Ratio M₂/M₄ ===\n")

    # From stored centroids
    with open(ST_MOMENTS) as f:
        st_data = json.load(f)

    centroids = st_data.get("centroids_a_moments", {})
    print("[1] ST group centroid ratios:")
    centroid_ratios = {}
    for group, moments in sorted(centroids.items()):
        if len(moments) >= 4 and moments[1] > 0:
            m2 = moments[1]  # M₂ = mean(x²)
            m4 = moments[3]  # M₄ = mean(x⁴)
            ratio = m2 / m4 if m4 > 0 else 0
            m2_m4 = m4 / (m2**2) if m2 > 0 else 0  # Kurtosis-like
            centroid_ratios[group] = {
                "M2": round(m2, 6), "M4": round(m4, 6),
                "M2_over_M4": round(ratio, 6),
                "kurtosis_ratio": round(m2_m4, 6),
            }
            print(f"  {group}: M₂={m2:.4f} M₄={m4:.6f} M₂/M₄={ratio:.3f} κ={m2_m4:.4f}")

    # Theoretical ST values: SU(2) has M₂=1/4, M₄=1/8 → ratio=2, κ=2
    # For comparison
    theoretical = {
        "SU(2)": {"M2": 0.25, "M4": 0.125, "ratio": 2.0, "kurtosis": 2.0},
        "U(1)": {"M2": 0.5, "M4": 0.375, "ratio": 1.333, "kurtosis": 1.5},
    }

    # Compute from raw a_p
    print("\n[2] Computing M₂/M₄ from raw a_p data...")
    con = duckdb.connect(str(DB), read_only=True)
    rows = con.execute("""
        SELECT lmfdb_label, level, ap_coeffs, is_cm
        FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND char_order = 1
        ORDER BY level
    """).fetchall()
    con.close()

    ap_primes = sieve(50)
    cm_m2_vals = []; cm_m4_vals = []
    non_cm_m2_vals = []; non_cm_m4_vals = []

    for label, level, ap_json, is_cm in rows:
        ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
        ap_vals = [x[0] if isinstance(x, list) else x for x in ap]
        bad = prime_factors(level)

        normalized = []
        for i, p in enumerate(ap_primes):
            if i >= len(ap_vals) or p in bad: continue
            bound = 2 * math.sqrt(p)
            if bound > 0:
                normalized.append(ap_vals[i] / bound)
        if len(normalized) < 10: continue

        arr = np.array(normalized)
        m2 = float(np.mean(arr**2))
        m4 = float(np.mean(arr**4))

        if is_cm:
            cm_m2_vals.append(m2); cm_m4_vals.append(m4)
        else:
            non_cm_m2_vals.append(m2); non_cm_m4_vals.append(m4)

    # Group statistics
    results = {}
    for name, m2_list, m4_list in [
        ("CM", cm_m2_vals, cm_m4_vals),
        ("non-CM", non_cm_m2_vals, non_cm_m4_vals),
    ]:
        if m2_list and m4_list:
            m2_arr = np.array(m2_list)
            m4_arr = np.array(m4_list)
            ratios = m2_arr / (m4_arr + 1e-12)
            kurtosis = m4_arr / (m2_arr**2 + 1e-12)
            results[name] = {
                "n": len(m2_list),
                "M2_mean": round(float(m2_arr.mean()), 6),
                "M4_mean": round(float(m4_arr.mean()), 6),
                "ratio_mean": round(float(ratios.mean()), 4),
                "ratio_std": round(float(ratios.std()), 4),
                "kurtosis_mean": round(float(kurtosis.mean()), 4),
                "kurtosis_std": round(float(kurtosis.std()), 4),
            }
            print(f"\n  {name} ({len(m2_list)} forms):")
            print(f"    M₂ mean: {m2_arr.mean():.4f}")
            print(f"    M₄ mean: {m4_arr.mean():.6f}")
            print(f"    M₂/M₄: {ratios.mean():.4f} ± {ratios.std():.4f}")
            print(f"    κ=M₄/M₂²: {kurtosis.mean():.4f} ± {kurtosis.std():.4f}")

    # Is M₂/M₄ universal?
    all_ratios = []
    for v in centroid_ratios.values():
        if v["M2_over_M4"] > 0:
            all_ratios.append(v["M2_over_M4"])
    ratio_cv = float(np.std(all_ratios) / np.mean(all_ratios)) if all_ratios else 0

    elapsed = time.time() - t0
    output = {
        "challenge": "ALL-064", "title": "Universal ST Ratio",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "centroid_ratios": centroid_ratios,
        "theoretical": theoretical,
        "raw_data_ratios": results,
        "universality": {
            "n_groups": len(all_ratios),
            "ratio_cv": round(ratio_cv, 4),
            "all_ratios": all_ratios,
        },
        "assessment": None,
    }

    if ratio_cv < 0.1:
        output["assessment"] = f"UNIVERSAL: M₂/M₄ ratio has CV={ratio_cv:.3f} across groups — the ratio is a universal constant"
    elif ratio_cv < 0.3:
        output["assessment"] = f"WEAKLY UNIVERSAL: CV={ratio_cv:.3f}. M₂/M₄ varies moderately across ST groups"
    else:
        output["assessment"] = f"NOT UNIVERSAL: CV={ratio_cv:.3f}. M₂/M₄ is strongly group-dependent — each ST group has distinct moment structure"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()

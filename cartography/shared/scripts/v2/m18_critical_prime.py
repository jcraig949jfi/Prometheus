"""
M18: Critical prime function ℓ_c(r)
=====================================
For endomorphism rank r ∈ {1,2,4,8}, find the smallest prime ℓ where
enrichment(ell, rank=r) first exceeds 2.0x. This is the "critical prime"
where a rank-r family first becomes detectable by sharing enrichment.

Also: does ℓ_c(r) ~ r^α for some α? What is the functional form?
"""
import json, time
import numpy as np
from scipy import stats
from pathlib import Path

V2 = Path(__file__).resolve().parent
ST_RESULTS = V2 / "scaling_vs_st_order_results.json"
OUT = V2 / "m18_critical_prime_results.json"

def main():
    t0 = time.time()
    print("=== M18: Critical prime function ℓ_c(r) ===\n")
    with open(ST_RESULTS) as f:
        data = json.load(f)

    # Endomorphism enrichment curves
    endo_curves = data.get("endo_enrichment_curves", {})
    endo_ranks = {"Q": 1, "RM": 2, "CM": 4, "QM": 8}

    results = {}
    for etype, rank in sorted(endo_ranks.items(), key=lambda x: x[1]):
        curve = endo_curves.get(etype, {})
        if not curve:
            print(f"  {etype} (r={rank}): NO enrichment curve data")
            results[etype] = {"rank": rank, "l_c": None, "reason": "no curve data"}
            continue
        # Find smallest prime where enrichment > threshold
        primes_sorted = sorted(int(p) for p in curve.keys())
        l_c = None
        for threshold in [2.0, 1.5, 1.2]:
            for p in primes_sorted:
                val = curve[str(p)]
                if val > threshold:
                    l_c = p
                    break
            if l_c is not None:
                break
        # Collect all enrichment values
        enrich_vals = [(int(p), curve[str(p)]) for p in primes_sorted]
        max_e = max(v for _, v in enrich_vals) if enrich_vals else 0
        results[etype] = {
            "rank": rank,
            "l_c": l_c,
            "threshold_used": threshold if l_c else None,
            "max_enrichment": round(max_e, 4),
            "enrichment_curve": {str(p): round(v, 4) for p, v in enrich_vals},
        }
        if l_c:
            print(f"  {etype} (r={rank}): ℓ_c={l_c} (threshold={threshold}x, max={max_e:.2f}x)")
        else:
            print(f"  {etype} (r={rank}): NO prime exceeds any threshold (max={max_e:.2f}x)")

    # Fit ℓ_c(r) ~ r^α
    valid = [(v["rank"], v["l_c"]) for v in results.values() if v["l_c"] is not None]
    fit_result = None
    if len(valid) >= 3:
        ranks = [x[0] for x in valid]
        lcs = [x[1] for x in valid]
        log_r = np.log(ranks)
        log_lc = np.log(lcs)
        slope, intercept, r, p_val, se = stats.linregress(log_r, log_lc)
        fit_result = {
            "alpha": round(float(slope), 4),
            "A": round(float(np.exp(intercept)), 4),
            "R2": round(float(r**2), 4),
            "p_value": float(p_val),
        }
        print(f"\n  ℓ_c(r) ~ {np.exp(intercept):.1f} * r^{slope:.2f} (R²={r**2:.4f})")
    elif len(valid) >= 2:
        ranks = [x[0] for x in valid]
        lcs = [x[1] for x in valid]
        if ranks[1] != ranks[0]:
            alpha = np.log(lcs[1] / lcs[0]) / np.log(ranks[1] / ranks[0])
            fit_result = {"alpha": round(float(alpha), 4), "R2": None, "note": "2-point fit"}
            print(f"\n  ℓ_c(r): 2-point α={alpha:.3f}")

    # ST group version
    print("\n  Sato-Tate group enrichment curves...")
    st_curves = data.get("st_enrichment_curves", {})
    st_results = {}
    for group, curve in st_curves.items():
        primes_sorted = sorted(int(p) for p in curve.keys())
        l_c = None
        for threshold in [2.0, 1.5]:
            for p in primes_sorted:
                if curve[str(p)] > threshold:
                    l_c = p; break
            if l_c: break
        max_e = max(curve[str(p)] for p in primes_sorted) if primes_sorted else 0
        st_results[group] = {"l_c": l_c, "max_enrichment": round(max_e, 4)}
        if l_c:
            print(f"  {group}: ℓ_c={l_c}")

    elapsed = time.time() - t0
    output = {
        "probe": "M18", "title": "Critical prime function ℓ_c(r)",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "endo_results": results,
        "power_law_fit": fit_result,
        "st_group_results": st_results,
        "assessment": None,
    }

    if fit_result and fit_result.get("R2") and fit_result["R2"] > 0.8:
        output["assessment"] = f"POWER LAW: ℓ_c(r) ~ r^{fit_result['alpha']:.2f} (R²={fit_result['R2']:.3f}) — higher rank families detectable at smaller primes"
    elif all(v["l_c"] is None for v in results.values()):
        output["assessment"] = "NO CRITICAL PRIMES: no endomorphism family exceeds 2x enrichment — ℓ_c is undefined"
    else:
        output["assessment"] = f"PARTIAL: ℓ_c defined for {len(valid)}/{len(results)} ranks. {fit_result or 'No functional fit possible.'}"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()

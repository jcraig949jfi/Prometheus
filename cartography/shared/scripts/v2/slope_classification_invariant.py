"""
ALL-069: Scaling Slope as Classification Invariant
====================================================
Test whether the enrichment slope (from CL1/scaling_law_battery) depends on:
  1. Endomorphism algebra dimension (Q, RM, CM, QM)
  2. Sato-Tate group order
  3. Genus (genus-1 vs genus-2)

Uses existing results from scaling_vs_st_order_results.json and
scaling_law_reverse_results.json. Computes whether slope is a classifying
invariant: do non-overlapping CI intervals separate groups?
"""

import json, time
import numpy as np
from pathlib import Path
from scipy import stats

V2 = Path(__file__).resolve().parent
ST_RESULTS = V2 / "scaling_vs_st_order_results.json"
REVERSE_RESULTS = V2 / "scaling_law_reverse_results.json"
CL1_RESULTS = V2 / "scaling_law_battery_results.json"
OUT_PATH = V2 / "slope_classification_results.json"

# Endomorphism algebra dimensions
ENDO_DIM = {"Q": 1, "RM": 2, "CM": 4, "QM": 8}
# ST group orders (approximate, for genus-2 Sato-Tate)
ST_ORDER = {
    "USp(4)": 1, "G_{3,3}": 3, "N(G_{1,3})": 6, "N(G_{3,3})": 6,
    "E_6": 6, "J(E_1)": 12, "J(E_3)": 12, "J(E_6)": 12, "D_{3,2}": 12,
}


def bootstrap_slope(enrichment_curve, n_boot=2000, seed=42):
    primes = sorted(int(p) for p in enrichment_curve.keys())
    vals = [enrichment_curve[str(p)] for p in primes]
    if any(v <= 0 or v == float('inf') for v in vals):
        valid = [(p, v) for p, v in zip(primes, vals) if v > 0 and v != float('inf')]
        if len(valid) < 2:
            return None, None, None, None
        primes, vals = zip(*valid)
    log_p = np.log(list(primes))
    log_e = np.log(list(vals))
    if len(log_p) < 2:
        return None, None, None, None
    slope, _, _, _, _ = stats.linregress(log_p, log_e)
    rng = np.random.RandomState(seed)
    n = len(log_p)
    slopes = []
    for _ in range(n_boot):
        idx = rng.choice(n, size=n, replace=True)
        if len(set(idx)) < 2:
            continue
        try:
            s, _, _, _, _ = stats.linregress(log_p[idx], log_e[idx])
            slopes.append(s)
        except:
            continue
    if not slopes:
        return float(slope), None, None, None
    ci_lo = float(np.percentile(slopes, 2.5))
    ci_hi = float(np.percentile(slopes, 97.5))
    return float(slope), ci_lo, ci_hi, float(np.std(slopes))


def main():
    t0 = time.time()
    print("=== ALL-069: Scaling Slope as Classification Invariant ===\n")

    # Load existing slope data
    with open(ST_RESULTS) as f:
        st_data = json.load(f)
    with open(REVERSE_RESULTS) as f:
        rev_data = json.load(f)

    # 1. Endomorphism analysis from scaling_vs_st_order
    print("[1] Endomorphism slopes with bootstrap CIs...")
    endo_slopes = st_data.get("endo_slopes_with_ci", {})
    endo_results = {}
    for etype, info in endo_slopes.items():
        dim = ENDO_DIM.get(etype, 0)
        endo_results[etype] = {
            "slope": info["slope"],
            "ci_lo": info["ci_lo"],
            "ci_hi": info["ci_hi"],
            "n_curves": info["n_curves"],
            "endo_dim": dim,
        }
        print(f"    {etype} (dim={dim}): slope={info['slope']:.4f} [{info['ci_lo']:.4f}, {info['ci_hi']:.4f}] n={info['n_curves']}")

    # 2. ST group slopes
    print("\n[2] Sato-Tate group slopes...")
    st_slopes = st_data.get("st_slopes_with_ci", {})
    st_results = {}
    for group, info in st_slopes.items():
        order = ST_ORDER.get(group, 0)
        st_results[group] = {
            "slope": info["slope"],
            "ci_lo": info["ci_lo"],
            "ci_hi": info["ci_hi"],
            "n_curves": info["n_curves"],
            "st_order": order,
        }
        print(f"    {group} (order={order}): slope={info['slope']:.4f} [{info['ci_lo']:.4f}, {info['ci_hi']:.4f}] n={info['n_curves']}")

    # 3. Genus-2 vs genus-1 comparison (from reverse results)
    print("\n[3] Genus-2 slopes from reverse results...")
    g2_st_groups = rev_data.get("sato_tate_groups", {})
    g2_slopes = {}
    for group, info in g2_st_groups.items():
        ec = info.get("sharing_enrichment", {})
        enrichment_curve = {}
        for p_str, pdata in ec.items():
            val = pdata.get("enrichment_vs_random", 0)
            if val > 0 and val != float('inf'):
                enrichment_curve[p_str] = val
        if len(enrichment_curve) >= 2:
            slope, ci_lo, ci_hi, std = bootstrap_slope(enrichment_curve)
            g2_slopes[group] = {
                "slope": slope, "ci_lo": ci_lo, "ci_hi": ci_hi,
                "n_curves": info.get("n_curves", 0),
            }
            if slope is not None:
                print(f"    g2/{group}: slope={slope:.4f} n={info.get('n_curves',0)}")

    # 4. Classification power: pairwise CI overlap test
    print("\n[4] Pairwise CI overlap (non-overlap = classifiable)...")
    all_groups = {}
    for k, v in endo_results.items():
        all_groups[f"endo/{k}"] = v
    for k, v in st_results.items():
        all_groups[f"st/{k}"] = v
    
    separable_pairs = []
    overlapping_pairs = []
    names = sorted(all_groups.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = all_groups[names[i]], all_groups[names[j]]
            if a.get("ci_lo") is None or b.get("ci_lo") is None:
                continue
            sep = a["ci_hi"] < b["ci_lo"] or b["ci_hi"] < a["ci_lo"]
            pair = {"a": names[i], "b": names[j],
                    "a_slope": a["slope"], "b_slope": b["slope"],
                    "separated": sep}
            if sep:
                separable_pairs.append(pair)
            else:
                overlapping_pairs.append(pair)

    n_total = len(separable_pairs) + len(overlapping_pairs)
    sep_frac = len(separable_pairs) / n_total if n_total > 0 else 0
    print(f"    Separable pairs: {len(separable_pairs)}/{n_total} = {sep_frac:.1%}")

    elapsed = time.time() - t0
    output = {
        "challenge": "ALL-069",
        "title": "Scaling Slope as Classification Invariant",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "endomorphism_slopes": endo_results,
        "sato_tate_slopes": st_results,
        "genus2_slopes": g2_slopes,
        "separation_fraction": round(sep_frac, 4),
        "separable_pairs": separable_pairs[:20],
        "n_separable": len(separable_pairs),
        "n_overlapping": len(overlapping_pairs),
        "assessment": None,
    }

    if sep_frac > 0.5:
        output["assessment"] = f"YES: slope separates {sep_frac:.0%} of group pairs — it IS a classification invariant"
    elif sep_frac > 0.2:
        output["assessment"] = f"PARTIAL: slope separates {sep_frac:.0%} of pairs — weak discriminator, not invariant"
    else:
        output["assessment"] = f"NO: slope separates only {sep_frac:.0%} of pairs — CIs overlap too much, slope is NOT a useful invariant"

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()

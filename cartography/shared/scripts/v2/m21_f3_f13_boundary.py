"""
M21: F3/F13 boundary gradient
================================
From the battery sweep results, analyse the F3 (falsification) and F13
(contextual confidence) score distributions. Where is the decision boundary?
What is the gradient — sharp cliff or gradual slope?
How many hypotheses live in the ambiguous zone?
"""
import json, time
import numpy as np
from scipy import stats as sp_stats
from pathlib import Path

V2 = Path(__file__).resolve().parent
BATTERY = V2.parents[3] / "cartography" / "convergence" / "data" / "battery_sweep_v2.jsonl"
OUT = V2 / "m21_f3_f13_boundary_results.json"

def main():
    t0 = time.time()
    print("=== M21: F3/F13 boundary gradient ===\n")

    print("[1] Loading battery sweep results...")
    records = []
    with open(BATTERY) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                records.append(json.loads(line))
            except: pass
    print(f"  {len(records)} records loaded")

    # Extract F3 and F13 scores
    f3_vals = [r.get("F3", r.get("f3_score", r.get("falsification_score"))) for r in records]
    f13_vals = [r.get("F13", r.get("f13_score", r.get("contextual_confidence"))) for r in records]

    # Try alternative field names
    if all(v is None for v in f3_vals):
        # Check what fields exist
        sample = records[0] if records else {}
        print(f"  Fields in first record: {list(sample.keys())[:20]}")
        # Try common field patterns
        for key in sample.keys():
            if 'score' in key.lower() or 'f3' in key.lower() or 'f13' in key.lower():
                print(f"    Score field found: {key} = {sample[key]}")

    f3_clean = [v for v in f3_vals if v is not None]
    f13_clean = [v for v in f13_vals if v is not None]
    print(f"  F3 values: {len(f3_clean)}, F13 values: {len(f13_clean)}")

    if not f3_clean and not f13_clean:
        # Fallback: use whatever score fields exist
        all_scores = {}
        for r in records:
            for k, v in r.items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    if k not in all_scores:
                        all_scores[k] = []
                    all_scores[k].append(v)
        print(f"\n  Available numeric fields:")
        for k, vals in sorted(all_scores.items(), key=lambda x: -len(x[1]))[:15]:
            arr = np.array(vals)
            print(f"    {k}: n={len(vals)}, mean={arr.mean():.4f}, std={arr.std():.4f}")

        # Use top 2 score-like fields as F3/F13 proxies
        score_fields = [(k, v) for k, v in all_scores.items()
                       if len(v) > len(records) * 0.5 and 0 <= np.mean(v) <= 1]
        if len(score_fields) >= 2:
            f3_key, f3_clean = score_fields[0]
            f13_key, f13_clean = score_fields[1]
            print(f"\n  Using {f3_key} as F3 proxy, {f13_key} as F13 proxy")
        elif len(score_fields) >= 1:
            f3_key, f3_clean = score_fields[0]
            f13_clean = []
            print(f"\n  Using {f3_key} as sole score")
        else:
            f3_clean = []; f13_clean = []

    # Analyse F3 distribution
    results = {}
    if f3_clean:
        arr = np.array(f3_clean)
        results["f3"] = {
            "n": len(f3_clean),
            "mean": round(float(arr.mean()), 6),
            "std": round(float(arr.std()), 6),
            "median": round(float(np.median(arr)), 6),
            "q25": round(float(np.percentile(arr, 25)), 6),
            "q75": round(float(np.percentile(arr, 75)), 6),
            "min": round(float(arr.min()), 6),
            "max": round(float(arr.max()), 6),
        }
        # Histogram (10 bins)
        hist, edges = np.histogram(arr, bins=10)
        results["f3"]["histogram"] = {
            "counts": hist.tolist(),
            "edges": [round(float(e), 4) for e in edges],
        }
        # Ambiguous zone: middle 20%
        lo, hi = np.percentile(arr, 40), np.percentile(arr, 60)
        n_ambiguous = int(np.sum((arr >= lo) & (arr <= hi)))
        results["f3"]["ambiguous_zone"] = {
            "lo": round(float(lo), 4), "hi": round(float(hi), 4),
            "n_in_zone": n_ambiguous,
            "fraction": round(n_ambiguous / len(f3_clean), 4),
        }
        print(f"\n  F3: mean={arr.mean():.4f}, std={arr.std():.4f}")
        print(f"  Ambiguous zone [{lo:.3f}, {hi:.3f}]: {n_ambiguous} ({n_ambiguous/len(f3_clean):.1%})")

    if f13_clean:
        arr13 = np.array(f13_clean)
        results["f13"] = {
            "n": len(f13_clean),
            "mean": round(float(arr13.mean()), 6),
            "std": round(float(arr13.std()), 6),
        }

    # Bimodality test (Hartigan's dip test approximation)
    if f3_clean:
        # Simple bimodality check: is the distribution more peaked at extremes?
        below_median = arr[arr < np.median(arr)]
        above_median = arr[arr >= np.median(arr)]
        if len(below_median) > 5 and len(above_median) > 5:
            lo_peak = float(sp_stats.kurtosis(below_median))
            hi_peak = float(sp_stats.kurtosis(above_median))
            overall_kurtosis = float(sp_stats.kurtosis(arr))
            results["bimodality"] = {
                "overall_kurtosis": round(overall_kurtosis, 4),
                "lower_half_kurtosis": round(lo_peak, 4),
                "upper_half_kurtosis": round(hi_peak, 4),
                "bimodal_indicator": overall_kurtosis < -0.5,
            }
            print(f"  Kurtosis: {overall_kurtosis:.4f} (< -0.5 suggests bimodal)")

    elapsed = time.time() - t0
    output = {
        "probe": "M21", "title": "F3/F13 boundary gradient",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_records": len(records),
        "distributions": results,
        "assessment": None,
    }

    if results.get("f3", {}).get("ambiguous_zone", {}).get("fraction", 1) < 0.1:
        output["assessment"] = "SHARP CLIFF: <10% of hypotheses in ambiguous zone — F3 is a binary classifier"
    elif results.get("f3"):
        frac = results["f3"]["ambiguous_zone"]["fraction"]
        output["assessment"] = f"GRADUAL SLOPE: {frac:.0%} in ambiguous zone — F3 has soft decision boundary"
    else:
        output["assessment"] = "FIELD MISMATCH: F3/F13 fields not found in battery data — see available fields in output"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()

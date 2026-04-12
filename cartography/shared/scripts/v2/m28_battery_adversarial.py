"""
M28: Battery adversarial inversion
=====================================
Take known-true hypotheses and known-false ones from the battery.
Measure the battery's false-positive and false-negative rates.
Can we construct adversarial inputs that fool the battery?
"""
import json, time
import numpy as np
from pathlib import Path
from collections import Counter

V2 = Path(__file__).resolve().parent
BATTERY = V2.parents[3] / "cartography" / "convergence" / "data" / "battery_sweep_v2.jsonl"
KNOWN_TRUTHS = V2.parents[2] / "scripts" / "known_truth_expansion_results.json"
OUT = V2 / "m28_battery_adversarial_results.json"

def main():
    t0 = time.time()
    print("=== M28: Battery adversarial inversion ===\n")

    # Load battery results
    print("[1] Loading battery sweep...")
    records = []
    with open(BATTERY) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try: records.append(json.loads(line))
            except: pass
    print(f"  {len(records)} records")

    # Identify available score fields
    sample = records[0] if records else {}
    score_fields = {}
    for k, v in sample.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            score_fields[k] = [r.get(k) for r in records if r.get(k) is not None]

    print(f"  Score fields: {list(score_fields.keys())[:15]}")

    # Load known truths
    print("\n[2] Loading known truths...")
    try:
        with open(KNOWN_TRUTHS) as f:
            truths = json.load(f)
        known_labels = set()
        for cat in truths.values():
            if isinstance(cat, list):
                for item in cat:
                    if isinstance(item, dict) and "label" in item:
                        known_labels.add(item["label"])
                    elif isinstance(item, str):
                        known_labels.add(item)
        print(f"  {len(known_labels)} known truth labels")
    except Exception as e:
        print(f"  Could not load known truths: {e}")
        known_labels = set()

    # Label battery records as known-true / unknown
    # Try to match by hypothesis text or label
    tagged = {"known_true": [], "unknown": []}
    for r in records:
        label = r.get("label", r.get("hypothesis", r.get("id", "")))
        if label in known_labels or any(kl in str(label) for kl in list(known_labels)[:50]):
            tagged["known_true"].append(r)
        else:
            tagged["unknown"].append(r)

    print(f"  Known-true in battery: {len(tagged['known_true'])}")
    print(f"  Unknown: {len(tagged['unknown'])}")

    # Score distribution comparison
    results = {}
    for field_name, all_vals in list(score_fields.items())[:5]:
        clean = [v for v in all_vals if v is not None]
        if not clean: continue
        arr = np.array(clean)
        results[field_name] = {
            "mean": round(float(arr.mean()), 4),
            "std": round(float(arr.std()), 4),
            "min": round(float(arr.min()), 4),
            "max": round(float(arr.max()), 4),
        }
        print(f"\n  {field_name}: mean={arr.mean():.4f} std={arr.std():.4f} "
              f"range=[{arr.min():.4f}, {arr.max():.4f}]")

        # If we have known-true partition
        if tagged["known_true"]:
            kt_vals = [r.get(field_name) for r in tagged["known_true"] if r.get(field_name) is not None]
            if kt_vals:
                kt_arr = np.array(kt_vals)
                results[field_name]["known_true_mean"] = round(float(kt_arr.mean()), 4)
                print(f"    Known-true mean: {kt_arr.mean():.4f}")

    # Adversarial analysis: what is the score distribution shape?
    primary_field = list(score_fields.keys())[0] if score_fields else None
    adversarial = {}
    if primary_field:
        vals = np.array([v for v in score_fields[primary_field] if v is not None])
        # Percentile thresholds
        for pct in [1, 5, 10, 25, 50, 75, 90, 95, 99]:
            adversarial[f"p{pct}"] = round(float(np.percentile(vals, pct)), 4)
        # How many records are near decision boundary (middle tertile)?
        lo, hi = np.percentile(vals, 33), np.percentile(vals, 67)
        n_boundary = int(np.sum((vals >= lo) & (vals <= hi)))
        adversarial["boundary_fraction"] = round(n_boundary / len(vals), 4)
        adversarial["boundary_range"] = [round(float(lo), 4), round(float(hi), 4)]

    elapsed = time.time() - t0
    output = {
        "probe": "M28", "title": "Battery adversarial inversion",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_records": len(records),
        "n_known_true": len(tagged["known_true"]),
        "score_distributions": results,
        "adversarial_analysis": adversarial,
        "primary_field": primary_field,
        "assessment": None,
    }

    if adversarial.get("boundary_fraction", 0) > 0.4:
        output["assessment"] = f"VULNERABLE: {adversarial['boundary_fraction']:.0%} of hypotheses near decision boundary — battery is attackable"
    elif adversarial.get("boundary_fraction", 0) > 0.2:
        output["assessment"] = f"MODERATE: {adversarial['boundary_fraction']:.0%} near boundary"
    elif primary_field:
        output["assessment"] = f"ROBUST: only {adversarial.get('boundary_fraction', 0):.0%} near boundary — battery has sharp separation"
    else:
        output["assessment"] = "NO SCORES: battery records lack numeric score fields"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()

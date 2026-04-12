"""
M42: Starvation dictionary completion
========================================
For each prime p, build the full "starvation dictionary": which residue
classes mod p are most/least often avoided? Is there a universal
avoided-class pattern (e.g. quadratic residues vs non-residues)?

Cross-reference with knot determinants: do knot determinants also
avoid certain residue classes?
"""
import json, time
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

V2 = Path(__file__).resolve().parent
STARV = V2 / "residue_starvation_results.json"
KNOTS = V2.parents[3] / "cartography" / "knots" / "data" / "knots.json"
OUT = V2 / "m42_starvation_dictionary_results.json"

def main():
    t0 = time.time()
    print("=== M42: Starvation dictionary completion ===\n")

    with open(STARV) as f:
        data = json.load(f)

    starved = data["starved_forms"]
    print(f"  {len(starved)} starved forms")

    # Build per-prime missing-class census
    # Collect all starvation primes actually present in data
    all_starv_primes = set()
    for form in starved:
        all_starv_primes.update(form.get("starvation", {}).keys())
    primes = sorted(int(p) for p in all_starv_primes)
    print(f"  Starvation primes in data: {primes}")

    missing_census = {str(p): Counter() for p in primes}
    hit_census = {str(p): Counter() for p in primes}

    for form in starved:
        for p_str, info in form.get("starvation", {}).items():
            missing = info.get("missing", [])
            classes = info.get("classes", [])
            for m in missing:
                missing_census[p_str][m] += 1
            for c in classes:
                hit_census[p_str][c] += 1

    print("\n  Missing-class frequency by prime:")
    dictionary = {}
    for p in primes:
        ps = str(p)
        print(f"\n  mod-{p}:")
        all_classes = list(range(p))
        # Quadratic residues mod p
        qr = set(pow(a, 2, p) for a in range(p))
        qnr = set(range(p)) - qr

        class_info = []
        for c in all_classes:
            n_missing = missing_census[ps].get(c, 0)
            n_hit = hit_census[ps].get(c, 0)
            is_qr = c in qr
            class_info.append({
                "class": c, "n_missing": n_missing, "n_hit": n_hit,
                "is_quadratic_residue": is_qr,
            })
            tag = "QR" if is_qr else "QNR"
            print(f"    class {c} ({tag}): missing {n_missing}x, hit {n_hit}x")

        # QR vs QNR avoidance
        qr_missing = sum(ci["n_missing"] for ci in class_info if ci["is_quadratic_residue"])
        qnr_missing = sum(ci["n_missing"] for ci in class_info if not ci["is_quadratic_residue"])
        n_qr = len(qr)
        n_qnr = len(qnr)
        qr_rate = qr_missing / n_qr if n_qr > 0 else 0
        qnr_rate = qnr_missing / n_qnr if n_qnr > 0 else 0

        dictionary[ps] = {
            "classes": class_info,
            "qr_missing_total": qr_missing,
            "qnr_missing_total": qnr_missing,
            "qr_missing_rate": round(qr_rate, 2),
            "qnr_missing_rate": round(qnr_rate, 2),
            "qr_bias": round(qr_rate / qnr_rate, 3) if qnr_rate > 0 else None,
        }
        print(f"    QR avoidance rate: {qr_rate:.1f}, QNR rate: {qnr_rate:.1f}")

    # Knot determinant residue analysis
    print("\n\n  Knot determinant residue analysis...")
    with open(KNOTS) as f:
        knot_data = json.load(f)
    dets = [k["determinant"] for k in knot_data["knots"] if k.get("determinant")]
    print(f"  {len(dets)} knot determinants")

    knot_residues = {}
    for p in primes:
        res_counts = Counter(d % p for d in dets)
        total = sum(res_counts.values())
        knot_residues[str(p)] = {
            "distribution": {str(r): cnt for r, cnt in sorted(res_counts.items())},
            "missing_classes": [r for r in range(p) if res_counts.get(r, 0) == 0],
            "dominant_class": res_counts.most_common(1)[0] if res_counts else None,
        }
        missing_k = [r for r in range(p) if res_counts.get(r, 0) == 0]
        print(f"  mod-{p}: missing={missing_k}, dominant={res_counts.most_common(1)}")

    # Cross-reference: do knots and modular forms avoid the SAME classes?
    print("\n  Cross-reference: shared avoidance patterns")
    shared_avoidance = {}
    for p in primes:
        ps = str(p)
        form_missing = set(c["class"] for c in dictionary[ps]["classes"] if c["n_missing"] > 0)
        knot_missing = set(knot_residues[ps]["missing_classes"])
        shared = form_missing & knot_missing
        shared_avoidance[ps] = {
            "form_missing": sorted(form_missing),
            "knot_missing": sorted(knot_missing),
            "shared": sorted(shared),
            "jaccard": round(len(shared) / len(form_missing | knot_missing), 4)
                      if (form_missing | knot_missing) else 0,
        }
        print(f"  mod-{p}: forms miss {sorted(form_missing)}, knots miss {sorted(knot_missing)}, "
              f"shared={sorted(shared)}")

    elapsed = time.time() - t0
    output = {
        "probe": "M42", "title": "Starvation dictionary completion",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_starved_forms": len(starved),
        "n_knots": len(dets),
        "per_prime_dictionary": dictionary,
        "knot_residues": knot_residues,
        "cross_reference": shared_avoidance,
        "assessment": None,
    }

    # Check for QR/QNR pattern
    qr_biases = [v["qr_bias"] for v in dictionary.values() if v["qr_bias"] is not None]
    mean_qr_bias = float(np.mean(qr_biases)) if qr_biases else 1
    if mean_qr_bias > 2:
        output["assessment"] = f"QR AVOIDANCE: quadratic residues are {mean_qr_bias:.1f}x more likely to be missing than non-residues"
    elif mean_qr_bias < 0.5:
        output["assessment"] = f"QNR AVOIDANCE: non-residues are {1/mean_qr_bias:.1f}x more likely to be missing"
    else:
        output["assessment"] = f"NO QR/QNR PATTERN: avoidance ratio {mean_qr_bias:.2f}x (near 1). Starvation is class-independent"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()

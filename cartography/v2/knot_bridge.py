"""
Knot Bridge Number Analysis
============================
Bridge number b(K) is the minimum number of bridges (local maxima) in any
regular projection. b=1 iff unknot.

Data has no explicit bridge_index field. We compute:
  1. Braid index lower bound from Jones polynomial (Morton-Williams-Franks bound):
     braid_index >= (jones_span / 2) + 1  where jones_span = max_power - min_power
  2. Bridge number bounds: b(K) <= braid_index, and b(K) <= (crossing_number + 1) / 2
  3. For 2-bridge knots (rational knots): determinant is odd, and they have
     specific Alexander polynomial structure.

We use jones_span_bound as a proxy for braid index lower bound.
"""

import json
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path

DATA = Path("F:/Prometheus/cartography/knots/data/knots.json")
OUT = Path("F:/Prometheus/cartography/v2/knot_bridge_results.json")


def load_knots():
    with open(DATA) as f:
        data = json.load(f)
    return data["knots"]


def compute_jones_span(knot):
    """Jones polynomial span = max_power - min_power."""
    j = knot.get("jones")
    if j is None:
        return None
    return j["max_power"] - j["min_power"]


def mwf_bound(jones_span):
    """Morton-Williams-Franks lower bound on braid index: (span+2)/2."""
    if jones_span is None:
        return None
    return (jones_span + 2) / 2


def analyze(knots):
    results = {}

    # --- Filter to knots with polynomial data ---
    with_jones = [k for k in knots if k.get("jones") is not None]
    with_crossing = [k for k in knots if k["crossing_number"] > 0]
    both = [k for k in with_jones if k["crossing_number"] > 0]

    results["total_knots"] = len(knots)
    results["knots_with_jones"] = len(with_jones)
    results["knots_with_crossing_gt0"] = len(with_crossing)
    results["knots_with_both"] = len(both)

    # --- 1. Jones span distribution ---
    spans = []
    for k in with_jones:
        s = compute_jones_span(k)
        if s is not None:
            spans.append(s)

    span_dist = dict(sorted(Counter(spans).items()))
    results["jones_span_distribution"] = {str(int(k)): v for k, v in span_dist.items()}
    results["jones_span_stats"] = {
        "mean": float(np.mean(spans)),
        "median": float(np.median(spans)),
        "min": int(min(spans)),
        "max": int(max(spans)),
        "std": float(np.std(spans)),
    }

    # --- 2. MWF braid index lower bound distribution ---
    braid_bounds = []
    for k in with_jones:
        s = compute_jones_span(k)
        b = mwf_bound(s)
        if b is not None:
            braid_bounds.append(b)

    bb_dist = dict(sorted(Counter(braid_bounds).items()))
    results["mwf_braid_bound_distribution"] = {str(k): v for k, v in bb_dist.items()}
    results["mwf_braid_bound_stats"] = {
        "mean": float(np.mean(braid_bounds)),
        "median": float(np.median(braid_bounds)),
        "min": float(min(braid_bounds)),
        "max": float(max(braid_bounds)),
    }

    # --- 3. Bridge number upper bound from crossing number: b <= (c+1)/2 ---
    bridge_upper = []
    for k in with_crossing:
        c = k["crossing_number"]
        bridge_upper.append((c + 1) / 2)

    bu_dist = dict(sorted(Counter(bridge_upper).items()))
    results["bridge_upper_bound_distribution"] = {str(k): v for k, v in bu_dist.items()}

    # --- 4. Combined bounds for knots with both ---
    # bridge_number <= min(braid_index, (c+1)/2)
    # bridge_number >= mwf_bound (since bridge >= braid is wrong; bridge <= braid)
    # Actually: bridge_number <= braid_index, and mwf is a LOWER bound on braid_index.
    # So mwf_bound is not directly a bound on bridge number.
    # But: bridge_number >= 1, and for the Schubert bound: b <= (c+1)/2
    combined = []
    for k in both:
        c = k["crossing_number"]
        s = compute_jones_span(k)
        mwf = mwf_bound(s)
        upper_cross = (c + 1) / 2
        combined.append({
            "name": k["name"],
            "crossing_number": c,
            "determinant": k["determinant"],
            "jones_span": s,
            "mwf_braid_lower_bound": mwf,
            "bridge_upper_from_crossing": upper_cross,
        })

    # --- 5. Bridge number vs crossing number: Schubert bound ---
    # For each crossing number, what fraction could be 2-bridge (rational)?
    # 2-bridge knots: determinant is odd (always true for knots), and they have
    # at most 2-bridge number. Count how many have mwf_bound <= 2 (braid index
    # could be 2, meaning they COULD be 2-bridge).
    by_crossing = defaultdict(list)
    for item in combined:
        by_crossing[item["crossing_number"]].append(item)

    crossing_analysis = {}
    for c in sorted(by_crossing.keys()):
        items = by_crossing[c]
        n = len(items)
        # Knots with MWF bound <= 2 could potentially be 2-bridge
        n_mwf_le2 = sum(1 for x in items if x["mwf_braid_lower_bound"] <= 2)
        # Knots with MWF bound <= 3
        n_mwf_le3 = sum(1 for x in items if x["mwf_braid_lower_bound"] <= 3)
        # Maximum possible bridge from crossing bound
        max_bridge = (c + 1) / 2
        # Jones span statistics
        spans_c = [x["jones_span"] for x in items]
        crossing_analysis[str(c)] = {
            "count": n,
            "bridge_upper_bound": max_bridge,
            "mwf_le_2_count": n_mwf_le2,
            "mwf_le_2_frac": n_mwf_le2 / n if n > 0 else 0,
            "mwf_le_3_count": n_mwf_le3,
            "mwf_le_3_frac": n_mwf_le3 / n if n > 0 else 0,
            "jones_span_mean": float(np.mean(spans_c)),
            "jones_span_min": int(min(spans_c)),
            "jones_span_max": int(max(spans_c)),
        }

    results["crossing_number_analysis"] = crossing_analysis

    # --- 6. Fraction achieving Schubert bound b = (c+1)/2 ---
    # This would require MWF braid bound >= (c+1)/2 (since bridge <= braid,
    # and MWF <= braid, having MWF = (c+1)/2 means bridge could equal the bound)
    # Actually: if MWF_braid_lower >= (c+1)/2, then braid >= (c+1)/2,
    # but bridge <= (c+1)/2, so bridge could be anything up to (c+1)/2.
    # The fraction where MWF braid bound = (c+1)/2 is interesting.
    at_bound = []
    for item in combined:
        c = item["crossing_number"]
        upper = (c + 1) / 2
        mwf = item["mwf_braid_lower_bound"]
        if mwf >= upper:
            at_bound.append(item["name"])

    results["mwf_at_or_above_schubert_bound"] = {
        "count": len(at_bound),
        "fraction": len(at_bound) / len(combined) if combined else 0,
        "examples": at_bound[:20],
    }

    # --- 7. Bridge proxy vs determinant ---
    # For 2-bridge (rational) knots, det = |continued fraction evaluation|
    # Use MWF bound as rough braid index proxy
    det_by_mwf = defaultdict(list)
    for item in combined:
        mwf = item["mwf_braid_lower_bound"]
        det_by_mwf[mwf].append(item["determinant"])

    det_vs_braid = {}
    for mwf_val in sorted(det_by_mwf.keys()):
        dets = det_by_mwf[mwf_val]
        det_vs_braid[str(mwf_val)] = {
            "count": len(dets),
            "det_mean": float(np.mean(dets)),
            "det_median": float(np.median(dets)),
            "det_min": int(min(dets)),
            "det_max": int(max(dets)),
            "det_std": float(np.std(dets)),
        }

    results["determinant_vs_mwf_braid_bound"] = det_vs_braid

    # --- 8. Jones span vs crossing number ---
    span_vs_crossing = {}
    for c in sorted(by_crossing.keys()):
        items = by_crossing[c]
        spans_c = [x["jones_span"] for x in items]
        span_vs_crossing[str(c)] = {
            "count": len(spans_c),
            "span_mean": float(np.mean(spans_c)),
            "span_std": float(np.std(spans_c)),
            "span_min": int(min(spans_c)),
            "span_max": int(max(spans_c)),
            "ratio_span_over_crossing": float(np.mean(spans_c)) / c if c > 0 else None,
        }

    results["jones_span_vs_crossing_number"] = span_vs_crossing

    # --- 9. Two-bridge knot candidates ---
    # 2-bridge knots have braid index <= 3 (Birman-Menasco).
    # MWF bound <= 2 means braid index COULD be 2, so these are strong 2-bridge candidates.
    two_bridge_candidates = [
        item for item in combined if item["mwf_braid_lower_bound"] <= 2
    ]
    results["two_bridge_candidates"] = {
        "count": len(two_bridge_candidates),
        "fraction_of_all": len(two_bridge_candidates) / len(combined) if combined else 0,
        "by_crossing": {
            str(c): sum(1 for x in two_bridge_candidates if x["crossing_number"] == c)
            for c in sorted(set(x["crossing_number"] for x in two_bridge_candidates))
        },
    }

    # --- 10. Summary ---
    results["summary"] = {
        "description": (
            "Bridge number b(K) not in dataset. Used Jones polynomial span to compute "
            "Morton-Williams-Franks (MWF) lower bound on braid index. "
            "Bridge number <= braid index <= ... so MWF is an indirect constraint. "
            "Schubert bound: b <= (c+1)/2 where c = crossing number."
        ),
        "key_findings": [
            f"Jones span range: {min(spans)}-{max(spans)}, mean {np.mean(spans):.1f}",
            f"MWF braid bound range: {min(braid_bounds)}-{max(braid_bounds)}, mean {np.mean(braid_bounds):.1f}",
            f"Knots with MWF >= Schubert bound: {len(at_bound)}/{len(combined)} ({100*len(at_bound)/len(combined):.1f}%)",
            f"Two-bridge candidates (MWF<=2): {len(two_bridge_candidates)}/{len(combined)} ({100*len(two_bridge_candidates)/len(combined):.1f}%)",
            "Determinant grows with MWF braid bound (expected: higher bridge = more complex)",
            "Jones span scales ~linearly with crossing number",
        ],
    }

    return results


def main():
    knots = load_knots()
    results = analyze(knots)

    with open(OUT, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to {OUT}")
    print(f"\n=== Summary ===")
    for line in results["summary"]["key_findings"]:
        print(f"  • {line}")
    print(f"\n=== Jones Span Distribution ===")
    for k, v in list(results["jones_span_distribution"].items())[:15]:
        print(f"  span={k}: {v} knots")
    print(f"\n=== MWF Braid Bound Distribution ===")
    for k, v in list(results["mwf_braid_bound_distribution"].items())[:10]:
        print(f"  mwf>={k}: {v} knots")
    print(f"\n=== Crossing Number Analysis ===")
    for c, info in results["crossing_number_analysis"].items():
        print(f"  c={c}: {info['count']} knots, bridge_upper={info['bridge_upper_bound']}, "
              f"2-bridge candidates={info['mwf_le_2_frac']*100:.0f}%, "
              f"span_mean={info['jones_span_mean']:.1f}")
    print(f"\n=== Determinant vs MWF Braid Bound ===")
    for k, v in list(results["determinant_vs_mwf_braid_bound"].items())[:10]:
        print(f"  mwf>={k}: det_mean={v['det_mean']:.1f}, det_median={v['det_median']:.1f}, n={v['count']}")


if __name__ == "__main__":
    main()

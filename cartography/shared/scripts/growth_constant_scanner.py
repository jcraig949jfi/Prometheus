"""
Growth Constant Scanner — High-precision constant identification from extended terms.
=======================================================================================
Takes the extended term files from term_extender and computes growth constants
at higher precision than the constant_telescope could with original OEIS terms.

For each sequence:
  1. Compute consecutive ratios a(n+1)/a(n)
  2. Split into odd/even sub-sequences (parity test from A148763 lesson)
  3. Compute geometric mean of paired ratios (the true growth constant)
  4. Match against 83 known constants with tighter tolerance
  5. Flag sequences where odd/even subsequences converge to DIFFERENT limits
     (these have parity structure worth investigating)

Usage:
    python growth_constant_scanner.py                    # scan all extended
    python growth_constant_scanner.py --family 148700    # one family
"""

import json
import math
import sys
import time
import numpy as np
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from constant_matcher import identify_constant, LOCAL_CONSTANTS

ROOT = Path(__file__).resolve().parents[3]
QUEUE_DIR = ROOT / "cartography" / "oeis" / "data" / "new_terms"
RESULTS_FILE = ROOT / "cartography" / "convergence" / "data" / "growth_constant_scan.json"


def analyze_growth(seq_id, terms, name=""):
    """Analyze the growth constant of a sequence at high precision."""
    pos = [t for t in terms if t > 0]
    if len(pos) < 20:
        return None

    arr = np.array(pos, dtype=float)
    n = len(arr)

    # Consecutive ratios
    ratios = [arr[i+1] / arr[i] for i in range(n-1) if arr[i] > 0]
    if len(ratios) < 10:
        return None

    # Split into odd/even indexed ratios
    odd_ratios = [ratios[i] for i in range(0, len(ratios), 2)]
    even_ratios = [ratios[i] for i in range(1, len(ratios), 2)]

    # Tail means (last 5 of each)
    tail_all = np.mean(ratios[-5:])
    tail_odd = np.mean(odd_ratios[-5:]) if len(odd_ratios) >= 5 else np.mean(odd_ratios)
    tail_even = np.mean(even_ratios[-5:]) if len(even_ratios) >= 5 else np.mean(even_ratios)

    # Geometric mean of paired ratios (true growth constant)
    n_pairs = min(len(odd_ratios), len(even_ratios))
    if n_pairs >= 3:
        geo_means = [math.sqrt(odd_ratios[i] * even_ratios[i]) for i in range(n_pairs)]
        growth_constant = np.mean(geo_means[-5:]) if len(geo_means) >= 5 else np.mean(geo_means)
    else:
        growth_constant = tail_all

    # Parity divergence: are odd and even converging to different limits?
    parity_gap = abs(tail_odd - tail_even)
    parity_ratio = parity_gap / max(abs(growth_constant), 0.01)

    # nth root
    nth_root = arr[-1] ** (1.0 / (n-1)) if arr[-1] > 0 else None

    # Convergence quality: are the last few geometric means stable?
    if len(geo_means) >= 5:
        convergence_std = np.std(geo_means[-5:])
    else:
        convergence_std = np.std(ratios[-5:])

    return {
        "seq_id": seq_id,
        "name": name[:100],
        "n_terms": n,
        "growth_constant": round(growth_constant, 12),
        "tail_all": round(tail_all, 10),
        "tail_odd": round(tail_odd, 10),
        "tail_even": round(tail_even, 10),
        "parity_gap": round(parity_gap, 8),
        "parity_ratio": round(parity_ratio, 6),
        "convergence_std": round(convergence_std, 8),
        "nth_root": round(nth_root, 10) if nth_root else None,
        "has_parity_structure": parity_ratio > 0.01,
    }


def scan_extended_terms():
    """Scan all extended term files for growth constants."""
    print("=" * 70)
    print("  GROWTH CONSTANT SCANNER")
    print("  High-precision constant identification from extended terms")
    print("=" * 70)

    t0 = time.time()

    # Load all extended term files
    files = sorted(QUEUE_DIR.glob("A*.json"))
    print(f"\n  Found {len(files)} extended sequence files")

    analyses = []
    constant_hits = []

    for jf in files:
        try:
            data = json.load(open(jf))
            seq_id = data["seq_id"]
            terms = data.get("all_terms") or list(data.get("new_terms", {}).values())
            name = data.get("name", "")

            # If we only have new_terms dict, we need original too
            if not data.get("all_terms"):
                from search_engine import _load_oeis, _oeis_cache
                _load_oeis()
                known = _oeis_cache.get(seq_id, [])
                new_vals = [v for v in data.get("new_terms", {}).values()]
                terms = list(known) + new_vals
        except Exception:
            continue

        result = analyze_growth(seq_id, terms, name)
        if result is None:
            continue

        analyses.append(result)

        # Match growth constant against known constants
        gc = result["growth_constant"]
        if 0.5 < gc < 100 and np.isfinite(gc):
            matches = identify_constant(gc, tolerance=1e-4, use_ries=False)
            for m in matches[:1]:
                if m.confidence > 0.99:
                    constant_hits.append({
                        "seq_id": seq_id,
                        "growth_constant": gc,
                        "constant": m.name,
                        "residual": m.residual,
                        "confidence": m.confidence,
                        "n_terms": result["n_terms"],
                        "convergence_std": result["convergence_std"],
                        "has_parity": result["has_parity_structure"],
                    })

    elapsed = time.time() - t0

    # Save results
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_s": round(elapsed, 1),
        "n_sequences": len(analyses),
        "n_constant_hits": len(constant_hits),
        "constant_hits": constant_hits,
        "analyses": analyses,
    }
    def _json_default(obj):
        if isinstance(obj, (np.bool_, np.integer)):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return str(obj)

    with open(RESULTS_FILE, "w") as f:
        json.dump(output, f, indent=2, default=_json_default)

    # Summary
    print(f"\n  Analyzed {len(analyses)} sequences in {elapsed:.1f}s")

    # Growth constant distribution
    gcs = [a["growth_constant"] for a in analyses if 1 < a["growth_constant"] < 20]
    if gcs:
        print(f"\n  Growth constant distribution:")
        print(f"    Mean: {np.mean(gcs):.4f}")
        print(f"    Median: {np.median(gcs):.4f}")
        print(f"    Std: {np.std(gcs):.4f}")
        print(f"    Range: [{min(gcs):.4f}, {max(gcs):.4f}]")

    # Parity structure
    parity_seqs = [a for a in analyses if a["has_parity_structure"]]
    print(f"\n  Sequences with parity structure: {len(parity_seqs)}/{len(analyses)}")
    if parity_seqs:
        print(f"  Top parity gaps:")
        for a in sorted(parity_seqs, key=lambda x: -x["parity_ratio"])[:10]:
            print(f"    {a['seq_id']}: gap={a['parity_gap']:.4f} "
                  f"(odd={a['tail_odd']:.4f}, even={a['tail_even']:.4f}, "
                  f"geo={a['growth_constant']:.4f})")

    # Constant matches
    if constant_hits:
        from collections import Counter
        by_const = Counter(h["constant"] for h in constant_hits)
        print(f"\n  Constant matches ({len(constant_hits)} total):")
        for const, count in by_const.most_common(15):
            examples = [h for h in constant_hits if h["constant"] == const]
            best = min(examples, key=lambda x: x["residual"])
            print(f"    {const:35s} {count:4d} hits  "
                  f"(best: {best['seq_id']} residual={best['residual']:.2e} n={best['n_terms']})")
    else:
        print(f"\n  No constant matches at tolerance 1e-4")

    print(f"\n  Results saved to {RESULTS_FILE}")
    print(f"{'=' * 70}")

    return output


if __name__ == "__main__":
    scan_extended_terms()

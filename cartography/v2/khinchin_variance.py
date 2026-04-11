"""
NF13: Continued Fraction Khinchin Variance
===========================================
For 1000 OEIS sequences with 50+ positive terms that could plausibly be
CF partial quotients (all terms > 0, reasonable growth), compute the
geometric mean of the first 50 partial quotients and compare to Khinchin's
constant K ≈ 2.685452.

Measures:
  (1) MSE between observed geometric means and K across all 1000 sequences
  (2) Fraction of sequences "Khinchin-compliant" (geometric mean within 10% of K)
  (3) Comparison: famous-constant CF sequences vs arbitrary OEIS sequences
"""

import json
import math
import numpy as np
from pathlib import Path

KHINCHIN = 2.6854520010653064  # Khinchin's constant

DATA_PATH = Path(__file__).resolve().parent.parent / "oeis" / "data" / "stripped_new.txt"
OUT_PATH = Path(__file__).resolve().parent / "khinchin_variance_results.json"

# Known CF sequences for famous constants
FAMOUS_CF = {
    # CF partial quotients of pi
    "A001203": "pi",
    # CF partial quotients of e
    "A003417": "e",
    # CF of sqrt(2) = [1;2,2,2,...]
    "A040000": "sqrt(2)",
    # CF of sqrt(3)
    "A040001": "sqrt(3)",
    # CF of sqrt(5)
    "A040002": "sqrt(5)",
    # CF of golden ratio phi
    "A000012": "phi (all 1s)",
    # CF of e-1
    "A005131": "e-1",
    # CF of pi/2
    "A053300": "pi/2",
    # CF of log(2)
    "A073743": "log(2)",
    # CF of Euler-Mascheroni gamma
    "A002852": "Euler gamma",
    # CF of zeta(3) Apery's constant
    "A013631": "zeta(3)",
    # CF of sqrt(7)
    "A010121": "sqrt(7)",
    # CF of cbrt(2)
    "A002945": "cbrt(2)",
    # CF of pi^2
    "A058284": "pi^2",
    # CF of e^2
    "A058282": "e^2",
}


def parse_sequences(path):
    """Parse OEIS stripped file into dict of {Axxxxxx: [int, ...]}."""
    seqs = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Format: Axxxxxx ,val1,val2,...
            idx = line.index(" ")
            seq_id = line[:idx]
            vals_str = line[idx+1:].strip().strip(",")
            if not vals_str:
                continue
            try:
                vals = [int(x) for x in vals_str.split(",") if x.strip()]
            except ValueError:
                continue
            seqs[seq_id] = vals
    return seqs


def is_cf_candidate(terms, min_len=50):
    """Check if a sequence could plausibly be CF partial quotients.

    Requirements:
      - At least min_len terms
      - All terms > 0 (CF partial quotients are positive integers, except possibly a[0])
        We allow a[0] >= 0 (the integer part) and require a[1:] > 0
      - No term exceeds 10^8 (avoid sequences that are clearly not CF-like)
      - At least 3 distinct values in first 50 terms (avoid constant/trivial sequences)
    """
    # If a[0]==0, we need 51 terms to get 50 partial quotients
    if len(terms) < min_len:
        return False
    # Determine the partial quotients we'd actually use
    if terms[0] == 0:
        if len(terms) < min_len + 1:
            return False
        pq = terms[1:min_len + 1]
    else:
        pq = terms[:min_len]
    # All partial quotients must be > 0
    if any(t <= 0 for t in pq):
        return False
    # Cap on maximum value
    if any(t > 1e8 for t in pq):
        return False
    # Need some variety (exclude constant sequences like all-1s, all-2s)
    if len(set(pq)) < 3:
        return False
    return True


def geometric_mean(terms):
    """Compute geometric mean via log to avoid overflow."""
    logs = [math.log(t) for t in terms]
    return math.exp(sum(logs) / len(logs))


def main():
    print("Loading OEIS sequences...")
    seqs = parse_sequences(DATA_PATH)
    print(f"  Parsed {len(seqs)} sequences")

    # Find CF candidates
    candidates = {}
    for seq_id, terms in seqs.items():
        if is_cf_candidate(terms, min_len=50):
            candidates[seq_id] = terms[:50]

    print(f"  Found {len(candidates)} CF-candidate sequences (50+ positive terms, 3+ distinct values)")

    # If more than 1000, sample deterministically
    sorted_ids = sorted(candidates.keys())
    if len(sorted_ids) > 1000:
        # Take every N-th to get 1000, ensuring famous constants are included
        famous_in_candidates = [s for s in sorted_ids if s in FAMOUS_CF]
        non_famous = [s for s in sorted_ids if s not in FAMOUS_CF]
        need = 1000 - len(famous_in_candidates)
        step = max(1, len(non_famous) // need)
        selected_non_famous = non_famous[::step][:need]
        selected = sorted(famous_in_candidates + selected_non_famous)
    else:
        selected = sorted_ids[:1000]

    print(f"  Selected {len(selected)} sequences for analysis")

    # Compute geometric means
    # For CF partial quotients [a0; a1, a2, ...], Khinchin's theorem applies to a1, a2, ...
    # If a0 == 0, use terms[1:51]; otherwise use terms[0:50]
    # Either way, all terms fed to geometric_mean must be > 0
    results = {}
    for seq_id in selected:
        terms = candidates[seq_id]
        # Skip the leading zero if present (integer part of CF)
        if terms[0] == 0:
            pq = terms[1:51]
        else:
            pq = terms[:50]
        # Safety: all must be > 0
        if any(t <= 0 for t in pq) or len(pq) < 50:
            continue
        gm = geometric_mean(pq)
        results[seq_id] = {
            "geometric_mean": gm,
            "is_famous_cf": seq_id in FAMOUS_CF,
            "famous_name": FAMOUS_CF.get(seq_id, None),
            "first_10_terms": terms[:10],
        }

    # Update selected to only those that survived
    selected = sorted(results.keys())
    print(f"  After filtering: {len(selected)} sequences with valid geometric means")

    geo_means = np.array([r["geometric_mean"] for r in results.values()])

    # (1) MSE between observed geometric means and K
    mse = float(np.mean((geo_means - KHINCHIN) ** 2))

    # (2) Fraction Khinchin-compliant (within 10% of K)
    lower = KHINCHIN * 0.9
    upper = KHINCHIN * 1.1
    compliant_mask = (geo_means >= lower) & (geo_means <= upper)
    fraction_compliant = float(np.mean(compliant_mask))

    # (3) Famous constants vs arbitrary
    famous_gms = []
    arbitrary_gms = []
    famous_details = []
    for seq_id in selected:
        r = results[seq_id]
        if r["is_famous_cf"]:
            famous_gms.append(r["geometric_mean"])
            famous_details.append({
                "seq_id": seq_id,
                "name": r["famous_name"],
                "geometric_mean": round(r["geometric_mean"], 6),
                "deviation_from_K": round(r["geometric_mean"] - KHINCHIN, 6),
                "within_10pct": bool(lower <= r["geometric_mean"] <= upper),
            })
        else:
            arbitrary_gms.append(r["geometric_mean"])

    famous_gms = np.array(famous_gms) if famous_gms else np.array([])
    arbitrary_gms = np.array(arbitrary_gms)

    # Distribution stats
    def dist_stats(arr, label):
        if len(arr) == 0:
            return {"n": 0, "label": label}
        return {
            "label": label,
            "n": int(len(arr)),
            "mean": round(float(np.mean(arr)), 6),
            "median": round(float(np.median(arr)), 6),
            "std": round(float(np.std(arr)), 6),
            "min": round(float(np.min(arr)), 6),
            "max": round(float(np.max(arr)), 6),
            "mse_vs_K": round(float(np.mean((arr - KHINCHIN) ** 2)), 6),
            "fraction_within_10pct_K": round(float(np.mean((arr >= lower) & (arr <= upper))), 6),
        }

    # Find most and least Khinchin-compliant
    sorted_by_deviation = sorted(results.items(), key=lambda x: abs(x[1]["geometric_mean"] - KHINCHIN))
    closest_to_K = [
        {"seq_id": s, "geometric_mean": round(r["geometric_mean"], 6),
         "deviation": round(r["geometric_mean"] - KHINCHIN, 6)}
        for s, r in sorted_by_deviation[:10]
    ]
    farthest_from_K = [
        {"seq_id": s, "geometric_mean": round(r["geometric_mean"], 6),
         "deviation": round(r["geometric_mean"] - KHINCHIN, 6)}
        for s, r in sorted_by_deviation[-10:]
    ]

    # Histogram bins for geometric means
    bin_edges = [0, 1, 1.5, 2, 2.4, 2.6, 2.8, 3.0, 3.5, 4, 5, 10, 50, 500, 10000, 1e8]
    hist, _ = np.histogram(geo_means, bins=bin_edges)
    histogram = [{"bin": f"[{bin_edges[i]:.1f}, {bin_edges[i+1]:.1f})", "count": int(hist[i])}
                 for i in range(len(hist))]

    output = {
        "problem": "NF13: Continued Fraction Khinchin Variance",
        "khinchin_constant": KHINCHIN,
        "total_sequences_parsed": len(seqs),
        "cf_candidates_found": len(candidates),
        "sequences_analyzed": len(selected),
        "partial_quotients_used": 50,
        "measure_1_mse_vs_K": round(mse, 6),
        "measure_2_fraction_khinchin_compliant_10pct": round(fraction_compliant, 6),
        "measure_3_famous_vs_arbitrary": {
            "famous_constants": dist_stats(famous_gms, "famous_CF_sequences"),
            "arbitrary_sequences": dist_stats(arbitrary_gms, "arbitrary_OEIS_sequences"),
            "famous_details": famous_details,
        },
        "geometric_mean_distribution": histogram,
        "closest_to_K": closest_to_K,
        "farthest_from_K": farthest_from_K,
        "interpretation": {
            "khinchin_theorem": (
                "Khinchin's theorem states that for almost all real numbers, "
                "the geometric mean of CF partial quotients converges to K ≈ 2.685452. "
                "However, specific algebraic numbers (quadratic irrationals have periodic CFs) "
                "and many mathematically interesting constants may not satisfy this."
            ),
            "expectation": (
                "We expect most OEIS sequences to NOT be Khinchin-compliant, because "
                "OEIS sequences are curated for mathematical interest — they are not "
                "'almost all' reals. Famous transcendental constants (pi, e, gamma) are "
                "conjectured to be Khinchin-compliant but this is unproven."
            ),
        }
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    # Print summary
    print(f"\n{'='*60}")
    print(f"NF13: Khinchin Variance Results")
    print(f"{'='*60}")
    print(f"Sequences analyzed:         {len(selected)}")
    print(f"Khinchin's constant K:      {KHINCHIN:.6f}")
    print(f"")
    print(f"(1) MSE vs K:               {mse:.6f}")
    print(f"(2) Khinchin-compliant:     {fraction_compliant:.4f} ({int(fraction_compliant*len(selected))}/{len(selected)})")
    print(f"")
    print(f"(3) Famous constants ({len(famous_gms)} found in sample):")
    for d in famous_details:
        flag = "OK" if d["within_10pct"] else "OUTSIDE"
        print(f"    {d['seq_id']} ({d['name']:>15s}): GM = {d['geometric_mean']:.6f}  "
              f"(dev = {d['deviation_from_K']:+.6f}) [{flag}]")

    if len(famous_gms) > 0 and len(arbitrary_gms) > 0:
        print(f"\n  Famous mean GM:    {np.mean(famous_gms):.6f}")
        print(f"  Arbitrary mean GM: {np.mean(arbitrary_gms):.6f}")
        print(f"  Famous MSE vs K:   {np.mean((famous_gms - KHINCHIN)**2):.6f}")
        print(f"  Arbitrary MSE vs K:{np.mean((arbitrary_gms - KHINCHIN)**2):.6f}")

    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()

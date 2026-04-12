"""
M19: Tri-prime interference β₃
================================
For forms congruent mod ℓ₁ AND mod ℓ₂, does requiring congruence mod ℓ₃
show constructive or destructive interference?

Measure P(cong mod ℓ₃ | cong mod ℓ₁ AND ℓ₂) vs P(cong mod ℓ₃).
If ratio > 1: constructive. If < 1: destructive. β₃ = this ratio.

Compute for all triples (ℓ₁,ℓ₂,ℓ₃) from {2,3,5,7,11}.
"""
import json, time
import numpy as np
import duckdb
from pathlib import Path
from collections import defaultdict
from itertools import combinations

V2 = Path(__file__).resolve().parent
DB = V2.parents[3] / "charon" / "data" / "charon.duckdb"
HECKE = V2 / "hecke_graph_results.json"
OUT = V2 / "m19_tri_prime_interference_results.json"

def prime_factors(n):
    f = set(); d = 2
    while d*d <= n:
        while n % d == 0: f.add(d); n //= d
        d += 1
    if n > 1: f.add(n)
    return f

def sieve(limit):
    is_p = [True] * (limit + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_p[i]:
            for j in range(i*i, limit+1, i): is_p[j] = False
    return [i for i in range(2, limit+1) if is_p[i]]

def main():
    t0 = time.time()
    print("=== M19: Tri-prime interference β₃ ===\n")

    con = duckdb.connect(str(DB), read_only=True)
    rows = con.execute("""
        SELECT lmfdb_label, level, ap_coeffs FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND char_order = 1
        ORDER BY level LIMIT 5000
    """).fetchall()
    con.close()
    print(f"  Loaded {len(rows)} forms (capped at 5000 for speed)")

    ap_primes = sieve(50)
    ELLS = [2, 3, 5, 7, 11]

    # Parse a_p data
    forms = []
    for label, level, ap_json in rows:
        ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
        ap_vals = [x[0] if isinstance(x, list) else x for x in ap]
        forms.append({"label": label, "level": level, "ap": ap_vals})

    # For each pair at same level, check congruence at each ell
    print("  Computing pairwise congruences by level...")
    by_level = defaultdict(list)
    for f in forms:
        by_level[f["level"]].append(f)

    # Count pairs congruent mod each ell and combination
    pair_cong = defaultdict(int)  # key = frozenset of ells
    total_pairs = 0

    for level, group in by_level.items():
        if len(group) < 2: continue
        bad = prime_factors(level)
        good_idx = [i for i, p in enumerate(ap_primes) if p not in bad and p not in ELLS]

        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                total_pairs += 1
                ap1, ap2 = group[i]["ap"], group[j]["ap"]
                cong_at = set()
                for ell in ELLS:
                    # Check if a_p ≡ mod ell for all good primes
                    all_cong = True
                    tested = 0
                    for k in good_idx:
                        if k >= len(ap1) or k >= len(ap2): break
                        tested += 1
                        if (ap1[k] - ap2[k]) % ell != 0:
                            all_cong = False; break
                        if tested >= 15: break
                    if all_cong and tested >= 10:
                        cong_at.add(ell)

                # Record all subsets
                for r in range(1, len(cong_at) + 1):
                    for subset in combinations(cong_at, r):
                        pair_cong[frozenset(subset)] += 1

    print(f"  Total pairs checked: {total_pairs}")
    for ell in ELLS:
        cnt = pair_cong.get(frozenset([ell]), 0)
        print(f"  Congruent mod {ell}: {cnt} ({cnt/total_pairs:.4%})")

    # Tri-prime interference
    print("\n  Tri-prime interference ratios:")
    results = []
    for l1, l2, l3 in combinations(ELLS, 3):
        p12 = pair_cong.get(frozenset([l1, l2]), 0) / total_pairs if total_pairs > 0 else 0
        p123 = pair_cong.get(frozenset([l1, l2, l3]), 0) / total_pairs if total_pairs > 0 else 0
        p3 = pair_cong.get(frozenset([l3]), 0) / total_pairs if total_pairs > 0 else 0
        n12 = pair_cong.get(frozenset([l1, l2]), 0)

        # β₃ = P(cong ℓ₃ | cong ℓ₁∧ℓ₂) / P(cong ℓ₃)
        if n12 > 0 and p3 > 0:
            p3_given_12 = p123 * total_pairs / n12 if n12 > 0 else 0
            beta3 = (p3_given_12) / p3 if p3 > 0 else 0
        else:
            beta3 = None

        row = {
            "triple": [l1, l2, l3],
            "n_cong_12": pair_cong.get(frozenset([l1, l2]), 0),
            "n_cong_123": pair_cong.get(frozenset([l1, l2, l3]), 0),
            "n_cong_3": pair_cong.get(frozenset([l3]), 0),
            "beta3": round(beta3, 4) if beta3 is not None else None,
        }
        results.append(row)
        tag = "CONSTRUCTIVE" if beta3 and beta3 > 1.5 else ("DESTRUCTIVE" if beta3 and beta3 < 0.5 else "NEUTRAL")
        print(f"    ({l1},{l2},{l3}): n₁₂={row['n_cong_12']}, n₁₂₃={row['n_cong_123']}, "
              f"β₃={beta3:.3f} [{tag}]" if beta3 else f"    ({l1},{l2},{l3}): β₃=undefined")

    betas = [r["beta3"] for r in results if r["beta3"] is not None]
    elapsed = time.time() - t0
    output = {
        "probe": "M19", "title": "Tri-prime interference β₃",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_forms": len(forms), "n_pairs": total_pairs,
        "single_prime_counts": {str(ell): pair_cong.get(frozenset([ell]), 0) for ell in ELLS},
        "triple_results": results,
        "beta3_statistics": {
            "mean": round(float(np.mean(betas)), 4) if betas else None,
            "std": round(float(np.std(betas)), 4) if betas else None,
            "min": round(float(min(betas)), 4) if betas else None,
            "max": round(float(max(betas)), 4) if betas else None,
        },
        "assessment": None,
    }

    if betas and np.mean(betas) > 2.0:
        output["assessment"] = f"CONSTRUCTIVE: mean β₃={np.mean(betas):.2f} — triple congruences are MORE likely than independence predicts"
    elif betas and np.mean(betas) > 1.0:
        output["assessment"] = f"MILD CONSTRUCTIVE: mean β₃={np.mean(betas):.2f}"
    elif betas and np.mean(betas) < 0.5:
        output["assessment"] = f"DESTRUCTIVE: mean β₃={np.mean(betas):.2f} — triple congruences suppressed"
    elif betas:
        output["assessment"] = f"NEUTRAL: mean β₃={np.mean(betas):.2f} — near independence"
    else:
        output["assessment"] = "NO DATA: insufficient congruences for tri-prime analysis"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()

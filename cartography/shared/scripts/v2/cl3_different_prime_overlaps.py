"""
ALL-056: CL3 Different-Prime Overlaps
=======================================
5 forms have starvation at one prime and Hecke congruence at a DIFFERENT prime.
This is the most interesting structural anomaly: the form has two independent
arithmetic phenomena at different primes.

Dissect each of the 5 forms:
1. What is the starvation prime? What residue classes are missing?
2. What is the congruence prime? What form is it congruent to?
3. Is there a common algebraic explanation? (Level factorization, CM, ...)
4. Does the congruence partner also show starvation?
5. Statistical test: is different-prime overlap rate above chance?

Uses starved_congruence_results.json + hecke_graph_results.json + DuckDB.
"""

import json, time
import numpy as np
import duckdb
from pathlib import Path
from scipy import stats

V2 = Path(__file__).resolve().parent
STARV_CROSS = V2 / "starved_congruence_results.json"
HECKE = V2 / "hecke_graph_results.json"
STARVATION = V2 / "residue_starvation_results.json"
DB_PATH = V2.parents[3] / "charon" / "data" / "charon.duckdb"
OUT_PATH = V2 / "cl3_different_prime_results.json"


def prime_factors(n):
    f = set()
    d = 2
    while d * d <= n:
        while n % d == 0: f.add(d); n //= d
        d += 1
    if n > 1: f.add(n)
    return f


def main():
    t0 = time.time()
    print("=== ALL-056: CL3 Different-Prime Overlaps ===\n")

    with open(STARV_CROSS) as f:
        cross = json.load(f)

    alignment = cross.get("prime_alignment", {})
    diff_forms = alignment.get("different_prime_forms", [])
    same_forms = alignment.get("same_prime_forms", [])
    same_count = alignment.get("same_prime_count", len(same_forms))
    diff_count = alignment.get("different_prime_count", len(diff_forms))

    print(f"[1] Same-prime forms: {same_count}")
    print(f"    Different-prime forms: {diff_count}")
    print(f"    Total overlap: {same_count + diff_count}")

    # Load the 5 different-prime forms
    print(f"\n[2] Dissecting {len(diff_forms)} different-prime forms...")

    # Load starvation details
    with open(STARVATION) as f:
        starv_data = json.load(f)

    # Build starvation lookup
    starv_by_label = {}
    for form in starv_data.get("starved_forms", []):
        starv_by_label[form["label"]] = form

    # Load DuckDB for form details
    con = duckdb.connect(str(DB_PATH), read_only=True)

    dissections = []
    for df in diff_forms:
        label = df["label"]
        starv_primes = df["starvation_primes"]
        cong_primes = df["congruence_primes"]

        print(f"\n  --- {label} ---")
        print(f"    Starvation primes: {starv_primes}")
        print(f"    Congruence primes: {cong_primes}")

        # Get form details from DuckDB
        row = con.execute("""
            SELECT level, is_cm, self_twist_type, ap_coeffs
            FROM modular_forms
            WHERE lmfdb_label = ?
        """, [label]).fetchone()

        level = None
        is_cm = None
        level_factors = set()
        if row:
            level, is_cm, st_type, ap_json = row
            level_factors = prime_factors(level)
            print(f"    Level: {level}, factors: {sorted(level_factors)}")
            print(f"    CM: {is_cm}, self-twist: {st_type}")

        # Check starvation details
        starv_info = starv_by_label.get(label, {})
        starv_detail = {}
        for sp in starv_primes:
            sp_key = str(sp)
            if "starvation" in starv_info and sp_key in starv_info["starvation"]:
                sd = starv_info["starvation"][sp_key]
                starv_detail[sp_key] = {
                    "classes_hit": sd.get("classes", []),
                    "missing": sd.get("missing", []),
                    "ratio": sd.get("ratio", 0),
                }
                print(f"    Starvation at {sp}: missing classes {sd.get('missing', [])}")

        # Check if starvation prime divides level
        starv_divides_level = any(sp in level_factors for sp in starv_primes) if level_factors else None
        cong_divides_level = any(cp in level_factors for cp in cong_primes) if level_factors else None
        print(f"    Starvation prime | level: {starv_divides_level}")
        print(f"    Congruence prime | level: {cong_divides_level}")

        # Look up the congruence partner
        partner_labels = []
        for cp in cong_primes:
            partners = con.execute("""
                SELECT mf2.lmfdb_label, mf2.level, mf2.is_cm
                FROM modular_forms mf1
                JOIN modular_forms mf2 ON mf1.level = mf2.level
                WHERE mf1.lmfdb_label = ? AND mf2.lmfdb_label != ?
                  AND mf2.weight = 2 AND mf2.dim = 1
            """, [label, label]).fetchall()
            for p_label, p_level, p_cm in partners:
                partner_labels.append({"label": p_label, "level": p_level, "is_cm": bool(p_cm)})
                # Is the partner also starved?
                p_starved = p_label in starv_by_label
                print(f"    Partner {p_label}: CM={p_cm}, starved={p_starved}")

        dissections.append({
            "label": label,
            "level": level,
            "level_factors": sorted(level_factors) if level_factors else [],
            "is_cm": bool(is_cm) if is_cm is not None else None,
            "starvation_primes": starv_primes,
            "congruence_primes": cong_primes,
            "starvation_details": starv_detail,
            "starv_divides_level": starv_divides_level,
            "cong_divides_level": cong_divides_level,
            "partners": partner_labels[:5],
        })

    con.close()

    # Statistical test
    print(f"\n[3] Statistical test: is different-prime rate above chance?...")
    total_overlap = same_count + diff_count
    if total_overlap > 0:
        observed_diff_frac = diff_count / total_overlap
        # Under null: starvation and congruence primes are independent
        # P(different) ≈ 1 - 1/n_primes_tested
        n_primes = 5  # 2,3,5,7,11
        null_same_prob = 1.0 / n_primes
        null_diff_prob = 1 - null_same_prob
        # Binomial test
        p_val = stats.binomtest(same_count, total_overlap, null_same_prob).pvalue
        print(f"    Observed same-prime: {same_count}/{total_overlap} = {same_count/total_overlap:.1%}")
        print(f"    Null expectation (random): {null_same_prob:.0%}")
        print(f"    p-value (binomial): {p_val:.2e}")
        enrichment_same = (same_count / total_overlap) / null_same_prob if null_same_prob > 0 else 0
        print(f"    Same-prime enrichment: {enrichment_same:.1f}x")
    else:
        p_val = 1.0
        enrichment_same = 0

    elapsed = time.time() - t0
    output = {
        "challenge": "ALL-056",
        "title": "CL3 Different-Prime Overlaps",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "same_prime_count": same_count,
        "different_prime_count": diff_count,
        "dissections": dissections,
        "statistical_test": {
            "same_prime_enrichment": round(enrichment_same, 2),
            "p_value": float(p_val),
            "null_model": "uniform random prime assignment",
        },
        "assessment": None,
    }

    if enrichment_same > 3 and p_val < 0.01:
        output["assessment"] = (f"SAME-PRIME DOMINATES: {same_count}/{total_overlap} same-prime ({enrichment_same:.0f}x enrichment, p={p_val:.1e}). "
                                f"Different-prime overlaps ({diff_count}) are the rare exceptions — starvation and congruence share a common cause at the SAME prime.")
    elif diff_count == 0:
        output["assessment"] = "NO DIFFERENT-PRIME CASES: starvation and congruence always share a prime"
    else:
        output["assessment"] = (f"MIXED: {same_count} same-prime, {diff_count} different-prime. "
                                f"Different-prime cases may indicate independent arithmetic mechanisms.")

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()

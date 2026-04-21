"""
Greenberg's Iwasawa Conjecture — Screening Pass
Aporia Deep Research Report #11

Greenberg (1976): For every totally real number field K and every prime p,
the Iwasawa lambda and mu invariants of the cyclotomic Z_p-extension are zero.

Necessary condition for lambda > 0: p | h(K).
This script screens the 22M LMFDB number fields for totally real fields
where small primes divide the class number.

These are NOT counterexamples — they are candidates where one would LOOK.
"""

import json
import time
import psycopg2
from collections import defaultdict

DB_PARAMS = dict(host="localhost", port=5432, dbname="lmfdb",
                 user="postgres", password="prometheus")

PRIMES = [2, 3, 5, 7, 11, 13]


def connect():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    cur.execute("SET work_mem = '256MB'")
    conn.commit()
    return conn


def task1_count_by_degree(cur):
    """Count totally real fields by degree."""
    print("[1] Counting totally real fields by degree...")
    cur.execute("""
        SELECT CAST(degree AS integer) AS deg, COUNT(*)
        FROM nf_fields
        WHERE r2 = '0'
        GROUP BY deg
        ORDER BY deg
    """)
    rows = cur.fetchall()
    result = {int(r[0]): int(r[1]) for r in rows}
    total = sum(result.values())
    print(f"    Total totally real: {total:,}")
    for deg in sorted(result):
        print(f"    degree {deg}: {result[deg]:,}")
    return result, total


def task2_prime_divisibility(cur, total):
    """For each prime p, count totally real fields where p | h."""
    print("\n[2] Prime divisibility of class number...")
    results = {}
    for p in PRIMES:
        cur.execute("""
            SELECT COUNT(*)
            FROM nf_fields
            WHERE r2 = '0'
              AND CAST(class_number AS bigint) %% %s = 0
        """, (p,))
        count = cur.fetchone()[0]
        pct = 100.0 * count / total if total > 0 else 0
        results[p] = {"count": int(count), "pct": round(pct, 4)}
        print(f"    p={p:2d}: {count:>8,} fields ({pct:.4f}%)")
    return results


def task3_cross_tabulate(cur):
    """Degree distribution for p | h survivors."""
    print("\n[3] Cross-tabulation: degree x prime for p | h survivors...")
    results = {}
    for p in PRIMES:
        cur.execute("""
            SELECT CAST(degree AS integer) AS deg, COUNT(*)
            FROM nf_fields
            WHERE r2 = '0'
              AND CAST(class_number AS bigint) %% %s = 0
            GROUP BY deg
            ORDER BY deg
        """, (p,))
        rows = cur.fetchall()
        dist = {int(r[0]): int(r[1]) for r in rows}
        results[p] = dist
        print(f"    p={p}: {dist}")
    return results


def task4_multiple_primes(cur):
    """Fields where multiple primes divide h — stronger Greenberg candidates."""
    print("\n[4] Multiple-prime divisibility...")
    # Count fields by number of primes dividing h
    # Build CASE expression
    conditions = " + ".join(
        f"CASE WHEN CAST(class_number AS bigint) % {p} = 0 THEN 1 ELSE 0 END"
        for p in PRIMES
    )
    cur.execute(f"""
        SELECT num_primes, COUNT(*) FROM (
            SELECT ({conditions}) AS num_primes
            FROM nf_fields
            WHERE r2 = '0'
              AND CAST(class_number AS bigint) > 1
        ) sub
        GROUP BY num_primes
        ORDER BY num_primes
    """)
    rows = cur.fetchall()
    result = {int(r[0]): int(r[1]) for r in rows}
    for k, v in sorted(result.items()):
        print(f"    {k} primes divide h: {v:,} fields")

    # Get examples with >= 3 primes dividing h
    cur.execute(f"""
        SELECT label, class_number, degree
        FROM (
            SELECT label, class_number, degree,
                   ({conditions}) AS num_primes
            FROM nf_fields
            WHERE r2 = '0'
              AND CAST(class_number AS bigint) > 1
        ) sub
        WHERE num_primes >= 3
        ORDER BY CAST(class_number AS bigint) DESC
        LIMIT 20
    """)
    examples = [{"label": r[0], "class_number": r[1], "degree": r[2]}
                for r in cur.fetchall()]
    if examples:
        print(f"    Top examples (>=3 primes): {len(examples)}")
        for ex in examples[:5]:
            print(f"      {ex['label']}: h={ex['class_number']}, deg={ex['degree']}")

    return {"by_count": result, "examples_ge3": examples}


def task5_p2_valuation_depth(cur):
    """For p=2 survivors: how deep does the 2-adic valuation go?"""
    print("\n[5] 2-adic valuation depth for p=2 survivors...")
    results = {}
    for power_label, divisor in [("2|h", 2), ("4|h", 4), ("8|h", 8),
                                  ("16|h", 16), ("32|h", 32)]:
        cur.execute("""
            SELECT COUNT(*)
            FROM nf_fields
            WHERE r2 = '0'
              AND CAST(class_number AS bigint) %% %s = 0
        """, (divisor,))
        count = cur.fetchone()[0]
        results[power_label] = int(count)
        print(f"    {power_label:5s}: {count:>8,}")

    # Degree distribution for 8|h
    cur.execute("""
        SELECT CAST(degree AS integer) AS deg, COUNT(*)
        FROM nf_fields
        WHERE r2 = '0'
          AND CAST(class_number AS bigint) %% %s = 0
        GROUP BY deg
        ORDER BY deg
    """, (8,))
    depth_by_degree = {int(r[0]): int(r[1]) for r in cur.fetchall()}
    results["8|h_by_degree"] = depth_by_degree
    print(f"    8|h by degree: {depth_by_degree}")
    return results


def task6_greenberg_properties(cur):
    """Analyze properties of p|h survivors relevant to Greenberg."""
    print("\n[6] Greenberg-relevant properties of survivors...")
    results = {}

    # For p=2 survivors: discriminant and regulator statistics
    for p in [2, 3, 5]:
        cur.execute("""
            SELECT
                CAST(degree AS integer) AS deg,
                COUNT(*) AS cnt,
                AVG(CAST(regulator AS double precision)) AS avg_reg,
                AVG(LN(CAST(disc_abs AS double precision))) AS avg_ln_disc
            FROM nf_fields
            WHERE r2 = '0'
              AND CAST(class_number AS bigint) %% %s = 0
              AND regulator IS NOT NULL
              AND regulator != ''
              AND disc_abs IS NOT NULL
            GROUP BY deg
            ORDER BY deg
        """, (p,))
        rows = cur.fetchall()
        stats = {}
        for r in rows:
            stats[int(r[0])] = {
                "count": int(r[1]),
                "avg_regulator": round(float(r[2]), 6) if r[2] else None,
                "avg_ln_disc": round(float(r[3]), 4) if r[3] else None,
            }
        results[f"p={p}_stats"] = stats
        print(f"    p={p} survivor stats by degree:")
        for deg, s in sorted(stats.items()):
            print(f"      deg {deg}: n={s['count']}, avg_reg={s['avg_regulator']}, avg_ln|D|={s['avg_ln_disc']}")

    # Galois vs non-Galois among survivors
    cur.execute("""
        SELECT
            is_galois,
            COUNT(*) AS cnt
        FROM nf_fields
        WHERE r2 = '0'
          AND CAST(class_number AS bigint) > 1
        GROUP BY is_galois
    """)
    galois_split = {r[0]: int(r[1]) for r in cur.fetchall()}
    results["galois_split_h_gt_1"] = galois_split
    print(f"    Galois split (h>1): {galois_split}")

    # Class number distribution for survivors
    cur.execute("""
        SELECT class_number, COUNT(*) AS cnt
        FROM nf_fields
        WHERE r2 = '0'
          AND CAST(class_number AS bigint) > 1
        GROUP BY class_number
        ORDER BY cnt DESC
        LIMIT 20
    """)
    h_dist = {r[0]: int(r[1]) for r in cur.fetchall()}
    results["top_class_numbers"] = h_dist
    print(f"    Top class numbers: {h_dist}")

    return results


def task7_summary(total, by_degree, prime_counts, multi_prime, valuation):
    """Build the final summary report."""
    print("\n[7] Summary report...")
    summary = {
        "conjecture": "Greenberg (1976)",
        "statement": "For every totally real K and prime p, lambda(K,p) = mu(K,p) = 0",
        "screening_criterion": "Necessary condition: p | h(K)",
        "database": "LMFDB nf_fields, 22.2M rows",
        "totally_real_count": total,
        "totally_real_by_degree": by_degree,
        "survivors_by_prime": prime_counts,
        "multiple_prime_survivors": multi_prime["by_count"],
        "p2_valuation_depth": {k: v for k, v in valuation.items()
                               if k != "8|h_by_degree"},
        "interpretation": {
            "what_these_are": "Fields where Greenberg COULD fail (necessary condition met)",
            "what_these_are_NOT": "These are NOT counterexamples to Greenberg",
            "next_step": "Compute Iwasawa lambda via p-adic L-function for survivors",
            "key_observation": "Fields with deep p-adic valuation (e.g. 32|h) are "
                               "the strongest candidates — the tower has more work to do",
        },
    }
    return summary


def main():
    t0 = time.time()
    conn = connect()
    cur = conn.cursor()

    # Task 1
    by_degree, total = task1_count_by_degree(cur)

    # Task 2
    prime_counts = task2_prime_divisibility(cur, total)

    # Task 3
    cross_tab = task3_cross_tabulate(cur)

    # Task 4
    multi_prime = task4_multiple_primes(cur)

    # Task 5
    valuation = task5_p2_valuation_depth(cur)

    # Task 6
    properties = task6_greenberg_properties(cur)

    # Task 7
    summary = task7_summary(total, by_degree, prime_counts,
                            multi_prime, valuation)

    # Assemble full results
    full_results = {
        "report": "Aporia Deep Research #11: Greenberg Iwasawa Screening",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "runtime_seconds": round(time.time() - t0, 1),
        "summary": summary,
        "detail": {
            "cross_tabulation": {str(k): v for k, v in cross_tab.items()},
            "multiple_prime_examples": multi_prime["examples_ge3"],
            "valuation_depth_by_degree": valuation.get("8|h_by_degree", {}),
            "survivor_properties": properties,
        },
    }

    # Convert all dict keys to strings for JSON
    def stringify_keys(obj):
        if isinstance(obj, dict):
            return {str(k): stringify_keys(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [stringify_keys(i) for i in obj]
        return obj

    full_results = stringify_keys(full_results)

    out_path = "F:/Prometheus/charon/data/greenberg_screen.json"
    with open(out_path, "w") as f:
        json.dump(full_results, f, indent=2)
    print(f"\nResults saved to {out_path}")
    print(f"Total runtime: {time.time() - t0:.1f}s")

    conn.close()


if __name__ == "__main__":
    main()

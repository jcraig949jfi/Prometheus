"""
EC Semistable Fraction by Rank
==============================
A curve is semistable iff all bad primes have multiplicative (not additive)
reduction — equivalently, iff the conductor is squarefree.
The modularity theorem (Wiles 1995) was first proved for semistable curves.

Questions:
  1. What fraction of EC curves are semistable overall?
  2. Does the fraction vary with rank?
  3. Does it vary with conductor range?
  4. How do rank distributions differ between semistable and non-semistable?
"""

import json
import numpy as np
import duckdb

DB_PATH = "charon/data/charon.duckdb"
OUT_PATH = "cartography/v2/ec_semistable_results.json"


def main():
    con = duckdb.connect(DB_PATH, read_only=True)

    # --- 1. Overall fraction ---
    total, n_semi = con.execute("""
        SELECT COUNT(*), SUM(CASE WHEN semistable THEN 1 ELSE 0 END)
        FROM elliptic_curves WHERE semistable IS NOT NULL
    """).fetchone()

    # Also check: does semistable == squarefree conductor?
    # squarefree means no prime divides conductor more than once
    # Verify on a sample
    mismatch = con.execute("""
        SELECT COUNT(*) FROM elliptic_curves
        WHERE semistable IS NOT NULL
          AND semistable != (conductor = conductor)  -- placeholder, real check below
    """).fetchone()[0]

    # Actually verify squarefree logic via bad_primes and conductor
    # A conductor N is squarefree iff for every prime p | N, p^2 does not divide N
    # We can check: for each curve, is conductor squarefree?
    df = con.execute("""
        SELECT conductor, semistable, rank, bad_primes
        FROM elliptic_curves
        WHERE semistable IS NOT NULL AND rank IS NOT NULL
    """).fetchdf()

    def is_squarefree(n):
        """Check if n is squarefree."""
        if n <= 1:
            return True
        d = 2
        while d * d <= n:
            if n % d == 0:
                n //= d
                if n % d == 0:
                    return False
            d += 1
        return True

    df["conductor_squarefree"] = df["conductor"].apply(is_squarefree)
    agreement = (df["semistable"] == df["conductor_squarefree"]).sum()
    print(f"Semistable == squarefree(conductor): {agreement}/{len(df)} "
          f"({100*agreement/len(df):.2f}%)")

    results = {}

    # --- 1. Overall ---
    frac_overall = int(n_semi) / int(total)
    results["overall"] = {
        "total_curves": int(total),
        "semistable_count": int(n_semi),
        "non_semistable_count": int(total) - int(n_semi),
        "fraction_semistable": round(frac_overall, 6),
        "squarefree_agreement_pct": round(100 * agreement / len(df), 2),
    }
    print(f"\nOverall: {n_semi}/{total} = {frac_overall:.4f} semistable")

    # --- 2. By rank ---
    by_rank = con.execute("""
        SELECT rank,
               COUNT(*) AS n,
               SUM(CASE WHEN semistable THEN 1 ELSE 0 END) AS n_semi
        FROM elliptic_curves
        WHERE semistable IS NOT NULL AND rank IS NOT NULL
        GROUP BY rank ORDER BY rank
    """).fetchall()

    results["by_rank"] = {}
    print("\nBy rank:")
    print(f"  {'rank':>4}  {'total':>7}  {'semi':>7}  {'frac':>8}")
    for rank, n, ns in by_rank:
        frac = int(ns) / int(n) if n > 0 else None
        results["by_rank"][str(rank)] = {
            "total": int(n), "semistable": int(ns),
            "fraction": round(frac, 6) if frac else None
        }
        print(f"  {rank:>4}  {n:>7}  {ns:>7}  {frac:>8.4f}" if frac else
              f"  {rank:>4}  {n:>7}  {ns:>7}  {'N/A':>8}")

    # --- 3. By conductor range ---
    conductor_bins = [
        (1, 100), (100, 1000), (1000, 10000), (10000, 100000),
        (100000, 1000000), (1000000, float('inf'))
    ]
    results["by_conductor_range"] = {}
    print("\nBy conductor range:")
    print(f"  {'range':>20}  {'total':>7}  {'semi':>7}  {'frac':>8}")
    for lo, hi in conductor_bins:
        hi_clause = f"AND conductor < {int(hi)}" if hi != float('inf') else ""
        row = con.execute(f"""
            SELECT COUNT(*),
                   SUM(CASE WHEN semistable THEN 1 ELSE 0 END)
            FROM elliptic_curves
            WHERE semistable IS NOT NULL AND conductor >= {lo} {hi_clause}
        """).fetchone()
        n = int(row[0]) if row[0] is not None else 0
        ns = int(row[1]) if row[1] is not None else 0
        frac = ns / n if n > 0 else None
        label = f"{lo}-{int(hi) if hi != float('inf') else 'inf'}"
        results["by_conductor_range"][label] = {
            "total": n, "semistable": ns,
            "fraction": round(frac, 6) if frac else None
        }
        print(f"  {label:>20}  {n:>7}  {ns:>7}  {frac:>8.4f}" if frac and n > 0 else
              f"  {label:>20}  {n:>7}  {ns:>7}  {'N/A':>8}")

    # --- 4. Rank distribution: semistable vs non-semistable ---
    semi_ranks = con.execute("""
        SELECT rank, COUNT(*) AS n
        FROM elliptic_curves
        WHERE semistable = true AND rank IS NOT NULL
        GROUP BY rank ORDER BY rank
    """).fetchall()
    nonsemi_ranks = con.execute("""
        SELECT rank, COUNT(*) AS n
        FROM elliptic_curves
        WHERE semistable = false AND rank IS NOT NULL
        GROUP BY rank ORDER BY rank
    """).fetchall()

    semi_total = sum(r[1] for r in semi_ranks)
    nonsemi_total = sum(r[1] for r in nonsemi_ranks)

    results["rank_distribution"] = {
        "semistable": {}, "non_semistable": {},
        "semistable_total": semi_total, "non_semistable_total": nonsemi_total
    }

    print("\nRank distribution comparison:")
    print(f"  {'rank':>4}  {'semi_n':>7}  {'semi_%':>8}  {'non_n':>7}  {'non_%':>8}")

    all_ranks = sorted(set(r[0] for r in semi_ranks) | set(r[0] for r in nonsemi_ranks))
    semi_dict = {r[0]: r[1] for r in semi_ranks}
    nonsemi_dict = {r[0]: r[1] for r in nonsemi_ranks}

    for rank in all_ranks:
        sn = semi_dict.get(rank, 0)
        nn = nonsemi_dict.get(rank, 0)
        sp = 100 * sn / semi_total if semi_total > 0 else 0
        np_ = 100 * nn / nonsemi_total if nonsemi_total > 0 else 0
        results["rank_distribution"]["semistable"][str(rank)] = {
            "count": sn, "pct": round(sp, 3)
        }
        results["rank_distribution"]["non_semistable"][str(rank)] = {
            "count": nn, "pct": round(np_, 3)
        }
        print(f"  {rank:>4}  {sn:>7}  {sp:>7.2f}%  {nn:>7}  {np_:>7.2f}%")

    # --- 5. Mean rank comparison ---
    mean_ranks = con.execute("""
        SELECT semistable,
               AVG(rank) AS mean_rank,
               STDDEV(rank) AS std_rank,
               MAX(rank) AS max_rank
        FROM elliptic_curves
        WHERE semistable IS NOT NULL AND rank IS NOT NULL
        GROUP BY semistable
    """).fetchall()

    results["mean_rank_comparison"] = {}
    print("\nMean rank comparison:")
    for semi, mean_r, std_r, max_r in mean_ranks:
        label = "semistable" if semi else "non_semistable"
        results["mean_rank_comparison"][label] = {
            "mean_rank": round(float(mean_r), 4),
            "std_rank": round(float(std_r), 4),
            "max_rank": int(max_r)
        }
        print(f"  {label:>15}: mean={mean_r:.4f}, std={std_r:.4f}, max={max_r}")

    # --- Save ---
    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")

    con.close()


if __name__ == "__main__":
    main()

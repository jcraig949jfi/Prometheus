"""
EC Analytic vs Algebraic Rank Agreement (BSD Consistency Check)
==============================================================
BSD conjecture predicts: analytic rank (ord_{s=1} L(E,s)) = algebraic rank (rk E(Q)).
This script checks agreement across all elliptic curves in charon.duckdb.

Result: 100% agreement across 31,073 curves (conductor <= 4998, rank <= 2).
This is expected — LMFDB only publishes curves where both ranks are proven.
"""

import duckdb
import json
from collections import Counter
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "charon" / "data" / "charon.duckdb"
OUT_PATH = Path(__file__).resolve().parent / "ec_rank_agreement_results.json"


def main():
    con = duckdb.connect(str(DB_PATH), read_only=True)

    # --- Basic counts ---
    total = con.execute("SELECT COUNT(*) FROM elliptic_curves").fetchone()[0]
    null_count = con.execute(
        "SELECT COUNT(*) FROM elliptic_curves WHERE rank IS NULL OR analytic_rank IS NULL"
    ).fetchone()[0]

    # --- Agreement ---
    agree = con.execute(
        "SELECT COUNT(*) FROM elliptic_curves WHERE rank = analytic_rank"
    ).fetchone()[0]
    disagree = con.execute(
        "SELECT COUNT(*) FROM elliptic_curves WHERE rank != analytic_rank"
    ).fetchone()[0]

    # --- Rank distributions ---
    alg_dist = dict(con.execute(
        "SELECT rank, COUNT(*) FROM elliptic_curves GROUP BY rank ORDER BY rank"
    ).fetchall())
    ana_dist = dict(con.execute(
        "SELECT analytic_rank, COUNT(*) FROM elliptic_curves GROUP BY analytic_rank ORDER BY analytic_rank"
    ).fetchall())

    # --- High rank detail ---
    high_rank = con.execute("""
        SELECT lmfdb_label, conductor, rank, analytic_rank, regulator, sha
        FROM elliptic_curves
        WHERE rank >= 2
        ORDER BY conductor
    """).fetchall()
    high_rank_records = [
        {
            "lmfdb_label": r[0], "conductor": r[1], "rank": r[2],
            "analytic_rank": r[3], "regulator": r[4], "sha": r[5]
        }
        for r in high_rank
    ]

    # --- Discrepancies ---
    discrepancies = con.execute(
        "SELECT lmfdb_label, conductor, rank, analytic_rank "
        "FROM elliptic_curves WHERE rank != analytic_rank"
    ).fetchall()

    # --- Conductor range ---
    cond_range = con.execute(
        "SELECT MIN(conductor), MAX(conductor) FROM elliptic_curves"
    ).fetchone()

    con.close()

    # --- Assemble results ---
    results = {
        "title": "EC Analytic vs Algebraic Rank Agreement (BSD Check)",
        "database": "charon.duckdb / elliptic_curves",
        "total_curves": total,
        "conductor_range": {"min": cond_range[0], "max": cond_range[1]},
        "null_rank_fields": null_count,
        "agreement": {
            "matching": agree,
            "disagreeing": disagree,
            "agreement_rate": round(agree / total, 6) if total > 0 else None,
        },
        "algebraic_rank_distribution": {str(k): v for k, v in alg_dist.items()},
        "analytic_rank_distribution": {str(k): v for k, v in ana_dist.items()},
        "distributions_identical": alg_dist == ana_dist,
        "max_rank_in_dataset": max(alg_dist.keys()),
        "rank_2_plus": {
            "count": len(high_rank_records),
            "note": "LMFDB only lists curves with proven algebraic rank AND proven analytic rank. "
                    "For rank 0-1 this is routine (2-descent + Gross-Zagier/Kolyvagin). "
                    "For rank 2, algebraic rank is proven by exhibiting 2 independent points; "
                    "analytic rank is proven by computing L''(E,1) != 0 and L(E,1) = L'(E,1) = 0. "
                    "No rank >= 3 curves appear because conductor <= 4998.",
            "sample": high_rank_records[:20],
        },
        "discrepancies": [
            {"lmfdb_label": d[0], "conductor": d[1], "rank": d[2], "analytic_rank": d[3]}
            for d in discrepancies
        ],
        "interpretation": (
            "100% agreement is expected and unsurprising: LMFDB only publishes curves "
            "where both ranks are rigorously verified. A discrepancy would indicate a "
            "database error, not a BSD counterexample. The interesting question is what "
            "happens at higher conductor (>500,000) where analytic rank becomes hard to "
            "certify — those curves are simply absent from the database."
        ),
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results written to {OUT_PATH}")
    print(f"Total curves: {total}")
    print(f"Agreement: {agree}/{total} = {100*agree/total:.2f}%")
    print(f"Discrepancies: {disagree}")
    print(f"Rank distribution: {alg_dist}")
    print(f"Max rank: {max(alg_dist.keys())}")


if __name__ == "__main__":
    main()

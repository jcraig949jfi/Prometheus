"""
EC a_2 Parity Structure Analysis
=================================
For elliptic curves over Q, a_2 = p+1-#E(F_2) where p=2.
By Hasse bound |a_2| <= 2*sqrt(2) ~ 2.83, so a_2 in {-2,-1,0,1,2}.
a_2 mod 2 indicates whether 2 | #E(F_2).

Questions:
  1. Distribution of a_2 values
  2. a_2 vs rank (chi-squared)
  3. a_2 vs torsion structure
  4. a_2 vs CM status
  5. Connection to reduction type at p=2
"""

import json
import numpy as np
import duckdb
from scipy import stats
from collections import Counter
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "charon" / "data" / "charon.duckdb"
OUT_PATH = Path(__file__).resolve().parent / "ec_a2_parity_results.json"


def load_data():
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df = con.execute("""
        SELECT
            aplist[1] AS a2,
            rank,
            torsion,
            torsion_structure,
            cm,
            bad_primes,
            conductor,
            lmfdb_label
        FROM elliptic_curves
        WHERE aplist[1] IS NOT NULL
    """).fetchdf()
    con.close()
    return df


def distribution_analysis(df):
    """1. Distribution of a_2 values."""
    counts = df["a2"].value_counts().sort_index().to_dict()
    total = len(df)
    dist = {int(k): {"count": int(v), "pct": round(100 * v / total, 2)} for k, v in counts.items()}
    # Parity: a_2 even vs odd
    even = df[df["a2"] % 2 == 0]
    odd = df[df["a2"] % 2 != 0]
    parity = {
        "even_count": len(even),
        "odd_count": len(odd),
        "even_pct": round(100 * len(even) / total, 2),
        "odd_pct": round(100 * len(odd) / total, 2),
    }
    # a_2 even means #E(F_2) = 3 - a_2 is odd (so 2 does not divide #E(F_2))
    # a_2 odd means #E(F_2) = 3 - a_2 is even (so 2 | #E(F_2))
    return {"values": dist, "parity": parity, "total": total}


def a2_vs_rank(df):
    """2. Chi-squared test: a_2 vs rank."""
    # Contingency table
    ct = {}
    for _, row in df.iterrows():
        a2 = int(row["a2"])
        r = int(row["rank"])
        ct.setdefault(a2, Counter())[r] += 1
    a2_vals = sorted(ct.keys())
    rank_vals = sorted(set(r for c in ct.values() for r in c))
    table = [[ct.get(a, {}).get(r, 0) for r in rank_vals] for a in a2_vals]
    chi2, p, dof, _ = stats.chi2_contingency(table)

    # Mean rank by a_2
    mean_rank = df.groupby("a2")["rank"].mean().to_dict()
    mean_rank = {int(k): round(v, 4) for k, v in mean_rank.items()}

    # Parity vs rank
    df["a2_parity"] = df["a2"] % 2
    parity_rank = df.groupby("a2_parity")["rank"].mean().to_dict()
    parity_rank = {("even" if int(k) == 0 else "odd"): round(v, 4) for k, v in parity_rank.items()}

    # Chi-squared for parity vs rank
    ct_parity = {}
    for _, row in df.iterrows():
        p_key = "even" if int(row["a2"]) % 2 == 0 else "odd"
        r = int(row["rank"])
        ct_parity.setdefault(p_key, Counter())[r] += 1
    par_keys = sorted(ct_parity.keys())
    rank_vals2 = sorted(set(r for c in ct_parity.values() for r in c))
    table_par = [[ct_parity[pk].get(r, 0) for r in rank_vals2] for pk in par_keys]
    chi2_par, p_par, dof_par, _ = stats.chi2_contingency(table_par)

    return {
        "contingency_a2_vals": a2_vals,
        "contingency_rank_vals": rank_vals,
        "contingency_table": table,
        "chi2": round(chi2, 4),
        "p_value": float(f"{p:.6e}"),
        "dof": dof,
        "mean_rank_by_a2": mean_rank,
        "parity_mean_rank": parity_rank,
        "parity_chi2": round(chi2_par, 4),
        "parity_p_value": float(f"{p_par:.6e}"),
    }


def a2_vs_torsion(df):
    """3. a_2 vs torsion structure."""
    # Torsion group as string
    def tors_str(ts):
        if ts is None or len(ts) == 0:
            return "[1]"
        return str(sorted(ts))
    df["tors_grp"] = df["torsion_structure"].apply(tors_str)

    ct = {}
    for _, row in df.iterrows():
        a2 = int(row["a2"])
        tg = row["tors_grp"]
        ct.setdefault(a2, Counter())[tg] += 1

    # For each a_2, top torsion groups
    result = {}
    for a2 in sorted(ct.keys()):
        total = sum(ct[a2].values())
        top = ct[a2].most_common(5)
        result[int(a2)] = {
            "total": total,
            "top_torsion": {k: {"count": v, "pct": round(100 * v / total, 2)} for k, v in top},
        }

    # Chi-squared on a_2 vs torsion order
    ct2 = {}
    for _, row in df.iterrows():
        a2 = int(row["a2"])
        t = int(row["torsion"])
        ct2.setdefault(a2, Counter())[t] += 1
    a2_vals = sorted(ct2.keys())
    tors_vals = sorted(set(t for c in ct2.values() for t in c))
    table = [[ct2[a].get(t, 0) for t in tors_vals] for a in a2_vals]
    chi2, p, dof, _ = stats.chi2_contingency(table)

    return {
        "a2_torsion_breakdown": result,
        "torsion_order_chi2": round(chi2, 4),
        "torsion_order_p_value": float(f"{p:.6e}"),
        "torsion_order_dof": dof,
    }


def a2_vs_cm(df):
    """4. a_2 vs CM status."""
    df["is_cm"] = df["cm"] != 0
    ct = {}
    for _, row in df.iterrows():
        a2 = int(row["a2"])
        cm = bool(row["is_cm"])
        ct.setdefault(a2, Counter())[cm] += 1

    result = {}
    for a2 in sorted(ct.keys()):
        total = sum(ct[a2].values())
        cm_count = ct[a2].get(True, 0)
        result[int(a2)] = {
            "total": total,
            "cm_count": cm_count,
            "cm_pct": round(100 * cm_count / total, 2) if total > 0 else 0,
        }

    # Chi-squared
    a2_vals = sorted(ct.keys())
    table = [[ct[a].get(True, 0), ct[a].get(False, 0)] for a in a2_vals]
    chi2, p, dof, _ = stats.chi2_contingency(table)

    # CM discriminant breakdown for a_2=0 (supersingular at 2)
    cm_at_0 = df[(df["a2"] == 0) & (df["is_cm"])]["cm"].value_counts().to_dict()
    cm_at_0 = {int(k): int(v) for k, v in cm_at_0.items()}

    return {
        "a2_cm_breakdown": result,
        "chi2": round(chi2, 4),
        "p_value": float(f"{p:.6e}"),
        "cm_discriminants_at_a2_0": cm_at_0,
    }


def reduction_type(df):
    """5. Connection to reduction type at p=2."""
    # a_2 = 0 => supersingular reduction at 2 (if good reduction)
    # If 2 | conductor => bad reduction (additive or multiplicative)
    # If 2 ∤ conductor => good reduction, a_2 tells us ordinary vs supersingular

    def classify(row):
        cond = int(row["conductor"])
        a2 = int(row["a2"])
        bad = row["bad_primes"]
        two_is_bad = (bad is not None and 2 in bad) or (cond % 2 == 0)
        if two_is_bad:
            if a2 == 0:
                return "additive"
            elif abs(a2) == 1:
                # Could still be multiplicative: a_2 = +1 (split) or -1 (non-split)
                return "multiplicative"
            else:
                return "bad_other"
        else:
            if a2 == 0:
                return "good_supersingular"
            else:
                return "good_ordinary"

    df["red_type"] = df.apply(classify, axis=1)
    red_counts = df["red_type"].value_counts().to_dict()
    red_counts = {k: int(v) for k, v in red_counts.items()}

    # a_2 distribution within each reduction type
    red_a2 = {}
    for rt in df["red_type"].unique():
        sub = df[df["red_type"] == rt]
        a2_dist = sub["a2"].value_counts().sort_index().to_dict()
        red_a2[rt] = {int(k): int(v) for k, v in a2_dist.items()}

    # What fraction have bad reduction at 2?
    bad_at_2 = len(df[df["red_type"].str.startswith("good") == False])
    good_at_2 = len(df) - bad_at_2

    return {
        "reduction_type_counts": red_counts,
        "a2_by_reduction_type": red_a2,
        "bad_at_2": bad_at_2,
        "good_at_2": good_at_2,
        "bad_at_2_pct": round(100 * bad_at_2 / len(df), 2),
    }


def main():
    print("Loading data...")
    df = load_data()
    print(f"Loaded {len(df)} curves")

    results = {}

    print("1. Distribution analysis...")
    results["distribution"] = distribution_analysis(df)

    print("2. a_2 vs rank...")
    results["a2_vs_rank"] = a2_vs_rank(df)

    print("3. a_2 vs torsion...")
    results["a2_vs_torsion"] = a2_vs_torsion(df)

    print("4. a_2 vs CM...")
    results["a2_vs_cm"] = a2_vs_cm(df)

    print("5. Reduction type...")
    results["reduction_type"] = reduction_type(df)

    # Summary
    results["summary"] = {
        "total_curves": len(df),
        "a2_values_observed": sorted(df["a2"].unique().tolist()),
        "key_findings": [],
    }

    # Add key findings
    findings = results["summary"]["key_findings"]

    # Distribution finding
    dist = results["distribution"]
    findings.append(
        f"a_2=0 dominates: {dist['values'][0]['pct']}% of curves (supersingular/additive at 2)"
    )
    findings.append(
        f"Parity split: {dist['parity']['even_pct']}% even vs {dist['parity']['odd_pct']}% odd"
    )

    # Rank finding
    rv = results["a2_vs_rank"]
    findings.append(
        f"a_2 vs rank chi2={rv['chi2']}, p={rv['p_value']} (dof={rv['dof']})"
    )
    findings.append(f"Mean rank by a_2: {rv['mean_rank_by_a2']}")
    findings.append(
        f"Parity vs rank: {rv['parity_mean_rank']} (chi2={rv['parity_chi2']}, p={rv['parity_p_value']})"
    )

    # Torsion finding
    tv = results["a2_vs_torsion"]
    findings.append(
        f"a_2 vs torsion_order chi2={tv['torsion_order_chi2']}, p={tv['torsion_order_p_value']}"
    )

    # CM finding
    cv = results["a2_vs_cm"]
    findings.append(f"a_2 vs CM chi2={cv['chi2']}, p={cv['p_value']}")

    # Reduction type finding
    rt = results["reduction_type"]
    findings.append(
        f"Bad reduction at 2: {rt['bad_at_2_pct']}% of curves"
    )

    # Save
    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {OUT_PATH}")

    # Print summary
    print("\n=== KEY FINDINGS ===")
    for finding in findings:
        print(f"  - {finding}")


if __name__ == "__main__":
    main()

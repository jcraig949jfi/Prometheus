#!/usr/bin/env python3
"""
EC Tamagawa Product Distribution and Rank Correlation
=====================================================
Fetches Tamagawa products from LMFDB PostgreSQL (ec_mwbsd table),
joins with local DuckDB elliptic_curves data, and analyzes:
  1. Distribution of Tamagawa product (geometric? power law?)
  2. Rank correlation (BSD predicts larger products for higher rank)
  3. Prime vs composite conductor comparison
  4. Most common values
  5. Correlation with conductor, regulator
"""

import json
import sys
import numpy as np
from collections import Counter
from pathlib import Path

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("ERROR: pip install psycopg2-binary")
    sys.exit(1)

import duckdb

# ── 1. Fetch Tamagawa products from LMFDB ──────────────────────────────

LMFDB_CONN = {
    "host": "devmirror.lmfdb.xyz",
    "port": 5432,
    "dbname": "lmfdb",
    "user": "lmfdb",
    "password": "lmfdb",
    "connect_timeout": 30,
}

DUCKDB_PATH = Path(__file__).resolve().parents[1].parent / "charon" / "data" / "charon.duckdb"
OUTPUT_PATH = Path(__file__).resolve().parent / "ec_tamagawa_results.json"


def fetch_tamagawa_data():
    """Fetch Tamagawa products and BSD data for our local EC labels."""
    # Get local labels
    con = duckdb.connect(str(DUCKDB_PATH), read_only=True)
    local = con.execute("""
        SELECT lmfdb_label, conductor, rank, regulator, torsion, sha,
               bad_primes, semistable
        FROM elliptic_curves
    """).fetchdf()
    con.close()
    print(f"Local curves: {len(local)}")

    labels = local["lmfdb_label"].tolist()

    # Fetch from LMFDB PostgreSQL
    pg = psycopg2.connect(**LMFDB_CONN)
    cur = pg.cursor()

    # Batch fetch in chunks
    chunk_size = 5000
    tam_rows = []
    for i in range(0, len(labels), chunk_size):
        chunk = labels[i:i + chunk_size]
        cur.execute(
            "SELECT lmfdb_label, tamagawa_product, special_value, real_period, sha_an "
            "FROM ec_mwbsd WHERE lmfdb_label = ANY(%s)",
            (chunk,)
        )
        tam_rows.extend(cur.fetchall())
        print(f"  Fetched {len(tam_rows)} rows...")

    # Also fetch per-prime Tamagawa numbers
    cur.execute(
        "SELECT lmfdb_label, prime, tamagawa_number, kodaira_symbol, reduction_type "
        "FROM ec_localdata WHERE lmfdb_label = ANY(%s)",
        (labels,)
    )
    local_data_rows = cur.fetchall()
    print(f"  Local data (per-prime): {len(local_data_rows)} rows")

    pg.close()

    return local, tam_rows, local_data_rows


def analyze(local_df, tam_rows, local_data_rows):
    """Run all analyses."""
    import pandas as pd

    # Build Tamagawa product lookup
    tam_map = {}
    for label, tprod, sval, rper, sha_an in tam_rows:
        tam_map[label] = {
            "tamagawa_product": int(tprod),
            "special_value": float(sval),
            "real_period": float(rper),
            "sha_an": float(sha_an),
        }

    # Build per-prime local data
    local_primes = {}
    for label, prime, cp, kodaira, red_type in local_data_rows:
        if label not in local_primes:
            local_primes[label] = []
        local_primes[label].append({
            "prime": int(prime),
            "tamagawa_number": int(cp),
            "kodaira_symbol": kodaira,
            "reduction_type": int(red_type) if red_type is not None else None,
        })

    # Merge
    records = []
    for _, row in local_df.iterrows():
        label = row["lmfdb_label"]
        if label not in tam_map:
            continue
        t = tam_map[label]
        records.append({
            "label": label,
            "conductor": int(row["conductor"]),
            "rank": int(row["rank"]),
            "regulator": float(row["regulator"]) if row["regulator"] else None,
            "torsion": int(row["torsion"]),
            "sha": int(row["sha"]) if row["sha"] else None,
            "semistable": bool(row["semistable"]) if row["semistable"] is not None else None,
            "tamagawa_product": t["tamagawa_product"],
            "special_value": t["special_value"],
            "real_period": t["real_period"],
            "sha_an": t["sha_an"],
            "num_bad_primes": len(row["bad_primes"]) if row["bad_primes"] is not None and len(row["bad_primes"]) > 0 else 0,
        })

    df = pd.DataFrame(records)
    print(f"Merged records: {len(df)}")

    results = {}

    # ── 2. Distribution of Tamagawa product ─────────────────────────────
    tprod_vals = df["tamagawa_product"].values
    results["distribution"] = {
        "count": len(tprod_vals),
        "mean": float(np.mean(tprod_vals)),
        "median": float(np.median(tprod_vals)),
        "std": float(np.std(tprod_vals)),
        "min": int(np.min(tprod_vals)),
        "max": int(np.max(tprod_vals)),
        "percentiles": {
            "25": float(np.percentile(tprod_vals, 25)),
            "50": float(np.percentile(tprod_vals, 50)),
            "75": float(np.percentile(tprod_vals, 75)),
            "90": float(np.percentile(tprod_vals, 90)),
            "95": float(np.percentile(tprod_vals, 95)),
            "99": float(np.percentile(tprod_vals, 99)),
        },
    }

    # Most common values
    counter = Counter(tprod_vals.tolist())
    most_common_20 = counter.most_common(20)
    results["most_common_values"] = [
        {"value": int(v), "count": int(c), "fraction": round(c / len(tprod_vals), 4)}
        for v, c in most_common_20
    ]

    # Test: geometric distribution? Fit geometric parameter
    # P(X=k) = (1-p)^(k-1) * p  for geometric
    # MLE: p = 1/mean
    geo_p = 1.0 / np.mean(tprod_vals)
    results["distribution"]["geometric_p_mle"] = round(float(geo_p), 6)

    # Test: power law? Fit on values >= 1
    vals_pos = tprod_vals[tprod_vals >= 1]
    if len(vals_pos) > 0:
        # MLE for discrete power law: alpha = 1 + n / sum(ln(x / xmin))
        xmin = 1
        log_ratios = np.log(vals_pos / xmin)
        log_ratios = log_ratios[log_ratios > 0]  # exclude x=xmin
        if len(log_ratios) > 0:
            alpha = 1 + len(log_ratios) / np.sum(log_ratios)
            results["distribution"]["power_law_alpha_mle"] = round(float(alpha), 4)

    # Histogram (binned)
    hist_bins = [1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 25, 32, 48, 64, 100, 200, 500, 1000]
    hist_counts = []
    for i in range(len(hist_bins)):
        lo = hist_bins[i]
        hi = hist_bins[i + 1] if i + 1 < len(hist_bins) else float("inf")
        c = int(np.sum((tprod_vals >= lo) & (tprod_vals < hi)))
        hist_counts.append({"range": f"[{lo}, {hi})", "count": c})
    results["distribution"]["histogram"] = hist_counts

    # ── 3. Rank correlation ─────────────────────────────────────────────
    rank_groups = df.groupby("rank")["tamagawa_product"].agg(["mean", "median", "std", "count"])
    results["rank_correlation"] = {}
    for rank_val, row_data in rank_groups.iterrows():
        results["rank_correlation"][str(int(rank_val))] = {
            "mean_tamagawa_product": round(float(row_data["mean"]), 4),
            "median_tamagawa_product": float(row_data["median"]),
            "std": round(float(row_data["std"]), 4) if not np.isnan(row_data["std"]) else 0,
            "count": int(row_data["count"]),
        }

    # Spearman correlation rank vs tamagawa_product
    from scipy import stats
    mask = ~np.isnan(df["tamagawa_product"].values.astype(float))
    spearman_r, spearman_p = stats.spearmanr(
        df.loc[mask, "rank"], df.loc[mask, "tamagawa_product"]
    )
    results["rank_spearman"] = {
        "rho": round(float(spearman_r), 6),
        "p_value": float(spearman_p),
    }

    # ── 4. Prime vs composite conductor ─────────────────────────────────
    from sympy import isprime
    df["conductor_is_prime"] = df["conductor"].apply(lambda c: isprime(c))

    for ctype, label_str in [(True, "prime_conductor"), (False, "composite_conductor")]:
        sub = df[df["conductor_is_prime"] == ctype]
        if len(sub) == 0:
            continue
        tp = sub["tamagawa_product"].values
        results[label_str] = {
            "count": len(sub),
            "mean_tamagawa_product": round(float(np.mean(tp)), 4),
            "median_tamagawa_product": float(np.median(tp)),
            "fraction_equal_1": round(float(np.mean(tp == 1)), 4),
            "mean_rank": round(float(sub["rank"].mean()), 4),
        }

    # ── 5. Correlation with other invariants ────────────────────────────
    results["correlations"] = {}
    for col in ["conductor", "regulator", "torsion"]:
        valid = df[[col, "tamagawa_product"]].dropna()
        if len(valid) < 10:
            continue
        r, p = stats.spearmanr(valid[col], valid["tamagawa_product"])
        results["correlations"][col] = {
            "spearman_rho": round(float(r), 6),
            "p_value": float(p),
            "n": len(valid),
        }

    # Log-conductor correlation
    valid = df[["conductor", "tamagawa_product"]].dropna()
    valid = valid[valid["conductor"] > 0]
    r, p = stats.spearmanr(np.log(valid["conductor"]), valid["tamagawa_product"])
    results["correlations"]["log_conductor"] = {
        "spearman_rho": round(float(r), 6),
        "p_value": float(p),
        "n": len(valid),
    }

    # ── 6. Semistable vs non-semistable ─────────────────────────────────
    for ss, label_str in [(True, "semistable"), (False, "non_semistable")]:
        sub = df[df["semistable"] == ss]
        if len(sub) == 0:
            continue
        tp = sub["tamagawa_product"].values
        results[label_str] = {
            "count": len(sub),
            "mean_tamagawa_product": round(float(np.mean(tp)), 4),
            "median_tamagawa_product": float(np.median(tp)),
            "fraction_equal_1": round(float(np.mean(tp == 1)), 4),
        }

    # ── 7. Per-prime Tamagawa number distribution ───────────────────────
    all_cp = [entry["tamagawa_number"] for entries in local_primes.values() for entry in entries]
    cp_counter = Counter(all_cp)
    results["per_prime_tamagawa_distribution"] = [
        {"value": int(v), "count": int(c), "fraction": round(c / len(all_cp), 4)}
        for v, c in cp_counter.most_common(15)
    ]

    # Kodaira symbol distribution
    all_kodaira = [entry["kodaira_symbol"] for entries in local_primes.values() for entry in entries]
    kod_counter = Counter(all_kodaira)
    results["kodaira_distribution"] = [
        {"symbol": str(v), "count": int(c), "fraction": round(c / len(all_kodaira), 4)}
        for v, c in kod_counter.most_common(15)
    ]

    # ── 8. Extreme Tamagawa products ────────────────────────────────────
    df_sorted = df.sort_values("tamagawa_product", ascending=False)
    top_10 = df_sorted.head(10)
    results["top_10_tamagawa"] = [
        {
            "label": r["label"],
            "tamagawa_product": int(r["tamagawa_product"]),
            "rank": int(r["rank"]),
            "conductor": int(r["conductor"]),
        }
        for _, r in top_10.iterrows()
    ]

    # ── 9. BSD ratio check: tamagawa_product * Omega * regulator / |E(Q)_tors|^2 ──
    # For rank 0: L(E,1) = (tam_prod * Omega * Sha) / torsion^2
    rank0 = df[df["rank"] == 0].copy()
    if len(rank0) > 0:
        rank0["bsd_ratio"] = (
            rank0["tamagawa_product"] * rank0["real_period"] * rank0["sha_an"]
        ) / (rank0["torsion"] ** 2)
        rank0["ratio_vs_lvalue"] = rank0["bsd_ratio"] / rank0["special_value"]
        good = rank0["ratio_vs_lvalue"].dropna()
        results["bsd_rank0_check"] = {
            "count": len(good),
            "mean_ratio": round(float(good.mean()), 6),
            "std_ratio": round(float(good.std()), 6),
            "min_ratio": round(float(good.min()), 6),
            "max_ratio": round(float(good.max()), 6),
            "note": "Should be ~1.0 if BSD holds for rank 0",
        }

    return results


def main():
    print("Fetching Tamagawa data...")
    local_df, tam_rows, local_data_rows = fetch_tamagawa_data()

    print("Analyzing...")
    results = analyze(local_df, tam_rows, local_data_rows)

    # Save
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {OUTPUT_PATH}")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    d = results["distribution"]
    print(f"\nDistribution (n={d['count']}):")
    print(f"  Mean: {d['mean']:.2f}, Median: {d['median']:.0f}, Max: {d['max']}")
    print(f"  Geometric MLE p: {d['geometric_p_mle']:.4f}")
    if "power_law_alpha_mle" in d:
        print(f"  Power law alpha: {d['power_law_alpha_mle']:.2f}")

    print(f"\nMost common values:")
    for item in results["most_common_values"][:10]:
        print(f"  {item['value']:>4d}: {item['count']:>5d} ({item['fraction']:.1%})")

    print(f"\nRank correlation (Spearman):")
    print(f"  rho = {results['rank_spearman']['rho']:.4f}, p = {results['rank_spearman']['p_value']:.2e}")
    print(f"\n  By rank:")
    for rank, data in sorted(results["rank_correlation"].items(), key=lambda x: int(x[0])):
        print(f"    Rank {rank}: mean={data['mean_tamagawa_product']:.2f}, "
              f"median={data['median_tamagawa_product']:.0f}, n={data['count']}")

    if "prime_conductor" in results:
        pc = results["prime_conductor"]
        cc = results["composite_conductor"]
        print(f"\nPrime conductor: n={pc['count']}, mean={pc['mean_tamagawa_product']:.2f}, "
              f"frac=1: {pc['fraction_equal_1']:.1%}")
        print(f"Composite conductor: n={cc['count']}, mean={cc['mean_tamagawa_product']:.2f}, "
              f"frac=1: {cc['fraction_equal_1']:.1%}")

    print(f"\nCorrelations:")
    for col, data in results["correlations"].items():
        print(f"  {col}: rho={data['spearman_rho']:.4f}, p={data['p_value']:.2e}")

    if "bsd_rank0_check" in results:
        bsd = results["bsd_rank0_check"]
        print(f"\nBSD rank-0 check (n={bsd['count']}): "
              f"mean ratio={bsd['mean_ratio']:.6f}, std={bsd['std_ratio']:.6f}")

    print(f"\nTop Tamagawa products:")
    for item in results["top_10_tamagawa"][:5]:
        print(f"  {item['label']}: tam={item['tamagawa_product']}, "
              f"rank={item['rank']}, N={item['conductor']}")


if __name__ == "__main__":
    main()

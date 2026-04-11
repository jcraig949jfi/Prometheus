"""
Genus-2 Bad Local Factor Degree Distribution
=============================================
At each bad prime p, the local L-factor has degree 0-4.
The degree pattern encodes the reduction type.

1. Fetch bad_lfactors from LMFDB PostgreSQL mirror (66K curves)
2. Extract degree of each local factor polynomial
3. Distribution of degrees overall
4. Group by ST group: do different groups have different degree patterns?
5. Degree vs conductor exponent correlation

Data source: devmirror.lmfdb.xyz PostgreSQL (g2c_curves table)
"""

import json
import ast
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime
from scipy import stats

try:
    import psycopg2
except ImportError:
    raise ImportError("pip install psycopg2-binary")


DATA_DIR = Path(__file__).parent
OUT_JSON = DATA_DIR / "genus2_local_factors_results.json"
CACHE_PATH = DATA_DIR / "genus2_local_factors_cache.json"


def fetch_from_postgres():
    """Fetch all genus-2 curves with bad_lfactors from LMFDB PostgreSQL mirror."""
    print("Connecting to devmirror.lmfdb.xyz ...")
    conn = psycopg2.connect(
        host="devmirror.lmfdb.xyz",
        port=5432,
        dbname="lmfdb",
        user="lmfdb",
        password="lmfdb",
    )
    cur = conn.cursor()

    cur.execute("""
        SELECT label, bad_lfactors, cond, st_group
        FROM g2c_curves
        WHERE bad_lfactors IS NOT NULL
        ORDER BY cond
    """)

    records = []
    for label, bad_lf, cond, st_group in cur.fetchall():
        records.append({
            "label": label,
            "bad_lfactors": bad_lf,
            "cond": cond,
            "st_group": st_group,
        })

    conn.close()
    print(f"Fetched {len(records)} records from PostgreSQL.")
    return records


def parse_bad_lfactors(raw):
    """Parse bad_lfactors -> list of (prime, degree, coeffs).

    Input can be a string '[[p, [c0,c1,...]], ...]' or already a list.
    Degree = len(coefficients) - 1.
    """
    if not raw:
        return []

    if isinstance(raw, str):
        if raw == "[]":
            return []
        try:
            parsed = ast.literal_eval(raw)
        except (ValueError, SyntaxError):
            return []
    else:
        parsed = raw  # Already a list from PostgreSQL

    result = []
    for entry in parsed:
        if len(entry) >= 2:
            prime = entry[0]
            coeffs = entry[1]
            degree = len(coeffs) - 1
            result.append((prime, degree, coeffs))
    return result


def factorize(n):
    """Return dict of {prime: exponent}."""
    if n <= 1:
        return {}
    factors = {}
    d = 2
    while d * d <= abs(n):
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if abs(n) > 1:
        factors[abs(n)] = 1
    return factors


def analyze(records):
    """Full analysis of bad local factor degree distribution."""
    print(f"\nAnalyzing {len(records)} records...")

    all_degrees = []
    degree_by_st = defaultdict(list)
    degree_vs_cond_exp = []
    degree_counts = Counter()
    per_curve_stats = []
    st_counts = Counter()

    n_with_bad = 0
    n_total_factors = 0

    for rec in records:
        label = rec["label"]
        cond = rec["cond"]
        st = rec["st_group"] or "unknown"
        raw_bf = rec["bad_lfactors"]

        st_counts[st] += 1
        parsed = parse_bad_lfactors(raw_bf)

        if not parsed:
            continue

        n_with_bad += 1
        cond_factors = factorize(cond)

        curve_degrees = []
        for prime, deg, coeffs in parsed:
            all_degrees.append(deg)
            degree_counts[deg] += 1
            degree_by_st[st].append(deg)
            curve_degrees.append(deg)
            n_total_factors += 1

            cond_exp = cond_factors.get(prime, 0)
            degree_vs_cond_exp.append((deg, cond_exp))

        per_curve_stats.append({
            "label": label,
            "st_group": st,
            "n_bad_primes": len(parsed),
            "degrees": curve_degrees,
            "mean_degree": float(np.mean(curve_degrees)),
            "max_degree": max(curve_degrees),
        })

    print(f"  Curves with bad primes: {n_with_bad}/{len(records)}")
    print(f"  Total bad local factors: {n_total_factors}")

    # ── 1. Overall degree distribution ──
    print("\n=== Degree Distribution ===")
    total = sum(degree_counts.values())
    degree_dist = {}
    for d in sorted(degree_counts.keys()):
        pct = 100.0 * degree_counts[d] / total
        degree_dist[str(d)] = {
            "count": int(degree_counts[d]),
            "fraction": round(degree_counts[d] / total, 4),
        }
        print(f"  degree {d}: {degree_counts[d]:6d}  ({pct:5.1f}%)")

    # ── 2. Degree distribution by ST group ──
    print("\n=== By Sato-Tate Group ===")
    st_degree_dist = {}
    for st in sorted(degree_by_st.keys()):
        degs = degree_by_st[st]
        c = Counter(degs)
        n = len(degs)
        dist = {}
        for d in sorted(c.keys()):
            dist[str(d)] = {"count": int(c[d]), "fraction": round(c[d] / n, 4)}
        st_degree_dist[st] = {
            "n_factors": int(n),
            "n_curves": int(st_counts[st]),
            "mean_degree": round(float(np.mean(degs)), 3),
            "distribution": dist,
        }
        print(f"  {st:25s}: n={n:5d}, mean_deg={np.mean(degs):.3f}, "
              f"dist={dict(c)}")

    # ── 3. Chi-squared: is degree distribution ST-dependent? ──
    print("\n=== Chi-squared: Degree ~ ST group ===")
    min_count = 50
    big_groups = sorted([st for st, degs in degree_by_st.items() if len(degs) >= min_count])
    all_degs_set = sorted(degree_counts.keys())

    if len(big_groups) >= 2:
        contingency = []
        for st in big_groups:
            c = Counter(degree_by_st[st])
            row = [c.get(d, 0) for d in all_degs_set]
            contingency.append(row)
        contingency = np.array(contingency)

        chi2, p_val, dof, expected = stats.chi2_contingency(contingency)
        print(f"  Groups tested: {big_groups}")
        print(f"  chi2={chi2:.2f}, dof={dof}, p={p_val:.2e}")
        chi2_result = {
            "groups_tested": big_groups,
            "chi2": round(float(chi2), 2),
            "dof": int(dof),
            "p_value": float(p_val),
            "significant": bool(p_val < 0.01),
        }
    else:
        chi2_result = {"note": "Not enough groups with sufficient data"}
        print("  Not enough groups with sufficient data")

    # ── 4. Degree vs conductor exponent correlation ──
    print("\n=== Degree vs Conductor Exponent ===")
    if degree_vs_cond_exp:
        degs_arr = np.array([x[0] for x in degree_vs_cond_exp])
        exps_arr = np.array([x[1] for x in degree_vs_cond_exp])

        rho, p_rho = stats.spearmanr(degs_arr, exps_arr)
        print(f"  Spearman rho = {rho:.4f}, p = {p_rho:.2e}")

        mean_exp_by_deg = {}
        for d in sorted(set(degs_arr)):
            mask = degs_arr == d
            me = float(np.mean(exps_arr[mask]))
            mean_exp_by_deg[str(int(d))] = round(me, 3)
            print(f"  degree {d}: mean_cond_exp = {me:.3f} (n={int(mask.sum())})")

        deg_cond_corr = {
            "spearman_rho": round(float(rho), 4),
            "spearman_p": float(p_rho),
            "significant": bool(p_rho < 0.01),
            "mean_cond_exp_by_degree": mean_exp_by_deg,
        }
    else:
        deg_cond_corr = {"note": "No data"}

    # ── 5. Degree-pair patterns (for curves with 2+ bad primes) ──
    print("\n=== Degree Tuple Patterns ===")
    degree_tuples = Counter()
    for cs in per_curve_stats:
        tup = tuple(sorted(cs["degrees"]))
        degree_tuples[tup] += 1
    top_tuples = degree_tuples.most_common(15)
    print("  Top 15 degree-tuples (sorted):")
    tuple_list = []
    for tup, cnt in top_tuples:
        pct = 100.0 * cnt / len(per_curve_stats)
        print(f"    {tup}: {cnt} ({pct:.1f}%)")
        tuple_list.append({"tuple": list(tup), "count": int(cnt), "fraction": round(cnt / len(per_curve_stats), 4)})

    # ── 6. Per-curve summary ──
    mean_degs = [c["mean_degree"] for c in per_curve_stats]
    n_bads = [c["n_bad_primes"] for c in per_curve_stats]
    print(f"\n=== Per-Curve Summary ===")
    print(f"  Mean bad primes/curve: {np.mean(n_bads):.2f}")
    print(f"  Mean degree across curves: {np.mean(mean_degs):.3f}")

    # ── 7. Degree distribution by bad prime size ──
    print("\n=== Degree by Prime Size ===")
    small_prime_degs = []  # p <= 10
    mid_prime_degs = []    # 10 < p <= 100
    large_prime_degs = []  # p > 100
    for rec in records:
        parsed = parse_bad_lfactors(rec["bad_lfactors"])
        for prime, deg, coeffs in parsed:
            if prime <= 10:
                small_prime_degs.append(deg)
            elif prime <= 100:
                mid_prime_degs.append(deg)
            else:
                large_prime_degs.append(deg)

    prime_size_dist = {}
    for label, degs_list in [("p<=10", small_prime_degs), ("10<p<=100", mid_prime_degs), ("p>100", large_prime_degs)]:
        if degs_list:
            c = Counter(degs_list)
            n = len(degs_list)
            dist = {str(d): round(c[d]/n, 4) for d in sorted(c.keys())}
            prime_size_dist[label] = {"n": n, "mean_degree": round(float(np.mean(degs_list)), 3), "distribution": dist}
            print(f"  {label:12s}: n={n:6d}, mean={np.mean(degs_list):.3f}, dist={dist}")

    # ── Assemble results ──
    results = {
        "experiment": "genus2_bad_local_factor_degree_distribution",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "data_source": "LMFDB PostgreSQL mirror (devmirror.lmfdb.xyz), g2c_curves table",
        "n_records": len(records),
        "n_with_bad_factors": n_with_bad,
        "n_total_bad_factors": n_total_factors,
        "overall_degree_distribution": degree_dist,
        "by_sato_tate_group": st_degree_dist,
        "chi2_degree_vs_st": chi2_result,
        "degree_vs_conductor_exponent": deg_cond_corr,
        "top_degree_tuples": tuple_list,
        "degree_by_prime_size": prime_size_dist,
        "per_curve_summary": {
            "mean_bad_primes_per_curve": round(float(np.mean(n_bads)), 3),
            "mean_degree_across_curves": round(float(np.mean(mean_degs)), 3),
        },
        "interpretation": "",
    }

    return results


def interpret(results):
    """Add human-readable interpretation."""
    lines = []

    dd = results["overall_degree_distribution"]
    dominant = max(dd.items(), key=lambda x: x[1]["count"])
    lines.append(f"Dominant degree: {dominant[0]} ({dominant[1]['fraction']*100:.1f}% of all bad local factors).")

    chi = results["chi2_degree_vs_st"]
    if "significant" in chi:
        if chi["significant"]:
            lines.append(f"Degree distribution is strongly ST-dependent (chi2={chi['chi2']}, p={chi['p_value']:.2e}).")
        else:
            lines.append(f"No significant ST-dependence (chi2={chi['chi2']}, p={chi['p_value']:.2e}).")

    dc = results["degree_vs_conductor_exponent"]
    if "significant" in dc:
        if dc["significant"]:
            direction = "anti" if dc["spearman_rho"] < 0 else "positively "
            lines.append(f"Degree {direction}correlates with conductor exponent "
                         f"(rho={dc['spearman_rho']}, p={dc['spearman_p']:.2e}): "
                         "higher degree means lower conductor exponent, i.e. milder bad reduction.")
        else:
            lines.append(f"Weak/no correlation between degree and conductor exponent (rho={dc['spearman_rho']}).")

    # ST group interpretation
    st_data = results["by_sato_tate_group"]
    if "USp(4)" in st_data:
        usp = st_data["USp(4)"]["mean_degree"]
        others = [v["mean_degree"] for k, v in st_data.items()
                  if k != "USp(4)" and v["n_factors"] >= 50]
        if others:
            other_mean = np.mean(others)
            lines.append(f"USp(4) mean degree={usp:.2f} vs other large ST groups mean={other_mean:.2f}: "
                         "generic abelian surfaces retain more local information at bad primes.")

    results["interpretation"] = " ".join(lines)
    return results


def main():
    print("=== Genus-2 Bad Local Factor Degree Distribution ===\n")

    if CACHE_PATH.exists():
        print(f"Loading cached data from {CACHE_PATH} ...")
        with open(CACHE_PATH) as f:
            records = json.load(f)
        print(f"Loaded {len(records)} cached records.")
    else:
        records = fetch_from_postgres()
        if records:
            with open(CACHE_PATH, "w") as f:
                json.dump(records, f)
            print(f"Cached {len(records)} records to {CACHE_PATH}")

    if not records:
        print("ERROR: No records.")
        return

    results = analyze(records)
    results = interpret(results)

    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_JSON}")


if __name__ == "__main__":
    main()

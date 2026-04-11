#!/usr/bin/env python3
"""
Gap Compression in Elliptic Curve Invariants by Rank

Tests whether the universal gap compression discovered in EC rank, genus-2 rank,
and MF dimension (Charon cross-family finding) extends to other EC invariants:
conductor, |discriminant|, regulator, degree (modular), faltings_height, |j-invariant|.

For each invariant X, groups curves by analytic_rank (0, 1, 2), sorts by X within
each group, computes nearest-neighbor gaps normalized by mean spacing, then measures
gap compression (variance ratio) and runs KS tests.

Data source: charon DuckDB (31K curves, conductor <= 5000).
"""

import json
import math
import numpy as np
from pathlib import Path
from scipy import stats

import duckdb

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = REPO_ROOT / "charon" / "data" / "charon.duckdb"
OUT_FILE = Path(__file__).parent / "ec_gap_compression_results.json"


def weierstrass_discriminant(ainvs):
    """Compute minimal discriminant from Weierstrass coefficients [a1,a2,a3,a4,a6]."""
    a1, a2, a3, a4, a6 = ainvs
    b2 = a1**2 + 4*a2
    b4 = 2*a4 + a1*a3
    b6 = a3**2 + 4*a6
    b8 = a1**2*a6 - a1*a3*a4 + a2*a3**2 + 4*a2*a6 - a4**2
    disc = -b2**2*b8 - 8*b4**3 - 27*b6**2 + 9*b2*b4*b6
    return disc


def load_curves():
    """Load EC data from charon DuckDB."""
    db = duckdb.connect(str(DB_PATH), read_only=True)
    rows = db.execute("""
        SELECT analytic_rank, conductor, ainvs, regulator, degree,
               faltings_height, jinv_num, jinv_den
        FROM elliptic_curves
        WHERE analytic_rank IS NOT NULL
    """).fetchall()
    db.close()

    curves = []
    for row in rows:
        rank, cond, ainvs, reg, deg, fh, jn, jd = row
        if ainvs is None or len(ainvs) != 5:
            continue

        disc = weierstrass_discriminant(ainvs)
        abs_disc = abs(disc) if disc != 0 else None

        # j-invariant height = log(max(|num|, |den|))
        j_height = None
        if jn is not None and jd is not None and jd != 0:
            j_height = math.log(max(abs(jn), abs(jd)) + 1)

        curves.append({
            "rank": int(rank),
            "conductor": int(cond),
            "abs_discriminant": abs_disc,
            "regulator": float(reg) if reg is not None else None,
            "degree": int(deg) if deg is not None else None,
            "faltings_height": float(fh) if fh is not None else None,
            "j_height": j_height,
        })

    return curves


def normalized_gaps(values):
    """Sort values, compute nearest-neighbor gaps, normalize by mean spacing."""
    vals = np.array(sorted(values), dtype=np.float64)
    if len(vals) < 10:
        return None
    gaps = np.diff(vals)
    mean_gap = np.mean(gaps)
    if mean_gap <= 0:
        return None
    return gaps / mean_gap


def gap_statistics(gaps):
    """Compute summary statistics for a gap distribution."""
    if gaps is None or len(gaps) < 5:
        return None
    return {
        "n": len(gaps),
        "mean": float(np.mean(gaps)),
        "std": float(np.std(gaps)),
        "variance": float(np.var(gaps)),
        "median": float(np.median(gaps)),
        "skew": float(stats.skew(gaps)),
        "kurtosis": float(stats.kurtosis(gaps)),
        "p10": float(np.percentile(gaps, 10)),
        "p90": float(np.percentile(gaps, 90)),
    }


def analyze_invariant(curves, invariant_name, rank_groups=(0, 1, 2)):
    """Analyze gap compression for one invariant across rank groups."""
    # Group curves by rank, extract invariant values
    by_rank = {}
    for c in curves:
        r = c["rank"]
        if r not in rank_groups:
            continue
        val = c[invariant_name]
        if val is None or not np.isfinite(val) or val <= 0:
            continue
        by_rank.setdefault(r, []).append(val)

    # Use log-scale for heavy-tailed invariants
    use_log = invariant_name in ("conductor", "abs_discriminant", "degree", "j_height")

    gap_data = {}
    gap_arrays = {}
    for r in rank_groups:
        values = by_rank.get(r, [])
        if len(values) < 50:
            continue
        if use_log:
            values = [math.log(v + 1) for v in values]
        gaps = normalized_gaps(values)
        if gaps is None:
            continue
        gap_data[r] = gap_statistics(gaps)
        gap_data[r]["raw_count"] = len(values)
        gap_arrays[r] = gaps

    if len(gap_data) < 2:
        return None

    # Compute compression ratios relative to rank-0
    result = {
        "invariant": invariant_name,
        "log_scale": use_log,
        "rank_stats": {str(r): gap_data[r] for r in sorted(gap_data.keys())},
        "compression_ratios": {},
        "ks_tests": {},
    }

    base_rank = min(gap_data.keys())
    base_var = gap_data[base_rank]["variance"]

    for r in sorted(gap_data.keys()):
        if r == base_rank:
            continue
        ratio = gap_data[r]["variance"] / base_var if base_var > 0 else None
        result["compression_ratios"][f"rank{r}_vs_rank{base_rank}"] = ratio

        # KS test
        ks_stat, ks_p = stats.ks_2samp(gap_arrays[base_rank], gap_arrays[r])
        result["ks_tests"][f"rank{r}_vs_rank{base_rank}"] = {
            "ks_statistic": float(ks_stat),
            "p_value": float(ks_p),
            "significant": ks_p < 0.01,
        }

    # Also compare rank-1 vs rank-2 if both exist
    if 1 in gap_arrays and 2 in gap_arrays:
        ks_stat, ks_p = stats.ks_2samp(gap_arrays[1], gap_arrays[2])
        result["ks_tests"]["rank2_vs_rank1"] = {
            "ks_statistic": float(ks_stat),
            "p_value": float(ks_p),
            "significant": ks_p < 0.01,
        }
        if gap_data[1]["variance"] > 0:
            result["compression_ratios"]["rank2_vs_rank1"] = (
                gap_data[2]["variance"] / gap_data[1]["variance"]
            )

    # Determine if compression is present (variance decreases with rank)
    variances = [(r, gap_data[r]["variance"]) for r in sorted(gap_data.keys())]
    monotonic_decrease = all(
        variances[i][1] >= variances[i+1][1] for i in range(len(variances)-1)
    )
    result["monotonic_compression"] = monotonic_decrease
    result["shows_compression"] = any(
        v < 1.0 for v in result["compression_ratios"].values() if v is not None
    )

    return result


def two_channel_analysis(curves):
    """
    Test the two-channel finding: rank and regulator as separable channels.
    Within each rank, does regulator gap structure differ from conductor gap structure?
    """
    results = {}
    for rank in (0, 1, 2):
        rank_curves = [c for c in curves if c["rank"] == rank]
        if len(rank_curves) < 50:
            continue

        # Get regulator values and conductor values
        reg_vals = [c["regulator"] for c in rank_curves
                    if c["regulator"] is not None and c["regulator"] > 0]
        cond_vals = [math.log(c["conductor"] + 1) for c in rank_curves
                     if c["conductor"] > 0]

        if len(reg_vals) < 50 or len(cond_vals) < 50:
            continue

        reg_gaps = normalized_gaps(reg_vals)
        cond_gaps = normalized_gaps(cond_vals)

        if reg_gaps is None or cond_gaps is None:
            continue

        # Compare gap distributions
        ks_stat, ks_p = stats.ks_2samp(reg_gaps, cond_gaps)

        results[f"rank_{rank}"] = {
            "regulator_gap_var": float(np.var(reg_gaps)),
            "conductor_gap_var": float(np.var(cond_gaps)),
            "variance_ratio_reg_over_cond": float(np.var(reg_gaps) / np.var(cond_gaps))
                if np.var(cond_gaps) > 0 else None,
            "ks_statistic": float(ks_stat),
            "ks_p_value": float(ks_p),
            "channels_separable": ks_p < 0.01,
            "n_regulator": len(reg_vals),
            "n_conductor": len(cond_vals),
        }

    return results


def null_test(curves, invariant_name, n_shuffles=200):
    """
    Permutation null: shuffle rank labels, measure how often we get
    the observed compression ratio by chance. Tests all available comparisons.
    """
    observed = analyze_invariant(curves, invariant_name)
    if observed is None:
        return None

    # Test all compression ratios
    test_results = {}
    for key, observed_ratio in observed["compression_ratios"].items():
        if observed_ratio is None:
            continue

        # Determine which ranks are involved
        # key format: "rankX_vs_rankY"
        parts = key.replace("rank", "").split("_vs_")
        if len(parts) != 2:
            continue
        rank_a, rank_b = int(parts[0]), int(parts[1])
        test_ranks = (rank_a, rank_b)

        valid_curves = [c for c in curves if c[invariant_name] is not None
                        and c[invariant_name] > 0 and c["rank"] in test_ranks]
        ranks = [c["rank"] for c in valid_curves]

        rng = np.random.default_rng(42)
        null_ratios = []

        for _ in range(n_shuffles):
            shuffled_ranks = rng.permutation(ranks)
            shuffled_curves = []
            for c, sr in zip(valid_curves, shuffled_ranks):
                sc = dict(c)
                sc["rank"] = int(sr)
                shuffled_curves.append(sc)

            null_result = analyze_invariant(shuffled_curves, invariant_name,
                                            rank_groups=test_ranks)
            if null_result and key in null_result["compression_ratios"]:
                nr = null_result["compression_ratios"][key]
                if nr is not None:
                    null_ratios.append(nr)

        if not null_ratios:
            continue

        null_arr = np.array(null_ratios)
        p_value = float(np.mean(null_arr <= observed_ratio))

        test_results[key] = {
            "observed_ratio": observed_ratio,
            "null_mean": float(np.mean(null_arr)),
            "null_std": float(np.std(null_arr)),
            "z_score": float((observed_ratio - np.mean(null_arr)) / np.std(null_arr))
                if np.std(null_arr) > 0 else 0.0,
            "p_value_one_sided": p_value,
            "n_shuffles": len(null_ratios),
            "significant": p_value < 0.05,
        }

    return test_results if test_results else None


def main():
    print("Loading curves from charon DuckDB...")
    curves = load_curves()
    print(f"  Loaded {len(curves)} curves")

    rank_counts = {}
    for c in curves:
        rank_counts[c["rank"]] = rank_counts.get(c["rank"], 0) + 1
    print(f"  Rank distribution: {dict(sorted(rank_counts.items()))}")

    invariants = [
        "conductor",
        "abs_discriminant",
        "regulator",
        "degree",
        "faltings_height",
        "j_height",
    ]

    results = {
        "metadata": {
            "total_curves": len(curves),
            "rank_distribution": {str(k): v for k, v in sorted(rank_counts.items())},
            "data_source": "charon DuckDB (LMFDB ec_curvedata)",
            "method": "nearest-neighbor gaps, normalized by mean spacing",
        },
        "invariant_results": {},
        "null_tests": {},
        "two_channel_analysis": {},
        "summary": {},
    }

    # Analyze each invariant
    for inv in invariants:
        print(f"\nAnalyzing {inv}...")
        result = analyze_invariant(curves, inv)
        if result:
            results["invariant_results"][inv] = result

            # Print key findings
            for key, ratio in result["compression_ratios"].items():
                direction = "COMPRESSED" if ratio < 1.0 else "EXPANDED"
                print(f"  {key}: variance ratio = {ratio:.4f} ({direction})")

            for key, ks in result["ks_tests"].items():
                sig = "***" if ks["significant"] else ""
                print(f"  KS {key}: D={ks['ks_statistic']:.4f}, p={ks['p_value']:.2e} {sig}")
        else:
            print(f"  Insufficient data")

    # Null tests for invariants showing compression
    print("\n\nRunning permutation null tests (200 shuffles each)...")
    for inv in invariants:
        if inv in results["invariant_results"]:
            res = results["invariant_results"][inv]
            if res.get("shows_compression"):
                print(f"  Null test for {inv}...")
                null_result = null_test(curves, inv)
                if null_result:
                    results["null_tests"][inv] = null_result
                    for comp_key, nr in null_result.items():
                        print(f"    {comp_key}: z={nr['z_score']:.2f}, "
                              f"p={nr['p_value_one_sided']:.4f} "
                              f"{'(SIGNIFICANT)' if nr['significant'] else '(not sig)'}")

    # Two-channel analysis
    print("\nTwo-channel analysis (regulator vs conductor gap separation)...")
    two_ch = two_channel_analysis(curves)
    results["two_channel_analysis"] = two_ch
    for rank_key, data in two_ch.items():
        print(f"  {rank_key}: reg_var={data['regulator_gap_var']:.4f}, "
              f"cond_var={data['conductor_gap_var']:.4f}, "
              f"ratio={data['variance_ratio_reg_over_cond']:.4f}, "
              f"KS p={data['ks_p_value']:.2e} "
              f"{'(SEPARABLE)' if data['channels_separable'] else ''}")

    # Summary
    compressed = [inv for inv, res in results["invariant_results"].items()
                  if res.get("shows_compression")]
    monotonic = [inv for inv, res in results["invariant_results"].items()
                 if res.get("monotonic_compression")]
    significant_null = [inv for inv, res in results["null_tests"].items()
                        if any(v.get("significant") for v in res.values()
                               if isinstance(v, dict))]

    results["summary"] = {
        "invariants_tested": invariants,
        "invariants_showing_compression": compressed,
        "invariants_monotonic_compression": monotonic,
        "invariants_surviving_null_test": significant_null,
        "two_channel_separable_ranks": [
            k for k, v in two_ch.items() if v.get("channels_separable")
        ],
        "cross_family_comparison": {
            "note": "Previous finding: EC rank d~-0.05, genus-2 rank d~-0.12 to -0.36, MF dim d~-1.0 to -2.3",
            "extension": (
                f"{len(compressed)}/{len(invariants)} invariants show gap compression by rank. "
                f"{len(significant_null)} survive permutation null test."
            ),
        },
    }

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Invariants tested: {len(invariants)}")
    print(f"Showing compression: {len(compressed)} — {compressed}")
    print(f"Monotonic compression: {len(monotonic)} — {monotonic}")
    print(f"Surviving null test: {len(significant_null)} — {significant_null}")

    # Save (handle numpy types)
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.integer,)):
                return int(obj)
            if isinstance(obj, (np.floating,)):
                return float(obj)
            if isinstance(obj, (np.bool_,)):
                return bool(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    with open(OUT_FILE, "w") as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to {OUT_FILE}")


if __name__ == "__main__":
    main()

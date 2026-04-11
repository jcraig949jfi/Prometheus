#!/usr/bin/env python3
"""
Genus-2 Igusa Invariant Distribution Analysis
==============================================
Measure distribution of Igusa-Clebsch invariants [I2, I4, I6, I10] across 66K genus-2 curves.

Data: LMFDB postgres dump with igusa_clebsch_inv, igusa_inv, g2_inv fields.

Analyses:
1. Basic statistics of each I_k
2. Distribution of I10 (discriminant-related)
3. Correlations with conductor, ST group, rank
4. Special invariant values (analogues of j=0, j=1728 for EC)
"""

import json
import sys
import os
from collections import Counter, defaultdict
from fractions import Fraction
from math import log, log10, sqrt, gcd
from pathlib import Path

DUMP_PATH = Path(__file__).resolve().parent.parent / "lmfdb_dump" / "g2c_curves.json"
OUT_PATH = Path(__file__).resolve().parent / "genus2_igusa_results.json"


def _parse_str_list(raw):
    """Parse a string like \"['30','540','-1926','-2563']\" into a Python list of strings."""
    if isinstance(raw, list):
        return raw
    if isinstance(raw, str):
        # Strip outer brackets, split on commas, strip quotes/spaces
        s = raw.strip()
        if s.startswith('[') and s.endswith(']'):
            s = s[1:-1]
        parts = [p.strip().strip("'\"") for p in s.split(',')]
        return parts
    return None


def parse_ic(raw):
    """Parse igusa_clebsch_inv [I2, I4, I6, I10] to list of ints."""
    parts = _parse_str_list(raw)
    if not parts or len(parts) != 4:
        return None
    try:
        return [int(x) for x in parts]
    except (ValueError, TypeError):
        return None


def parse_igusa(raw):
    """Parse igusa_inv [J2,J4,J6,J8,J10] to list of ints."""
    parts = _parse_str_list(raw)
    if not parts or len(parts) != 5:
        return None
    try:
        return [int(x) for x in parts]
    except (ValueError, TypeError):
        return None


def parse_g2_inv(raw):
    """Parse g2_inv (absolute Igusa invariants) from list of rational strings."""
    parts = _parse_str_list(raw)
    if not parts or len(parts) != 3:
        return None
    try:
        return [Fraction(x) for x in parts]
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def percentiles(vals, ps):
    """Compute percentiles from sorted list."""
    n = len(vals)
    if n == 0:
        return {p: None for p in ps}
    result = {}
    for p in ps:
        idx = int(p / 100 * (n - 1))
        result[p] = vals[idx]
    return result


def stats_summary(vals):
    """Compute basic statistics."""
    if not vals:
        return {"count": 0}
    n = len(vals)
    s = sorted(vals)
    mean = sum(vals) / n
    median = s[n // 2]
    variance = sum((x - mean) ** 2 for x in vals) / n if n > 1 else 0
    pcts = percentiles(s, [1, 5, 25, 50, 75, 95, 99])

    # Log-scale stats for absolute values
    abs_vals = [abs(x) for x in vals if x != 0]
    log_abs = [log10(a) for a in abs_vals] if abs_vals else []
    log_mean = sum(log_abs) / len(log_abs) if log_abs else None

    return {
        "count": n,
        "mean": float(mean),
        "median": int(median),
        "std": float(sqrt(variance)),
        "min": int(s[0]),
        "max": int(s[-1]),
        "n_zero": sum(1 for x in vals if x == 0),
        "n_positive": sum(1 for x in vals if x > 0),
        "n_negative": sum(1 for x in vals if x < 0),
        "percentiles": {str(k): int(v) for k, v in pcts.items()},
        "log10_abs_mean": round(log_mean, 3) if log_mean is not None else None,
    }


def main():
    print(f"Loading {DUMP_PATH}...")
    with open(DUMP_PATH, 'r', encoding='utf-8') as f:
        dump = json.load(f)

    records = dump["records"]
    total = len(records)
    print(f"Loaded {total} records")

    # ─── Parse all invariants ────────────────────────────────────────────
    curves = []
    ic_fail = 0
    for rec in records:
        ic = parse_ic(rec.get("igusa_clebsch_inv"))
        igusa = parse_igusa(rec.get("igusa_inv"))
        g2 = parse_g2_inv(rec.get("g2_inv"))

        if ic is None:
            ic_fail += 1
            continue

        curves.append({
            "label": rec.get("label"),
            "ic": ic,        # [I2, I4, I6, I10]
            "igusa": igusa,  # [J2, J4, J6, J8, J10]
            "g2": g2,        # [j1, j2, j3] absolute Igusa
            "cond": rec.get("cond"),
            "st_group": rec.get("st_group"),
            "mw_rank": rec.get("mw_rank"),
            "analytic_rank": rec.get("analytic_rank"),
            "end_alg": rec.get("end_alg"),
            "geom_end_alg": rec.get("geom_end_alg"),
            "aut_grp": rec.get("aut_grp_label"),
            "disc_sign": rec.get("disc_sign"),
        })

    n = len(curves)
    print(f"Parsed {n} curves with Igusa-Clebsch invariants ({ic_fail} failures)")

    results = {"total_curves": total, "parsed_curves": n, "parse_failures": ic_fail}

    # ─── 1. Basic statistics of each I_k ─────────────────────────────────
    print("\n=== 1. IGUSA-CLEBSCH INVARIANT STATISTICS ===")
    ic_names = ["I2", "I4", "I6", "I10"]
    ic_stats = {}
    for i, name in enumerate(ic_names):
        vals = [c["ic"][i] for c in curves]
        s = stats_summary(vals)
        ic_stats[name] = s
        print(f"\n{name}:")
        print(f"  count={s['count']}, zeros={s['n_zero']}, pos={s['n_positive']}, neg={s['n_negative']}")
        print(f"  mean={s['mean']:.1f}, median={s['median']}, std={s['std']:.1f}")
        print(f"  range=[{s['min']}, {s['max']}]")
        print(f"  log10|mean|={s['log10_abs_mean']}")

    results["igusa_clebsch_stats"] = ic_stats

    # ─── 2. I10 Distribution (discriminant-related) ──────────────────────
    print("\n=== 2. I10 DISTRIBUTION ===")
    I10_vals = [c["ic"][3] for c in curves]
    I10_abs = [abs(x) for x in I10_vals]
    I10_log = [log10(a) if a > 0 else None for a in I10_abs]
    I10_log_clean = [x for x in I10_log if x is not None]

    # Sign distribution
    I10_signs = Counter(1 if x > 0 else (-1 if x < 0 else 0) for x in I10_vals)
    print(f"I10 sign distribution: pos={I10_signs[1]}, neg={I10_signs[-1]}, zero={I10_signs[0]}")

    # Histogram of log10|I10| in bins
    if I10_log_clean:
        log_min, log_max = min(I10_log_clean), max(I10_log_clean)
        n_bins = 20
        bin_width = (log_max - log_min) / n_bins if log_max > log_min else 1
        log_hist = Counter()
        for v in I10_log_clean:
            b = int((v - log_min) / bin_width)
            b = min(b, n_bins - 1)
            log_hist[b] += 1

        I10_dist = {
            "sign_distribution": {"positive": I10_signs[1], "negative": I10_signs[-1], "zero": I10_signs[0]},
            "log10_abs_range": [round(log_min, 2), round(log_max, 2)],
            "log10_abs_histogram": {
                f"[{round(log_min + i * bin_width, 2)}, {round(log_min + (i + 1) * bin_width, 2)})": log_hist.get(i, 0)
                for i in range(n_bins)
            }
        }
        print(f"  log10|I10| range: [{log_min:.2f}, {log_max:.2f}]")
    else:
        I10_dist = {"sign_distribution": dict(I10_signs)}

    # Most common I10 values
    I10_counter = Counter(I10_vals)
    I10_top = I10_counter.most_common(20)
    I10_dist["most_common_values"] = [{"value": v, "count": c} for v, c in I10_top]
    print(f"  Most common I10 values:")
    for v, c in I10_top[:10]:
        print(f"    I10={v}: {c} curves")

    results["I10_distribution"] = I10_dist

    # ─── 3. Special invariant values ─────────────────────────────────────
    print("\n=== 3. SPECIAL INVARIANT VALUES ===")
    # Analogues of j=0, j=1728: I2=0, small I4, I6 patterns
    # Key special cases:
    # - I2 = 0: extra automorphisms (like j=0 has Z/6Z)
    # - I10 = 0 would be singular (shouldn't appear)
    # - Small absolute values

    special = {}

    # I2 = 0 cases
    I2_zero = [c for c in curves if c["ic"][0] == 0]
    print(f"\nI2 = 0: {len(I2_zero)} curves ({100 * len(I2_zero) / n:.2f}%)")
    if I2_zero:
        st_of_I2_zero = Counter(c["st_group"] for c in I2_zero)
        aut_of_I2_zero = Counter(c["aut_grp"] for c in I2_zero)
        special["I2_zero"] = {
            "count": len(I2_zero),
            "fraction": round(len(I2_zero) / n, 6),
            "st_groups": dict(st_of_I2_zero.most_common(10)),
            "aut_groups": dict(aut_of_I2_zero.most_common(10)),
        }
        print(f"  ST groups: {dict(st_of_I2_zero.most_common(5))}")
        print(f"  Aut groups: {dict(aut_of_I2_zero.most_common(5))}")

    # Both I2=0 and I4=0
    I2_I4_zero = [c for c in curves if c["ic"][0] == 0 and c["ic"][1] == 0]
    print(f"\nI2 = I4 = 0: {len(I2_I4_zero)} curves")
    if I2_I4_zero:
        st_of_both = Counter(c["st_group"] for c in I2_I4_zero)
        special["I2_I4_zero"] = {
            "count": len(I2_I4_zero),
            "fraction": round(len(I2_I4_zero) / n, 6),
            "st_groups": dict(st_of_both.most_common(10)),
        }
        print(f"  ST groups: {dict(st_of_both.most_common(5))}")

    # I2=I4=I6=0 (y^2 = x^5 + c type)
    I2_I4_I6_zero = [c for c in curves if c["ic"][0] == 0 and c["ic"][1] == 0 and c["ic"][2] == 0]
    print(f"\nI2 = I4 = I6 = 0: {len(I2_I4_I6_zero)} curves")
    if I2_I4_I6_zero:
        special["I2_I4_I6_zero"] = {
            "count": len(I2_I4_I6_zero),
            "labels": [c["label"] for c in I2_I4_I6_zero[:20]],
            "st_groups": dict(Counter(c["st_group"] for c in I2_I4_I6_zero).most_common(5)),
        }

    # Most repeated full IC tuples (analogue of "popular j-invariants")
    ic_tuples = Counter(tuple(c["ic"]) for c in curves)
    ic_repeated = [(t, cnt) for t, cnt in ic_tuples.most_common(30) if cnt > 1]
    print(f"\nMost repeated Igusa-Clebsch tuples:")
    for t, cnt in ic_repeated[:10]:
        print(f"  {list(t)}: {cnt} curves")

    special["most_repeated_ic_tuples"] = [
        {"ic": list(t), "count": cnt} for t, cnt in ic_repeated[:20]
    ]
    special["n_distinct_ic_tuples"] = len(ic_tuples)
    special["n_unique_ic_tuples"] = sum(1 for cnt in ic_tuples.values() if cnt == 1)
    print(f"\nDistinct IC tuples: {len(ic_tuples)} / {n}")
    print(f"Unique (appear once): {special['n_unique_ic_tuples']}")

    # Small I10 (close to singular)
    I10_small = sorted(curves, key=lambda c: abs(c["ic"][3]))[:20]
    special["smallest_I10"] = [
        {"label": c["label"], "ic": c["ic"], "st_group": c["st_group"]}
        for c in I10_small
    ]
    print(f"\nSmallest |I10|:")
    for c in I10_small[:5]:
        print(f"  {c['label']}: I10={c['ic'][3]}, ST={c['st_group']}")

    results["special_values"] = special

    # ─── 4. Correlations with conductor, ST group, rank ──────────────────
    print("\n=== 4. CORRELATIONS ===")

    # 4a. IC stats by ST group
    st_groups = defaultdict(list)
    for c in curves:
        st_groups[c["st_group"]].append(c)

    ic_by_st = {}
    print(f"\nST groups: {len(st_groups)} distinct")
    for sg in sorted(st_groups.keys(), key=lambda x: -len(st_groups[x])):
        group = st_groups[sg]
        if len(group) < 5:
            continue
        ic_medians = {}
        for i, name in enumerate(ic_names):
            vals = [c["ic"][i] for c in group]
            s = sorted(vals)
            ic_medians[name] = {
                "median": int(s[len(s) // 2]),
                "mean_log10_abs": round(
                    sum(log10(abs(x)) for x in vals if x != 0) / max(1, sum(1 for x in vals if x != 0)), 2
                ),
                "n_zero": sum(1 for x in vals if x == 0),
            }
        ic_by_st[sg] = {
            "count": len(group),
            "ic_medians": ic_medians,
        }
        print(f"  {sg} ({len(group)} curves): "
              f"median I2={ic_medians['I2']['median']}, I10={ic_medians['I10']['median']}, "
              f"I2_zeros={ic_medians['I2']['n_zero']}")

    results["ic_by_st_group"] = ic_by_st

    # 4b. IC stats by rank
    ranks = defaultdict(list)
    for c in curves:
        r = c.get("mw_rank")
        if r is not None:
            ranks[r].append(c)

    ic_by_rank = {}
    print(f"\nRanks: {sorted(ranks.keys())}")
    for rank in sorted(ranks.keys()):
        group = ranks[rank]
        ic_means = {}
        for i, name in enumerate(ic_names):
            vals = [c["ic"][i] for c in group]
            abs_vals = [abs(x) for x in vals if x != 0]
            ic_means[name] = {
                "count": len(vals),
                "mean_log10_abs": round(
                    sum(log10(a) for a in abs_vals) / len(abs_vals), 3
                ) if abs_vals else None,
                "n_zero": sum(1 for x in vals if x == 0),
            }
        ic_by_rank[str(rank)] = ic_means
        print(f"  rank {rank} ({len(group)} curves): "
              f"log10|I10| mean={ic_means['I10']['mean_log10_abs']}")

    results["ic_by_rank"] = ic_by_rank

    # 4c. Conductor vs I10 correlation
    cond_I10_data = [(c["cond"], abs(c["ic"][3])) for c in curves if c["cond"] and c["ic"][3] != 0]
    if cond_I10_data:
        log_cond = [log10(x[0]) for x in cond_I10_data]
        log_I10 = [log10(x[1]) for x in cond_I10_data]
        n_corr = len(log_cond)
        mean_lc = sum(log_cond) / n_corr
        mean_li = sum(log_I10) / n_corr
        cov = sum((log_cond[i] - mean_lc) * (log_I10[i] - mean_li) for i in range(n_corr)) / n_corr
        var_lc = sum((x - mean_lc) ** 2 for x in log_cond) / n_corr
        var_li = sum((x - mean_li) ** 2 for x in log_I10) / n_corr
        corr = cov / sqrt(var_lc * var_li) if var_lc > 0 and var_li > 0 else 0

        results["conductor_I10_correlation"] = {
            "pearson_r_log10": round(corr, 4),
            "n_pairs": n_corr,
            "interpretation": "log10(conductor) vs log10(|I10|)",
        }
        print(f"\nlog10(cond) vs log10|I10|: r = {corr:.4f} (n={n_corr})")

    # 4d. I2=0 enrichment in special ST groups
    print("\n=== 5. AUTOMORPHISM-IGUSA CONNECTION ===")
    aut_groups = defaultdict(list)
    for c in curves:
        aut_groups[c["aut_grp"]].append(c)

    aut_igusa = {}
    for ag in sorted(aut_groups.keys(), key=lambda x: -len(aut_groups[x])):
        group = aut_groups[ag]
        if len(group) < 3:
            continue
        i2_zero_frac = sum(1 for c in group if c["ic"][0] == 0) / len(group)
        aut_igusa[ag] = {
            "count": len(group),
            "I2_zero_fraction": round(i2_zero_frac, 4),
            "st_groups": dict(Counter(c["st_group"] for c in group).most_common(5)),
        }
        print(f"  Aut {ag} ({len(group)} curves): I2=0 fraction={i2_zero_frac:.3f}")

    results["automorphism_igusa"] = aut_igusa

    # 4e. Endomorphism algebra vs Igusa
    print("\n=== 6. ENDOMORPHISM ALGEBRA VS IGUSA ===")
    end_alg_groups = defaultdict(list)
    for c in curves:
        ea = c.get("end_alg")
        if ea:
            end_alg_groups[ea].append(c)

    end_alg_igusa = {}
    for ea in sorted(end_alg_groups.keys(), key=lambda x: -len(end_alg_groups[x])):
        group = end_alg_groups[ea]
        i2_zero = sum(1 for c in group if c["ic"][0] == 0)
        I10_abs_vals = [abs(c["ic"][3]) for c in group if c["ic"][3] != 0]
        log_I10_mean = sum(log10(a) for a in I10_abs_vals) / len(I10_abs_vals) if I10_abs_vals else None
        end_alg_igusa[ea] = {
            "count": len(group),
            "I2_zero_count": i2_zero,
            "I2_zero_fraction": round(i2_zero / len(group), 4),
            "mean_log10_I10": round(log_I10_mean, 3) if log_I10_mean else None,
        }
        print(f"  {ea} ({len(group)}): I2=0: {i2_zero} ({100 * i2_zero / len(group):.1f}%), "
              f"log10|I10| mean={log_I10_mean:.2f}" if log_I10_mean else f"  {ea}: no data")

    results["endomorphism_algebra_igusa"] = end_alg_igusa

    # ─── 5. Absolute Igusa invariants (g2_inv) ───────────────────────────
    print("\n=== 7. ABSOLUTE IGUSA INVARIANTS (g2_inv) ===")
    g2_curves = [c for c in curves if c["g2"] is not None]
    print(f"Curves with g2_inv: {len(g2_curves)} / {n}")

    if g2_curves:
        # Check for repeated absolute invariants (isomorphic curves over Qbar)
        g2_tuples = Counter(tuple(str(x) for x in c["g2"]) for c in g2_curves)
        g2_repeated = [(t, cnt) for t, cnt in g2_tuples.most_common(20) if cnt > 1]
        print(f"Distinct g2_inv tuples: {len(g2_tuples)}")
        print(f"Repeated (>1 curve): {sum(1 for _, c in g2_repeated)}")
        if g2_repeated:
            print("Most repeated absolute Igusa invariants:")
            for t, cnt in g2_repeated[:5]:
                print(f"  {list(t)}: {cnt} curves")

        results["absolute_igusa"] = {
            "n_with_g2_inv": len(g2_curves),
            "n_distinct": len(g2_tuples),
            "n_repeated": sum(1 for _, c in g2_repeated),
            "most_repeated": [
                {"g2_inv": list(t), "count": cnt} for t, cnt in g2_repeated[:10]
            ],
        }

    # ─── Summary ─────────────────────────────────────────────────────────
    print("\n=== SUMMARY ===")
    print(f"Total curves: {total}")
    print(f"Parsed with IC: {n}")
    print(f"Distinct IC tuples: {special['n_distinct_ic_tuples']}")
    n_I2_zero = len(I2_zero) if I2_zero else 0
    print(f"I2=0 (extra automorphisms): {n_I2_zero} ({100 * n_I2_zero / n:.2f}%)")
    print(f"I2=I4=0: {len(I2_I4_zero)}")
    print(f"I2=I4=I6=0: {len(I2_I4_I6_zero)}")
    if "conductor_I10_correlation" in results:
        print(f"Conductor-I10 correlation (log): r={results['conductor_I10_correlation']['pearson_r_log10']}")

    results["summary"] = {
        "key_findings": [
            f"{n} curves analyzed with Igusa-Clebsch invariants [I2, I4, I6, I10]",
            f"I2=0 in {n_I2_zero} curves ({100 * n_I2_zero / n:.2f}%) — analogous to j=0 for EC (extra automorphisms)",
            f"I2=I4=0 in {len(I2_I4_zero)} curves — higher symmetry stratum",
            f"I2=I4=I6=0 in {len(I2_I4_I6_zero)} curves — maximal symmetry (y^2=x^5+c type)",
            f"{special['n_distinct_ic_tuples']} distinct IC tuples out of {n} curves",
            f"Conductor-I10 log-correlation: r={results.get('conductor_I10_correlation', {}).get('pearson_r_log10', 'N/A')}",
        ]
    }

    # ─── Save ────────────────────────────────────────────────────────────
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()

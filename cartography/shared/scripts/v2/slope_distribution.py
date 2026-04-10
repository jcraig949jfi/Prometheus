#!/usr/bin/env python3
"""
Gouvêa-Mazur Slope Distribution — Mapping the p-adic Eigencurve

For each weight-2 newform with dim=1 (rational eigenvalues), compute
the p-adic valuation v_p(a_p) for small primes p, then analyze:
  - Slope distributions per prime
  - Ordinary vs supersingular fractions
  - Level dependence (p | N vs p  ndiv N, and p^k || N)
  - Eigencurve cross-sections
  - Higher-weight comparison from Hecke algebra orbits

Charon / Project Prometheus — 2026-04-09
"""

import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import duckdb

# ── Config ──────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[4]  # F:\Prometheus
DB_PATH = REPO_ROOT / "charon" / "data" / "charon.duckdb"
HECKE_ALGEBRAS_PATH = REPO_ROOT / "cartography" / "lmfdb_dump" / "hecke_algebras.json"
HECKE_ORBITS_PATH = REPO_ROOT / "cartography" / "lmfdb_dump" / "hecke_orbits.json"
OUT_PATH = Path(__file__).resolve().parent / "slope_distribution_results.json"

PRIMES_SMALL = [2, 3, 5, 7, 11, 13]
PRIMES_ALL = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
              53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
INFINITY_SENTINEL = 99


def v_p(n, p):
    """p-adic valuation of integer n. Returns INFINITY_SENTINEL if n == 0."""
    if n == 0:
        return INFINITY_SENTINEL
    n = int(n)
    v = 0
    while n % p == 0:
        n //= p
        v += 1
    return v


def ord_p_in_N(N, p):
    """How many times p divides N."""
    if N == 0:
        return 0
    v = 0
    while N % p == 0:
        N //= p
        v += 1
    return v


# ── 1. Load modular forms (dim=1, weight=2) ────────────────────────
def load_forms():
    con = duckdb.connect(str(DB_PATH), read_only=True)
    rows = con.execute(
        "SELECT lmfdb_label, level, traces FROM modular_forms WHERE dim = 1"
    ).fetchall()
    con.close()
    print(f"Loaded {len(rows)} dim-1 weight-2 forms from DuckDB")
    return rows


# ── 2. Compute slopes ──────────────────────────────────────────────
def compute_slopes(rows):
    """For each form, compute v_p(a_p) for all small primes."""
    # slopes[p] = list of (level, v_p_value, a_p_value)
    slopes = {p: [] for p in PRIMES_SMALL}
    for label, level, traces in rows:
        if traces is None or len(traces) < 97:
            continue
        for p in PRIMES_SMALL:
            a_p = int(traces[p - 1])
            val = v_p(a_p, p)
            slopes[p].append((level, val, a_p))
    return slopes


# ── 3. Slope distribution per prime ────────────────────────────────
def analyze_distributions(slopes):
    results = {}
    for p in PRIMES_SMALL:
        data = slopes[p]
        n = len(data)
        if n == 0:
            continue

        # Count slope values
        val_counts = Counter(val for _, val, _ in data)
        ordinary = val_counts.get(0, 0)
        supersingular = n - ordinary
        # Finite slopes only (exclude v_p = infinity sentinel)
        finite_slopes = [val for _, val, _ in data if val < INFINITY_SENTINEL]
        inf_count = n - len(finite_slopes)

        # Distribution of finite slopes
        slope_dist = {}
        for v, c in sorted(val_counts.items()):
            key = str(v) if v < INFINITY_SENTINEL else "inf"
            slope_dist[key] = c

        # Mean finite slope
        mean_slope = sum(finite_slopes) / len(finite_slopes) if finite_slopes else None

        results[str(p)] = {
            "total_forms": n,
            "ordinary_count": ordinary,
            "ordinary_fraction": round(ordinary / n, 6),
            "supersingular_count": supersingular,
            "a_p_zero_count": inf_count,
            "slope_distribution": slope_dist,
            "mean_finite_slope": round(mean_slope, 6) if mean_slope is not None else None,
            "max_finite_slope": max(finite_slopes) if finite_slopes else None,
        }

        print(f"\n  p = {p}: {n} forms")
        print(f"    Ordinary (v_p=0): {ordinary} ({100*ordinary/n:.1f}%)")
        print(f"    a_p = 0 (v_p=inf): {inf_count} ({100*inf_count/n:.1f}%)")
        print(f"    Slope dist: { {k: v for k, v in sorted(slope_dist.items(), key=lambda x: (x[0]=='inf', x[0]))} }")
        if mean_slope is not None:
            print(f"    Mean finite slope: {mean_slope:.4f}")

    return results


# ── 4. Level dependence ────────────────────────────────────────────
def analyze_level_dependence(slopes):
    results = {}
    for p in PRIMES_SMALL:
        data = slopes[p]
        if not data:
            continue

        # Split: p | level vs p  ndiv level
        divides = [(lvl, val, ap) for lvl, val, ap in data if lvl % p == 0]
        not_divides = [(lvl, val, ap) for lvl, val, ap in data if lvl % p != 0]

        def stats(subset, label):
            n = len(subset)
            if n == 0:
                return {"count": 0}
            ord_count = sum(1 for _, v, _ in subset if v == 0)
            inf_count = sum(1 for _, v, _ in subset if v >= INFINITY_SENTINEL)
            finite = [v for _, v, _ in subset if v < INFINITY_SENTINEL]
            return {
                "count": n,
                "ordinary_fraction": round(ord_count / n, 6),
                "a_p_zero_fraction": round(inf_count / n, 6),
                "mean_finite_slope": round(sum(finite) / len(finite), 6) if finite else None,
            }

        # Further split by ord_p(level)
        by_k = defaultdict(list)
        for lvl, val, ap in divides:
            k = ord_p_in_N(lvl, p)
            by_k[k].append((lvl, val, ap))

        k_analysis = {}
        for k in sorted(by_k.keys()):
            k_analysis[str(k)] = stats(by_k[k], f"k={k}")

        results[str(p)] = {
            "p_divides_level": stats(divides, "p|N"),
            "p_not_divides_level": stats(not_divides, "p ndivN"),
            "by_ord_p_of_level": k_analysis,
        }

        print(f"\n  p = {p}:")
        s1 = stats(divides, "p|N")
        s2 = stats(not_divides, "p ndivN")
        print(f"    p|N: {s1['count']} forms, ordinary {s1.get('ordinary_fraction','N/A')}, "
              f"mean slope {s1.get('mean_finite_slope','N/A')}")
        print(f"    p ndivN: {s2['count']} forms, ordinary {s2.get('ordinary_fraction','N/A')}, "
              f"mean slope {s2.get('mean_finite_slope','N/A')}")
        for k in sorted(by_k.keys()):
            ks = k_analysis[str(k)]
            print(f"      ord_p(N)={k}: {ks['count']} forms, ordinary {ks.get('ordinary_fraction','N/A')}")

    return results


# ── 5. Eigencurve cross-section (slopes vs level at fixed p) ──────
def eigencurve_cross_section(slopes):
    """For each prime p, bin slopes by level and look for structure."""
    results = {}
    for p in PRIMES_SMALL:
        data = slopes[p]
        if not data:
            continue

        # Group by level, record slope distribution at each level
        by_level = defaultdict(list)
        for lvl, val, ap in data:
            by_level[lvl].append(val)

        # For eigencurve analysis: find levels with multiple forms
        multi_levels = {lvl: vals for lvl, vals in by_level.items() if len(vals) >= 2}

        # Look for "slope gaps" — missing slopes between observed ones
        all_finite = sorted(set(v for _, v, _ in data if v < INFINITY_SENTINEL))
        gap_info = []
        for i in range(len(all_finite) - 1):
            if all_finite[i + 1] - all_finite[i] > 1:
                gap_info.append({"between": [all_finite[i], all_finite[i + 1]],
                                 "gap_size": all_finite[i + 1] - all_finite[i]})

        # Slope multiplicity at each level (for levels with p  ndiv N)
        coprime_levels = {lvl: vals for lvl, vals in by_level.items() if lvl % p != 0}
        slope_by_level_summary = []
        for lvl in sorted(coprime_levels.keys())[:20]:  # first 20 for brevity
            vals = coprime_levels[lvl]
            dist = Counter(vals)
            slope_by_level_summary.append({
                "level": lvl,
                "num_forms": len(vals),
                "slope_counts": {str(k): c for k, c in sorted(dist.items())},
            })

        results[str(p)] = {
            "levels_with_multiple_forms": len(multi_levels),
            "total_levels": len(by_level),
            "observed_finite_slopes": all_finite,
            "slope_gaps": gap_info,
            "sample_levels_coprime_to_p": slope_by_level_summary,
        }

    return results


# ── 6. Higher-weight from Hecke orbits ─────────────────────────────
def load_hecke_data():
    with open(HECKE_ALGEBRAS_PATH) as f:
        algebras = json.load(f)
    with open(HECKE_ORBITS_PATH) as f:
        orbits = json.load(f)
    return algebras["records"], orbits["records"]


def analyze_higher_weight(orbits):
    """Extract eigenvalues from dim-1 Hecke orbits and compute slopes at higher weights."""
    results = {}

    for orb in orbits:
        # Only dim-1 orbits (scalar eigenvalues)
        if orb["Zbasis"] != [[1]]:
            continue

        level = orb["level"]
        weight = orb["weight"]
        op_str = orb["hecke_op"]

        # Parse [[ n ]] patterns
        eigenvalues = [int(x) for x in re.findall(r'\[\[\s*(-?\d+)\s*\]\]', op_str)]
        if not eigenvalues:
            continue

        # eigenvalues[n-1] = a_n for T_n
        label = orb["orbit_label"]
        entry = {
            "label": label,
            "level": level,
            "weight": weight,
            "num_eigenvalues": len(eigenvalues),
        }

        slopes_for_entry = {}
        for p in PRIMES_SMALL:
            if p - 1 < len(eigenvalues):
                a_p = eigenvalues[p - 1]
                val = v_p(a_p, p)
                slopes_for_entry[str(p)] = {
                    "a_p": a_p,
                    "v_p": val if val < INFINITY_SENTINEL else "inf",
                    "normalized_slope": round(val / ((weight - 1) / 2), 6) if val < INFINITY_SENTINEL and weight > 1 else None,
                }

        entry["slopes"] = slopes_for_entry
        key = f"N={level}_k={weight}"
        if key not in results:
            results[key] = []
        results[key].append(entry)

    return results


# ── 7. Gouvêa-Mazur ladder check ───────────────────────────────────
def check_ladders(algebras, higher_weight_results):
    """For fixed level, check if slopes form discrete patterns across weights."""
    # Group by level
    by_level = defaultdict(list)
    for key, entries in higher_weight_results.items():
        for e in entries:
            by_level[e["level"]].append(e)

    # Also add weight-2 data marker
    ladders = {}
    for level, entries in sorted(by_level.items()):
        if len(entries) < 2:
            continue
        weights = sorted(set(e["weight"] for e in entries))
        if len(weights) < 2:
            continue

        ladder = {"level": level, "weights": weights, "slopes_by_weight": {}}
        for w in weights:
            w_entries = [e for e in entries if e["weight"] == w]
            for p in PRIMES_SMALL:
                pkey = str(p)
                for e in w_entries:
                    if pkey in e["slopes"]:
                        if pkey not in ladder["slopes_by_weight"]:
                            ladder["slopes_by_weight"][pkey] = {}
                        wkey = str(w)
                        if wkey not in ladder["slopes_by_weight"][pkey]:
                            ladder["slopes_by_weight"][pkey][wkey] = []
                        ladder["slopes_by_weight"][pkey][wkey].append(e["slopes"][pkey])

        ladders[str(level)] = ladder

    return ladders


# ── 8. Theoretical predictions ──────────────────────────────────────
def theoretical_comparison(dist_results, level_results):
    """Compare observed ordinary fractions to Hasse bound expectations."""
    theory = {}
    for p in PRIMES_SMALL:
        pkey = str(p)
        if pkey not in dist_results:
            continue

        d = dist_results[pkey]
        ld = level_results.get(pkey, {})

        # For weight 2: a_p ranges from -2sqrt(p) to 2sqrt(p) (Hasse bound)
        hasse_bound = 2 * math.sqrt(p)
        # Ordinary means p  ndiv a_p. Among integers in [-2sqrt(p), 2sqrt(p)],
        # fraction divisible by p ≈ 1/p (for large a_p range)
        # But a_p=0 is special (supersingular at p)
        total_ints_in_range = int(2 * hasse_bound) + 1
        divisible_by_p = sum(1 for a in range(-int(hasse_bound), int(hasse_bound) + 1) if a % p == 0)
        naive_ordinary_pred = 1 - divisible_by_p / total_ints_in_range

        # Sato-Tate prediction for a_p = 0 fraction: measure of θ = π/2
        # P(a_p = 0) ~ 0 for continuous distribution, but for integers it's ~1/sqrt(p)
        # More precisely, for equidistributed a_p/2sqrt(p) under Sato-Tate (sin^2 θ dθ),
        # the fraction with |a_p| < p is high for small p.

        theory[pkey] = {
            "hasse_bound": round(hasse_bound, 4),
            "integer_range_size": total_ints_in_range,
            "naive_ordinary_prediction": round(naive_ordinary_pred, 6),
            "observed_ordinary_fraction": d["ordinary_fraction"],
            "coprime_ordinary": ld.get("p_not_divides_level", {}).get("ordinary_fraction"),
            "divides_ordinary": ld.get("p_divides_level", {}).get("ordinary_fraction"),
        }

    return theory


# ── Main ────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("Gouvêa-Mazur Slope Distribution Analysis")
    print("=" * 60)

    # 1. Load
    rows = load_forms()

    # 2. Compute slopes
    print("\n-- Slope Distributions --")
    slopes = compute_slopes(rows)
    dist_results = analyze_distributions(slopes)

    # 3. Level dependence
    print("\n-- Level Dependence --")
    level_results = analyze_level_dependence(slopes)

    # 4. Eigencurve cross-section
    print("\n-- Eigencurve Cross-Section --")
    ec_results = eigencurve_cross_section(slopes)

    # 5. Higher-weight data from Hecke orbits
    print("\n-- Higher-Weight Hecke Orbits --")
    algebras, orbits = load_hecke_data()
    higher_weight = analyze_higher_weight(orbits)
    print(f"  Found {sum(len(v) for v in higher_weight.values())} dim-1 orbits across "
          f"{len(higher_weight)} (level, weight) pairs")

    # 6. Ladder check
    ladders = check_ladders(algebras, higher_weight)
    print(f"  Levels with multi-weight data: {len(ladders)}")

    # 7. Theory comparison
    print("\n-- Theoretical Comparison --")
    theory = theoretical_comparison(dist_results, level_results)
    for p in PRIMES_SMALL:
        pkey = str(p)
        if pkey in theory:
            t = theory[pkey]
            print(f"  p={p}: observed ordinary={t['observed_ordinary_fraction']:.4f}, "
                  f"naive prediction={t['naive_ordinary_prediction']:.4f}, "
                  f"coprime-level ordinary={t.get('coprime_ordinary', 'N/A')}")

    # ── Assemble full results ──
    full_results = {
        "metadata": {
            "date": "2026-04-09",
            "description": "Gouvêa-Mazur slope distribution for weight-2 dim-1 modular forms",
            "num_forms": len(rows),
            "primes_analyzed": PRIMES_SMALL,
            "db_path": str(DB_PATH),
        },
        "slope_distributions": dist_results,
        "level_dependence": level_results,
        "eigencurve_cross_section": {
            p: {k: v for k, v in ec_results[p].items() if k != "sample_levels_coprime_to_p"}
            for p in ec_results
        },
        "eigencurve_samples": {
            p: ec_results[p].get("sample_levels_coprime_to_p", [])
            for p in ec_results
        },
        "higher_weight_orbits": higher_weight,
        "gouvea_mazur_ladders": ladders,
        "theoretical_comparison": theory,
    }

    # ── Summary statistics ──
    summary = {}
    for p in PRIMES_SMALL:
        pkey = str(p)
        if pkey not in dist_results:
            continue
        d = dist_results[pkey]
        ld = level_results.get(pkey, {})
        summary[pkey] = {
            "ordinary_fraction_overall": d["ordinary_fraction"],
            "ordinary_when_p_coprime_to_N": ld.get("p_not_divides_level", {}).get("ordinary_fraction"),
            "ordinary_when_p_divides_N": ld.get("p_divides_level", {}).get("ordinary_fraction"),
            "a_p_zero_fraction": round(d["a_p_zero_count"] / d["total_forms"], 6),
            "mean_finite_slope": d["mean_finite_slope"],
            "key_finding": "",
        }
        # Note key findings
        coprime_ord = ld.get("p_not_divides_level", {}).get("ordinary_fraction")
        div_ord = ld.get("p_divides_level", {}).get("ordinary_fraction")
        if coprime_ord is not None and div_ord is not None:
            if coprime_ord > div_ord + 0.1:
                summary[pkey]["key_finding"] = (
                    f"Strong level effect: ordinary fraction drops from "
                    f"{coprime_ord:.3f} (p ndivN) to {div_ord:.3f} (p|N)"
                )
            elif abs(coprime_ord - div_ord) < 0.05:
                summary[pkey]["key_finding"] = "Minimal level effect on ordinary fraction"

    full_results["summary"] = summary

    # Write
    with open(OUT_PATH, "w") as f:
        json.dump(full_results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")
    print(f"File size: {OUT_PATH.stat().st_size / 1024:.1f} KB")

    # ── Final summary ──
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for p in PRIMES_SMALL:
        pkey = str(p)
        if pkey in summary:
            s = summary[pkey]
            print(f"\n  p = {p}:")
            print(f"    Overall ordinary fraction: {s['ordinary_fraction_overall']:.4f}")
            print(f"    Ordinary (p ndivN): {s.get('ordinary_when_p_coprime_to_N', 'N/A')}")
            print(f"    Ordinary (p|N): {s.get('ordinary_when_p_divides_N', 'N/A')}")
            print(f"    a_p=0 fraction: {s['a_p_zero_fraction']:.4f}")
            if s["key_finding"]:
                print(f"    ** {s['key_finding']}")

    if ladders:
        print(f"\n  Gouvêa-Mazur ladders found at {len(ladders)} level(s):")
        for lvl_key, ladder in list(ladders.items())[:5]:
            print(f"    Level {lvl_key}: weights {ladder['weights']}")

    return full_results


if __name__ == "__main__":
    main()

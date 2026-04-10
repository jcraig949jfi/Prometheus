#!/usr/bin/env python3
"""
M13: Knot-Primes Starvation Dictionary
========================================
Arithmetic topology analogy: primes ↔ knots.
Computes residue-class starvation for Alexander and Jones polynomial
coefficients, probes knot determinant mod p structure, and cross-references
with modular form starvation (C02).

Outputs: v2/knot_primes_starvation_results.json
"""

import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
import math
import statistics

SCRIPT_DIR = Path(__file__).resolve().parent
KNOTS_PATH = SCRIPT_DIR.parent.parent.parent / "knots" / "data" / "knots.json"
MF_STARVATION_PATH = SCRIPT_DIR / "residue_starvation_results.json"
OUTPUT_PATH = SCRIPT_DIR / "knot_primes_starvation_results.json"

PRIMES = [2, 3, 5, 7, 11]
STARVATION_THRESHOLD = 0.5  # flag if ratio < 0.5


def load_knots():
    with open(KNOTS_PATH) as f:
        data = json.load(f)
    # Filter to knots with polynomial data
    return [k for k in data["knots"] if k.get("alex_coeffs") and len(k["alex_coeffs"]) > 0]


def load_mf_starvation():
    with open(MF_STARVATION_PATH) as f:
        data = json.load(f)
    return data["starved_forms"]


def compute_starvation(coeffs, primes=PRIMES):
    """Compute residue class starvation for a list of integer coefficients."""
    results = {}
    for p in primes:
        residues = [c % p for c in coeffs]
        classes_hit = set(residues)
        ratio = len(classes_hit) / p
        distribution = Counter(residues)
        missing = sorted(set(range(p)) - classes_hit)
        results[p] = {
            "classes_hit": len(classes_hit),
            "total_classes": p,
            "ratio": round(ratio, 4),
            "hit": sorted(classes_hit),
            "missing": missing,
            "distribution": {str(k): v for k, v in sorted(distribution.items())},
            "starved": ratio < STARVATION_THRESHOLD,
        }
    return results


def analyze_knot_starvation(knots):
    """Task 1 & 2: Compute starvation for Alexander and Jones coefficients."""
    results = []
    for knot in knots:
        name = knot["name"]
        det = knot["determinant"]
        alex = knot.get("alex_coeffs", [])
        jones = knot.get("jones_coeffs", [])

        alex_starv = compute_starvation(alex) if alex else None
        jones_starv = compute_starvation(jones) if jones else None

        entry = {
            "name": name,
            "determinant": det,
            "crossing_number": knot.get("crossing_number", None),
            "n_alex_coeffs": len(alex),
            "n_jones_coeffs": len(jones),
            "alexander_starvation": alex_starv,
            "jones_starvation": jones_starv,
        }
        results.append(entry)
    return results


def starvation_summary(knot_results):
    """Summarize how many knots are starved at each prime, for each poly type."""
    summary = {}
    for poly_key in ["alexander_starvation", "jones_starvation"]:
        label = poly_key.replace("_starvation", "")
        counts = {}
        for p in PRIMES:
            starved = sum(
                1 for r in knot_results
                if r[poly_key] and r[poly_key][p]["starved"]
            )
            total = sum(1 for r in knot_results if r[poly_key] is not None)
            counts[p] = {"starved": starved, "total": total,
                         "fraction": round(starved / total, 4) if total else 0}
        summary[label] = counts
    return summary


def alex_jones_correlation(knot_results):
    """Task 3: For each prime, compute correlation between Alexander and Jones starvation."""
    correlation = {}
    for p in PRIMES:
        both_starved = 0
        alex_only = 0
        jones_only = 0
        neither = 0
        total = 0

        for r in knot_results:
            a = r["alexander_starvation"]
            j = r["jones_starvation"]
            if a is None or j is None:
                continue
            total += 1
            a_s = a[p]["starved"]
            j_s = j[p]["starved"]
            if a_s and j_s:
                both_starved += 1
            elif a_s and not j_s:
                alex_only += 1
            elif not a_s and j_s:
                jones_only += 1
            else:
                neither += 1

        # Compute phi coefficient (Matthews correlation)
        # phi = (n11*n00 - n10*n01) / sqrt((n11+n10)(n01+n00)(n11+n01)(n10+n00))
        n11, n10, n01, n00 = both_starved, alex_only, jones_only, neither
        denom = math.sqrt(
            max((n11 + n10) * (n01 + n00) * (n11 + n01) * (n10 + n00), 1)
        )
        phi = (n11 * n00 - n10 * n01) / denom if denom > 0 else 0

        correlation[p] = {
            "both_starved": both_starved,
            "alex_only": alex_only,
            "jones_only": jones_only,
            "neither": neither,
            "total": total,
            "phi_coefficient": round(phi, 4),
            "interpretation": (
                "correlated" if phi > 0.3 else
                "anti-correlated" if phi < -0.3 else
                "independent"
            ),
        }
    return correlation


def determinant_mod_analysis(knot_results):
    """Task 4: Compute det(K) mod p and compare polynomial starvation."""
    analysis = {}
    for p in PRIMES:
        divisible = []  # p | det
        not_divisible = []  # p ∤ det

        for r in knot_results:
            det = r["determinant"]
            if det is None:
                continue
            if det % p == 0:
                divisible.append(r)
            else:
                not_divisible.append(r)

        # For each group, compute average starvation ratio
        def avg_ratio(group, poly_key):
            ratios = [
                r[poly_key][p]["ratio"]
                for r in group
                if r[poly_key] is not None
            ]
            return round(statistics.mean(ratios), 4) if ratios else None

        def starved_frac(group, poly_key):
            vals = [
                r[poly_key][p]["starved"]
                for r in group
                if r[poly_key] is not None
            ]
            return round(sum(vals) / len(vals), 4) if vals else None

        analysis[p] = {
            "n_divisible": len(divisible),
            "n_not_divisible": len(not_divisible),
            "divisible_alex_avg_ratio": avg_ratio(divisible, "alexander_starvation"),
            "divisible_jones_avg_ratio": avg_ratio(divisible, "jones_starvation"),
            "not_div_alex_avg_ratio": avg_ratio(not_divisible, "alexander_starvation"),
            "not_div_jones_avg_ratio": avg_ratio(not_divisible, "jones_starvation"),
            "divisible_alex_starved_frac": starved_frac(divisible, "alexander_starvation"),
            "divisible_jones_starved_frac": starved_frac(divisible, "jones_starvation"),
            "not_div_alex_starved_frac": starved_frac(not_divisible, "alexander_starvation"),
            "not_div_jones_starved_frac": starved_frac(not_divisible, "jones_starvation"),
        }
    return analysis


def det_residue_class_distribution(knot_results):
    """Which residue classes do knot determinants hit at each prime?"""
    dist = {}
    for p in PRIMES:
        classes = Counter()
        for r in knot_results:
            det = r["determinant"]
            if det is not None:
                classes[det % p] += 1
        missing = sorted(set(range(p)) - set(classes.keys()))
        dist[p] = {
            "distribution": {str(k): v for k, v in sorted(classes.items())},
            "classes_hit": len(classes),
            "missing": missing,
            "starvation_ratio": round(len(classes) / p, 4),
        }
    return dist


def modular_form_crossref(knot_results, mf_forms):
    """Task 5: Cross-reference starved MF levels with knot determinants."""
    # Build lookup: determinant -> list of knots
    det_to_knots = defaultdict(list)
    for r in knot_results:
        if r["determinant"] is not None:
            det_to_knots[r["determinant"]].append(r)

    # Starved MF levels
    mf_level_to_forms = defaultdict(list)
    for f in mf_forms:
        mf_level_to_forms[f["level"]].append(f)

    # Find overlaps
    mf_levels = set(mf_level_to_forms.keys())
    knot_dets = set(det_to_knots.keys())
    overlap = sorted(mf_levels & knot_dets)

    matches = []
    for level in overlap:
        forms = mf_level_to_forms[level]
        knots = det_to_knots[level]

        # MF starvation primes
        mf_starv_primes = set()
        for f in forms:
            for p_str in f["starvation"]:
                mf_starv_primes.add(int(p_str))

        # Knot starvation primes (using threshold)
        knot_alex_starv = set()
        knot_jones_starv = set()
        for k in knots:
            for p in PRIMES:
                if k["alexander_starvation"] and k["alexander_starvation"][p]["starved"]:
                    knot_alex_starv.add(p)
                if k["jones_starvation"] and k["jones_starvation"][p]["starved"]:
                    knot_jones_starv.add(p)

        # Overlap of starvation primes
        alex_mf_overlap = sorted(mf_starv_primes & knot_alex_starv)
        jones_mf_overlap = sorted(mf_starv_primes & knot_jones_starv)

        matches.append({
            "level_det": level,
            "n_mf_forms": len(forms),
            "n_knots": len(knots),
            "mf_starvation_primes": sorted(mf_starv_primes),
            "knot_alex_starvation_primes": sorted(knot_alex_starv),
            "knot_jones_starvation_primes": sorted(knot_jones_starv),
            "alex_mf_prime_overlap": alex_mf_overlap,
            "jones_mf_prime_overlap": jones_mf_overlap,
            "any_shared_starvation_prime": len(alex_mf_overlap) > 0 or len(jones_mf_overlap) > 0,
        })

    # Aggregate statistics
    n_any_shared = sum(1 for m in matches if m["any_shared_starvation_prime"])
    n_alex_shared = sum(1 for m in matches if m["alex_mf_prime_overlap"])
    n_jones_shared = sum(1 for m in matches if m["jones_mf_prime_overlap"])

    return {
        "n_overlap_values": len(overlap),
        "n_any_shared_starvation": n_any_shared,
        "n_alex_mf_shared": n_alex_shared,
        "n_jones_mf_shared": n_jones_shared,
        "fraction_shared": round(n_any_shared / len(overlap), 4) if overlap else 0,
        "sample_matches": matches[:30],
        "all_matches": matches,
    }


def build_starvation_dictionary(knot_results, mf_forms, det_analysis, correlation):
    """Task 6: Define starvation types that apply across domains."""
    dictionary = {}

    for p in PRIMES:
        # Knot-side starvation types
        # Type A: Both Alexander and Jones starved
        # Type B: Only Alexander starved
        # Type C: Only Jones starved
        # Type D: Neither starved
        type_counts = {"A_both": 0, "B_alex_only": 0, "C_jones_only": 0, "D_neither": 0}
        for r in knot_results:
            a = r["alexander_starvation"]
            j = r["jones_starvation"]
            if a is None or j is None:
                continue
            a_s = a[p]["starved"]
            j_s = j[p]["starved"]
            if a_s and j_s:
                type_counts["A_both"] += 1
            elif a_s:
                type_counts["B_alex_only"] += 1
            elif j_s:
                type_counts["C_jones_only"] += 1
            else:
                type_counts["D_neither"] += 1

        # Determinant divisibility cross-tab
        det_div_starved = {"p_divides_det_and_starved": 0, "p_divides_det_not_starved": 0,
                           "p_not_div_and_starved": 0, "p_not_div_not_starved": 0}
        for r in knot_results:
            det = r["determinant"]
            a = r["alexander_starvation"]
            if det is None or a is None:
                continue
            div = (det % p == 0)
            s = a[p]["starved"]
            if div and s:
                det_div_starved["p_divides_det_and_starved"] += 1
            elif div and not s:
                det_div_starved["p_divides_det_not_starved"] += 1
            elif not div and s:
                det_div_starved["p_not_div_and_starved"] += 1
            else:
                det_div_starved["p_not_div_not_starved"] += 1

        # MF-side: how many starved at this prime
        mf_starved_at_p = sum(1 for f in mf_forms if str(p) in f["starvation"])

        # Missing class patterns in knots at this prime
        missing_patterns = Counter()
        for r in knot_results:
            a = r["alexander_starvation"]
            if a is None:
                continue
            missing = tuple(a[p]["missing"])
            if missing:
                missing_patterns[missing] += 1

        top_patterns = missing_patterns.most_common(5)

        # Feasibility: can a single starvation type classify both?
        # If the dominant missing-class pattern in knots matches the dominant
        # missing class in MF starvation at this prime, there's a shared type.
        mf_missing_patterns = Counter()
        for f in mf_forms:
            if str(p) in f["starvation"]:
                missing = tuple(f["starvation"][str(p)]["missing"])
                mf_missing_patterns[missing] += 1
        mf_top = mf_missing_patterns.most_common(5)

        # Check overlap in top patterns
        knot_top_set = set(pat for pat, _ in top_patterns)
        mf_top_set = set(pat for pat, _ in mf_top)
        shared_patterns = sorted(knot_top_set & mf_top_set)

        dictionary[p] = {
            "knot_starvation_types": type_counts,
            "det_divisibility_crosstab": det_div_starved,
            "mf_starved_at_prime": mf_starved_at_p,
            "knot_top_missing_patterns": [
                {"missing": list(pat), "count": cnt} for pat, cnt in top_patterns
            ],
            "mf_top_missing_patterns": [
                {"missing": list(pat), "count": cnt} for pat, cnt in mf_top
            ],
            "shared_missing_patterns": [list(p_) for p_ in shared_patterns],
            "n_shared_patterns": len(shared_patterns),
            "dictionary_feasible": len(shared_patterns) > 0,
        }

    return dictionary


def main():
    print("M13: Knot-Primes Starvation Dictionary")
    print("=" * 50)

    # Load data
    print("Loading knots...")
    knots = load_knots()
    print(f"  {len(knots)} knots with polynomial data")

    print("Loading modular form starvation...")
    mf_forms = load_mf_starvation()
    print(f"  {len(mf_forms)} starved modular forms")

    # Task 1 & 2: Compute starvation
    print("\nComputing polynomial starvation...")
    knot_results = analyze_knot_starvation(knots)
    summary = starvation_summary(knot_results)
    print("  Alexander starvation by prime:")
    for p in PRIMES:
        s = summary["alexander"][p]
        print(f"    p={p}: {s['starved']}/{s['total']} starved ({s['fraction']:.1%})")
    print("  Jones starvation by prime:")
    for p in PRIMES:
        s = summary["jones"][p]
        print(f"    p={p}: {s['starved']}/{s['total']} starved ({s['fraction']:.1%})")

    # Task 3: Alexander vs Jones correlation
    print("\nAlexander vs Jones starvation correlation:")
    correlation = alex_jones_correlation(knot_results)
    for p in PRIMES:
        c = correlation[p]
        print(f"  p={p}: phi={c['phi_coefficient']:.3f} ({c['interpretation']}), "
              f"both={c['both_starved']}, alex_only={c['alex_only']}, "
              f"jones_only={c['jones_only']}, neither={c['neither']}")

    # Task 4: Determinant mod p analysis
    print("\nDeterminant mod p analysis:")
    det_analysis = determinant_mod_analysis(knot_results)
    det_residues = det_residue_class_distribution(knot_results)
    for p in PRIMES:
        d = det_analysis[p]
        print(f"  p={p}: {d['n_divisible']} divisible, {d['n_not_divisible']} not")
        print(f"    div: alex_ratio={d['divisible_alex_avg_ratio']}, jones_ratio={d['divisible_jones_avg_ratio']}")
        print(f"    not: alex_ratio={d['not_div_alex_avg_ratio']}, jones_ratio={d['not_div_jones_avg_ratio']}")

    # Task 5: Cross-reference with MF
    print("\nModular form cross-reference:")
    crossref = modular_form_crossref(knot_results, mf_forms)
    print(f"  Overlap values (det=level): {crossref['n_overlap_values']}")
    print(f"  Shared starvation prime: {crossref['n_any_shared_starvation']}/{crossref['n_overlap_values']}")
    print(f"  Alex-MF shared: {crossref['n_alex_mf_shared']}")
    print(f"  Jones-MF shared: {crossref['n_jones_mf_shared']}")

    # Task 6: Dictionary
    print("\nBuilding starvation dictionary...")
    dictionary = build_starvation_dictionary(knot_results, mf_forms, det_analysis, correlation)
    for p in PRIMES:
        d = dictionary[p]
        print(f"  p={p}: {d['n_shared_patterns']} shared missing-class patterns, "
              f"feasible={d['dictionary_feasible']}")
        if d["shared_missing_patterns"]:
            print(f"    shared: {d['shared_missing_patterns']}")

    # Assess overall dictionary feasibility
    feasible_primes = [p for p in PRIMES if dictionary[p]["dictionary_feasible"]]
    print(f"\nDictionary feasible at primes: {feasible_primes}")

    # Build compact output (strip per-knot detail for JSON, keep aggregates)
    # Per-knot detail: save top starved knots only
    top_starved_knots = []
    for r in knot_results:
        a = r["alexander_starvation"]
        j = r["jones_starvation"]
        if a is None:
            continue
        n_alex_starved = sum(1 for p in PRIMES if a[p]["starved"])
        n_jones_starved = sum(1 for p in PRIMES if j[p]["starved"])
        if n_alex_starved >= 2 or n_jones_starved >= 2:
            top_starved_knots.append({
                "name": r["name"],
                "determinant": r["determinant"],
                "crossing_number": r["crossing_number"],
                "n_alex_starved_primes": n_alex_starved,
                "n_jones_starved_primes": n_jones_starved,
                "alex_starved_at": [p for p in PRIMES if a[p]["starved"]],
                "jones_starved_at": [p for p in PRIMES if j[p]["starved"]],
            })

    top_starved_knots.sort(
        key=lambda x: x["n_alex_starved_primes"] + x["n_jones_starved_primes"],
        reverse=True,
    )

    output = {
        "metadata": {
            "challenge": "M13",
            "title": "Knot-Primes Starvation Dictionary",
            "primes": PRIMES,
            "starvation_threshold": STARVATION_THRESHOLD,
            "n_knots_analyzed": len(knot_results),
            "n_starved_mf": len(mf_forms),
        },
        "starvation_summary": summary,
        "alex_jones_correlation": correlation,
        "determinant_mod_analysis": det_analysis,
        "determinant_residue_distribution": det_residues,
        "mf_crossref": {
            "n_overlap_values": crossref["n_overlap_values"],
            "n_any_shared_starvation": crossref["n_any_shared_starvation"],
            "n_alex_mf_shared": crossref["n_alex_mf_shared"],
            "n_jones_mf_shared": crossref["n_jones_mf_shared"],
            "fraction_shared": crossref["fraction_shared"],
            "sample_matches": crossref["sample_matches"],
        },
        "starvation_dictionary": dictionary,
        "dictionary_feasible_primes": feasible_primes,
        "top_starved_knots": top_starved_knots[:50],
        "report": {},
    }

    # Generate report
    alex_rates = ", ".join(
        f"p={p}: {summary['alexander'][p]['fraction']:.1%}" for p in PRIMES
    )
    jones_rates = ", ".join(
        f"p={p}: {summary['jones'][p]['fraction']:.1%}" for p in PRIMES
    )
    phi_parts = ", ".join(
        f"p={p}: {correlation[p]['phi_coefficient']:.3f} ({correlation[p]['interpretation']})"
        for p in PRIMES
    )
    det_parts = "; ".join(
        f"p={p}: alex ratio {det_analysis[p]['divisible_alex_avg_ratio']} vs {det_analysis[p]['not_div_alex_avg_ratio']}"
        for p in PRIMES
    )
    report = {
        "knot_starvation_patterns": (
            f"Analyzed {len(knot_results)} knots at primes {PRIMES}. "
            f"Alexander starvation rates: {alex_rates}. "
            f"Jones starvation rates: {jones_rates}."
        ),
        "alex_jones_correlation": (
            f"Phi coefficients by prime: {phi_parts}. "
            "This measures whether starvation in one polynomial predicts starvation in the other."
        ),
        "determinant_structure": (
            f"Knots whose determinant is divisible by p show {det_parts}"
        ),
        "knot_mf_correspondence": (
            f"{crossref['n_overlap_values']} values where knot det = starved MF level. "
            f"{crossref['n_any_shared_starvation']} have shared starvation prime "
            f"({crossref['fraction_shared']:.1%})."
        ),
        "dictionary_feasibility": (
            f"Starvation dictionary feasible at primes: {feasible_primes}. "
            f"Shared missing-class patterns exist at {len(feasible_primes)}/{len(PRIMES)} primes. "
            + ("The arithmetic topology analogy has a computable manifestation via shared residue avoidance." if len(feasible_primes) >= 2
               else "Limited cross-domain structure found; dictionary may need richer invariants.")
        ),
    }
    output["report"] = report

    # Save
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUTPUT_PATH}")

    # Print report
    print("\n" + "=" * 60)
    print("REPORT")
    print("=" * 60)
    for key, text in report.items():
        print(f"\n{key}:")
        print(f"  {text}")


if __name__ == "__main__":
    main()

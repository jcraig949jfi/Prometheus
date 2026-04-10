#!/usr/bin/env python3
"""
hmf_congruence_scan.py — Hilbert Modular Form Congruence Feasibility Scan (C04)

Challenge: Extend GL_2/Q congruence fiber map to Hilbert modular forms over
real quadratic (and higher) number fields.

Finding: The LMFDB HMF dump (368K forms) contains NO Hecke eigenvalues.
This script performs:
  1. Complete data inventory (what we have)
  2. Structural proxy analysis (what we can do without eigenvalues)
  3. Level-multiplicity analysis (congruence-readiness metric)
  4. Cross-field comparison
  5. Comparison to GL_2/Q congruence landscape
  6. Roadmap for eigenvalue acquisition
"""

import json
import math
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime

REPO = Path(__file__).resolve().parents[4]  # F:/Prometheus
HMF_FORMS = REPO / "cartography" / "lmfdb_dump" / "hmf_forms.json"
HMF_FIELDS = REPO / "cartography" / "lmfdb_dump" / "hmf_fields.json"
OUTPUT = Path(__file__).resolve().parent / "hmf_congruence_results.json"


def load_jsonl_wrapper(path):
    """Load LMFDB dump format: single JSONL line with {source, table, columns, records}."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.loads(f.readline())
    return data["records"], data["columns"], data.get("total_records", len(data["records"]))


def inventory_forms(records):
    """Complete structural inventory of HMF forms."""
    total = len(records)

    # Check for eigenvalue fields
    all_keys = set()
    for r in records[:1000]:
        all_keys.update(r.keys())
    eigenvalue_fields = [k for k in all_keys if "hecke" in k.lower() or "eigen" in k.lower()
                         or "al_dims" in k.lower() or "a_p" in k.lower()]
    has_eigenvalues = len(eigenvalue_fields) > 0

    # Field distribution
    field_counts = Counter(r["field_label"] for r in records)

    # Degree distribution
    deg_counts = Counter(r["deg"] for r in records)

    # Dimension distribution
    dim_counts = Counter(r["dimension"] for r in records)
    dim1_count = dim_counts.get(1, 0)

    # Discriminant distribution
    disc_counts = Counter(r["disc"] for r in records)

    # Base change and CM
    bc_counts = Counter(r["is_base_change"] for r in records)
    cm_counts = Counter(r["is_CM"] for r in records)

    # Weight
    pw_counts = Counter(r["parallel_weight"] for r in records)

    # Level norm stats
    norms = [r["level_norm"] for r in records]

    return {
        "total_forms": total,
        "available_columns": sorted(all_keys),
        "eigenvalue_fields_found": eigenvalue_fields,
        "has_eigenvalues": has_eigenvalues,
        "distinct_fields": len(field_counts),
        "field_distribution_top20": field_counts.most_common(20),
        "degree_distribution": dict(sorted(deg_counts.items())),
        "dimension_distribution_top15": dim_counts.most_common(15),
        "dim1_forms": dim1_count,
        "dim1_fraction": round(dim1_count / total, 4),
        "distinct_discriminants": len(disc_counts),
        "disc_top10": disc_counts.most_common(10),
        "is_base_change": dict(bc_counts),
        "is_CM": dict(cm_counts),
        "parallel_weight": dict(pw_counts),
        "level_norm_min": min(norms),
        "level_norm_max": max(norms),
        "level_norm_median": sorted(norms)[len(norms) // 2],
    }


def analyze_dim1_by_field(records):
    """For dim-1 forms, analyze level multiplicity per field (congruence readiness)."""
    dim1 = [r for r in records if r["dimension"] == 1]

    # Group by field
    by_field = defaultdict(list)
    for r in dim1:
        by_field[r["field_label"]].append(r)

    field_stats = {}
    for fl, forms in sorted(by_field.items(), key=lambda x: -len(x[1])):
        norm_counter = Counter(r["level_norm"] for r in forms)
        multi_norms = {n: c for n, c in norm_counter.items() if c > 1}

        # Potential congruence pairs: C(c, 2) for each norm with c > 1
        potential_pairs = sum(c * (c - 1) // 2 for c in norm_counter.values() if c > 1)

        field_stats[fl] = {
            "count": len(forms),
            "distinct_levels": len(norm_counter),
            "levels_with_multiplicity": len(multi_norms),
            "max_multiplicity": max(norm_counter.values()),
            "potential_same_level_pairs": potential_pairs,
            "disc": forms[0]["disc"],
            "deg": forms[0]["deg"],
            "cm_count": sum(1 for r in forms if r["is_CM"] == "yes"),
            "base_change_count": sum(1 for r in forms if r["is_base_change"] == "yes"),
        }

    return field_stats


def cross_field_level_overlap(records):
    """Check if forms over different fields share level norms (cross-field comparison)."""
    dim1 = [r for r in records if r["dimension"] == 1]

    # Focus on real quadratic fields (deg 2)
    rq_forms = [r for r in dim1 if r["deg"] == 2]

    # Group norms by field
    field_norms = defaultdict(set)
    for r in rq_forms:
        field_norms[r["field_label"]].add(r["level_norm"])

    # Key fields for cross-comparison
    key_fields = ["2.2.5.1", "2.2.8.1", "2.2.12.1", "2.2.13.1", "2.2.17.1"]
    key_fields = [f for f in key_fields if f in field_norms]

    overlaps = {}
    for i, f1 in enumerate(key_fields):
        for f2 in key_fields[i + 1:]:
            shared = field_norms[f1] & field_norms[f2]
            overlaps[f"{f1} vs {f2}"] = {
                "shared_norms": len(shared),
                "f1_norms": len(field_norms[f1]),
                "f2_norms": len(field_norms[f2]),
                "jaccard": round(len(shared) / len(field_norms[f1] | field_norms[f2]), 4),
            }

    return overlaps


def proxy_congruence_analysis(records):
    """
    Without eigenvalues, detect 'structural congruence candidates':
    pairs of dim-1 forms over the same field with same level norm,
    same CM status, and same base-change status.

    These would be the first pairs to check once eigenvalues are obtained.
    For mod-ell congruences, same level is necessary (Ribet's level-lowering
    gives level divisibility constraints).
    """
    dim1 = [r for r in records if r["dimension"] == 1]

    # Group by (field, level_norm, is_CM, is_base_change)
    groups = defaultdict(list)
    for r in dim1:
        key = (r["field_label"], r["level_norm"], r["is_CM"], r["is_base_change"])
        groups[key].append(r["label"])

    # Count candidate pairs
    total_pairs = 0
    pair_examples = []
    size_dist = Counter()

    for key, labels in groups.items():
        n = len(labels)
        if n > 1:
            pairs = n * (n - 1) // 2
            total_pairs += pairs
            size_dist[n] += 1
            if len(pair_examples) < 20:
                pair_examples.append({
                    "field": key[0],
                    "level_norm": key[1],
                    "is_CM": key[2],
                    "is_base_change": key[3],
                    "count": n,
                    "labels": labels[:5],
                })

    return {
        "total_candidate_pairs": total_pairs,
        "groups_with_multiplicity": sum(size_dist.values()),
        "group_size_distribution": dict(sorted(size_dist.items())),
        "examples": pair_examples,
    }


def hasse_squeeze_prediction(n_forms, n_primes, ell_values=(3, 5, 7)):
    """
    Predict random congruence count for comparison.
    For dim-1 forms with rational eigenvalues, a_p mod ell matches with prob 1/ell.
    After P good primes: prob = (1/ell)^P.
    Expected pairs = C(n, 2) * (1/ell)^P.
    """
    predictions = {}
    for ell in ell_values:
        for P in [5, 10, 15, 20]:
            n_pairs = n_forms * (n_forms - 1) / 2
            prob = (1.0 / ell) ** P
            expected = n_pairs * prob
            predictions[f"ell={ell}, P={P}"] = {
                "n_forms": n_forms,
                "n_pairs": int(n_pairs),
                "probability_per_pair": prob,
                "expected_random_pairs": round(expected, 4),
            }
    return predictions


def gl2_comparison():
    """Compare HMF landscape to known GL_2/Q results."""
    return {
        "GL2_over_Q": {
            "total_forms_scanned": "~73K (weight-2 newforms, level <= 5000)",
            "congruences_found": 981,
            "independent_congruences": 242,
            "primes_tested": [3, 5, 7, 11],
            "eigenvalue_availability": "Full (from LMFDB)",
            "source": "congruence_graph.py results",
        },
        "HMF_comparison": {
            "total_forms": 368356,
            "dim1_forms": 132081,
            "eigenvalue_availability": "NONE in current dump",
            "congruence_detection_possible": False,
            "structural_proxy_available": True,
            "candidate_pairs_identified": "See proxy_congruence_analysis",
            "estimated_congruences_if_eigenvalues_available": (
                "For Q(sqrt5) alone: 4605 dim-1 forms, "
                "~10.6M pairs. At mod-3 with 10 primes: "
                "expect ~0.18 random pairs. Any detection = signal."
            ),
        },
    }


def eigenvalue_acquisition_roadmap():
    """What's needed to actually detect HMF congruences."""
    return {
        "option_1_lmfdb_api": {
            "description": "Query LMFDB API for individual HMF Hecke eigenvalues",
            "endpoint": "https://www.lmfdb.org/api/hmf_hecke/?label=LABEL",
            "feasibility": "Slow. 132K dim-1 forms x API rate limits = weeks",
            "data_table": "hmf_hecke (separate from hmf_forms)",
            "priority": "HIGH — this is the missing piece",
        },
        "option_2_postgres_dump": {
            "description": "Download hmf_hecke table from LMFDB PostgreSQL mirror",
            "method": "Same approach as hmf_forms dump (lmfdb_postgres_dump.py)",
            "table": "hmf_hecke",
            "expected_columns": ["label", "hecke_eigenvalues", "hecke_polynomial"],
            "feasibility": "Best option. Single dump, all eigenvalues at once.",
            "priority": "CRITICAL — next action",
        },
        "option_3_magma_computation": {
            "description": "Compute eigenvalues directly using Magma/Sage",
            "feasibility": "Very expensive. Only for forms not in LMFDB.",
            "priority": "LOW — LMFDB should have everything",
        },
        "next_step": (
            "Run lmfdb_postgres_dump.py targeting the 'hmf_hecke' table. "
            "This should give hecke_eigenvalues for all 368K forms. "
            "Then re-run this scan with eigenvalue comparison enabled."
        ),
    }


def main():
    print("=" * 70)
    print("HMF Congruence Scan — Feasibility Assessment")
    print("=" * 70)

    # Load data
    print("\nLoading HMF forms...")
    forms, cols, total = load_jsonl_wrapper(HMF_FORMS)
    print(f"  Loaded {len(forms)} forms ({total} reported)")

    print("Loading HMF fields...")
    fields, fcols, ftotal = load_jsonl_wrapper(HMF_FIELDS)
    print(f"  Loaded {len(fields)} fields")

    # 1. Inventory
    print("\n--- INVENTORY ---")
    inv = inventory_forms(forms)
    print(f"  Total forms: {inv['total_forms']}")
    print(f"  Columns: {inv['available_columns']}")
    print(f"  Eigenvalue fields found: {inv['eigenvalue_fields_found']}")
    print(f"  HAS EIGENVALUES: {inv['has_eigenvalues']}")
    print(f"  Dim-1 forms: {inv['dim1_forms']} ({inv['dim1_fraction']*100:.1f}%)")
    print(f"  Distinct fields: {inv['distinct_fields']}")
    print(f"  All parallel weight 2: {inv['parallel_weight']}")

    # 2. Dim-1 analysis
    print("\n--- DIM-1 FIELD ANALYSIS ---")
    field_stats = analyze_dim1_by_field(forms)
    total_potential = sum(fs["potential_same_level_pairs"] for fs in field_stats.values())
    print(f"  Fields with dim-1 forms: {len(field_stats)}")
    print(f"  Total same-level pairs (congruence candidates): {total_potential:,}")
    print("  Top 5 fields by candidate pairs:")
    top5 = sorted(field_stats.items(), key=lambda x: -x[1]["potential_same_level_pairs"])[:5]
    for fl, fs in top5:
        print(f"    {fl} (disc={fs['disc']}): {fs['count']} forms, "
              f"{fs['potential_same_level_pairs']:,} pairs")

    # 3. Proxy congruence candidates
    print("\n--- PROXY CONGRUENCE CANDIDATES ---")
    proxy = proxy_congruence_analysis(forms)
    print(f"  Total structural candidate pairs: {proxy['total_candidate_pairs']:,}")
    print(f"  Groups with multiplicity > 1: {proxy['groups_with_multiplicity']}")
    print(f"  Group size distribution: {proxy['group_size_distribution']}")

    # 4. Cross-field overlap
    print("\n--- CROSS-FIELD LEVEL OVERLAP ---")
    overlaps = cross_field_level_overlap(forms)
    for pair, stats in overlaps.items():
        print(f"  {pair}: {stats['shared_norms']} shared norms "
              f"(Jaccard={stats['jaccard']})")

    # 5. Hasse squeeze predictions (for when eigenvalues arrive)
    print("\n--- HASSE SQUEEZE PREDICTIONS ---")
    # Use Q(sqrt5) dim-1 count as example
    hasse = hasse_squeeze_prediction(4605, 20)
    for key in ["ell=3, P=10", "ell=5, P=10", "ell=7, P=10"]:
        p = hasse[key]
        print(f"  Q(sqrt5) {key}: {p['expected_random_pairs']:.4f} expected random pairs")

    # 6. GL_2 comparison
    print("\n--- GL_2 COMPARISON ---")
    gl2 = gl2_comparison()
    print(f"  GL_2/Q: {gl2['GL2_over_Q']['congruences_found']} congruences from "
          f"{gl2['GL2_over_Q']['total_forms_scanned']}")
    print(f"  HMF: {inv['total_forms']} forms, 0 congruences (no eigenvalues)")

    # 7. Roadmap
    print("\n--- EIGENVALUE ACQUISITION ROADMAP ---")
    roadmap = eigenvalue_acquisition_roadmap()
    print(f"  CRITICAL NEXT STEP: {roadmap['next_step']}")

    # Compile results
    results = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "challenge": "C04 — HMF Congruence Scan",
        "status": "DATA_INVENTORY_COMPLETE",
        "critical_finding": (
            "The LMFDB HMF dump contains NO Hecke eigenvalues. "
            "The hmf_forms table has only metadata (label, level, dimension, CM, base_change). "
            "Eigenvalues are in a SEPARATE table: hmf_hecke. "
            "Congruence detection is BLOCKED until hmf_hecke is acquired."
        ),
        "data_inventory": inv,
        "dim1_field_analysis": {
            "total_fields": len(field_stats),
            "total_same_level_candidate_pairs": total_potential,
            "top10_fields": {
                fl: fs for fl, fs in sorted(
                    field_stats.items(), key=lambda x: -x[1]["potential_same_level_pairs"]
                )[:10]
            },
        },
        "proxy_congruence_candidates": proxy,
        "cross_field_overlap": overlaps,
        "hasse_squeeze_predictions": hasse,
        "gl2_comparison": gl2,
        "eigenvalue_roadmap": roadmap,
        "key_statistics": {
            "total_forms": inv["total_forms"],
            "dim1_forms": inv["dim1_forms"],
            "real_quadratic_dim1": sum(
                fs["count"] for fl, fs in field_stats.items() if fs["deg"] == 2
            ),
            "fields_with_dim1": len(field_stats),
            "structural_candidate_pairs": proxy["total_candidate_pairs"],
            "eigenvalues_available": False,
            "congruences_detected": 0,
        },
    }

    # Save
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {OUTPUT}")

    print("\n" + "=" * 70)
    print("VERDICT: Eigenvalue data missing. Acquire hmf_hecke table to proceed.")
    print("=" * 70)

    return results


if __name__ == "__main__":
    main()

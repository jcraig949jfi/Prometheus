"""
Depth Extractor — Extract deep features from existing data into the concept layer.
====================================================================================
The shallow index used scalar invariants (conductor, determinant, class number).
The depth index extracts SEQUENCE features from the polynomial/coefficient data
that's already in our databases but not in the concept layer.

Extracts:
  1. EC coefficient features: sign patterns, zero counts, growth rates, extremes
  2. Knot polynomial features: degree, coefficient symmetry, alternation, magnitude
  3. OEIS formula features: function references, variable patterns
  4. Fungrim symbol co-occurrence: which symbols appear together

Outputs to convergence/data/depth_concepts.jsonl and depth_links.jsonl

Usage:
    python depth_extractor.py                  # extract all
    python depth_extractor.py --source ec      # EC only
"""

import json
import math
import re
import sys
import time
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

ROOT = Path(__file__).resolve().parents[3]
CONVERGENCE = ROOT / "cartography" / "convergence"
DEPTH_CONCEPTS = CONVERGENCE / "data" / "depth_concepts.jsonl"
DEPTH_LINKS = CONVERGENCE / "data" / "depth_links.jsonl"


def extract_ec_depth():
    """Extract depth features from EC coefficient sequences."""
    print("  Extracting EC coefficient depth features...")
    from search_engine import _get_duck

    con = _get_duck()
    rows = con.execute("""
        SELECT lmfdb_label, conductor, aplist, anlist, ainvs, rank
        FROM elliptic_curves
        WHERE aplist IS NOT NULL
    """).fetchall()
    con.close()

    concepts = set()
    links = []

    for row in rows:
        label, cond, aplist, anlist, ainvs, rank = row
        obj_id = label

        ap = aplist if isinstance(aplist, list) else json.loads(aplist) if isinstance(aplist, str) else None
        an = anlist if isinstance(anlist, list) else json.loads(anlist) if isinstance(anlist, str) else None

        if not ap:
            continue

        ap_int = [int(x) for x in ap]
        obj_concepts = []

        # 1. Sign pattern of a_p sequence
        signs = tuple(1 if x > 0 else (-1 if x < 0 else 0) for x in ap_int[:8])
        sign_key = "".join("+" if s > 0 else ("-" if s < 0 else "0") for s in signs)
        obj_concepts.append(f"depth_ap_sign_{sign_key}")

        # 2. Number of zeros in a_p
        n_zeros = sum(1 for x in ap_int if x == 0)
        obj_concepts.append(f"depth_ap_zeros_{n_zeros}")

        # 3. Number of sign changes
        sign_changes = sum(1 for i in range(len(ap_int)-1)
                          if ap_int[i] * ap_int[i+1] < 0)
        obj_concepts.append(f"depth_ap_signchanges_{sign_changes}")

        # 4. Max absolute coefficient (binned)
        max_abs = max(abs(x) for x in ap_int)
        if max_abs <= 2:
            obj_concepts.append("depth_ap_small")
        elif max_abs <= 10:
            obj_concepts.append("depth_ap_medium")
        elif max_abs <= 50:
            obj_concepts.append("depth_ap_large")
        else:
            obj_concepts.append("depth_ap_very_large")

        # 5. Sum of a_p (related to analytic rank)
        ap_sum = sum(ap_int)
        if ap_sum > 5:
            obj_concepts.append("depth_ap_sum_positive")
        elif ap_sum < -5:
            obj_concepts.append("depth_ap_sum_negative")
        else:
            obj_concepts.append("depth_ap_sum_near_zero")

        # 6. First coefficient (a_2) — reduction type at 2
        if len(ap_int) > 0:
            a2 = ap_int[0]
            obj_concepts.append(f"depth_a2_{a2}")

        # 7. a_n features (if available)
        if an:
            an_int = [int(x) for x in an]
            # a_1 should always be 1
            # Check multiplicativity: a_6 = a_2 * a_3?
            if len(an_int) >= 7:
                a2 = an_int[2] if len(an_int) > 2 else 0
                a3 = an_int[3] if len(an_int) > 3 else 0
                a6 = an_int[6] if len(an_int) > 6 else 0
                if a2 * a3 == a6:
                    obj_concepts.append("depth_an_multiplicative")
                else:
                    obj_concepts.append("depth_an_not_multiplicative")

        # 8. Weierstrass invariant pattern
        if ainvs:
            ai = ainvs if isinstance(ainvs, list) else json.loads(ainvs) if isinstance(ainvs, str) else None
            if ai and len(ai) >= 5:
                ai_int = [int(x) for x in ai]
                n_zero_ainvs = sum(1 for x in ai_int if x == 0)
                obj_concepts.append(f"depth_ainvs_zeros_{n_zero_ainvs}")
                # Minimal model signature
                if ai_int[0] in (0, 1) and ai_int[2] in (0, 1):
                    obj_concepts.append("depth_ainvs_minimal")

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept,
                "dataset": "LMFDB_depth",
                "object_id": obj_id,
                "relationship": "has_depth_feature",
            })

    print(f"    {len(concepts)} depth concepts, {len(links)} links from {len(rows)} curves")
    return concepts, links


def extract_knot_depth():
    """Extract depth features from knot polynomial coefficients."""
    print("  Extracting knot polynomial depth features...")
    from search_engine import _load_knots, _knots_cache
    _load_knots()

    knot_list = _knots_cache.get("knots", []) if isinstance(_knots_cache, dict) else []
    concepts = set()
    links = []

    for i, k in enumerate(knot_list):
        if not isinstance(k, dict):
            continue

        obj_id = f"knot_{i}"
        obj_concepts = []

        # Alexander polynomial features
        alex = k.get("alex_coeffs")
        if alex and len(alex) >= 3:
            # 1. Degree
            obj_concepts.append(f"depth_alex_degree_{len(alex)-1}")

            # 2. Palindrome score
            is_palindrome = alex == alex[::-1]
            obj_concepts.append(f"depth_alex_palindrome_{is_palindrome}")

            # 3. Alternating signs
            alternating = all(alex[j] * alex[j+1] < 0 for j in range(len(alex)-1) if alex[j] != 0 and alex[j+1] != 0)
            if alternating:
                obj_concepts.append("depth_alex_alternating")

            # 4. Coefficient magnitude pattern
            max_coeff = max(abs(c) for c in alex)
            obj_concepts.append(f"depth_alex_maxcoeff_bin_{int(math.log2(max(max_coeff,1)))}")

            # 5. Alexander evaluated at specific points (invariant values)
            # alex(-1) = determinant (should match)
            alex_at_neg1 = sum(c * ((-1)**j) for j, c in enumerate(alex))
            obj_concepts.append(f"depth_alex_at_neg1_{abs(alex_at_neg1)}")

            # 6. Coefficient sum
            coeff_sum = sum(alex)
            obj_concepts.append(f"depth_alex_sum_{coeff_sum}")

        # Jones polynomial features
        jones = k.get("jones_coeffs")
        if jones and len(jones) >= 3:
            obj_concepts.append(f"depth_jones_degree_{len(jones)-1}")

            # Sign pattern
            signs = tuple(1 if x > 0 else (-1 if x < 0 else 0) for x in jones[:6])
            sign_key = "".join("+" if s > 0 else ("-" if s < 0 else "0") for s in signs)
            obj_concepts.append(f"depth_jones_sign_{sign_key}")

            # Alternating
            alt = all(jones[j] * jones[j+1] < 0 for j in range(len(jones)-1) if jones[j] != 0 and jones[j+1] != 0)
            if alt:
                obj_concepts.append("depth_jones_alternating")

            max_j = max(abs(c) for c in jones)
            obj_concepts.append(f"depth_jones_maxcoeff_bin_{int(math.log2(max(max_j,1)))}")

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept,
                "dataset": "KnotInfo_depth",
                "object_id": obj_id,
                "relationship": "has_depth_feature",
            })

    print(f"    {len(concepts)} depth concepts, {len(links)} links from {len(knot_list)} knots")
    return concepts, links


def extract_oeis_formula_depth():
    """Extract depth features from OEIS formula text."""
    print("  Extracting OEIS formula depth features...")
    formula_file = ROOT / "cartography" / "oeis" / "data" / "oeis_formulas.jsonl"
    if not formula_file.exists():
        print("    Formula file not found")
        return set(), []

    # Mathematical function names to detect
    math_functions = {
        "zeta": "depth_func_zeta",
        "gamma": "depth_func_gamma",
        "bernoulli": "depth_func_bernoulli",
        "euler": "depth_func_euler",
        "fibonacci": "depth_func_fibonacci",
        "catalan": "depth_func_catalan",
        "partition": "depth_func_partition",
        "prime": "depth_func_prime",
        "sigma": "depth_func_sigma",
        "phi": "depth_func_totient",
        "mobius": "depth_func_mobius",
        "moebius": "depth_func_mobius",
        "dirichlet": "depth_func_dirichlet",
        "theta": "depth_func_theta",
        "modular": "depth_func_modular",
        "elliptic": "depth_func_elliptic",
        "bessel": "depth_func_bessel",
        "hypergeometric": "depth_func_hypergeometric",
        "legendre": "depth_func_legendre",
        "chebyshev": "depth_func_chebyshev",
        "stirling": "depth_func_stirling",
        "binomial": "depth_func_binomial",
        "gcd": "depth_func_gcd",
        "lcm": "depth_func_lcm",
        "floor": "depth_func_floor",
        "sqrt": "depth_func_sqrt",
        "log": "depth_func_log",
        "exp": "depth_func_exp",
        "sum": "depth_func_sum",
        "product": "depth_func_product",
        "integral": "depth_func_integral",
        "convolution": "depth_func_convolution",
        "recurrence": "depth_func_recurrence",
        "generating function": "depth_func_gf",
        "g.f.": "depth_func_gf",
    }

    concepts = set()
    links = []
    seq_functions = defaultdict(set)

    n_processed = 0
    with open(formula_file, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except:
                continue
            seq_id = rec.get("seq_id", "")
            formula = rec.get("formula", "").lower()

            for keyword, concept in math_functions.items():
                if keyword in formula:
                    seq_functions[seq_id].add(concept)

            n_processed += 1
            if n_processed % 100000 == 0:
                print(f"    Processed {n_processed} formulas...")

    # Build links
    for seq_id, funcs in seq_functions.items():
        for concept in funcs:
            concepts.add(concept)
            links.append({
                "concept": concept,
                "dataset": "OEIS_depth",
                "object_id": seq_id,
                "relationship": "formula_references",
            })

        # Co-occurrence concepts (which functions appear together)
        func_list = sorted(funcs)
        for i in range(len(func_list)):
            for j in range(i+1, min(i+3, len(func_list))):
                co_concept = f"depth_cooccur_{func_list[i]}+{func_list[j]}"
                concepts.add(co_concept)
                links.append({
                    "concept": co_concept,
                    "dataset": "OEIS_depth",
                    "object_id": seq_id,
                    "relationship": "formula_co_occurrence",
                })

    print(f"    {len(concepts)} depth concepts, {len(links)} links from {n_processed} formulas ({len(seq_functions)} sequences)")
    return concepts, links


def extract_fungrim_depth():
    """Extract depth features from Fungrim symbol co-occurrence."""
    print("  Extracting Fungrim symbol co-occurrence depth features...")
    fungrim_file = ROOT / "cartography" / "fungrim" / "data" / "fungrim_index.json"
    if not fungrim_file.exists():
        return set(), []

    data = json.loads(fungrim_file.read_text(encoding="utf-8"))
    concepts = set()
    links = []

    for formula in data.get("formulas", []):
        fid = formula.get("id", "")
        symbols = formula.get("symbols", [])

        # Symbol pair co-occurrence (deeper than single symbols)
        for i in range(len(symbols)):
            for j in range(i+1, len(symbols)):
                s1, s2 = sorted([symbols[i], symbols[j]])
                co_concept = f"depth_fungrim_pair_{s1}_{s2}"
                concepts.add(co_concept)
                links.append({
                    "concept": co_concept,
                    "dataset": "Fungrim_depth",
                    "object_id": fid,
                    "relationship": "symbol_co_occurrence",
                })

        # Formula type + symbol combination
        ftype = formula.get("type", "unknown")
        for sym in symbols[:5]:
            type_concept = f"depth_fungrim_{ftype}_{sym}"
            concepts.add(type_concept)
            links.append({
                "concept": type_concept,
                "dataset": "Fungrim_depth",
                "object_id": fid,
                "relationship": "typed_symbol",
            })

    print(f"    {len(concepts)} depth concepts, {len(links)} links from {len(data.get('formulas',[]))} formulas")
    return concepts, links


def run_extraction(sources=None):
    """Run all depth extractions."""
    print("=" * 70)
    print("  DEPTH EXTRACTOR — Indexing the deep features")
    print("  Polynomials, coefficients, formulas, co-occurrences")
    print("=" * 70)

    t0 = time.time()
    all_concepts = set()
    all_links = []

    extractors = [
        ("ec", "EC coefficients", extract_ec_depth),
        ("knot", "Knot polynomials", extract_knot_depth),
        ("oeis", "OEIS formulas", extract_oeis_formula_depth),
        ("fungrim", "Fungrim symbols", extract_fungrim_depth),
    ]

    for key, name, fn in extractors:
        if sources and key not in sources:
            continue
        print(f"\n  [{name}]")
        try:
            concepts, links = fn()
            all_concepts.update(concepts)
            all_links.extend(links)
        except Exception as e:
            print(f"    ERROR: {e}")

    # Save
    print(f"\n  Saving depth index...")
    with open(DEPTH_CONCEPTS, "w") as f:
        for c in sorted(all_concepts):
            f.write(json.dumps({"id": c, "type": "depth_feature"}) + "\n")
    with open(DEPTH_LINKS, "w") as f:
        for link in all_links:
            f.write(json.dumps(link) + "\n")

    elapsed = time.time() - t0

    print(f"\n{'=' * 70}")
    print(f"  DEPTH EXTRACTION COMPLETE in {elapsed:.1f}s")
    print(f"  Depth concepts: {len(all_concepts):,}")
    print(f"  Depth links: {len(all_links):,}")

    # Breakdown by dataset
    by_ds = defaultdict(int)
    for link in all_links:
        by_ds[link["dataset"]] += 1
    for ds, n in sorted(by_ds.items(), key=lambda x: -x[1]):
        print(f"    {ds:20s}: {n:,} links")

    print(f"  Saved to {DEPTH_CONCEPTS} and {DEPTH_LINKS}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Depth Extractor")
    parser.add_argument("--source", nargs="+", default=None,
                        choices=["ec", "knot", "oeis", "fungrim"],
                        help="Extract specific sources only")
    args = parser.parse_args()
    run_extraction(sources=args.source)

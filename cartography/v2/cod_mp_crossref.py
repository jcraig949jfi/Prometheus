#!/usr/bin/env python3
"""
COD vs Materials Project Cross-Validation
==========================================
Compares crystal structures between the Crystallography Open Database (COD)
and Materials Project (MP) to assess data consistency and coverage overlap.

Matching strategy: normalize chemical formulas to canonical reduced form
(alphabetical elements, GCD-reduced stoichiometry), then compare cell volumes
for matched formulas.

Output: cod_mp_crossref_results.json
"""

import json
import re
import math
import os
from collections import Counter, defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = Path(__file__).resolve().parent.parent  # cartography/
COD_PATH = BASE / "physics" / "data" / "cod" / "cod_structures.json"
MP_PATH  = BASE / "physics" / "data" / "materials_project_10k.json"
OUT_PATH = Path(__file__).resolve().parent / "cod_mp_crossref_results.json"

# ---------------------------------------------------------------------------
# Formula normalization
# ---------------------------------------------------------------------------

def parse_formula(formula_str):
    """Parse a chemical formula string into {element: count} dict."""
    if not formula_str:
        return {}
    tokens = re.findall(r'([A-Z][a-z]?)(\d*\.?\d*)', formula_str)
    composition = {}
    for elem, count_str in tokens:
        if not elem:
            continue
        count = float(count_str) if count_str else 1.0
        composition[elem] = composition.get(elem, 0) + count
    return composition


def gcd_of_list(lst):
    """GCD of a list of integers."""
    result = lst[0]
    for x in lst[1:]:
        result = math.gcd(result, x)
    return result


def normalize_formula(formula_str):
    """
    Normalize formula to canonical reduced form:
    - Parse elements and counts
    - Reduce to smallest integer ratios (GCD)
    - Sort elements alphabetically
    - Return canonical string like "Al2O3"
    """
    comp = parse_formula(formula_str)
    if not comp:
        return None

    # Check if all counts are integers (or very close)
    int_counts = {}
    for elem, count in comp.items():
        rounded = round(count)
        if abs(count - rounded) < 0.01:
            int_counts[elem] = rounded
        else:
            # Use as-is with 2 decimal places for non-integer stoichiometry
            int_counts[elem] = round(count, 2)

    # Try GCD reduction if all integer
    all_int = all(isinstance(v, int) or (isinstance(v, float) and v == int(v))
                  for v in int_counts.values())
    if all_int:
        int_vals = [int(v) for v in int_counts.values()]
        if all(v > 0 for v in int_vals):
            g = gcd_of_list(int_vals)
            if g > 1:
                int_counts = {k: int(v) // g for k, v in int_counts.items()}

    # Build canonical string: alphabetical elements
    parts = []
    for elem in sorted(int_counts.keys()):
        c = int_counts[elem]
        if isinstance(c, float) and c == int(c):
            c = int(c)
        if c == 1:
            parts.append(elem)
        else:
            parts.append(f"{elem}{c}")

    return "".join(parts)


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

def load_data():
    print(f"Loading COD from {COD_PATH}")
    with open(COD_PATH) as f:
        cod_raw = json.load(f)
    print(f"  {len(cod_raw)} entries")

    print(f"Loading MP from {MP_PATH}")
    with open(MP_PATH) as f:
        mp_raw = json.load(f)
    print(f"  {len(mp_raw)} entries")

    return cod_raw, mp_raw


# ---------------------------------------------------------------------------
# Build normalized lookup tables
# ---------------------------------------------------------------------------

def build_cod_table(cod_raw):
    """Build dict: normalized_formula -> list of {id, volume, nelements, ...}"""
    table = defaultdict(list)
    skipped = 0
    for entry in cod_raw:
        formula = entry.get("chemical_formula_reduced")
        if not formula:
            skipped += 1
            continue
        norm = normalize_formula(formula)
        if not norm:
            skipped += 1
            continue
        vol = entry.get("cell_volume")
        table[norm].append({
            "id": entry.get("id"),
            "raw_formula": formula,
            "volume": vol,
            "nelements": entry.get("nelements"),
            "spacegroup_number": entry.get("space_group_it_number"),
            "spacegroup_hm": entry.get("space_group_symbol_hermann_mauguin"),
        })
    print(f"COD: {len(table)} unique normalized formulas ({skipped} entries skipped)")
    return table


def build_mp_table(mp_raw):
    """Build dict: normalized_formula -> list of {material_id, volume, crystal_system, ...}"""
    table = defaultdict(list)
    skipped = 0
    for entry in mp_raw:
        formula = entry.get("formula")
        if not formula:
            skipped += 1
            continue
        norm = normalize_formula(formula)
        if not norm:
            skipped += 1
            continue
        table[norm].append({
            "material_id": entry.get("material_id"),
            "raw_formula": formula,
            "volume": entry.get("volume"),
            "crystal_system": entry.get("crystal_system"),
            "spacegroup": entry.get("spacegroup"),
            "spacegroup_number": entry.get("spacegroup_number"),
            "nsites": entry.get("nsites"),
            "density": entry.get("density"),
        })
    print(f"MP:  {len(table)} unique normalized formulas ({skipped} entries skipped)")
    return table


# ---------------------------------------------------------------------------
# Cross-validation analysis
# ---------------------------------------------------------------------------

def analyze_coverage(cod_table, mp_table):
    """Coverage overlap analysis."""
    cod_set = set(cod_table.keys())
    mp_set = set(mp_table.keys())

    both = cod_set & mp_set
    cod_only = cod_set - mp_set
    mp_only = mp_set - cod_set

    print(f"\n=== Coverage Overlap ===")
    print(f"  COD unique formulas:  {len(cod_set)}")
    print(f"  MP unique formulas:   {len(mp_set)}")
    print(f"  In both:              {len(both)}")
    print(f"  COD only:             {len(cod_only)}")
    print(f"  MP only:              {len(mp_only)}")
    print(f"  Overlap / COD:        {len(both)/len(cod_set)*100:.1f}%")
    print(f"  Overlap / MP:         {len(both)/len(mp_set)*100:.1f}%")
    print(f"  Jaccard index:        {len(both)/len(cod_set | mp_set)*100:.1f}%")

    return {
        "cod_unique_formulas": len(cod_set),
        "mp_unique_formulas": len(mp_set),
        "in_both": len(both),
        "cod_only": len(cod_only),
        "mp_only": len(mp_only),
        "overlap_frac_of_cod": round(len(both) / len(cod_set), 4),
        "overlap_frac_of_mp": round(len(both) / len(mp_set), 4),
        "jaccard_index": round(len(both) / len(cod_set | mp_set), 4),
        "sample_shared": sorted(both)[:20],
        "sample_cod_only": sorted(cod_only)[:20],
        "sample_mp_only": sorted(mp_only)[:20],
    }


def analyze_volume_agreement(cod_table, mp_table):
    """
    For matched formulas, compare cell volumes.
    Note: volumes may differ due to different polymorphs, Z (formula units per cell),
    or different structure determinations. We compare min volumes from each source
    to find the closest match.
    """
    shared = set(cod_table.keys()) & set(mp_table.keys())

    comparisons = []
    for formula in sorted(shared):
        cod_entries = cod_table[formula]
        mp_entries = mp_table[formula]

        cod_vols = [e["volume"] for e in cod_entries if e["volume"] is not None and e["volume"] > 0]
        mp_vols = [e["volume"] for e in mp_entries if e["volume"] is not None and e["volume"] > 0]

        if not cod_vols or not mp_vols:
            continue

        # Find best matching pair (minimum relative difference)
        best_rel_diff = float("inf")
        best_cod_vol = None
        best_mp_vol = None
        for cv in cod_vols:
            for mv in mp_vols:
                avg = (cv + mv) / 2
                if avg > 0:
                    rel = abs(cv - mv) / avg
                    if rel < best_rel_diff:
                        best_rel_diff = rel
                        best_cod_vol = cv
                        best_mp_vol = mv

        if best_cod_vol is not None:
            # Also check integer-ratio matches (Z differences: vol_COD / vol_MP ~ integer)
            ratio = best_cod_vol / best_mp_vol if best_mp_vol > 0 else None
            comparisons.append({
                "formula": formula,
                "cod_volume": round(best_cod_vol, 3),
                "mp_volume": round(best_mp_vol, 3),
                "rel_diff": round(best_rel_diff, 4),
                "ratio": round(ratio, 3) if ratio else None,
                "n_cod_entries": len(cod_entries),
                "n_mp_entries": len(mp_entries),
            })

    # Agreement rates at different thresholds
    n = len(comparisons)
    if n == 0:
        print("\nNo volume comparisons possible.")
        return {"n_comparisons": 0}

    thresholds = [0.01, 0.02, 0.05, 0.10, 0.20, 0.50]
    agreement = {}
    for t in thresholds:
        count = sum(1 for c in comparisons if c["rel_diff"] <= t)
        agreement[f"within_{int(t*100)}pct"] = {"count": count, "fraction": round(count / n, 4)}

    # Check for integer-ratio matches (Z=2,3,4 multiples)
    z_ratio_matches = {"exact_or_close": 0}
    for z in [2, 3, 4]:
        key = f"Z_ratio_{z}"
        count = sum(1 for c in comparisons
                    if c["ratio"] and (abs(c["ratio"] - z) < 0.15 or abs(c["ratio"] - 1/z) < 0.15/z))
        z_ratio_matches[key] = count

    # Systematic bias: is COD systematically larger or smaller?
    diffs = [(c["cod_volume"] - c["mp_volume"]) / ((c["cod_volume"] + c["mp_volume"]) / 2)
             for c in comparisons]
    mean_bias = sum(diffs) / len(diffs)
    median_bias = sorted(diffs)[len(diffs) // 2]

    # Fraction where COD > MP
    cod_larger = sum(1 for d in diffs if d > 0)

    print(f"\n=== Volume Agreement ({n} comparisons) ===")
    for t in thresholds:
        key = f"within_{int(t*100)}pct"
        a = agreement[key]
        print(f"  Within {int(t*100):2d}%: {a['count']:4d} / {n} = {a['fraction']*100:.1f}%")

    print(f"\n=== Systematic Bias ===")
    print(f"  Mean relative diff (COD-MP)/avg: {mean_bias:+.4f}")
    print(f"  Median relative diff:            {median_bias:+.4f}")
    print(f"  COD > MP:  {cod_larger}/{n} = {cod_larger/n*100:.1f}%")

    print(f"\n=== Z-ratio matches ===")
    for k, v in z_ratio_matches.items():
        print(f"  {k}: {v}")

    # Top disagreements
    worst = sorted(comparisons, key=lambda x: -x["rel_diff"])[:10]

    return {
        "n_comparisons": n,
        "agreement_rates": agreement,
        "systematic_bias": {
            "mean_relative_diff_cod_minus_mp": round(mean_bias, 4),
            "median_relative_diff": round(median_bias, 4),
            "cod_larger_fraction": round(cod_larger / n, 4),
        },
        "z_ratio_matches": z_ratio_matches,
        "best_matches": sorted(comparisons, key=lambda x: x["rel_diff"])[:15],
        "worst_matches": worst,
    }


def analyze_crystal_systems(cod_table, mp_table):
    """Crystal system representation in each database."""
    # MP has crystal_system directly
    mp_systems = Counter()
    for entries in mp_table.values():
        for e in entries:
            cs = e.get("crystal_system")
            if cs:
                mp_systems[cs] += 1

    # COD: infer crystal system from spacegroup number
    def sg_to_crystal_system(sg_num):
        if sg_num is None:
            return None
        sg_num = int(sg_num)
        if 1 <= sg_num <= 2:
            return "Triclinic"
        elif 3 <= sg_num <= 15:
            return "Monoclinic"
        elif 16 <= sg_num <= 74:
            return "Orthorhombic"
        elif 75 <= sg_num <= 142:
            return "Tetragonal"
        elif 143 <= sg_num <= 167:
            return "Trigonal"
        elif 168 <= sg_num <= 194:
            return "Hexagonal"
        elif 195 <= sg_num <= 230:
            return "Cubic"
        return None

    cod_systems = Counter()
    for entries in cod_table.values():
        for e in entries:
            cs = sg_to_crystal_system(e.get("spacegroup_number"))
            if cs:
                cod_systems[cs] += 1

    all_systems = sorted(set(list(mp_systems.keys()) + list(cod_systems.keys())))

    print(f"\n=== Crystal System Distribution ===")
    print(f"{'System':<15} {'COD':>6} {'COD%':>6} {'MP':>6} {'MP%':>6}")
    print("-" * 45)
    total_cod = sum(cod_systems.values())
    total_mp = sum(mp_systems.values())
    comparison = {}
    for sys in all_systems:
        cc = cod_systems.get(sys, 0)
        mc = mp_systems.get(sys, 0)
        cp = cc / total_cod * 100 if total_cod > 0 else 0
        mp_p = mc / total_mp * 100 if total_mp > 0 else 0
        print(f"  {sys:<15} {cc:>5} {cp:>5.1f}% {mc:>5} {mp_p:>5.1f}%")
        comparison[sys] = {
            "cod_count": cc, "cod_pct": round(cp, 2),
            "mp_count": mc, "mp_pct": round(mp_p, 2),
        }

    cod_with_sg = total_cod
    cod_without_sg = sum(len(v) for v in cod_table.values()) - total_cod
    print(f"\n  COD with spacegroup: {cod_with_sg}, without: {cod_without_sg}")

    return {
        "crystal_systems": comparison,
        "cod_entries_with_spacegroup": cod_with_sg,
        "cod_entries_without_spacegroup": cod_without_sg,
        "mp_total": total_mp,
    }


def analyze_element_coverage(cod_table, mp_table):
    """Which elements are better represented in each?"""
    cod_elements = Counter()
    mp_elements = Counter()

    for entries in cod_table.values():
        for e in entries:
            raw = e.get("raw_formula", "")
            for elem in re.findall(r'[A-Z][a-z]?', raw):
                cod_elements[elem] += 1

    for entries in mp_table.values():
        for e in entries:
            raw = e.get("raw_formula", "")
            for elem in re.findall(r'[A-Z][a-z]?', raw):
                mp_elements[elem] += 1

    # Elements unique to each
    cod_only_elems = set(cod_elements.keys()) - set(mp_elements.keys())
    mp_only_elems = set(mp_elements.keys()) - set(cod_elements.keys())
    shared_elems = set(cod_elements.keys()) & set(mp_elements.keys())

    print(f"\n=== Element Coverage ===")
    print(f"  COD elements: {len(cod_elements)}")
    print(f"  MP elements:  {len(mp_elements)}")
    print(f"  Shared:       {len(shared_elems)}")
    print(f"  COD only:     {sorted(cod_only_elems)}")
    print(f"  MP only:      {sorted(mp_only_elems)}")

    # Top elements in each
    print(f"\n  Top 15 COD elements: {cod_elements.most_common(15)}")
    print(f"  Top 15 MP elements:  {mp_elements.most_common(15)}")

    return {
        "cod_element_count": len(cod_elements),
        "mp_element_count": len(mp_elements),
        "shared_elements": len(shared_elems),
        "cod_only_elements": sorted(cod_only_elems),
        "mp_only_elements": sorted(mp_only_elems),
        "top_cod": cod_elements.most_common(15),
        "top_mp": mp_elements.most_common(15),
    }


def analyze_nelements_overlap(cod_table, mp_table):
    """Overlap rates by number of elements."""
    shared = set(cod_table.keys()) & set(mp_table.keys())

    # Classify by nelements
    bins = defaultdict(lambda: {"cod": 0, "mp": 0, "shared": 0})

    for formula, entries in cod_table.items():
        nel = len(parse_formula(formula))
        bins[nel]["cod"] += 1
        if formula in shared:
            bins[nel]["shared"] += 1

    for formula, entries in mp_table.items():
        nel = len(parse_formula(formula))
        bins[nel]["mp"] += 1

    print(f"\n=== Overlap by Number of Elements ===")
    print(f"{'nelem':>5} {'COD':>6} {'MP':>6} {'shared':>6} {'overlap%':>8}")
    result = {}
    for nel in sorted(bins.keys()):
        b = bins[nel]
        union = b["cod"] + b["mp"] - b["shared"]
        pct = b["shared"] / union * 100 if union > 0 else 0
        print(f"  {nel:>3}   {b['cod']:>5}  {b['mp']:>5}  {b['shared']:>5}  {pct:>6.1f}%")
        result[nel] = {**b, "jaccard_pct": round(pct, 2)}

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    cod_raw, mp_raw = load_data()
    cod_table = build_cod_table(cod_raw)
    mp_table = build_mp_table(mp_raw)

    results = {
        "metadata": {
            "description": "COD vs Materials Project cross-validation",
            "cod_entries": len(cod_raw),
            "mp_entries": len(mp_raw),
            "cod_path": str(COD_PATH),
            "mp_path": str(MP_PATH),
        },
        "coverage": analyze_coverage(cod_table, mp_table),
        "volume_agreement": analyze_volume_agreement(cod_table, mp_table),
        "crystal_systems": analyze_crystal_systems(cod_table, mp_table),
        "element_coverage": analyze_element_coverage(cod_table, mp_table),
        "nelements_overlap": analyze_nelements_overlap(cod_table, mp_table),
    }

    # Save
    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()

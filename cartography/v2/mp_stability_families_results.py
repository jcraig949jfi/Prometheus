"""
Materials Project: Which Element Combinations Are Most Stable?

Compute mean formation energy per element combination type and identify
the "most stable" chemical families from 10K MP entries.
"""

import json
import re
import os
from collections import defaultdict
from pathlib import Path

# -- Electronegativity data (Pauling scale) --
ELECTRONEGATIVITY = {
    'H': 2.20, 'He': 0, 'Li': 0.98, 'Be': 1.57, 'B': 2.04, 'C': 2.55,
    'N': 3.04, 'O': 3.44, 'F': 3.98, 'Ne': 0, 'Na': 0.93, 'Mg': 1.31,
    'Al': 1.61, 'Si': 1.90, 'P': 2.19, 'S': 2.58, 'Cl': 3.16, 'Ar': 0,
    'K': 0.82, 'Ca': 1.00, 'Sc': 1.36, 'Ti': 1.54, 'V': 1.63, 'Cr': 1.66,
    'Mn': 1.55, 'Fe': 1.83, 'Co': 1.88, 'Ni': 1.91, 'Cu': 1.90, 'Zn': 1.65,
    'Ga': 1.81, 'Ge': 2.01, 'As': 2.18, 'Se': 2.55, 'Br': 2.96, 'Kr': 3.00,
    'Rb': 0.82, 'Sr': 0.95, 'Y': 1.22, 'Zr': 1.33, 'Nb': 1.60, 'Mo': 2.16,
    'Tc': 1.90, 'Ru': 2.20, 'Rh': 2.28, 'Pd': 2.20, 'Ag': 1.93, 'Cd': 1.69,
    'In': 1.78, 'Sn': 1.96, 'Sb': 2.05, 'Te': 2.10, 'I': 2.66, 'Xe': 2.60,
    'Cs': 0.79, 'Ba': 0.89, 'La': 1.10, 'Ce': 1.12, 'Pr': 1.13, 'Nd': 1.14,
    'Pm': 1.13, 'Sm': 1.17, 'Eu': 1.20, 'Gd': 1.20, 'Tb': 1.10, 'Dy': 1.22,
    'Ho': 1.23, 'Er': 1.24, 'Tm': 1.25, 'Yb': 1.10, 'Lu': 1.27, 'Hf': 1.30,
    'Ta': 1.50, 'W': 2.36, 'Re': 1.90, 'Os': 2.20, 'Ir': 2.20, 'Pt': 2.28,
    'Au': 2.54, 'Hg': 2.00, 'Tl': 1.62, 'Pb': 2.33, 'Bi': 2.02, 'Po': 2.00,
    'At': 2.20, 'Rn': 0, 'Fr': 0.70, 'Ra': 0.90, 'Ac': 1.10, 'Th': 1.30,
    'Pa': 1.50, 'U': 1.38, 'Np': 1.36, 'Pu': 1.28, 'Am': 1.13
}

# Metals (broad definition: alkali, alkaline earth, transition metals, lanthanides, actinides, post-transition)
METALS = {
    'Li', 'Be', 'Na', 'Mg', 'Al', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn',
    'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo',
    'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Cs', 'Ba', 'La', 'Ce',
    'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb',
    'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb',
    'Bi', 'Po', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am'
}

NONMETALS = {'H', 'He', 'C', 'N', 'O', 'F', 'Ne', 'P', 'S', 'Cl', 'Ar', 'Se', 'Br', 'Kr', 'I', 'Xe', 'Rn', 'At'}
METALLOIDS = {'B', 'Si', 'Ge', 'As', 'Sb', 'Te'}


def parse_elements(formula):
    """Extract unique element symbols from a chemical formula."""
    return sorted(set(re.findall(r'[A-Z][a-z]?', formula)))


def classify_bonding(elements):
    """Classify element combo as metal+nonmetal, metal+metal, nonmetal+nonmetal, or mixed."""
    has_metal = any(e in METALS for e in elements)
    has_nonmetal = any(e in NONMETALS for e in elements)
    has_metalloid = any(e in METALLOIDS for e in elements)

    if len(elements) == 1:
        return "elemental"
    if has_metal and has_nonmetal and not has_metalloid:
        return "metal+nonmetal"
    if has_metal and not has_nonmetal and not has_metalloid:
        return "metal+metal"
    if has_nonmetal and not has_metal and not has_metalloid:
        return "nonmetal+nonmetal"
    return "mixed/metalloid"


def max_en_diff(elements):
    """Compute max electronegativity difference across element pairs."""
    ens = [ELECTRONEGATIVITY.get(e, 0) for e in elements if ELECTRONEGATIVITY.get(e, 0) > 0]
    if len(ens) < 2:
        return 0.0
    return max(ens) - min(ens)


def main():
    data_path = Path(__file__).parent.parent / "physics" / "data" / "materials_project_10k.json"
    with open(data_path) as f:
        data = json.load(f)

    print(f"Loaded {len(data)} materials")

    # -- Group by element combination --
    combos = defaultdict(list)
    for entry in data:
        elems = tuple(parse_elements(entry["formula"]))
        combos[elems].append(entry)

    print(f"Unique element combinations: {len(combos)}")

    # -- Compute stats per combination --
    combo_stats = []
    for elems, entries in combos.items():
        e_forms = [e["formation_energy_per_atom"] for e in entries]
        gaps = [e["band_gap"] for e in entries]
        combo_stats.append({
            "elements": list(elems),
            "n_elements": len(elems),
            "count": len(entries),
            "mean_formation_energy": sum(e_forms) / len(e_forms),
            "min_formation_energy": min(e_forms),
            "max_formation_energy": max(e_forms),
            "mean_band_gap": sum(gaps) / len(gaps),
            "all_stable": all(e < 0 for e in e_forms),
            "bonding_type": classify_bonding(elems),
            "max_en_difference": max_en_diff(elems),
        })

    # -- Sort by mean formation energy (most negative = most stable) --
    combo_stats.sort(key=lambda x: x["mean_formation_energy"])

    # -- Most stable binary --
    binaries = [c for c in combo_stats if c["n_elements"] == 2]
    ternaries = [c for c in combo_stats if c["n_elements"] == 3]
    quaternaries = [c for c in combo_stats if c["n_elements"] == 4]
    unary = [c for c in combo_stats if c["n_elements"] == 1]

    print(f"\nBy arity: unary={len(unary)}, binary={len(binaries)}, "
          f"ternary={len(ternaries)}, quaternary+={len(quaternaries)}")

    print("\n-- TOP 10 MOST STABLE BINARIES (by mean E_form) --")
    for c in binaries[:10]:
        print(f"  {'-'.join(c['elements']):12s}  mean={c['mean_formation_energy']:+.4f}  "
              f"min={c['min_formation_energy']:+.4f}  n={c['count']}  "
              f"type={c['bonding_type']}  EN_diff={c['max_en_difference']:.2f}")

    print("\n-- TOP 10 MOST STABLE TERNARIES (by mean E_form) --")
    for c in ternaries[:10]:
        print(f"  {'-'.join(c['elements']):16s}  mean={c['mean_formation_energy']:+.4f}  "
              f"min={c['min_formation_energy']:+.4f}  n={c['count']}  "
              f"type={c['bonding_type']}  EN_diff={c['max_en_difference']:.2f}")

    # -- Deepest formation energy (hull) --
    best_binary_hull = min(binaries, key=lambda x: x["min_formation_energy"])
    best_ternary_hull = min(ternaries, key=lambda x: x["min_formation_energy"]) if ternaries else None

    print(f"\n-- DEEPEST BINARY (min E_form across all polymorphs) --")
    print(f"  {'-'.join(best_binary_hull['elements'])}  "
          f"min={best_binary_hull['min_formation_energy']:+.4f} eV/atom  n={best_binary_hull['count']}")

    if best_ternary_hull:
        print(f"\n-- DEEPEST TERNARY (min E_form across all polymorphs) --")
        print(f"  {'-'.join(best_ternary_hull['elements'])}  "
              f"min={best_ternary_hull['min_formation_energy']:+.4f} eV/atom  n={best_ternary_hull['count']}")

    # -- Stability vs bonding type --
    print("\n-- STABILITY BY BONDING TYPE --")
    type_stats = defaultdict(list)
    for c in combo_stats:
        if c["n_elements"] >= 2:
            type_stats[c["bonding_type"]].append(c["mean_formation_energy"])

    for btype, energies in sorted(type_stats.items()):
        mean_e = sum(energies) / len(energies)
        frac_stable = sum(1 for e in energies if e < 0) / len(energies)
        print(f"  {btype:20s}  n_combos={len(energies):4d}  "
              f"mean_E={mean_e:+.4f}  frac_stable={frac_stable:.3f}")

    # -- Electronegativity correlation --
    # Bin by EN difference and check stability
    print("\n-- STABILITY VS ELECTRONEGATIVITY DIFFERENCE --")
    en_bins = [(0, 0.5), (0.5, 1.0), (1.0, 1.5), (1.5, 2.0), (2.0, 2.5), (2.5, 4.0)]
    multi_elem = [c for c in combo_stats if c["n_elements"] >= 2 and c["max_en_difference"] > 0]

    for lo, hi in en_bins:
        in_bin = [c for c in multi_elem if lo <= c["max_en_difference"] < hi]
        if not in_bin:
            continue
        mean_e = sum(c["mean_formation_energy"] for c in in_bin) / len(in_bin)
        frac_neg = sum(1 for c in in_bin if c["mean_formation_energy"] < 0) / len(in_bin)
        print(f"  EN_diff [{lo:.1f}, {hi:.1f})  n={len(in_bin):4d}  "
              f"mean_E={mean_e:+.4f}  frac_stable={frac_neg:.3f}")

    # -- Fraction of combos where ALL polymorphs stable --
    multi_combos = [c for c in combo_stats if c["n_elements"] >= 2]
    n_all_stable = sum(1 for c in multi_combos if c["all_stable"])
    frac_all_stable = n_all_stable / len(multi_combos) if multi_combos else 0

    print(f"\n-- ALL-STABLE COMBOS --")
    print(f"  Multi-element combos: {len(multi_combos)}")
    print(f"  All polymorphs stable (E_form < 0): {n_all_stable} ({frac_all_stable:.1%})")

    # Compute Pearson correlation: EN_diff vs mean_formation_energy
    en_diffs = [c["max_en_difference"] for c in multi_elem]
    mean_es = [c["mean_formation_energy"] for c in multi_elem]
    n = len(en_diffs)
    if n > 2:
        mean_x = sum(en_diffs) / n
        mean_y = sum(mean_es) / n
        cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(en_diffs, mean_es)) / n
        std_x = (sum((x - mean_x)**2 for x in en_diffs) / n) ** 0.5
        std_y = (sum((y - mean_y)**2 for y in mean_es) / n) ** 0.5
        r = cov / (std_x * std_y) if std_x > 0 and std_y > 0 else 0
        print(f"\n  Pearson r(EN_diff, mean_E_form) = {r:.4f}  (n={n})")
        print(f"  {'Negative r => larger EN diff correlates with more negative (stable) formation energy' if r < 0 else 'Positive r => larger EN diff does NOT correlate with more stability'}")

    # -- Build results --
    results = {
        "dataset": "materials_project_10k",
        "n_materials": len(data),
        "n_unique_element_combos": len(combos),
        "by_arity": {
            "unary": len(unary),
            "binary": len(binaries),
            "ternary": len(ternaries),
            "quaternary_plus": len(quaternaries),
        },
        "top10_most_stable_binaries": [
            {
                "elements": c["elements"],
                "count": c["count"],
                "mean_formation_energy": round(c["mean_formation_energy"], 6),
                "min_formation_energy": round(c["min_formation_energy"], 6),
                "bonding_type": c["bonding_type"],
                "max_en_difference": round(c["max_en_difference"], 3),
            }
            for c in binaries[:10]
        ],
        "top10_most_stable_ternaries": [
            {
                "elements": c["elements"],
                "count": c["count"],
                "mean_formation_energy": round(c["mean_formation_energy"], 6),
                "min_formation_energy": round(c["min_formation_energy"], 6),
                "bonding_type": c["bonding_type"],
                "max_en_difference": round(c["max_en_difference"], 3),
            }
            for c in ternaries[:10]
        ],
        "deepest_binary": {
            "elements": best_binary_hull["elements"],
            "min_formation_energy": round(best_binary_hull["min_formation_energy"], 6),
            "count": best_binary_hull["count"],
        },
        "deepest_ternary": {
            "elements": best_ternary_hull["elements"],
            "min_formation_energy": round(best_ternary_hull["min_formation_energy"], 6),
            "count": best_ternary_hull["count"],
        } if best_ternary_hull else None,
        "stability_by_bonding_type": {
            btype: {
                "n_combos": len(energies),
                "mean_formation_energy": round(sum(energies) / len(energies), 6),
                "fraction_stable": round(sum(1 for e in energies if e < 0) / len(energies), 4),
            }
            for btype, energies in sorted(type_stats.items())
        },
        "stability_vs_electronegativity": [
            {
                "en_diff_range": [lo, hi],
                "n_combos": len([c for c in multi_elem if lo <= c["max_en_difference"] < hi]),
                "mean_formation_energy": round(
                    sum(c["mean_formation_energy"] for c in multi_elem if lo <= c["max_en_difference"] < hi)
                    / max(1, len([c for c in multi_elem if lo <= c["max_en_difference"] < hi])), 6
                ),
                "fraction_stable": round(
                    sum(1 for c in multi_elem if lo <= c["max_en_difference"] < hi and c["mean_formation_energy"] < 0)
                    / max(1, len([c for c in multi_elem if lo <= c["max_en_difference"] < hi])), 4
                ),
            }
            for lo, hi in en_bins
            if len([c for c in multi_elem if lo <= c["max_en_difference"] < hi]) > 0
        ],
        "en_diff_vs_stability_pearson_r": round(r, 4) if n > 2 else None,
        "all_stable_fraction": {
            "n_multi_element_combos": len(multi_combos),
            "n_all_polymorphs_stable": n_all_stable,
            "fraction": round(frac_all_stable, 4),
        },
    }

    # -- Save --
    out_path = Path(__file__).with_suffix(".json").parent / "mp_stability_families_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved results to {out_path}")


if __name__ == "__main__":
    main()

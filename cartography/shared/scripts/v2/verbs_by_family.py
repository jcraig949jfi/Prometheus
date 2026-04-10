#!/usr/bin/env python3
"""
Challenge CL3-P3#10: Map Which Universal Verbs Dominate in Each Scaling-Law Family

Connects CL1 (scaling slopes), C12 (4 universal operators), and R4-4 (slope vs endo rank).
Key question: do high-slope families use different verbs than low-slope families?

Outputs: verbs_by_family_results.json
"""

import json
import math
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

V2 = Path(__file__).parent
DATA_ROOT = V2.parent.parent.parent  # cartography/
FUNGRIM_INDEX = DATA_ROOT / "fungrim" / "data" / "fungrim_index.json"
SCALING_REVERSE = V2 / "scaling_law_reverse_results.json"
SCALING_ST = V2 / "scaling_vs_st_order_results.json"
OPERADIC = V2 / "operadic_dynamics_results.json"
GAMMA_WORMHOLE = V2 / "gamma_wormhole_results.json"
SCALING_BATTERY = V2 / "scaling_law_battery_results.json"

OUT = V2 / "verbs_by_family_results.json"

# The 4 universal verbs from C12
UNIVERSAL_VERBS = ["Equal", "For", "And", "Set"]

# Domain/number-type symbols (not verbs)
DOMAIN_SYMBOLS = {
    "CC", "RR", "ZZ", "QQ", "NN", "ZZGreaterEqual", "ZZLessEqual",
    "OpenInterval", "ClosedInterval", "OpenClosedInterval", "ClosedOpenInterval",
    "HH", "UnitCircle", "PP", "This", "Illustrations", "Represents",
    "Arithmetic", "Convergents"
}


def load_json(path):
    with open(path) as f:
        return json.load(f)


def compute_module_verb_distributions(fungrim):
    """For each Fungrim module, count verb/operator usage across formulas."""
    module_formulas = defaultdict(list)
    for formula in fungrim["formulas"]:
        module_formulas[formula["module"]].append(formula)

    module_verbs = {}
    for module, formulas in module_formulas.items():
        all_symbols = Counter()
        verb_symbols = Counter()  # non-domain symbols
        n_formulas = len(formulas)

        for f in formulas:
            for sym in f["symbols"]:
                all_symbols[sym] += 1
                if sym not in DOMAIN_SYMBOLS:
                    verb_symbols[sym] += 1

        # Universal verb fractions
        universal_counts = {v: all_symbols.get(v, 0) for v in UNIVERSAL_VERBS}
        total_symbol_uses = sum(all_symbols.values())
        universal_fracs = {
            v: c / n_formulas for v, c in universal_counts.items()
        }  # fraction of formulas using each verb

        # Per-formula presence (not just count)
        verb_presence = {v: 0 for v in UNIVERSAL_VERBS}
        for f in formulas:
            syms = set(f["symbols"])
            for v in UNIVERSAL_VERBS:
                if v in syms:
                    verb_presence[v] += 1
        verb_presence_frac = {v: c / n_formulas for v, c in verb_presence.items()}

        # Module-specific operators (non-universal, non-domain)
        specific_ops = Counter()
        for sym, count in verb_symbols.items():
            if sym not in UNIVERSAL_VERBS:
                specific_ops[sym] = count

        module_verbs[module] = {
            "n_formulas": n_formulas,
            "universal_verb_presence": verb_presence_frac,
            "universal_verb_counts": universal_counts,
            "top_specific_ops": dict(specific_ops.most_common(10)),
            "total_symbol_uses": total_symbol_uses,
            "unique_symbols": len(all_symbols),
        }

    return module_verbs


def compute_module_scaling_slopes(fungrim):
    """
    Compute a per-module 'scaling slope' analogous to CL1.

    CL1 measured enrichment decay across primes for ST groups.
    For Fungrim modules, we compute: for each module, what fraction of
    formula pairs share exact coefficients mod p, and how does this decay?

    Proxy: we use the operadic within-module distance as a measure of
    internal coherence (lower = more algebraically tight = higher effective slope).
    Combined with the formula count, this gives a module-level 'algebraic depth'.
    """
    operadic = load_json(OPERADIC)
    within_dists = operadic["within_module_distances"]

    # The "slope" proxy: modules with LOW within-module distance have HIGH
    # algebraic coherence — they are tightly structured families.
    # We invert: slope_proxy = 1 - within_distance (higher = more coherent)
    module_slopes = {}
    for module, dist in within_dists.items():
        module_slopes[module] = {
            "within_distance": dist,
            "coherence": round(1.0 - dist, 6),  # higher = tighter family
        }

    return module_slopes


def compute_gamma_bridge_strength(fungrim):
    """Per-module Gamma bridge strength from CL5 data."""
    gamma_data = load_json(GAMMA_WORMHOLE)
    gamma_core = set(gamma_data["gamma_family"]["core_modules"])
    gamma_extended = set(gamma_data["gamma_family"]["extended_modules"])

    # Build per-module gamma connectivity from cross_pairs_ranked
    module_gamma_deltas = defaultdict(list)
    for pair in gamma_data["cross_pairs_ranked"]:
        ma, mb = pair["module_a"], pair["module_b"]
        delta = pair.get("delta", 0)
        gamma_closer = pair.get("gamma_closer", False)
        if gamma_closer:
            module_gamma_deltas[ma].append(delta)
            module_gamma_deltas[mb].append(delta)

    module_gamma = {}
    for module in fungrim["module_stats"]:
        is_core = module in gamma_core
        is_extended = module in gamma_extended
        deltas = module_gamma_deltas.get(module, [])
        avg_delta = float(np.mean(deltas)) if deltas else 0.0

        module_gamma[module] = {
            "is_gamma_core": is_core,
            "is_gamma_extended": is_extended,
            "n_gamma_bridges": len(deltas),
            "avg_gamma_delta": round(avg_delta, 6),
        }

    return module_gamma


def compute_st_group_concept_links():
    """
    Link genus-2 ST groups to Fungrim modules via shared concepts.

    ST groups connect to Fungrim through:
    - Sato-Tate -> riemann_zeta, dirichlet (L-functions)
    - Endomorphism types -> modular forms -> eisenstein, dedekind_eta, modular_j
    - Genus-2 curves -> weierstrass_elliptic, legendre_elliptic
    - Component groups -> partitions, factorials (group theory)
    """
    st_data = load_json(SCALING_ST)

    # Concept mapping: which Fungrim modules are conceptually linked to each ST group
    # Based on the mathematical content:
    concept_links = {
        "USp(4)": {
            "primary": ["riemann_zeta", "dirichlet", "gamma", "pi"],
            "secondary": ["weierstrass_elliptic", "legendre_elliptic", "eisenstein"],
            "reason": "Generic: full symplectic group, L-function theory"
        },
        "G_{3,3}": {
            "primary": ["weierstrass_elliptic", "legendre_elliptic", "modular_j"],
            "secondary": ["eisenstein", "dedekind_eta", "riemann_zeta"],
            "reason": "RM: real multiplication, elliptic curve products"
        },
        "N(G_{1,3})": {
            "primary": ["weierstrass_elliptic", "legendre_elliptic", "modular_j"],
            "secondary": ["eisenstein", "dedekind_eta", "jacobi_theta"],
            "reason": "RM normalizer: extra symmetry in real multiplication"
        },
        "N(G_{3,3})": {
            "primary": ["modular_j", "eisenstein", "jacobi_theta"],
            "secondary": ["weierstrass_elliptic", "dedekind_eta", "modular_lambda"],
            "reason": "QM: quaternionic multiplication, modular parametrization"
        },
        "E_6": {
            "primary": ["weierstrass_elliptic", "legendre_elliptic", "carlson_elliptic"],
            "secondary": ["modular_j", "eisenstein", "const_gamma"],
            "reason": "CM: complex multiplication, elliptic curves with extra endomorphisms"
        },
        "J(E_1)": {
            "primary": ["modular_j", "eisenstein", "jacobi_theta"],
            "secondary": ["weierstrass_elliptic", "dedekind_eta", "gamma"],
            "reason": "QM product: Jacobian of CM elliptic curve"
        },
    }

    return concept_links, st_data


def correlate_slope_vs_verbs(module_verbs, module_slopes):
    """Compute correlation between coherence (slope proxy) and universal verb fractions."""
    modules = sorted(set(module_verbs.keys()) & set(module_slopes.keys()))

    results = {}
    for verb in UNIVERSAL_VERBS:
        coherences = []
        fracs = []
        for m in modules:
            coherences.append(module_slopes[m]["coherence"])
            fracs.append(module_verbs[m]["universal_verb_presence"].get(verb, 0))

        if len(coherences) >= 5:
            r = float(np.corrcoef(coherences, fracs)[0, 1])
        else:
            r = None

        results[verb] = {
            "pearson_r": round(r, 6) if r is not None else None,
            "n_modules": len(modules),
            "mean_fraction": round(float(np.mean(fracs)), 6),
            "std_fraction": round(float(np.std(fracs)), 6),
        }

    return results


def correlate_slope_vs_gamma(module_slopes, module_gamma):
    """Correlate coherence (slope proxy) with Gamma bridge strength."""
    modules = sorted(set(module_slopes.keys()) & set(module_gamma.keys()))

    coherences = []
    gamma_deltas = []
    gamma_core_flag = []

    for m in modules:
        coherences.append(module_slopes[m]["coherence"])
        gamma_deltas.append(module_gamma[m]["avg_gamma_delta"])
        gamma_core_flag.append(1.0 if module_gamma[m]["is_gamma_core"] else 0.0)

    # Filter out modules with no gamma data for delta correlation
    valid_idx = [i for i, d in enumerate(gamma_deltas) if d > 0]
    if len(valid_idx) >= 5:
        c_valid = [coherences[i] for i in valid_idx]
        g_valid = [gamma_deltas[i] for i in valid_idx]
        r_delta = float(np.corrcoef(c_valid, g_valid)[0, 1])
    else:
        r_delta = None
    r_core = float(np.corrcoef(coherences, gamma_core_flag)[0, 1]) if len(coherences) >= 5 else None

    # Compare verb distributions: Gamma-core vs non-Gamma modules
    return {
        "coherence_vs_gamma_delta": round(r_delta, 6) if r_delta is not None else None,
        "coherence_vs_gamma_core": round(r_core, 6) if r_core is not None else None,
        "n_modules": len(modules),
    }


def st_group_verb_analysis(concept_links, st_data, module_verbs):
    """For each ST group, aggregate verb distributions from linked Fungrim modules."""
    st_slopes = st_data["st_slopes_with_ci"]

    st_verb_profiles = {}
    for group, links in concept_links.items():
        slope_info = st_slopes.get(group, {})
        slope = slope_info.get("slope", 0)

        # Aggregate verb presence from primary + secondary modules
        all_linked = links["primary"] + links["secondary"]
        available = [m for m in all_linked if m in module_verbs]

        agg_verb_presence = {v: 0.0 for v in UNIVERSAL_VERBS}
        agg_specific = Counter()
        total_formulas = 0

        for m in available:
            mv = module_verbs[m]
            n = mv["n_formulas"]
            total_formulas += n
            for v in UNIVERSAL_VERBS:
                agg_verb_presence[v] += mv["universal_verb_counts"].get(v, 0)
            for op, count in mv["top_specific_ops"].items():
                agg_specific[op] += count

        if total_formulas > 0:
            agg_verb_frac = {v: round(c / total_formulas, 6) for v, c in agg_verb_presence.items()}
        else:
            agg_verb_frac = {v: 0.0 for v in UNIVERSAL_VERBS}

        st_verb_profiles[group] = {
            "slope": round(slope, 6),
            "ci_lo": round(slope_info.get("ci_lo", 0), 6),
            "ci_hi": round(slope_info.get("ci_hi", 0), 6),
            "n_curves": slope_info.get("n_curves", 0),
            "linked_modules": available,
            "total_linked_formulas": total_formulas,
            "universal_verb_fractions": agg_verb_frac,
            "top_specific_ops": dict(agg_specific.most_common(8)),
            "endo_type": st_data["group_parameters"].get(group, {}).get("endo_type", "?"),
            "endo_rank": st_data["group_parameters"].get(group, {}).get("endo_rank", 0),
        }

    return st_verb_profiles


def rank_modules_by_verb_profile(module_verbs, module_slopes):
    """Classify modules into high-coherence vs low-coherence and compare verb profiles."""
    modules = sorted(set(module_verbs.keys()) & set(module_slopes.keys()))
    coherences = [(m, module_slopes[m]["coherence"]) for m in modules]
    coherences.sort(key=lambda x: x[1], reverse=True)

    n = len(coherences)
    top_third = coherences[:n // 3]
    bottom_third = coherences[2 * n // 3:]

    def avg_verb_profile(module_list):
        profile = {v: [] for v in UNIVERSAL_VERBS}
        for m, _ in module_list:
            for v in UNIVERSAL_VERBS:
                profile[v].append(module_verbs[m]["universal_verb_presence"].get(v, 0))
        return {v: round(float(np.mean(vals)), 6) if vals else 0.0 for v, vals in profile.items()}

    high = avg_verb_profile(top_third)
    low = avg_verb_profile(bottom_third)

    diff = {v: round(high[v] - low[v], 6) for v in UNIVERSAL_VERBS}

    return {
        "high_coherence_modules": [m for m, _ in top_third],
        "low_coherence_modules": [m for m, _ in bottom_third],
        "high_coherence_verb_profile": high,
        "low_coherence_verb_profile": low,
        "verb_difference_high_minus_low": diff,
        "interpretation": (
            "Positive diff = verb is MORE common in high-coherence (tight) families; "
            "Negative = more common in low-coherence (loose) families"
        ),
    }


def main():
    print("Loading data...")
    fungrim = load_json(FUNGRIM_INDEX)
    print(f"  Fungrim: {len(fungrim['formulas'])} formulas, {len(fungrim['module_stats'])} modules")

    # 1. Per-module verb distributions
    print("Computing per-module verb distributions...")
    module_verbs = compute_module_verb_distributions(fungrim)
    print(f"  Analyzed {len(module_verbs)} modules")

    # 2. Per-module scaling slope proxy (coherence from operadic distance)
    print("Computing per-module coherence (slope proxy)...")
    module_slopes = compute_module_scaling_slopes(fungrim)

    # 3. Per-module Gamma bridge strength
    print("Computing per-module Gamma bridge strength...")
    module_gamma = compute_gamma_bridge_strength(fungrim)

    # 4. Correlation: slope vs verb fractions
    print("Computing slope-verb correlations...")
    slope_verb_corr = correlate_slope_vs_verbs(module_verbs, module_slopes)

    # 5. Correlation: slope vs Gamma
    print("Computing slope-Gamma correlations...")
    slope_gamma_corr = correlate_slope_vs_gamma(module_slopes, module_gamma)

    # 6. ST group verb analysis
    print("Analyzing ST group verb profiles...")
    concept_links, st_data = compute_st_group_concept_links()
    st_verb_profiles = st_group_verb_analysis(concept_links, st_data, module_verbs)

    # 7. High vs Low coherence verb comparison
    print("Comparing high vs low coherence verb profiles...")
    coherence_comparison = rank_modules_by_verb_profile(module_verbs, module_slopes)

    # 8. Detailed per-module table (top 15 most coherent, top 15 least)
    modules_sorted = sorted(
        module_slopes.keys(),
        key=lambda m: module_slopes[m]["coherence"],
        reverse=True,
    )
    top_modules = []
    for m in modules_sorted[:15]:
        top_modules.append({
            "module": m,
            "coherence": module_slopes[m]["coherence"],
            "n_formulas": module_verbs.get(m, {}).get("n_formulas", 0),
            "verb_presence": module_verbs.get(m, {}).get("universal_verb_presence", {}),
            "gamma_core": module_gamma.get(m, {}).get("is_gamma_core", False),
            "top_specific": list(module_verbs.get(m, {}).get("top_specific_ops", {}).keys())[:5],
        })

    bottom_modules = []
    for m in modules_sorted[-15:]:
        bottom_modules.append({
            "module": m,
            "coherence": module_slopes[m]["coherence"],
            "n_formulas": module_verbs.get(m, {}).get("n_formulas", 0),
            "verb_presence": module_verbs.get(m, {}).get("universal_verb_presence", {}),
            "gamma_core": module_gamma.get(m, {}).get("is_gamma_core", False),
            "top_specific": list(module_verbs.get(m, {}).get("top_specific_ops", {}).keys())[:5],
        })

    # 9. ST slope vs verb fraction correlation
    st_slope_verb_corr = {}
    st_groups = list(st_verb_profiles.keys())
    if len(st_groups) >= 4:
        for verb in UNIVERSAL_VERBS:
            slopes = [st_verb_profiles[g]["slope"] for g in st_groups]
            fracs = [st_verb_profiles[g]["universal_verb_fractions"].get(verb, 0) for g in st_groups]
            r = float(np.corrcoef(slopes, fracs)[0, 1])
            st_slope_verb_corr[verb] = {
                "pearson_r": round(r, 6),
                "n_groups": len(st_groups),
            }

    # Assemble results
    results = {
        "meta": {
            "challenge": "CL3_P3_10",
            "title": "Universal Verbs by Scaling-Law Family",
            "timestamp": __import__("datetime").datetime.now().isoformat()[:19],
            "n_modules": len(module_verbs),
            "n_formulas": len(fungrim["formulas"]),
            "n_st_groups": len(st_verb_profiles),
            "universal_verbs": UNIVERSAL_VERBS,
        },
        "slope_verb_correlations": slope_verb_corr,
        "slope_gamma_correlations": slope_gamma_corr,
        "st_group_verb_profiles": st_verb_profiles,
        "st_slope_vs_verb_correlations": st_slope_verb_corr,
        "coherence_comparison": coherence_comparison,
        "top_coherence_modules": top_modules,
        "bottom_coherence_modules": bottom_modules,
        "interpretation": {
            "slope_verb": (
                "Correlation between module coherence (1 - operadic distance) and "
                "fraction of formulas using each universal verb. Positive r means "
                "tighter families use that verb MORE."
            ),
            "slope_gamma": (
                "Correlation between module coherence and Gamma bridge strength. "
                "Tests whether algebraically tight families are more/less Gamma-connected."
            ),
            "st_groups": (
                "For each genus-2 ST group, verb distributions are aggregated from "
                "conceptually linked Fungrim modules. High-slope ST groups (N(G_{3,3}), "
                "J(E_1)) should show different verb signatures than low-slope (G_{3,3})."
            ),
            "key_question": (
                "If high-slope families are dominated by DIFFERENT verbs than low-slope "
                "families, algebraic depth (slope) connects to syntactic structure (operadic "
                "verb). This bridges CL1 and C12."
            ),
        },
    }

    # Print summary
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    print("\n1. SLOPE-VERB CORRELATIONS (module coherence vs verb presence):")
    for verb, data in slope_verb_corr.items():
        r = data["pearson_r"]
        if r is not None:
            direction = "MORE in tight" if r > 0 else "MORE in loose"
            strength = "strong" if abs(r) > 0.4 else "moderate" if abs(r) > 0.2 else "weak"
            print(f"   {verb:8s}: r = {r:+.4f} ({strength}, {direction})")

    print("\n2. SLOPE-GAMMA CORRELATIONS:")
    r_delta = slope_gamma_corr.get("coherence_vs_gamma_delta")
    r_core = slope_gamma_corr.get("coherence_vs_gamma_core")
    if r_delta is not None:
        print(f"   Coherence vs Gamma delta:  r = {r_delta:+.4f}")
    if r_core is not None:
        print(f"   Coherence vs Gamma core:   r = {r_core:+.4f}")

    print("\n3. HIGH vs LOW COHERENCE VERB PROFILES:")
    cc = coherence_comparison
    print(f"   High coherence ({len(cc['high_coherence_modules'])} modules):")
    for v in UNIVERSAL_VERBS:
        print(f"     {v:8s}: {cc['high_coherence_verb_profile'][v]:.4f}")
    print(f"   Low coherence ({len(cc['low_coherence_modules'])} modules):")
    for v in UNIVERSAL_VERBS:
        print(f"     {v:8s}: {cc['low_coherence_verb_profile'][v]:.4f}")
    print(f"   Difference (high - low):")
    for v in UNIVERSAL_VERBS:
        d = cc['verb_difference_high_minus_low'][v]
        print(f"     {v:8s}: {d:+.4f}")

    print("\n4. ST GROUP VERB PROFILES:")
    for group in sorted(st_verb_profiles.keys(), key=lambda g: st_verb_profiles[g]["slope"]):
        p = st_verb_profiles[group]
        print(f"   {group:12s} (slope={p['slope']:+.4f}, endo={p['endo_type']}, rank={p['endo_rank']}):")
        for v in UNIVERSAL_VERBS:
            print(f"     {v:8s}: {p['universal_verb_fractions'].get(v, 0):.4f}")
        print(f"     specific: {list(p['top_specific_ops'].keys())[:5]}")

    print("\n5. ST SLOPE vs VERB CORRELATION:")
    for verb, data in st_slope_verb_corr.items():
        r = data["pearson_r"]
        print(f"   {verb:8s}: r = {r:+.4f}")

    # Save
    with open(OUT, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {OUT}")


if __name__ == "__main__":
    main()

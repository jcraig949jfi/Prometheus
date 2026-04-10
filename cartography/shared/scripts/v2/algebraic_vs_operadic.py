"""
Algebraic Family Clusters vs Operadic Skeleton Partition
========================================================
Challenge C08 #8: Do algebraic family clusters (shared characteristic
polynomial from BM) respect the operadic skeleton partition (Fungrim
module structure + operator types from C12)?

Three-layer analysis:
  Layer 1: Module-level -- do algebraic families touch one or many Fungrim modules?
  Layer 2: Operator-profile -- do all Fungrim-connected formulas in a family
           share the same structural operator signature?
  Layer 3: Reverse -- do Fungrim modules contain one or many char polys?

Hierarchy test: which partition is coarser (recurrence or skeleton)?

Usage:
    python algebraic_vs_operadic.py
"""

import json
import math
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[4]
V2_DIR = Path(__file__).resolve().parent
C08_RESULTS = V2_DIR / "recurrence_euler_factor_results.json"
C11_RESULTS = V2_DIR / "algebraic_dna_fungrim_results.json"
C12_RESULTS = V2_DIR / "operadic_dynamics_results.json"
FUNGRIM_INDEX = ROOT / "cartography" / "fungrim" / "data" / "fungrim_index.json"
OUT_FILE = V2_DIR / "algebraic_vs_operadic_results.json"

# Structural operators (the "verbs" of mathematics)
STRUCTURAL_OPS = frozenset({
    "Equal", "For", "And", "Set", "Sum", "Integral",
    "Product", "Limit", "Derivative", "ComplexDerivative",
    "Div", "Add", "Sub", "Mul", "Pow", "Neg",
    "Factorial", "Binomial", "Abs", "Sqrt",
    "Floor", "Ceil", "Less", "LessEqual", "Greater",
    "GreaterEqual", "NotEqual", "Element", "Not",
    "Or", "Implies", "Equivalent", "Exists", "ForAll",
    "Where", "Def", "Solutions", "Zeros", "Poles",
    "Residues", "Image", "Convergents",
})

# Domain/context markers (not operadically meaningful)
DOMAIN_MARKERS = frozenset({
    "CC", "RR", "ZZ", "QQ", "HH", "NN", "PP",
    "ZZGreaterEqual", "ZZLessEqual", "ZZBetween",
    "ClosedInterval", "OpenInterval", "OpenClosedInterval",
    "ClosedOpenInterval", "This", "Illustrations", "Plot",
    "Represents", "ImageSource", "Arithmetic",
})


def load_data():
    """Load all upstream datasets."""
    print("[1] Loading upstream data...")

    with open(str(C08_RESULTS)) as f:
        c08 = json.load(f)
    poly_clusters = c08["polynomial_clusters"]["top_clusters"]
    total_clusters = c08["polynomial_clusters"]["total_clusters"]
    print(f"  C08: {len(poly_clusters)} top clusters (of {total_clusters} total)")

    with open(str(C11_RESULTS)) as f:
        c11 = json.load(f)
    all_cluster_results = c11["all_cluster_results"]
    print(f"  C11: {len(all_cluster_results)} cluster results")

    with open(str(C12_RESULTS)) as f:
        c12 = json.load(f)
    print(f"  C12: {c12['meta']['n_formulas_analyzed']} formulas analyzed")

    with open(str(FUNGRIM_INDEX)) as f:
        fungrim = json.load(f)
    print(f"  Fungrim: {fungrim['n_formulas']} formulas, {fungrim['n_modules']} modules")

    return poly_clusters, all_cluster_results, c12, fungrim


def build_formula_signatures(fungrim):
    """
    Build operadic signature for each Fungrim formula.

    The operadic signature of a formula is its set of structural operators,
    stripped of domain-specific functions and context markers. This is the
    "tree shape" -- the verbs without the nouns.

    Returns:
        formula_sigs: {formula_id: frozenset of structural ops}
        formula_modules: {formula_id: module_name}
        module_formulas: {module_name: [formula_ids]}
        module_op_profiles: {module_name: Counter of structural ops across formulas}
    """
    print("\n[2] Building formula-level operadic signatures...")

    formula_sigs = {}
    formula_modules = {}
    module_formulas = defaultdict(list)
    module_op_profiles = defaultdict(Counter)

    for f in fungrim["formulas"]:
        fid = f["id"]
        mod = f["module"]
        ops = frozenset(s for s in f["symbols"] if s in STRUCTURAL_OPS)
        domain_fns = frozenset(s for s in f["symbols"]
                               if s not in STRUCTURAL_OPS and s not in DOMAIN_MARKERS)

        formula_sigs[fid] = ops
        formula_modules[fid] = mod
        module_formulas[mod].append(fid)
        for op in ops:
            module_op_profiles[mod][op] += 1

    # Compute distinct signature count per module
    module_sig_counts = {}
    for mod, fids in module_formulas.items():
        unique_sigs = len(set(formula_sigs[fid] for fid in fids))
        module_sig_counts[mod] = unique_sigs

    print(f"  {len(formula_sigs)} formulas with operadic signatures")
    print(f"  {len(module_formulas)} modules")
    avg_sigs = sum(module_sig_counts.values()) / max(len(module_sig_counts), 1)
    print(f"  Avg distinct signatures per module: {avg_sigs:.1f}")

    return formula_sigs, formula_modules, module_formulas, module_op_profiles


def signature_to_class(sig):
    """
    Map a structural operator signature to an operadic class label.

    Classes are defined by which "tiers" of operators are present:
      Tier 1 (core): Equal, For, And
      Tier 2 (arithmetic): Add, Sub, Mul, Div, Pow, Neg, Sqrt
      Tier 3 (analytic): Sum, Product, Integral, Limit, Derivative, ComplexDerivative
      Tier 4 (combinatorial): Factorial, Binomial, Floor, Ceil
      Tier 5 (relational): Less, LessEqual, Greater, GreaterEqual, NotEqual
      Tier 6 (set-theoretic): Set, Element, Exists, ForAll, Or, Not, Implies, Equivalent
      Tier 7 (special): Zeros, Poles, Residues, Solutions, Image, Convergents, Def, Where, Abs
    """
    tiers = {
        "core": {"Equal", "For", "And"},
        "arith": {"Add", "Sub", "Mul", "Div", "Pow", "Neg", "Sqrt"},
        "analytic": {"Sum", "Product", "Integral", "Limit", "Derivative", "ComplexDerivative"},
        "combin": {"Factorial", "Binomial", "Floor", "Ceil"},
        "relational": {"Less", "LessEqual", "Greater", "GreaterEqual", "NotEqual"},
        "settheory": {"Set", "Element", "Exists", "ForAll", "Or", "Not", "Implies", "Equivalent"},
        "special": {"Zeros", "Poles", "Residues", "Solutions", "Image", "Convergents", "Def", "Where", "Abs"},
    }
    present = []
    for tier_name, tier_ops in tiers.items():
        if sig & tier_ops:
            present.append(tier_name)
    return "+".join(present) if present else "empty"


def analyze_algebraic_families(all_cluster_results, formula_sigs,
                                formula_modules, module_formulas):
    """
    Layer 1 & 2: For each algebraic family with Fungrim connections,
    analyze operadic homogeneity at module and signature levels.
    """
    print("\n[3] Analyzing algebraic families vs operadic signatures...")

    families = [c for c in all_cluster_results
                if c.get("fungrim_modules") and len(c["fungrim_modules"]) > 0]
    print(f"  {len(families)} algebraic families have Fungrim connections")

    # Module-level homogeneity
    mod_homogeneous = 0
    mod_heterogeneous = 0

    # Signature-class level homogeneity
    class_homogeneous = 0
    class_heterogeneous = 0

    family_analyses = []

    for fam in families:
        modules = fam["fungrim_modules"]
        char_poly = fam["char_poly_str"]

        # Collect all formula signatures across connected modules
        all_formula_ids = []
        for mod in modules:
            all_formula_ids.extend(module_formulas.get(mod, []))

        # Get signature classes for all connected formulas
        sig_classes = Counter()
        for fid in all_formula_ids:
            sig = formula_sigs.get(fid, frozenset())
            cls = signature_to_class(sig)
            sig_classes[cls] += 1

        # Module-level: single module or multiple?
        n_modules = len(modules)
        is_mod_homogeneous = n_modules == 1
        if is_mod_homogeneous:
            mod_homogeneous += 1
        else:
            mod_heterogeneous += 1

        # Signature-class level: single class or multiple?
        n_classes = len(sig_classes)
        is_class_homogeneous = n_classes == 1
        if is_class_homogeneous:
            class_homogeneous += 1
        else:
            class_heterogeneous += 1

        # Compute dominant class fraction (how concentrated is the family?)
        total_formulas = sum(sig_classes.values())
        dominant_class, dominant_count = sig_classes.most_common(1)[0] if sig_classes else ("empty", 0)
        dominant_fraction = dominant_count / max(total_formulas, 1)

        # Categorize each module by its dominant operadic class
        module_classes = {}
        for mod in modules:
            mod_fids = module_formulas.get(mod, [])
            mod_classes = Counter()
            for fid in mod_fids:
                sig = formula_sigs.get(fid, frozenset())
                cls = signature_to_class(sig)
                mod_classes[cls] += 1
            if mod_classes:
                dom_cls = mod_classes.most_common(1)[0][0]
            else:
                dom_cls = "empty"
            module_classes[mod] = dom_cls

        # How many distinct dominant classes across modules?
        distinct_module_classes = set(module_classes.values())
        n_distinct_module_classes = len(distinct_module_classes)

        analysis = {
            "char_poly": char_poly,
            "degree": fam["degree"],
            "n_sequences": fam["n_sequences"],
            "n_modules": n_modules,
            "modules": modules,
            "n_signature_classes": n_classes,
            "signature_class_distribution": dict(sig_classes.most_common()),
            "dominant_class": dominant_class,
            "dominant_fraction": round(dominant_fraction, 4),
            "is_module_homogeneous": is_mod_homogeneous,
            "is_class_homogeneous": is_class_homogeneous,
            "n_distinct_module_classes": n_distinct_module_classes,
            "module_dominant_classes": module_classes,
            "is_euler_factor": fam.get("is_euler_factor", False),
            "total_connected_formulas": total_formulas,
        }

        family_analyses.append(analysis)

    family_analyses.sort(key=lambda x: -x["n_sequences"])

    total = len(families)
    print(f"\n  Module-level homogeneity:")
    print(f"    Homogeneous (single module): {mod_homogeneous}/{total} "
          f"({100*mod_homogeneous/max(total,1):.1f}%)")
    print(f"    Heterogeneous (multi-module): {mod_heterogeneous}/{total} "
          f"({100*mod_heterogeneous/max(total,1):.1f}%)")
    print(f"\n  Signature-class homogeneity:")
    print(f"    Homogeneous (single class): {class_homogeneous}/{total} "
          f"({100*class_homogeneous/max(total,1):.1f}%)")
    print(f"    Heterogeneous (multi-class): {class_heterogeneous}/{total} "
          f"({100*class_heterogeneous/max(total,1):.1f}%)")

    # Dominant fraction statistics
    dom_fracs = [a["dominant_fraction"] for a in family_analyses]
    if dom_fracs:
        print(f"\n  Dominant class fraction stats:")
        print(f"    Mean: {sum(dom_fracs)/len(dom_fracs):.3f}")
        print(f"    Min: {min(dom_fracs):.3f}, Max: {max(dom_fracs):.3f}")
        above_80 = sum(1 for f in dom_fracs if f >= 0.8)
        print(f"    Families with >80%% concentration: {above_80}/{total}")

    # Module-class homogeneity (all modules in family have same dominant class?)
    mc_homo = sum(1 for a in family_analyses if a["n_distinct_module_classes"] == 1)
    print(f"\n  Module-class homogeneity (all modules share dominant class):")
    print(f"    {mc_homo}/{total} ({100*mc_homo/max(total,1):.1f}%)")

    return family_analyses, {
        "n_families": total,
        "module_homogeneous": mod_homogeneous,
        "module_heterogeneous": mod_heterogeneous,
        "class_homogeneous": class_homogeneous,
        "class_heterogeneous": class_heterogeneous,
        "module_class_homogeneous": mc_homo,
        "avg_dominant_fraction": round(sum(dom_fracs)/max(len(dom_fracs), 1), 4),
    }


def reverse_test(all_cluster_results, formula_sigs, module_formulas):
    """
    Reverse: for each Fungrim module, how many distinct char polys
    does it connect to? If module = operadic class, is it algebraically pure?
    """
    print("\n[4] Reverse test: Fungrim modules -> algebraic families...")

    # Build module -> char polys
    module_to_polys = defaultdict(set)
    module_to_seqcount = defaultdict(int)

    for c in all_cluster_results:
        if not c.get("fungrim_modules"):
            continue
        poly = c["char_poly_str"]
        for mod in c["fungrim_modules"]:
            module_to_polys[mod].add(poly)
            module_to_seqcount[mod] += c["n_sequences"]

    module_analyses = []
    homo = 0
    hetero = 0

    for mod in sorted(module_to_polys.keys()):
        polys = module_to_polys[mod]
        n_polys = len(polys)
        n_seqs = module_to_seqcount[mod]

        # Compute the signature class distribution within this module
        fids = module_formulas.get(mod, [])
        sig_classes = Counter()
        for fid in fids:
            sig = formula_sigs.get(fid, frozenset())
            cls = signature_to_class(sig)
            sig_classes[cls] += 1

        is_homo = n_polys == 1
        if is_homo:
            homo += 1
        else:
            hetero += 1

        module_analyses.append({
            "module": mod,
            "n_char_polys": n_polys,
            "char_polys": sorted(polys),
            "is_algebraically_homogeneous": is_homo,
            "total_connected_sequences": n_seqs,
            "n_formulas": len(fids),
            "signature_class_distribution": dict(sig_classes.most_common(5)),
        })

    module_analyses.sort(key=lambda x: -x["n_char_polys"])

    total = homo + hetero
    print(f"  {total} modules have OEIS-connected algebraic families")
    print(f"  Algebraically homogeneous: {homo}/{total} ({100*homo/max(total,1):.1f}%)")
    print(f"  Algebraically heterogeneous: {hetero}/{total} ({100*hetero/max(total,1):.1f}%)")

    # Show top heterogeneous modules
    for ma in module_analyses[:5]:
        if not ma["is_algebraically_homogeneous"]:
            print(f"    {ma['module']}: {ma['n_char_polys']} char polys, "
                  f"{ma['n_formulas']} formulas")

    return module_analyses, {
        "total_modules_with_oeis": total,
        "algebraically_homogeneous": homo,
        "algebraically_heterogeneous": hetero,
        "homogeneity_rate": round(homo / max(total, 1), 4),
    }


def classify_hierarchy(fwd_stats, rev_stats):
    """Determine the hierarchy relationship."""
    print("\n[5] Classifying hierarchy...")

    fam_total = fwd_stats["n_families"]
    fam_mod_homo = fwd_stats["module_homogeneous"]
    fam_class_homo = fwd_stats["module_class_homogeneous"]

    skel_total = rev_stats["total_modules_with_oeis"]
    skel_homo = rev_stats["algebraically_homogeneous"]

    # The meaningful homogeneity is module-class level
    # (do all modules in a family have the same dominant operadic class?)
    fwd_rate = fam_class_homo / max(fam_total, 1)
    rev_rate = skel_homo / max(skel_total, 1)

    if fwd_rate > 0.7 and rev_rate < 0.3:
        hierarchy = "skeleton_coarser"
        explanation = ("Algebraic families nest within operadic classes. "
                       "The skeleton is coarser -- recurrence detects finer structure.")
    elif rev_rate > 0.7 and fwd_rate < 0.3:
        hierarchy = "recurrence_coarser"
        explanation = ("Operadic classes nest within algebraic families. "
                       "Recurrence is coarser -- syntax detects finer structure.")
    elif fwd_rate < 0.3 and rev_rate < 0.3:
        hierarchy = "orthogonal"
        explanation = ("Neither partition nests inside the other. "
                       "Recurrence algebra and formula syntax detect genuinely "
                       "different mathematical structure -- they are complementary "
                       "classification axes.")
    elif fwd_rate > 0.5 and rev_rate > 0.5:
        hierarchy = "aligned"
        explanation = ("Both partitions show mutual nesting. They detect "
                       "the same structure through different lenses.")
    else:
        hierarchy = "partial_nesting"
        explanation = (f"Partial nesting: algebraic->operadic class homogeneity "
                       f"= {fwd_rate:.1%}, operadic->algebraic homogeneity "
                       f"= {rev_rate:.1%}.")

    print(f"  Algebraic -> Operadic class homogeneity: {fwd_rate:.1%}")
    print(f"  Operadic -> Algebraic homogeneity: {rev_rate:.1%}")
    print(f"  Hierarchy: {hierarchy}")
    print(f"  {explanation}")

    return {
        "hierarchy": hierarchy,
        "algebraic_to_operadic_homogeneity": round(fwd_rate, 4),
        "operadic_to_algebraic_homogeneity": round(rev_rate, 4),
        "explanation": explanation,
    }


def analyze_cross_boundary(family_analyses):
    """
    For families spanning multiple operadic classes:
    what makes them different? Same recurrence, different formula syntax.
    """
    print("\n[6] Analyzing cross-boundary families...")

    cross = [f for f in family_analyses if f["n_distinct_module_classes"] > 1]
    print(f"  {len(cross)} families span multiple operadic classes")

    cases = []
    for fam in cross:
        # Group modules by their dominant class
        class_groups = defaultdict(list)
        for mod, cls in fam["module_dominant_classes"].items():
            class_groups[cls].append(mod)

        # Classify the type of crossing
        classical_mods = {"fibonacci", "golden_ratio", "chebyshev", "sine",
                          "exp", "log", "sinc", "sqrt"}
        analytic_mods = {"riemann_zeta", "dedekind_eta", "dirichlet",
                         "hurwitz_zeta", "bernoulli_numbers", "gamma",
                         "eisenstein", "jacobi_theta", "modular_j"}
        combinatorial_mods = {"factorial", "factorials", "partitions",
                              "stirling_numbers", "bell_numbers",
                              "integer_sequences", "prime_numbers", "totient"}

        mod_set = set(fam["modules"])
        domains_present = []
        if mod_set & classical_mods:
            domains_present.append("classical_analysis")
        if mod_set & analytic_mods:
            domains_present.append("analytic_number_theory")
        if mod_set & combinatorial_mods:
            domains_present.append("combinatorics")
        other = mod_set - classical_mods - analytic_mods - combinatorial_mods
        if other:
            domains_present.append("other")

        interpretation = _interpret(fam, domains_present)

        cases.append({
            "char_poly": fam["char_poly"],
            "degree": fam["degree"],
            "n_sequences": fam["n_sequences"],
            "n_modules": fam["n_modules"],
            "n_operadic_classes": fam["n_distinct_module_classes"],
            "class_groups": {k: sorted(v) for k, v in class_groups.items()},
            "domains_present": domains_present,
            "dominant_class": fam["dominant_class"],
            "dominant_fraction": fam["dominant_fraction"],
            "interpretation": interpretation,
        })

    cases.sort(key=lambda x: -x["n_sequences"])
    return cases


def _interpret(fam, domains):
    """Generate interpretation for cross-boundary family."""
    n = len(domains)
    poly = fam["char_poly"]

    if n >= 3:
        return (f"Triple-domain crossing: the recurrence {poly} generates "
                f"sequences appearing in {', '.join(domains)}. "
                f"The algebra is more fundamental than any single domain -- "
                f"different mathematical communities have independently "
                f"discovered sequences obeying this recurrence.")
    elif n == 2:
        return (f"Dual-domain bridge: {poly} connects {domains[0]} "
                f"and {domains[1]}. Same algebraic skeleton, different "
                f"mathematical interpretations.")
    else:
        return (f"The family {poly} spans multiple operadic classes "
                f"within {domains[0] if domains else 'unknown domain'}.")


def main():
    t0 = time.time()

    poly_clusters, all_cluster_results, c12, fungrim = load_data()

    formula_sigs, formula_modules, module_formulas, module_op_profiles = \
        build_formula_signatures(fungrim)

    family_analyses, fwd_stats = \
        analyze_algebraic_families(all_cluster_results, formula_sigs,
                                    formula_modules, module_formulas)

    module_analyses, rev_stats = \
        reverse_test(all_cluster_results, formula_sigs, module_formulas)

    hierarchy = classify_hierarchy(fwd_stats, rev_stats)

    cross_boundary = analyze_cross_boundary(family_analyses)

    elapsed = time.time() - t0

    # Compute signature class universe
    all_classes = set()
    for fid, sig in formula_sigs.items():
        all_classes.add(signature_to_class(sig))

    results = {
        "challenge": "C08_8",
        "title": "Algebraic Family Clusters vs Operadic Skeleton Partition",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "summary": {
            "forward_direction": fwd_stats,
            "reverse_direction": rev_stats,
            "n_distinct_operadic_classes": len(all_classes),
            "operadic_classes": sorted(all_classes),
        },
        "hierarchy": hierarchy,
        "family_analyses": family_analyses,
        "module_analyses": module_analyses,
        "cross_boundary_families": cross_boundary,
        "elapsed_seconds": round(elapsed, 2),
    }

    with open(str(OUT_FILE), "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_FILE}")
    print(f"Elapsed: {elapsed:.1f}s")

    # Final summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\n{len(all_classes)} distinct operadic classes across {len(formula_sigs)} formulas")

    print(f"\nDirection 1 (Algebraic -> Operadic):")
    print(f"  {fwd_stats['n_families']} families with Fungrim connections")
    print(f"  Module homogeneity: {fwd_stats['module_homogeneous']}/{fwd_stats['n_families']} "
          f"({100*fwd_stats['module_homogeneous']/max(fwd_stats['n_families'],1):.1f}%)")
    print(f"  Module-class homogeneity: {fwd_stats['module_class_homogeneous']}/{fwd_stats['n_families']} "
          f"({100*fwd_stats['module_class_homogeneous']/max(fwd_stats['n_families'],1):.1f}%)")
    print(f"  Avg dominant class fraction: {fwd_stats['avg_dominant_fraction']:.3f}")

    print(f"\nDirection 2 (Operadic -> Algebraic):")
    print(f"  {rev_stats['total_modules_with_oeis']} modules with algebraic data")
    print(f"  Algebraically homogeneous: {rev_stats['algebraically_homogeneous']}/{rev_stats['total_modules_with_oeis']} "
          f"({rev_stats['homogeneity_rate']:.1%})")

    print(f"\nHierarchy: {hierarchy['hierarchy']}")
    print(f"  {hierarchy['explanation']}")

    print(f"\nCross-boundary families: {len(cross_boundary)}")
    for cb in cross_boundary[:5]:
        print(f"  {cb['char_poly']} (n={cb['n_sequences']}, "
              f"{cb['n_operadic_classes']} classes, {cb['n_modules']} modules)")
        print(f"    Domains: {', '.join(cb['domains_present'])}")

    return results


if __name__ == "__main__":
    main()

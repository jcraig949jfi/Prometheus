"""
Unified Signature Profile — Merge all extractor outputs into one profile per formula.
======================================================================================
Every formula gets a single record with signatures from all available extractors.
This is the zip file fully decompressed. The profile enables multi-lens comparison:
when two formulas from different domains match across 5+ independent lenses,
that's a structural bridge the scalar battery could never see.

Usage:
    python unified_profile.py                    # build profiles
    python unified_profile.py --match            # build + cross-domain match
    python unified_profile.py --battery          # build + match + battery test
"""

import argparse
import hashlib
import json
import sys
import time
import numpy as np
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
DATA = ROOT / "cartography" / "convergence" / "data"

# All signature files and what they provide
SIGNATURE_SOURCES = {
    # Tree-based (hash key)
    "operadic": ("operadic_signatures.jsonl", "hash",
                 ["skeleton_hash", "skeleton_str", "n_operators", "depth"]),
    "symmetry": ("symmetry_signatures.jsonl", "hash",
                 ["commutativity", "var_symmetry_order", "parity", "balance", "self_similarity", "symmetry_class"]),
    "convexity": ("convexity_signatures.jsonl", "hash",
                  ["curvature_vector", "dominant", "entropy", "nonlinearity_ratio", "curvature_class"]),
    "coeff_field": ("coefficient_field_signatures.jsonl", "hash",
                    ["field_type", "n_coefficients", "max_coefficient"]),
    "functional_eq": ("functional_equation_signatures.jsonl", "hash",
                      ["has_reflection", "has_shift", "has_scaling", "has_multiplicative", "functional_eq_type"]),
    "categorical": ("categorical_equivalence_signatures.jsonl", "hash",
                    ["primary_category", "n_categories", "category_pair_hash"]),
    "tropical": ("tropical_signatures.jsonl", "hash",
                 ["n_edges", "n_vertices", "tropical_genus", "max_slope"]),
    "newton": ("newton_polytopes.jsonl", "hash",
               ["dimension", "degree", "n_monomials", "n_vertices", "volume", "vertex_hash"]),
    "discriminant": ("discriminant_signatures.jsonl", "hash",
                     ["degree", "discriminant", "disc_sign", "n_sign_changes", "coeff_hash"]),
    "ade": ("ade_singularity_signatures.jsonl", "hash",
            ["n_singular_points", "ade_type", "milnor_number", "corank"]),
    "monodromy": ("monodromy_signatures.jsonl", "hash",
                  ["n_singularities", "n_poles", "n_branch_points", "max_pole_order"]),

    # Eval-based (hash key)
    "complex_plane": ("complex_plane_signatures.jsonl", "hash",
                      ["n_poles", "n_zeros", "phase_winding", "max_modulus_log",
                       "has_conjugate_symmetry", "has_negation_symmetry"]),
    "fractional_deriv": ("fractional_derivative_signatures.jsonl", "hash",
                         ["signature"]),
    "mod_p": ("mod_p_signatures.jsonl", "hash",
              ["signature", "degree"]),
    "padic": ("padic_signatures.jsonl", "hash",
              ["newton_polygons"]),
    "galois": ("galois_group_signatures.jsonl", "hash",
               ["degree", "galois_group", "galois_order", "is_solvable"]),
    "automorphic": ("automorphic_signatures.jsonl", "hash",
                    ["a_p_vector", "sato_tate_type", "euler_product_at_2"]),
    "zeta": ("zeta_function_signatures.jsonl", "hash",
             ["N_p_vector", "a_p_vector"]),
    "morse": ("morse_level_set_signatures.jsonl", "hash",
              ["max_components", "betti_curve_entropy", "n_critical_values"]),
    "spectral_curve": ("spectral_curve_signatures.jsonl", "hash",
                       ["n_real_roots", "n_complex_roots", "spectral_radius", "root_spread"]),

    # OEIS-based (id key)
    "spectral": ("spectral_signatures.jsonl", "id",
                 ["signature"]),
    "phase_space": ("phase_space_signatures.jsonl", "id",
                    ["autocorr_1", "autocorr_2", "lyapunov", "orbit_type", "period"]),
    "info_theoretic": ("info_theoretic_signatures.jsonl", "id",
                       ["entropy", "compression_ratio", "lz_complexity"]),
    "renormalization": ("renormalization_signatures.jsonl", "id",
                        ["mean_change_rate", "var_change_rate", "is_scale_invariant"]),
    "arithmetic_dynamics": ("arithmetic_dynamics_signatures.jsonl", "id",
                            ["lyapunov", "orbit_type", "period", "n_returns"]),
    "resurgence": ("resurgence_signatures.jsonl", "id",
                   ["radius_of_convergence", "gevrey_order", "is_borel_summable", "classification"]),
    "recursion_op": ("recursion_operator_signatures.jsonl", "id",
                     ["is_linear_recurrence", "recurrence_degree", "dominant_root_modulus"]),
}


def load_all_signatures():
    """Load all available signature files into a unified dict of id -> {extractor: data}."""
    profiles = defaultdict(dict)
    loaded = {}

    for name, (filename, id_field, fields) in SIGNATURE_SOURCES.items():
        filepath = DATA / filename
        if not filepath.exists():
            continue

        n = 0
        with open(filepath) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    fid = rec.get(id_field, rec.get("hash", rec.get("seq_id", "")))
                    if not fid:
                        continue
                    # Extract relevant fields
                    sig = {}
                    for field in fields:
                        if field in rec:
                            sig[field] = rec[field]
                    if sig:
                        profiles[fid][name] = sig
                        n += 1
                except Exception:
                    pass

        if n > 0:
            loaded[name] = n
            print(f"  {name:20s}: {n:>6,} records")

    return profiles, loaded


def compute_similarity(profile_a, profile_b):
    """Compute multi-lens similarity between two profiles.

    Returns (n_matching_lenses, total_lenses_compared, lens_details).
    """
    shared_extractors = set(profile_a.keys()) & set(profile_b.keys())
    if not shared_extractors:
        return 0, 0, {}

    n_match = 0
    n_compared = 0
    details = {}

    for ext in shared_extractors:
        sa, sb = profile_a[ext], profile_b[ext]

        # Exact match extractors (discrete signatures)
        # EXCLUDE trivial/default values (Kill #12 prevention)
        TRIVIAL_VALUES = {None, "none", "None", "Z", "unknown", "unclassified",
                          "neither", "linear", 0, 1, ""}
        if ext in ("operadic", "symmetry", "categorical", "coeff_field", "galois"):
            n_compared += 1
            for field in ("skeleton_hash", "symmetry_class", "category_pair_hash",
                          "field_type", "galois_group"):
                if field in sa and field in sb:
                    val = sa[field]
                    if val == sb[field] and val not in TRIVIAL_VALUES:
                        n_match += 1
                        details[ext] = f"exact:{field}={val}"
                    break

        # Numerical similarity extractors
        elif ext in ("convexity",):
            n_compared += 1
            va = sa.get("curvature_vector", [])
            vb = sb.get("curvature_vector", [])
            if va and vb and len(va) == len(vb):
                dist = np.linalg.norm(np.array(va, dtype=float) - np.array(vb, dtype=float))
                if dist < 3.0:  # threshold
                    n_match += 1
                    details[ext] = f"euclid={dist:.2f}"

        elif ext in ("complex_plane",):
            n_compared += 1
            # Compare pole/zero counts and symmetry
            if (sa.get("n_poles") == sb.get("n_poles") and
                sa.get("n_zeros") == sb.get("n_zeros") and
                sa.get("has_conjugate_symmetry") == sb.get("has_conjugate_symmetry")):
                n_match += 1
                details[ext] = f"poles={sa.get('n_poles')},zeros={sa.get('n_zeros')}"

        elif ext in ("functional_eq",):
            n_compared += 1
            fe_type = sa.get("functional_eq_type")
            if (fe_type == sb.get("functional_eq_type") and
                fe_type and fe_type not in ("none", "None", None, "")):
                n_match += 1
                details[ext] = f"type={fe_type}"

        elif ext in ("phase_space", "arithmetic_dynamics"):
            n_compared += 1
            if sa.get("orbit_type") == sb.get("orbit_type") and sa.get("orbit_type"):
                n_match += 1
                details[ext] = f"orbit={sa['orbit_type']}"

        elif ext in ("resurgence",):
            n_compared += 1
            if sa.get("classification") == sb.get("classification") and sa.get("classification"):
                n_match += 1
                details[ext] = f"class={sa['classification']}"

        elif ext in ("mod_p",):
            n_compared += 1
            if sa.get("signature") == sb.get("signature") and sa.get("signature"):
                n_match += 1
                details[ext] = "exact_fingerprint"

        elif ext in ("discriminant",):
            n_compared += 1
            da, db = sa.get("discriminant"), sb.get("discriminant")
            if da is not None and db is not None and da != 0 and db != 0:
                if da == db:
                    n_match += 1
                    details[ext] = f"disc={da}"

        elif ext == "tropical":
            n_compared += 1
            if (sa.get("tropical_genus") == sb.get("tropical_genus") and
                sa.get("n_vertices") == sb.get("n_vertices") and
                sa.get("tropical_genus") is not None):
                n_match += 1
                details[ext] = f"genus={sa['tropical_genus']},verts={sa['n_vertices']}"

    return n_match, n_compared, details


def find_bridges(profiles, domain_map, min_lenses=3):
    """Find cross-domain formula pairs that match across multiple lenses."""
    # Group by domain
    by_domain = defaultdict(list)
    for fid, profile in profiles.items():
        domain = domain_map.get(fid, "unknown")
        if len(profile) >= 2:  # need at least 2 lenses to compare
            by_domain[domain].append(fid)

    domains = sorted(by_domain.keys())
    bridges = []

    print(f"\n  Comparing across {len(domains)} domains...")
    n_pairs_tested = 0

    for i, d1 in enumerate(domains):
        for d2 in domains[i+1:]:
            if d1 == d2 or d1 == "unknown" or d2 == "unknown":
                continue
            ids1 = by_domain[d1][:200]  # cap per domain to avoid combinatorial explosion
            ids2 = by_domain[d2][:200]

            for fid1 in ids1:
                for fid2 in ids2:
                    n_pairs_tested += 1
                    n_match, n_compared, details = compute_similarity(
                        profiles[fid1], profiles[fid2])

                    if n_match >= min_lenses:
                        bridges.append({
                            "id_a": fid1, "domain_a": d1,
                            "id_b": fid2, "domain_b": d2,
                            "n_matching_lenses": n_match,
                            "n_compared": n_compared,
                            "match_ratio": round(n_match / max(n_compared, 1), 3),
                            "details": details,
                        })

    bridges.sort(key=lambda x: -x["n_matching_lenses"])
    return bridges, n_pairs_tested


def main():
    parser = argparse.ArgumentParser(description="Unified Signature Profile")
    parser.add_argument("--match", action="store_true", help="Run cross-domain matching")
    parser.add_argument("--battery", action="store_true", help="Battery test bridges")
    parser.add_argument("--min-lenses", type=int, default=3, help="Min matching lenses for bridge (default: 3)")
    args = parser.parse_args()

    print("=" * 70)
    print("  UNIFIED SIGNATURE PROFILE")
    print("=" * 70)

    t0 = time.time()

    # Load all signatures
    print("\n  Loading signatures from all extractors...")
    profiles, loaded = load_all_signatures()
    print(f"\n  {len(profiles):,} unique objects with signatures")
    print(f"  {len(loaded)} extractors loaded")

    # Lens coverage stats
    lens_counts = defaultdict(int)
    for fid, profile in profiles.items():
        lens_counts[len(profile)] += 1

    print(f"\n  Lens coverage distribution:")
    for n_lenses in sorted(lens_counts.keys()):
        print(f"    {n_lenses:>2} lenses: {lens_counts[n_lenses]:>6,} objects")

    # Save profiles
    profile_file = DATA / "unified_profiles.jsonl"
    with open(profile_file, "w") as f:
        for fid, profile in profiles.items():
            f.write(json.dumps({"id": fid, "n_lenses": len(profile),
                                "extractors": sorted(profile.keys()),
                                **{f"sig_{k}": v for k, v in profile.items()}},
                               default=str) + "\n")
    print(f"\n  Saved {len(profiles):,} profiles to {profile_file.name}")

    if args.match or args.battery:
        # Load domain map
        domain_map = {}
        formulas_file = DATA / "openwebmath_formulas.jsonl"
        if formulas_file.exists():
            print("\n  Loading domain map...")
            with open(formulas_file) as f:
                for line in f:
                    try:
                        d = json.loads(line)
                        domains = d.get("domains", [])
                        domain_map[d["hash"]] = domains[0] if domains else "unknown"
                    except Exception:
                        pass
            print(f"    {len(domain_map):,} domain mappings")

        print(f"\n  Finding cross-domain bridges (min {args.min_lenses} lenses)...")
        bridges, n_tested = find_bridges(profiles, domain_map, min_lenses=args.min_lenses)

        print(f"\n  Pairs tested: {n_tested:,}")
        print(f"  Bridges found: {len(bridges)}")

        if bridges:
            bridge_file = DATA / "unified_bridges.jsonl"
            with open(bridge_file, "w") as f:
                for b in bridges:
                    f.write(json.dumps(b, default=str) + "\n")

            print(f"\n  === TOP BRIDGES ===")
            for b in bridges[:20]:
                print(f"    {b['id_a'][:12]} ({b['domain_a']}) <-> {b['id_b'][:12]} ({b['domain_b']})")
                print(f"      {b['n_matching_lenses']}/{b['n_compared']} lenses match: {b['details']}")
        else:
            print(f"\n  No bridges found at {args.min_lenses}+ lenses.")
            # Try lower threshold
            for threshold in [2, 1]:
                bridges_lower, _ = find_bridges(profiles, domain_map, min_lenses=threshold)
                if bridges_lower:
                    print(f"  At {threshold}+ lenses: {len(bridges_lower)} bridges")
                    for b in bridges_lower[:5]:
                        print(f"    {b['id_a'][:12]} ({b['domain_a']}) <-> {b['id_b'][:12]} ({b['domain_b']}) "
                              f"[{b['n_matching_lenses']}/{b['n_compared']}] {b['details']}")
                    break

        if args.battery and bridges:
            print(f"\n  Running battery on {len(bridges)} bridges...")
            from falsification_battery import run_battery
            for b in bridges[:10]:
                print(f"    {b['id_a'][:12]} <-> {b['id_b'][:12]}: ", end="")
                # For signature-based bridges, we note the structural match
                print(f"STRUCTURAL MATCH ({b['n_matching_lenses']} lenses) — needs object-level data for battery")

    elapsed = time.time() - t0
    print(f"\n  Total time: {elapsed:.1f}s")
    print("=" * 70)


if __name__ == "__main__":
    main()

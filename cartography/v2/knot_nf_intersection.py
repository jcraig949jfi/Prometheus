#!/usr/bin/env python3
"""
Arithmetic Intersection of Knot Invariants and Number Fields

For knots with Alexander polynomials, evaluate Delta_K(e^{2pi*i/n}) for n=3,4,5,6.
Compute |Delta_K(zeta_n)|^2 (always a non-negative integer for Alexander polys at roots of unity).
For number fields, extract discriminants.
Measure cross-domain collision density: how often does |Delta_K(zeta_n)|^2 equal a
number field discriminant? Compare to random baseline with integers in the same range.
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

KNOTS_FILE = Path(__file__).parent.parent / "knots" / "data" / "knots.json"
NF_FILE = Path(__file__).parent.parent / "number_fields" / "data" / "number_fields.json"
OUT_FILE = Path(__file__).parent / "knot_nf_intersection_results.json"

ROOTS_N = [3, 4, 5, 6]
N_RANDOM_TRIALS = 1000


def load_knots():
    """Load knots with Alexander polynomials."""
    with open(KNOTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    knots = []
    for k in data["knots"]:
        if k.get("alexander") and k["alexander"].get("coefficients"):
            knots.append(k)
    return knots


def load_number_fields():
    """Load number fields, extract discriminants and regulators."""
    with open(NF_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    fields = []
    for nf in data:
        disc = int(nf["disc_abs"])
        reg = float(nf.get("regulator", 0))
        fields.append({
            "label": nf["label"],
            "degree": nf["degree"],
            "disc_abs": disc,
            "disc_sign": nf["disc_sign"],
            "regulator": reg,
        })
    return fields


def eval_alexander_at_root(coeffs, min_power, zeta):
    """
    Evaluate Alexander polynomial at zeta.
    The polynomial is sum_{i} coeffs[i] * t^(min_power + i).
    Alexander polynomials use the convention Delta(t) with Laurent coefficients.
    """
    result = 0.0 + 0.0j
    for i, c in enumerate(coeffs):
        power = min_power + i
        result += c * (zeta ** power)
    return result


def compute_knot_invariants(knots):
    """
    For each knot and each n in ROOTS_N, compute |Delta_K(zeta_n)|^2
    rounded to nearest integer.
    Returns dict: n -> list of (knot_name, value).
    """
    results = defaultdict(list)
    zetas = {}
    for n in ROOTS_N:
        zetas[n] = np.exp(2j * np.pi / n)

    for knot in knots:
        alex = knot["alexander"]
        coeffs = alex["coefficients"]
        min_power = alex["min_power"]
        name = knot["name"]

        for n in ROOTS_N:
            val = eval_alexander_at_root(coeffs, min_power, zetas[n])
            abs_sq = abs(val) ** 2
            # Should be close to integer for Alexander polys at roots of unity
            int_val = int(round(abs_sq))
            if int_val > 0:  # skip trivial zeros
                results[n].append((name, int_val))

    return results


def compute_collisions(knot_vals_by_n, disc_set, disc_range):
    """
    Compute collision density: fraction of knot |Delta(zeta_n)|^2 values
    that land in the discriminant set. Compare to random baseline.
    """
    rng = np.random.default_rng(42)
    collision_stats = {}

    for n in ROOTS_N:
        vals = knot_vals_by_n[n]
        if not vals:
            continue

        int_vals = [v for _, v in vals]
        unique_vals = set(int_vals)

        # Observed collisions
        collisions = unique_vals & disc_set
        n_collisions = len(collisions)
        collision_density = n_collisions / len(unique_vals) if unique_vals else 0

        # Which knot values hit discriminants (count multiplicity)
        hit_count = sum(1 for v in int_vals if v in disc_set)
        hit_fraction = hit_count / len(int_vals) if int_vals else 0

        # Random baseline: draw same number of unique integers from same range
        val_min = min(int_vals)
        val_max = max(int_vals)
        n_unique = len(unique_vals)

        random_collision_densities = []
        random_hit_fractions = []
        for _ in range(N_RANDOM_TRIALS):
            rand_vals = set(rng.integers(val_min, val_max + 1, size=n_unique))
            rand_collisions = rand_vals & disc_set
            random_collision_densities.append(len(rand_collisions) / len(rand_vals))

            # Also simulate hit fraction with multiplicity
            rand_draw = rng.integers(val_min, val_max + 1, size=len(int_vals))
            rand_hits = sum(1 for v in rand_draw if v in disc_set)
            random_hit_fractions.append(rand_hits / len(rand_draw))

        mean_random_density = float(np.mean(random_collision_densities))
        std_random_density = float(np.std(random_collision_densities))
        mean_random_hit = float(np.mean(random_hit_fractions))
        std_random_hit = float(np.std(random_hit_fractions))

        z_density = ((collision_density - mean_random_density) / std_random_density
                     if std_random_density > 0 else 0.0)
        z_hit = ((hit_fraction - mean_random_hit) / std_random_hit
                 if std_random_hit > 0 else 0.0)

        # Enrichment ratio
        enrichment_density = (collision_density / mean_random_density
                              if mean_random_density > 0 else float("inf"))
        enrichment_hit = (hit_fraction / mean_random_hit
                          if mean_random_hit > 0 else float("inf"))

        collision_stats[str(n)] = {
            "n_knots_evaluated": len(int_vals),
            "n_unique_values": n_unique,
            "value_range": [int(val_min), int(val_max)],
            "n_collisions_unique": n_collisions,
            "collision_density_unique": round(collision_density, 6),
            "hit_fraction_with_multiplicity": round(hit_fraction, 6),
            "random_baseline_density_mean": round(mean_random_density, 6),
            "random_baseline_density_std": round(std_random_density, 6),
            "random_baseline_hit_mean": round(mean_random_hit, 6),
            "random_baseline_hit_std": round(std_random_hit, 6),
            "z_score_density": round(z_density, 3),
            "z_score_hit": round(z_hit, 3),
            "enrichment_density": round(enrichment_density, 3),
            "enrichment_hit": round(enrichment_hit, 3),
            "collision_examples": sorted(list(collisions))[:20],
        }

    return collision_stats


def analyze_collision_structure(knot_vals_by_n, disc_counter):
    """
    Deeper analysis: do collisions prefer particular discriminant multiplicities?
    Which knot families contribute most collisions?
    """
    structure = {}

    for n in ROOTS_N:
        vals = knot_vals_by_n[n]
        if not vals:
            continue

        disc_set = set(disc_counter.keys())
        hitting_knots = [(name, v) for name, v in vals if v in disc_set]

        # Value distribution of hits
        hit_vals = Counter(v for _, v in hitting_knots)

        # Discriminant multiplicity of hit values
        hit_disc_mults = {v: disc_counter[v] for v in hit_vals if v in disc_counter}

        # Average discriminant multiplicity for hits vs all discriminants
        if hit_disc_mults:
            avg_hit_mult = np.mean(list(hit_disc_mults.values()))
            avg_all_mult = np.mean(list(disc_counter.values()))
        else:
            avg_hit_mult = 0
            avg_all_mult = np.mean(list(disc_counter.values()))

        structure[str(n)] = {
            "n_hitting_knot_evaluations": len(hitting_knots),
            "n_unique_hit_values": len(hit_vals),
            "top_hit_values": dict(hit_vals.most_common(10)),
            "avg_disc_multiplicity_at_hits": round(float(avg_hit_mult), 3),
            "avg_disc_multiplicity_overall": round(float(avg_all_mult), 3),
        }

    return structure


def analyze_by_degree(knot_vals_by_n, fields):
    """Check if collisions prefer number fields of particular degree."""
    degree_discs = defaultdict(set)
    for nf in fields:
        degree_discs[nf["degree"]].add(nf["disc_abs"])

    by_degree = {}
    for n in ROOTS_N:
        vals = knot_vals_by_n[n]
        if not vals:
            continue
        int_vals = set(v for _, v in vals)
        degree_hits = {}
        for deg, dset in sorted(degree_discs.items()):
            hits = int_vals & dset
            degree_hits[str(deg)] = {
                "n_discs_in_degree": len(dset),
                "n_collisions": len(hits),
                "collision_rate": round(len(hits) / len(dset), 4) if dset else 0,
            }
        by_degree[str(n)] = degree_hits

    return by_degree


def main():
    print("Loading knots...")
    knots = load_knots()
    print(f"  {len(knots)} knots with Alexander polynomials")

    print("Loading number fields...")
    fields = load_number_fields()
    print(f"  {len(fields)} number fields")

    # Build discriminant set and counter
    disc_counter = Counter(nf["disc_abs"] for nf in fields)
    disc_set = set(disc_counter.keys())
    print(f"  {len(disc_set)} unique discriminants, range [{min(disc_set)}, {max(disc_set)}]")

    print("Computing Alexander polynomial evaluations at roots of unity...")
    knot_vals_by_n = compute_knot_invariants(knots)
    for n in ROOTS_N:
        vals = knot_vals_by_n[n]
        unique = set(v for _, v in vals)
        print(f"  zeta_{n}: {len(vals)} evaluations, {len(unique)} unique values, "
              f"range [{min(v for _, v in vals)}, {max(v for _, v in vals)}]")

    print("Computing collision densities...")
    collision_stats = compute_collisions(knot_vals_by_n, disc_set, None)
    for n_str, stats in collision_stats.items():
        z = stats["z_score_density"]
        enrich = stats["enrichment_density"]
        print(f"  zeta_{n_str}: {stats['n_collisions_unique']} collisions, "
              f"density={stats['collision_density_unique']:.4f}, "
              f"enrichment={enrich:.2f}x, z={z:.2f}")

    print("Analyzing collision structure...")
    structure = analyze_collision_structure(knot_vals_by_n, disc_counter)

    print("Analyzing by number field degree...")
    by_degree = analyze_by_degree(knot_vals_by_n, fields)

    # Aggregate: overall collision metric mu_{K/F}
    all_z_scores = [collision_stats[str(n)]["z_score_density"] for n in ROOTS_N
                    if str(n) in collision_stats]
    all_enrichments = [collision_stats[str(n)]["enrichment_density"] for n in ROOTS_N
                       if str(n) in collision_stats]
    mu_kf = float(np.mean(all_enrichments)) if all_enrichments else 0.0

    # Verdict
    max_z = max(abs(z) for z in all_z_scores) if all_z_scores else 0
    if max_z > 3:
        verdict = "SIGNIFICANT: collision density deviates strongly from random"
    elif max_z > 2:
        verdict = "MARGINAL: weak evidence of non-random collision"
    else:
        verdict = "NULL: collision density consistent with random integers in same range"

    results = {
        "experiment": "Arithmetic Intersection of Knot Invariants and Number Fields",
        "description": (
            "Evaluate Alexander polynomials at roots of unity zeta_n (n=3,4,5,6), "
            "compute |Delta_K(zeta_n)|^2, test collision with number field discriminants"
        ),
        "n_knots_with_alexander": len(knots),
        "n_number_fields": len(fields),
        "n_unique_discriminants": len(disc_set),
        "roots_of_unity_tested": ROOTS_N,
        "collision_stats": collision_stats,
        "collision_structure": structure,
        "collisions_by_nf_degree": by_degree,
        "mu_KF_mean_enrichment": round(mu_kf, 4),
        "max_abs_z_score": round(max_z, 3),
        "verdict": verdict,
    }

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults written to {OUT_FILE}")
    print(f"mu_{{K/F}} = {mu_kf:.4f} (mean enrichment over random)")
    print(f"Max |z| = {max_z:.3f}")
    print(f"Verdict: {verdict}")


if __name__ == "__main__":
    main()

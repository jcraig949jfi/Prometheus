"""
Knot Determinant vs Lattice Determinant Resonance (ChatGPT #13)
================================================================
Measure overlap enrichment of shared determinant values between knots
and lattices using second-order mod-p structure.

Data:
  - Knots: cartography/knots/data/knots.json (12,965 knots with determinants)
  - Lattices: cartography/lmfdb_dump/lat_lattices.json (39,293 lattices with det)
"""

import json
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path
import os

REPO = Path(__file__).resolve().parent.parent.parent
KNOT_PATH = REPO / "cartography" / "knots" / "data" / "knots.json"
LATTICE_PATH = REPO / "cartography" / "lmfdb_dump" / "lat_lattices.json"
OUT_PATH = REPO / "cartography" / "v2" / "knot_lattice_det_resonance_results.json"

N_PERM = 2000
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23]
rng = np.random.default_rng(42)


def load_data():
    with open(KNOT_PATH) as f:
        kdata = json.load(f)
    knots = kdata["knots"]
    knot_dets = np.array([k["determinant"] for k in knots if k.get("determinant") is not None])
    knot_crossing = np.array([k.get("crossing_number", 0) for k in knots if k.get("determinant") is not None])
    # jones span as another invariant
    knot_span = []
    for k in knots:
        if k.get("determinant") is None:
            continue
        j = k.get("jones", {})
        if j and j.get("min_power") is not None and j.get("max_power") is not None:
            knot_span.append(j["max_power"] - j["min_power"])
        else:
            knot_span.append(np.nan)
    knot_span = np.array(knot_span, dtype=float)

    with open(LATTICE_PATH) as f:
        ldata = json.load(f)
    recs = ldata["records"]
    lat_dets = np.array([r["det"] for r in recs if r.get("det") is not None and r["det"] > 0])
    lat_dim = np.array([r.get("dim", 0) for r in recs if r.get("det") is not None and r["det"] > 0])
    lat_kissing = np.array([r.get("kissing", 0) for r in recs if r.get("det") is not None and r["det"] > 0], dtype=float)

    return knot_dets, knot_crossing, knot_span, lat_dets, lat_dim, lat_kissing


# ── 1. First-order: exact determinant overlap ──────────────────────────
def first_order_overlap(knot_dets, lat_dets):
    knot_set = set(knot_dets.tolist())
    lat_set = set(lat_dets.tolist())
    shared = knot_set & lat_set
    n_shared = len(shared)

    # How many knots have a det that appears in lattices?
    knots_with_match = sum(1 for d in knot_dets if d in lat_set)
    lats_with_match = sum(1 for d in lat_dets if d in knot_set)

    # Null: random integers drawn from union range
    all_vals = sorted(knot_set | lat_set)
    max_val = max(all_vals)
    null_shared = []
    for _ in range(N_PERM):
        fake_knot = set(rng.integers(1, max_val + 1, size=len(knot_set)))
        fake_lat = set(rng.integers(1, max_val + 1, size=len(lat_set)))
        null_shared.append(len(fake_knot & fake_lat))

    null_mean = float(np.mean(null_shared))
    null_std = float(np.std(null_shared))
    enrichment = n_shared / null_mean if null_mean > 0 else float("inf")
    z = (n_shared - null_mean) / null_std if null_std > 0 else 0.0

    return {
        "unique_knot_dets": len(knot_set),
        "unique_lat_dets": len(lat_set),
        "shared_values": n_shared,
        "knots_with_lattice_match": int(knots_with_match),
        "lattices_with_knot_match": int(lats_with_match),
        "null_mean_shared": round(null_mean, 2),
        "null_std_shared": round(null_std, 2),
        "enrichment": round(enrichment, 4),
        "z_score": round(z, 2),
        "sample_shared": sorted(list(shared))[:30],
    }


# ── 2. Mod-p residue overlap ──────────────────────────────────────────
def modp_overlap(knot_dets, lat_dets):
    results = {}
    for p in PRIMES:
        knot_residues = set(int(d % p) for d in knot_dets)
        lat_residues = set(int(d % p) for d in lat_dets)
        shared = knot_residues & lat_residues
        # This is trivially full for small p, so measure distribution overlap instead
        knot_counts = Counter(int(d % p) for d in knot_dets)
        lat_counts = Counter(int(d % p) for d in lat_dets)
        # Normalize to distributions
        knot_total = sum(knot_counts.values())
        lat_total = sum(lat_counts.values())
        # Bhattacharyya coefficient
        bc = 0.0
        for r in range(p):
            pk = knot_counts.get(r, 0) / knot_total
            pl = lat_counts.get(r, 0) / lat_total
            bc += np.sqrt(pk * pl)

        # Null: uniform would give BC = 1.0
        # Permutation null: shuffle labels
        null_bcs = []
        all_dets = np.concatenate([knot_dets, lat_dets])
        for _ in range(N_PERM):
            perm = rng.permutation(len(all_dets))
            fake_knot = all_dets[perm[: len(knot_dets)]]
            fake_lat = all_dets[perm[len(knot_dets):]]
            fk_counts = Counter(int(d % p) for d in fake_knot)
            fl_counts = Counter(int(d % p) for d in fake_lat)
            fk_total = sum(fk_counts.values())
            fl_total = sum(fl_counts.values())
            nbc = sum(
                np.sqrt(fk_counts.get(r, 0) / fk_total * fl_counts.get(r, 0) / fl_total)
                for r in range(p)
            )
            null_bcs.append(nbc)

        null_mean = float(np.mean(null_bcs))
        null_std = float(np.std(null_bcs))
        z = (bc - null_mean) / null_std if null_std > 0 else 0.0

        knot_dist = {str(r): round(knot_counts.get(r, 0) / knot_total, 4) for r in range(p)}
        lat_dist = {str(r): round(lat_counts.get(r, 0) / lat_total, 4) for r in range(p)}

        results[f"mod_{p}"] = {
            "bhattacharyya": round(bc, 6),
            "null_mean": round(null_mean, 6),
            "null_std": round(null_std, 6),
            "z_score": round(z, 2),
            "knot_distribution": knot_dist,
            "lattice_distribution": lat_dist,
        }
    return results


# ── 3. Second-order within-domain: mod-p class → invariant similarity ─
def second_order_within(dets, aux, label, p=5):
    """For pairs sharing det mod p, is auxiliary invariant more similar?"""
    mask = ~np.isnan(aux) if aux.dtype == float else np.ones(len(aux), dtype=bool)
    dets_m = dets[mask]
    aux_m = aux[mask]
    residues = dets_m % p

    # Mean absolute difference for same-residue pairs (sample)
    same_diffs = []
    diff_diffs = []
    n = len(dets_m)
    n_sample = min(500_000, n * (n - 1) // 2)

    for _ in range(n_sample):
        i, j = rng.integers(0, n, size=2)
        if i == j:
            continue
        d = abs(float(aux_m[i]) - float(aux_m[j]))
        if residues[i] == residues[j]:
            same_diffs.append(d)
        else:
            diff_diffs.append(d)

    if not same_diffs or not diff_diffs:
        return {"status": "insufficient_pairs"}

    same_mean = float(np.mean(same_diffs))
    diff_mean = float(np.mean(diff_diffs))
    ratio = same_mean / diff_mean if diff_mean > 0 else float("inf")

    # Null: permute residues
    null_ratios = []
    for _ in range(500):
        perm_res = rng.permutation(residues)
        s_diffs = []
        d_diffs = []
        for _ in range(10_000):
            i, j = rng.integers(0, n, size=2)
            if i == j:
                continue
            d = abs(float(aux_m[i]) - float(aux_m[j]))
            if perm_res[i] == perm_res[j]:
                s_diffs.append(d)
            else:
                d_diffs.append(d)
        if s_diffs and d_diffs:
            null_ratios.append(np.mean(s_diffs) / np.mean(d_diffs))

    null_mean = float(np.mean(null_ratios))
    null_std = float(np.std(null_ratios))
    z = (ratio - null_mean) / null_std if null_std > 0 else 0.0

    return {
        "domain": label,
        "mod_p": p,
        "same_residue_mean_diff": round(same_mean, 4),
        "diff_residue_mean_diff": round(diff_mean, 4),
        "ratio_same_over_diff": round(ratio, 6),
        "null_mean_ratio": round(null_mean, 6),
        "null_std_ratio": round(null_std, 6),
        "z_score": round(z, 2),
        "n_same_pairs": len(same_diffs),
        "n_diff_pairs": len(diff_diffs),
    }


# ── 4. Cross-domain second-order: shared mod-3 AND mod-5 → mod-7 ─────
def cross_domain_second_order(knot_dets, lat_dets):
    """Among knot-lattice pairs sharing det mod 3 AND mod 5, is mod-7 co-occurrence elevated?"""
    # Build residue signatures
    knot_mod3 = knot_dets % 3
    knot_mod5 = knot_dets % 5
    knot_mod7 = knot_dets % 7

    lat_mod3 = lat_dets % 3
    lat_mod5 = lat_dets % 5
    lat_mod7 = lat_dets % 7

    # Group knots and lattices by (mod3, mod5) class
    knot_by_class = defaultdict(list)
    for i in range(len(knot_dets)):
        knot_by_class[(int(knot_mod3[i]), int(knot_mod5[i]))].append(int(knot_mod7[i]))

    lat_by_class = defaultdict(list)
    for i in range(len(lat_dets)):
        lat_by_class[(int(lat_mod3[i]), int(lat_mod5[i]))].append(int(lat_mod7[i]))

    # For each shared (mod3, mod5) class, measure mod-7 distribution overlap
    shared_classes = set(knot_by_class.keys()) & set(lat_by_class.keys())

    # Overall mod-7 match rate: among paired samples from same (mod3,mod5) class
    same_class_mod7_match = 0
    same_class_total = 0
    n_sample_per_class = 1000

    for cls in shared_classes:
        k7 = knot_by_class[cls]
        l7 = lat_by_class[cls]
        for _ in range(min(n_sample_per_class, len(k7) * len(l7))):
            ki = rng.integers(0, len(k7))
            li = rng.integers(0, len(l7))
            same_class_total += 1
            if k7[ki] == l7[li]:
                same_class_mod7_match += 1

    observed_rate = same_class_mod7_match / same_class_total if same_class_total > 0 else 0

    # Null: expected mod-7 match rate = 1/7 for uniform
    expected_uniform = 1.0 / 7.0

    # Better null: permutation - shuffle lattice det assignments
    null_rates = []
    for _ in range(N_PERM):
        perm_lat_dets = rng.permutation(lat_dets)
        pl_mod3 = perm_lat_dets % 3
        pl_mod5 = perm_lat_dets % 5
        pl_mod7 = perm_lat_dets % 7

        pl_by_class = defaultdict(list)
        for i in range(len(perm_lat_dets)):
            pl_by_class[(int(pl_mod3[i]), int(pl_mod5[i]))].append(int(pl_mod7[i]))

        match = 0
        total = 0
        for cls in shared_classes:
            if cls not in pl_by_class:
                continue
            k7 = knot_by_class[cls]
            l7 = pl_by_class[cls]
            for _ in range(min(200, len(k7) * len(l7))):
                ki = rng.integers(0, len(k7))
                li = rng.integers(0, len(l7))
                total += 1
                if k7[ki] == l7[li]:
                    match += 1
        if total > 0:
            null_rates.append(match / total)

    null_mean = float(np.mean(null_rates))
    null_std = float(np.std(null_rates))
    enrichment = observed_rate / null_mean if null_mean > 0 else float("inf")
    z = (observed_rate - null_mean) / null_std if null_std > 0 else 0.0

    return {
        "conditioning": "det mod 3 AND det mod 5",
        "target": "det mod 7 co-occurrence",
        "n_shared_classes": len(shared_classes),
        "n_pairs_sampled": same_class_total,
        "observed_mod7_match_rate": round(observed_rate, 6),
        "expected_uniform_rate": round(expected_uniform, 6),
        "null_mean_rate": round(null_mean, 6),
        "null_std_rate": round(null_std, 6),
        "enrichment_vs_null": round(enrichment, 4),
        "z_score": round(z, 2),
    }


# ── 5. Multi-prime cross-domain enrichment scan ──────────────────────
def multi_prime_cross(knot_dets, lat_dets):
    """For each pair (p_cond, p_target), condition on shared mod-p_cond, measure mod-p_target overlap."""
    results = {}
    test_primes = [3, 5, 7, 11, 13]

    for p_cond in test_primes:
        for p_target in test_primes:
            if p_cond == p_target:
                continue

            # Group by mod-p_cond
            knot_by = defaultdict(list)
            for i, d in enumerate(knot_dets):
                knot_by[int(d % p_cond)].append(int(d % p_target))
            lat_by = defaultdict(list)
            for i, d in enumerate(lat_dets):
                lat_by[int(d % p_cond)].append(int(d % p_target))

            # Match rate for same-class pairs
            match = 0
            total = 0
            shared_classes = set(knot_by.keys()) & set(lat_by.keys())
            for cls in shared_classes:
                k_vals = knot_by[cls]
                l_vals = lat_by[cls]
                n_samp = min(500, len(k_vals) * len(l_vals))
                for _ in range(n_samp):
                    ki = rng.integers(0, len(k_vals))
                    li = rng.integers(0, len(l_vals))
                    total += 1
                    if k_vals[ki] == l_vals[li]:
                        match += 1

            obs_rate = match / total if total > 0 else 0
            expected = 1.0 / p_target

            results[f"cond_mod{p_cond}_target_mod{p_target}"] = {
                "observed_rate": round(obs_rate, 6),
                "expected_uniform": round(expected, 6),
                "enrichment": round(obs_rate / expected, 4) if expected > 0 else None,
            }

    return results


def main():
    print("Loading data...")
    knot_dets, knot_crossing, knot_span, lat_dets, lat_dim, lat_kissing = load_data()
    print(f"  Knots: {len(knot_dets)} with determinants")
    print(f"  Lattices: {len(lat_dets)} with determinants")

    results = {
        "experiment": "Knot Determinant vs Lattice Determinant Resonance",
        "challenge": "ChatGPT #13",
        "n_knots": int(len(knot_dets)),
        "n_lattices": int(len(lat_dets)),
    }

    print("\n1. First-order overlap...")
    results["first_order_overlap"] = first_order_overlap(knot_dets, lat_dets)
    print(f"   Shared values: {results['first_order_overlap']['shared_values']}")
    print(f"   Enrichment: {results['first_order_overlap']['enrichment']}x")
    print(f"   z = {results['first_order_overlap']['z_score']}")

    print("\n2. Mod-p distribution overlap (Bhattacharyya)...")
    results["modp_distribution_overlap"] = modp_overlap(knot_dets, lat_dets)
    for p in PRIMES:
        r = results["modp_distribution_overlap"][f"mod_{p}"]
        print(f"   mod {p}: BC={r['bhattacharyya']:.4f}, z={r['z_score']}")

    print("\n3. Second-order within-domain...")
    results["second_order_within"] = {}

    print("   Knots: det mod 5 -> crossing number similarity")
    results["second_order_within"]["knot_crossing_mod5"] = second_order_within(
        knot_dets, knot_crossing.astype(float), "knots_crossing", p=5
    )
    r = results["second_order_within"]["knot_crossing_mod5"]
    print(f"     ratio={r.get('ratio_same_over_diff', 'N/A')}, z={r.get('z_score', 'N/A')}")

    print("   Knots: det mod 5 -> jones span similarity")
    results["second_order_within"]["knot_span_mod5"] = second_order_within(
        knot_dets, knot_span, "knots_span", p=5
    )
    r = results["second_order_within"]["knot_span_mod5"]
    print(f"     ratio={r.get('ratio_same_over_diff', 'N/A')}, z={r.get('z_score', 'N/A')}")

    print("   Lattices: det mod 5 -> dimension similarity")
    results["second_order_within"]["lattice_dim_mod5"] = second_order_within(
        lat_dets, lat_dim.astype(float), "lattices_dim", p=5
    )
    r = results["second_order_within"]["lattice_dim_mod5"]
    print(f"     ratio={r.get('ratio_same_over_diff', 'N/A')}, z={r.get('z_score', 'N/A')}")

    print("   Lattices: det mod 5 -> kissing number similarity")
    results["second_order_within"]["lattice_kissing_mod5"] = second_order_within(
        lat_dets, lat_kissing, "lattices_kissing", p=5
    )
    r = results["second_order_within"]["lattice_kissing_mod5"]
    print(f"     ratio={r.get('ratio_same_over_diff', 'N/A')}, z={r.get('z_score', 'N/A')}")

    print("\n4. Cross-domain second-order: mod-3 & mod-5 -> mod-7...")
    results["cross_domain_second_order"] = cross_domain_second_order(knot_dets, lat_dets)
    r = results["cross_domain_second_order"]
    print(f"   Observed mod-7 match: {r['observed_mod7_match_rate']:.4f}")
    print(f"   Null mean: {r['null_mean_rate']:.4f}")
    print(f"   Enrichment: {r['enrichment_vs_null']}x, z={r['z_score']}")

    print("\n5. Multi-prime cross-domain scan...")
    results["multi_prime_scan"] = multi_prime_cross(knot_dets, lat_dets)
    # Summarize
    enrichments = []
    for key, val in results["multi_prime_scan"].items():
        e = val.get("enrichment")
        if e is not None:
            enrichments.append(e)
            if abs(e - 1.0) > 0.05:
                print(f"   {key}: enrichment={e}")
    print(f"   Mean enrichment across all prime pairs: {np.mean(enrichments):.4f}")
    print(f"   Std: {np.std(enrichments):.4f}")

    # ── Verdict ─────────────────────────────────────────────────────
    fo = results["first_order_overlap"]
    cd = results["cross_domain_second_order"]
    verdict_parts = []
    if fo["z_score"] > 3:
        verdict_parts.append(f"first-order overlap significant (z={fo['z_score']})")
    else:
        verdict_parts.append(f"first-order overlap NOT significant (z={fo['z_score']})")

    if abs(cd["z_score"]) > 3:
        verdict_parts.append(f"cross-domain mod-7 significant (z={cd['z_score']})")
    else:
        verdict_parts.append(f"cross-domain mod-7 NOT significant (z={cd['z_score']})")

    # Check within-domain
    within_sig = []
    for key, val in results["second_order_within"].items():
        if isinstance(val, dict) and abs(val.get("z_score", 0)) > 3:
            within_sig.append(key)
    if within_sig:
        verdict_parts.append(f"within-domain significant: {within_sig}")
    else:
        verdict_parts.append("within-domain: no significant second-order structure")

    results["verdict"] = "; ".join(verdict_parts)
    results["summary"] = (
        "Knot and lattice determinant overlap is tested at first order (exact value sharing), "
        "mod-p distribution level (Bhattacharyya coefficient), within-domain second order "
        "(do shared-residue pairs have more similar auxiliary invariants?), and cross-domain "
        "second order (conditioning on mod-3 and mod-5, is mod-7 co-occurrence elevated?)."
    )

    print(f"\nVERDICT: {results['verdict']}")

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {OUT_PATH}")


if __name__ == "__main__":
    main()

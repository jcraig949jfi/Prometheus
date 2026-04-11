"""
Cross-Domain: EC Hecke Fingerprint vs Lattice Invariant Fingerprint MI

Tests whether elliptic curve mod-p fingerprints (from Hecke traces a_p)
and lattice mod-p fingerprints (from numeric invariants) share mutual information.

EC fingerprint: first 10 a_p values mod p → tuple hash
Lattice fingerprint: (dimension, determinant, level, class_number, minimal_vector,
                       aut_group_order) mod p → tuple hash

Note: Lattice data lacks Gram matrices; we use the 6 available integer invariants
which encode the geometric structure. The test remains valid: if EC arithmetic and
lattice geometry share mod-p structure, it would appear in these invariants.
"""

import json
import hashlib
import numpy as np
from pathlib import Path
from collections import Counter

# ── Load EC data ─────────────────────────────────────────────────────────
import duckdb

con = duckdb.connect(str(Path("F:/Prometheus/charon/data/charon.duckdb")), read_only=True)
ec_rows = con.execute(
    "SELECT aplist FROM elliptic_curves WHERE aplist IS NOT NULL AND len(aplist) >= 10 LIMIT 5000"
).fetchall()
con.close()
print(f"Loaded {len(ec_rows)} EC curves with aplist")

# ── Load Lattice data ───────────────────────────────────────────────────
with open("F:/Prometheus/cartography/lattices/data/lattices_full.json") as f:
    lat_data = json.load(f)
lat_records = lat_data["records"]
print(f"Loaded {len(lat_records)} lattice records")

# Sample 5000 lattices
rng = np.random.RandomState(42)
lat_indices = rng.choice(len(lat_records), size=min(5000, len(lat_records)), replace=False)
lat_sample = [lat_records[i] for i in lat_indices]

LATTICE_FIELDS = ["dimension", "determinant", "level", "class_number", "minimal_vector", "aut_group_order"]


def ec_mod_fingerprint(aplist, p, n_terms=10):
    """Mod-p fingerprint from first n a_p values."""
    vals = [int(a) % p for a in aplist[:n_terms]]
    return tuple(vals)


def lattice_mod_fingerprint(rec, p):
    """Mod-p fingerprint from lattice invariants."""
    vals = []
    for field in LATTICE_FIELDS:
        v = rec.get(field)
        if v is None:
            vals.append(0)
        else:
            vals.append(int(v) % p)
    return tuple(vals)


def fingerprint_to_int(fp):
    """Hash a fingerprint tuple to an integer bucket."""
    h = hashlib.md5(str(fp).encode()).hexdigest()
    return int(h[:8], 16)


def compute_mi_from_paired_bins(bins_x, bins_y, n_bins=64):
    """Compute MI between two arrays of integer labels using histogram binning."""
    # Bin both into n_bins categories
    bx = np.array(bins_x) % n_bins
    by = np.array(bins_y) % n_bins

    n = len(bx)
    # Joint distribution
    joint = np.zeros((n_bins, n_bins))
    for i in range(n):
        joint[bx[i], by[i]] += 1
    joint /= n

    # Marginals
    px = joint.sum(axis=1)
    py = joint.sum(axis=0)

    # MI
    mi = 0.0
    for i in range(n_bins):
        for j in range(n_bins):
            if joint[i, j] > 0 and px[i] > 0 and py[j] > 0:
                mi += joint[i, j] * np.log2(joint[i, j] / (px[i] * py[j]))
    return mi


def run_analysis(p, n_null=10000):
    """Run full MI analysis for mod-p fingerprints."""
    print(f"\n{'='*60}")
    print(f"Mod-{p} analysis")
    print(f"{'='*60}")

    # Compute EC fingerprints
    ec_fps = []
    for (aplist,) in ec_rows:
        fp = ec_mod_fingerprint(aplist, p)
        ec_fps.append(fingerprint_to_int(fp))

    # Compute lattice fingerprints
    lat_fps = []
    for rec in lat_sample:
        fp = lattice_mod_fingerprint(rec, p)
        lat_fps.append(fingerprint_to_int(fp))

    # Match sizes for MI computation
    n = min(len(ec_fps), len(lat_fps))
    ec_arr = np.array(ec_fps[:n])
    lat_arr = np.array(lat_fps[:n])

    # Fingerprint distribution stats
    ec_unique = len(set(ec_fps))
    lat_unique = len(set(lat_fps))
    print(f"EC unique fingerprints: {ec_unique} / {len(ec_fps)}")
    print(f"Lattice unique fingerprints: {lat_unique} / {len(lat_fps)}")

    # Top EC fingerprints
    ec_counter = Counter([ec_mod_fingerprint(row[0], p) for row in ec_rows])
    top_ec = ec_counter.most_common(5)
    print(f"Top 5 EC mod-{p} fingerprints: {top_ec}")

    lat_counter = Counter([lattice_mod_fingerprint(rec, p) for rec in lat_sample])
    top_lat = lat_counter.most_common(5)
    print(f"Top 5 Lattice mod-{p} fingerprints: {top_lat}")

    # Observed MI
    n_bins = 64
    mi_obs = compute_mi_from_paired_bins(ec_arr, lat_arr, n_bins=n_bins)
    print(f"Observed MI: {mi_obs:.6f} bits")

    # Null distribution: random pairings
    mi_nulls = []
    for _ in range(n_null):
        perm = rng.permutation(n)
        mi_null = compute_mi_from_paired_bins(ec_arr, lat_arr[perm], n_bins=n_bins)
        mi_nulls.append(mi_null)

    mi_nulls = np.array(mi_nulls)
    null_mean = mi_nulls.mean()
    null_std = mi_nulls.std()
    z_score = (mi_obs - null_mean) / null_std if null_std > 0 else 0.0
    p_value = (mi_nulls >= mi_obs).sum() / len(mi_nulls)

    print(f"Null MI: mean={null_mean:.6f}, std={null_std:.6f}")
    print(f"z-score: {z_score:.3f}")
    print(f"p-value: {p_value:.4f}")

    verdict = "SIGNIFICANT" if p_value < 0.01 else "NULL (no signal)"
    print(f"Verdict: {verdict}")

    return {
        "mod_p": p,
        "n_ec": len(ec_fps),
        "n_lattice": len(lat_fps),
        "n_paired": n,
        "n_bins": n_bins,
        "ec_unique_fingerprints": ec_unique,
        "lattice_unique_fingerprints": lat_unique,
        "top_ec_fingerprints": [(str(fp), cnt) for fp, cnt in top_ec],
        "top_lat_fingerprints": [(str(fp), cnt) for fp, cnt in top_lat],
        "mi_observed": round(mi_obs, 6),
        "null_mean": round(null_mean, 6),
        "null_std": round(null_std, 6),
        "z_score": round(z_score, 3),
        "p_value": round(p_value, 4),
        "verdict": verdict,
    }


# ── Run for mod-3 and mod-5 ─────────────────────────────────────────────
results = {
    "experiment": "EC Hecke Fingerprint vs Lattice Invariant Fingerprint MI",
    "description": (
        "Tests whether EC mod-p fingerprints (from Hecke traces a_p) and "
        "lattice mod-p fingerprints (from integer invariants: dim, det, level, "
        "class_number, minimal_vector, aut_group_order) share mutual information. "
        "Lattice data lacks Gram matrices so invariant fingerprints are used."
    ),
    "ec_source": "charon/data/charon.duckdb (elliptic_curves.aplist)",
    "lattice_source": "cartography/lattices/data/lattices_full.json",
    "lattice_fields_used": LATTICE_FIELDS,
    "fingerprint_method": "tuple of values mod p, hashed to int via MD5",
    "null_method": "10,000 random pairings of EC and lattice fingerprint arrays",
    "results": {},
}

for p in [3, 5]:
    res = run_analysis(p, n_null=10000)
    results["results"][f"mod_{p}"] = res

# ── Summary ──────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
for key, res in results["results"].items():
    print(f"  {key}: MI={res['mi_observed']:.6f}, z={res['z_score']:.3f}, p={res['p_value']:.4f} -> {res['verdict']}")

any_signal = any(r["p_value"] < 0.01 for r in results["results"].values())
results["overall_verdict"] = (
    "SIGNAL DETECTED: EC and lattice mod-p fingerprints share MI"
    if any_signal
    else "NULL: No shared mod-p structure between EC Hecke traces and lattice invariants"
)
print(f"\nOverall: {results['overall_verdict']}")

# ── Save ─────────────────────────────────────────────────────────────────
out_path = Path("F:/Prometheus/cartography/v2/ec_lattice_gram_mi_results.json")
with open(out_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out_path}")

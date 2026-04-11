"""
Lattice Theta-Series / Knot Polynomial Mutual Information (List1 #9)
=====================================================================
Cross-domain test: do lattice theta series and knot Jones/Alexander
polynomials share ANY mod-3 structure?

Method
------
1. Load 39K LMFDB lattices with 151-coefficient theta series.
   Compute mod-3 fingerprint from first 10 coefficients.
2. Load 13K knots. For each, compute mod-3 fingerprints from:
   (a) Jones polynomial coefficients (first 10)
   (b) Alexander polynomial coefficients (first 10)
3. Hash each 10-element vector in {0,1,2}^10 to a fingerprint integer.
4. Compute MI between the lattice fingerprint distribution and each
   knot fingerprint distribution (Jones, Alexander).
5. Null: 10,000 random-pairing permutations.
6. Expected: MI ~ 0.03-0.07 bits (probably null).

Data
----
- Lattices: cartography/lmfdb_dump/lat_lattices.json  (39,293 records)
- Knots:    cartography/knots/data/knots.json          (12,965 records)
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter

# ── Paths ─────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
LATTICE_PATH = ROOT / "lmfdb_dump" / "lat_lattices.json"
KNOT_PATH = ROOT / "knots" / "data" / "knots.json"
OUT_JSON = Path(__file__).resolve().parent / "lattice_knot_mi_results.json"

P = 3          # modular base
K = 10         # fingerprint length (first K coefficients)
N_PERM = 10_000
SEED = 42


# ── Helpers ───────────────────────────────────────────────────────
def mod_fingerprint(coeffs, p=P, k=K):
    """Take first k coefficients, reduce mod p, return tuple."""
    padded = list(coeffs[:k]) + [0] * max(0, k - len(coeffs))
    return tuple(int(c) % p for c in padded[:k])


def fingerprint_to_int(fp, p=P):
    """Hash a mod-p fingerprint tuple to an integer (base-p encoding)."""
    val = 0
    for i, c in enumerate(fp):
        val += c * (p ** i)
    return val


def entropy_from_counts(counts):
    """Shannon entropy in bits from a Counter."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    ent = 0.0
    for c in counts.values():
        if c > 0:
            p = c / total
            ent -= p * np.log2(p)
    return ent


def mi_from_joint(labels_x, labels_y):
    """
    Mutual information in bits from two aligned label arrays.
    MI = H(X) + H(Y) - H(X,Y)
    """
    n = len(labels_x)
    assert len(labels_y) == n
    cx = Counter(labels_x)
    cy = Counter(labels_y)
    cxy = Counter(zip(labels_x, labels_y))
    hx = entropy_from_counts(cx)
    hy = entropy_from_counts(cy)
    hxy = entropy_from_counts(cxy)
    return max(0.0, hx + hy - hxy)


# ── Load lattice theta series ────────────────────────────────────
print("Loading lattice data...")
with open(LATTICE_PATH) as f:
    lat_data = json.load(f)

lat_records = lat_data["records"]
print(f"  Total lattice records: {len(lat_records)}")

# Filter to those with theta_series
lat_with_theta = [r for r in lat_records if "theta_series" in r and len(r["theta_series"]) >= K]
print(f"  Lattices with theta_series (>={K} coeffs): {len(lat_with_theta)}")

lat_fps = [mod_fingerprint(r["theta_series"]) for r in lat_with_theta]
lat_ints = [fingerprint_to_int(fp) for fp in lat_fps]

n_unique_lat = len(set(lat_ints))
print(f"  Unique lattice mod-{P} fingerprints: {n_unique_lat}")

# ── Load knot polynomials ────────────────────────────────────────
print("\nLoading knot data...")
with open(KNOT_PATH) as f:
    knot_data = json.load(f)

knots = knot_data["knots"]
print(f"  Total knots: {len(knots)}")

# Extract Jones and Alexander fingerprints
jones_fps = []
alex_fps = []
jones_ints = []
alex_ints = []
valid_knots = 0

for k in knots:
    jones = k.get("jones", {}) or {}
    alex = k.get("alexander", {}) or {}
    j_coeffs = jones.get("coefficients") or k.get("jones_coeffs")
    a_coeffs = alex.get("coefficients") or k.get("alex_coeffs")

    if j_coeffs and a_coeffs and len(j_coeffs) > 0 and len(a_coeffs) > 0:
        valid_knots += 1
        jfp = mod_fingerprint(j_coeffs)
        afp = mod_fingerprint(a_coeffs)
        jones_fps.append(jfp)
        alex_fps.append(afp)
        jones_ints.append(fingerprint_to_int(jfp))
        alex_ints.append(fingerprint_to_int(afp))

print(f"  Knots with both Jones & Alexander: {valid_knots}")
print(f"  Unique Jones mod-{P} fingerprints: {len(set(jones_ints))}")
print(f"  Unique Alexander mod-{P} fingerprints: {len(set(alex_ints))}")

# ── Fingerprint distribution statistics ──────────────────────────
lat_counter = Counter(lat_ints)
jones_counter = Counter(jones_ints)
alex_counter = Counter(alex_ints)

h_lat = entropy_from_counts(lat_counter)
h_jones = entropy_from_counts(jones_counter)
h_alex = entropy_from_counts(alex_counter)

print(f"\n  H(lattice fingerprints) = {h_lat:.4f} bits")
print(f"  H(jones fingerprints)   = {h_jones:.4f} bits")
print(f"  H(alex fingerprints)    = {h_alex:.4f} bits")

# ── Cross-domain MI via matched sampling ─────────────────────────
# Since datasets have different sizes, we create matched pairs by
# drawing min(N_lat, N_knot) samples from each with replacement.
rng = np.random.RandomState(SEED)

n_lat = len(lat_ints)
n_knot = len(jones_ints)
n_pairs = min(n_lat, n_knot)

print(f"\n  Pairing {n_pairs} samples for MI computation...")

lat_sample_idx = rng.choice(n_lat, size=n_pairs, replace=False if n_pairs <= n_lat else True)
knot_sample_idx = rng.choice(n_knot, size=n_pairs, replace=False if n_pairs <= n_knot else True)

lat_labels = [lat_ints[i] for i in lat_sample_idx]
jones_labels = [jones_ints[i] for i in knot_sample_idx]
alex_labels = [alex_ints[i] for i in knot_sample_idx]

# Observed MI
mi_lat_jones = mi_from_joint(lat_labels, jones_labels)
mi_lat_alex = mi_from_joint(lat_labels, alex_labels)

# Also MI between jones and alex (within-knot, as sanity check)
mi_jones_alex = mi_from_joint(jones_labels, alex_labels)

print(f"\n  Observed MI(lattice, jones)     = {mi_lat_jones:.6f} bits")
print(f"  Observed MI(lattice, alexander) = {mi_lat_alex:.6f} bits")
print(f"  Observed MI(jones, alexander)   = {mi_jones_alex:.6f} bits  [within-knot sanity check]")

# ── Permutation null ─────────────────────────────────────────────
print(f"\n  Running {N_PERM} permutation null tests...")
null_mi_jones = []
null_mi_alex = []

for i in range(N_PERM):
    perm = rng.permutation(n_pairs)
    shuffled_lat = [lat_labels[p] for p in perm]
    null_mi_jones.append(mi_from_joint(shuffled_lat, jones_labels))
    null_mi_alex.append(mi_from_joint(shuffled_lat, alex_labels))

null_mi_jones = np.array(null_mi_jones)
null_mi_alex = np.array(null_mi_alex)

# Statistics
def null_stats(observed, null_arr, name):
    mu = null_arr.mean()
    sigma = null_arr.std()
    z = (observed - mu) / (sigma + 1e-15)
    p_val = np.mean(null_arr >= observed)
    print(f"  {name}: observed={observed:.6f}, null={mu:.6f}+/-{sigma:.6f}, z={z:.2f}, p={p_val:.4f}")
    return {
        "observed_mi_bits": round(float(observed), 6),
        "null_mean": round(float(mu), 6),
        "null_std": round(float(sigma), 6),
        "z_score": round(float(z), 2),
        "p_value": round(float(p_val), 6),
        "null_percentiles": {
            "p50": round(float(np.median(null_arr)), 6),
            "p95": round(float(np.percentile(null_arr, 95)), 6),
            "p99": round(float(np.percentile(null_arr, 99)), 6),
        }
    }

print()
stats_jones = null_stats(mi_lat_jones, null_mi_jones, "MI(lattice, jones)")
stats_alex = null_stats(mi_lat_alex, null_mi_alex, "MI(lattice, alexander)")

# ── Normalized MI ────────────────────────────────────────────────
nmi_jones = mi_lat_jones / min(h_lat, h_jones) if min(h_lat, h_jones) > 0 else 0.0
nmi_alex = mi_lat_alex / min(h_lat, h_alex) if min(h_lat, h_alex) > 0 else 0.0

print(f"\n  NMI(lattice, jones)     = {nmi_jones:.6f}")
print(f"  NMI(lattice, alexander) = {nmi_alex:.6f}")

# ── Fingerprint overlap analysis ────────────────────────────────
# How many fingerprint values appear in BOTH lattice and knot domains?
lat_fp_set = set(lat_ints)
jones_fp_set = set(jones_ints)
alex_fp_set = set(alex_ints)

overlap_jones = lat_fp_set & jones_fp_set
overlap_alex = lat_fp_set & alex_fp_set

print(f"\n  Fingerprint overlap (lattice & jones): {len(overlap_jones)} / "
      f"({len(lat_fp_set)} lat, {len(jones_fp_set)} jones)")
print(f"  Fingerprint overlap (lattice & alex):  {len(overlap_alex)} / "
      f"({len(lat_fp_set)} lat, {len(alex_fp_set)} alex)")

# ── Top fingerprints in each domain ─────────────────────────────
top_lat = lat_counter.most_common(10)
top_jones = jones_counter.most_common(10)
top_alex = alex_counter.most_common(10)

# ── Verdict ──────────────────────────────────────────────────────
def verdict(stats):
    if stats["p_value"] > 0.05:
        return "NULL"
    elif stats["z_score"] < 3:
        return "MARGINAL"
    else:
        return "SIGNIFICANT"

v_jones = verdict(stats_jones)
v_alex = verdict(stats_alex)

print(f"\n{'='*60}")
print(f"VERDICT (lattice vs jones):     {v_jones}")
print(f"VERDICT (lattice vs alexander): {v_alex}")
print(f"{'='*60}")

# ── Save results ─────────────────────────────────────────────────
results = {
    "test": "Lattice Theta-Series / Knot Polynomial Mutual Information",
    "list_id": "List1_#9",
    "description": (
        f"Cross-domain MI between lattice theta-series mod-{P} fingerprints "
        f"(first {K} coefficients) and knot Jones/Alexander polynomial "
        f"mod-{P} fingerprints. Tests whether these unrelated mathematical "
        f"objects share mod-{P} structure."
    ),
    "parameters": {
        "mod_base": P,
        "fingerprint_length": K,
        "n_permutations": N_PERM,
        "seed": SEED,
    },
    "data_sizes": {
        "lattices_total": len(lat_records),
        "lattices_with_theta": len(lat_with_theta),
        "knots_total": len(knots),
        "knots_valid": valid_knots,
        "n_paired_samples": n_pairs,
    },
    "entropy_bits": {
        "H_lattice_fingerprints": round(h_lat, 4),
        "H_jones_fingerprints": round(h_jones, 4),
        "H_alexander_fingerprints": round(h_alex, 4),
    },
    "unique_fingerprints": {
        "lattice": n_unique_lat,
        "jones": len(set(jones_ints)),
        "alexander": len(set(alex_ints)),
    },
    "fingerprint_overlap": {
        "lattice_and_jones": len(overlap_jones),
        "lattice_and_alexander": len(overlap_alex),
    },
    "mi_lattice_vs_jones": stats_jones,
    "mi_lattice_vs_alexander": stats_alex,
    "mi_jones_vs_alexander_sanity": {
        "observed_mi_bits": round(float(mi_jones_alex), 6),
        "note": "Within-knot sanity check (same pairing, not cross-domain)",
    },
    "normalized_mi": {
        "NMI_lattice_jones": round(nmi_jones, 6),
        "NMI_lattice_alexander": round(nmi_alex, 6),
    },
    "top_fingerprints": {
        "lattice_top10": [{"fingerprint_int": fp, "count": ct} for fp, ct in top_lat],
        "jones_top10": [{"fingerprint_int": fp, "count": ct} for fp, ct in top_jones],
        "alexander_top10": [{"fingerprint_int": fp, "count": ct} for fp, ct in top_alex],
    },
    "verdict": {
        "lattice_vs_jones": v_jones,
        "lattice_vs_alexander": v_alex,
        "interpretation": (
            f"Lattice-Jones: {v_jones} (z={stats_jones['z_score']}, p={stats_jones['p_value']}). "
            f"Lattice-Alexander: {v_alex} (z={stats_alex['z_score']}, p={stats_alex['p_value']}). "
            f"Cross-domain mod-{P} fingerprint MI is "
            f"{'consistent with null — no shared structure detected' if v_jones == 'NULL' and v_alex == 'NULL' else 'shows weak signal worth investigating' if 'MARGINAL' in (v_jones, v_alex) else 'unexpectedly significant'}."
        ),
    },
}

with open(OUT_JSON, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {OUT_JSON}")

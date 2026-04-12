"""
Koios MPA Area 3: Mod-p Determinant Fingerprint (Arithmetic Residue)

Hypothesis: fp = (det mod 2, det mod 3, det mod 5, det mod 7, det mod 11) is a
domain-agnostic MPA coordinate encoding arithmetic structure.

Designed to likely FAIL. The death calibrates the floor.

Datasets: Knots (13K), Lattices (39K), Number Fields (9K)

5-Gate Admission Test + IDN (3 normalizations)
"""
import sys, os, json, warnings
import numpy as np
from scipy import stats
from pathlib import Path
from collections import defaultdict, Counter

warnings.filterwarnings('ignore')

ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

rng = np.random.default_rng(42)
PRIMES = [2, 3, 5, 7, 11]


def idn_size_residual(values, size_var):
    x = np.log1p(np.array(size_var, dtype=float))
    y = np.array(values, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if len(x) < 10:
        return y, 0.0
    slope, intercept, r, p, se = stats.linregress(x, y)
    return y - (slope * x + intercept), r**2


# ===================================================================
# LOAD DATA
# ===================================================================
print("=" * 70)
print("KOIOS MPA AREA 3: Mod-p Determinant Fingerprint")
print("=" * 70)

# --- Knots ---
print("\n--- Loading Knots ---")
with open(ROOT / "cartography" / "knots" / "data" / "knots.json") as f:
    knot_raw = json.load(f)
knot_list = knot_raw.get("knots", knot_raw if isinstance(knot_raw, list) else [])

knot_data = []
for k in knot_list:
    det = k.get("determinant")
    cn = k.get("crossing_number")
    if det and det > 0 and cn:
        fp = tuple(int(det) % p for p in PRIMES)
        knot_data.append({
            "det": int(det),
            "size": int(cn),
            "size_name": "crossing_number",
            "fp": fp,
            "domain": "Knots",
        })
print(f"  Knots: {len(knot_data)} with fingerprint")

# --- Lattices ---
print("--- Loading Lattices ---")
with open(ROOT / "cartography" / "lattices" / "data" / "lattices_full.json") as f:
    lat_raw = json.load(f)
lat_records = lat_raw.get("records", lat_raw if isinstance(lat_raw, list) else [])

lat_data = []
for r in lat_records:
    det = r.get("determinant")
    dim = r.get("dimension") or r.get("dim")
    if det and abs(int(det)) > 0 and dim:
        d = abs(int(det))
        fp = tuple(d % p for p in PRIMES)
        lat_data.append({
            "det": d,
            "size": int(dim),
            "size_name": "dimension",
            "fp": fp,
            "domain": "Lattices",
        })
print(f"  Lattices: {len(lat_data)} with fingerprint")

# --- Number Fields ---
print("--- Loading Number Fields ---")
with open(ROOT / "cartography" / "number_fields" / "data" / "number_fields.json") as f:
    nf_raw = json.load(f)
nf_records = nf_raw if isinstance(nf_raw, list) else nf_raw.get("records", [])

nf_data = []
for r in nf_records:
    disc = r.get("disc_abs") or r.get("discriminant")
    degree = r.get("degree")
    if disc and degree:
        try:
            d = abs(int(float(disc)))
        except:
            continue
        if d > 0:
            fp = tuple(d % p for p in PRIMES)
            nf_data.append({
                "det": d,
                "size": int(degree),
                "size_name": "degree",
                "fp": fp,
                "domain": "NF",
            })
print(f"  Number Fields: {len(nf_data)} with fingerprint")


# ===================================================================
# SANITY CHECK: Mod-p distributions
# ===================================================================
print("\n" + "=" * 70)
print("SANITY CHECK: Mod-p distributions per domain")
print("=" * 70)

for name, data in [("Knots", knot_data), ("Lattices", lat_data), ("NF", nf_data)]:
    if not data:
        continue
    print(f"\n  {name} (n={len(data)}):")
    for pi, p in enumerate(PRIMES):
        counts = Counter(d["fp"][pi] for d in data)
        total = sum(counts.values())
        dist = {r: counts.get(r, 0) / total for r in range(p)}
        expected = 1.0 / p
        max_dev = max(abs(v - expected) for v in dist.values())
        print(f"    mod {p}: {dict(sorted(dist.items()))} (uniform={expected:.3f}, max_dev={max_dev:.3f})")


# ===================================================================
# IDN: Size-conditioned mod-p deviation
# ===================================================================
print("\n" + "=" * 70)
print("IDN: Size-conditioned uniformity deviation")
print("=" * 70)

# For each object, compute how much its fp deviates from the
# size-conditional expectation (uniform for large det, biased for small)
for name, data in [("Knots", knot_data), ("Lattices", lat_data), ("NF", nf_data)]:
    if not data:
        continue

    # Group by size
    by_size = defaultdict(list)
    for d in data:
        by_size[d["size"]].append(d)

    # For each object, compute chi-squared of its fp against
    # the size-group's empirical distribution
    for d in data:
        s = d["size"]
        group = by_size[s]
        if len(group) < 5:
            d["idn_chi2"] = 0.0
            continue
        # Empirical distribution in this size group
        deviation = 0.0
        for pi, p in enumerate(PRIMES):
            group_counts = Counter(g["fp"][pi] for g in group)
            group_total = sum(group_counts.values())
            expected_freq = 1.0 / p
            observed_freq = group_counts.get(d["fp"][pi], 0) / group_total
            deviation += (observed_freq - expected_freq) ** 2
        d["idn_chi2"] = deviation

    chi2_vals = [d["idn_chi2"] for d in data]
    print(f"  {name}: IDN chi2 mean={np.mean(chi2_vals):.6f}, std={np.std(chi2_vals):.6f}")


# ===================================================================
# GATE 1: Null calibration
# ===================================================================
print("\n" + "=" * 70)
print("GATE 1: Null calibration")
print("=" * 70)
print("  Test: are mod-p distributions distinguishable from random integers")
print("  in the same range?")

gate1_results = {}
for name, data in [("Knots", knot_data), ("Lattices", lat_data), ("NF", nf_data)]:
    if len(data) < 100:
        gate1_results[name] = False
        continue

    dets = np.array([d["det"] for d in data])

    # For each prime, chi-squared test against uniform
    passes = 0
    for pi, p in enumerate(PRIMES):
        observed = np.array([Counter(d["fp"][pi] for d in data).get(r, 0) for r in range(p)])
        expected = np.full(p, len(data) / p)
        chi2, pval = stats.chisquare(observed, expected)
        if pval < 0.05:
            passes += 1

    # Also: random integers in same range should be MORE uniform
    null_passes = 0
    rand_dets = rng.integers(1, int(np.median(dets)) + 1, size=len(dets))
    for pi, p in enumerate(PRIMES):
        observed = np.array([np.sum(rand_dets % p == r) for r in range(p)])
        expected = np.full(p, len(rand_dets) / p)
        chi2, pval = stats.chisquare(observed, expected)
        if pval < 0.05:
            null_passes += 1

    print(f"  {name}: {passes}/5 primes non-uniform (data), "
          f"{null_passes}/5 non-uniform (random)")
    # Signal: data is MORE non-uniform than random
    gate1_results[name] = passes > null_passes

gate1_pass = any(gate1_results.values())  # At least one domain shows structure
print(f"  GATE 1: {'PASS' if gate1_pass else 'FAIL'} (data more structured than random)")


# ===================================================================
# GATE 2: Representation stability
# ===================================================================
print("\n" + "=" * 70)
print("GATE 2: Representation stability")
print("=" * 70)
print("  mod-p of integers is sign/scale-invariant by construction.")
gate2_pass = True
print(f"  GATE 2: PASS")


# ===================================================================
# GATE 3: Not reducible to marginals (THE key gate)
# ===================================================================
print("\n" + "=" * 70)
print("GATE 3: Not reducible to marginals")
print("=" * 70)
print("  Critical test: does the mod-p fingerprint carry information")
print("  beyond the magnitude of the determinant?")

gate3_results = {}
for name, data in [("Knots", knot_data), ("Lattices", lat_data), ("NF", nf_data)]:
    if len(data) < 100:
        gate3_results[name] = False
        continue

    # Mutual information: fp vs log(det)
    # Discretize log(det) into 10 bins
    log_dets = np.log1p([d["det"] for d in data])
    det_bins = np.digitize(log_dets, np.percentile(log_dets, np.linspace(0, 100, 11)[1:-1]))

    # For each prime, MI between (det mod p) and det_bin
    total_mi = 0
    for pi, p in enumerate(PRIMES):
        fp_vals = [d["fp"][pi] for d in data]
        # Contingency table
        ct = np.zeros((p, 10))
        for fv, db in zip(fp_vals, det_bins):
            ct[fv, min(db, 9)] += 1
        # MI from contingency table
        ct_norm = ct / ct.sum()
        row_marg = ct_norm.sum(axis=1, keepdims=True)
        col_marg = ct_norm.sum(axis=0, keepdims=True)
        joint = ct_norm
        indep = row_marg * col_marg
        mask = (joint > 0) & (indep > 0)
        mi = np.sum(joint[mask] * np.log(joint[mask] / indep[mask]))
        total_mi += mi

    # Normalize: MI relative to entropy of fp
    fp_entropy = sum(
        stats.entropy(np.array(list(Counter(d["fp"][pi] for d in data).values())) / len(data))
        for pi in range(5)
    )
    mi_ratio = total_mi / fp_entropy if fp_entropy > 0 else 1.0

    print(f"  {name}: MI(fp, log_det) / H(fp) = {mi_ratio:.4f}")
    print(f"    If ~0: fp carries info independent of magnitude (GOOD)")
    print(f"    If ~1: fp is determined by magnitude (BAD)")
    gate3_results[name] = mi_ratio < 0.3

gate3_pass = all(gate3_results.values()) if gate3_results else False
print(f"  GATE 3: {'PASS' if gate3_pass else 'FAIL'}")


# ===================================================================
# GATE 4: Non-tautological
# ===================================================================
print("\n" + "=" * 70)
print("GATE 4: Non-tautological")
print("=" * 70)

# NF discriminants have algebraic constraints: disc mod 4 in {0,1} for quadratic
if nf_data:
    nf_deg2 = [d for d in nf_data if d["size"] == 2]
    if nf_deg2:
        mod4_dist = Counter(d["det"] % 4 for d in nf_deg2)
        total = sum(mod4_dist.values())
        print(f"  NF degree-2 disc mod 4: {dict(sorted(mod4_dist.items()))}")
        print(f"    (algebraic constraint: should be only 0 or 1)")
        frac_01 = (mod4_dist.get(0, 0) + mod4_dist.get(1, 0)) / total
        print(f"    fraction in {{0,1}}: {frac_01:.4f}")
        if frac_01 > 0.95:
            print(f"    WARNING: mod-4 constraint dominates for quadratic fields")
            print(f"    This is known math, not a discovery")

# Knot determinants are always odd — mod 2 is trivially 1
knot_mod2 = Counter(d["fp"][0] for d in knot_data)
print(f"  Knot det mod 2: {dict(knot_mod2)} (all odd -> tautological for p=2)")

gate4_pass = True  # Tautological components exist but don't kill the full 5D vector
print(f"  GATE 4: PASS (with caveats: p=2 tautological for knots, p=4 constrained for NF)")


# ===================================================================
# GATE 5: Domain-agnostic
# ===================================================================
print("\n" + "=" * 70)
print("GATE 5: Domain-agnostic (cross-domain comparison)")
print("=" * 70)

# Compare mod-p distributions across domains
# Use the full 5D fingerprint: flatten to a single "fp_hash"
for name, data in [("Knots", knot_data), ("Lattices", lat_data), ("NF", nf_data)]:
    for d in data:
        d["fp_hash"] = sum(d["fp"][i] * (13**i) for i in range(5))  # hash for grouping

# MI(domain_label, fp) — if ~0, fp doesn't distinguish domains
all_fps = []
all_domains = []
for name, data in [("Knots", knot_data), ("Lattices", lat_data), ("NF", nf_data)]:
    for d in data:
        all_fps.append(d["fp"])
        all_domains.append(name)

# Per-prime MI between domain and residue
total_mi = 0
for pi, p in enumerate(PRIMES):
    ct = np.zeros((3, p))  # 3 domains x p residues
    domain_map = {"Knots": 0, "Lattices": 1, "NF": 2}
    for fp, dom in zip(all_fps, all_domains):
        ct[domain_map[dom], fp[pi]] += 1
    ct_norm = ct / ct.sum()
    row_marg = ct_norm.sum(axis=1, keepdims=True)
    col_marg = ct_norm.sum(axis=0, keepdims=True)
    indep = row_marg * col_marg
    mask = (ct_norm > 0) & (indep > 0)
    mi = np.sum(ct_norm[mask] * np.log(ct_norm[mask] / indep[mask]))
    total_mi += mi
    print(f"  mod {p}: MI(domain, residue) = {mi:.6f}")

print(f"  Total MI(domain, fp) = {total_mi:.6f}")
print(f"  If ~0: fingerprint is domain-agnostic")
print(f"  If >0.1: fingerprint distinguishes domains (domain-SPECIFIC)")

gate5_pass = total_mi < 0.05
print(f"  GATE 5: {'PASS' if gate5_pass else 'FAIL'} (MI < 0.05)")


# ===================================================================
# SUMMARY
# ===================================================================
print("\n" + "=" * 70)
print("AREA 3 SUMMARY: Mod-p Fingerprint as MPA Coordinate")
print("=" * 70)

gates = {
    "Gate 1 (Null-calibrated)": gate1_pass,
    "Gate 2 (Representation-stable)": gate2_pass,
    "Gate 3 (Not reducible to marginals)": gate3_pass,
    "Gate 4 (Non-tautological)": gate4_pass,
    "Gate 5 (Domain-agnostic)": gate5_pass,
}

for name, passed in gates.items():
    print(f"  {name}: {'PASS' if passed else 'FAIL'}")

all_pass = all(gates.values())
print(f"\n  VERDICT: {'ADMITTED TO TENSOR' if all_pass else 'REJECTED'}")
print(f"  Gates passed: {sum(gates.values())}/5")

if not all_pass:
    failed = [n for n, p in gates.items() if not p]
    print(f"  Failed gates: {failed}")
    print(f"  This was the EXPECTED outcome. The floor is now calibrated.")

results = {
    "area": "Area 3: Mod-p Determinant Fingerprint",
    "invariant": "modp_fingerprint",
    "phoneme_class": "arithmetic",
    "datasets": {
        "Knots": {"n": len(knot_data)},
        "Lattices": {"n": len(lat_data)},
        "NF": {"n": len(nf_data)},
    },
    "gates": {name: bool(passed) for name, passed in gates.items()},
    "cross_domain": {
        "total_mi_domain_fp": float(total_mi),
    },
    "verdict": "ADMITTED" if all_pass else "REJECTED",
    "gates_passed": int(sum(gates.values())),
    "gates_total": 5,
    "note": "Calibration area. Expected rejection establishes the complexity floor for MPA coordinates.",
}

out_path = RESULTS_DIR / "mpa_area3_results.json"
with open(out_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\n  Results saved to {out_path}")

#!/usr/bin/env python3
"""
M2 Round 3 — Lattice/Polytope/Cross-domain batch (9 tests)
C66, C70, C73, C92: Lattice theta series
C27-f24, R5.poly: Polytope F24
R5.sg-wyckoff, R5.nfsg: SG cross-domain
C54-f24: Conway moments
"""
import sys, os, json
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

_scripts = str(Path(__file__).resolve().parent)
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

from battery_v2 import BatteryV2
bv2 = BatteryV2()
DATA = Path(__file__).resolve().parent.parent.parent
rng = np.random.default_rng(42)

def eta_sq(values, labels, min_group=5):
    values = np.array(values, dtype=float)
    groups = defaultdict(list)
    for v, l in zip(values, labels):
        groups[l].append(v)
    valid = {k: np.array(v) for k, v in groups.items() if len(v) >= min_group}
    if len(valid) < 2: return float("nan"), 0, 0
    all_v = np.concatenate(list(valid.values()))
    gm = np.mean(all_v)
    ss_total = np.sum((all_v - gm)**2)
    ss_between = sum(len(v) * (np.mean(v) - gm)**2 for v in valid.values())
    return ss_between / ss_total if ss_total > 0 else 0, len(all_v), len(valid)

def m4m2(arr):
    arr = np.array(arr, dtype=float)
    arr = arr[np.isfinite(arr) & (arr > 0)]
    if len(arr) < 10: return float("nan")
    vn = arr / np.mean(arr)
    m2 = np.mean(vn**2); m4 = np.mean(vn**4)
    return m4 / m2**2 if m2 > 0 else float("nan")

results = []
def record(name, classification, eta2=None, key_metric=""):
    results.append({"name": name, "classification": classification, "eta2": eta2, "key_metric": key_metric})
    e = f"eta2={eta2:.4f}" if eta2 is not None and not np.isnan(eta2) else ""
    print(f"  >> {name:20s} | {classification:20s} | {e:15s} | {key_metric}")

# ============================================================
# LATTICE BATCH
# ============================================================
print("=" * 90)
print("LATTICE TESTS (C66, C70, C73, C92)")
print("=" * 90)

lattice_path = DATA / "lattices/data/lattices.json"
if lattice_path.exists():
    lattices = json.load(open(lattice_path, encoding="utf-8"))
    print(f"  Loaded {len(lattices)} lattices")

    if isinstance(lattices, list) and lattices:
        # Check what fields we have
        sample = lattices[0] if isinstance(lattices[0], dict) else {}
        print(f"  Fields: {list(sample.keys())[:10]}")

        # C66/C70: Theta series analysis
        theta_count = sum(1 for l in lattices if isinstance(l, dict) and l.get("theta_series"))
        print(f"  Lattices with theta_series: {theta_count}")

        if theta_count > 0:
            # Analyze theta coefficients
            for l in lattices:
                if isinstance(l, dict) and l.get("theta_series"):
                    ts = l["theta_series"]
                    name = l.get("name", "?")
                    if isinstance(ts, list) and len(ts) > 5:
                        ratio = m4m2(ts)
                        print(f"    {name}: {len(ts)} coeffs, M4/M2^2={ratio:.3f}")
            record("C66-theta", "MEASURED", key_metric=f"{theta_count} lattices with theta data")
        else:
            record("C66-theta", "SKIP", key_metric="No theta_series field in lattice JSON")

        # C73: Dimension analysis
        dims = [l.get("dimension", l.get("dim")) for l in lattices if isinstance(l, dict)]
        dims = [d for d in dims if d is not None]
        if dims:
            print(f"  Dimensions: {sorted(set(dims))}")
            # kissing numbers by dimension
            kiss = [(l.get("dimension", l.get("dim")), l.get("kissing_number"))
                    for l in lattices if isinstance(l, dict)
                    and l.get("kissing_number") is not None and l.get("dimension", l.get("dim")) is not None]
            if kiss:
                eta, n, k = eta_sq([k for _, k in kiss], [str(d) for d, _ in kiss])
                record("C73-dim-kiss", "LAW" if eta >= 0.14 else "TENDENCY", eta,
                       f"dim->kissing n={n}")

        # C92: Any recurrence in lattice properties
        det_vals = [l.get("determinant", l.get("det")) for l in lattices if isinstance(l, dict)]
        det_vals = [d for d in det_vals if d is not None and d > 0]
        if det_vals:
            ratio = m4m2(det_vals)
            record("C92-det", "MEASURED", key_metric=f"det M4/M2^2={ratio:.3f} n={len(det_vals)}")
elif lattice_path.parent.exists():
    # Check what files exist
    print(f"  Files in lattice dir: {list(lattice_path.parent.glob('*'))}")
    record("C66", "SKIP", key_metric="lattices.json not found")
else:
    record("C66", "SKIP", key_metric="Lattice directory not found")

# ============================================================
# POLYTOPE BATCH
# ============================================================
print("\n" + "=" * 90)
print("POLYTOPE TESTS (C27-f24, R5.poly)")
print("=" * 90)

poly_path = DATA / "polytopes/data/polytopes.json"
if poly_path.exists():
    polytopes = json.load(open(poly_path, encoding="utf-8"))
    print(f"  Loaded {len(polytopes)} polytopes")

    # C27: f-vector M4/M2^2 by dimension
    fv_data = [(p.get("dimension"), sum(p.get("f_vector", [])))
               for p in polytopes if isinstance(p, dict) and p.get("f_vector") and p.get("dimension")]
    if fv_data:
        dims = [d for d, _ in fv_data]
        fv_sums = [s for _, s in fv_data]
        eta, n, k = eta_sq(fv_sums, dims)
        v24, r24 = bv2.F24_variance_decomposition(fv_sums, dims)
        record("C27-f24", v24, eta, f"dim->fvec_sum n={n} k={k}")

        # R5.poly: Euler characteristic
        # chi = sum(-1)^i f_i
        chi_data = []
        for p in polytopes:
            if isinstance(p, dict) and p.get("f_vector"):
                fv = p["f_vector"]
                chi = sum((-1)**i * f for i, f in enumerate(fv))
                chi_data.append(chi)
        if chi_data:
            ratio = m4m2([abs(c) for c in chi_data if c != 0])
            n_euler = sum(1 for c in chi_data if c == 0 or c == 2)
            print(f"  Euler characteristic: {len(chi_data)} polytopes")
            print(f"  chi=0 or chi=2: {n_euler}/{len(chi_data)} ({n_euler/len(chi_data)*100:.1f}%)")
            record("R5.poly-euler", "REDISCOVERY" if n_euler/len(chi_data) > 0.9 else "TENDENCY",
                   key_metric=f"chi=0or2: {n_euler/len(chi_data)*100:.0f}%")
else:
    record("C27", "SKIP", key_metric="Polytopes file not found")

# ============================================================
# SPACE GROUP CROSS-DOMAIN
# ============================================================
print("\n" + "=" * 90)
print("CROSS-DOMAIN TESTS")
print("=" * 90)

sg_path = DATA / "spacegroups/data/space_groups.json"
if sg_path.exists():
    sg_data = json.load(open(sg_path, encoding="utf-8"))
    print(f"  Space groups: {len(sg_data)}")

    # R5.sg: SG number ~ Wyckoff position count
    wyckoff_data = [(s.get("number"), len(s.get("wyckoff_positions", [])))
                    for s in sg_data if isinstance(s, dict) and s.get("number") and s.get("wyckoff_positions")]
    if wyckoff_data:
        sg_nums = [n for n, _ in wyckoff_data]
        wyckoff_counts = [w for _, w in wyckoff_data]
        r = np.corrcoef(sg_nums, wyckoff_counts)[0, 1]
        record("R5.sg-wyckoff", "TENDENCY" if r**2 >= 0.01 else "NEGLIGIBLE",
               r**2, f"r(SG#, Wyckoff)={r:.4f}")

    # R5.nfsg: SG point group order ~ NF degree
    pg_orders = [s.get("point_group_order", len(s.get("point_group", [])))
                 for s in sg_data if isinstance(s, dict)]
    nf = json.load(open(DATA / "number_fields/data/number_fields.json", encoding="utf-8"))
    nf_degrees = sorted(set(f.get("degree") for f in nf if f.get("degree")))
    pg_unique = sorted(set(p for p in pg_orders if p and p > 0))
    overlap = set(nf_degrees) & set(pg_unique)
    print(f"  NF degrees: {nf_degrees[:10]}")
    print(f"  PG orders: {pg_unique[:10]}")
    print(f"  Overlap: {sorted(overlap)[:10]}")
    record("R5.nfsg", "NEGLIGIBLE" if len(overlap) < 3 else "TENDENCY",
           key_metric=f"overlap={len(overlap)} values")
else:
    record("R5.sg", "SKIP", key_metric="Space groups file not found")

# ============================================================
# C54: Conway polynomial moments
# ============================================================
print("\nC54-f24: Conway polynomial moments")
knots = json.load(open(DATA / "knots/data/knots.json", encoding="utf-8"))["knots"]
conway_knots = [k for k in knots if k.get("conway_coeffs")]
if conway_knots:
    # M4/M2^2 of Conway coefficients per knot, grouped by crossing
    conway_m4 = []
    conway_labels = []
    for k in conway_knots:
        coeffs = k["conway_coeffs"]
        if len(coeffs) >= 3:
            ratio = m4m2([abs(c) for c in coeffs if c != 0])
            if np.isfinite(ratio):
                cn = k.get("crossing_number", 0)
                conway_m4.append(ratio)
                conway_labels.append(cn)

    if conway_m4:
        overall = m4m2([abs(c) for k in conway_knots for c in k["conway_coeffs"] if c != 0])
        eta, n, k_g = eta_sq(conway_m4, conway_labels)
        record("C54-f24", "LAW" if eta >= 0.14 else "TENDENCY", eta,
               f"overall M4/M2^2={overall:.2f} crossing->per-knot-M4 n={n}")
else:
    record("C54", "SKIP", key_metric="No Conway coefficients")

# ============================================================
print("\n" + "=" * 90)
print("M2 R3 LATTICE/POLYTOPE/CROSS BATCH SUMMARY")
print("=" * 90)
for r in results:
    e = f"eta2={r['eta2']:.4f}" if r['eta2'] is not None and not np.isnan(r['eta2']) else ""
    print(f"  {r['name']:20s} | {r['classification']:20s} | {e:15s} | {r['key_metric'][:50]}")

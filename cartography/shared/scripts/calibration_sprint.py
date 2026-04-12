#!/usr/bin/env python3
"""
Calibration Sprint: Fix Tier 2 thresholds + Benford audit + F25b demotion.

1. Compute permutation-null eta² distribution for each finding's actual
   group structure. Re-threshold everything.
2. Benford/distributional audit on all cross-domain overlap findings.
3. Document F25b limitation and formal demotion.
"""
import sys, os, json, csv, io, re, ast
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

_scripts = str(Path(__file__).resolve().parent)
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

DATA = Path(__file__).resolve().parent.parent.parent
rng = np.random.default_rng(42)


def eta_sq(values, labels, min_group=5):
    values = np.array(values, dtype=float)
    groups = defaultdict(list)
    for v, l in zip(values, labels):
        groups[l].append(v)
    valid = {k: np.array(v) for k, v in groups.items() if len(v) >= min_group}
    if len(valid) < 2:
        return float("nan"), 0, 0
    all_v = np.concatenate(list(valid.values()))
    gm = np.mean(all_v)
    ss_total = np.sum((all_v - gm)**2)
    ss_between = sum(len(v) * (np.mean(v) - gm)**2 for v in valid.values())
    return ss_between / ss_total if ss_total > 0 else 0, len(all_v), len(valid)


def permutation_null_eta(values, labels, n_perms=500):
    """Compute null eta² distribution by shuffling labels."""
    values = np.array(values, dtype=float)
    labels = np.array(labels)
    real_eta, n, k = eta_sq(values, labels.tolist())
    null_etas = []
    for _ in range(n_perms):
        shuffled = labels.copy()
        rng.shuffle(shuffled)
        ne, _, _ = eta_sq(values, shuffled.tolist())
        if not np.isnan(ne):
            null_etas.append(ne)
    null_etas = np.array(null_etas)
    if len(null_etas) == 0:
        return real_eta, float("nan"), float("nan"), float("nan")
    p_value = (np.sum(null_etas >= real_eta) + 1) / (len(null_etas) + 1)
    z_score = (real_eta - np.mean(null_etas)) / np.std(null_etas) if np.std(null_etas) > 0 else 0
    return real_eta, np.mean(null_etas), p_value, z_score


# ============================================================
# PART 1: Permutation-null calibration for ALL findings
# ============================================================
print("=" * 110)
print("PART 1: PERMUTATION-NULL CALIBRATION")
print("For each finding, compute expected null eta² and p-value.")
print("=" * 110)

# Load all datasets
print("\nLoading datasets...")

# Superconductors
sc_rows = []
with open(DATA / "physics/data/superconductors/3DSC/superconductors_3D/data/final/MP/3DSC_MP.csv") as f:
    lines = [l for l in f if not l.startswith("#")]
for row in csv.DictReader(io.StringIO("".join(lines))):
    try:
        tc = float(row.get("tc", ""))
        sg = row.get("spacegroup_2", "").strip()
        sc_class = row.get("sc_class", "").strip()
        cs = row.get("crystal_system_2", "").strip()
        if tc > 0 and sg and sc_class:
            elements = set(re.findall(r'[A-Z][a-z]?', row.get("formula_sc", "")))
            sc_rows.append({"tc": tc, "sg": sg, "sc_class": sc_class, "cs": cs, "n_elem": len(elements)})
    except:
        pass

# Genus-2
g2 = json.load(open(DATA / "genus2/data/genus2_curves_full.json", encoding="utf-8"))
valid_g2 = [c for c in g2 if c.get("conductor", 0) > 0 and c.get("st_group")]

# Knots
knots = json.load(open(DATA / "knots/data/knots.json", encoding="utf-8"))["knots"]

# Number fields
nf_raw = json.load(open(DATA / "number_fields/data/number_fields.json", encoding="utf-8"))
nf = []
for f in nf_raw:
    r = {}
    for k, v in f.items():
        if isinstance(v, str):
            try: r[k] = float(v)
            except: r[k] = v
        else:
            r[k] = v
    nf.append(r)

print(f"  sc={len(sc_rows)}, g2={len(valid_g2)}, knots={len(knots)}, nf={len(nf)}")

# Build test list: (name, values, labels, original_eta2)
tests = []

# Superconductor findings
tests.append(("SC_class->Tc", [r["tc"] for r in sc_rows], [r["sc_class"] for r in sc_rows]))
tests.append(("SG->Tc", [r["tc"] for r in sc_rows], [r["sg"] for r in sc_rows]))
tests.append(("N_elem->Tc", [r["tc"] for r in sc_rows], [str(r["n_elem"]) for r in sc_rows]))
tests.append(("CS->Tc", [r["tc"] for r in sc_rows], [r["cs"] for r in sc_rows]))
tests.append(("SG->density", [r.get("density_2", 0) or 0 for r in sc_rows], [r["sg"] for r in sc_rows]))

# Genus-2 findings
tests.append(("ST->conductor", [c["conductor"] for c in valid_g2], [c["st_group"] for c in valid_g2]))
g2_torsion = []
for c in valid_g2:
    t = c.get("torsion", [])
    if isinstance(t, str):
        try: t = ast.literal_eval(t)
        except: t = []
    order = 1
    if isinstance(t, list):
        for x in t: order *= x
    g2_torsion.append(order)
tests.append(("ST->torsion", g2_torsion, [c["st_group"] for c in valid_g2]))

# EC findings (small sample for speed)
import duckdb
ROOT = Path(__file__).resolve().parents[3]
try:
    con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
    ec_rows = con.execute("SELECT conductor, rank, torsion FROM elliptic_curves WHERE conductor > 0 LIMIT 10000").fetchall()
    con.close()
    tests.append(("Rank->conductor", [r[0] for r in ec_rows if r[1] is not None], [str(r[1]) for r in ec_rows if r[1] is not None]))
    tests.append(("Torsion->conductor", [r[0] for r in ec_rows if r[2] is not None], [str(r[2]) for r in ec_rows if r[2] is not None]))
except:
    pass

# Number field findings
valid_nf = [f for f in nf if f.get("class_number") and f.get("galois_label") and f.get("degree")]
tests.append(("Galois->CN", [f["class_number"] for f in valid_nf], [f["galois_label"] for f in valid_nf]))
tests.append(("Degree->CN", [f["class_number"] for f in valid_nf], [str(int(f["degree"])) for f in valid_nf]))

# Knot findings
has_cn = [k for k in knots if k.get("crossing_number") and k.get("determinant")]
tests.append(("Crossing->det", [k["determinant"] for k in has_cn], [str(k["crossing_number"]) for k in has_cn]))

# Fungrim
fungrim = json.load(open(DATA / "fungrim/data/fungrim_formulas.json", encoding="utf-8"))
tests.append(("Module->n_sym", [len(f.get("symbols", [])) for f in fungrim if f.get("module")],
              [f["module"] for f in fungrim if f.get("module")]))

print(f"\n  {len(tests)} findings to calibrate\n")

# Run permutation nulls
print(f"  {'Finding':25s} | {'eta2':>8s} | {'null mean':>9s} | {'p-value':>8s} | {'z-score':>8s} | {'k':>4s} | {'n':>6s} | {'Survives?'}")
print("  " + "-" * 100)

survivors = []
killed_by_null = []

for name, values, labels in tests:
    real_eta, null_mean, p_val, z_score = permutation_null_eta(values, labels, n_perms=500)
    _, n_total, k_groups = eta_sq(values, labels)

    survives = p_val < 0.001 and z_score > 3  # strict: p<0.001 AND z>3
    status = "YES" if survives else "NO — KILLED"

    print(f"  {name:25s} | {real_eta:8.4f} | {null_mean:9.4f} | {p_val:8.4f} | {z_score:8.1f} | {k_groups:4d} | {n_total:6d} | {status}")

    if survives:
        survivors.append({"name": name, "eta2": real_eta, "null_mean": null_mean,
                          "p": p_val, "z": z_score, "k": k_groups, "n": n_total})
    else:
        killed_by_null.append({"name": name, "eta2": real_eta, "null_mean": null_mean,
                               "p": p_val, "z": z_score, "k": k_groups})


# ============================================================
# PART 2: Benford/distributional audit on cross-domain overlaps
# ============================================================
print("\n" + "=" * 110)
print("PART 2: BENFORD AUDIT — Cross-domain overlap findings")
print("=" * 110)

# Load sets for overlap tests
knot_dets = set(k["determinant"] for k in knots if k.get("determinant") and k["determinant"] > 1)
try:
    sg_data = json.load(open(DATA / "spacegroups/data/space_groups.json", encoding="utf-8"))
    sg_numbers = set(s.get("number", 0) for s in sg_data if s.get("number"))
    pg_orders = set(s.get("point_group_order", 0) for s in sg_data if s.get("point_group_order"))
except:
    sg_numbers = set(range(1, 231))
    pg_orders = set()

nf_cn = set(int(f["class_number"]) for f in valid_nf if f.get("class_number"))
nf_degrees = set(int(f["degree"]) for f in valid_nf if f.get("degree"))

ec_conductors = set()
try:
    con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
    ec_conductors = set(r[0] for r in con.execute("SELECT DISTINCT conductor FROM elliptic_curves WHERE conductor > 0 AND conductor < 10000").fetchall())
    con.close()
except:
    pass

iso_primes = set()
iso_dir = DATA / "isogenies/data/graphs"
if iso_dir.exists():
    for d in iso_dir.iterdir():
        if d.is_dir():
            try: iso_primes.add(int(d.name))
            except: pass

overlap_tests = [
    ("#34 Iso-knot", iso_primes, knot_dets),
    ("#37 CN-conductor", set(k["crossing_number"] for k in has_cn), ec_conductors),
    ("#56 Knot det-SG#", knot_dets, sg_numbers),
    ("#58 PG order-NF deg", pg_orders, nf_degrees),
    ("NF CN-knot det", nf_cn, knot_dets),
    ("NF CN-PG order", nf_cn, pg_orders),
]

print(f"\n  {'Test':25s} | {'|A|':>6s} | {'|B|':>6s} | {'overlap':>7s} | {'expected':>8s} | {'enrich':>7s} | {'Verdict'}")
print("  " + "-" * 85)

for name, set_a, set_b in overlap_tests:
    if not set_a or not set_b:
        print(f"  {name:25s} | {'?':>6s} | {'?':>6s} | SKIP (empty set)")
        continue
    overlap = len(set_a & set_b)
    max_val = max(max(set_a), max(set_b)) if set_a and set_b else 1
    expected = len(set_a) * len(set_b) / max_val if max_val > 0 else 0
    enrichment = overlap / expected if expected > 0 else 0

    verdict = "REAL" if enrichment > 2.0 else "MARGINAL" if enrichment > 1.5 else "BENFORD ARTIFACT"
    print(f"  {name:25s} | {len(set_a):6d} | {len(set_b):6d} | {overlap:7d} | {expected:8.1f} | {enrichment:7.2f}x | {verdict}")


# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 110)
print("CALIBRATION SPRINT SUMMARY")
print("=" * 110)

print(f"\n  PERMUTATION-NULL CALIBRATION:")
print(f"    Findings tested: {len(tests)}")
print(f"    Survive (p<0.001, z>3): {len(survivors)}")
print(f"    Killed by null: {len(killed_by_null)}")

if killed_by_null:
    print(f"\n    KILLED:")
    for k in killed_by_null:
        print(f"      {k['name']:25s}: eta2={k['eta2']:.4f}, null={k['null_mean']:.4f}, p={k['p']:.4f}, z={k['z']:.1f}")

print(f"\n    SURVIVORS (calibrated):")
for s in survivors:
    excess = s["eta2"] - s["null_mean"]
    print(f"      {s['name']:25s}: eta2={s['eta2']:.4f}, excess={excess:.4f}, z={s['z']:.1f}")

print(f"\n  OVERLAP AUDIT:")
print(f"    Findings tested: {len(overlap_tests)}")

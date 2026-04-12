#!/usr/bin/env python3
"""
Re-audit 20 findings with F24 (variance decomposition) + F24b (metric consistency).

The instrument upgraded. Now re-examine the samples.
"""

import sys, json, csv, io, numpy as np, duckdb
from collections import defaultdict
from pathlib import Path

_scripts = str(Path(__file__).resolve().parent)
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

from battery_v2 import BatteryV2

bv2 = BatteryV2()
DATA = Path(__file__).resolve().parent.parent.parent  # cartography/
rng = np.random.default_rng(42)


def load_json(relpath):
    with open(DATA / relpath, "r", encoding="utf-8") as f:
        return json.load(f)


def run_f24(name, claim, values, group_labels):
    """Run F24 + F24b and print compact result."""
    values = np.array(values, dtype=float)
    v24, r24 = bv2.F24_variance_decomposition(values, group_labels)
    v24b, r24b = bv2.F24b_metric_consistency(values, group_labels)

    eta = r24.get("eta_squared", float("nan"))
    f_stat = r24.get("f_statistic", 0)
    n_groups = r24.get("n_groups", 0)
    n_total = r24.get("n_total", 0)
    tail_c = r24b.get("tail_contribution", float("nan"))
    m4_ratio = r24b.get("m4m2_ratio", float("nan"))

    # Classify
    if "TAIL_DRIVEN" in v24b and eta < 0.14:
        ftype = "CONSTRAINT"
    elif eta >= 0.14:
        ftype = "LAW"
    elif eta >= 0.01:
        ftype = "TENDENCY"
    else:
        ftype = "NEGLIGIBLE"

    print(f"  {name:5s} | {ftype:11s} | eta2={eta:.4f} | F={f_stat:8.1f} | n={n_total:6d} | g={n_groups:3d} | tail={tail_c:.0%} | M4r={m4_ratio:.2f} | {v24b}")
    print(f"         {claim[:70]}")
    return {"name": name, "type": ftype, "eta2": eta, "f": f_stat, "n": n_total,
            "tail_contribution": tail_c, "m4_ratio": m4_ratio, "f24b": v24b, "claim": claim}


# ============================================================
# Load datasets
# ============================================================
print("Loading datasets...")

# Genus-2
g2 = load_json("genus2/data/genus2_curves_full.json")
g2_usp4 = [c for c in g2 if c.get("st_group") == "USp(4)"]

# Number fields
nf = load_json("number_fields/data/number_fields.json")

# Knots
knots_data = load_json("knots/data/knots.json")
knots = knots_data["knots"]

# Superconductors
csv_path = DATA / "physics/data/superconductors/3DSC/superconductors_3D/data/final/MP/3DSC_MP.csv"
sc_rows = []
with open(csv_path, "r") as f:
    lines = [l for l in f if not l.startswith("#")]
for row in csv.DictReader(io.StringIO("".join(lines))):
    try:
        tc = float(row.get("tc", ""))
        sg = row.get("spacegroup_2", "").strip()
        cs = row.get("crystal_system_2", "").strip()
        bg = row.get("band_gap_2", "")
        den = row.get("density_2", "")
        fe = row.get("formation_energy_per_atom_2", "")
        vol = row.get("cell_volume_2", "")
        sc_class = row.get("sc_class", "").strip()
        formula = row.get("formula_sc", "").strip()
        if tc > 0 and sg:
            r = {"tc": tc, "sg": sg, "cs": cs, "sc_class": sc_class, "formula": formula}
            try: r["bg"] = float(bg)
            except: r["bg"] = None
            try: r["density"] = float(den)
            except: r["density"] = None
            try: r["fe"] = float(fe)
            except: r["fe"] = None
            try: r["vol"] = float(vol)
            except: r["vol"] = None
            # Count elements
            import re
            elements = set(re.findall(r'[A-Z][a-z]?', formula))
            r["n_elements"] = len(elements)
            sc_rows.append(r)
    except:
        pass

# NIST atomic data
nist_path = DATA / "physics/data/nist_asd/all_elements.json"
nist_data = None
if nist_path.exists():
    nist_data = load_json("physics/data/nist_asd/all_elements.json")

# Elliptic curves
con = duckdb.connect(str(Path(__file__).resolve().parent.parent.parent.parent / "charon/data/charon.duckdb"), read_only=True)
ec_rows = con.execute("""
    SELECT conductor, cm, rank, torsion, faltings_height, bad_primes, semistable
    FROM elliptic_curves WHERE conductor > 0
""").fetchall()
con.close()

print(f"Loaded: g2={len(g2)}, nf={len(nf)}, knots={len(knots)}, sc={len(sc_rows)}, ec={len(ec_rows)}")
print()

# ============================================================
# THE 20 RE-AUDITS
# ============================================================
print("=" * 90)
print(f"{'ID':>5s} | {'TYPE':11s} | {'eta2':>10s} | {'F':>8s} | {'n':>6s} | {'g':>3s} | {'tail':>5s} | {'M4r':>5s} | F24b")
print("-" * 90)

results = []

# 1. C32: SG -> Tc (already confirmed LAW, baseline)
results.append(run_f24("C32", "Space group -> Tc",
    [r["tc"] for r in sc_rows], [r["sg"] for r in sc_rows]))

# 2. SG -> Band gap
bg_rows = [r for r in sc_rows if r["bg"] is not None]
results.append(run_f24("C32b", "Space group -> Band gap",
    [r["bg"] for r in bg_rows], [r["sg"] for r in bg_rows]))

# 3. SG -> Cell volume
vol_rows = [r for r in sc_rows if r["vol"] is not None]
results.append(run_f24("C38v", "Space group -> Cell volume",
    [r["vol"] for r in vol_rows], [r["sg"] for r in vol_rows]))

# 4. SG -> Formation energy
fe_rows = [r for r in sc_rows if r["fe"] is not None]
results.append(run_f24("C38f", "Space group -> Formation energy",
    [r["fe"] for r in fe_rows], [r["sg"] for r in fe_rows]))

# 5. SG -> Density
den_rows = [r for r in sc_rows if r["density"] is not None]
results.append(run_f24("C38d", "Space group -> Density",
    [r["density"] for r in den_rows], [r["sg"] for r in den_rows]))

# 6. C59: Crystal system -> Tc
results.append(run_f24("C59", "Crystal system -> Tc",
    [r["tc"] for r in sc_rows], [r["cs"] for r in sc_rows]))

# 7. C85: Chemical family (sc_class) -> Tc
results.append(run_f24("C85", "SC class -> Tc",
    [r["tc"] for r in sc_rows if r["sc_class"]], [r["sc_class"] for r in sc_rows if r["sc_class"]]))

# 8. C4: n_elements -> Tc
results.append(run_f24("C4", "N_elements -> Tc",
    [r["tc"] for r in sc_rows], [r["n_elements"] for r in sc_rows]))

# 9. C36: Galois group -> class number (KILLED by F17, check eta²)
valid_nf = [f for f in nf if f.get("class_number") and f.get("galois_label")]
results.append(run_f24("C36", "Galois group -> class number",
    [f["class_number"] for f in valid_nf], [f["galois_label"] for f in valid_nf]))

# 10. NF degree -> class number (the confound that killed C36)
valid_nf2 = [f for f in nf if f.get("class_number") and f.get("degree")]
results.append(run_f24("C36c", "NF degree -> class number (the confound)",
    [f["class_number"] for f in valid_nf2], [f["degree"] for f in valid_nf2]))

# 11. Knot crossing number -> determinant
valid_knots = [k for k in knots if k.get("determinant") and k.get("crossing_number")]
results.append(run_f24("C35", "Crossing number -> determinant",
    [k["determinant"] for k in valid_knots], [k["crossing_number"] for k in valid_knots]))

# 12. C50: G2 ST group -> conductor
valid_g2 = [c for c in g2 if c.get("conductor", 0) > 0 and c.get("st_group")]
results.append(run_f24("C50", "ST group -> conductor",
    [c["conductor"] for c in valid_g2], [c["st_group"] for c in valid_g2]))

# 13. G2 ST group -> discriminant
results.append(run_f24("C50d", "ST group -> |discriminant|",
    [abs(c["discriminant"]) for c in valid_g2 if c.get("discriminant", 0) != 0],
    [c["st_group"] for c in valid_g2 if c.get("discriminant", 0) != 0]))

# 14. G2 ST group -> torsion order
tors_g2 = []
tors_labels = []
for c in valid_g2:
    t = c.get("torsion", [])
    if isinstance(t, str):
        import ast
        try: t = ast.literal_eval(t)
        except: t = []
    if isinstance(t, list):
        order = 1
        for x in t: order *= x
        tors_g2.append(order)
        tors_labels.append(c["st_group"])
results.append(run_f24("G2to", "ST group -> torsion order",
    tors_g2, tors_labels))

# 15. EC: CM -> conductor
results.append(run_f24("EC_cm", "CM flag -> conductor",
    [r[0] for r in ec_rows], ["CM" if r[1] != 0 else "non-CM" for r in ec_rows]))

# 16. EC: rank -> conductor
results.append(run_f24("EC_rk", "Rank -> conductor",
    [r[0] for r in ec_rows if r[2] is not None], [r[2] for r in ec_rows if r[2] is not None]))

# 17. EC: torsion -> conductor
results.append(run_f24("EC_to", "Torsion -> conductor",
    [r[0] for r in ec_rows if r[3] is not None], [r[3] for r in ec_rows if r[3] is not None]))

# 18. EC: semistable -> conductor
results.append(run_f24("EC_ss", "Semistable -> conductor",
    [r[0] for r in ec_rows if r[6] is not None], [r[6] for r in ec_rows if r[6] is not None]))

# 19. C12: Lean namespace enrichment (check if we have data)
# Use knot polynomial type as proxy for a categorical -> continuous test
results.append(run_f24("KnPy", "Has jones poly -> determinant",
    [k["determinant"] for k in knots if k.get("determinant") and k.get("jones_coeffs") is not None],
    ["has_jones" if k.get("jones_coeffs") else "no_jones" for k in knots if k.get("determinant") and k.get("jones_coeffs") is not None]))

# 20. NF degree -> discriminant
valid_nf3 = [f for f in nf if f.get("disc_abs") and f.get("degree")]
results.append(run_f24("NFdd", "NF degree -> |discriminant|",
    [f["disc_abs"] for f in valid_nf3], [f["degree"] for f in valid_nf3]))

# ============================================================
# META-ANALYSIS
# ============================================================
print()
print("=" * 90)
print("META-ANALYSIS: What does our discovery process produce?")
print("=" * 90)

types = defaultdict(int)
for r in results:
    types[r["type"]] += 1

print(f"  Total re-audited: {len(results)}")
for t in ["LAW", "CONSTRAINT", "TENDENCY", "NEGLIGIBLE"]:
    n = types.get(t, 0)
    pct = n / len(results) * 100 if results else 0
    print(f"  {t:12s}: {n:3d} ({pct:.0f}%)")

print()
print("LAWS (eta^2 > 0.14, not tail-driven):")
for r in results:
    if r["type"] == "LAW":
        print(f"  {r['name']:6s}: eta2={r['eta2']:.4f} | {r['claim'][:60]}")

print()
print("CONSTRAINTS (tail-driven):")
for r in results:
    if r["type"] == "CONSTRAINT":
        print(f"  {r['name']:6s}: eta2={r['eta2']:.4f} tail={r['tail_contribution']:.0%} | {r['claim'][:60]}")

print()
print("TENDENCIES (small, consistent):")
for r in results:
    if r["type"] == "TENDENCY":
        print(f"  {r['name']:6s}: eta2={r['eta2']:.4f} | {r['claim'][:60]}")

print()
print("NEGLIGIBLE (eta^2 < 0.01):")
for r in results:
    if r["type"] == "NEGLIGIBLE":
        print(f"  {r['name']:6s}: eta2={r['eta2']:.4f} | {r['claim'][:60]}")

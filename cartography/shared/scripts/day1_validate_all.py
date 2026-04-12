#!/usr/bin/env python3
"""Day 1 validation: F24 permutation + F25c shrinkage + CrossDomainProtocol."""
import sys, os, json, csv, io
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
from cross_domain_protocol import CrossDomainProtocol

bv2 = BatteryV2()
cdp = CrossDomainProtocol(bv2)
DATA = Path(__file__).resolve().parent.parent.parent
ROOT = Path(__file__).resolve().parents[3]
rng = np.random.default_rng(42)

# Load SC data
sc_rows = []
with open(DATA / "physics/data/superconductors/3DSC/superconductors_3D/data/final/MP/3DSC_MP.csv") as f:
    lines = [l for l in f if not l.startswith("#")]
for row in csv.DictReader(io.StringIO("".join(lines))):
    try:
        tc = float(row.get("tc", ""))
        sg = row.get("spacegroup_2", "").strip()
        sc_class = row.get("sc_class", "").strip()
        if tc > 0 and sg and sc_class:
            sc_rows.append({"tc": tc, "sg": sg, "sc_class": sc_class})
    except: pass

tc_all = [r["tc"] for r in sc_rows]
sg_all = [r["sg"] for r in sc_rows]
sc_cls = [r["sc_class"] for r in sc_rows]

print("=" * 90)
print("DAY 1 VALIDATION: F24 permutation + F25c shrinkage + CrossDomainProtocol")
print("=" * 90)

# ============================================================
# 1a: F24 permutation calibration
# ============================================================
print("\n--- 1a: F24 PERMUTATION CALIBRATION ---")

# Real findings
for name, vals, labs in [("SC_class->Tc", tc_all, sc_cls), ("SG->Tc", tc_all, sg_all)]:
    v, r = bv2.F24_variance_decomposition(vals, labs, permutation_calibrate=True, n_perms=500)
    perm = r.get("permutation_null", {})
    print(f"  {name:20s}: eta2={r['eta_squared']:.4f}, null={perm.get('null_mean',0):.4f}, "
          f"z={perm.get('z_score',0):.1f}, perm_verdict={r.get('perm_verdict','N/A')}")

# Junk data
junk_vals = list(rng.normal(0, 1, 4000))
junk_labs = [f"g{i}" for i in rng.choice(50, 4000)]
v_junk, r_junk = bv2.F24_variance_decomposition(junk_vals, junk_labs, permutation_calibrate=True, n_perms=500)
perm_junk = r_junk.get("permutation_null", {})
print(f"  {'JUNK (50 groups)':20s}: eta2={r_junk['eta_squared']:.4f}, null={perm_junk.get('null_mean',0):.4f}, "
      f"z={perm_junk.get('z_score',0):.1f}, perm_verdict={r_junk.get('perm_verdict','N/A')}")

# ============================================================
# 1b: F25c shrinkage transportability
# ============================================================
print("\n--- 1b: F25c SHRINKAGE TRANSPORTABILITY ---")

# Synthetic interaction
n_syn = 3000
class_labels = list(rng.choice([f"c{i}" for i in range(5)], n_syn))
struct_labels = list(rng.choice([f"s{i}" for i in range(20)], n_syn))
class_eff = {f"c{i}": rng.normal(0, 10) for i in range(5)}
struct_eff = {f"s{i}": rng.normal(0, 5) for i in range(20)}
inter_eff = {(c, s): rng.normal(0, 3) for c in class_eff for s in struct_eff}

y_inter = [class_eff[c] + struct_eff[s] + inter_eff[(c,s)] + rng.normal(0, 2)
           for c, s in zip(class_labels, struct_labels)]
y_additive = [class_eff[c] + struct_eff[s] + rng.normal(0, 2)
              for c, s in zip(class_labels, struct_labels)]

# Test F25c
for name, y, expected in [
    ("Interaction class->y", y_inter, "UNIVERSAL (strong main)"),
    ("Interaction struct->y", y_inter, "CONDITIONAL or WEAK"),
    ("Additive class->y", y_additive, "UNIVERSAL"),
    ("Additive struct->y", y_additive, "UNIVERSAL or WEAK"),
]:
    if "class" in name:
        v, r = bv2.F25c_shrinkage_transportability(y, class_labels, struct_labels)
    else:
        v, r = bv2.F25c_shrinkage_transportability(y, struct_labels, class_labels)
    main_r2 = r.get("weighted_r2_main", 0)
    inter_r2 = r.get("weighted_r2_interaction", 0)
    print(f"  {name:30s}: {v:15s} main={main_r2:.4f} inter={inter_r2:.4f} (expected: {expected})")

# Real SG->Tc
v_sg, r_sg = bv2.F25c_shrinkage_transportability(tc_all, sg_all, sc_cls)
print(f"  {'Real SG->Tc':30s}: {v_sg:15s} main={r_sg.get('weighted_r2_main',0):.4f} inter={r_sg.get('weighted_r2_interaction',0):.4f}")

# Deuring with fragmentation
iso_dir = DATA / "isogenies/data/graphs"
iso_n = []
for d in iso_dir.iterdir():
    if d.is_dir():
        md = d / f"{d.name}_metadata.json"
        if md.exists():
            try:
                m = json.load(open(md))
                iso_n.append(m["nodes"])
            except: pass
if iso_n:
    dummy_200 = [str(i) for i in rng.choice(200, len(iso_n))]
    context = [str(i % 4) for i in range(len(iso_n))]
    v_d, r_d = bv2.F25c_shrinkage_transportability(iso_n, dummy_200, context)
    print(f"  {'Deuring 200 groups':30s}: {v_d:15s} main={r_d.get('weighted_r2_main',0):.4f}")

# ============================================================
# 1c: CrossDomainProtocol
# ============================================================
print("\n--- 1c: CROSS-DOMAIN PROTOCOL AUTOMATION ---")

# Load datasets for known kills
knots = json.load(open(DATA / "knots/data/knots.json", encoding="utf-8"))["knots"]
knot_dets = set(k["determinant"] for k in knots if k.get("determinant") and k["determinant"] > 1)

try:
    sg_data = json.load(open(DATA / "spacegroups/data/space_groups.json", encoding="utf-8"))
    sg_numbers = set(s.get("number", 0) for s in sg_data if s.get("number"))
    pg_orders = set(s.get("point_group_order", 0) for s in sg_data if s.get("point_group_order"))
except:
    sg_numbers = set(range(1, 231))
    pg_orders = set()

nf = json.load(open(DATA / "number_fields/data/number_fields.json", encoding="utf-8"))
nf_cn = set(int(float(f["class_number"])) for f in nf if f.get("class_number"))
nf_deg = set(int(float(f["degree"])) for f in nf if f.get("degree"))

import duckdb
con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
ec_cond = set(r[0] for r in con.execute("SELECT DISTINCT conductor FROM elliptic_curves WHERE conductor > 0 AND conductor < 10000").fetchall())
con.close()

maass = json.load(open(DATA / "maass/data/maass_with_coefficients.json", encoding="utf-8"))
maass_levels = set(m.get("level") for m in maass if m.get("level"))

iso_primes = set()
for d in iso_dir.iterdir():
    if d.is_dir():
        try: iso_primes.add(int(d.name))
        except: pass

tests = [
    ("#56 Knot det vs SG#", knot_dets, sg_numbers),
    ("#34 Iso vs knot det", iso_primes, knot_dets),
    ("#58 PG vs NF degree", pg_orders, nf_deg),
    ("EC cond vs Maass lev", ec_cond, maass_levels),
    ("NF CN vs knot det", nf_cn, knot_dets),
    ("NF CN vs PG order", nf_cn, pg_orders),
]

kills = 0
for name, sa, sb in tests:
    verdict, layers = cdp.test(sa, sb, domain_a=name.split()[0], domain_b=name.split()[-1])
    killed = "KILLED" in verdict
    kills += killed
    print(f"  {name:30s}: {verdict:30s} {'CORRECT' if killed else 'MISSED'}")

print(f"\n  Kills reproduced: {kills}/{len(tests)}")
print(f"  {'ALL KILLS REPRODUCED — PASS' if kills == len(tests) else f'MISSED {len(tests)-kills} — FAIL'}")

print("\n" + "=" * 90)
print("DAY 1 VALIDATION COMPLETE")
print("=" * 90)

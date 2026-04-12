#!/usr/bin/env python3
"""
F25b Validation: Does model-based transportability fix the synthetic failure?
Then: retest SG × SC_class → Tc with the corrected test.

Expected outcomes:
  Synthetic interaction:  class→y UNIVERSAL (strong main), struct→y WEAK_NOISY (not conditional)
  Synthetic additive:     both UNIVERSAL
  Real SG→Tc:            the honest answer (CONDITIONAL or WEAK_NOISY?)
"""
import sys, os, json, csv, io, re
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
    if len(valid) < 2:
        return float("nan"), 0, 0
    all_v = np.concatenate(list(valid.values()))
    gm = np.mean(all_v)
    ss_total = np.sum((all_v - gm)**2)
    ss_between = sum(len(v) * (np.mean(v) - gm)**2 for v in valid.values())
    return ss_between / ss_total if ss_total > 0 else 0, len(all_v), len(valid)


# ============================================================
# PART 1: Validate F25b on synthetic data (the test that broke F25)
# ============================================================
print("=" * 100)
print("PART 1: F25b VALIDATION ON SYNTHETIC DATA")
print("=" * 100)

n_syn = 3000
n_classes = 5
n_structures = 20

class_labels = rng.choice([f"class_{i}" for i in range(n_classes)], n_syn)
struct_labels = rng.choice([f"struct_{i}" for i in range(n_structures)], n_syn)

class_effects = {f"class_{i}": rng.normal(0, 10) for i in range(n_classes)}
struct_effects = {f"struct_{i}": rng.normal(0, 5) for i in range(n_structures)}
interaction_effects = {(c, s): rng.normal(0, 3)
                       for c in class_effects for s in struct_effects}

# WITH interaction
y_inter = np.array([
    class_effects[c] + struct_effects[s] + interaction_effects[(c, s)] + rng.normal(0, 2)
    for c, s in zip(class_labels, struct_labels)
])

# WITHOUT interaction (pure additive)
y_additive = np.array([
    class_effects[c] + struct_effects[s] + rng.normal(0, 2)
    for c, s in zip(class_labels, struct_labels)
])

print(f"\n  Synthetic: n={n_syn}, {n_classes} classes (σ=10), {n_structures} structures (σ=5)")
print(f"  Interaction σ=3, noise σ=2\n")

# F25 (old) for comparison
print("  F25 (group-mean, OLD):")
v25_old_ci, r25_old_ci = bv2.F25_transportability(y_inter.tolist(), class_labels.tolist(), struct_labels.tolist())
v25_old_si, r25_old_si = bv2.F25_transportability(y_inter.tolist(), struct_labels.tolist(), class_labels.tolist())
v25_old_ca, r25_old_ca = bv2.F25_transportability(y_additive.tolist(), class_labels.tolist(), struct_labels.tolist())
v25_old_sa, r25_old_sa = bv2.F25_transportability(y_additive.tolist(), struct_labels.tolist(), class_labels.tolist())

print(f"    INTERACTION model:")
print(f"      class→y:  {v25_old_ci:20s} OOS R²={r25_old_ci.get('weighted_oos_r2', 0):.4f}")
print(f"      struct→y: {v25_old_si:20s} OOS R²={r25_old_si.get('weighted_oos_r2', 0):.4f}")
print(f"    ADDITIVE model:")
print(f"      class→y:  {v25_old_ca:20s} OOS R²={r25_old_ca.get('weighted_oos_r2', 0):.4f}")
print(f"      struct→y: {v25_old_sa:20s} OOS R²={r25_old_sa.get('weighted_oos_r2', 0):.4f}")

# F25b (new)
print(f"\n  F25b (model-based, NEW):")
v25b_ci, r25b_ci = bv2.F25b_model_transportability(y_inter.tolist(), class_labels.tolist(), struct_labels.tolist())
v25b_si, r25b_si = bv2.F25b_model_transportability(y_inter.tolist(), struct_labels.tolist(), class_labels.tolist())
v25b_ca, r25b_ca = bv2.F25b_model_transportability(y_additive.tolist(), class_labels.tolist(), struct_labels.tolist())
v25b_sa, r25b_sa = bv2.F25b_model_transportability(y_additive.tolist(), struct_labels.tolist(), class_labels.tolist())

print(f"    INTERACTION model:")
print(f"      class→y:  {v25b_ci:20s} main R²={r25b_ci.get('weighted_r2_main', 0):.4f}, inter R²={r25b_ci.get('weighted_r2_interaction', 0):.4f}")
print(f"      struct→y: {v25b_si:20s} main R²={r25b_si.get('weighted_r2_main', 0):.4f}, inter R²={r25b_si.get('weighted_r2_interaction', 0):.4f}")
print(f"    ADDITIVE model:")
print(f"      class→y:  {v25b_ca:20s} main R²={r25b_ca.get('weighted_r2_main', 0):.4f}, inter R²={r25b_ca.get('weighted_r2_interaction', 0):.4f}")
print(f"      struct→y: {v25b_sa:20s} main R²={r25b_sa.get('weighted_r2_main', 0):.4f}, inter R²={r25b_sa.get('weighted_r2_interaction', 0):.4f}")

# Verdict
print(f"\n  EXPECTED OUTCOMES:")
print(f"    Interaction model, class→y:   UNIVERSAL (strong main effect dominates)")
print(f"    Interaction model, struct→y:  CONDITIONAL (interaction blocks transfer)")
print(f"    Additive model, class→y:      UNIVERSAL")
print(f"    Additive model, struct→y:     UNIVERSAL (no interaction to block)")
print(f"\n  ACTUAL OUTCOMES (F25b):")
print(f"    Interaction model, class→y:   {v25b_ci}")
print(f"    Interaction model, struct→y:  {v25b_si}")
print(f"    Additive model, class→y:      {v25b_ca}")
print(f"    Additive model, struct→y:     {v25b_sa}")

# Score
correct = 0
total = 4
if v25b_ci == "UNIVERSAL": correct += 1
if v25b_si in ("CONDITIONAL", "WEAK_NOISY"): correct += 1  # either is acceptable
if v25b_ca == "UNIVERSAL": correct += 1
if v25b_sa in ("UNIVERSAL", "WEAKLY_TRANSFERABLE"): correct += 1
print(f"\n  SCORE: {correct}/{total} correct classifications")
if correct >= 3:
    print(f"  F25b PASSES synthetic validation.")
else:
    print(f"  F25b FAILS synthetic validation.")


# ============================================================
# PART 2: Retest SG × SC_class → Tc with F25b
# ============================================================
print("\n" + "=" * 100)
print("PART 2: SG × SC_class → Tc — THE REAL TEST")
print("Is this truly CONDITIONAL, or WEAK_NOISY?")
print("=" * 100)

csv_path = DATA / "physics/data/superconductors/3DSC/superconductors_3D/data/final/MP/3DSC_MP.csv"
sc_rows = []
with open(csv_path, "r") as f:
    lines = [l for l in f if not l.startswith("#")]
for row in csv.DictReader(io.StringIO("".join(lines))):
    try:
        tc = float(row.get("tc", ""))
        sg = row.get("spacegroup_2", "").strip()
        sc_class = row.get("sc_class", "").strip()
        if tc > 0 and sg and sc_class:
            sc_rows.append({"tc": tc, "sg": sg, "sc_class": sc_class})
    except:
        pass

tc = [r["tc"] for r in sc_rows]
sg = [r["sg"] for r in sc_rows]
sc_cls = [r["sc_class"] for r in sc_rows]

print(f"\n  {len(sc_rows)} superconductors")

# F25 (old) for reference
v25_sg, r25_sg = bv2.F25_transportability(tc, sg, sc_cls)
v25_sc, r25_sc = bv2.F25_transportability(tc, sc_cls, sg)
print(f"\n  F25 (old, group-mean):")
print(f"    SG→Tc across SC_class:     {v25_sg:20s} OOS R²={r25_sg.get('weighted_oos_r2', 0):.4f}")
print(f"    SC_class→Tc across SG:     {v25_sc:20s} OOS R²={r25_sc.get('weighted_oos_r2', 0):.4f}")

# F25b (new)
v25b_sg, r25b_sg = bv2.F25b_model_transportability(tc, sg, sc_cls)
v25b_sc, r25b_sc = bv2.F25b_model_transportability(tc, sc_cls, sg)
print(f"\n  F25b (model-based):")
print(f"    SG→Tc across SC_class:     {v25b_sg:20s} main R²={r25b_sg.get('weighted_r2_main', 0):.4f}, inter R²={r25b_sg.get('weighted_r2_interaction', 0):.4f}")
print(f"    SC_class→Tc across SG:     {v25b_sc:20s} main R²={r25b_sc.get('weighted_r2_main', 0):.4f}, inter R²={r25b_sc.get('weighted_r2_interaction', 0):.4f}")

# Per-group details for SG→Tc
print(f"\n  F25b SG→Tc per held-out class:")
for g in r25b_sg.get("per_group", []):
    print(f"    {g['held_out']:25s}: n={g['n']}, main R²={g['r2_a']:.4f}, inter R²={g['r2_b']:.4f}")

# Also test: NF Galois → class number across degree (the other conditional)
print(f"\n  --- Number field comparison ---")
nf = json.load(open(DATA / "number_fields/data/number_fields.json", encoding="utf-8"))
valid_nf = [f for f in nf if f.get("class_number") and f.get("galois_label") and f.get("degree")]
nf_cn = [f["class_number"] for f in valid_nf]
nf_gal = [f["galois_label"] for f in valid_nf]
nf_deg = [str(f["degree"]) for f in valid_nf]

v25b_gal, r25b_gal = bv2.F25b_model_transportability(nf_cn, nf_gal, nf_deg)
print(f"  F25b Galois→CN across degree: {v25b_gal:20s} main R²={r25b_gal.get('weighted_r2_main', 0):.4f}, inter R²={r25b_gal.get('weighted_r2_interaction', 0):.4f}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 100)
print("F25b VALIDATION SUMMARY")
print("=" * 100)
print(f"""
  SYNTHETIC VALIDATION: {correct}/{total} correct

  REAL DATA RECLASSIFICATION:
    SG→Tc (F25 old):         {v25_sg} (OOS R²={r25_sg.get('weighted_oos_r2', 0):.4f})
    SG→Tc (F25b new):        {v25b_sg} (main R²={r25b_sg.get('weighted_r2_main', 0):.4f}, inter R²={r25b_sg.get('weighted_r2_interaction', 0):.4f})

    SC_class→Tc (F25 old):   {v25_sc} (OOS R²={r25_sc.get('weighted_oos_r2', 0):.4f})
    SC_class→Tc (F25b new):  {v25b_sc} (main R²={r25b_sc.get('weighted_r2_main', 0):.4f}, inter R²={r25b_sc.get('weighted_r2_interaction', 0):.4f})

    Galois→CN (F25b):        {v25b_gal} (main R²={r25b_gal.get('weighted_r2_main', 0):.4f}, inter R²={r25b_gal.get('weighted_r2_interaction', 0):.4f})

  INTERPRETATION:
    If SG→Tc is CONDITIONAL under F25b: TRUE interaction (mapping genuinely changes)
    If SG→Tc is WEAK_NOISY under F25b: estimation noise, not true conditionality
    If SG→Tc is UNIVERSAL under F25b: the old F25 was wrong, SG transfers after all
""")

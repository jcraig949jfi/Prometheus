"""C21: Number field class number distribution shape.
Sharp degree-dependence. F24+F25 classification.
Battery v6. Machine: M1 (Skullport), 2026-04-12
"""
import sys, json
import numpy as np
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from battery_v2 import BatteryV2

DATA = Path(__file__).resolve().parent.parent.parent
bv2 = BatteryV2()

with open(DATA / "number_fields/data/number_fields.json") as f:
    fields = json.load(f)
print(f"Loaded {len(fields)} number fields")

records = []
for nf in fields:
    deg = nf["degree"]
    cn = int(nf["class_number"])
    gal = nf["galois_label"]
    disc = abs(int(nf["disc_abs"]))
    reg = float(nf["regulator"]) if nf["regulator"] not in ("", "0") else 0.0
    disc_sign = int(nf["disc_sign"])
    if deg >= 2 and cn >= 1:
        records.append({"degree": deg, "cn": cn, "galois": gal, "disc": disc,
                        "reg": reg, "log_cn": np.log(cn + 1), "disc_sign": disc_sign})

print(f"Records: {len(records)}")

cn_vals = np.array([r["cn"] for r in records], dtype=float)
log_cn = np.array([r["log_cn"] for r in records])
deg_labels = np.array([str(r["degree"]) for r in records])
gal_labels = np.array([r["galois"] for r in records])
disc_signs = np.array([r["disc_sign"] for r in records])

# --- Test 1: F24 - degree -> class number ---
print("\n" + "="*70)
print("TEST 1: F24 - degree -> class number")
print("="*70)
v1, r1 = bv2.F24_variance_decomposition(log_cn, deg_labels)
print(f"Verdict: {v1}, eta2 = {r1.get('eta_squared', 0):.4f}")
for label, gs in sorted(r1.get("group_stats", {}).items()):
    print(f"  Degree {label}: n={gs['n']}, mean log(h)={gs['mean']:.3f}, std={gs['std']:.3f}")

v1b, r1b = bv2.F24b_metric_consistency(log_cn, deg_labels)
print(f"F24b: {v1b}")

# --- Test 2: Class number distribution shape per degree ---
print("\n" + "="*70)
print("TEST 2: Class number distribution shape by degree")
print("="*70)

deg_array = np.array([r["degree"] for r in records])
from scipy import stats as sp_stats

for deg in sorted(set(deg_array)):
    mask = deg_array == deg
    cns = cn_vals[mask]
    if len(cns) < 30:
        continue
    h1_frac = np.mean(cns == 1)
    median_cn = np.median(cns)
    max_cn = np.max(cns)
    skew = sp_stats.skew(cns)
    print(f"  Degree {deg}: n={len(cns)}, h=1 frac={h1_frac:.3f}, median={median_cn:.0f}, max={max_cn:.0f}, skew={skew:.2f}")

# --- Test 3: F24 - discriminant sign -> class number ---
print("\n" + "="*70)
print("TEST 3: F24 - discriminant sign -> class number")
print("="*70)
sign_labels = np.array([str(r["disc_sign"]) for r in records])
v3, r3 = bv2.F24_variance_decomposition(log_cn, sign_labels)
print(f"Verdict: {v3}, eta2 = {r3.get('eta_squared', 0):.4f}")
for label, gs in sorted(r3.get("group_stats", {}).items()):
    print(f"  Sign {label}: n={gs['n']}, mean log(h)={gs['mean']:.3f}")

# --- Test 4: F25 - does degree->CN transfer across discriminant sign? ---
print("\n" + "="*70)
print("TEST 4: F25 - degree->CN transportability across disc sign")
print("="*70)
v4, r4 = bv2.F25_transportability(log_cn, deg_labels, sign_labels)
print(f"F25 verdict: {v4}")
if "weighted_oos_r2" in r4:
    print(f"Weighted OOS R2: {r4['weighted_oos_r2']:.4f}")

# --- Test 5: M4/M2 of class numbers per degree ---
print("\n" + "="*70)
print("TEST 5: M4/M2 of class number within each degree")
print("="*70)
for deg in sorted(set(deg_array)):
    mask = deg_array == deg
    cns = cn_vals[mask]
    if len(cns) < 30:
        continue
    normed = cns / np.mean(cns)
    m2 = np.mean(normed**2)
    m4 = np.mean(normed**4)
    ratio = m4 / (m2**2) if m2 > 0 else 0
    print(f"  Degree {deg}: n={len(cns)}, M4/M2={ratio:.4f}")

# --- Test 6: Class group structure ---
print("\n" + "="*70)
print("TEST 6: Class group rank by degree")
print("="*70)
for deg in sorted(set(deg_array)):
    mask = deg_array == deg
    deg_recs = [r for r, m in zip(records, mask) if m]
    # Class group structure from original data
    deg_fields = [nf for nf in fields if nf["degree"] == deg]
    ranks = []
    for nf in deg_fields:
        cg = nf.get("class_group", [])
        if isinstance(cg, list):
            ranks.append(len(cg))
    if ranks:
        print(f"  Degree {deg}: mean rank={np.mean(ranks):.2f}, max rank={max(ranks)}, frac rank 0={np.mean(np.array(ranks)==0):.3f}")

# --- Test 7: Brauer-Siegel ratio ---
print("\n" + "="*70)
print("TEST 7: Brauer-Siegel ratio log(h*R)/log(sqrt(|D|)) by degree")
print("="*70)
for deg in sorted(set(deg_array)):
    mask = deg_array == deg
    deg_recs = [r for r, m in zip(records, mask) if m]
    bs_ratios = []
    for r in deg_recs:
        if r["reg"] > 0 and r["disc"] > 1:
            log_hR = np.log(r["cn"] * r["reg"])
            log_sqrtD = 0.5 * np.log(r["disc"])
            if log_sqrtD > 0:
                bs_ratios.append(log_hR / log_sqrtD)
    if bs_ratios:
        arr = np.array(bs_ratios)
        print(f"  Degree {deg}: n={len(arr)}, mean BS ratio={np.mean(arr):.4f}, std={np.std(arr):.4f}")

# --- Classification ---
print("\n" + "="*70)
print("CLASSIFICATION")
print("="*70)
deg_eta2 = r1.get("eta_squared", 0)
sign_eta2 = r3.get("eta_squared", 0)
print(f"Degree->CN eta2: {deg_eta2:.4f}")
print(f"Disc sign->CN eta2: {sign_eta2:.4f}")

if deg_eta2 >= 0.14:
    classification = "LAW"
elif deg_eta2 >= 0.01:
    classification = "TENDENCY"
else:
    classification = "NEGLIGIBLE"

print(f"-> Degree->CN: {classification}")

results = {
    "test": "C21",
    "claim": "Number field class number distribution depends sharply on degree",
    "degree_eta2": deg_eta2,
    "sign_eta2": sign_eta2,
    "f24b_verdict": v1b if 'v1b' in dir() else None,
    "f25_verdict": v4 if 'v4' in dir() else None,
    "classification": classification,
}
with open(DATA / "shared/scripts/v2/r2_c21_nf_classnum_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults saved to v2/r2_c21_nf_classnum_results.json")

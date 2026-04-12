"""C56: NF regulator by Galois within degree — F17 confound check.
Does degree mediate Galois->regulator?
Machine: M1 (Skullport), 2026-04-12
"""
import json, sys
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
    gal = nf["galois_label"]
    reg = float(nf["regulator"]) if nf["regulator"] not in ("", "0") else 0.0
    disc = abs(int(nf["disc_abs"]))
    cn = int(nf["class_number"])
    if deg >= 2 and reg > 0:
        records.append({"degree": deg, "galois": gal, "reg": reg, "log_reg": np.log(reg),
                        "disc": disc, "cn": cn})

print(f"Records with degree >= 2, reg > 0: {len(records)}")

log_reg = np.array([r["log_reg"] for r in records])
deg_labels = np.array([str(r["degree"]) for r in records])
gal_labels = np.array([r["galois"] for r in records])

# --- Test 1: Global Galois -> regulator ---
print("\n" + "="*70)
print("TEST 1: Galois -> log(regulator) (F24)")
print("="*70)
v1, r1 = bv2.F24_variance_decomposition(log_reg, gal_labels)
print(f"Verdict: {v1}, eta2 = {r1.get('eta_squared', 0):.4f}")

v1b, r1b = bv2.F24b_metric_consistency(log_reg, gal_labels)
print(f"F24b: {v1b}")

# --- Test 2: Degree -> regulator ---
print("\n" + "="*70)
print("TEST 2: Degree -> log(regulator) (F24)")
print("="*70)
v2, r2 = bv2.F24_variance_decomposition(log_reg, deg_labels)
print(f"Verdict: {v2}, eta2 = {r2.get('eta_squared', 0):.4f}")
for label, gs in sorted(r2.get("group_stats", {}).items()):
    print(f"  Degree {label}: n={gs['n']}, mean={gs['mean']:.3f}, std={gs['std']:.3f}")

# --- Test 3: Incremental Galois | degree ---
print("\n" + "="*70)
print("TEST 3: Incremental Galois | degree -> log(regulator)")
print("="*70)
deg_means = {}
for d in set(deg_labels):
    deg_means[d] = np.mean(log_reg[deg_labels == d])
reg_resid = np.array([log_reg[i] - deg_means[deg_labels[i]] for i in range(len(log_reg))])
v3, r3 = bv2.F24_variance_decomposition(reg_resid, gal_labels)
print(f"Verdict: {v3}, incremental eta2 = {r3.get('eta_squared', 0):.4f}")

# --- Test 4: Within-degree Galois -> regulator ---
print("\n" + "="*70)
print("TEST 4: Within-degree Galois -> log(regulator)")
print("="*70)
deg_array = np.array([r["degree"] for r in records])
for deg in sorted(set(deg_array)):
    mask = deg_array == deg
    lr = log_reg[mask]
    gl = gal_labels[mask]
    gc = Counter(gl)
    valid = [g for g, c in gc.items() if c >= 5]
    if len(valid) < 2:
        print(f"  Degree {deg}: {sum(mask)} fields -- SKIP")
        continue
    v, r = bv2.F24_variance_decomposition(lr, gl)
    print(f"  Degree {deg}: {sum(mask)} fields, {len(valid)} groups -> eta2 = {r.get('eta_squared', 0):.4f} ({v})")

# --- Test 5: Regulator vs class number correlation ---
print("\n" + "="*70)
print("TEST 5: Regulator vs class number (Brauer-Siegel context)")
print("="*70)
from scipy import stats as sp_stats
cn_vals = np.array([r["cn"] for r in records], dtype=float)
rho, p = sp_stats.spearmanr(log_reg, np.log(cn_vals + 1))
print(f"Spearman rho(log_reg, log_cn) = {rho:.4f}, p = {p:.2e}")

# Per degree
for deg in sorted(set(deg_array)):
    mask = deg_array == deg
    if sum(mask) < 30:
        continue
    lr = log_reg[mask]
    lc = np.log(cn_vals[mask] + 1)
    rho_d, p_d = sp_stats.spearmanr(lr, lc)
    print(f"  Degree {deg}: rho = {rho_d:.4f}, p = {p_d:.2e}")

# --- Classification ---
print("\n" + "="*70)
print("CLASSIFICATION")
print("="*70)
global_eta2 = r1.get("eta_squared", 0)
deg_eta2 = r2.get("eta_squared", 0)
incr_eta2 = r3.get("eta_squared", 0)
print(f"Galois->reg eta2 = {global_eta2:.4f}")
print(f"Degree->reg eta2 = {deg_eta2:.4f}")
print(f"Galois|degree->reg eta2 = {incr_eta2:.4f}")

if incr_eta2 < 0.01:
    print("\n-> VERDICT: Galois->regulator is DEGREE-MEDIATED (confound)")
elif incr_eta2 < 0.06:
    print(f"\n-> VERDICT: SMALL genuine Galois effect beyond degree (eta2={incr_eta2:.4f})")
else:
    print(f"\n-> VERDICT: MODERATE+ genuine Galois effect beyond degree (eta2={incr_eta2:.4f})")

results = {
    "test": "C56",
    "claim": "Galois group predicts regulator within degree",
    "global_galois_eta2": global_eta2,
    "degree_eta2": deg_eta2,
    "incremental_eta2": incr_eta2,
    "f24b_verdict": v1b,
    "classification": "CONFOUND" if incr_eta2 < 0.01 else "SMALL" if incr_eta2 < 0.06 else "MODERATE+",
}
with open(DATA / "shared/scripts/v2/c56_nf_reg_galois_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults saved to v2/c56_nf_reg_galois_results.json")

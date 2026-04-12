"""C52: NF discriminant moments by degree — F24 + Galois interaction.
Prior: Regulator scales with degree. Need F24 classification + interaction with Galois.
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

# Load number fields
with open(DATA / "number_fields/data/number_fields.json") as f:
    fields = json.load(f)

print(f"Loaded {len(fields)} number fields")

# Parse — use log(disc) for moment analysis
records = []
for nf in fields:
    deg = nf["degree"]
    disc = abs(int(nf["disc_abs"]))
    cn = int(nf["class_number"])
    gal = nf["galois_label"]
    reg = float(nf["regulator"]) if nf["regulator"] not in ("", "0") else 0.0
    if deg >= 2 and disc > 1:
        records.append({"degree": deg, "disc": disc, "log_disc": np.log(disc),
                        "cn": cn, "galois": gal, "reg": reg})

print(f"Records with degree >= 2, disc > 1: {len(records)}")

log_disc = np.array([r["log_disc"] for r in records])
deg_labels = np.array([str(r["degree"]) for r in records])
gal_labels = np.array([r["galois"] for r in records])
reg_vals = np.array([r["reg"] for r in records])

# ─── Test 1: F24 — Degree → log(discriminant) ───
print("\n" + "="*70)
print("TEST 1: Degree → log(discriminant) (F24)")
print("="*70)
verdict, result = bv2.F24_variance_decomposition(log_disc, deg_labels)
print(f"Verdict: {verdict}")
print(f"eta² = {result.get('eta_squared', 0):.4f}")
print(f"F = {result.get('f_statistic', 0):.2f}")
for label, gs in sorted(result.get("group_stats", {}).items()):
    print(f"  Degree {label}: n={gs['n']}, mean log(disc)={gs['mean']:.3f}, std={gs['std']:.3f}")

verdict_b, result_b = bv2.F24b_metric_consistency(log_disc, deg_labels)
print(f"F24b: {verdict_b}")

# ─── Test 2: F24 — Galois → log(discriminant) ───
print("\n" + "="*70)
print("TEST 2: Galois → log(discriminant) (F24)")
print("="*70)
v2, r2 = bv2.F24_variance_decomposition(log_disc, gal_labels)
print(f"Verdict: {v2}")
print(f"eta² = {r2.get('eta_squared', 0):.4f}")

# ─── Test 3: Incremental — Galois after degree ───
print("\n" + "="*70)
print("TEST 3: Incremental Galois | degree → log(discriminant)")
print("="*70)
deg_means = {}
for d in set(deg_labels):
    deg_means[d] = np.mean(log_disc[deg_labels == d])
disc_resid = np.array([log_disc[i] - deg_means[deg_labels[i]] for i in range(len(log_disc))])
v_incr, r_incr = bv2.F24_variance_decomposition(disc_resid, gal_labels)
print(f"Verdict: {v_incr}")
print(f"Incremental eta² (Galois | degree) = {r_incr.get('eta_squared', 0):.4f}")

# ─── Test 4: Within-degree Galois → discriminant ───
print("\n" + "="*70)
print("TEST 4: Within-degree Galois → log(discriminant)")
print("="*70)
deg_array = np.array([r["degree"] for r in records])
for deg in sorted(set(deg_array)):
    mask = deg_array == deg
    ld = log_disc[mask]
    gl = gal_labels[mask]
    gc = Counter(gl)
    valid = [g for g, c in gc.items() if c >= 5]
    if len(valid) < 2:
        print(f"  Degree {deg}: {sum(mask)} fields — SKIP")
        continue
    v, r = bv2.F24_variance_decomposition(ld, gl)
    print(f"  Degree {deg}: {sum(mask)} fields, {len(valid)} groups → eta² = {r.get('eta_squared', 0):.4f} ({v})")

# ─── Test 5: M4/M² of discriminants per degree ───
print("\n" + "="*70)
print("TEST 5: M4/M² of discriminant within each degree")
print("="*70)
for deg in sorted(set(deg_array)):
    mask = deg_array == deg
    d = np.array([r["disc"] for r in records])[mask].astype(float)
    if len(d) < 30:
        continue
    dn = d / np.mean(d)
    sm2 = np.mean(dn**2)
    sm4 = np.mean(dn**4)
    ratio = sm4 / (sm2**2)
    print(f"  Degree {deg}: n={len(d):5d}, M4/M² = {ratio:.4f}")

# ─── Test 6: Degree → regulator ───
print("\n" + "="*70)
print("TEST 6: Degree → regulator (F24)")
print("="*70)
reg_positive = reg_vals[reg_vals > 0]
deg_positive = deg_labels[reg_vals > 0]
if len(reg_positive) > 30:
    log_reg = np.log(reg_positive)
    v_reg, r_reg = bv2.F24_variance_decomposition(log_reg, deg_positive)
    print(f"Verdict: {v_reg}")
    print(f"eta² = {r_reg.get('eta_squared', 0):.4f}")
    for label, gs in sorted(r_reg.get("group_stats", {}).items()):
        print(f"  Degree {label}: n={gs['n']}, mean log(reg)={gs['mean']:.3f}")
else:
    print("  Insufficient positive regulators")

# ─── Test 7: Interaction — rank correlation of Galois effects across degrees ───
print("\n" + "="*70)
print("TEST 7: Galois effect consistency across degrees (rank correlation)")
print("="*70)
from scipy import stats as sp_stats

degree_galois_means = {}
for deg in sorted(set(deg_array)):
    mask = deg_array == deg
    gl = gal_labels[mask]
    ld = log_disc[mask]
    gc = Counter(gl)
    valid = {g: np.mean(ld[gl == g]) for g, c in gc.items() if c >= 5}
    if len(valid) >= 3:
        degree_galois_means[deg] = valid

if len(degree_galois_means) >= 2:
    degs = sorted(degree_galois_means.keys())
    for i in range(len(degs)):
        for j in range(i+1, len(degs)):
            d1, d2 = degs[i], degs[j]
            shared = set(degree_galois_means[d1]) & set(degree_galois_means[d2])
            if len(shared) >= 3:
                v1 = [degree_galois_means[d1][g] for g in shared]
                v2_ = [degree_galois_means[d2][g] for g in shared]
                rho, p = sp_stats.spearmanr(v1, v2_)
                print(f"  Degree {d1} vs {d2}: {len(shared)} shared groups, rho = {rho:.3f}, p = {p:.4f}")

# ─── Classification ───
print("\n" + "="*70)
print("CLASSIFICATION")
print("="*70)
deg_eta2 = result.get("eta_squared", 0)
gal_eta2 = r2.get("eta_squared", 0)
incr_eta2 = r_incr.get("eta_squared", 0)
print(f"Degree→disc eta² = {deg_eta2:.4f} ({verdict})")
print(f"Galois→disc eta² = {gal_eta2:.4f}")
print(f"Galois|degree→disc eta² = {incr_eta2:.4f}")
print(f"F24b: {verdict_b}")

if deg_eta2 >= 0.14:
    print(f"\n→ Degree→disc: LAW (eta²={deg_eta2:.3f})")
elif deg_eta2 >= 0.01:
    print(f"\n→ Degree→disc: TENDENCY (eta²={deg_eta2:.3f})")

if incr_eta2 >= 0.14:
    print(f"→ Galois adds: LAW-level beyond degree (eta²={incr_eta2:.3f})")
elif incr_eta2 >= 0.01:
    print(f"→ Galois adds: TENDENCY-level beyond degree (eta²={incr_eta2:.3f})")
else:
    print(f"→ Galois adds: NEGLIGIBLE beyond degree (eta²={incr_eta2:.3f})")

results = {
    "test": "C52",
    "claim": "NF discriminant moments vary by degree, Galois adds signal",
    "degree_eta2": deg_eta2,
    "galois_eta2": gal_eta2,
    "incremental_galois_eta2": incr_eta2,
    "degree_verdict": verdict,
    "f24b_verdict": verdict_b,
    "classification_degree": "LAW" if deg_eta2 >= 0.14 else "TENDENCY" if deg_eta2 >= 0.01 else "NEGLIGIBLE",
    "classification_galois_incr": "LAW" if incr_eta2 >= 0.14 else "TENDENCY" if incr_eta2 >= 0.01 else "NEGLIGIBLE",
}
with open(DATA / "shared/scripts/v2/c52_nf_disc_moments_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults saved to v2/c52_nf_disc_moments_results.json")

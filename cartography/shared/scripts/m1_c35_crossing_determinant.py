"""C35: Crossing number → determinant — F24 + Alexander polynomial control.
Prior: eta²=0.219 LAW. Need to check if Alexander polynomial mediates.
Machine: M1 (Skullport), 2026-04-12
"""
import json, sys, re
import numpy as np
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from battery_v2 import BatteryV2

DATA = Path(__file__).resolve().parent.parent.parent
bv2 = BatteryV2()

# Load knots
with open(DATA / "knots/data/knots.json") as f:
    data = json.load(f)
knots = data["knots"]
print(f"Loaded {len(knots)} knots")

# Extract crossing number from name (field is mostly 0/missing)
def parse_crossing(name):
    m = re.match(r'(\d+)', name)
    return int(m.group(1)) if m else 0

# Extract crossing number, determinant, Alexander data
records = []
for k in knots:
    cn = k.get("crossing_number") or 0
    if cn == 0:
        cn = parse_crossing(k.get("name", ""))
    det = k.get("determinant") or 0
    alex = k.get("alexander") if isinstance(k.get("alexander"), dict) else {}
    alex_coeffs = k.get("alex_coeffs") or []
    if cn > 0 and det > 0:
        records.append({
            "name": k["name"],
            "crossing": cn,
            "det": det,
            "alex_degree": alex.get("max_power", 0) - alex.get("min_power", 0) if alex else 0,
            "alex_n_coeffs": len(alex_coeffs),
            "alex_sum_abs": sum(abs(c) for c in alex_coeffs) if alex_coeffs else 0,
        })

print(f"Records with crossing > 0, det > 0: {len(records)}")

crossing_vals = np.array([r["crossing"] for r in records])
det_vals = np.array([r["det"] for r in records], dtype=float)
crossing_labels = np.array([str(r["crossing"]) for r in records])

# ─── Test 1: F24 — Crossing → determinant ───
print("\n" + "="*70)
print("TEST 1: Crossing number → determinant (F24)")
print("="*70)
verdict, result = bv2.F24_variance_decomposition(det_vals, crossing_labels)
print(f"Verdict: {verdict}")
print(f"eta² = {result.get('eta_squared', 0):.4f}")
print(f"F = {result.get('f_statistic', 0):.2f}")
print(f"n_groups = {result.get('n_groups')}, n_total = {result.get('n_total')}")

verdict_b, result_b = bv2.F24b_metric_consistency(det_vals, crossing_labels)
print(f"F24b: {verdict_b}")
if "tail_contribution" in result_b:
    print(f"  tail_contribution = {result_b['tail_contribution']:.3f}")

# ─── Test 2: F24 — Alexander degree → determinant ───
print("\n" + "="*70)
print("TEST 2: Alexander degree → determinant (F24)")
print("="*70)
alex_deg_labels = np.array([str(r["alex_degree"]) for r in records])
v2, r2 = bv2.F24_variance_decomposition(det_vals, alex_deg_labels)
print(f"Verdict: {v2}")
print(f"eta² = {r2.get('eta_squared', 0):.4f}")

# ─── Test 3: Crossing → determinant WITHIN Alexander degree ───
print("\n" + "="*70)
print("TEST 3: Within-Alexander-degree: crossing → determinant")
print("="*70)
alex_degrees = np.array([r["alex_degree"] for r in records])
for ad in sorted(set(alex_degrees)):
    if ad == 0:
        continue
    mask = alex_degrees == ad
    det_ad = det_vals[mask]
    cr_ad = crossing_labels[mask]
    gc = Counter(cr_ad)
    valid = [g for g, c in gc.items() if c >= 5]
    if len(valid) < 2:
        print(f"  Alex degree {ad}: {sum(mask)} knots — SKIP")
        continue
    v, r = bv2.F24_variance_decomposition(det_ad, cr_ad)
    print(f"  Alex degree {ad}: {sum(mask)} knots → eta² = {r.get('eta_squared', 0):.4f} ({v})")

# ─── Test 4: Incremental — Crossing after Alexander degree ───
print("\n" + "="*70)
print("TEST 4: Incremental eta² (crossing | Alexander degree)")
print("="*70)
# Residualize determinant by Alexander degree
ad_means = {}
for ad in set(alex_deg_labels):
    ad_means[ad] = np.mean(det_vals[alex_deg_labels == ad])
det_resid = np.array([det_vals[i] - ad_means[alex_deg_labels[i]] for i in range(len(det_vals))])
v_resid, r_resid = bv2.F24_variance_decomposition(det_resid, crossing_labels)
print(f"Verdict: {v_resid}")
print(f"Incremental eta² (crossing | Alexander degree) = {r_resid.get('eta_squared', 0):.4f}")

# ─── Test 5: Correlation — crossing vs log(det) ───
print("\n" + "="*70)
print("TEST 5: Correlation — crossing vs log(det)")
print("="*70)
from scipy import stats as sp_stats
log_det = np.log(det_vals + 1)
rho, p = sp_stats.spearmanr(crossing_vals, log_det)
print(f"Spearman rho = {rho:.4f}, p = {p:.2e}")
r_pearson, p_pearson = sp_stats.pearsonr(crossing_vals.astype(float), log_det)
print(f"Pearson r (crossing vs log det) = {r_pearson:.4f}, p = {p_pearson:.2e}")

# ─── Test 6: Is det ~ f(Alexander)? Near-identity check ───
print("\n" + "="*70)
print("TEST 6: Near-identity check — det vs Alexander eval at -1")
print("="*70)
# Alexander polynomial evaluated at t=-1 should equal determinant (up to sign)
alex_at_neg1 = []
for r in records:
    coeffs = [rr for rr in records if rr["name"] == r["name"]][0]
    # Reconstruct from knots data
    pass

# Direct check: det = |Alexander(-1)| is a known identity
# Alexander(-1) = sum of coefficients * (-1)^k
matches = 0
mismatches = 0
for k in knots:
    det = k.get("determinant") or 0
    alex = k.get("alexander")
    if not alex or not isinstance(alex, dict):
        continue
    coeffs = alex.get("coefficients", [])
    min_pow = alex.get("min_power", 0)
    if det > 0 and coeffs:
        # Evaluate at t = -1
        val = sum(c * ((-1) ** (min_pow + i)) for i, c in enumerate(coeffs))
        if abs(abs(val) - det) < 0.5:
            matches += 1
        else:
            mismatches += 1

total = matches + mismatches
if total > 0:
    print(f"  |Alexander(-1)| == determinant: {matches}/{total} ({100*matches/total:.1f}%)")
    if matches / total > 0.99:
        print("  → This is a MATHEMATICAL IDENTITY (det = |Δ(-1)|)")
        print("  → Crossing→det relationship is mediated by Alexander polynomial")

# ─── Classification ───
print("\n" + "="*70)
print("CLASSIFICATION")
print("="*70)
global_eta2 = result.get("eta_squared", 0)
incr_eta2 = r_resid.get("eta_squared", 0)
alex_eta2 = r2.get("eta_squared", 0)
print(f"Crossing→det eta² = {global_eta2:.4f} ({verdict})")
print(f"Alex_degree→det eta² = {alex_eta2:.4f}")
print(f"Crossing→det | Alex_degree eta² = {incr_eta2:.4f}")
print(f"F24b: {verdict_b}")

if matches / max(total, 1) > 0.99:
    print("\n→ NOTE: det = |Alexander(-1)| is a KNOWN IDENTITY.")
    print("  The crossing→det relationship works through Alexander polynomial complexity.")
    print("  This is a CONDITIONAL LAW mediated by topology, not a direct law.")

classification = "LAW" if global_eta2 >= 0.14 and verdict_b != "TAIL_DRIVEN" else \
                 "CONSTRAINT" if global_eta2 >= 0.01 else "NEGLIGIBLE"
print(f"\n→ CLASSIFICATION: {classification}")

results = {
    "test": "C35",
    "claim": "Crossing number predicts determinant",
    "global_crossing_eta2": global_eta2,
    "alex_degree_eta2": alex_eta2,
    "incremental_eta2": incr_eta2,
    "f24_verdict": verdict,
    "f24b_verdict": verdict_b,
    "det_is_alex_neg1_identity": matches / max(total, 1) > 0.99,
    "identity_match_rate": matches / max(total, 1),
    "spearman_rho": rho,
    "classification": classification,
}
with open(DATA / "shared/scripts/v2/c35_crossing_det_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults saved to v2/c35_crossing_det_results.json")

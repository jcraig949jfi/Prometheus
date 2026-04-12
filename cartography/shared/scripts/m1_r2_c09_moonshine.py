"""C09: Moonshine network expansion — F24+F25 classification.
Prior: 307 bridges, enrichment grows with prime. Moonshine breaks flat pattern.
Battery v6. Machine: M1 (Skullport), 2026-04-12
"""
import sys, json, glob
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from battery_v2 import BatteryV2

DATA = Path(__file__).resolve().parent.parent.parent
bv2 = BatteryV2()

# Load moonshine data
moon_dir = DATA / "convergence/data/moonshine"
moon_files = sorted(glob.glob(str(moon_dir / "mckay_*.json")))
print(f"Found {len(moon_files)} moonshine files")

moonshine_data = {}
for f in moon_files:
    with open(f) as fp:
        d = json.load(fp)
    key = d.get("class", Path(f).stem)
    moonshine_data[key] = d

# Also load prior moonshine results if available
prior_results = {}
for candidate in [
    DATA / "shared/scripts/v2/moonshine_scaling_results.json",
    DATA / "shared/scripts/v2/moonshine_oeis_results.json",
]:
    if candidate.exists():
        with open(candidate) as f:
            prior_results[candidate.stem] = json.load(f)
        print(f"Loaded prior: {candidate.stem}")

# --- Test 1: Coefficient structure per McKay-Thompson class ---
print("\n" + "="*70)
print("TEST 1: McKay-Thompson coefficient statistics")
print("="*70)

class_stats = {}
all_coeffs = []
all_labels = []
for key, d in moonshine_data.items():
    coeffs = d.get("coefficients") or d.get("data", [])
    if not coeffs or not isinstance(coeffs, list):
        continue
    coeffs_arr = np.array(coeffs[:200], dtype=float)
    coeffs_arr = coeffs_arr[np.isfinite(coeffs_arr) & (coeffs_arr != 0)]
    if len(coeffs_arr) < 10:
        continue

    log_abs = np.log(np.abs(coeffs_arr) + 1)
    m2 = np.mean((log_abs / np.mean(log_abs))**2) if np.mean(log_abs) > 0 else 0
    m4 = np.mean((log_abs / np.mean(log_abs))**4) if np.mean(log_abs) > 0 else 0
    m4m2 = m4 / (m2**2) if m2 > 0 else 0

    class_stats[key] = {
        "n_coeffs": len(coeffs_arr),
        "mean_log": float(np.mean(log_abs)),
        "std_log": float(np.std(log_abs)),
        "m4m2": float(m4m2),
    }
    print(f"  {key}: n={len(coeffs_arr)}, mean_log={np.mean(log_abs):.3f}, M4/M2={m4m2:.4f}")

    for c in log_abs:
        all_coeffs.append(c)
        all_labels.append(key)

# --- Test 2: F24 - class -> coefficient magnitude ---
print("\n" + "="*70)
print("TEST 2: F24 - McKay-Thompson class -> coefficient magnitude")
print("="*70)

if len(set(all_labels)) >= 2:
    v2, r2 = bv2.F24_variance_decomposition(np.array(all_coeffs), np.array(all_labels))
    print(f"Verdict: {v2}, eta2 = {r2.get('eta_squared', 0):.4f}")
    v2b, r2b = bv2.F24b_metric_consistency(np.array(all_coeffs), np.array(all_labels))
    print(f"F24b: {v2b}")
else:
    print("Not enough classes for F24")
    r2 = {}

# --- Test 3: Mod-p enrichment per class ---
print("\n" + "="*70)
print("TEST 3: Mod-p enrichment by McKay-Thompson class")
print("="*70)

enrichment_by_p = defaultdict(dict)
for key, d in moonshine_data.items():
    coeffs = d.get("coefficients") or d.get("data", [])
    if not coeffs or len(coeffs) < 50:
        continue
    coeffs_arr = np.array(coeffs[:200], dtype=float)
    coeffs_int = coeffs_arr[np.isfinite(coeffs_arr)].astype(int)

    for p in [2, 3, 5, 7, 11]:
        residues = coeffs_int % p
        counts = Counter(residues)
        # Enrichment = max count / expected uniform
        expected = len(coeffs_int) / p
        max_enrichment = max(counts.values()) / expected if expected > 0 else 0
        enrichment_by_p[key][p] = float(max_enrichment)

print("Class-level enrichment (max residue / expected):")
for key in sorted(enrichment_by_p.keys()):
    vals = enrichment_by_p[key]
    line = f"  {key}:"
    for p in [2, 3, 5, 7, 11]:
        if p in vals:
            line += f" p={p}:{vals[p]:.2f}"
    print(line)

# --- Test 4: Does enrichment grow with prime? ---
print("\n" + "="*70)
print("TEST 4: Enrichment scaling with prime (per class)")
print("="*70)

from scipy import stats as sp_stats
for key in sorted(enrichment_by_p.keys()):
    primes = [2, 3, 5, 7, 11]
    enrich = [enrichment_by_p[key].get(p, 0) for p in primes]
    if all(e > 0 for e in enrich):
        rho, p_val = sp_stats.spearmanr(primes, enrich)
        print(f"  {key}: enrichment vs prime rho={rho:.3f}, p={p_val:.3f}, trend={'GROWING' if rho > 0.5 else 'FLAT' if abs(rho) < 0.3 else 'DECLINING'}")

# --- Test 5: Coefficient divisibility patterns ---
print("\n" + "="*70)
print("TEST 5: Divisibility structure (fraction divisible by p)")
print("="*70)

for key, d in sorted(moonshine_data.items()):
    coeffs = d.get("coefficients") or d.get("data", [])
    if not coeffs or len(coeffs) < 50:
        continue
    coeffs_arr = np.array(coeffs[:200], dtype=float)
    coeffs_int = coeffs_arr[np.isfinite(coeffs_arr)].astype(int)
    if len(coeffs_int) == 0:
        continue

    divs = []
    for p in [2, 3, 5, 7, 11, 13]:
        frac = np.mean(coeffs_int % p == 0)
        divs.append(f"p={p}:{frac:.2f}")
    print(f"  {key}: {', '.join(divs)}")

# --- Test 6: F27 consequence check ---
print("\n" + "="*70)
print("TEST 6: F27 - consequence check (tautology?)")
print("="*70)
v7, r7 = bv2.F27_consequence_check("mckay_thompson_class", "coefficient_magnitude")
print(f"Verdict: {v7}")
if r7:
    print(f"  {r7}")

# --- Classification ---
print("\n" + "="*70)
print("CLASSIFICATION")
print("="*70)
eta2 = r2.get("eta_squared", 0)
print(f"Class->coefficient eta2: {eta2:.4f}")
print(f"N classes analyzed: {len(class_stats)}")

if eta2 >= 0.14:
    classification = "LAW"
elif eta2 >= 0.01:
    classification = "TENDENCY"
else:
    classification = "NEGLIGIBLE"
print(f"-> CLASSIFICATION: {classification}")
print(f"   Moonshine coefficient structure across McKay-Thompson classes.")

results = {
    "test": "C09",
    "claim": "Moonshine enrichment grows with prime; coefficient structure varies by class",
    "class_eta2": eta2,
    "n_classes": len(class_stats),
    "class_stats": class_stats,
    "classification": classification,
}
with open(DATA / "shared/scripts/v2/r2_c09_moonshine_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults saved to v2/r2_c09_moonshine_results.json")

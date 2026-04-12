"""S5: Fricke enrichment 1.44x — run through F24 magnitude check.
Prior: Fricke +1 vs -1 shows 1.44x enrichment. Mechanism unknown.
Machine: M1 (Skullport), 2026-04-12
"""
import json, sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from battery_v2 import BatteryV2

DATA = Path(__file__).resolve().parent.parent.parent
bv2 = BatteryV2()

# Load Maass forms (need Fricke eigenvalue)
maass_path = DATA / "maass/data/maass_with_coefficients.json"
if not maass_path.exists():
    maass_path = DATA / "maass/data/maass_forms_full.json"
    if not maass_path.exists():
        maass_path = DATA / "maass/data/maass_forms.json"

print(f"Loading Maass forms from {maass_path.name}...")
with open(maass_path) as f:
    maass_data = json.load(f)

# Handle different formats
if isinstance(maass_data, dict):
    forms = maass_data.get("forms", maass_data.get("results", []))
    if not forms:
        forms = [v for v in maass_data.values() if isinstance(v, list) and len(v) > 0]
        forms = forms[0] if forms else []
elif isinstance(maass_data, list):
    forms = maass_data
else:
    forms = []

print(f"Loaded {len(forms)} Maass forms")

# Extract Fricke eigenvalue and spectral parameter
records = []
for f_item in forms:
    if not isinstance(f_item, dict):
        continue
    # Try different field names
    fricke = f_item.get("Fricke_eigenvalue") or f_item.get("fricke") or f_item.get("sign") or f_item.get("symmetry")
    spectral = f_item.get("Eigenvalue") or f_item.get("spectral_parameter") or f_item.get("eigenvalue") or f_item.get("R")
    level = f_item.get("Level") or f_item.get("level") or f_item.get("N")
    coeffs = f_item.get("coefficients") or f_item.get("Coefficients") or []

    if fricke is not None and spectral is not None:
        # Normalize Fricke to +1/-1
        if isinstance(fricke, str):
            if fricke in ("even", "Even", "+", "1"):
                fricke_val = 1
            elif fricke in ("odd", "Odd", "-", "-1"):
                fricke_val = -1
            else:
                try:
                    fricke_val = int(float(fricke))
                except:
                    continue
        else:
            fricke_val = int(fricke)

        if fricke_val not in (-1, 1):
            continue

        try:
            spec_val = float(spectral)
        except:
            continue

        records.append({
            "fricke": fricke_val,
            "spectral": spec_val,
            "level": int(level) if level else 0,
            "n_coeffs": len(coeffs) if isinstance(coeffs, list) else 0,
        })

print(f"Records with Fricke + spectral: {len(records)}")
if len(records) == 0:
    # Try to see what fields exist
    if forms:
        print(f"Sample form keys: {list(forms[0].keys())[:15]}")
        print(f"Sample form: {dict(list(forms[0].items())[:8])}")
    print("Cannot proceed without Fricke eigenvalue data")
    sys.exit(1)

from collections import Counter
fricke_dist = Counter(r["fricke"] for r in records)
print(f"Fricke distribution: {dict(fricke_dist)}")

spectral_vals = np.array([r["spectral"] for r in records])
fricke_labels = np.array([str(r["fricke"]) for r in records])
level_vals = np.array([r["level"] for r in records])

# --- Test 1: F24 -- Fricke -> spectral parameter ---
print("\n" + "="*70)
print("TEST 1: Fricke -> spectral parameter (F24)")
print("="*70)
v1, r1 = bv2.F24_variance_decomposition(spectral_vals, fricke_labels)
print(f"Verdict: {v1}, eta2 = {r1.get('eta_squared', 0):.4f}")
for label, gs in sorted(r1.get("group_stats", {}).items()):
    print(f"  Fricke {label}: n={gs['n']}, mean R={gs['mean']:.4f}, std={gs['std']:.4f}")

v1b, r1b = bv2.F24b_metric_consistency(spectral_vals, fricke_labels)
print(f"F24b: {v1b}")

# --- Test 2: Enrichment calculation ---
print("\n" + "="*70)
print("TEST 2: Enrichment (Fricke +1 vs -1)")
print("="*70)
plus_R = spectral_vals[fricke_labels == "1"]
minus_R = spectral_vals[fricke_labels == "-1"]
if len(plus_R) > 0 and len(minus_R) > 0:
    enrichment = np.mean(plus_R) / np.mean(minus_R)
    print(f"Mean R (Fricke +1): {np.mean(plus_R):.4f}")
    print(f"Mean R (Fricke -1): {np.mean(minus_R):.4f}")
    print(f"Enrichment ratio: {enrichment:.4f}")

    # Mann-Whitney U test
    from scipy import stats as sp_stats
    u_stat, u_p = sp_stats.mannwhitneyu(plus_R, minus_R, alternative='two-sided')
    print(f"Mann-Whitney U: stat={u_stat:.1f}, p={u_p:.2e}")

    # Cohen's d
    pooled_std = np.sqrt((np.var(plus_R) * len(plus_R) + np.var(minus_R) * len(minus_R)) / (len(plus_R) + len(minus_R)))
    cohens_d = (np.mean(plus_R) - np.mean(minus_R)) / pooled_std if pooled_std > 0 else 0
    print(f"Cohen's d: {cohens_d:.4f}")

# --- Test 3: Level as confound ---
print("\n" + "="*70)
print("TEST 3: F17-style confound check (level)")
print("="*70)
level_labels = np.array([str(r["level"]) for r in records])
v_level, r_level = bv2.F24_variance_decomposition(spectral_vals, level_labels)
print(f"Level -> spectral eta2: {r_level.get('eta_squared', 0):.4f}")

# Within prime levels only
prime_levels = [r for r in records if r["level"] > 1]
if len(prime_levels) > 30:
    # Check Fricke within a single level
    level_counts = Counter(r["level"] for r in records)
    big_levels = [lv for lv, c in level_counts.items() if c >= 10]
    print(f"Levels with >= 10 forms: {len(big_levels)}")
    for lv in sorted(big_levels)[:5]:
        lv_recs = [r for r in records if r["level"] == lv]
        lv_spec = np.array([r["spectral"] for r in lv_recs])
        lv_frick = np.array([str(r["fricke"]) for r in lv_recs])
        fc = Counter(lv_frick)
        if len(fc) >= 2 and all(c >= 3 for c in fc.values()):
            v, r = bv2.F24_variance_decomposition(lv_spec, lv_frick)
            print(f"  Level {lv}: n={len(lv_recs)}, Fricke->R eta2={r.get('eta_squared', 0):.4f}")

# --- Classification ---
print("\n" + "="*70)
print("CLASSIFICATION")
print("="*70)
eta2 = r1.get("eta_squared", 0)
print(f"Fricke->spectral eta2: {eta2:.4f}")
print(f"F24b: {v1b}")

if eta2 >= 0.14:
    classification = "LAW"
elif eta2 >= 0.06:
    classification = "MODERATE_EFFECT"
elif eta2 >= 0.01:
    classification = "TENDENCY"
else:
    classification = "NEGLIGIBLE"

print(f"-> CLASSIFICATION: {classification}")

final_results = {
    "test": "S5",
    "claim": "Fricke eigenvalue enrichment 1.44x on spectral parameter",
    "fricke_eta2": eta2,
    "f24_verdict": v1,
    "f24b_verdict": v1b,
    "enrichment_ratio": float(enrichment) if 'enrichment' in dir() else None,
    "cohens_d": float(cohens_d) if 'cohens_d' in dir() else None,
    "classification": classification,
}
with open(DATA / "shared/scripts/v2/s5_fricke_enrichment_results.json", "w") as f:
    json.dump(final_results, f, indent=2, default=str)
print(f"\nResults saved to v2/s5_fricke_enrichment_results.json")

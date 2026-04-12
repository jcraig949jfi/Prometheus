#!/usr/bin/env python3
"""Deep dive: Does congruence enrichment universally grow with prime?
Seen in HMF (C04: 1.21x->2.83x) and moonshine (7B: rho=0.9).
Test on EC traces, Maass coefficients, and compare.
M1 (Skullport), 2026-04-12
"""
import sys, os, json
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

_scripts = str(Path("F:/Prometheus/cartography/shared/scripts").resolve())
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)
from battery_v2 import BatteryV2
bv2 = BatteryV2()

from scipy import stats as sp_stats
import duckdb

primes_test = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

def compute_congruence_enrichment(traces_list, n_pairs=5000):
    """For a list of trace sequences, compute mod-l congruence enrichment at each prime."""
    enrichments = {}
    rng = np.random.RandomState(42)
    n = len(traces_list)
    if n < 10:
        return enrichments

    for l in primes_test:
        match_densities = []
        for _ in range(min(n_pairs, n*(n-1)//2)):
            i, j = rng.choice(n, 2, replace=False)
            a, b = traces_list[i], traces_list[j]
            min_len = min(len(a), len(b), 100)
            if min_len < 10:
                continue
            matches = sum(1 for k in range(min_len) if int(a[k]) % l == int(b[k]) % l)
            match_densities.append(matches / min_len)

        if match_densities:
            mean_density = np.mean(match_densities)
            baseline = 1.0 / l
            enrichments[l] = mean_density / baseline if baseline > 0 else 0

    return enrichments

# --- 1. EC modular forms (weight-2, dim-1) ---
print("="*70)
print("FAMILY 1: Elliptic curve modular forms (weight-2, dim-1)")
print("="*70)

con = duckdb.connect("F:/Prometheus/charon/data/charon.duckdb", read_only=True)
df = con.execute("""
    SELECT traces FROM modular_forms
    WHERE weight = 2 AND dim = 1 AND traces IS NOT NULL
    LIMIT 5000
""").fetchdf()

ec_traces = []
for _, row in df.iterrows():
    t = row["traces"]
    if isinstance(t, (list, np.ndarray)) and len(t) >= 20:
        ec_traces.append(np.array(t[:100], dtype=float))

print(f"  {len(ec_traces)} trace sequences")
ec_enrich = compute_congruence_enrichment(ec_traces)
for l in sorted(ec_enrich.keys()):
    print(f"  mod-{l:2d}: enrichment = {ec_enrich[l]:.3f}x")

# --- 2. Higher weight modular forms ---
print("\n" + "="*70)
print("FAMILY 2: Higher weight modular forms (weight > 2, dim-1)")
print("="*70)

df2 = con.execute("""
    SELECT traces FROM modular_forms
    WHERE weight > 2 AND dim = 1 AND traces IS NOT NULL
    LIMIT 5000
""").fetchdf()

hw_traces = []
for _, row in df2.iterrows():
    t = row["traces"]
    if isinstance(t, (list, np.ndarray)) and len(t) >= 20:
        hw_traces.append(np.array(t[:100], dtype=float))

print(f"  {len(hw_traces)} trace sequences")
hw_enrich = compute_congruence_enrichment(hw_traces)
for l in sorted(hw_enrich.keys()):
    print(f"  mod-{l:2d}: enrichment = {hw_enrich[l]:.3f}x")

con.close()

# --- 3. Maass form coefficients ---
print("\n" + "="*70)
print("FAMILY 3: Maass form coefficients")
print("="*70)

maass_path = Path("F:/Prometheus/cartography/maass/data/maass_with_coefficients.json")
if maass_path.exists():
    with open(maass_path) as f:
        maass_data = json.load(f)

    maass_traces = []
    forms = maass_data if isinstance(maass_data, list) else maass_data.get("forms", [])
    for form in forms[:5000]:
        if not isinstance(form, dict):
            continue
        coeffs = form.get("coefficients") or form.get("Coefficients") or []
        if isinstance(coeffs, list) and len(coeffs) >= 20:
            # Maass coefficients are real, round to nearest int for mod-p
            arr = np.array(coeffs[:100], dtype=float)
            arr = np.round(arr).astype(int)
            maass_traces.append(arr.astype(float))

    print(f"  {len(maass_traces)} coefficient sequences")
    if maass_traces:
        maass_enrich = compute_congruence_enrichment(maass_traces)
        for l in sorted(maass_enrich.keys()):
            print(f"  mod-{l:2d}: enrichment = {maass_enrich[l]:.3f}x")
    else:
        maass_enrich = {}
        print("  No valid sequences")
else:
    maass_enrich = {}
    print("  Maass data not found")

# --- 4. Moonshine McKay-Thompson coefficients ---
print("\n" + "="*70)
print("FAMILY 4: Moonshine McKay-Thompson coefficients")
print("="*70)

moon_dir = Path("F:/Prometheus/cartography/convergence/data/moonshine")
moon_traces = []
if moon_dir.exists():
    import glob
    for fp in sorted(glob.glob(str(moon_dir / "mckay_*.json"))):
        with open(fp) as f:
            d = json.load(f)
        coeffs = d.get("coefficients") or d.get("data", [])
        if isinstance(coeffs, list) and len(coeffs) >= 20:
            arr = np.array(coeffs[:200], dtype=float)
            arr = arr[np.isfinite(arr)]
            if len(arr) >= 20:
                moon_traces.append(arr)

    print(f"  {len(moon_traces)} coefficient sequences")
    if len(moon_traces) >= 10:
        moon_enrich = compute_congruence_enrichment(moon_traces, n_pairs=min(1000, len(moon_traces)*(len(moon_traces)-1)//2))
        for l in sorted(moon_enrich.keys()):
            print(f"  mod-{l:2d}: enrichment = {moon_enrich[l]:.3f}x")
    else:
        moon_enrich = {}
else:
    moon_enrich = {}
    print("  Moonshine data not found")

# --- 5. Comparison: does enrichment grow with prime in all families? ---
print("\n" + "="*70)
print("TEST: Does enrichment grow with prime across all families?")
print("="*70)

families = {
    "EC (wt-2)": ec_enrich,
    "Higher wt": hw_enrich,
    "Maass": maass_enrich,
    "Moonshine": moon_enrich,
}

print(f"\n{'Family':<15s}", end="")
for l in primes_test[:8]:
    print(f" mod-{l:<3d}", end="")
print(f"  rho    p-val  trend")

for name, enrich in families.items():
    if not enrich:
        print(f"{name:<15s} (no data)")
        continue
    print(f"{name:<15s}", end="")
    vals = []
    ps = []
    for l in primes_test[:8]:
        if l in enrich:
            print(f" {enrich[l]:.3f}", end="  ")
            vals.append(enrich[l])
            ps.append(l)
        else:
            print(f" ---  ", end="  ")

    if len(vals) >= 4:
        rho, p = sp_stats.spearmanr(ps, vals)
        trend = "GROWING" if rho > 0.5 else "FLAT" if abs(rho) < 0.3 else "DECLINING"
        print(f"  {rho:.3f}  {p:.4f}  {trend}")
    else:
        print()

# --- Classification ---
print("\n" + "="*70)
print("CLASSIFICATION")
print("="*70)

growing_count = 0
total_count = 0
for name, enrich in families.items():
    if not enrich or len(enrich) < 4:
        continue
    ps = sorted(enrich.keys())[:8]
    vs = [enrich[p] for p in ps]
    rho, _ = sp_stats.spearmanr(ps, vs)
    total_count += 1
    if rho > 0.5:
        growing_count += 1

print(f"Families with enrichment growing with prime: {growing_count}/{total_count}")
if growing_count == total_count and total_count >= 2:
    print("-> UNIVERSAL: congruence enrichment grows with prime across ALL tested families")
elif growing_count > 0:
    print("-> PARTIAL: some families show growth, others don't")
else:
    print("-> NOT UNIVERSAL: enrichment does NOT consistently grow with prime")

results = {
    "test": "congruence_universality",
    "families": {name: dict(enrich) for name, enrich in families.items()},
    "growing_count": growing_count,
    "total_count": total_count,
}
with open(Path("F:/Prometheus/cartography/shared/scripts/v2/deep_congruence_universality_results.json"), "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nSaved to v2/deep_congruence_universality_results.json")

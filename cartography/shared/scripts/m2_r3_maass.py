#!/usr/bin/env python3
"""
M2 Round 3 — Maass deep dive (4 tests, single-threaded: 342MB load)
C53-f24: Coefficient moments by symmetry/level
C05-deep: Per-level spacing (GUE vs Poisson)
Maass.coeff: Coefficient autocorrelation structure
Maass.fricke: Fricke -> coefficient structure
"""
import sys, os, json
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy import stats as sp_stats

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
    if len(valid) < 2: return float("nan"), 0, 0
    all_v = np.concatenate(list(valid.values()))
    gm = np.mean(all_v)
    ss_total = np.sum((all_v - gm)**2)
    ss_between = sum(len(v) * (np.mean(v) - gm)**2 for v in valid.values())
    return ss_between / ss_total if ss_total > 0 else 0, len(all_v), len(valid)

def m4m2(arr):
    arr = np.array(arr, dtype=float)
    arr = arr[np.isfinite(arr) & (arr != 0)]
    if len(arr) < 10: return float("nan")
    vn = arr / np.mean(np.abs(arr))
    m2 = np.mean(vn**2); m4 = np.mean(vn**4)
    return m4 / m2**2 if m2 > 0 else float("nan")

results = []
def record(name, classification, eta2=None, key_metric=""):
    results.append({"name": name, "classification": classification, "eta2": eta2, "key_metric": key_metric})
    e = f"eta2={eta2:.4f}" if eta2 is not None and not np.isnan(eta2) else ""
    print(f"  >> {name:20s} | {classification:20s} | {e:15s} | {key_metric}")

# Load Maass (342MB — single load)
print("Loading Maass forms (14,995 with coefficients)...")
maass = json.load(open(DATA / "maass/data/maass_with_coefficients.json", encoding="utf-8"))
print(f"  Loaded {len(maass)} forms")

# Also load full metadata (300 forms with Fricke)
maass_full = json.load(open(DATA / "maass/data/maass_forms_full.json", encoding="utf-8"))
fricke_map = {}
for m in maass_full:
    label = m.get("maass_label", "")
    fricke = m.get("fricke_eigenvalue")
    if label and fricke is not None:
        fricke_map[label] = fricke
print(f"  Fricke data for {len(fricke_map)} forms\n")

# ============================================================
print("=" * 90)
print("C53-f24: Maass coefficient moments by level")
print("=" * 90)

# For each form, compute M4/M2^2 of its coefficients
level_m4m2 = []
level_labels = []
for m in maass:
    coeffs = m.get("coefficients", [])
    level = m.get("level")
    if coeffs and level is not None and len(coeffs) >= 20:
        arr = np.array(coeffs[:500], dtype=float)  # cap at 500 for speed
        ratio = m4m2(arr)
        if np.isfinite(ratio):
            level_m4m2.append(ratio)
            level_labels.append(level)

print(f"  Forms with computable M4/M2^2: {len(level_m4m2)}")
if level_m4m2:
    eta, n, k = eta_sq(level_m4m2, level_labels)
    v24, r24 = bv2.F24_variance_decomposition(level_m4m2, level_labels)
    record("C53-f24", v24, eta, f"level->coeff M4/M2^2 n={n} k={k}")

    # Overall M4/M2^2 distribution
    arr = np.array(level_m4m2)
    print(f"  M4/M2^2 distribution: mean={np.mean(arr):.2f}, median={np.median(arr):.2f}, std={np.std(arr):.2f}")
    print(f"  % near SU(2) (1.8-2.2): {np.mean((arr > 1.8) & (arr < 2.2))*100:.1f}%")
    print(f"  % near Poisson (>5): {np.mean(arr > 5)*100:.1f}%")

# ============================================================
print("\nC05-deep: Per-level spacing statistics (GUE vs Poisson)")
print("=" * 90)

# Group spectral parameters by level
level_specs = defaultdict(list)
for m in maass:
    sp = m.get("spectral_parameter")
    lv = m.get("level")
    if sp is not None and lv is not None:
        level_specs[lv].append(float(sp))

# For levels with enough forms, compute normalized nearest-neighbor spacing
print(f"  {'Level':>6s} | {'n':>5s} | {'mean gap':>8s} | {'NNS M4/M2^2':>11s} | {'KS Poisson':>10s} | {'KS GUE':>8s}")
print("  " + "-" * 65)

gue_matches = 0
poisson_matches = 0
total_tested = 0

for lv in sorted(level_specs.keys()):
    specs = sorted(level_specs[lv])
    if len(specs) < 30:
        continue
    gaps = np.diff(specs)
    gaps = gaps[gaps > 0]
    if len(gaps) < 20:
        continue

    mg = np.mean(gaps)
    normalized = gaps / mg
    nns_m4m2 = m4m2(normalized)

    ks_poisson = sp_stats.kstest(normalized, 'expon')[0]

    # GUE: spacing distribution is Wigner surmise p(s) = (pi/2)s exp(-pi s^2/4)
    # CDF: 1 - exp(-pi s^2/4)
    def gue_cdf(s):
        return 1 - np.exp(-np.pi * s**2 / 4)
    ks_gue = sp_stats.kstest(normalized, gue_cdf)[0]

    total_tested += 1
    if ks_gue < ks_poisson:
        gue_matches += 1
    else:
        poisson_matches += 1

    if lv <= 20 or lv % 100 == 0 or lv > 900:
        print(f"  {lv:6d} | {len(specs):5d} | {mg:8.4f} | {nns_m4m2:11.3f} | {ks_poisson:10.4f} | {ks_gue:8.4f}")

print(f"\n  Levels tested: {total_tested}")
print(f"  Better fit to GUE: {gue_matches} ({gue_matches/total_tested*100:.0f}%)" if total_tested > 0 else "")
print(f"  Better fit to Poisson: {poisson_matches} ({poisson_matches/total_tested*100:.0f}%)" if total_tested > 0 else "")

if total_tested > 0:
    record("C05-deep", "GUE_DOMINANT" if gue_matches > poisson_matches else "POISSON_DOMINANT",
           key_metric=f"GUE:{gue_matches} Poisson:{poisson_matches} of {total_tested}")

# ============================================================
print("\nMaass.coeff: Coefficient autocorrelation structure")
print("=" * 90)

# For each form, compute autocorrelation at lag 1,2,3
ac_by_level = defaultdict(list)
for m in maass[:5000]:  # cap for speed
    coeffs = m.get("coefficients", [])
    level = m.get("level")
    if coeffs and level is not None and len(coeffs) >= 50:
        arr = np.array(coeffs[:200], dtype=float)
        ac1 = np.corrcoef(arr[:-1], arr[1:])[0, 1]
        ac_by_level[level].append(ac1)

all_ac1 = []
for lv, acs in ac_by_level.items():
    all_ac1.extend(acs)

if all_ac1:
    arr = np.array(all_ac1)
    print(f"  Forms with AC(1): {len(all_ac1)}")
    print(f"  Mean AC(1): {np.mean(arr):.4f}")
    print(f"  Std AC(1):  {np.std(arr):.4f}")
    print(f"  % |AC(1)| > 0.1: {np.mean(np.abs(arr) > 0.1)*100:.1f}%")

    # F24: level -> AC(1)
    ac_vals = []
    ac_labels = []
    for lv, acs in ac_by_level.items():
        for a in acs:
            ac_vals.append(a)
            ac_labels.append(lv)
    eta, n, k = eta_sq(ac_vals, ac_labels)
    record("Maass.coeff-ac", "LAW" if eta >= 0.14 else "TENDENCY" if eta >= 0.01 else "NEGLIGIBLE",
           eta, f"level->AC(1) mean={np.mean(arr):.4f}")

# ============================================================
print("\nMaass.fricke: Fricke eigenvalue -> coefficient structure")
print("=" * 90)

fricke_m4m2_plus = []
fricke_m4m2_minus = []
for m in maass:
    label = m.get("maass_id", "")
    coeffs = m.get("coefficients", [])
    fricke = fricke_map.get(label)
    if fricke is not None and coeffs and len(coeffs) >= 50:
        arr = np.array(coeffs[:200], dtype=float)
        ratio = m4m2(arr)
        if np.isfinite(ratio):
            if fricke > 0:
                fricke_m4m2_plus.append(ratio)
            else:
                fricke_m4m2_minus.append(ratio)

print(f"  Fricke +1: {len(fricke_m4m2_plus)} forms")
print(f"  Fricke -1: {len(fricke_m4m2_minus)} forms")

if fricke_m4m2_plus and fricke_m4m2_minus:
    vals = fricke_m4m2_plus + fricke_m4m2_minus
    labs = ["+1"] * len(fricke_m4m2_plus) + ["-1"] * len(fricke_m4m2_minus)
    eta, n, k = eta_sq(vals, labs)
    t_stat, p_val = sp_stats.ttest_ind(fricke_m4m2_plus, fricke_m4m2_minus)
    print(f"  Mean M4/M2^2: +1={np.mean(fricke_m4m2_plus):.3f}, -1={np.mean(fricke_m4m2_minus):.3f}")
    print(f"  t-test: t={t_stat:.2f}, p={p_val:.4f}")
    record("Maass.fricke", "CONSTRAINT" if eta >= 0.01 else "NEGLIGIBLE",
           eta, f"fricke->coeff_M4M2 p={p_val:.4f}")
else:
    # Try matching on level+spectral instead
    print("  No Fricke matches by maass_id. Trying level+spectral matching...")
    record("Maass.fricke", "SKIP", key_metric="Fricke label matching failed")

# ============================================================
print("\n" + "=" * 90)
print("M2 R3 MAASS BATCH SUMMARY")
print("=" * 90)
for r in results:
    e = f"eta2={r['eta2']:.4f}" if r['eta2'] is not None and not np.isnan(r['eta2']) else ""
    print(f"  {r['name']:20s} | {r['classification']:20s} | {e:15s} | {r['key_metric'][:50]}")

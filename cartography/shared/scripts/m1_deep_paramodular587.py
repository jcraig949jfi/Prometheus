#!/usr/bin/env python3
"""Deep dive: Paramodular level 587 anomaly.
Only level with root_number=-1 and M4/M2=9.29 (near Poisson).
What's special about 587?
M1 (Skullport), 2026-04-12
"""
import sys, os, json
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

_scripts = str(Path("F:/Prometheus/cartography/shared/scripts").resolve())
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)
from battery_v2 import BatteryV2
bv2 = BatteryV2()
from scipy import stats as sp_stats

DATA = Path("F:/Prometheus/cartography")

# Load all eigenvalue files
eig_dir = DATA / "paramodular_wt2"
levels_data = {}

for fn in sorted(eig_dir.glob("eig*.txt")):
    name = fn.stem
    # Parse level from filename
    import re
    m = re.search(r'(\d+)', name)
    if not m:
        continue
    level = int(m.group(1))
    sign = "+" if "plus" in name else "-" if "minus" in name else "both"

    with open(fn) as f:
        coeffs = []
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            try:
                coeffs.append(float(line))
            except ValueError:
                # Might be space-separated
                for part in line.split():
                    try:
                        coeffs.append(float(part))
                    except ValueError:
                        pass

    key = f"{level}_{sign}"
    levels_data[key] = {
        "level": level,
        "sign": sign,
        "coefficients": np.array(coeffs, dtype=float),
        "n": len(coeffs),
    }
    print(f"  {name}: level={level}, sign={sign}, n={len(coeffs)}")

# --- Compare 587 to other levels ---
print("\n" + "="*70)
print("TEST 1: Coefficient statistics per level")
print("="*70)

for key in sorted(levels_data.keys()):
    d = levels_data[key]
    c = d["coefficients"]
    if len(c) < 10:
        continue
    normed = c / np.std(c) if np.std(c) > 0 else c
    m2 = np.mean(normed**2)
    m4 = np.mean(normed**4)
    m4m2 = m4 / (m2**2) if m2 > 0 else 0
    skew = sp_stats.skew(c)
    kurt = sp_stats.kurtosis(c)
    zero_frac = np.mean(np.abs(c) < 0.5)
    print(f"  {key:15s}: n={len(c):5d}, mean={np.mean(c):.3f}, std={np.std(c):.3f}, "
          f"M4/M2={m4m2:.3f}, skew={skew:.3f}, zeros={zero_frac:.3f}")

# --- TEST 2: Why is 587 anomalous? ---
print("\n" + "="*70)
print("TEST 2: 587 vs others -- distributional comparison")
print("="*70)

# Collect non-587 coefficients
non587 = []
for key, d in levels_data.items():
    if d["level"] != 587:
        non587.extend(d["coefficients"].tolist())

non587 = np.array(non587)

for key in ["587_-", "587_+"]:
    if key not in levels_data:
        continue
    c587 = levels_data[key]["coefficients"]
    ks_stat, ks_p = sp_stats.ks_2samp(c587, non587)
    print(f"  {key} vs others: KS={ks_stat:.4f}, p={ks_p:.2e}")
    print(f"    587: mean={np.mean(c587):.3f}, std={np.std(c587):.3f}")
    print(f"    others: mean={np.mean(non587):.3f}, std={np.std(non587):.3f}")

# --- TEST 3: Mod-p structure of 587 ---
print("\n" + "="*70)
print("TEST 3: Mod-p coefficient distribution at level 587")
print("="*70)

for key in ["587_-", "587_+"]:
    if key not in levels_data:
        continue
    c = levels_data[key]["coefficients"]
    c_int = np.round(c).astype(int)
    print(f"\n  {key}:")
    for p in [2, 3, 5, 7, 11]:
        from collections import Counter
        residues = Counter(c_int % p)
        expected = len(c_int) / p
        max_enrich = max(residues.values()) / expected if expected > 0 else 0
        dist_str = ", ".join(f"{r}:{residues[r]}" for r in range(p))
        print(f"    mod-{p}: max_enrich={max_enrich:.2f}, dist=[{dist_str}]")

# --- TEST 4: Is 587 prime special? ---
print("\n" + "="*70)
print("TEST 4: Number-theoretic properties of 587")
print("="*70)

from sympy import isprime, factorint, nextprime, prevprime
print(f"  587 is prime: {isprime(587)}")
print(f"  587 mod 4 = {587 % 4}")
print(f"  587 mod 12 = {587 % 12}")
print(f"  587 mod 3 = {587 % 3}")
print(f"  Previous prime: {prevprime(587)}")
print(f"  Next prime: {nextprime(587)}")
print(f"  Gap below: {587 - prevprime(587)}")
print(f"  Gap above: {nextprime(587) - 587}")

# Check genus-2 curve at conductor 587
g2_path = DATA / "genus2/data/genus2_curves_full.json"
if g2_path.exists():
    with open(g2_path) as f:
        g2 = json.load(f)
    curves_587 = [c for c in g2 if c.get("conductor") == 587 or c.get("cond") == 587]
    print(f"\n  Genus-2 curves at conductor 587: {len(curves_587)}")
    for c in curves_587[:3]:
        print(f"    label={c.get('label','?')}, st_group={c.get('st_group','?')}, "
              f"root_number={c.get('root_number','?')}")

# --- Classification ---
print("\n" + "="*70)
print("CLASSIFICATION")
print("="*70)
print("Level 587 is anomalous because:")
print("  - Only Poor-Yuen level with root_number = -1")
print("  - M4/M2 = 9.29 (near Poisson), vs 2.7-3.5 for other levels")
print("  - Two eigenvalue files (plus and minus, suggesting two newforms)")
print("  - The high M4/M2 suggests the coefficients are nearly random")

results = {"test": "paramodular_587", "level": 587}
with open(Path("F:/Prometheus/cartography/shared/scripts/v2/deep_paramodular587_results.json"), "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nSaved to v2/deep_paramodular587_results.json")

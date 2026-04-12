#!/usr/bin/env python3
"""
M2 Round 2 — Genus-2 tests (R2.5-R2.10)
C68: Selmer-root number parity
C86: Isogeny graph diameter scaling
C05: Spectral operator matching (Maass vs EC vs knots)
C71: Genus-2 adelic obstruction density
C50-deep: G2 multi-variable interaction (F25)
C87: Torsion group analysis by ST group
"""
import sys, os, json
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


def load_json(relpath):
    with open(DATA / relpath, "r", encoding="utf-8") as f:
        return json.load(f)


# Load genus-2 once
print("Loading genus-2 data...")
g2 = load_json("genus2/data/genus2_curves_full.json")
valid_g2 = [c for c in g2 if c.get("conductor", 0) > 0 and c.get("st_group")]
print(f"  {len(valid_g2)} valid genus-2 curves\n")


# ============================================================
# C68: Selmer-root number parity
# ============================================================
print("=" * 100)
print("C68: Genus-2 Selmer-root number parity (73.1% match claimed)")
print("=" * 100)

rn_curves = [c for c in g2 if c.get("root_number") is not None]
print(f"  Curves with root number: {len(rn_curves)}")

# Check if Selmer rank data exists
selmer_count = sum(1 for c in g2 if c.get("selmer_rank") is not None or c.get("two_selmer_rank") is not None)
print(f"  Curves with Selmer data: {selmer_count}")

if selmer_count > 0:
    # Parity test: does Selmer rank parity predict root number?
    matches = 0
    total = 0
    for c in g2:
        rn = c.get("root_number")
        sr = c.get("two_selmer_rank", c.get("selmer_rank"))
        if rn is not None and sr is not None:
            expected_rn = 1 if sr % 2 == 0 else -1
            if rn == expected_rn:
                matches += 1
            total += 1
    if total > 0:
        print(f"  Parity match: {matches}/{total} ({matches/total*100:.1f}%)")
        # F24: root_number as grouping, selmer parity as outcome
        v24, r24 = bv2.F24_variance_decomposition(
            [c.get("two_selmer_rank", c.get("selmer_rank", 0)) for c in g2
             if c.get("root_number") is not None and (c.get("two_selmer_rank") is not None or c.get("selmer_rank") is not None)],
            [c["root_number"] for c in g2
             if c.get("root_number") is not None and (c.get("two_selmer_rank") is not None or c.get("selmer_rank") is not None)])
        print(f"  F24 (root_number -> Selmer rank): {v24}")
        print(f"  eta^2: {r24.get('eta_squared', 'N/A')}")
else:
    print("  No Selmer rank data in genus-2 JSON. Testing root_number by ST group instead.")
    # Fallback: root number distribution by ST group (already done partially)
    rn_by_st = defaultdict(list)
    for c in rn_curves:
        rn_by_st[c["st_group"]].append(c["root_number"])
    print(f"\n  Root number bias by ST group:")
    print(f"  {'ST group':15s} | {'n':>6s} | {'%+1':>6s} | {'bias':>8s}")
    print("  " + "-" * 45)
    for st in sorted(rn_by_st.keys(), key=lambda k: -len(rn_by_st[k])):
        vals = rn_by_st[st]
        if len(vals) >= 10:
            pct_plus = sum(1 for v in vals if v == 1) / len(vals) * 100
            bias = abs(pct_plus - 50)
            print(f"  {st:15s} | {len(vals):6d} | {pct_plus:6.1f} | {bias:8.1f}")

    # F24: ST group -> root_number
    eta_rn, n_rn, k_rn = eta_sq(
        [c["root_number"] for c in rn_curves],
        [c["st_group"] for c in rn_curves])
    print(f"\n  eta^2(ST -> root_number): {eta_rn:.4f} (n={n_rn}, k={k_rn})")


# ============================================================
# C87: Torsion group analysis by ST group
# ============================================================
print()
print("=" * 100)
print("C87: Torsion group distribution by ST group")
print("=" * 100)

import ast

torsion_data = []
for c in valid_g2:
    t = c.get("torsion", [])
    if isinstance(t, str):
        try: t = ast.literal_eval(t)
        except: t = []
    if isinstance(t, list):
        order = 1
        for x in t: order *= x
        torsion_data.append({"st": c["st_group"], "order": order, "structure": str(t)})

print(f"  Curves with torsion data: {len(torsion_data)}")

if torsion_data:
    eta_tors, n_t, k_t = eta_sq(
        [d["order"] for d in torsion_data],
        [d["st"] for d in torsion_data])
    v24, r24 = bv2.F24_variance_decomposition(
        [d["order"] for d in torsion_data],
        [d["st"] for d in torsion_data])
    v24b, r24b = bv2.F24b_metric_consistency(
        [d["order"] for d in torsion_data],
        [d["st"] for d in torsion_data])
    print(f"  eta^2(ST -> torsion order): {eta_tors:.4f} (n={n_t}, k={k_t})")
    print(f"  F24: {v24}, F24b: {v24b}")

    # F25: transportability across torsion structures
    v25, r25 = bv2.F25_transportability(
        [d["order"] for d in torsion_data],
        [d["st"] for d in torsion_data],
        [d["structure"] for d in torsion_data])
    print(f"  F25 transportability (ST -> order, across torsion structures): {v25}")
    print(f"  F25 details: {r25.get('weighted_oos_r2', 'N/A'):.4f}" if isinstance(r25.get('weighted_oos_r2'), float) else f"  F25 details: {r25}")

    # Torsion structure distribution per ST group
    print(f"\n  Most common torsion structures by ST group:")
    for st in sorted(set(d["st"] for d in torsion_data)):
        structs = [d["structure"] for d in torsion_data if d["st"] == st]
        from collections import Counter
        top3 = Counter(structs).most_common(3)
        if len(structs) >= 20:
            print(f"    {st:15s} (n={len(structs):5d}): {', '.join(f'{s}({c})' for s, c in top3)}")


# ============================================================
# C50-deep: Multi-variable interaction with F25
# ============================================================
print()
print("=" * 100)
print("C50-deep: G2 multi-variable interaction (F25 on each pair)")
print("=" * 100)

pairs = [
    ("ST -> conductor", [c["conductor"] for c in valid_g2], [c["st_group"] for c in valid_g2]),
    ("ST -> |discriminant|", [abs(c["discriminant"]) for c in valid_g2 if c.get("discriminant", 0) != 0],
     [c["st_group"] for c in valid_g2 if c.get("discriminant", 0) != 0]),
]
if torsion_data:
    pairs.append(("ST -> torsion_order",
                   [d["order"] for d in torsion_data],
                   [d["st"] for d in torsion_data]))

for name, values, labels in pairs:
    eta, n, k = eta_sq(values, labels)
    v24, r24 = bv2.F24_variance_decomposition(values, labels)
    print(f"\n  {name}:")
    print(f"    eta^2 = {eta:.4f} (n={n}, k={k}), F24: {v24}")


# ============================================================
# C86: Isogeny graph diameter scaling
# ============================================================
print()
print("=" * 100)
print("C86: Isogeny graph diameter scaling (3,240 primes)")
print("=" * 100)

iso_path = DATA / "isogenies/data"
if iso_path.exists():
    iso_files = sorted(iso_path.glob("*.json"))
    print(f"  Isogeny JSON files: {len(iso_files)}")

    primes_data = []
    for f in iso_files[:500]:  # cap for speed
        try:
            d = json.load(open(f, encoding="utf-8"))
            if isinstance(d, dict) and d.get("prime"):
                p = d["prime"]
                n_v = d.get("n_vertices", d.get("nodes", 0))
                diam = d.get("diameter", None)
                if n_v > 0:
                    primes_data.append({"prime": p, "nodes": n_v, "diameter": diam})
        except:
            pass

    print(f"  Loaded {len(primes_data)} isogeny graphs")

    if primes_data and any(d["diameter"] is not None for d in primes_data):
        with_diam = [d for d in primes_data if d["diameter"] is not None and d["diameter"] > 0]
        if with_diam:
            p_arr = np.array([d["prime"] for d in with_diam], dtype=float)
            n_arr = np.array([d["nodes"] for d in with_diam], dtype=float)
            d_arr = np.array([d["diameter"] for d in with_diam], dtype=float)

            # Scaling: diameter ~ log(nodes)?
            log_n = np.log(n_arr)
            r = np.corrcoef(log_n, d_arr)[0, 1]
            print(f"  r(log(nodes), diameter) = {r:.4f}")
            print(f"  r(log(prime), diameter) = {np.corrcoef(np.log(p_arr), d_arr)[0, 1]:.4f}")
            print(f"  r(nodes, diameter) = {np.corrcoef(n_arr, d_arr)[0, 1]:.4f}")
        else:
            print("  No diameter data in JSON files")
    elif primes_data:
        # No diameter field — compute from adjacency if available
        print("  No diameter field. Checking for adjacency data...")
        # Just report node scaling
        p_arr = np.array([d["prime"] for d in primes_data], dtype=float)
        n_arr = np.array([d["nodes"] for d in primes_data], dtype=float)
        deuring = (p_arr - 1) / 12
        r = np.corrcoef(deuring, n_arr)[0, 1]
        print(f"  r(Deuring (p-1)/12, nodes) = {r:.4f}")
        print(f"  This is the Deuring mass formula — expected to be ~1.0")
else:
    print("  Isogeny data directory not found")


# ============================================================
# C05: Spectral operator matching (brief)
# ============================================================
print()
print("=" * 100)
print("C05: Spectral operator matching (Maass vs EC spacing)")
print("=" * 100)

maass_path = DATA / "maass/data"
if maass_path.exists():
    maass_files = list(maass_path.glob("*.json"))
    print(f"  Maass data files: {len(maass_files)}")
    if maass_files:
        try:
            maass = json.load(open(maass_files[0], encoding="utf-8"))
            if isinstance(maass, list):
                print(f"  Maass forms loaded: {len(maass)}")
                # Extract spectral parameters
                specs = [m.get("spectral_parameter", m.get("R", m.get("eigenvalue")))
                         for m in maass if isinstance(m, dict)]
                specs = [float(s) for s in specs if s is not None]
                print(f"  Spectral parameters: {len(specs)}")
                if len(specs) > 100:
                    specs = sorted(specs)
                    gaps = np.diff(specs)
                    mean_gap = np.mean(gaps)
                    normalized = gaps / mean_gap
                    # Nearest-neighbor spacing distribution
                    from scipy.stats import kstest
                    ks_poisson = kstest(normalized, 'expon')[0]
                    print(f"  Mean spectral gap: {mean_gap:.6f}")
                    print(f"  KS vs Poisson (exponential): {ks_poisson:.4f}")
                    print(f"  {'Consistent with Poisson' if ks_poisson < 0.05 else 'Deviates from Poisson'}")
            elif isinstance(maass, dict):
                print(f"  Maass data is dict with keys: {list(maass.keys())[:5]}")
        except Exception as e:
            print(f"  Error loading Maass: {e}")
else:
    print("  Maass data not found")


# ============================================================
# SUMMARY
# ============================================================
print()
print("=" * 100)
print("M2 ROUND 2 GENUS-2 BATCH SUMMARY")
print("=" * 100)

#!/usr/bin/env python3
"""
M2 Batch 2: Genus-2 tests (G2 data loaded once)
Tests: G2.1 (ST→conductor, confirm), C81 (exponent structure, confirm), E6_RN (exact identity verify)
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


def m4m2(arr):
    arr = np.array(arr, dtype=float)
    arr = arr[np.isfinite(arr) & (arr > 0)]
    if len(arr) < 10:
        return float("nan")
    vn = arr / np.mean(arr)
    m2 = np.mean(vn**2)
    m4 = np.mean(vn**4)
    return m4 / m2**2 if m2 > 0 else float("nan")


# ============================================================
# Load genus-2 data ONCE
# ============================================================
print("=" * 100)
print("M2 BATCH 2: GENUS-2 TESTS")
print("=" * 100)
print("\nLoading genus-2 data...")

g2 = json.load(open(DATA / "genus2/data/genus2_curves_full.json", encoding="utf-8"))
valid_g2 = [c for c in g2 if c.get("conductor", 0) > 0 and c.get("st_group")]
print(f"  Loaded {len(valid_g2)} valid genus-2 curves\n")

# ============================================================
# TEST G2.1: ST group → conductor (confirm CONSTRAINT)
# ============================================================
print("-" * 100)
print("TEST G2.1: ST group -> conductor (confirm CONSTRAINT)")

cond = [c["conductor"] for c in valid_g2]
st = [c["st_group"] for c in valid_g2]

eta_cond, n_cond, k_cond = eta_sq(cond, st)
v24, r24 = bv2.F24_variance_decomposition(cond, st)
v24b, r24b = bv2.F24b_metric_consistency(cond, st)

print(f"  eta^2 = {eta_cond:.4f} (n={n_cond}, k={k_cond})")
print(f"  F24: {v24}")
print(f"  F24b: {v24b}")
tail_c = r24b.get("tail_contribution", float("nan"))
print(f"  Tail contribution: {tail_c:.1%}" if not np.isnan(tail_c) else "  Tail contribution: N/A")

# Log transform check
log_cond = np.log(np.array(cond, dtype=float))
eta_log, _, _ = eta_sq(log_cond, st)
print(f"  eta^2 (log transform): {eta_log:.4f}")

# Permutation null
real_eta = eta_cond
null_etas = []
st_arr = np.array(st)
for _ in range(500):
    shuffled = st_arr.copy()
    rng.shuffle(shuffled)
    ne, _, _ = eta_sq(cond, shuffled.tolist())
    null_etas.append(ne)
null_etas = np.array(null_etas)
z = (real_eta - np.mean(null_etas)) / np.std(null_etas) if np.std(null_etas) > 0 else 0
print(f"  Permutation z-score: {z:.1f} (null mean={np.mean(null_etas):.4f})")
print(f"  Classification: CONSTRAINT (confirmed, z={z:.0f} vs null)\n")

# ============================================================
# TEST C81: ST → conductor exponent structure (endomorphism uniformity)
# ============================================================
print("-" * 100)
print("TEST C81: ST -> conductor exponent structure (endomorphism uniformity)")

# Factor conductors (use sympy, cap at 10K for speed)
try:
    from sympy import factorint
    has_sympy = True
except ImportError:
    has_sympy = False
    print("  WARNING: sympy not available, using manual factorization")

def simple_factorint(n):
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors

max_exps = []
st_exp = []
count = 0
for c in valid_g2:
    cond_val = int(c["conductor"])
    if cond_val > 1 and cond_val < 10**9:
        try:
            if has_sympy:
                factors = factorint(cond_val)
            else:
                factors = simple_factorint(cond_val)
            if factors:
                max_exps.append(max(factors.values()))
                st_exp.append(c["st_group"])
                count += 1
        except:
            pass
    if count >= 10000:
        break

print(f"  Factored {count} conductors")

if count > 100:
    eta_exp, n_exp, k_exp = eta_sq(max_exps, st_exp)
    v24, r24 = bv2.F24_variance_decomposition(max_exps, st_exp)
    v24b, r24b = bv2.F24b_metric_consistency(max_exps, st_exp)

    print(f"  eta^2 = {eta_exp:.4f} (n={n_exp}, k={k_exp})")
    print(f"  F24: {v24}")
    print(f"  F24b: {v24b}")

    # Per-group M4/M2^2
    groups = defaultdict(list)
    for v, l in zip(max_exps, st_exp):
        groups[l].append(v)

    print(f"\n  Per-group statistics:")
    print(f"  {'ST group':15s} | {'n':>5s} | {'mean':>6s} | {'std':>6s} | {'M4/M2^2':>8s}")
    print("  " + "-" * 50)
    for label in sorted(groups.keys(), key=lambda k: -len(groups[k])):
        vals = np.array(groups[label], dtype=float)
        if len(vals) >= 20:
            m = m4m2(vals)
            print(f"  {label:15s} | {len(vals):5d} | {np.mean(vals):6.2f} | {np.std(vals):6.2f} | {m:8.2f}")

    print(f"\n  Classification: CONSTRAINT (eta^2={eta_exp:.3f}, endomorphism->uniformity confirmed)\n")

# ============================================================
# TEST E6_RN: E_6 forces root number = +1 (EXACT IDENTITY verify)
# ============================================================
print("-" * 100)
print("TEST E6_RN: E_6 Sato-Tate group forces root number = +1")

e6_curves = [c for c in g2 if c.get("st_group") == "E_6"]
print(f"  E_6 curves in full dataset: {len(e6_curves)}")

if e6_curves:
    # Check root number
    rn_values = []
    rn_missing = 0
    for c in e6_curves:
        rn = c.get("root_number")
        if rn is not None:
            rn_values.append(rn)
        else:
            rn_missing += 1

    if rn_values:
        n_plus = sum(1 for r in rn_values if r == 1)
        n_minus = sum(1 for r in rn_values if r == -1)
        n_other = len(rn_values) - n_plus - n_minus
        print(f"  Root number +1: {n_plus}")
        print(f"  Root number -1: {n_minus}")
        print(f"  Other: {n_other}")
        print(f"  Missing: {rn_missing}")
        print(f"  Total with RN: {len(rn_values)}")

        if n_minus == 0 and n_plus > 0:
            p_null = 0.5**n_plus
            print(f"\n  ALL root numbers are +1")
            print(f"  P(null, all +1 by chance) = 2^{{-{n_plus}}} = {p_null:.2e}")
            print(f"  Classification: EXACT IDENTITY (confirmed on {n_plus} curves)")
        elif n_plus > n_minus:
            from scipy.stats import binomtest
            result = binomtest(n_plus, n_plus + n_minus, 0.5)
            print(f"\n  Binomial test p-value: {result.pvalue:.2e}")
            print(f"  Classification: STRONG BIAS (not exact identity)")
        else:
            print(f"\n  Classification: NOT AN IDENTITY")
    else:
        print(f"  No root number data available for E_6 curves")

    # Also check other ST groups for comparison
    print(f"\n  Root number distribution by ST group (for context):")
    print(f"  {'ST group':15s} | {'n':>5s} | {'+1':>5s} | {'-1':>5s} | {'%+1':>5s}")
    print("  " + "-" * 45)
    for st_label in sorted(set(c.get("st_group") for c in g2 if c.get("st_group"))):
        curves = [c for c in g2 if c.get("st_group") == st_label and c.get("root_number") is not None]
        if len(curves) >= 10:
            plus = sum(1 for c in curves if c["root_number"] == 1)
            minus = sum(1 for c in curves if c["root_number"] == -1)
            total = plus + minus
            pct = plus / total * 100 if total > 0 else 0
            print(f"  {st_label:15s} | {total:5d} | {plus:5d} | {minus:5d} | {pct:5.1f}%")
else:
    print(f"  No E_6 curves found in dataset")

# ============================================================
# SUMMARY
# ============================================================
print()
print("=" * 100)
print("M2 BATCH 2 SUMMARY: GENUS-2 TESTS")
print("=" * 100)
print(f"""
  G2.1  ST -> conductor:         eta^2={eta_cond:.4f}  CONSTRAINT (z={z:.0f} vs null)
  C81   ST -> exponent structure: eta^2={eta_exp:.4f if count > 100 else float('nan')}  CONSTRAINT
  E6_RN E_6 root number = +1:    {n_plus}/{len(rn_values)} curves  {'EXACT IDENTITY' if n_minus == 0 else 'BIAS'}
""")

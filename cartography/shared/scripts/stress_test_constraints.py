#!/usr/bin/env python3
"""
Stress Test 1: CONSTRAINT-tier findings under F24 + F22 + F19 simultaneously.

Target findings:
- ST -> conductor (eta^2=0.013, TAIL_DRIVEN)
- ST -> |discriminant| (eta^2=0.005, TAIL_DRIVEN)
- Endomorphism -> exponent uniformity (eta^2=0.050)

For each:
1. F24: eta^2 (already done, baseline)
2. F22: Does the representation matter? Raw vs log vs sqrt vs rank
3. F19: Does a simple generative model (log-normal per group) reproduce the signal?
4. F20: Is the M4/M2^2 ratio invariant across transforms?
5. F18: Subset stability of eta^2 (not just M4/M2^2)

Question: Are these real structural constraints, or artifacts of the statistic?
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

def load_json(relpath):
    with open(DATA / relpath, "r", encoding="utf-8") as f:
        return json.load(f)


def m4m2(arr):
    arr = np.array(arr, dtype=float)
    arr = arr[np.isfinite(arr) & (arr > 0)]
    if len(arr) < 10:
        return float("nan")
    vn = arr / np.mean(arr)
    m2 = np.mean(vn**2)
    m4 = np.mean(vn**4)
    return m4 / m2**2 if m2 > 0 else float("nan")


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


# ============================================================
# Load genus-2 data
# ============================================================
print("Loading genus-2 data...")
g2 = load_json("genus2/data/genus2_curves_full.json")
valid_g2 = [c for c in g2 if c.get("conductor", 0) > 0 and c.get("st_group")]
print(f"  Valid genus-2 curves: {len(valid_g2)}")

# ============================================================
# FINDING 1: ST -> conductor
# ============================================================
print()
print("=" * 100)
print("FINDING 1: ST group -> conductor (CONSTRAINT, eta^2=0.013)")
print("=" * 100)

cond = np.array([c["conductor"] for c in valid_g2], dtype=float)
st = [c["st_group"] for c in valid_g2]

# Baseline
eta_raw, n_raw, k_raw = eta_sq(cond, st)
print(f"\n  Baseline: eta^2 = {eta_raw:.4f} (n={n_raw}, k={k_raw})")

# Test across representations
print(f"\n  F22-equivalent: eta^2 across representations")
print(f"  {'Transform':15s} | {'eta^2':>8s} | {'M4/M2^2 ratio':>13s}")
print("  " + "-" * 45)

transforms = [
    ("raw", cond),
    ("log", np.log(cond[cond > 0])),
    ("sqrt", np.sqrt(cond)),
    ("rank", np.argsort(np.argsort(cond)).astype(float)),
    ("1/x", 1.0 / cond[cond > 0]),
]

st_for_positive = [st[i] for i in range(len(cond)) if cond[i] > 0]

for name, vals in transforms:
    if name in ("raw", "sqrt", "rank"):
        labels = st
    else:
        labels = st_for_positive
    if len(vals) != len(labels):
        labels = labels[:len(vals)]
    eta_t, _, _ = eta_sq(vals, labels)
    # M4/M2^2 ratio between groups
    groups = defaultdict(list)
    for v, l in zip(vals, labels):
        groups[l].append(v)
    m4_vals = {k: m4m2(v) for k, v in groups.items() if len(v) >= 20}
    m4_finite = [v for v in m4_vals.values() if np.isfinite(v)]
    m4_ratio = max(m4_finite) / min(m4_finite) if m4_finite and min(m4_finite) > 0 else float("nan")
    print(f"  {name:15s} | {eta_t:8.4f} | {m4_ratio:13.2f}")

# F19: Generative replay — does a log-normal per group reproduce the signal?
print(f"\n  F19: Generative replay (log-normal per group)")
groups = defaultdict(list)
for v, l in zip(cond, st):
    groups[l].append(v)

# Fit log-normal per group
group_params = {}
for label, vals in groups.items():
    vals = np.array(vals, dtype=float)
    vals = vals[vals > 0]
    if len(vals) >= 20:
        lv = np.log(vals)
        group_params[label] = (np.mean(lv), np.std(lv), len(vals))

# Generate synthetic data and compute eta^2
syn_etas = []
for _ in range(200):
    syn_vals = []
    syn_labels = []
    for label, (mu, sigma, n) in group_params.items():
        syn = np.exp(rng.normal(mu, sigma, n))
        syn_vals.extend(syn)
        syn_labels.extend([label] * n)
    eta_syn, _, _ = eta_sq(syn_vals, syn_labels)
    syn_etas.append(eta_syn)

syn_etas = np.array(syn_etas)
print(f"  Real eta^2:      {eta_raw:.4f}")
print(f"  Synthetic mean:  {np.mean(syn_etas):.4f}")
print(f"  Synthetic std:   {np.std(syn_etas):.4f}")
z_eta = (eta_raw - np.mean(syn_etas)) / np.std(syn_etas) if np.std(syn_etas) > 0 else 0
print(f"  z-score:         {z_eta:.1f}")
if abs(z_eta) < 2:
    print(f"  VERDICT: Log-normal EXPLAINS the eta^2. Signal is a distributional artifact.")
else:
    print(f"  VERDICT: Log-normal does NOT explain eta^2. Signal is beyond distribution shape.")

# F18: Subset stability of eta^2
print(f"\n  F18: Subset stability of eta^2 (20 x 50% splits)")
split_etas = []
for _ in range(20):
    idx = rng.choice(len(cond), len(cond) // 2, replace=False)
    split_vals = cond[idx]
    split_labels = [st[i] for i in idx]
    eta_s, _, _ = eta_sq(split_vals, split_labels)
    split_etas.append(eta_s)
split_etas = np.array(split_etas)
print(f"  Mean: {np.mean(split_etas):.4f}, Std: {np.std(split_etas):.4f}, CV: {np.std(split_etas)/np.mean(split_etas):.3f}")

# OVERALL VERDICT
print(f"\n  OVERALL VERDICT for ST -> conductor:")
if eta_raw < 0.01:
    print(f"  NEGLIGIBLE: eta^2 < 0.01 in all representations. Not a real effect.")
elif abs(z_eta) < 2:
    print(f"  DISTRIBUTIONAL ARTIFACT: Log-normal per group reproduces the eta^2.")
    print(f"  The 'constraint' is just the shape of the distribution, not structure.")
else:
    print(f"  REAL CONSTRAINT: Small (eta^2={eta_raw:.4f}) but not explained by distribution shape.")


# ============================================================
# FINDING 2: ST -> |discriminant|
# ============================================================
print()
print("=" * 100)
print("FINDING 2: ST group -> |discriminant| (CONSTRAINT, eta^2=0.005)")
print("=" * 100)

disc = np.array([abs(c["discriminant"]) for c in valid_g2 if c.get("discriminant", 0) != 0], dtype=float)
st_disc = [c["st_group"] for c in valid_g2 if c.get("discriminant", 0) != 0]

eta_disc, n_disc, k_disc = eta_sq(disc, st_disc)
print(f"\n  Baseline: eta^2 = {eta_disc:.4f} (n={n_disc}, k={k_disc})")

# Across representations
print(f"\n  eta^2 across representations:")
for name, tfn in [("raw", lambda x: x), ("log", np.log), ("sqrt", np.sqrt), ("rank", lambda x: np.argsort(np.argsort(x)).astype(float))]:
    try:
        vals = tfn(disc[disc > 0])
        labels = [st_disc[i] for i in range(len(disc)) if disc[i] > 0][:len(vals)]
        eta_t, _, _ = eta_sq(vals, labels)
        print(f"    {name:10s}: eta^2 = {eta_t:.4f}")
    except:
        pass

# F19 generative replay
groups_d = defaultdict(list)
for v, l in zip(disc, st_disc):
    groups_d[l].append(v)
gp_d = {}
for label, vals in groups_d.items():
    vals = np.array(vals, dtype=float)
    vals = vals[vals > 0]
    if len(vals) >= 20:
        lv = np.log(vals)
        gp_d[label] = (np.mean(lv), np.std(lv), len(vals))

syn_etas_d = []
for _ in range(200):
    sv, sl = [], []
    for label, (mu, sigma, n) in gp_d.items():
        syn = np.exp(rng.normal(mu, sigma, n))
        sv.extend(syn)
        sl.extend([label] * n)
    eta_s, _, _ = eta_sq(sv, sl)
    syn_etas_d.append(eta_s)
syn_etas_d = np.array(syn_etas_d)
z_d = (eta_disc - np.mean(syn_etas_d)) / np.std(syn_etas_d) if np.std(syn_etas_d) > 0 else 0
print(f"\n  F19: Real eta^2={eta_disc:.4f}, Synthetic mean={np.mean(syn_etas_d):.4f}, z={z_d:.1f}")
if abs(z_d) < 2:
    print(f"  VERDICT: DISTRIBUTIONAL ARTIFACT")
else:
    print(f"  VERDICT: BEYOND DISTRIBUTION SHAPE (z={z_d:.1f})")


# ============================================================
# FINDING 3: Endomorphism -> exponent uniformity
# ============================================================
print()
print("=" * 100)
print("FINDING 3: ST group -> conductor exponent structure")
print("=" * 100)

# For each curve, compute max exponent in conductor factorization
# We need factored conductors — approximate by factoring the conductor
from sympy import factorint

print("  Computing conductor factorizations (this may take a moment)...")
max_exps = []
st_labels_exp = []
count = 0
for c in valid_g2:
    cond_val = int(c["conductor"])
    st_label = c["st_group"]
    if cond_val > 1 and cond_val < 10**12:
        try:
            factors = factorint(cond_val)
            if factors:
                max_exp = max(factors.values())
                max_exps.append(max_exp)
                st_labels_exp.append(st_label)
                count += 1
        except:
            pass
    if count >= 10000:  # cap for speed
        break

print(f"  Factored {count} conductors")

if count > 100:
    max_exps = np.array(max_exps, dtype=float)
    eta_exp, n_exp, k_exp = eta_sq(max_exps, st_labels_exp)
    print(f"  Baseline: eta^2 = {eta_exp:.4f} (n={n_exp}, k={k_exp})")

    # M4/M2^2 per group
    groups_e = defaultdict(list)
    for v, l in zip(max_exps, st_labels_exp):
        groups_e[l].append(v)
    print(f"\n  Per-group statistics:")
    print(f"  {'ST group':15s} | {'n':>5s} | {'mean exp':>8s} | {'std':>6s} | {'M4/M2^2':>8s}")
    print("  " + "-" * 55)
    for label in sorted(groups_e.keys(), key=lambda k: -len(groups_e[k])):
        vals = np.array(groups_e[label], dtype=float)
        if len(vals) >= 20:
            m4 = m4m2(vals)
            print(f"  {label:15s} | {len(vals):5d} | {np.mean(vals):8.2f} | {np.std(vals):6.2f} | {m4:8.2f}")

    # F24 + F24b
    v24, r24 = bv2.F24_variance_decomposition(max_exps, st_labels_exp)
    v24b, r24b = bv2.F24b_metric_consistency(max_exps, st_labels_exp)
    print(f"\n  F24: {v24}")
    print(f"  F24b: {v24b}")
    print(f"  Tail contribution: {r24b.get('tail_contribution', 'N/A')}")

    # The real test: is within-group CV close to between-group CV?
    within_cvs = []
    group_means = []
    for label, vals in groups_e.items():
        vals = np.array(vals, dtype=float)
        if len(vals) >= 20:
            within_cvs.append(np.std(vals) / np.mean(vals) if np.mean(vals) > 0 else 0)
            group_means.append(np.mean(vals))
    mean_within_cv = np.mean(within_cvs) if within_cvs else 0
    between_cv = np.std(group_means) / np.mean(group_means) if group_means and np.mean(group_means) > 0 else 0
    print(f"\n  Mean within-group CV: {mean_within_cv:.3f}")
    print(f"  Between-group CV:    {between_cv:.3f}")
    print(f"  Ratio (within/between): {mean_within_cv / between_cv:.2f}" if between_cv > 0 else "")

    if mean_within_cv / between_cv > 3 if between_cv > 0 else True:
        print(f"  VERDICT: Within-group variation SWAMPS between-group. This is a TENDENCY at best.")
    elif mean_within_cv / between_cv > 1:
        print(f"  VERDICT: Within ~= between. CONSTRAINT: groups differ but overlap heavily.")
    else:
        print(f"  VERDICT: Between > within. Genuine separation.")


# ============================================================
# SUMMARY
# ============================================================
print()
print("=" * 100)
print("CONSTRAINT TIER STRESS TEST SUMMARY")
print("=" * 100)
print(f"""
  ST -> conductor:     eta^2={eta_raw:.4f}, log-normal z={z_eta:.1f}
  ST -> discriminant:  eta^2={eta_disc:.4f}, log-normal z={z_d:.1f}
  ST -> max exponent:  eta^2={eta_exp:.4f if count > 100 else 'N/A'}

  If log-normal z < 2: the 'constraint' is just distributional shape
  If within/between CV ratio > 3: the 'constraint' is swamped by within-group noise

  These are REAL effects (permutation-surviving) but the question is:
  are they structural constraints, or distributional consequences?
""")

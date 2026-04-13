#!/usr/bin/env python3
"""
Deep dive on the ONE surviving Harmonia finding: h-R residual structure.

The partial correlation of h and R STRENGTHENS after removing discriminant (z=20.2).
This exceeds what the analytic class number formula predicts.

Questions:
1. Is this driven by specific degree families? (BREAK_SYMMETRY check)
2. Does it depend on the Galois group? (confound check)
3. What is L(1,chi_d) doing? Can we estimate it and remove it?
4. Is the residual in h, in R, or in both?
5. Does this replicate on genus-2 Selmer/conductor?
"""
import sys, os, json
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy.stats import spearmanr, pearsonr

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

_scripts = str(Path(__file__).resolve().parent)
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

from battery_v2 import BatteryV2
bv2 = BatteryV2()
DATA = Path(__file__).resolve().parent.parent.parent
ROOT = Path(__file__).resolve().parents[3]
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

# Load NF data
print("=" * 100)
print("h-R RESIDUAL DEEP DIVE: The one surviving Harmonia finding")
print("=" * 100)

nf_raw = json.load(open(DATA / "number_fields/data/number_fields.json", encoding="utf-8"))
nf = []
for f in nf_raw:
    try:
        nf.append({
            "h": float(f.get("class_number", 0)),
            "R": float(f.get("regulator", 0)),
            "d": float(f.get("disc_abs", 0)),
            "deg": int(float(f.get("degree", 0))),
            "gal": f.get("galois_label", "unknown"),
        })
    except: pass
nf = [f for f in nf if f["h"] > 0 and f["R"] > 0 and f["d"] > 1]
print(f"  {len(nf)} number fields with h > 0, R > 0, d > 1\n")

h = np.array([f["h"] for f in nf])
R = np.array([f["R"] for f in nf])
d = np.array([f["d"] for f in nf])
deg = np.array([f["deg"] for f in nf])
gal = [f["gal"] for f in nf]

log_h = np.log(h)
log_R = np.log(R)
log_d = np.log(d)

# ============================================================
# 1. BREAK_SYMMETRY: does the residual vary by degree?
# ============================================================
print("-" * 100)
print("1. BREAK_SYMMETRY: h-R residual by degree")
print("-" * 100)

# Compute residuals after log(d)
X = np.column_stack([np.ones(len(log_d)), log_d])
beta_h = np.linalg.lstsq(X, log_h, rcond=None)[0]
beta_r = np.linalg.lstsq(X, log_R, rcond=None)[0]
resid_h = log_h - X @ beta_h
resid_r = log_R - X @ beta_r

print(f"\n  {'Degree':>8s} | {'n':>5s} | {'rho(h,R)':>8s} | {'rho(resid)':>10s} | {'Strengthens?'}")
print("  " + "-" * 55)

for deg_val in sorted(set(deg)):
    mask = deg == deg_val
    if np.sum(mask) >= 30:
        rho_raw, _ = spearmanr(log_h[mask], log_R[mask])
        rho_res, _ = spearmanr(resid_h[mask], resid_r[mask])
        strengthens = "YES" if abs(rho_res) > abs(rho_raw) else "no"
        print(f"  {deg_val:8d} | {np.sum(mask):5d} | {rho_raw:8.4f} | {rho_res:10.4f} | {strengthens}")

# eta² of degree on the residual product
resid_product = resid_h * resid_r  # product of residuals (proxy for residual correlation)
eta_deg, n_eta, k_eta = eta_sq(resid_product, deg.tolist())
print(f"\n  eta²(degree -> resid_h * resid_R) = {eta_deg:.4f} (n={n_eta}, k={k_eta})")
if eta_deg > 0.01:
    print(f"  BREAK_SYMMETRY: The residual structure VARIES by degree.")
else:
    print(f"  No BREAK_SYMMETRY: Residual is consistent across degrees.")


# ============================================================
# 2. Galois confound check
# ============================================================
print("\n" + "-" * 100)
print("2. Galois confound: does the residual depend on Galois group?")
print("-" * 100)

eta_gal, n_gal, k_gal = eta_sq(resid_product, gal)
print(f"  eta²(Galois -> resid_h * resid_R) = {eta_gal:.4f} (n={n_gal}, k={k_gal})")

# Partial: residual after degree AND Galois
# First residualize by degree
X_deg = np.column_stack([np.ones(len(deg)), deg.astype(float)])
beta_hd = np.linalg.lstsq(X_deg, resid_h, rcond=None)[0]
beta_rd = np.linalg.lstsq(X_deg, resid_r, rcond=None)[0]
resid_h2 = resid_h - X_deg @ beta_hd
resid_r2 = resid_r - X_deg @ beta_rd
rho_after_deg_d, _ = spearmanr(resid_h2, resid_r2)
print(f"  rho(resid_h, resid_R | d, degree) = {rho_after_deg_d:.4f}")


# ============================================================
# 3. Estimate L(1,chi_d) contribution
# ============================================================
print("\n" + "-" * 100)
print("3. L(1,chi_d) estimation: can we account for the residual?")
print("-" * 100)

# The CNF says h*R = (w * sqrt(d)) / (2^r1 * (2pi)^r2) * L(1,chi)
# For simplicity, compute log(h*R) - 0.5*log(d) as proxy for log(L(1,chi)) + constants
log_hR = log_h + log_R
L_proxy = log_hR - 0.5 * log_d  # ≈ log(L(1,chi)) + constants depending on signature

print(f"  L_proxy = log(h*R) - 0.5*log(d)")
print(f"  L_proxy stats: mean={np.mean(L_proxy):.3f}, std={np.std(L_proxy):.3f}")

# Does L_proxy correlate with h or R separately?
rho_L_h, _ = spearmanr(L_proxy, log_h)
rho_L_R, _ = spearmanr(L_proxy, log_R)
print(f"  rho(L_proxy, log h) = {rho_L_h:.4f}")
print(f"  rho(L_proxy, log R) = {rho_L_R:.4f}")

# If L_proxy correlates with both h and R (same sign), it creates
# the h-R anti-correlation beyond what d alone explains.
# If it correlates with h but not R (or vice versa), the residual
# is in the L-value's relationship to one invariant specifically.

if abs(rho_L_h) > 0.1 and abs(rho_L_R) > 0.1:
    if np.sign(rho_L_h) != np.sign(rho_L_R):
        print(f"  L_proxy anti-correlates with h and R in OPPOSITE directions.")
        print(f"  This IS the CNF residual: L(1,chi) varies in a way that")
        print(f"  pushes h UP when R is DOWN and vice versa, beyond the d constraint.")
    else:
        print(f"  L_proxy correlates with h and R in SAME direction.")
        print(f"  The residual is NOT from the h-R trade-off but from shared L variation.")

# Control: after removing L_proxy, does h-R anti-correlation weaken?
X_full = np.column_stack([np.ones(len(log_d)), log_d, L_proxy])
beta_h3 = np.linalg.lstsq(X_full, log_h, rcond=None)[0]
beta_r3 = np.linalg.lstsq(X_full, log_R, rcond=None)[0]
resid_h3 = log_h - X_full @ beta_h3
resid_r3 = log_R - X_full @ beta_r3
rho_after_L, _ = spearmanr(resid_h3, resid_r3)
print(f"\n  rho(h, R | d, L_proxy) = {rho_after_L:.4f}")
print(f"  rho(h, R | d only)    = {spearmanr(resid_h, resid_r)[0]:.4f}")

if abs(rho_after_L) < abs(spearmanr(resid_h, resid_r)[0]) * 0.5:
    print(f"  L_proxy EXPLAINS most of the residual. The 'novel' structure is L(1,chi) variation.")
else:
    print(f"  L_proxy does NOT explain the residual. Structure persists beyond L(1,chi).")


# ============================================================
# 4. Where is the residual — in h, in R, or in both?
# ============================================================
print("\n" + "-" * 100)
print("4. Where is the residual? h variance vs R variance after controls")
print("-" * 100)

# Variance of residuals
var_h = np.var(resid_h)
var_R = np.var(resid_r)
print(f"  Var(resid log h | d) = {var_h:.4f}")
print(f"  Var(resid log R | d) = {var_R:.4f}")
print(f"  Ratio: {var_h / var_R:.2f}x")

if var_h > var_R * 2:
    print(f"  The residual is mostly in h (class number is more variable than regulator at fixed d).")
elif var_R > var_h * 2:
    print(f"  The residual is mostly in R (regulator is more variable at fixed d).")
else:
    print(f"  The residual is in BOTH h and R roughly equally.")


# ============================================================
# 5. Replication on genus-2: Selmer rank vs conductor
# ============================================================
print("\n" + "-" * 100)
print("5. Replication: does genus-2 show a similar residual structure?")
print("-" * 100)

import ast
g2 = json.load(open(DATA / "genus2/data/genus2_curves_full.json", encoding="utf-8"))
valid_g2 = []
for c in g2:
    if c.get("conductor", 0) > 0:
        t = c.get("torsion", [])
        if isinstance(t, str):
            try: t = ast.literal_eval(t)
            except: t = []
        order = 1
        if isinstance(t, list):
            for x in t: order *= x
        disc = abs(c.get("discriminant", 0))
        if order > 0 and disc > 0:
            valid_g2.append({"cond": c["conductor"], "torsion": order, "disc": disc})

if len(valid_g2) > 100:
    g2_cond = np.log(np.array([c["cond"] for c in valid_g2], dtype=float))
    g2_tors = np.log(np.array([c["torsion"] for c in valid_g2], dtype=float) + 1)
    g2_disc = np.log(np.array([c["disc"] for c in valid_g2], dtype=float) + 1)

    # Raw correlation
    rho_ct, _ = spearmanr(g2_cond, g2_tors)

    # Partial after disc
    X_g2 = np.column_stack([np.ones(len(g2_disc)), g2_disc])
    b_c = np.linalg.lstsq(X_g2, g2_cond, rcond=None)[0]
    b_t = np.linalg.lstsq(X_g2, g2_tors, rcond=None)[0]
    r_c = g2_cond - X_g2 @ b_c
    r_t = g2_tors - X_g2 @ b_t
    rho_partial_g2, _ = spearmanr(r_c, r_t)

    print(f"  Genus-2: {len(valid_g2)} curves")
    print(f"  rho(log cond, log torsion) = {rho_ct:.4f}")
    print(f"  rho(log cond, log torsion | log disc) = {rho_partial_g2:.4f}")
    print(f"  Strengthening: {rho_partial_g2 - rho_ct:+.4f}")

    if abs(rho_partial_g2) > abs(rho_ct):
        print(f"  REPLICATES: Partial correlation strengthens in genus-2 too!")
    else:
        print(f"  Does NOT replicate: Partial weakens or unchanged in genus-2.")
else:
    print(f"  Insufficient genus-2 data for replication test.")


# ============================================================
# 6. Permutation null for the strengthening effect
# ============================================================
print("\n" + "-" * 100)
print("6. Permutation null: is the strengthening itself significant?")
print("-" * 100)

# The observed strengthening = partial_rho - raw_rho
observed_strengthening = spearmanr(resid_h, resid_r)[0] - spearmanr(log_h, log_R)[0]

# Null: shuffle h values, recompute both raw and partial
null_strengthenings = []
for _ in range(500):
    shuf_h = log_h.copy()
    rng.shuffle(shuf_h)
    raw_rho, _ = spearmanr(shuf_h, log_R)
    resid_sh = shuf_h - X @ np.linalg.lstsq(X, shuf_h, rcond=None)[0]
    part_rho, _ = spearmanr(resid_sh, resid_r)
    null_strengthenings.append(part_rho - raw_rho)

null_arr = np.array(null_strengthenings)
z_perm = (observed_strengthening - np.mean(null_arr)) / np.std(null_arr) if np.std(null_arr) > 0 else 0

print(f"  Observed strengthening: {observed_strengthening:+.4f}")
print(f"  Null mean: {np.mean(null_arr):+.4f}, std: {np.std(null_arr):.4f}")
print(f"  z-score: {z_perm:.1f}")

if abs(z_perm) > 3:
    print(f"  The strengthening effect is SIGNIFICANT (z={z_perm:.1f}).")
    print(f"  This is GENUINE residual structure in the h-R relationship.")
else:
    print(f"  The strengthening effect is NOT significant (z={z_perm:.1f}).")
    print(f"  It may be a statistical artifact of the log-partial procedure.")


# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 100)
print("h-R RESIDUAL DEEP DIVE SUMMARY")
print("=" * 100)
print(f"""
  The h-R anti-correlation after removing discriminant:
    Raw rho(h,R):             {spearmanr(log_h, log_R)[0]:.4f}
    Partial rho(h,R|d):       {spearmanr(resid_h, resid_r)[0]:.4f}
    Partial rho(h,R|d,deg):   {rho_after_deg_d:.4f}
    Partial rho(h,R|d,L):     {rho_after_L:.4f}

  Strengthening permutation z: {z_perm:.1f}
  L_proxy explains:            {'YES' if abs(rho_after_L) < abs(spearmanr(resid_h, resid_r)[0]) * 0.5 else 'NO'}
  Varies by degree:            {'YES' if eta_deg > 0.01 else 'NO'} (eta²={eta_deg:.4f})
  Residual location:           {'h' if var_h > var_R * 2 else 'R' if var_R > var_h * 2 else 'both equally'}
  Replicates in genus-2:       See above
""")

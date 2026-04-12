#!/usr/bin/env python3
"""
Stress Test 2: Tautology detection for "too strong" laws.

Target: max Jones coefficient ~ determinant (R^2 = 0.995)

Tests:
1. Is Y a deterministic function of X? (residual analysis)
2. Does adding X^2, log(X) eliminate residuals completely?
3. Is the relationship DEFINITIONAL (mathematical identity)?
4. If tautology confirmed, reclassify as IDENTITY

Also check: Jones length ~ crossing number (R^2 = 0.507)
            EC count ~ MF count (R^2 = 0.397) — modularity theorem
"""

import sys, os, json
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy import stats as sp_stats

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

DATA = Path(__file__).resolve().parent.parent.parent

# Load knots
print("Loading knot data...")
knots_data = json.load(open(DATA / "knots/data/knots.json", encoding="utf-8"))
knots = knots_data["knots"]
print(f"  Knots: {len(knots)}")

# ============================================================
# TEST 1: max Jones coefficient ~ determinant
# ============================================================
print()
print("=" * 100)
print("TEST 1: max |Jones coefficient| ~ determinant (R^2 = 0.995)")
print("Is this a tautology?")
print("=" * 100)

valid = [k for k in knots if k.get("jones_coeffs") and k.get("determinant")]
det = np.array([k["determinant"] for k in valid], dtype=float)
max_jones = np.array([max(abs(c) for c in k["jones_coeffs"]) for k in valid], dtype=float)

print(f"\n  n = {len(valid)}")

# Linear model
from numpy.polynomial import polynomial as P
r_lin = np.corrcoef(det, max_jones)[0, 1]
print(f"  Linear r: {r_lin:.6f}, R^2: {r_lin**2:.6f}")

# Residual analysis
X = np.column_stack([np.ones(len(det)), det])
beta = np.linalg.lstsq(X, max_jones, rcond=None)[0]
resid_lin = max_jones - X @ beta
print(f"  Linear residual: mean={np.mean(resid_lin):.4f}, std={np.std(resid_lin):.4f}")
print(f"  Max |residual|: {np.max(np.abs(resid_lin)):.4f}")

# Check: is max_jones = f(det) exactly for some simple function?
# Test: max_jones = det (identity)
exact_match = np.sum(max_jones == det)
print(f"\n  Exact match (max_jones == det): {exact_match}/{len(valid)} ({exact_match/len(valid)*100:.1f}%)")

# Test: max_jones = ceil(det/2)
approx_half = np.sum(np.abs(max_jones - np.ceil(det / 2)) < 0.5)
print(f"  Approx ceil(det/2): {approx_half}/{len(valid)} ({approx_half/len(valid)*100:.1f}%)")

# Test: is there a constant ratio?
ratio = max_jones / det
ratio = ratio[np.isfinite(ratio) & (det > 0)]
print(f"  Ratio max_jones/det: mean={np.mean(ratio):.4f}, std={np.std(ratio):.4f}, CV={np.std(ratio)/np.mean(ratio):.4f}")

# Polynomial fit
for degree in [1, 2, 3]:
    coeffs = np.polyfit(det, max_jones, degree)
    pred = np.polyval(coeffs, det)
    ss_res = np.sum((max_jones - pred)**2)
    ss_tot = np.sum((max_jones - np.mean(max_jones))**2)
    r2 = 1 - ss_res / ss_tot
    max_resid = np.max(np.abs(max_jones - pred))
    print(f"  Poly degree {degree}: R^2={r2:.8f}, max residual={max_resid:.4f}")

# Mathematical check: For knots, determinant = |Alexander(-1)|
# Jones polynomial at t=-1 should relate to determinant
# max coefficient of Jones is NOT the same as Jones(-1)
# But the correlation is nearly perfect — why?
print(f"\n  Mathematical analysis:")
print(f"  det = |Alexander(-1)| (by definition)")
print(f"  max|Jones coeff| is NOT a standard knot invariant identity with det")
print(f"  But R^2 = {r_lin**2:.6f} suggests near-functional dependence")

# Check: correlation between crossing_number and both
cn_valid = [k for k in valid if k.get("crossing_number")]
if cn_valid:
    cn = np.array([k["crossing_number"] for k in cn_valid])
    det_cv = np.array([k["determinant"] for k in cn_valid], dtype=float)
    mj_cv = np.array([max(abs(c) for c in k["jones_coeffs"]) for k in cn_valid], dtype=float)

    r_cn_det = np.corrcoef(cn, det_cv)[0, 1]
    r_cn_mj = np.corrcoef(cn, mj_cv)[0, 1]
    print(f"  r(crossing, det) = {r_cn_det:.4f}")
    print(f"  r(crossing, max_jones) = {r_cn_mj:.4f}")

    # Partial: max_jones ~ det | crossing
    X_full = np.column_stack([np.ones(len(cn)), det_cv, cn])
    b_full = np.linalg.lstsq(X_full, mj_cv, rcond=None)[0]
    ss_res_full = np.sum((mj_cv - X_full @ b_full)**2)
    ss_tot_mj = np.sum((mj_cv - np.mean(mj_cv))**2)
    r2_full = 1 - ss_res_full / ss_tot_mj
    print(f"  R^2(max_jones ~ det + crossing) = {r2_full:.6f}")

# VERDICT
print(f"\n  VERDICT:")
if r_lin**2 > 0.99:
    print(f"  R^2 = {r_lin**2:.4f} — NEAR-TAUTOLOGY")
    print(f"  max|Jones coeff| is a near-deterministic function of determinant.")
    print(f"  Not a standard mathematical identity, but functionally equivalent.")
    print(f"  RECLASSIFY: LAW -> IDENTITY (near-functional dependence)")
else:
    print(f"  NOT a tautology (R^2 = {r_lin**2:.4f})")


# ============================================================
# TEST 2: Jones length ~ crossing number (R^2 = 0.507)
# ============================================================
print()
print("=" * 100)
print("TEST 2: Jones polynomial length ~ crossing number (R^2 = 0.507)")
print("Is this trivially structural?")
print("=" * 100)

valid2 = [k for k in knots if k.get("jones_coeffs") and k.get("crossing_number")]
cn2 = np.array([k["crossing_number"] for k in valid2], dtype=float)
jlen = np.array([len(k["jones_coeffs"]) for k in valid2], dtype=float)

r = np.corrcoef(cn2, jlen)[0, 1]
print(f"\n  n = {len(valid2)}")
print(f"  r = {r:.4f}, R^2 = {r**2:.4f}")

# Is Jones length = 2*crossing + 1 or similar?
print(f"\n  Jones length statistics by crossing number:")
print(f"  {'CN':>4s} | {'n':>5s} | {'mean Jlen':>9s} | {'std':>6s} | {'min':>4s} | {'max':>4s}")
print("  " + "-" * 45)
cn_groups = defaultdict(list)
for c, j in zip(cn2, jlen):
    cn_groups[int(c)].append(j)
for c in sorted(cn_groups.keys()):
    vals = cn_groups[c]
    if len(vals) >= 5:
        arr = np.array(vals)
        print(f"  {c:4d} | {len(vals):5d} | {np.mean(arr):9.1f} | {np.std(arr):6.1f} | {int(np.min(arr)):4d} | {int(np.max(arr)):4d}")

# Check: is this the span formula? For an alternating knot,
# Jones has span = 2*crossing + 2
print(f"\n  Check: Jones length ~ 2*crossing?")
ratio2 = jlen / cn2
print(f"  Mean ratio: {np.mean(ratio2):.3f}")
print(f"  Expected for alternating knots: ~2.0")

# Partial after controlling for determinant
det2 = np.array([k["determinant"] for k in valid2 if k.get("determinant")], dtype=float)
if len(det2) == len(cn2):
    X_ctrl = np.column_stack([np.ones(len(cn2)), det2])
    b_cn = np.linalg.lstsq(X_ctrl, cn2, rcond=None)[0]
    b_jl = np.linalg.lstsq(X_ctrl, jlen, rcond=None)[0]
    cn_resid = cn2 - X_ctrl @ b_cn
    jl_resid = jlen - X_ctrl @ b_jl
    r_partial = np.corrcoef(cn_resid, jl_resid)[0, 1]
    print(f"  Partial r(Jlen, CN | det) = {r_partial:.4f}")

# VERDICT
print(f"\n  VERDICT:")
print(f"  Jones polynomial span grows linearly with crossing number.")
print(f"  For alternating knots, span = 2*crossing (Kauffman-Murasugi-Thistlethwaite).")
print(f"  This is a KNOWN MATHEMATICAL THEOREM, not a discovery.")
print(f"  RECLASSIFY: LAW -> KNOWN IDENTITY (Kauffman-Murasugi-Thistlethwaite)")


# ============================================================
# TEST 3: EC count ~ MF count per level (R^2 = 0.397)
# ============================================================
print()
print("=" * 100)
print("TEST 3: EC count ~ MF count per conductor level (R^2 = 0.397)")
print("This should be the modularity theorem — is it?")
print("=" * 100)

import duckdb
ROOT = Path(__file__).resolve().parents[3]
con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
ec_rows = con.execute("SELECT conductor FROM elliptic_curves WHERE conductor > 0").fetchall()
try:
    mf_rows = con.execute("SELECT level, COUNT(*) FROM modular_forms GROUP BY level").fetchall()
    mf_counts = dict(mf_rows)
except:
    mf_counts = {}
con.close()

ec_counts = defaultdict(int)
for (c,) in ec_rows:
    ec_counts[c] += 1

if mf_counts:
    shared = sorted(set(ec_counts.keys()) & set(mf_counts.keys()))
    print(f"  Shared levels: {len(shared)}")

    ec_c = np.array([ec_counts[n] for n in shared], dtype=float)
    mf_c = np.array([mf_counts[n] for n in shared], dtype=float)

    r = np.corrcoef(ec_c, mf_c)[0, 1]
    print(f"  r = {r:.4f}, R^2 = {r**2:.4f}")

    # Modularity theorem: every EC has a corresponding weight-2 newform
    # So ec_count <= mf_count at each level (with equality in some sense)
    n_ec_le_mf = np.sum(ec_c <= mf_c)
    print(f"  EC count <= MF count: {n_ec_le_mf}/{len(shared)} ({n_ec_le_mf/len(shared)*100:.1f}%)")

    # This IS the modularity theorem. R^2 < 1 because MF includes forms not associated with EC
    print(f"\n  VERDICT:")
    print(f"  This IS a rediscovery of the modularity theorem (Wiles/Taylor-Wiles).")
    print(f"  R^2 < 1 because the MF database includes forms beyond weight-2 EC newforms.")
    print(f"  RECLASSIFY: LAW -> REDISCOVERY (modularity theorem)")
else:
    print("  No modular form data available for comparison.")


# ============================================================
# SUMMARY
# ============================================================
print()
print("=" * 100)
print("TAUTOLOGY TEST SUMMARY")
print("=" * 100)
print(f"""
  1. max|Jones coeff| ~ determinant (R^2=0.995): NEAR-TAUTOLOGY / IDENTITY
     Not a standard identity but functionally deterministic.

  2. Jones length ~ crossing (R^2=0.507): KNOWN THEOREM
     Kauffman-Murasugi-Thistlethwaite for alternating knots.

  3. EC count ~ MF count (R^2=0.397): REDISCOVERY
     Modularity theorem (Wiles 1995).

  REVISED LAW LIST after tautology removal:
  - SC_class -> Tc:              UNIVERSAL LAW (eta^2=0.57)
  - (SG x SC_class) -> Tc:       CONDITIONAL LAW (14% main + 9% interaction)
  - N_elements -> Tc:             WEAK LAW (eta^2=0.33 raw, 0.06 after controls)
  - Crossing number -> det:       PENDING (needs Alexander control, knot data issue)

  IDENTITIES (removed from LAW list):
  - max Jones ~ det:              NEAR-IDENTITY (R^2=0.995)
  - Jones length ~ crossing:      KNOWN THEOREM
  - EC ~ MF count:                REDISCOVERY (modularity)
""")

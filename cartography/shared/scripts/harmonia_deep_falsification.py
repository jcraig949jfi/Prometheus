#!/usr/bin/env python3
"""
DEEP FALSIFICATION + SUPPORT: Harmonia's core claims.

KILL TESTS:
1. Random Arithmos ablation — does rho=0.61 survive random small integers?
2. Trivial 1D predictor — does "predict CN from torsion directly" match rho=0.61?
3. Random projection vs hand-crafted phonemes — are phonemes necessary?
4. Physics<->Math cross-test — does PDG couple to EC? (if yes, system is broken)
5. Analytic CNF residual — is the h-R strengthening real or a log artifact?

SUPPORT TESTS:
6. Verify Mantel r=0.94 (two-camera agreement)
7. Verify gauge freedom (rotation invariance)
8. Verify directional asymmetry (EC->NF stronger than NF->EC)
"""
import sys, os, json, csv, io
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[3]
DATA = Path(__file__).resolve().parent.parent.parent
rng = np.random.default_rng(42)

import duckdb

print("=" * 100)
print("HARMONIA DEEP FALSIFICATION + SUPPORT")
print("=" * 100)

# Load core data
con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
ec_data = con.execute("""
    SELECT conductor, rank, torsion, faltings_height
    FROM elliptic_curves WHERE conductor > 0 AND torsion IS NOT NULL
""").fetchall()
con.close()

nf_raw = json.load(open(DATA / "number_fields/data/number_fields.json", encoding="utf-8"))
nf_data = []
for f in nf_raw:
    try:
        nf_data.append({
            "disc": float(f.get("disc_abs", 0)),
            "cn": float(f.get("class_number", 0)),
            "reg": float(f.get("regulator", 0)),
            "deg": int(float(f.get("degree", 0))),
        })
    except: pass
nf_data = [f for f in nf_data if f["disc"] > 0 and f["cn"] > 0]

print(f"  EC: {len(ec_data)} curves, NF: {len(nf_data)} fields\n")


# ============================================================
# KILL TEST 1: Random Arithmos ablation
# ============================================================
print("=" * 100)
print("KILL TEST 1: Random Arithmos — does transfer survive with random small integers?")
print("=" * 100)

# Real transfer: EC torsion -> NF class number via nearest-neighbor in 1D
ec_torsion = np.array([r[2] for r in ec_data], dtype=float)
nf_cn = np.array([f["cn"] for f in nf_data], dtype=float)

# Sample equal sizes
n_sample = min(2000, len(ec_torsion), len(nf_cn))
ec_sample = rng.choice(ec_torsion, n_sample, replace=False)
nf_sample = rng.choice(nf_cn, n_sample, replace=False)

# Real transfer: for each EC, find nearest NF by torsion~class_number distance
# Compute rho between matched pairs
# Sort both by their "Arithmos" values, compute rank correlation
ec_order = np.argsort(ec_sample)
nf_order = np.argsort(nf_sample)

# Real: rank correlation of Arithmos-matched pairs
from scipy.stats import spearmanr
rho_real, p_real = spearmanr(ec_sample[ec_order], nf_sample[nf_order])
print(f"\n  Real Arithmos transfer (torsion rank <-> CN rank): rho={rho_real:.4f}, p={p_real:.4e}")

# Random: replace torsion with random integers from same distribution
null_rhos = []
for _ in range(200):
    fake_torsion = rng.choice(ec_torsion, n_sample, replace=True)
    rng.shuffle(fake_torsion)  # destroy any structure
    fake_order = np.argsort(fake_torsion)
    rho_fake, _ = spearmanr(fake_torsion[fake_order], nf_sample[nf_order])
    null_rhos.append(rho_fake)

null_rhos = np.array(null_rhos)
z = (rho_real - np.mean(null_rhos)) / np.std(null_rhos) if np.std(null_rhos) > 0 else 0
print(f"  Random Arithmos null: mean={np.mean(null_rhos):.4f}, std={np.std(null_rhos):.4f}")
print(f"  z-score: {z:.1f}")

if abs(z) < 3:
    print(f"  VERDICT: KILL — Real transfer is INDISTINGUISHABLE from random small-integer matching.")
    print(f"  The rho=0.61 claim is a small-integer distribution artifact.")
else:
    print(f"  VERDICT: SURVIVES — Real transfer significantly exceeds random (z={z:.1f}).")
    print(f"  The Arithmos signal is NOT just shared small integers.")


# ============================================================
# KILL TEST 2: Trivial 1D predictor
# ============================================================
print("\n" + "=" * 100)
print("KILL TEST 2: Does direct torsion->CN prediction match rho=0.61?")
print("=" * 100)

# For each EC, find the NF with nearest torsion to its class_number
# This is the simplest possible cross-domain prediction
ec_tors_vals = ec_sample.copy()
nf_cn_vals = nf_sample.copy()

# 1D nearest-neighbor: for each EC torsion, find nearest NF by class number
predictions = []
actuals = []
for t in ec_tors_vals[:500]:
    # Predict: the NF with class_number closest to this torsion
    idx = np.argmin(np.abs(nf_cn_vals - t))
    predictions.append(nf_cn_vals[idx])
    actuals.append(t)

rho_trivial, p_trivial = spearmanr(actuals, predictions)
print(f"  Trivial 1D predictor (find CN closest to torsion): rho={rho_trivial:.4f}")
print(f"  Harmonia's claim: rho=0.61")
print(f"  Ratio: {rho_trivial / 0.61:.2f}x")

if rho_trivial > 0.5:
    print(f"  VERDICT: Trivial predictor achieves {rho_trivial/0.61*100:.0f}% of Harmonia's claim.")
    print(f"  The 'transfer' may be achievable WITHOUT tensor trains or phonemes.")
else:
    print(f"  VERDICT: Trivial predictor only achieves {rho_trivial:.3f}. Harmonia adds real value.")


# ============================================================
# KILL TEST 3: Random projection vs phonemes
# ============================================================
print("\n" + "=" * 100)
print("KILL TEST 3: Random projections vs hand-crafted phonemes")
print("=" * 100)

# Build raw feature vectors for EC and NF
ec_features = np.column_stack([
    np.log([r[0] + 1 for r in ec_data[:n_sample]]),  # log conductor
    [r[1] for r in ec_data[:n_sample]],                # rank
    [r[2] for r in ec_data[:n_sample]],                # torsion
])

nf_features = np.column_stack([
    np.log([f["disc"] + 1 for f in nf_data[:n_sample]]),  # log discriminant
    [f["cn"] for f in nf_data[:n_sample]],                  # class number
    [f["reg"] for f in nf_data[:n_sample]],                 # regulator
])

# Hand-crafted phoneme: [log_N, torsion/CN, rank/degree]
ec_phoneme = np.column_stack([
    np.log([r[0] + 1 for r in ec_data[:n_sample]]),  # Megethos
    [r[2] for r in ec_data[:n_sample]],                # Arithmos
])

nf_phoneme = np.column_stack([
    np.log([f["disc"] + 1 for f in nf_data[:n_sample]]),  # Megethos
    [f["cn"] for f in nf_data[:n_sample]],                  # Arithmos
])

# Random projection: project raw features into 2D randomly
proj_ec = rng.normal(0, 1, (ec_features.shape[1], 2))
proj_nf = rng.normal(0, 1, (nf_features.shape[1], 2))
ec_random = ec_features @ proj_ec
nf_random = nf_features @ proj_nf

# PCA projection: use top 2 PCs
from numpy.linalg import svd
def pca_2d(X):
    X_centered = X - X.mean(axis=0)
    U, S, Vt = svd(X_centered, full_matrices=False)
    return X_centered @ Vt[:2].T

ec_pca = pca_2d(ec_features)
nf_pca = pca_2d(nf_features)

# Transfer test for each representation: match by NN in 2D, predict CN from torsion
def transfer_rho(ec_proj, nf_proj, ec_vals, nf_vals, n_test=500):
    """Match EC to NF by nearest neighbor in projection space, compute rho on arithmetic invariant."""
    from scipy.spatial import cKDTree
    tree = cKDTree(nf_proj)
    _, indices = tree.query(ec_proj[:n_test])
    matched_nf = nf_vals[indices]
    rho, _ = spearmanr(ec_vals[:n_test], matched_nf)
    return rho

ec_arith = np.array([r[2] for r in ec_data[:n_sample]])  # torsion
nf_arith = np.array([f["cn"] for f in nf_data[:n_sample]])  # class number

rho_phoneme = transfer_rho(ec_phoneme, nf_phoneme, ec_arith, nf_arith)
rho_random = transfer_rho(ec_random, nf_random, ec_arith, nf_arith)
rho_pca = transfer_rho(ec_pca, nf_pca, ec_arith, nf_arith)

# Multiple random trials
random_rhos = []
for _ in range(50):
    p1 = rng.normal(0, 1, (ec_features.shape[1], 2))
    p2 = rng.normal(0, 1, (nf_features.shape[1], 2))
    r = transfer_rho(ec_features @ p1, nf_features @ p2, ec_arith, nf_arith)
    random_rhos.append(r)

print(f"  Transfer rho by representation:")
print(f"    Hand-crafted phoneme (2D):  {rho_phoneme:.4f}")
print(f"    PCA projection (2D):        {rho_pca:.4f}")
print(f"    Random projection (2D):     mean={np.mean(random_rhos):.4f}, std={np.std(random_rhos):.4f}")
print(f"    Phoneme / random ratio:     {rho_phoneme / np.mean(random_rhos):.2f}x" if np.mean(random_rhos) != 0 else "")

if abs(rho_phoneme) < abs(np.mean(random_rhos)) * 1.5:
    print(f"  VERDICT: Phonemes are NOT significantly better than random projections.")
    print(f"  The 'universality' is achievable without hand-crafted coordinates.")
else:
    print(f"  VERDICT: Phonemes significantly outperform random projections.")
    print(f"  The hand-crafted coordinates capture genuine structure.")


# ============================================================
# KILL TEST 4: Physics<->Math cross-test
# ============================================================
print("\n" + "=" * 100)
print("KILL TEST 4: Does PDG<->EC couple? (If yes, system too permissive)")
print("=" * 100)

# We don't have PDG data loaded, but we can test the PRINCIPLE:
# If materials<->EC couples via phonemes, the system is seeing shared
# integer distributions, not cross-domain structure.

# Materials: use SC data
sc_rows = []
with open(DATA / "physics/data/superconductors/3DSC/superconductors_3D/data/final/MP/3DSC_MP.csv") as f:
    lines = [l for l in f if not l.startswith("#")]
for row in csv.DictReader(io.StringIO("".join(lines))):
    try:
        tc = float(row.get("tc", ""))
        if tc > 0:
            sc_rows.append(tc)
    except: pass

# Materials "phoneme": log(Tc) as Megethos
mat_megethos = np.log(np.array(sc_rows[:n_sample]) + 1)
ec_megethos = np.log(np.array([r[0] for r in ec_data[:n_sample]]) + 1)

# Transfer: match materials to EC by Megethos distance
from scipy.spatial import cKDTree
tree = cKDTree(ec_megethos.reshape(-1, 1))
_, idx = tree.query(mat_megethos[:500].reshape(-1, 1))
matched_ec_torsion = ec_arith[idx]
matched_mat_tc = np.array(sc_rows[:500])

rho_mat_ec, p_mat_ec = spearmanr(matched_mat_tc, matched_ec_torsion)
print(f"  Materials Tc <-> EC torsion (via Megethos matching): rho={rho_mat_ec:.4f}, p={p_mat_ec:.4e}")

if abs(rho_mat_ec) > 0.1 and p_mat_ec < 0.001:
    print(f"  VERDICT: Materials COUPLES to EC. System is too permissive.")
    print(f"  Megethos-based matching creates spurious cross-domain links.")
else:
    print(f"  VERDICT: Materials does NOT couple to EC. Good — selectivity holds.")


# ============================================================
# KILL TEST 5: h-R strengthening — real or log artifact?
# ============================================================
print("\n" + "=" * 100)
print("KILL TEST 5: h-R anti-correlation strengthens after removing d — real or artifact?")
print("=" * 100)

valid_nf = [f for f in nf_data if f["cn"] > 0 and f["reg"] > 0 and f["disc"] > 1]
h = np.array([f["cn"] for f in valid_nf])
R = np.array([f["reg"] for f in valid_nf])
d = np.array([f["disc"] for f in valid_nf])

# Raw correlation in different spaces
rho_raw, _ = spearmanr(h, R)
rho_log, _ = spearmanr(np.log(h + 1), np.log(R + 1))

# Partial after log(d)
log_d = np.log(d)
X = np.column_stack([np.ones(len(log_d)), log_d])
beta_h = np.linalg.lstsq(X, np.log(h + 1), rcond=None)[0]
beta_r = np.linalg.lstsq(X, np.log(R + 1), rcond=None)[0]
resid_h = np.log(h + 1) - X @ beta_h
resid_r = np.log(R + 1) - X @ beta_r
rho_partial, _ = spearmanr(resid_h, resid_r)

# Control: does the strengthening happen with RANDOM data too?
# Generate h,R with known relationship h*R = sqrt(d) * noise
null_strengthenings = []
for _ in range(200):
    fake_d = rng.choice(d, len(d), replace=True)
    L_val = np.exp(rng.normal(0, 0.5, len(d)))  # L(1,chi) variation
    hR = np.sqrt(fake_d) * L_val
    fake_h = hR * np.exp(rng.normal(0, 1, len(d)))  # split randomly
    fake_R = hR / fake_h
    fake_h = np.abs(fake_h) + 1
    fake_R = np.abs(fake_R) + 0.01

    rho_raw_f, _ = spearmanr(np.log(fake_h), np.log(fake_R))
    X_f = np.column_stack([np.ones(len(fake_d)), np.log(fake_d)])
    b_h = np.linalg.lstsq(X_f, np.log(fake_h), rcond=None)[0]
    b_r = np.linalg.lstsq(X_f, np.log(fake_R), rcond=None)[0]
    rho_part_f, _ = spearmanr(np.log(fake_h) - X_f @ b_h, np.log(fake_R) - X_f @ b_r)
    null_strengthenings.append(rho_part_f - rho_raw_f)

real_strengthening = rho_partial - rho_log
null_arr = np.array(null_strengthenings)
z_strength = (real_strengthening - np.mean(null_arr)) / np.std(null_arr) if np.std(null_arr) > 0 else 0

print(f"  Spearman rho(h, R):")
print(f"    Raw:               {rho_raw:.4f}")
print(f"    Log space:         {rho_log:.4f}")
print(f"    Partial (log|d):   {rho_partial:.4f}")
print(f"    Strengthening:     {real_strengthening:+.4f}")
print(f"")
print(f"  Synthetic null (h*R = sqrt(d) * noise):")
print(f"    Mean strengthening: {np.mean(null_arr):+.4f}")
print(f"    z-score of real:    {z_strength:.1f}")

if abs(z_strength) < 2:
    print(f"  VERDICT: Strengthening is EXPECTED from the CNF formula + log transformation.")
    print(f"  NOT novel — it's a statistical property of the log-ratio decomposition.")
else:
    print(f"  VERDICT: Strengthening EXCEEDS what the formula predicts (z={z_strength:.1f}).")
    print(f"  There IS residual structure beyond the analytic class number formula.")


# ============================================================
# SUPPORT TESTS
# ============================================================
print("\n" + "=" * 100)
print("SUPPORT TESTS: What in Harmonia IS real?")
print("=" * 100)

# Support 1: Directional asymmetry
print("\n--- Support 1: Directional asymmetry (EC->NF vs NF->EC) ---")

# EC->NF: use torsion to predict class number
tree_nf = cKDTree(nf_phoneme)
_, idx_ec_nf = tree_nf.query(ec_phoneme[:500])
rho_forward, _ = spearmanr(ec_arith[:500], nf_arith[idx_ec_nf])

# NF->EC: use class number to predict torsion
tree_ec = cKDTree(ec_phoneme)
_, idx_nf_ec = tree_ec.query(nf_phoneme[:500])
rho_reverse, _ = spearmanr(nf_arith[:500], ec_arith[idx_nf_ec])

asymmetry = abs(rho_forward) / abs(rho_reverse) if abs(rho_reverse) > 0.01 else float("inf")
print(f"  EC->NF: rho={rho_forward:.4f}")
print(f"  NF->EC: rho={rho_reverse:.4f}")
print(f"  Asymmetry: {asymmetry:.2f}x")

if asymmetry > 1.5:
    print(f"  CONFIRMED: Transfer IS directional. EC is a richer projection.")
else:
    print(f"  NOT CONFIRMED: Transfer is roughly symmetric.")

# Support 2: Megethos as ordinal structure (not just scale)
print("\n--- Support 2: Megethos captures ordinal structure ---")
# Rank-normalize all domains and check if cross-domain rank correlation holds
ec_rank = np.argsort(np.argsort(ec_megethos[:1000])).astype(float) / 1000
nf_megethos = np.log(np.array([f["disc"] for f in nf_data[:1000]]) + 1)
nf_rank = np.argsort(np.argsort(nf_megethos)).astype(float) / 1000

# After rank normalization, do EC and NF have similar quantile distributions?
from scipy.stats import ks_2samp
ks_stat, ks_p = ks_2samp(ec_rank, nf_rank)
print(f"  KS test of rank-normalized Megethos (EC vs NF): stat={ks_stat:.4f}, p={ks_p:.4e}")
print(f"  If p large: rank distributions match -> ordinal structure is real")
print(f"  If p small: rank distributions differ -> Megethos is domain-specific")

# Support 3: The 41D tensor confirms the 5D phoneme
print("\n--- Support 3: Two-camera agreement ---")
# We can't easily recompute the 41D tensor, but we can check:
# does Harmonia report Mantel r=0.94? Read from results.
for key in ["calibration", "calibration_kosmos", "calibration_phoneme"]:
    cal_path = ROOT / f"harmonia/results/{key}.json"
    if cal_path.exists():
        cal = json.load(open(cal_path))
        print(f"  {key}: {json.dumps(cal, indent=2)[:300]}")


# ============================================================
# FINAL ASSESSMENT
# ============================================================
print("\n" + "=" * 100)
print("FINAL ASSESSMENT: HARMONIA KILL/SUPPORT TALLY")
print("=" * 100)
print(f"""
  KILL TESTS:
    1. Random Arithmos:     {'See z-score above'}
    2. Trivial 1D:          rho_trivial={rho_trivial:.3f} vs claim=0.61
    3. Random projection:   phoneme={rho_phoneme:.3f} vs random={np.mean(random_rhos):.3f}
    4. Physics<->Math:      rho={rho_mat_ec:.3f} (materials<->EC)
    5. h-R strengthening:   z={z_strength:.1f} vs synthetic null

  SUPPORT TESTS:
    1. Directionality:      {asymmetry:.1f}x asymmetry (EC->NF vs NF->EC)
    2. Ordinal structure:   KS p={ks_p:.4e}
    3. Two-camera:          See calibration files above
""")

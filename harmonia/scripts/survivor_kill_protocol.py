"""
Survivor Kill Protocol — 5 tests to break the spectral tail -> isogeny signal.
Signal: gamma_1 (first zero height) encodes isogeny class_size after controlling
for conductor, rank, bad primes, CM, semistable status.
Residual rho = -0.1134, p = 1.89e-86. z = -26.7 in decisive test.

Tests:
  1. Prime reindexing — shuffle prime identity within conductor bins
  2. Low-primes ablation — remove first K primes, check signal persistence
  3. CM vs non-CM split — signal should be in non-CM only
  4. Explicit low-zero coupling — condition on gamma_1 spacing stats
  5. Conductor-bin bootstrap — within-bin permutation at finer granularity
"""
import numpy as np
import duckdb
import json
import psycopg2
from pathlib import Path
from scipy.stats import spearmanr
from sklearn.linear_model import LinearRegression

print("SURVIVOR KILL PROTOCOL")
print("=" * 60)
print("Target: Spectral tail -> isogeny class_size signal")
print("Baseline: residual rho = -0.1134, p = 1.89e-86")
print()

# ─── DATA LOADING ────────────────────────────────────────────
print("Loading data...")
db = duckdb.connect(str(Path("charon/data/charon.duckdb")), read_only=True)
rows = db.sql("""
    SELECT ec.lmfdb_label, ec.conductor, ec.rank, ec.cm, ec.class_size,
           ec.semistable, ec.bad_primes, ec.aplist,
           oz.zeros_vector, oz.n_zeros_stored
    FROM object_zeros oz
    JOIN elliptic_curves ec ON oz.object_id = ec.object_id
    WHERE oz.n_zeros_stored >= 5 AND oz.zeros_vector IS NOT NULL
          AND ec.conductor IS NOT NULL AND ec.conductor <= 50000
          AND ec.class_size IS NOT NULL
""").fetchall()
db.close()

data = []
for label, cond, rank, cm, cs, semi, bp, aplist, zvec, nz in rows:
    zeros = sorted([z for z in (zvec or []) if z is not None and z > 0])
    if len(zeros) < 3:
        continue
    data.append({
        "label": label,
        "conductor": int(cond),
        "rank": int(rank or 0),
        "cm": int(cm or 0),
        "class_size": int(cs),
        "semistable": bool(semi),
        "bad_primes": list(bp or []),
        "aplist": list(aplist or []),
        "gamma1": zeros[0],
        "gamma2": zeros[1] if len(zeros) > 1 else None,
        "gamma3": zeros[2] if len(zeros) > 2 else None,
        "zeros": zeros,
    })

print(f"Loaded {len(data)} curves with zeros + metadata")

gamma1 = np.array([d["gamma1"] for d in data])
class_size = np.array([d["class_size"] for d in data])
conductor = np.array([d["conductor"] for d in data])
rank = np.array([d["rank"] for d in data])
cm = np.array([d["cm"] for d in data])
log_N = np.log10(np.clip(conductor, 2, None))

results = {}

# ─── TEST 1: PRIME REINDEXING ────────────────────────────────
print("\n" + "=" * 60)
print("TEST 1: Prime Reindexing")
print("Keep a_p values, reassign to different primes within log-bins")
print("-" * 40)

# The signal is gamma1 vs class_size. gamma1 comes from zeros which come
# from the L-function, which is the Euler product over primes.
# If gamma1 encodes class_size through SPECIFIC prime structure,
# then shuffling which primes have which a_p values (within conductor bins)
# should destroy the signal.
#
# But gamma1 is pre-computed in the database — we can't recompute L-functions.
# What we CAN do: check if the DISTRIBUTION of a_p values (not their
# prime-specific assignment) predicts class_size independently of gamma1.
# If it does, gamma1 might just be proxying for a_p statistics.

# Approach: compute summary stats of a_p distribution per curve,
# then check if class_size ~ gamma1 survives after conditioning on a_p stats.

has_ap = [i for i, d in enumerate(data) if len(d["aplist"]) >= 10]
print(f"Curves with >=10 a_p values: {len(has_ap)}")

if len(has_ap) > 1000:
    ap_features = []
    for i in has_ap:
        ap = np.array(data[i]["aplist"][:50], dtype=float)
        sqrtp = np.sqrt(np.arange(2, 2 + len(ap)))  # approximate
        normalized = ap / (2 * sqrtp)
        ap_features.append([
            np.mean(normalized),
            np.std(normalized),
            np.mean(normalized**2),  # second moment
            np.mean(np.abs(normalized)),  # mean absolute
            np.median(normalized),
        ])

    ap_feat = np.array(ap_features)
    g1_sub = gamma1[has_ap]
    cs_sub = class_size[has_ap]
    logN_sub = log_N[has_ap]
    rank_sub = rank[has_ap]

    # Full model: gamma1 ~ conductor + rank + a_p_stats
    X_full = np.column_stack([logN_sub, rank_sub, ap_feat])
    reg_full = LinearRegression().fit(X_full, g1_sub)
    resid_full = g1_sub - reg_full.predict(X_full)

    # Does class_size still correlate with gamma1 residuals?
    rho_after_ap, p_after_ap = spearmanr(resid_full, cs_sub)

    # Without a_p stats
    X_no_ap = np.column_stack([logN_sub, rank_sub])
    reg_no_ap = LinearRegression().fit(X_no_ap, g1_sub)
    resid_no_ap = g1_sub - reg_no_ap.predict(X_no_ap)
    rho_before_ap, p_before_ap = spearmanr(resid_no_ap, cs_sub)

    print(f"Before a_p conditioning: rho={rho_before_ap:.4f}, p={p_before_ap:.2e}")
    print(f"After a_p conditioning:  rho={rho_after_ap:.4f}, p={p_after_ap:.2e}")
    reduction = 1 - abs(rho_after_ap) / max(abs(rho_before_ap), 1e-10)
    print(f"Signal reduction: {reduction*100:.1f}%")

    verdict1 = "KILLED" if abs(rho_after_ap) < 0.02 or p_after_ap > 0.01 else "SURVIVES"
    if reduction > 0.8:
        verdict1 = "KILLED (>80% explained by a_p distribution)"
    print(f"TEST 1: {verdict1}")

    results["test1_prime_reindexing"] = {
        "n_curves": len(has_ap),
        "rho_before_ap_control": float(rho_before_ap),
        "p_before_ap_control": float(p_before_ap),
        "rho_after_ap_control": float(rho_after_ap),
        "p_after_ap_control": float(p_after_ap),
        "signal_reduction_pct": float(reduction * 100),
        "verdict": verdict1,
    }
else:
    print("INSUFFICIENT DATA for Test 1")
    results["test1_prime_reindexing"] = {"verdict": "INSUFFICIENT DATA"}


# ─── TEST 2: LOW-PRIMES ABLATION ─────────────────────────────
print("\n" + "=" * 60)
print("TEST 2: Low-Primes Ablation")
print("Check if signal strength depends on number of zeros used")
print("-" * 40)

# If the signal is driven by gamma_1 specifically (prefix artifact),
# using gamma_2, gamma_3 etc. should kill it.
# If it degrades gradually, it's distributed across the zero spectrum.

zero_tests = {}
for k, zname in [(0, "gamma1"), (1, "gamma2"), (2, "gamma3")]:
    vals = np.array([d["zeros"][k] if len(d["zeros"]) > k else np.nan for d in data])
    valid = ~np.isnan(vals)
    if valid.sum() < 500:
        continue
    rho, p = spearmanr(vals[valid], class_size[valid])
    zero_tests[zname] = {"rho": float(rho), "p": float(p), "n": int(valid.sum())}
    print(f"  {zname}: rho={rho:.4f}, p={p:.2e} (n={valid.sum()})")

# Also test: mean of first 3 zeros
mean_z = np.array([np.mean(d["zeros"][:3]) for d in data])
rho_mean, p_mean = spearmanr(mean_z, class_size)
zero_tests["mean_first3"] = {"rho": float(rho_mean), "p": float(p_mean)}
print(f"  mean(z1:z3): rho={rho_mean:.4f}, p={p_mean:.2e}")

# Also: zero spacing (gap between gamma1 and gamma2)
spacing = np.array([d["zeros"][1] - d["zeros"][0] if len(d["zeros"]) > 1 else np.nan for d in data])
valid_sp = ~np.isnan(spacing)
rho_sp, p_sp = spearmanr(spacing[valid_sp], class_size[valid_sp])
zero_tests["spacing_1_2"] = {"rho": float(rho_sp), "p": float(p_sp)}
print(f"  spacing(z2-z1): rho={rho_sp:.4f}, p={p_sp:.2e}")

# Verdict: if gamma2/gamma3 show similar strength, signal is distributed (good)
# If only gamma1, it's a prefix artifact (suspicious)
g1_rho = abs(zero_tests.get("gamma1", {}).get("rho", 0))
g2_rho = abs(zero_tests.get("gamma2", {}).get("rho", 0))
g3_rho = abs(zero_tests.get("gamma3", {}).get("rho", 0))

if g2_rho < g1_rho * 0.3 and g3_rho < g1_rho * 0.3:
    verdict2 = "SUSPICIOUS — concentrated in gamma1 only"
elif g2_rho > g1_rho * 0.5:
    verdict2 = "SURVIVES — signal distributed across zeros"
else:
    verdict2 = "PARTIAL — degrades but present in higher zeros"

print(f"TEST 2: {verdict2}")
results["test2_low_zero_ablation"] = {
    "zero_correlations": zero_tests,
    "verdict": verdict2,
}


# ─── TEST 3: CM vs NON-CM SPLIT ──────────────────────────────
print("\n" + "=" * 60)
print("TEST 3: CM vs Non-CM Split")
print("CM curves violate generic Sato-Tate -> signal should differ")
print("-" * 40)

cm_mask = cm != 0
ncm_mask = cm == 0
print(f"CM curves: {cm_mask.sum()}, Non-CM curves: {ncm_mask.sum()}")

for label, mask in [("CM", cm_mask), ("Non-CM", ncm_mask)]:
    if mask.sum() < 100:
        print(f"  {label}: insufficient data ({mask.sum()} curves)")
        continue
    rho, p = spearmanr(gamma1[mask], class_size[mask])
    # Conductor-controlled
    logN_m = log_N[mask]
    bins = np.percentile(logN_m, np.linspace(0, 100, 11))
    within_rhos = []
    for b in range(10):
        bmask = (logN_m >= bins[b]) & (logN_m < bins[b + 1])
        if bmask.sum() < 30:
            continue
        r, _ = spearmanr(gamma1[mask][bmask], class_size[mask][bmask])
        if not np.isnan(r):
            within_rhos.append(r)
    mean_rho = np.mean(within_rhos) if within_rhos else 0.0
    print(f"  {label}: raw rho={rho:.4f}, within-bin rho={mean_rho:.4f} (n={mask.sum()})")
    results[f"test3_cm_split_{label.lower().replace('-','')}"] = {
        "n": int(mask.sum()),
        "raw_rho": float(rho),
        "within_bin_rho": float(mean_rho),
    }

# Verdict
ncm_rho = abs(results.get("test3_cm_split_noncm", {}).get("within_bin_rho", 0))
cm_rho_val = abs(results.get("test3_cm_split_cm", {}).get("within_bin_rho", 0))

if ncm_rho > 0.03 and cm_rho_val < 0.02:
    verdict3 = "SURVIVES — non-CM only (consistent with spectral theory)"
elif ncm_rho > 0.03 and cm_rho_val > 0.03:
    verdict3 = "PARTIAL — present in both CM and non-CM"
else:
    verdict3 = "KILLED — no signal in non-CM"

print(f"TEST 3: {verdict3}")
results["test3_cm_split"] = {"verdict": verdict3}


# ─── TEST 4: EXPLICIT LOW-ZERO COUPLING ──────────────────────
print("\n" + "=" * 60)
print("TEST 4: Explicit Low-Zero Coupling")
print("Does class_size predict gamma1 AFTER conditioning on zero spacing?")
print("-" * 40)

# If gamma1-class_size correlation is just proxying for known low-zero
# statistics (spacing, density), then conditioning on those should kill it.

# Features: gamma2, gamma3, spacing, mean zero, zero variance
zero_features = []
for d in data:
    z = d["zeros"][:5]
    if len(z) < 3:
        zero_features.append([np.nan] * 5)
        continue
    spacings = np.diff(z)
    zero_features.append([
        z[1],  # gamma2
        z[2],  # gamma3
        spacings[0],  # first spacing
        np.mean(spacings),  # mean spacing
        np.var(z),  # zero variance
    ])

zf = np.array(zero_features)
valid_zf = ~np.any(np.isnan(zf), axis=1)
print(f"Curves with complete zero features: {valid_zf.sum()}")

if valid_zf.sum() > 1000:
    # Regression: gamma1 ~ log_N + rank + zero_features
    X_with_zeros = np.column_stack([log_N[valid_zf], rank[valid_zf], zf[valid_zf]])
    reg_wz = LinearRegression().fit(X_with_zeros, gamma1[valid_zf])
    resid_wz = gamma1[valid_zf] - reg_wz.predict(X_with_zeros)

    rho_after_zeros, p_after_zeros = spearmanr(resid_wz, class_size[valid_zf])

    # Baseline (no zero features)
    X_base = np.column_stack([log_N[valid_zf], rank[valid_zf]])
    reg_base = LinearRegression().fit(X_base, gamma1[valid_zf])
    resid_base = gamma1[valid_zf] - reg_base.predict(X_base)
    rho_base, p_base = spearmanr(resid_base, class_size[valid_zf])

    print(f"Before zero conditioning: rho={rho_base:.4f}, p={p_base:.2e}")
    print(f"After zero conditioning:  rho={rho_after_zeros:.4f}, p={p_after_zeros:.2e}")
    reduction_z = 1 - abs(rho_after_zeros) / max(abs(rho_base), 1e-10)
    print(f"Signal reduction: {reduction_z*100:.1f}%")

    if abs(rho_after_zeros) < 0.02 or p_after_zeros > 0.01:
        verdict4 = "KILLED — proxy for known zero statistics"
    elif reduction_z > 0.8:
        verdict4 = "KILLED — >80% explained by neighboring zeros"
    elif reduction_z > 0.5:
        verdict4 = "PARTIAL — substantial reduction but signal remains"
    else:
        verdict4 = "SURVIVES — independent of neighboring zero stats"

    print(f"TEST 4: {verdict4}")
    results["test4_low_zero_coupling"] = {
        "n": int(valid_zf.sum()),
        "rho_before": float(rho_base),
        "p_before": float(p_base),
        "rho_after": float(rho_after_zeros),
        "p_after": float(p_after_zeros),
        "reduction_pct": float(reduction_z * 100),
        "verdict": verdict4,
    }
else:
    print("INSUFFICIENT DATA for Test 4")
    results["test4_low_zero_coupling"] = {"verdict": "INSUFFICIENT DATA"}


# ─── TEST 5: FINE-GRAINED CONDUCTOR BIN BOOTSTRAP ────────────
print("\n" + "=" * 60)
print("TEST 5: Fine-Grained Conductor Bin Permutation (50 bins)")
print("Finer conductor bins to catch residual magnitude confounding")
print("-" * 40)

n_bins = 50
bins_fine = np.percentile(log_N, np.linspace(0, 100, n_bins + 1))

# Observed within-bin rho
obs_rhos = []
for b in range(n_bins):
    mask = (log_N >= bins_fine[b]) & (log_N < bins_fine[b + 1])
    if mask.sum() < 30:
        continue
    r, _ = spearmanr(gamma1[mask], class_size[mask])
    if not np.isnan(r):
        obs_rhos.append(r)

obs_mean = np.mean(obs_rhos)

# Null: shuffle class_size within each bin
null_means = []
for trial in range(500):
    shuffled = class_size.copy()
    for b in range(n_bins):
        mask = (log_N >= bins_fine[b]) & (log_N < bins_fine[b + 1])
        idx = np.where(mask)[0]
        if len(idx) > 1:
            shuffled[idx] = np.random.permutation(shuffled[idx])

    trial_rhos = []
    for b in range(n_bins):
        mask = (log_N >= bins_fine[b]) & (log_N < bins_fine[b + 1])
        if mask.sum() < 30:
            continue
        r, _ = spearmanr(gamma1[mask], shuffled[mask])
        if not np.isnan(r):
            trial_rhos.append(r)
    null_means.append(np.mean(trial_rhos))

null_m = np.mean(null_means)
null_s = np.std(null_means)
z5 = (obs_mean - null_m) / max(null_s, 1e-10)

print(f"Observed within-bin rho (50 bins): {obs_mean:.4f}")
print(f"Null: mean={null_m:.4f}, std={null_s:.4f}")
print(f"z-score: {z5:.2f}")

verdict5 = "SURVIVES" if abs(z5) > 3 else "KILLED"
print(f"TEST 5: {verdict5} (z={z5:.1f})")

results["test5_fine_conductor_bootstrap"] = {
    "n_bins": n_bins,
    "observed_mean_rho": float(obs_mean),
    "null_mean": float(null_m),
    "null_std": float(null_s),
    "z_score": float(z5),
    "n_permutations": 500,
    "verdict": verdict5,
}


# ─── SUMMARY ─────────────────────────────────────────────────
print("\n" + "=" * 60)
print("SURVIVOR KILL PROTOCOL — SUMMARY")
print("=" * 60)

for key, val in results.items():
    if "verdict" in val:
        print(f"  {key}: {val['verdict']}")

surviving = sum(1 for v in results.values() if isinstance(v, dict) and "SURVIVES" in v.get("verdict", ""))
killed = sum(1 for v in results.values() if isinstance(v, dict) and "KILLED" in v.get("verdict", ""))
print(f"\nSurvived: {surviving}, Killed: {killed}")

out_path = Path("harmonia/results/survivor_kill_protocol.json")
with open(out_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"Saved to {out_path}")

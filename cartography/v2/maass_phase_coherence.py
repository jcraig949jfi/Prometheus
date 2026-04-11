"""
Maass Frobenius Phase Coherence -- Challenge #316
Does phase coherence of Hecke eigenvalues correlate with level,
analogous to how EC phase coherence correlates with analytic rank (rho=0.197)?

For each Maass form: R = |mean(exp(2pii * c_p / 4))| across primes p,
mapping coefficients in [-2,2] to phases in [-pi/2, pi/2].

Correlate R with: level, spectral parameter, symmetry type.
Partial correlation: R vs level controlling for spectral parameter.
"""

import json
import numpy as np
from scipy import stats
from pathlib import Path

# ── Load data ──────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent.parent / "maass" / "data" / "maass_with_coefficients.json"
OUT_PATH = Path(__file__).parent / "maass_phase_coherence_results.json"

print("Loading Maass forms...")
with open(DATA_PATH) as f:
    all_forms = json.load(f)
print(f"  Loaded {len(all_forms)} forms")

# ── Sample 5000 for speed ─────────────────────────────────────────────
rng = np.random.RandomState(42)
if len(all_forms) > 5000:
    indices = rng.choice(len(all_forms), 5000, replace=False)
    forms = [all_forms[i] for i in sorted(indices)]
else:
    forms = all_forms
print(f"  Sampled {len(forms)} forms")

# ── Sieve primes up to max coefficient count ──────────────────────────
max_n = max(f["n_coefficients"] for f in forms)
sieve = np.ones(max_n + 1, dtype=bool)
sieve[:2] = False
for i in range(2, int(max_n**0.5) + 1):
    if sieve[i]:
        sieve[i*i::i] = False
primes = np.where(sieve)[0]
print(f"  {len(primes)} primes up to {max_n}")

# ── Compute phase coherence R for each form ───────────────────────────
print("Computing phase coherence...")
levels = []
spectral_params = []
symmetries = []
phase_coherences = []

for form in forms:
    coeffs = np.array(form["coefficients"])
    n_coeffs = len(coeffs)

    # Extract c_p at prime indices (coefficient index = n-1, so c_p is at index p-1)
    prime_mask = primes < n_coeffs  # primes where we have data (p <= n_coeffs means index p-1 < n_coeffs)
    usable_primes = primes[prime_mask]

    if len(usable_primes) < 10:
        continue

    c_p = coeffs[usable_primes - 1]  # c_p is at index p-1 (c_1 at index 0, etc.)

    # Map c_p in [-2, 2] to phase θ in [-pi/2, pi/2] via θ = (pi/2) * (c_p / 2)
    # Then R = |mean(exp(iθ))|
    theta = (np.pi / 2.0) * (c_p / 2.0)  # c_p/2 maps [-2,2] to [-1,1], then * pi/2
    phases = np.exp(1j * theta)
    R = np.abs(np.mean(phases))

    phase_coherences.append(R)
    levels.append(form["level"])
    spectral_params.append(form["spectral_parameter"])
    symmetries.append(form["symmetry"])

levels = np.array(levels, dtype=float)
spectral_params = np.array(spectral_params, dtype=float)
symmetries = np.array(symmetries, dtype=float)
phase_coherences = np.array(phase_coherences)

print(f"  Computed R for {len(phase_coherences)} forms")
print(f"  R: mean={phase_coherences.mean():.6f}, std={phase_coherences.std():.6f}, "
      f"range=[{phase_coherences.min():.6f}, {phase_coherences.max():.6f}]")

# ── Correlations ──────────────────────────────────────────────────────
print("\n=== Raw Correlations ===")

# (a) R vs level
r_level, p_level = stats.spearmanr(phase_coherences, levels)
print(f"  R vs level:     rho = {r_level:.6f}  (p = {p_level:.2e})")

# (b) R vs spectral parameter
r_spectral, p_spectral = stats.spearmanr(phase_coherences, spectral_params)
print(f"  R vs spectral:  rho = {r_spectral:.6f}  (p = {p_spectral:.2e})")

# (c) R vs symmetry
r_sym, p_sym = stats.spearmanr(phase_coherences, symmetries)
print(f"  R vs symmetry:  rho = {r_sym:.6f}  (p = {p_sym:.2e})")

# Pearson too
rp_level, pp_level = stats.pearsonr(phase_coherences, levels)
rp_spectral, pp_spectral = stats.pearsonr(phase_coherences, spectral_params)
print(f"\n  Pearson R vs level:    r = {rp_level:.6f}  (p = {pp_level:.2e})")
print(f"  Pearson R vs spectral: r = {rp_spectral:.6f}  (p = {pp_spectral:.2e})")

# ── Partial correlation: R vs level controlling for spectral parameter ──
print("\n=== Partial Correlation (R vs level | spectral) ===")

def partial_corr(x, y, z):
    """Partial Spearman correlation of x,y controlling for z."""
    # Rank-based partial correlation
    rx = stats.rankdata(x)
    ry = stats.rankdata(y)
    rz = stats.rankdata(z)
    # Residualize
    slope_xz = np.polyfit(rz, rx, 1)
    slope_yz = np.polyfit(rz, ry, 1)
    res_x = rx - np.polyval(slope_xz, rz)
    res_y = ry - np.polyval(slope_yz, rz)
    r, p = stats.pearsonr(res_x, res_y)
    return r, p

r_partial, p_partial = partial_corr(phase_coherences, levels, spectral_params)
print(f"  Partial rho(R, level | spectral) = {r_partial:.6f}  (p = {p_partial:.2e})")

# ── Null distribution: shuffle R and recompute ────────────────────────
print("\n=== Null Distribution (1000 shuffles) ===")
null_corrs = []
for _ in range(1000):
    shuffled = rng.permutation(phase_coherences)
    r_null, _ = stats.spearmanr(shuffled, levels)
    null_corrs.append(r_null)
null_corrs = np.array(null_corrs)
z_score = (r_level - null_corrs.mean()) / null_corrs.std()
print(f"  Null mean: {null_corrs.mean():.6f}, std: {null_corrs.std():.6f}")
print(f"  Observed rho = {r_level:.6f}, z = {z_score:.2f}")

# ── By symmetry type ─────────────────────────────────────────────────
print("\n=== By Symmetry Type ===")
for sym_val in [-1, 1]:
    mask = symmetries == sym_val
    if mask.sum() < 30:
        continue
    r_s, p_s = stats.spearmanr(phase_coherences[mask], levels[mask])
    print(f"  sym={sym_val:+d}: n={mask.sum()}, rho(R,level)={r_s:.6f} (p={p_s:.2e}), "
          f"mean R={phase_coherences[mask].mean():.6f}")

# ── Log-level correlation (level spans wide range) ────────────────────
print("\n=== Log-Level Correlation ===")
log_levels = np.log(levels)
r_log, p_log = stats.spearmanr(phase_coherences, log_levels)
print(f"  R vs log(level): rho = {r_log:.6f}  (p = {p_log:.2e})")

# ── Level bins: mean R by level bracket ───────────────────────────────
print("\n=== Mean R by Level Bracket ===")
unique_levels = np.unique(levels)
level_brackets = np.percentile(levels, [0, 25, 50, 75, 100])
for i in range(4):
    lo, hi = level_brackets[i], level_brackets[i+1]
    if i < 3:
        mask = (levels >= lo) & (levels < hi)
    else:
        mask = (levels >= lo) & (levels <= hi)
    if mask.sum() > 0:
        print(f"  level [{lo:.0f}, {hi:.0f}]: n={mask.sum()}, "
              f"mean R={phase_coherences[mask].mean():.6f} ± {phase_coherences[mask].std():.6f}")

# ── Spectral bins: mean R by spectral parameter bracket ───────────────
print("\n=== Mean R by Spectral Parameter Bracket ===")
sp_brackets = np.percentile(spectral_params, [0, 25, 50, 75, 100])
for i in range(4):
    lo, hi = sp_brackets[i], sp_brackets[i+1]
    if i < 3:
        mask = (spectral_params >= lo) & (spectral_params < hi)
    else:
        mask = (spectral_params >= lo) & (spectral_params <= hi)
    if mask.sum() > 0:
        print(f"  spectral [{lo:.4f}, {hi:.4f}]: n={mask.sum()}, "
              f"mean R={phase_coherences[mask].mean():.6f} ± {phase_coherences[mask].std():.6f}")

# ── CRITICAL CONTROL: fixed prime count to eliminate n_coefficients confound ──
# n_coefficients correlates with level (rho=0.66), so forms with higher level
# tend to have more coefficients, meaning more primes, meaning lower R variance.
# Fix to first 46 primes (up to p=199) for all forms with >= 200 coefficients.
print("\n=== CONTROLLED TEST (fixed 46 primes, n_coeffs >= 200) ===")
FIXED_THRESHOLD = 200
fixed_primes = primes[primes < FIXED_THRESHOLD]  # 46 primes
print(f"  Using {len(fixed_primes)} primes (up to p={fixed_primes[-1]})")

ctrl_R = []
ctrl_levels = []
ctrl_spectral = []
ctrl_sym = []

for form in forms:
    if form["n_coefficients"] < FIXED_THRESHOLD:
        continue
    coeffs = np.array(form["coefficients"])
    c_p = coeffs[fixed_primes - 1]
    theta = (np.pi / 2.0) * (c_p / 2.0)
    phases = np.exp(1j * theta)
    R = np.abs(np.mean(phases))
    ctrl_R.append(R)
    ctrl_levels.append(form["level"])
    ctrl_spectral.append(form["spectral_parameter"])
    ctrl_sym.append(form["symmetry"])

ctrl_R = np.array(ctrl_R)
ctrl_levels = np.array(ctrl_levels, dtype=float)
ctrl_spectral = np.array(ctrl_spectral, dtype=float)
print(f"  n={len(ctrl_R)} forms, R mean={ctrl_R.mean():.6f}, std={ctrl_R.std():.6f}")

r_ctrl_level, p_ctrl_level = stats.spearmanr(ctrl_R, ctrl_levels)
r_ctrl_spectral, p_ctrl_spectral = stats.spearmanr(ctrl_R, ctrl_spectral)
print(f"  CONTROLLED R vs level:    rho = {r_ctrl_level:.6f}  (p = {p_ctrl_level:.2e})")
print(f"  CONTROLLED R vs spectral: rho = {r_ctrl_spectral:.6f}  (p = {p_ctrl_spectral:.2e})")

# Null for controlled
ctrl_null_corrs = []
for _ in range(1000):
    shuffled = rng.permutation(ctrl_R)
    r_n, _ = stats.spearmanr(shuffled, ctrl_levels)
    ctrl_null_corrs.append(r_n)
ctrl_null_corrs = np.array(ctrl_null_corrs)
ctrl_z = (r_ctrl_level - ctrl_null_corrs.mean()) / ctrl_null_corrs.std()
print(f"  Controlled null: mean={ctrl_null_corrs.mean():.6f}, std={ctrl_null_corrs.std():.6f}")
print(f"  Controlled z-score = {ctrl_z:.2f}")

# Partial correlation controlled
r_ctrl_partial, p_ctrl_partial = partial_corr(ctrl_R, ctrl_levels, ctrl_spectral)
print(f"  CONTROLLED partial rho(R, level | spectral) = {r_ctrl_partial:.6f}  (p = {p_ctrl_partial:.2e})")

# ── Compare to EC benchmark ──────────────────────────────────────────
print("\n=== Comparison to EC Phase Coherence ===")
print(f"  EC phase coherence vs rank:     rho = 0.197")
print(f"  Maass phase coherence vs level: rho = {r_level:.6f}")
print(f"  Maass phase coherence vs spectral: rho = {r_spectral:.6f}")
ratio = abs(r_level) / 0.197 if abs(r_level) > 0 else 0
print(f"  |Maass/EC| ratio (level): {ratio:.3f}")

# ── Verdict ───────────────────────────────────────────────────────────
print("\n=== VERDICT ===")
sig_level = abs(r_level) > 0.05 and p_level < 0.001
sig_spectral = abs(r_spectral) > 0.05 and p_spectral < 0.001
if sig_level:
    print(f"  SIGNAL: Phase coherence correlates with level (rho={r_level:.4f}, p={p_level:.2e})")
else:
    print(f"  NULL: No meaningful correlation with level (rho={r_level:.4f}, p={p_level:.2e})")
if sig_spectral:
    print(f"  SIGNAL: Phase coherence correlates with spectral parameter (rho={r_spectral:.4f}, p={p_spectral:.2e})")
else:
    print(f"  NULL: No meaningful correlation with spectral parameter (rho={r_spectral:.4f}, p={p_spectral:.2e})")

# ── Save results ──────────────────────────────────────────────────────
results = {
    "challenge": "Maass Frobenius Phase Coherence vs Level",
    "challenge_number": 316,
    "n_forms": len(phase_coherences),
    "n_primes_max": len(primes),
    "phase_coherence_stats": {
        "mean": float(phase_coherences.mean()),
        "std": float(phase_coherences.std()),
        "min": float(phase_coherences.min()),
        "max": float(phase_coherences.max()),
    },
    "correlations": {
        "spearman_R_vs_level": {"rho": float(r_level), "p": float(p_level)},
        "spearman_R_vs_spectral": {"rho": float(r_spectral), "p": float(p_spectral)},
        "spearman_R_vs_symmetry": {"rho": float(r_sym), "p": float(p_sym)},
        "pearson_R_vs_level": {"r": float(rp_level), "p": float(pp_level)},
        "pearson_R_vs_spectral": {"r": float(rp_spectral), "p": float(pp_spectral)},
        "spearman_R_vs_log_level": {"rho": float(r_log), "p": float(p_log)},
        "partial_R_vs_level_given_spectral": {"rho": float(r_partial), "p": float(p_partial)},
    },
    "null_distribution": {
        "n_shuffles": 1000,
        "null_mean": float(null_corrs.mean()),
        "null_std": float(null_corrs.std()),
        "z_score": float(z_score),
    },
    "ec_comparison": {
        "ec_rho": 0.197,
        "maass_rho_level": float(r_level),
        "ratio": float(ratio),
    },
    "controlled_test": {
        "description": "Fixed 46 primes (up to p=199) for all forms with >= 200 coefficients",
        "n_forms": len(ctrl_R),
        "n_primes": len(fixed_primes),
        "spearman_R_vs_level": {"rho": float(r_ctrl_level), "p": float(p_ctrl_level)},
        "spearman_R_vs_spectral": {"rho": float(r_ctrl_spectral), "p": float(p_ctrl_spectral)},
        "partial_R_vs_level_given_spectral": {"rho": float(r_ctrl_partial), "p": float(p_ctrl_partial)},
        "z_score": float(ctrl_z),
    },
    "verdict_raw": "SIGNAL" if sig_level or sig_spectral else "NULL",
    "verdict_controlled": "SIGNAL" if abs(r_ctrl_level) > 0.05 and p_ctrl_level < 0.001 else "NULL",
    "note": "Phase coherence R = |mean(exp(i * pi/2 * c_p/2))| over primes p; controlled test eliminates n_coefficients confound"
}

# Final verdict uses controlled test
print(f"\n  FINAL (controlled): R vs level rho={r_ctrl_level:.4f}, z={ctrl_z:.1f}")
if abs(r_ctrl_level) > 0.05 and p_ctrl_level < 0.001:
    print(f"  ==> CONFIRMED: correlation survives controlling for #coefficients")
else:
    print(f"  ==> KILLED: raw correlation was artifact of variable #coefficients")

with open(OUT_PATH, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {OUT_PATH}")

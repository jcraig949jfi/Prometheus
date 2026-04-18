"""
Charon Frontier Batch 3: 5 hypotheses against artin_reps (798,140 rows).
Tests H60, H61, H27, H84, H03.

All columns in artin_reps are TEXT. No root_number column exists.
GalConjSigns = Frobenius-Schur indicators per Galois conjugate (not root numbers).
"""

import json
import sys
import numpy as np
import psycopg2
from collections import Counter
from pathlib import Path
from scipy.stats import linregress
from scipy.optimize import curve_fit

# ── Database connection ──────────────────────────────────────────────
CONN_PARAMS = dict(host="localhost", port=5432, dbname="lmfdb",
                   user="postgres", password="prometheus")

def fetch(query):
    with psycopg2.connect(**CONN_PARAMS) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

results = {}

# =====================================================================
# H60: Artin Frontier Clusters (<20 Manifolds)
# =====================================================================
print("=" * 60)
print("H60: Artin Frontier Clusters")
print("=" * 60)

try:
    rows = fetch('''
        SELECT "Dim"::int, "Conductor"::float, "Indicator"::int, "Is_Even"
        FROM artin_reps
        WHERE "Dim"::int >= 2 AND "Is_Even" = 'True'
          AND "Conductor" != 'Infinity'
          AND "Conductor"::float < 1e30
    ''')
    print(f"  Frontier reps (Dim>=2, even, finite cond): {len(rows)}")

    dims = np.array([r[0] for r in rows], dtype=float)
    conds = np.array([r[1] for r in rows], dtype=float)
    indicators = np.array([r[2] for r in rows], dtype=float)

    # Build feature matrix, drop zero-variance columns
    log_conds = np.log1p(conds)
    features = [dims, log_conds, indicators]
    names = ["dim", "log_cond", "indicator"]
    keep = []
    for i, f in enumerate(features):
        if np.std(f) > 1e-8:
            keep.append(i)
    X_raw = np.column_stack([features[i] for i in keep])
    used_features = [names[i] for i in keep]
    print(f"  Features used (nonzero variance): {used_features}")

    # Filter NaN/Inf rows
    good = np.all(np.isfinite(X_raw), axis=1)
    X_raw = X_raw[good]
    print(f"  Rows after NaN/Inf filter: {len(X_raw)}")

    # Standardize
    X = (X_raw - X_raw.mean(axis=0)) / (X_raw.std(axis=0) + 1e-12)

    # Subsample for tractability
    rng = np.random.RandomState(42)
    n = len(X)
    if n > 30000:
        idx = rng.choice(n, 30000, replace=False)
        Xs = X[idx]
    else:
        Xs = X

    from sklearn.mixture import GaussianMixture

    bics = {}
    for k in range(2, 61):
        gmm = GaussianMixture(n_components=k, covariance_type='diag',
                              max_iter=100, n_init=1, random_state=42)
        gmm.fit(Xs)
        bics[k] = gmm.bic(Xs)

    optimal_k = min(bics, key=bics.get)
    print(f"  Optimal k by BIC: {optimal_k}")
    print(f"  Kill threshold: k > 50")
    killed = optimal_k > 50
    verdict = "KILLED" if killed else "SURVIVES"
    print(f"  Verdict: {verdict}")

    results["H60"] = {
        "hypothesis": "Artin Frontier Clusters (<20 Manifolds)",
        "n_frontier": len(rows),
        "n_after_filter": int(X.shape[0]),
        "features_used": used_features,
        "optimal_k_bic": optimal_k,
        "bic_at_optimal": float(bics[optimal_k]),
        "kill_criterion": "optimal k > 50",
        "killed": killed,
        "verdict": verdict
    }
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback; traceback.print_exc()
    results["H60"] = {"error": str(e), "verdict": "ERROR"}

# =====================================================================
# H61: Artin Dimensional Gap
# =====================================================================
print("\n" + "=" * 60)
print("H61: Artin Dimensional Gap")
print("=" * 60)

try:
    rows = fetch('''
        SELECT "Dim"::int, "Is_Even", COUNT(*) as cnt
        FROM artin_reps
        GROUP BY "Dim"::int, "Is_Even"
        ORDER BY "Dim"::int
    ''')

    counts = {}
    for dim, is_even, cnt in rows:
        counts[(dim, is_even)] = cnt

    even_dim2 = counts.get((2, 'True'), 0)
    total_dim3 = counts.get((3, 'True'), 0) + counts.get((3, 'False'), 0)

    ratio = even_dim2 / total_dim3 if total_dim3 > 0 else float('inf')
    print(f"  Count(Dim=2, even): {even_dim2}")
    print(f"  Count(Dim=3, all):  {total_dim3}")
    print(f"  Ratio: {ratio:.2f}:1")

    # Context: overall distribution
    total_by_dim = {}
    for (d, ie), c in counts.items():
        total_by_dim[d] = total_by_dim.get(d, 0) + c
    print(f"  Dim distribution: { {d: total_by_dim[d] for d in sorted(total_by_dim)[:8]} }")

    killed = ratio < 10
    verdict = "KILLED" if killed else "SURVIVES"
    print(f"  Kill threshold: ratio < 10:1")
    print(f"  Verdict: {verdict}")

    results["H61"] = {
        "hypothesis": "Artin Dimensional Gap",
        "even_dim2": even_dim2,
        "total_dim3": total_dim3,
        "ratio": round(ratio, 4),
        "kill_criterion": "ratio < 10:1",
        "killed": killed,
        "verdict": verdict,
        "dim_distribution": {str(d): total_by_dim[d] for d in sorted(total_by_dim)[:10]}
    }
except Exception as e:
    print(f"  ERROR: {e}")
    results["H61"] = {"error": str(e), "verdict": "ERROR"}

# =====================================================================
# H27: Yakaboylu Root Number Bias
# =====================================================================
print("\n" + "=" * 60)
print("H27: Yakaboylu Root Number Bias")
print("=" * 60)

try:
    # No root_number column exists in artin_reps.
    # GalConjSigns stores Frobenius-Schur indicators (1=orth, -1=symp, 0=complex)
    # -- NOT root numbers.
    #
    # For even orthogonal reps (Indicator=1, Is_Even=True), the root number is:
    #   w = (-1)^(dim/2) * det(-1)
    # We can't extract det(-1) from Dets labels alone.
    #
    # Alternative approach: derive root_number = (-1)^(dim/2) for trivial det,
    # which is purely deterministic from dim -- no conductor dependence possible.
    #
    # We therefore use ALL orthogonal reps and compute the empirical
    # Frobenius-Schur distribution vs conductor to test for any bias at all.

    rows = fetch('''
        SELECT "Conductor"::float, "Indicator"::int, "Dim"::int
        FROM artin_reps
        WHERE "Indicator" != '0' AND "Is_Even" = 'True' AND "Dim"::int >= 2
          AND "Conductor" != 'Infinity'
          AND "Conductor"::float > 0 AND "Conductor"::float < 1e30
    ''')
    print(f"  Even non-complex reps (Dim>=2): {len(rows)}")

    conductors = np.array([r[0] for r in rows], dtype=float)
    indicators = np.array([r[1] for r in rows], dtype=float)  # +1 (orth) or -1 (symp)
    dims = np.array([r[2] for r in rows], dtype=int)

    # Compute root number proxy: w = (-1)^(dim//2) * indicator
    # For even dims: (-1)^(dim//2). For odd dims: (-1)^((dim-1)//2) (functional eq sign)
    root_proxy = ((-1.0) ** (dims // 2)) * indicators

    print(f"  Root proxy distribution: +1={np.sum(root_proxy>0)}, -1={np.sum(root_proxy<0)}")

    if np.unique(root_proxy).size < 2:
        # All same sign -- untestable
        print("  All root proxies have the same sign -- no variance to test bias")
        print("  Verdict: KILLED (untestable -- no root number variance in data)")
        results["H27"] = {
            "hypothesis": "Yakaboylu Root Number Bias",
            "n_reps": len(rows),
            "root_proxy_unique": np.unique(root_proxy).tolist(),
            "kill_criterion": "slope zero (p>0.01) or positive",
            "killed": True,
            "verdict": "KILLED (untestable)",
            "note": "No root_number column; proxy = (-1)^(dim/2)*Indicator has no variance for this subset"
        }
    else:
        # Bin by log(Conductor)
        log_c = np.log(conductors + 1)
        n_bins = 20
        bins = np.linspace(log_c.min(), log_c.max(), n_bins + 1)
        bin_centers = []
        bin_means = []
        for i in range(n_bins):
            mask = (log_c >= bins[i]) & (log_c < bins[i+1])
            if mask.sum() > 10:
                bin_centers.append((bins[i] + bins[i+1]) / 2)
                bin_means.append(root_proxy[mask].mean())

        bin_centers = np.array(bin_centers)
        bin_means = np.array(bin_means)

        x_fit = bin_centers ** (-0.5)
        slope, intercept, r_value, p_value, std_err = linregress(x_fit, bin_means)

        print(f"  Fit: mean_root_proxy ~ {slope:.6f} * log(C)^(-1/2) + {intercept:.6f}")
        print(f"  R^2 = {r_value**2:.4f}, p = {p_value:.6e}")
        print(f"  Kill: slope zero (p > 0.01) or positive")

        killed = p_value > 0.01 or slope >= 0
        verdict = "KILLED" if killed else "SURVIVES"
        print(f"  Verdict: {verdict}")

        results["H27"] = {
            "hypothesis": "Yakaboylu Root Number Bias",
            "n_reps": len(rows),
            "root_proxy_plus": int(np.sum(root_proxy > 0)),
            "root_proxy_minus": int(np.sum(root_proxy < 0)),
            "slope": round(float(slope), 6),
            "intercept": round(float(intercept), 6),
            "r_squared": round(float(r_value**2), 4),
            "p_value": float(p_value),
            "kill_criterion": "slope zero (p>0.01) or positive",
            "killed": killed,
            "verdict": verdict,
            "note": "Root proxy = (-1)^(dim/2)*Indicator; no root_number column in table"
        }
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback; traceback.print_exc()
    results["H27"] = {"error": str(e), "verdict": "ERROR"}

# =====================================================================
# H84: Mobius Autocorrelation in Artin Root Numbers
# =====================================================================
print("\n" + "=" * 60)
print("H84: Mobius Autocorrelation in Artin Root Numbers")
print("=" * 60)

try:
    # Odd 2-dim Artin reps, sorted by conductor
    # Use Indicator as sign proxy (Frobenius-Schur indicator)
    rows = fetch('''
        SELECT "Conductor"::float, "Indicator"::int
        FROM artin_reps
        WHERE "Dim" = '2' AND "Is_Even" = 'False'
          AND "Conductor" != 'Infinity'
          AND "Conductor"::float > 0 AND "Conductor"::float < 1e30
        ORDER BY "Conductor"::float
    ''')
    print(f"  Odd 2-dim reps: {len(rows)}")

    conductors = np.array([r[0] for r in rows], dtype=float)
    indicators = np.array([r[1] for r in rows], dtype=float)

    # For odd dim-2: root number proxy = (-1)^1 * indicator = -indicator
    signs = -indicators
    print(f"  Sign distribution: +1={np.sum(signs==1)}, -1={np.sum(signs==-1)}, 0={np.sum(signs==0)}")

    # Partial sums S(X) = cumulative sum of signs up to conductor X
    S = np.cumsum(signs)

    # Fit |S(X)| ~ X^alpha using log-log regression
    abs_S = np.abs(S)

    # Subsample evenly in index space for stability
    n = len(conductors)
    indices = np.linspace(max(100, n//100), n - 1, 500, dtype=int)
    log_X = np.log(conductors[indices])
    log_S = np.log(np.maximum(abs_S[indices], 1))

    slope, intercept, r_value, p_value, std_err = linregress(log_X, log_S)

    print(f"  Fit: |S(X)| ~ X^{slope:.4f}")
    print(f"  R^2 = {r_value**2:.4f}")
    print(f"  Expected alpha ~ 0.5")
    print(f"  Kill: alpha < 0.4 or alpha > 0.6")

    killed = slope < 0.4 or slope > 0.6
    verdict = "KILLED" if killed else "SURVIVES"
    print(f"  Verdict: {verdict}")

    # Check if signs are essentially all one value (no cancellation possible)
    frac_dominant = max(np.sum(signs == 1), np.sum(signs == -1)) / max(len(signs), 1)
    if frac_dominant > 0.95:
        # Monotonic sum -- not a cancellation test
        print(f"  WARNING: {frac_dominant*100:.1f}% of signs are the same -- no cancellation")
        print(f"  This measures counting growth, not Mobius-like cancellation")
        print(f"  Verdict: KILLED (degenerate -- no sign variance)")
        killed = True
        verdict = "KILLED (degenerate)"
        results["H84"] = {
            "hypothesis": "Mobius Autocorrelation in Artin Root Numbers",
            "n_odd_dim2": len(rows),
            "sign_plus1": int(np.sum(signs == 1)),
            "sign_minus1": int(np.sum(signs == -1)),
            "sign_zero": int(np.sum(signs == 0)),
            "dominant_fraction": round(float(frac_dominant), 4),
            "alpha_exponent": round(float(slope), 4),
            "kill_criterion": "alpha < 0.4 or > 0.6 (but test degenerate: no cancellation)",
            "killed": killed,
            "verdict": verdict,
            "note": "All odd dim-2 reps have Indicator=1, so proxy is all -1. No Mobius cancellation possible."
        }
    else:
        results["H84"] = {
            "hypothesis": "Mobius Autocorrelation in Artin Root Numbers",
            "n_odd_dim2": len(rows),
            "sign_plus1": int(np.sum(signs == 1)),
            "sign_minus1": int(np.sum(signs == -1)),
            "sign_zero": int(np.sum(signs == 0)),
            "alpha_exponent": round(float(slope), 4),
            "r_squared": round(float(r_value**2), 4),
            "p_value": float(p_value),
            "kill_criterion": "alpha < 0.4 or > 0.6",
            "killed": killed,
            "verdict": verdict,
            "note": "Root number proxy = -Indicator for odd dim-2"
        }
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback; traceback.print_exc()
    results["H84"] = {"error": str(e), "verdict": "ERROR"}

# =====================================================================
# H03: Artin Dimension She-Leveque
# =====================================================================
print("\n" + "=" * 60)
print("H03: Artin Dimension She-Leveque")
print("=" * 60)

try:
    rows = fetch('''
        SELECT "Dim"::int, MAX("Conductor"::float) as max_cond
        FROM artin_reps
        WHERE "Is_Even" = 'True'
          AND "Conductor" != 'Infinity'
          AND "Conductor"::float > 0 AND "Conductor"::float < 1e50
        GROUP BY "Dim"::int
        ORDER BY "Dim"::int
    ''')

    dims = np.array([r[0] for r in rows])
    max_conds = np.array([r[1] for r in rows])

    # Filter out any remaining inf/nan
    good = np.isfinite(max_conds) & (max_conds > 0)
    dims = dims[good]
    max_conds = max_conds[good]

    print(f"  Even dimensions found: {len(dims)}")
    for d, mc in zip(dims, max_conds):
        print(f"    dim={d:3d}  max_cond={mc:.3e}")

    # Gap ratios: log(max_cond[i+1]) / log(max_cond[i])
    log_mc = np.log(max_conds)
    gap_ratios = log_mc[1:] / log_mc[:-1]
    p_indices = np.arange(1, len(gap_ratios) + 1, dtype=float)

    # Filter out any inf/nan in gap_ratios
    valid = np.isfinite(gap_ratios)
    gap_ratios_v = gap_ratios[valid]
    p_indices_v = p_indices[valid]

    print(f"  Valid gap ratios: {len(gap_ratios_v)} / {len(gap_ratios)}")
    print(f"  Gap ratios (first 10): {np.round(gap_ratios_v[:10], 4).tolist()}")

    if len(p_indices_v) < 3:
        raise ValueError(f"Only {len(p_indices_v)} valid gap ratios, need >= 3")

    # Fit She-Leveque: zeta_p = p/3 + C*(1 - beta^(p/3))
    def she_leveque(p, C, beta):
        return p / 3.0 + C * (1.0 - np.clip(beta, 1e-10, 1-1e-10) ** (p / 3.0))

    try:
        popt, pcov = curve_fit(she_leveque, p_indices_v, gap_ratios_v,
                               p0=[0.1, 0.5], maxfev=10000,
                               bounds=([-100, 0.01], [100, 0.99]))
        C_fit, beta_fit = popt
        fitted = she_leveque(p_indices_v, C_fit, beta_fit)
        residuals = gap_ratios_v - fitted
        rel_residuals = np.abs(residuals) / (np.abs(gap_ratios_v) + 1e-12)
        max_rel_residual = float(rel_residuals.max())
        mean_rel_residual = float(rel_residuals.mean())

        # Bootstrap beta stability
        betas = []
        rng = np.random.RandomState(42)
        for _ in range(200):
            idx = rng.choice(len(p_indices_v), len(p_indices_v), replace=True)
            try:
                pb, _ = curve_fit(she_leveque, p_indices_v[idx], gap_ratios_v[idx],
                                  p0=[C_fit, beta_fit], maxfev=5000,
                                  bounds=([-100, 0.01], [100, 0.99]))
                betas.append(pb[1])
            except:
                pass

        beta_std = np.std(betas) if betas else float('inf')
        beta_cv = beta_std / (abs(beta_fit) + 1e-12)

        print(f"  Fit: C={C_fit:.4f}, beta={beta_fit:.4f}")
        print(f"  Max relative residual: {max_rel_residual:.4f}")
        print(f"  Mean relative residual: {mean_rel_residual:.4f}")
        print(f"  Beta stability (CV): {beta_cv:.4f} (from {len(betas)} bootstraps)")
        print(f"  Kill: residuals > 10% or beta unstable (CV > 0.5)")

        killed = max_rel_residual > 0.10 or beta_cv > 0.5
        verdict = "KILLED" if killed else "SURVIVES"
        print(f"  Verdict: {verdict}")

        results["H03"] = {
            "hypothesis": "Artin Dimension She-Leveque",
            "n_dims": len(dims),
            "n_valid_gaps": len(gap_ratios_v),
            "C_fit": round(float(C_fit), 4),
            "beta_fit": round(float(beta_fit), 4),
            "max_rel_residual": round(max_rel_residual, 4),
            "mean_rel_residual": round(mean_rel_residual, 4),
            "beta_cv": round(float(beta_cv), 4),
            "n_bootstraps": len(betas),
            "kill_criterion": "residuals > 10% or beta unstable (CV > 0.5)",
            "killed": killed,
            "verdict": verdict
        }
    except RuntimeError as e:
        print(f"  Curve fit failed: {e}")
        results["H03"] = {
            "hypothesis": "Artin Dimension She-Leveque",
            "error": f"Curve fit failed: {e}",
            "killed": True,
            "verdict": "KILLED (fit failure)"
        }
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback; traceback.print_exc()
    results["H03"] = {"error": str(e), "verdict": "ERROR"}

# =====================================================================
# Summary Table
# =====================================================================
print("\n" + "=" * 72)
print(f"{'Hypothesis':<12} {'Verdict':<20} {'Key Statistic':<30} {'Kill?'}")
print("-" * 72)

summaries = [
    ("H60", f"optimal_k={results.get('H60',{}).get('optimal_k_bic','?')}"),
    ("H61", f"ratio={results.get('H61',{}).get('ratio','?')}:1"),
]

# H27
h27 = results.get("H27", {})
if "slope" in h27:
    summaries.append(("H27", f"slope={h27['slope']}, p={h27['p_value']:.2e}"))
else:
    summaries.append(("H27", h27.get("note", "untestable")[:30]))

# H84
h84 = results.get("H84", {})
summaries.append(("H84", f"alpha={h84.get('alpha_exponent','?')}"))

# H03
h03 = results.get("H03", {})
if "max_rel_residual" in h03:
    summaries.append(("H03", f"resid={h03['max_rel_residual']}, beta_cv={h03['beta_cv']}"))
else:
    summaries.append(("H03", h03.get("error", "?")[:30]))

for h, stat in summaries:
    r = results.get(h, {})
    v = r.get("verdict", "ERROR")
    k = "YES" if r.get("killed", False) else "NO"
    print(f"{h:<12} {v:<20} {stat:<30} {k}")

print("=" * 72)

# ── Save results ─────────────────────────────────────────────────────
out_path = Path("F:/Prometheus/charon/data/frontier_batch3.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults saved to {out_path}")

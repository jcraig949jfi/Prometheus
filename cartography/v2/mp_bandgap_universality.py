"""
Materials Project: Band Gap Distribution Universality Classes
=============================================================
Test whether rescaled band gap distributions across crystal systems
collapse onto a single universal curve.
"""

import json
import numpy as np
from scipy import stats
from itertools import combinations
from pathlib import Path

# ── Load data ──────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent.parent / "physics" / "data" / "materials_project_10k.json"
OUT_PATH = Path(__file__).parent / "mp_bandgap_universality_results.json"

with open(DATA_PATH) as f:
    raw = json.load(f)

# ── Group nonzero band gaps by crystal system ──────────────────────────
systems = {}
for rec in raw:
    cs = rec["crystal_system"]
    bg = rec["band_gap"]
    if bg > 0:
        systems.setdefault(cs, []).append(bg)

# Convert to arrays, require minimum count for statistics
MIN_COUNT = 30
system_data = {}
for cs, vals in systems.items():
    arr = np.array(vals)
    if len(arr) >= MIN_COUNT:
        system_data[cs] = arr

print(f"Crystal systems with >= {MIN_COUNT} nonzero band gaps:")
for cs, arr in sorted(system_data.items(), key=lambda x: -len(x[1])):
    print(f"  {cs}: n={len(arr)}, mean={arr.mean():.3f}, std={arr.std():.3f}, "
          f"median={np.median(arr):.3f}, skew={stats.skew(arr):.3f}, kurtosis={stats.kurtosis(arr):.3f}")

# ── Rescale: z = (bg - mean) / std ────────────────────────────────────
rescaled = {}
for cs, arr in system_data.items():
    mu, sigma = arr.mean(), arr.std()
    if sigma > 1e-10:
        rescaled[cs] = (arr - mu) / sigma

# ── KS tests between all pairs of rescaled distributions ──────────────
print("\n=== KS Tests Between Rescaled Distributions ===")
ks_results = {}
system_names = sorted(rescaled.keys())
for a, b in combinations(system_names, 2):
    stat, pval = stats.ks_2samp(rescaled[a], rescaled[b])
    ks_results[f"{a} vs {b}"] = {"statistic": float(stat), "p_value": float(pval)}
    collapse = "COLLAPSE" if pval > 0.05 else "DISTINCT"
    print(f"  {a:12s} vs {b:12s}: KS={stat:.4f}, p={pval:.4e} [{collapse}]")

# Overall collapse assessment
p_values = [v["p_value"] for v in ks_results.values()]
n_collapse = sum(1 for p in p_values if p > 0.05)
n_total = len(p_values)
print(f"\nCollapse summary: {n_collapse}/{n_total} pairs consistent (p>0.05)")

# ── Fit distributions to each crystal system (on raw nonzero data) ────
# Candidates: Gaussian, Exponential, Weibull, Gamma, Lognormal
print("\n=== Distribution Fits (AIC) Per Crystal System ===")

def fit_and_aic(data, dist_name):
    """Fit a distribution and return AIC. Returns (params, aic, ks_stat, ks_p)."""
    n = len(data)
    try:
        if dist_name == "norm":
            params = stats.norm.fit(data)
            ll = np.sum(stats.norm.logpdf(data, *params))
            k = 2
        elif dist_name == "expon":
            params = stats.expon.fit(data, floc=0)
            ll = np.sum(stats.expon.logpdf(data, *params))
            k = 1  # only scale (loc fixed)
        elif dist_name == "weibull_min":
            params = stats.weibull_min.fit(data, floc=0)
            ll = np.sum(stats.weibull_min.logpdf(data, *params))
            k = 2  # shape + scale (loc fixed)
        elif dist_name == "gamma":
            params = stats.gamma.fit(data, floc=0)
            ll = np.sum(stats.gamma.logpdf(data, *params))
            k = 2  # shape + scale (loc fixed)
        elif dist_name == "lognorm":
            params = stats.lognorm.fit(data, floc=0)
            ll = np.sum(stats.lognorm.logpdf(data, *params))
            k = 2  # shape + scale (loc fixed)
        else:
            return None

        if not np.isfinite(ll):
            return None

        aic = 2 * k - 2 * ll
        # KS test against fitted distribution
        dist_obj = getattr(stats, dist_name)
        ks_stat, ks_p = stats.kstest(data, dist_name, args=params)
        return {"params": [float(p) for p in params], "aic": float(aic),
                "loglik": float(ll), "k": k,
                "ks_stat": float(ks_stat), "ks_p": float(ks_p)}
    except Exception as e:
        return None

DISTS = ["norm", "expon", "weibull_min", "gamma", "lognorm"]
fit_results = {}

for cs in sorted(system_data.keys()):
    arr = system_data[cs]
    fit_results[cs] = {}
    best_aic = np.inf
    best_name = None
    for dname in DISTS:
        result = fit_and_aic(arr, dname)
        if result is not None:
            fit_results[cs][dname] = result
            if result["aic"] < best_aic:
                best_aic = result["aic"]
                best_name = dname
    fit_results[cs]["best"] = best_name
    print(f"\n  {cs} (n={len(arr)}):")
    for dname in DISTS:
        if dname in fit_results[cs]:
            r = fit_results[cs][dname]
            tag = " *** BEST" if dname == best_name else ""
            print(f"    {dname:12s}: AIC={r['aic']:10.1f}  KS_p={r['ks_p']:.4e}{tag}")

# ── Fit the POOLED rescaled distribution ──────────────────────────────
print("\n=== Universal (Pooled Rescaled) Distribution Fit ===")
pooled = np.concatenate(list(rescaled.values()))
print(f"Pooled n={len(pooled)}, mean={pooled.mean():.4f}, std={pooled.std():.4f}")
print(f"  skew={stats.skew(pooled):.4f}, kurtosis={stats.kurtosis(pooled):.4f}")

# For the rescaled data, shift to positive for distributions that need it
pooled_shifted = pooled - pooled.min() + 0.001  # shift to positive

pooled_fits = {}
for dname in DISTS:
    if dname == "norm":
        result = fit_and_aic(pooled, dname)
    else:
        result = fit_and_aic(pooled_shifted, dname)
    if result is not None:
        pooled_fits[dname] = result

best_pooled = min(pooled_fits, key=lambda d: pooled_fits[d]["aic"])
for dname in DISTS:
    if dname in pooled_fits:
        r = pooled_fits[dname]
        tag = " *** BEST" if dname == best_pooled else ""
        print(f"  {dname:12s}: AIC={r['aic']:10.1f}  KS_p={r['ks_p']:.4e}{tag}")

# ── Anderson-Darling normality test on pooled rescaled ─────────────────
ad_stat, ad_crit, ad_sig = stats.anderson(pooled, dist='norm')
print(f"\nAnderson-Darling (normality) on pooled rescaled: stat={ad_stat:.4f}")
for c, s in zip(ad_crit, ad_sig):
    print(f"  significance {s}%: critical={c:.4f} {'REJECT' if ad_stat > c else 'ACCEPT'}")

# ── Shapiro-Wilk on subsamples ────────────────────────────────────────
if len(pooled) > 5000:
    rng = np.random.default_rng(42)
    subsample = rng.choice(pooled, 5000, replace=False)
else:
    subsample = pooled
sw_stat, sw_p = stats.shapiro(subsample)
print(f"Shapiro-Wilk on pooled rescaled (n={len(subsample)}): W={sw_stat:.6f}, p={sw_p:.4e}")

# ── Summary assessment ─────────────────────────────────────────────────
print("\n" + "="*60)
print("SUMMARY")
print("="*60)

collapse_fraction = n_collapse / n_total if n_total > 0 else 0
if collapse_fraction > 0.7:
    collapse_verdict = "STRONG COLLAPSE — distributions are consistent with a single universal shape"
elif collapse_fraction > 0.4:
    collapse_verdict = "PARTIAL COLLAPSE — some crystal systems share a universal shape, others deviate"
else:
    collapse_verdict = "NO COLLAPSE — crystal systems have distinct band gap distribution shapes"

print(f"Collapse: {n_collapse}/{n_total} pairs ({collapse_fraction:.1%}) — {collapse_verdict}")
print(f"Best pooled fit: {best_pooled}")

# Best fit per system
best_per_system = {cs: fit_results[cs]["best"] for cs in fit_results}
from collections import Counter
best_counts = Counter(best_per_system.values())
print(f"Best fit per system: {dict(best_counts)}")

# ── Lattice-PDG comparison ─────────────────────────────────────────────
# The "Lattice-PDG Dimensionless Universality" concept asks whether
# rescaled physical distributions from different lattice types collapse
# the way critical phenomena do. In stat mech, universality classes
# depend on symmetry + dimensionality, not microscopic details.
# Band gaps are NOT critical phenomena, but IF they collapse, it suggests
# the distribution shape is set by something more universal than crystal
# symmetry — possibly the density of states topology.

lattice_pdg_note = (
    "Band gap distributions are not critical phenomena, so 'universality' here "
    "means shape-invariance under rescaling, not RG fixed points. "
    "If collapse occurs, it suggests the distribution shape is determined by "
    "density-of-states topology rather than crystal symmetry specifics. "
    "If distinct classes emerge, crystal symmetry constrains the gap distribution "
    "beyond simple location-scale differences."
)
print(f"\nLattice-PDG note: {lattice_pdg_note}")

# ── Save results ───────────────────────────────────────────────────────
output = {
    "metadata": {
        "source": "materials_project_10k.json",
        "total_materials": len(raw),
        "nonzero_bandgap": sum(len(v) for v in system_data.values()),
        "crystal_systems_analyzed": list(system_data.keys()),
        "min_count_threshold": MIN_COUNT,
        "date": "2026-04-11"
    },
    "per_system_stats": {
        cs: {
            "n": len(arr),
            "mean": float(arr.mean()),
            "std": float(arr.std()),
            "median": float(np.median(arr)),
            "skew": float(stats.skew(arr)),
            "kurtosis": float(stats.kurtosis(arr))
        }
        for cs, arr in system_data.items()
    },
    "ks_pairwise": ks_results,
    "collapse_summary": {
        "pairs_tested": n_total,
        "pairs_consistent": n_collapse,
        "fraction": collapse_fraction,
        "verdict": collapse_verdict
    },
    "distribution_fits": {
        cs: {
            dname: fit_results[cs][dname]
            for dname in DISTS if dname in fit_results[cs]
        } | {"best": fit_results[cs]["best"]}
        for cs in fit_results
    },
    "pooled_rescaled_fits": {
        dname: pooled_fits[dname] for dname in DISTS if dname in pooled_fits
    } | {"best": best_pooled},
    "normality_tests": {
        "anderson_darling": {
            "statistic": float(ad_stat),
            "critical_values": {f"{s}%": float(c) for c, s in zip(ad_crit, ad_sig)},
            "reject_at_5pct": bool(ad_stat > ad_crit[2])
        },
        "shapiro_wilk": {
            "statistic": float(sw_stat),
            "p_value": float(sw_p),
            "n_tested": len(subsample)
        }
    },
    "lattice_pdg_note": lattice_pdg_note
}

with open(OUT_PATH, "w") as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {OUT_PATH}")

"""
Maass Form Spectral Parameter Distribution Analysis
=====================================================
Measures empirical spectral parameter distribution and compares to:
- Weyl law density prediction N(R) ~ cR^2
- GUE nearest-neighbor spacing (chaotic systems)
- Poisson nearest-neighbor spacing (integrable systems)

Data: LMFDB PostgreSQL dump of maass_newforms (14,995 records)
"""

import json
import numpy as np
from scipy import stats
from collections import Counter, defaultdict
from pathlib import Path

# ── Load data ──────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent.parent / "lmfdb_dump" / "maass_newforms.json"
OUT_PATH = Path(__file__).parent / "maass_spectral_stats_results.json"

with open(DATA_PATH) as f:
    raw = json.load(f)

records = raw["records"]
print(f"Loaded {len(records)} Maass newform records")

# Parse spectral parameters (stored as strings)
forms = []
for r in records:
    try:
        sp = float(r["spectral_parameter"])
    except (ValueError, TypeError):
        continue
    forms.append({
        "spectral_parameter": sp,
        "level": int(r["level"]),
        "symmetry": int(r["symmetry"]),  # 1=even, -1=odd
    })

print(f"Parsed {len(forms)} forms with valid spectral parameters")

# ── Helper: Compute spacing statistics ─────────────────────────────────
def spacing_stats(spectral_params):
    """Compute normalized nearest-neighbor spacings from sorted eigenvalues."""
    if len(spectral_params) < 5:
        return None
    sp = np.sort(spectral_params)
    gaps = np.diff(sp)
    # Normalize: divide by mean spacing (unfolding)
    mean_gap = np.mean(gaps)
    if mean_gap <= 0:
        return None
    s = gaps / mean_gap
    return s

def ks_tests(spacings):
    """KS test against Poisson (exponential) and GUE (Wigner surmise)."""
    if spacings is None or len(spacings) < 10:
        return {"poisson_ks": None, "poisson_p": None, "gue_ks": None, "gue_p": None,
                "goe_ks": None, "goe_p": None, "n_spacings": int(len(spacings)) if spacings is not None else 0,
                "mean_spacing_normalized": None, "std_spacing_normalized": None, "var_ratio": None}

    # Poisson: P(s) = exp(-s), CDF = 1 - exp(-s)
    ks_poi, p_poi = stats.kstest(spacings, 'expon', args=(0, 1))

    # GUE Wigner surmise: P(s) = (32/pi^2) s^2 exp(-4s^2/pi)
    # CDF: 1 - exp(-4s^2/pi) * (1 + 2s*sqrt(4/pi)*...)
    # Use custom CDF via numerical integration
    # Actually, for GUE the Wigner surmise CDF is: F(s) = 1 - erfc(2s/sqrt(pi))...
    # More precisely: P_GUE(s) = (32/pi^2) s^2 exp(-4s^2/pi)
    # CDF via integration
    from scipy.integrate import cumulative_trapezoid
    s_grid = np.linspace(0, max(spacings.max() * 1.1, 5), 10000)
    ds = s_grid[1] - s_grid[0]
    pdf_gue = (32 / np.pi**2) * s_grid**2 * np.exp(-4 * s_grid**2 / np.pi)
    cdf_gue = np.concatenate([[0], cumulative_trapezoid(pdf_gue, s_grid)])
    # Normalize CDF to ensure it reaches 1
    cdf_gue = cdf_gue / cdf_gue[-1]

    # Interpolate CDF at data points
    cdf_at_data = np.interp(np.sort(spacings), s_grid, cdf_gue)
    n = len(spacings)
    ecdf = np.arange(1, n + 1) / n
    ks_gue = np.max(np.abs(ecdf - cdf_at_data))
    # Approximate p-value
    p_gue = stats.kstwo.sf(ks_gue, n)

    # GOE Wigner surmise for comparison: P(s) = (pi/2) s exp(-pi s^2/4)
    pdf_goe = (np.pi / 2) * s_grid * np.exp(-np.pi * s_grid**2 / 4)
    cdf_goe = np.concatenate([[0], cumulative_trapezoid(pdf_goe, s_grid)])
    cdf_goe = cdf_goe / cdf_goe[-1]
    cdf_goe_at_data = np.interp(np.sort(spacings), s_grid, cdf_goe)
    ks_goe = np.max(np.abs(ecdf - cdf_goe_at_data))
    p_goe = stats.kstwo.sf(ks_goe, n)

    return {
        "poisson_ks": float(ks_poi), "poisson_p": float(p_poi),
        "gue_ks": float(ks_gue), "gue_p": float(p_gue),
        "goe_ks": float(ks_goe), "goe_p": float(p_goe),
        "n_spacings": int(len(spacings)),
        "mean_spacing_normalized": float(np.mean(spacings)),
        "std_spacing_normalized": float(np.std(spacings)),
        "var_ratio": float(np.var(spacings)),  # Poisson: var=1, GUE: var≈0.178
    }


# ── Group by (level, symmetry) ────────────────────────────────────────
groups = defaultdict(list)
for f in forms:
    groups[(f["level"], f["symmetry"])].append(f["spectral_parameter"])

print(f"\n{len(groups)} unique (level, symmetry) groups")

# ── Per-group analysis ─────────────────────────────────────────────────
group_results = []
for (level, sym), sps in sorted(groups.items()):
    s = spacing_stats(np.array(sps))
    if s is None:
        continue
    ks = ks_tests(s)
    ks["level"] = level
    ks["symmetry"] = "even" if sym == 1 else "odd"
    ks["n_eigenvalues"] = len(sps)
    ks["spectral_range"] = [float(min(sps)), float(max(sps))]
    group_results.append(ks)

print(f"Computed spacing stats for {len(group_results)} groups with >=5 eigenvalues")

# ── Aggregate: which model wins? ──────────────────────────────────────
poisson_wins = 0
gue_wins = 0
goe_wins = 0
for g in group_results:
    if g["poisson_p"] is None:
        continue
    # Winner = highest p-value (least rejected)
    best = max(
        ("poisson", g["poisson_p"]),
        ("gue", g["gue_p"]),
        ("goe", g["goe_p"]),
        key=lambda x: x[1]
    )
    if best[0] == "poisson":
        poisson_wins += 1
    elif best[0] == "gue":
        gue_wins += 1
    else:
        goe_wins += 1

print(f"\nModel preference (by highest KS p-value):")
print(f"  Poisson: {poisson_wins}, GUE: {gue_wins}, GOE: {goe_wins}")

# ── Level dependence ──────────────────────────────────────────────────
level_agg = defaultdict(lambda: {"poisson_p": [], "gue_p": [], "goe_p": [], "var_ratio": []})
for g in group_results:
    if g["poisson_p"] is None:
        continue
    lev = g["level"]
    level_agg[lev]["poisson_p"].append(g["poisson_p"])
    level_agg[lev]["gue_p"].append(g["gue_p"])
    level_agg[lev]["goe_p"].append(g["goe_p"])
    level_agg[lev]["var_ratio"].append(g["var_ratio"])

level_summary = {}
for lev in sorted(level_agg):
    la = level_agg[lev]
    level_summary[str(lev)] = {
        "mean_poisson_p": float(np.mean(la["poisson_p"])),
        "mean_gue_p": float(np.mean(la["gue_p"])),
        "mean_goe_p": float(np.mean(la["goe_p"])),
        "mean_var_ratio": float(np.mean(la["var_ratio"])),
        "n_groups": len(la["poisson_p"]),
    }

# ── Symmetry dependence ──────────────────────────────────────────────
sym_agg = defaultdict(lambda: {"poisson_p": [], "gue_p": [], "goe_p": [], "var_ratio": []})
for g in group_results:
    if g["poisson_p"] is None:
        continue
    sym_agg[g["symmetry"]]["poisson_p"].append(g["poisson_p"])
    sym_agg[g["symmetry"]]["gue_p"].append(g["gue_p"])
    sym_agg[g["symmetry"]]["goe_p"].append(g["goe_p"])
    sym_agg[g["symmetry"]]["var_ratio"].append(g["var_ratio"])

symmetry_summary = {}
for sym in ["even", "odd"]:
    if sym not in sym_agg:
        continue
    sa = sym_agg[sym]
    symmetry_summary[sym] = {
        "mean_poisson_p": float(np.mean(sa["poisson_p"])),
        "mean_gue_p": float(np.mean(sa["gue_p"])),
        "mean_goe_p": float(np.mean(sa["goe_p"])),
        "mean_var_ratio": float(np.mean(sa["var_ratio"])),
        "n_groups": len(sa["poisson_p"]),
    }

print(f"\nSymmetry dependence:")
for sym, s in symmetry_summary.items():
    print(f"  {sym}: Poisson p={s['mean_poisson_p']:.4f}, GUE p={s['mean_gue_p']:.4f}, GOE p={s['mean_goe_p']:.4f}, var={s['mean_var_ratio']:.4f}")

# ── Level-averaged spacing distribution ───────────────────────────────
all_spacings = []
for (level, sym), sps in groups.items():
    s = spacing_stats(np.array(sps))
    if s is not None:
        all_spacings.extend(s.tolist())

all_spacings = np.array(all_spacings)
print(f"\nTotal pooled spacings: {len(all_spacings)}")

pooled_ks = ks_tests(all_spacings)
print(f"Pooled KS: Poisson p={pooled_ks['poisson_p']:.6f}, GUE p={pooled_ks['gue_p']:.6f}, GOE p={pooled_ks['goe_p']:.6f}")
print(f"Pooled variance ratio: {pooled_ks['var_ratio']:.4f} (Poisson=1, GOE~0.273, GUE~0.178)")

# ── Spacing histogram for reporting ──────────────────────────────────
hist_counts, hist_edges = np.histogram(all_spacings, bins=50, range=(0, 4), density=True)
spacing_histogram = {
    "bin_edges": hist_edges.tolist(),
    "density": hist_counts.tolist(),
}

# ── Weyl law fit ──────────────────────────────────────────────────────
# For Maass forms on Gamma_0(N)\H, the Weyl law gives:
# N(R) = (Area / 4pi) R^2 - (scattering term) + lower order
# Area = pi * N * prod_{p|N} (1 + 1/p) / 3  for Gamma_0(N)
# Simplified: N(R) ~ c * R^2 for large R

# Fit per level
weyl_fits = {}
for level in sorted(set(f["level"] for f in forms)):
    level_sps = sorted([f["spectral_parameter"] for f in forms if f["level"] == level])
    if len(level_sps) < 10:
        continue

    R = np.array(level_sps)
    N_empirical = np.arange(1, len(R) + 1)

    # Fit N(R) = a * R^2 + b * R + c
    # Use least squares
    A = np.column_stack([R**2, R, np.ones_like(R)])
    coeffs, residuals, _, _ = np.linalg.lstsq(A, N_empirical, rcond=None)

    # Theoretical Weyl coefficient: Area/(4*pi) where Area = pi*N*prod(1+1/p)/3
    # For level 1: Area = pi/3, so c_theory = 1/12
    # For level N: Area = (N * prod_{p|N}(1+1/p)) * pi/3
    # c_theory = N * prod_{p|N}(1+1/p) / 12

    # Compute theoretical coefficient
    def weyl_coeff(N):
        """Theoretical leading Weyl law coefficient for Gamma_0(N)."""
        product = 1.0
        n = N
        p = 2
        while p * p <= n:
            if n % p == 0:
                product *= (1 + 1.0/p)
                while n % p == 0:
                    n //= p
            p += 1
        if n > 1:
            product *= (1 + 1.0/n)
        return N * product / 12.0

    c_theory = weyl_coeff(level)

    weyl_fits[str(level)] = {
        "n_forms": len(level_sps),
        "fit_quadratic_coeff": float(coeffs[0]),
        "fit_linear_coeff": float(coeffs[1]),
        "fit_constant": float(coeffs[2]),
        "theoretical_weyl_coeff": float(c_theory),
        "ratio_empirical_to_theory": float(coeffs[0] / c_theory) if c_theory > 0 else None,
        "R_max": float(R[-1]),
    }

# Report Weyl fit quality
print(f"\n-- Weyl Law Fits --")
for lev, wf in sorted(weyl_fits.items(), key=lambda x: int(x[0])):
    ratio = wf["ratio_empirical_to_theory"]
    if ratio is not None:
        print(f"  Level {lev}: c_emp={wf['fit_quadratic_coeff']:.6f}, c_theory={wf['theoretical_weyl_coeff']:.6f}, ratio={ratio:.4f} ({wf['n_forms']} forms)")

# ── Large-group analysis (more reliable) ──────────────────────────────
large_group_results = [g for g in group_results if g["n_spacings"] >= 30]
print(f"\n-- Large groups (>=30 spacings): {len(large_group_results)} --")

lg_poisson = sum(1 for g in large_group_results if g["poisson_p"] > g["gue_p"] and g["poisson_p"] > g["goe_p"])
lg_gue = sum(1 for g in large_group_results if g["gue_p"] > g["poisson_p"] and g["gue_p"] > g["goe_p"])
lg_goe = sum(1 for g in large_group_results if g["goe_p"] > g["poisson_p"] and g["goe_p"] > g["gue_p"])
print(f"  Poisson: {lg_poisson}, GUE: {lg_gue}, GOE: {lg_goe}")

# Variance ratio diagnostic (most robust)
lg_vars = [g["var_ratio"] for g in large_group_results]
print(f"  Mean var ratio: {np.mean(lg_vars):.4f} (Poisson=1, GOE~0.273, GUE~0.178)")

# ── Assemble results ──────────────────────────────────────────────────
results = {
    "metadata": {
        "source": str(DATA_PATH),
        "n_records": len(forms),
        "n_groups_analyzed": len(group_results),
        "n_large_groups": len(large_group_results),
        "total_pooled_spacings": len(all_spacings),
        "unique_levels": len(set(f["level"] for f in forms)),
    },
    "pooled_spacing_test": pooled_ks,
    "spacing_histogram": spacing_histogram,
    "symmetry_dependence": symmetry_summary,
    "level_summary": level_summary,
    "weyl_fits": weyl_fits,
    "per_group_results": group_results,
    "model_preference_all": {
        "poisson_wins": poisson_wins,
        "gue_wins": gue_wins,
        "goe_wins": goe_wins,
    },
    "model_preference_large_groups": {
        "poisson_wins": lg_poisson,
        "gue_wins": lg_gue,
        "goe_wins": lg_goe,
        "mean_var_ratio": float(np.mean(lg_vars)) if lg_vars else None,
    },
    "interpretation": {
        "spacing_model": (
            "GOE" if lg_goe > lg_gue and lg_goe > lg_poisson else
            "GUE" if lg_gue > lg_poisson else "Poisson"
        ),
        "variance_diagnostic": (
            "Poisson-like" if np.mean(lg_vars) > 0.7 else
            "GOE-like" if np.mean(lg_vars) > 0.2 else "GUE-like"
        ) if lg_vars else "insufficient_data",
        "symmetry_matters": bool(
            len(symmetry_summary) == 2 and
            abs(symmetry_summary.get("even", {}).get("mean_var_ratio", 0) -
                symmetry_summary.get("odd", {}).get("mean_var_ratio", 0)) > 0.1
        ),
        "weyl_law_holds": None,  # filled below
    },
}

# Weyl law assessment
ratios = [wf["ratio_empirical_to_theory"] for wf in weyl_fits.values()
          if wf["ratio_empirical_to_theory"] is not None and wf["n_forms"] >= 30]
if ratios:
    mean_ratio = np.mean(ratios)
    std_ratio = np.std(ratios)
    results["interpretation"]["weyl_law_holds"] = bool(abs(mean_ratio - 1.0) < 0.3)
    results["interpretation"]["weyl_mean_ratio"] = float(mean_ratio)
    results["interpretation"]["weyl_std_ratio"] = float(std_ratio)
    print(f"\nWeyl law: mean ratio emp/theory = {mean_ratio:.4f} ± {std_ratio:.4f}")

# ── Save ──────────────────────────────────────────────────────────────
with open(OUT_PATH, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {OUT_PATH}")

# ── Final summary ─────────────────────────────────────────────────────
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Spacing model preference: {results['interpretation']['spacing_model']}")
print(f"Variance diagnostic: {results['interpretation']['variance_diagnostic']}")
print(f"Symmetry matters: {results['interpretation']['symmetry_matters']}")
print(f"Weyl law holds: {results['interpretation']['weyl_law_holds']}")
if results['interpretation'].get('weyl_mean_ratio'):
    print(f"Weyl ratio: {results['interpretation']['weyl_mean_ratio']:.4f}")

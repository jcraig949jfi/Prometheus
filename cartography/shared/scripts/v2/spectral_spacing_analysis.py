#!/usr/bin/env python3
"""
C05: Spectral Operator Matching — Maass Form Spacing Statistics

Verifies GUE statistics in Maass spectral data and cross-compares
with lattice determinants and number field discriminants.
"""

import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

# ---------- paths ----------
BASE = Path(__file__).resolve().parents[4]  # F:/Prometheus
MAASS_PATH = BASE / "cartography" / "lmfdb_dump" / "maass_rigor.json"
LATTICE_PATH = BASE / "cartography" / "lmfdb_dump" / "lat_lattices.json"
NF_PATH = BASE / "cartography" / "number_fields" / "data" / "number_fields.json"
OUT_PATH = Path(__file__).resolve().parent / "spectral_spacing_results.json"

# Try scipy; fall back to manual KS
try:
    from scipy.stats import kstest as scipy_kstest
    from scipy.integrate import quad as scipy_quad
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


# ================================================================
# Helper functions
# ================================================================

def ks_statistic(data, cdf_func):
    """Two-sided KS statistic of sorted data against a theoretical CDF."""
    n = len(data)
    if n == 0:
        return 1.0
    s = np.sort(data)
    ecdf = np.arange(1, n + 1) / n
    ecdf_minus = np.arange(0, n) / n
    theo = np.array([cdf_func(x) for x in s])
    d_plus = np.max(ecdf - theo)
    d_minus = np.max(theo - ecdf_minus)
    return float(max(d_plus, d_minus))


def poisson_cdf(s):
    """CDF for Poisson spacing: P(s) = exp(-s), F(s) = 1 - exp(-s)."""
    if s < 0:
        return 0.0
    return 1.0 - math.exp(-s)


def gue_cdf(s):
    """CDF for Wigner surmise (GUE): P(s) = (pi*s/2)*exp(-pi*s^2/4)."""
    if s < 0:
        return 0.0
    return 1.0 - math.exp(-math.pi * s * s / 4.0)


def compute_spacings(values):
    """Sort values and return normalized nearest-neighbor spacings."""
    v = np.sort(values)
    spacings = np.diff(v)
    mean_sp = np.mean(spacings)
    if mean_sp <= 0:
        return np.array([])
    return spacings / mean_sp


def spacing_histogram(spacings, nbins=50, smax=4.0):
    """Compute a normalized histogram of spacings."""
    counts, edges = np.histogram(spacings, bins=nbins, range=(0, smax), density=True)
    centers = 0.5 * (edges[:-1] + edges[1:])
    return centers.tolist(), counts.tolist()


def level_repulsion_metric(spacings, threshold=0.1):
    """Fraction of spacings below threshold (near-zero). GUE -> ~0, Poisson -> ~threshold."""
    if len(spacings) == 0:
        return float('nan')
    return float(np.mean(spacings < threshold))


def number_variance(values_sorted, L_values):
    """
    Compute Sigma^2(L): variance in the number of eigenvalues in
    an interval of length L (in units of mean spacing).
    Slide a window of width L*mean_spacing across the spectrum.
    """
    v = np.asarray(values_sorted, dtype=np.float64)
    n = len(v)
    if n < 10:
        return {str(L): float('nan') for L in L_values}

    spacings = np.diff(v)
    mean_sp = np.mean(spacings)
    if mean_sp <= 0:
        return {str(L): float('nan') for L in L_values}

    results = {}
    for L in L_values:
        width = L * mean_sp
        # count eigenvalues in [v[i], v[i]+width) for many starting points
        # use binary search for efficiency
        counts = []
        # sample up to 2000 starting points
        step = max(1, n // 2000)
        for i in range(0, n, step):
            left = v[i]
            right = left + width
            c = np.searchsorted(v, right, side='right') - i
            counts.append(c)
        counts = np.array(counts, dtype=np.float64)
        results[str(L)] = float(np.var(counts))
    return results


def delta3_statistic(values_sorted, L_values):
    """
    Compute Delta_3(L) spectral rigidity: measures how well the
    staircase N(E) can be fit by a straight line over an interval of length L.
    Uses the Mehta-Dyson relation: Delta_3(L) = <min_{A,B} (1/L) int_0^L [N(x+a) - Ax - B]^2 dx>
    We approximate via discrete sampling.
    """
    v = np.asarray(values_sorted, dtype=np.float64)
    n = len(v)
    if n < 20:
        return {str(L): float('nan') for L in L_values}

    spacings = np.diff(v)
    mean_sp = np.mean(spacings)
    if mean_sp <= 0:
        return {str(L): float('nan') for L in L_values}

    results = {}
    for L in L_values:
        width = L * mean_sp
        if width <= 0:
            results[str(L)] = float('nan')
            continue

        d3_samples = []
        step = max(1, n // 500)
        for i in range(0, n - 1, step):
            a = v[i]
            b = a + width
            if b > v[-1]:
                break
            # staircase: N(x) = number of eigenvalues <= x, shifted so N(a)=0
            mask = (v >= a) & (v <= b)
            pts = v[mask]
            if len(pts) < 3:
                continue
            # x coordinates normalized to [0, L]
            x_norm = (pts - a) / mean_sp
            n_staircase = np.arange(1, len(pts) + 1, dtype=np.float64)
            # best fit line: N = A*x + B
            try:
                A_fit = np.polyfit(x_norm, n_staircase, 1)
                fit_vals = np.polyval(A_fit, x_norm)
                residuals = n_staircase - fit_vals
                d3_val = np.mean(residuals ** 2) / L
                d3_samples.append(d3_val)
            except np.linalg.LinAlgError:
                continue

        if d3_samples:
            results[str(L)] = float(np.mean(d3_samples))
        else:
            results[str(L)] = float('nan')
    return results


def analyze_spectrum(label, values, min_count=50):
    """Full spacing analysis on a sorted array of eigenvalue-like quantities."""
    values = np.sort(np.asarray(values, dtype=np.float64))
    n = len(values)
    if n < min_count:
        return None

    spacings = compute_spacings(values)
    if len(spacings) == 0:
        return None

    # KS tests
    if HAS_SCIPY:
        ks_poisson = scipy_kstest(spacings, lambda s: 1 - np.exp(-s))
        ks_gue = scipy_kstest(spacings, lambda s: 1 - np.exp(-np.pi * s**2 / 4))
        ks_p_stat, ks_p_pval = float(ks_poisson.statistic), float(ks_poisson.pvalue)
        ks_g_stat, ks_g_pval = float(ks_gue.statistic), float(ks_gue.pvalue)
    else:
        ks_p_stat = ks_statistic(spacings, poisson_cdf)
        ks_g_stat = ks_statistic(spacings, gue_cdf)
        ks_p_pval = float('nan')
        ks_g_pval = float('nan')

    L_values = [0.1, 0.5, 1.0, 2.0, 5.0]
    nv = number_variance(values, L_values)
    d3 = delta3_statistic(values, L_values)

    hist_centers, hist_density = spacing_histogram(spacings)

    repulsion = level_repulsion_metric(spacings)

    # classify
    closer_to = "GUE" if ks_g_stat < ks_p_stat else "Poisson"

    return {
        "label": label,
        "count": n,
        "mean_spacing": float(np.mean(np.diff(values))),
        "ks_poisson": {"statistic": ks_p_stat, "pvalue": ks_p_pval},
        "ks_gue": {"statistic": ks_g_stat, "pvalue": ks_g_pval},
        "closer_to": closer_to,
        "level_repulsion_frac_below_0.1": repulsion,
        "number_variance": nv,
        "delta3": d3,
        "histogram": {"centers": hist_centers, "density": hist_density},
    }


# ================================================================
# Main
# ================================================================

def main():
    results = {"maass_by_level": [], "cross_comparison": [], "summary": {}}

    # ---------- 1. Load Maass data ----------
    print("Loading Maass data...")
    with open(MAASS_PATH) as f:
        maass_data = json.load(f)
    records = maass_data["records"]
    print(f"  {len(records)} Maass forms loaded")

    # Group by level (mixed symmetry) and by (level, symmetry)
    by_level = defaultdict(list)
    by_level_sym = defaultdict(list)
    for r in records:
        sp = r.get("spectral_parameter")
        if sp is not None:
            val = float(sp)
            by_level[r["level"]].append(val)
            sym = r.get("symmetry", -1)
            by_level_sym[(r["level"], sym)].append(val)

    # Also collect all spectral parameters
    all_spectral = []
    for vals in by_level.values():
        all_spectral.extend(vals)

    # ---------- 2a. Per-level analysis (mixed symmetry) ----------
    print("Analyzing per-level spacing statistics (mixed symmetry)...")
    levels_analyzed = 0
    gue_count = 0
    poisson_count = 0

    for level in sorted(by_level.keys()):
        vals = by_level[level]
        if len(vals) < 50:
            continue
        res = analyze_spectrum(f"maass_level_{level}", vals)
        if res is None:
            continue
        results["maass_by_level"].append(res)
        levels_analyzed += 1
        if res["closer_to"] == "GUE":
            gue_count += 1
        else:
            poisson_count += 1

    print(f"  Analyzed {levels_analyzed} levels (>= 50 forms)")
    print(f"  GUE-like: {gue_count}, Poisson-like: {poisson_count}")

    # ---------- 2b. Per (level, symmetry) analysis ----------
    # This is the correct decomposition: each (level, symmetry) gives an
    # independent spectral sequence that should individually show GUE.
    print("\nAnalyzing per (level, symmetry) spacing statistics...")
    results["maass_by_level_sym"] = []
    ls_analyzed = 0
    ls_gue = 0
    ls_poisson = 0

    for (level, sym) in sorted(by_level_sym.keys()):
        vals = by_level_sym[(level, sym)]
        if len(vals) < 50:
            continue
        sym_label = {0: "even", 1: "odd"}.get(sym, f"sym{sym}")
        res = analyze_spectrum(f"maass_level_{level}_{sym_label}", vals)
        if res is None:
            continue
        results["maass_by_level_sym"].append(res)
        ls_analyzed += 1
        if res["closer_to"] == "GUE":
            ls_gue += 1
        else:
            ls_poisson += 1

    print(f"  Analyzed {ls_analyzed} (level, symmetry) pairs (>= 50 forms)")
    print(f"  GUE-like: {ls_gue}, Poisson-like: {ls_poisson}")

    # ---------- 3. All Maass combined ----------
    print("Analyzing all Maass forms combined...")
    all_res = analyze_spectrum("maass_all", all_spectral, min_count=50)
    if all_res:
        results["maass_all"] = all_res

    # ---------- 4. Cross-comparison: Lattice determinants ----------
    print("Loading lattice determinants...")
    with open(LATTICE_PATH) as f:
        lat_data = json.load(f)
    lat_dets = []
    for r in lat_data["records"]:
        det = r.get("det")
        if det is not None:
            try:
                lat_dets.append(float(det))
            except (ValueError, TypeError):
                pass
    print(f"  {len(lat_dets)} lattice determinants loaded")

    lat_res = analyze_spectrum("lattice_determinants", lat_dets, min_count=50)
    if lat_res:
        results["cross_comparison"].append(lat_res)

    # ---------- 5. Cross-comparison: Number field discriminants ----------
    print("Loading number field discriminants...")
    with open(NF_PATH) as f:
        nf_data = json.load(f)
    nf_discs = []
    for r in nf_data:
        da = r.get("disc_abs")
        if da is not None:
            try:
                nf_discs.append(float(da))
            except (ValueError, TypeError):
                pass
    print(f"  {len(nf_discs)} number field discriminants loaded")

    nf_res = analyze_spectrum("number_field_discriminants", nf_discs, min_count=50)
    if nf_res:
        results["cross_comparison"].append(nf_res)

    # ---------- 6. Summary ----------
    # Theoretical references for number variance
    # Poisson: Sigma^2(L) = L
    # GUE: Sigma^2(L) ~ (2/pi^2) * ln(L) + const  for large L
    summary_lines = []
    summary_lines.append(f"Maass forms: {len(records)} total")
    summary_lines.append(f"  Mixed-symmetry levels analyzed: {levels_analyzed}")
    summary_lines.append(f"    GUE-like: {gue_count}/{levels_analyzed}, Poisson-like: {poisson_count}/{levels_analyzed}")
    summary_lines.append(f"  (level, symmetry) pairs analyzed: {ls_analyzed}")
    summary_lines.append(f"    GUE-like: {ls_gue}/{ls_analyzed}, Poisson-like: {ls_poisson}/{ls_analyzed}")

    if all_res:
        summary_lines.append(f"  All Maass combined: closer to {all_res['closer_to']} "
                             f"(KS_Poisson={all_res['ks_poisson']['statistic']:.4f}, "
                             f"KS_GUE={all_res['ks_gue']['statistic']:.4f})")
        summary_lines.append(f"  Level repulsion (P(s<0.1)): {all_res['level_repulsion_frac_below_0.1']:.4f}")

    if lat_res:
        summary_lines.append(f"Lattice determinants ({lat_res['count']}): closer to {lat_res['closer_to']} "
                             f"(KS_P={lat_res['ks_poisson']['statistic']:.4f}, "
                             f"KS_GUE={lat_res['ks_gue']['statistic']:.4f})")

    if nf_res:
        summary_lines.append(f"Number field discs ({nf_res['count']}): closer to {nf_res['closer_to']} "
                             f"(KS_P={nf_res['ks_poisson']['statistic']:.4f}, "
                             f"KS_GUE={nf_res['ks_gue']['statistic']:.4f})")

    results["summary"] = {
        "text": summary_lines,
        "levels_analyzed_mixed": levels_analyzed,
        "gue_count_mixed": gue_count,
        "poisson_count_mixed": poisson_count,
        "level_sym_analyzed": ls_analyzed,
        "gue_count_level_sym": ls_gue,
        "poisson_count_level_sym": ls_poisson,
        "theoretical_notes": {
            "poisson_number_variance": "Sigma^2(L) = L",
            "gue_number_variance": "Sigma^2(L) ~ (2/pi^2)*ln(L) + const",
            "poisson_delta3": "Delta_3(L) = L/15",
            "gue_delta3": "Delta_3(L) ~ (1/pi^2)*ln(L) + const",
            "poisson_repulsion": "P(0) > 0 (no repulsion)",
            "gue_repulsion": "P(s) ~ s^2 near 0 (quadratic repulsion)",
        }
    }

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for line in summary_lines:
        print(line)

    # Print top-5 most GUE-like and most Poisson-like levels
    maass_levels = results["maass_by_level"]
    by_gue_ks = sorted(maass_levels, key=lambda x: x["ks_gue"]["statistic"])
    print("\nTop-5 most GUE-like levels (lowest KS_GUE):")
    for r in by_gue_ks[:5]:
        print(f"  {r['label']} (n={r['count']}): KS_GUE={r['ks_gue']['statistic']:.4f}, "
              f"KS_Poisson={r['ks_poisson']['statistic']:.4f}, repulsion={r['level_repulsion_frac_below_0.1']:.4f}")

    # (level, symmetry) analysis
    ls_results = results.get("maass_by_level_sym", [])
    if ls_results:
        ls_by_gue = sorted(ls_results, key=lambda x: x["ks_gue"]["statistic"])
        print("\nTop-5 most GUE-like (level, symmetry) pairs:")
        for r in ls_by_gue[:5]:
            print(f"  {r['label']} (n={r['count']}): KS_GUE={r['ks_gue']['statistic']:.4f}, "
                  f"KS_Poisson={r['ks_poisson']['statistic']:.4f}, repulsion={r['level_repulsion_frac_below_0.1']:.4f}")
        ls_by_poi = sorted(ls_results, key=lambda x: x["ks_poisson"]["statistic"])
        print("\nTop-5 most Poisson-like (level, symmetry) pairs:")
        for r in ls_by_poi[:5]:
            print(f"  {r['label']} (n={r['count']}): KS_Poisson={r['ks_poisson']['statistic']:.4f}, "
                  f"KS_GUE={r['ks_gue']['statistic']:.4f}, repulsion={r['level_repulsion_frac_below_0.1']:.4f}")

    by_poi_ks = sorted(maass_levels, key=lambda x: x["ks_poisson"]["statistic"])
    print("\nTop-5 most Poisson-like levels (lowest KS_Poisson):")
    for r in by_poi_ks[:5]:
        print(f"  {r['label']} (n={r['count']}): KS_Poisson={r['ks_poisson']['statistic']:.4f}, "
              f"KS_GUE={r['ks_gue']['statistic']:.4f}, repulsion={r['level_repulsion_frac_below_0.1']:.4f}")

    # Number variance comparison
    if all_res:
        print("\nNumber variance (all Maass combined):")
        for L in ["0.1", "0.5", "1.0", "2.0", "5.0"]:
            nv_val = all_res["number_variance"].get(L, float('nan'))
            poisson_ref = float(L)
            gue_ref = (2 / math.pi**2) * math.log(float(L)) + 0.44 if float(L) > 0 else 0
            print(f"  L={L}: Sigma^2={nv_val:.4f}  (Poisson={poisson_ref:.4f}, GUE~{max(gue_ref,0):.4f})")

    if all_res:
        print("\nDelta_3 spectral rigidity (all Maass combined):")
        for L in ["0.1", "0.5", "1.0", "2.0", "5.0"]:
            d3_val = all_res["delta3"].get(L, float('nan'))
            poisson_ref = float(L) / 15.0
            gue_ref = (1 / math.pi**2) * math.log(float(L)) + 0.06 if float(L) > 0 else 0
            print(f"  L={L}: Delta_3={d3_val:.4f}  (Poisson={poisson_ref:.4f}, GUE~{max(gue_ref,0):.4f})")

    # ---------- Save ----------
    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()

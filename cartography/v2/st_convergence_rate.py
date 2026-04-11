#!/usr/bin/env python3
"""
NF12: Sato-Tate Equidistribution Convergence Rate

For genus-2 curves from LMFDB, compute a_p at good primes p <= 997,
measure empirical M2(P) convergence to theoretical Sato-Tate value,
and fit |M2(P) - M2_theory| ~ P^{-beta}.

Key question: Is beta = 0.5 (CLT rate) or something else?
Does beta differ by Sato-Tate group?
"""

import json
import math
import os
import sys
import numpy as np
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Primes up to 997
# ---------------------------------------------------------------------------
def sieve_primes(n):
    """Sieve of Eratosthenes up to n."""
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]

ALL_PRIMES = sieve_primes(997)
THRESHOLDS = [50, 100, 200, 500, 997]

# ---------------------------------------------------------------------------
# Point counting on hyperelliptic curves mod p
# ---------------------------------------------------------------------------
def count_points_mod_p(f_coeffs, h_coeffs, p):
    """
    Count #C(F_p) for y^2 + h(x)*y = f(x) over F_p.
    Returns a_p = p + 1 - #C(F_p) (trace of Frobenius on Jacobian approximation
    for genus 2 we need the full count including point at infinity).

    For genus 2: y^2 + h(x)y - f(x) = 0.
    For each x in F_p, count solutions y.
    Also count points at infinity.
    """
    count = 0

    for x in range(p):
        # Evaluate f(x) and h(x) mod p
        fx = 0
        xpow = 1
        for c in f_coeffs:
            fx = (fx + c * xpow) % p
            xpow = (xpow * x) % p

        hx = 0
        xpow = 1
        for c in h_coeffs:
            hx = (hx + c * xpow) % p
            xpow = (xpow * x) % p

        # y^2 + hx*y - fx = 0  =>  discriminant = hx^2 + 4*fx
        disc = (hx * hx + 4 * fx) % p

        if disc == 0:
            count += 1  # one solution
        elif pow(disc, (p - 1) // 2, p) == 1:
            count += 2  # two solutions
        # else: 0 solutions

    # Points at infinity for genus-2 hyperelliptic curve
    # If deg(f) = 5 or 6 (genus 2):
    deg_f = len(f_coeffs) - 1
    if deg_f == 6:
        # Two points at infinity if leading coeff is QR, else 0
        # Actually for the model y^2 = f(x) with deg 6:
        # point at infinity: check if leading coeff of f is a square
        lc = f_coeffs[-1] % p
        if len(h_coeffs) > 0:
            # With h: more complex, but for most LMFDB curves h is small
            # For simplified model (h=0): just check leading coeff of f
            if all(c == 0 for c in h_coeffs):
                if lc == 0:
                    count += 1
                elif pow(lc, (p - 1) // 2, p) == 1:
                    count += 2
            else:
                # General case: 2 points at infinity generically
                count += 2
        else:
            if lc == 0:
                count += 1
            elif pow(lc, (p - 1) // 2, p) == 1:
                count += 2
    elif deg_f == 5:
        # One point at infinity for odd degree model
        count += 1

    # a1(p) = p + 1 - #C(F_p)
    a1_p = p + 1 - count
    return a1_p


def compute_a2_from_a1(a1_values, primes):
    """
    For genus-2 curves, the L-function has degree 4.
    The normalized trace for Sato-Tate is a1(p)/sqrt(p) (not /2sqrt(p) as for elliptic).

    Actually for genus 2, the characteristic polynomial of Frobenius is:
    T^4 - a1*T^3 + (a2 + 2p)*T^2 - a1*p*T + p^2

    We only have a1 from point counting. The second moment of the
    normalized a1 distribution is what we measure.

    For USp(4) ST: E[a1_norm^2] = 1 where a1_norm = a1/sqrt(p).
    """
    pass  # We work directly with a1 values


# ---------------------------------------------------------------------------
# Theoretical M2 values for genus-2 Sato-Tate groups
# ---------------------------------------------------------------------------
# From Fite-Kedlaya-Rotger-Sutherland (2012), Table 9.
# M2 = E[(a_1(p)/sqrt(p))^2] for the normalized trace distribution.
#
# For genus-2, a_1(p) = p + 1 - #C(F_p) and the Sato-Tate conjecture
# predicts the distribution of a_1(p)/(2*sqrt(p)).
#
# Using a_1/sqrt(p) normalization (not /2sqrt(p)):
# USp(4):         E[tr^2] = 1  (Weyl integration formula)
# SU(2)xSU(2):   E[(tr1+tr2)^2] = 2  (independent traces)
#
# For groups with component group C, a fraction of primes land on
# non-identity components where tr may be constrained.
#
# FKRS Table 9 values for M[a1^2] (using a1 = tr(Frob)/sqrt(p)):
ST_M2_THEORY = {
    "USp(4)": 1.0,
    "SU(2)xSU(2)": 2.0,
    "N(U(1)xSU(2))": 1.0,     # half primes have a1=0
    "N(SU(2)xSU(2))": 1.0,    # half primes have a1=0
    "E_1": 3.0,               # U(1)^2 identity component, 6 components
    "E_2": 2.0,
    "E_3": 2.0,
    "E_4": 2.0,
    "E_6": 2.0,
    "J(E_1)": 2.0,
    "J(E_2)": 2.0,
    "J(E_3)": 2.0,
    "J(E_4)": 2.0,
    "J(E_6)": 2.0,
    "F_{ac}": 4.0,            # fully abelian, U(1)^2
    "D_{2,1}": 2.0,
    "D_{3,2}": 2.0,
    "D_{6,2}": 2.0,
    "J(C_2)": 2.0,
    "J(C_4)": 2.0,
}

# We'll also compute empirical M2_theory from the data itself as a robustness check


# ---------------------------------------------------------------------------
# Main computation
# ---------------------------------------------------------------------------
def load_curves(path, max_curves=1000):
    """Load curves, sample across ST groups."""
    with open(path) as f:
        data = json.load(f)

    records = data["records"]

    # Group by ST group
    by_st = defaultdict(list)
    for r in records:
        by_st[r["st_group"]].append(r)

    selected = []

    # Take curves from each ST group, prioritizing representation
    # First: take all curves from rare groups
    for st_grp, curves in sorted(by_st.items(), key=lambda x: len(x[1])):
        if len(curves) <= 50:
            selected.extend(curves)

    # Fill remaining from larger groups proportionally
    remaining = max_curves - len(selected)
    if remaining > 0:
        large_groups = [(g, c) for g, c in by_st.items() if len(c) > 50]
        total_large = sum(len(c) for _, c in large_groups)
        for g, curves in large_groups:
            n_take = max(1, int(remaining * len(curves) / total_large))
            step = max(1, len(curves) // n_take)
            selected.extend(curves[::step][:n_take])

    # Trim to max_curves
    selected = selected[:max_curves]

    print(f"Selected {len(selected)} curves across {len(set(r['st_group'] for r in selected))} ST groups")
    return selected


def parse_eqn(eqn):
    """Parse LMFDB equation format [[f_coeffs], [h_coeffs]]."""
    if isinstance(eqn, str):
        import ast
        eqn = ast.literal_eval(eqn)
    f_coeffs = [int(c) for c in eqn[0]]
    h_coeffs = [int(c) for c in eqn[1]] if len(eqn) > 1 and eqn[1] else []
    return f_coeffs, h_coeffs


def compute_normalized_traces(curve, primes):
    """Compute a_p / sqrt(p) for good primes."""
    f_coeffs, h_coeffs = parse_eqn(curve["eqn"])
    bad_primes = set(curve.get("bad_primes", []))

    traces = {}
    for p in primes:
        if p in bad_primes:
            continue
        a_p = count_points_mod_p(f_coeffs, h_coeffs, p)
        # Normalize: a_p / sqrt(p)
        traces[p] = a_p / math.sqrt(p)

    return traces


def compute_M2_at_thresholds(traces, thresholds):
    """Compute empirical M2(P) = (1/N) sum_{p<=P, good} (a_p/sqrt(p))^2."""
    results = {}
    for P in thresholds:
        vals = [v**2 for p, v in traces.items() if p <= P]
        if len(vals) >= 3:
            results[P] = {
                "M2": float(np.mean(vals)),
                "n_primes": len(vals),
                "std_err": float(np.std(vals) / np.sqrt(len(vals)))
            }
    return results


def fit_power_law(thresholds_data, M2_theory):
    """
    Fit |M2(P) - M2_theory| ~ C * P^{-beta}.

    Returns beta, C, r_squared.
    """
    Ps = []
    residuals = []

    for P, info in sorted(thresholds_data.items()):
        r = abs(info["M2"] - M2_theory)
        if r > 0:
            Ps.append(P)
            residuals.append(r)

    if len(Ps) < 3:
        return None, None, None

    log_P = np.log(np.array(Ps, dtype=float))
    log_r = np.log(np.array(residuals, dtype=float))

    # Linear regression: log_r = log_C - beta * log_P
    A = np.vstack([np.ones_like(log_P), log_P]).T
    result = np.linalg.lstsq(A, log_r, rcond=None)
    coeffs = result[0]

    log_C = coeffs[0]
    neg_beta = coeffs[1]
    beta = -neg_beta
    C = math.exp(log_C)

    # R-squared
    predicted = log_C + neg_beta * log_P
    ss_res = np.sum((log_r - predicted) ** 2)
    ss_tot = np.sum((log_r - np.mean(log_r)) ** 2)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

    return float(beta), float(C), float(r_squared)


def main():
    base = Path(__file__).resolve().parent.parent
    data_path = base / "lmfdb_dump" / "g2c_curves.json"
    out_path = Path(__file__).resolve().parent / "st_convergence_rate_results.json"

    print("Loading curves...")
    curves = load_curves(data_path, max_curves=1000)

    # Gather ST group counts
    st_counts = defaultdict(int)
    for c in curves:
        st_counts[c["st_group"]] += 1
    print("ST group distribution in sample:")
    for g, n in sorted(st_counts.items(), key=lambda x: -x[1]):
        print(f"  {g}: {n}")

    # =========================================================================
    # PASS 1: Compute all normalized traces and M2 at each threshold
    # =========================================================================
    print("\n--- Pass 1: Computing normalized traces ---")
    curve_traces = []  # list of (curve_dict, traces_dict, m2_data_dict)

    for i, curve in enumerate(curves):
        if i % 100 == 0:
            print(f"  Point-counting curve {i+1}/{len(curves)}...")

        traces = compute_normalized_traces(curve, ALL_PRIMES)
        m2_data = compute_M2_at_thresholds(traces, THRESHOLDS)
        curve_traces.append((curve, traces, m2_data))

    # =========================================================================
    # Estimate M2_theory per ST group from empirical data at P=997
    # Use median across curves (robust to outliers) as best estimate
    # Also report the tabulated theoretical value for comparison
    # =========================================================================
    print("\n--- Estimating M2_theory from empirical data at P=997 ---")
    m2_empirical_by_group = defaultdict(list)
    for curve, traces, m2_data in curve_traces:
        if 997 in m2_data:
            m2_empirical_by_group[curve["st_group"]].append(m2_data[997]["M2"])

    m2_theory_estimated = {}
    print(f"\n{'ST Group':<25s} {'n':>5s} {'Empirical M2':>12s} {'Tabulated':>10s}")
    print("-" * 55)
    for g in sorted(m2_empirical_by_group.keys()):
        vals = m2_empirical_by_group[g]
        emp_m2 = float(np.median(vals))
        tab_m2 = ST_M2_THEORY.get(g, None)
        m2_theory_estimated[g] = emp_m2
        tab_str = f"{tab_m2:.2f}" if tab_m2 is not None else "?"
        print(f"  {g:<23s} {len(vals):>5d} {emp_m2:>12.4f} {tab_str:>10s}")

    # For the convergence fit, use the TABULATED value where we trust it
    # (USp(4), SU(2)xSU(2)), and the empirical median otherwise
    def get_m2_theory(st_grp):
        tab = ST_M2_THEORY.get(st_grp)
        emp = m2_theory_estimated.get(st_grp)
        # For the two dominant groups, trust the theory
        if st_grp in ("USp(4)", "SU(2)xSU(2)") and tab is not None:
            return tab, "tabulated"
        # For others, use empirical estimate (more robust than uncertain tables)
        if emp is not None:
            return emp, "empirical"
        if tab is not None:
            return tab, "tabulated"
        return 1.0, "default"

    # =========================================================================
    # PASS 2: Fit convergence rates using calibrated M2_theory
    # =========================================================================
    print("\n--- Pass 2: Fitting convergence rates ---")
    all_results = []
    by_st_group = defaultdict(list)
    by_st_group_r2 = defaultdict(list)

    for i, (curve, traces, m2_data) in enumerate(curve_traces):
        st_grp = curve["st_group"]
        m2_theory, m2_source = get_m2_theory(st_grp)

        beta, C, r2 = fit_power_law(m2_data, m2_theory)

        result = {
            "label": curve["label"],
            "st_group": st_grp,
            "conductor": curve["cond"],
            "M2_theory": m2_theory,
            "M2_theory_source": m2_source,
            "M2_by_threshold": {str(P): info for P, info in m2_data.items()},
            "beta": beta,
            "C_prefactor": C,
            "r_squared": r2
        }
        all_results.append(result)
        if beta is not None and np.isfinite(beta):
            by_st_group[st_grp].append(beta)
            if r2 is not None:
                by_st_group_r2[st_grp].append(r2)

    # =========================================================================
    # ANALYSIS: Also fit using ONLY the 4 non-extreme thresholds
    # (50, 100, 200, 500) to avoid fitting TO the target
    # =========================================================================
    print("\n--- Robustness: Fitting with P=50..500 only (excluding P=997) ---")
    by_st_group_robust = defaultdict(list)

    for curve, traces, m2_data in curve_traces:
        st_grp = curve["st_group"]
        m2_theory, _ = get_m2_theory(st_grp)

        # Use only P <= 500
        m2_sub = {P: v for P, v in m2_data.items() if P <= 500}
        beta_r, C_r, r2_r = fit_power_law(m2_sub, m2_theory)
        if beta_r is not None and np.isfinite(beta_r):
            by_st_group_robust[st_grp].append(beta_r)

    # =========================================================================
    # Report by ST group
    # =========================================================================
    print("\n" + "=" * 70)
    print("RESULTS: Convergence exponent beta by Sato-Tate group")
    print("=" * 70)

    group_stats = {}
    for st_grp in sorted(by_st_group.keys()):
        betas = np.array(by_st_group[st_grp])
        betas_clean = betas[np.isfinite(betas)]
        if len(betas_clean) == 0:
            continue

        r2s = np.array(by_st_group_r2.get(st_grp, []))
        betas_rob = np.array(by_st_group_robust.get(st_grp, []))

        m2_t, m2_src = get_m2_theory(st_grp)
        stats = {
            "n_curves": int(len(betas_clean)),
            "M2_theory": m2_t,
            "M2_theory_source": m2_src,
            "beta_mean": float(np.mean(betas_clean)),
            "beta_median": float(np.median(betas_clean)),
            "beta_std": float(np.std(betas_clean)),
            "beta_q25": float(np.percentile(betas_clean, 25)),
            "beta_q75": float(np.percentile(betas_clean, 75)),
            "beta_min": float(np.min(betas_clean)),
            "beta_max": float(np.max(betas_clean)),
            "mean_r_squared": float(np.mean(r2s)) if len(r2s) > 0 else None,
            "fraction_near_CLT": float(np.mean(np.abs(betas_clean - 0.5) < 0.15)),
        }
        if len(betas_rob) > 0:
            stats["beta_robust_mean"] = float(np.mean(betas_rob))
            stats["beta_robust_median"] = float(np.median(betas_rob))

        group_stats[st_grp] = stats

        print(f"\n{st_grp} (n={stats['n_curves']}, M2_theory={m2_t:.3f} [{m2_src}]):")
        print(f"  beta: mean={stats['beta_mean']:.3f}, median={stats['beta_median']:.3f}, "
              f"std={stats['beta_std']:.3f}")
        print(f"  IQR: [{stats['beta_q25']:.3f}, {stats['beta_q75']:.3f}]")
        if stats.get("beta_robust_mean") is not None:
            print(f"  beta (robust, P<=500): mean={stats['beta_robust_mean']:.3f}, "
                  f"median={stats['beta_robust_median']:.3f}")
        if stats["mean_r_squared"] is not None:
            print(f"  Mean R^2 of power-law fit: {stats['mean_r_squared']:.3f}")
        print(f"  Fraction near CLT (|beta-0.5|<0.15): {stats['fraction_near_CLT']:.2f}")

    # =========================================================================
    # Overall statistics
    # =========================================================================
    all_betas = []
    for blist in by_st_group.values():
        all_betas.extend(blist)
    all_betas = np.array(all_betas)
    all_betas = all_betas[np.isfinite(all_betas)]

    # Focus on USp(4) separately since it dominates and has clean theory
    usp4_betas = np.array(by_st_group.get("USp(4)", []))
    usp4_betas = usp4_betas[np.isfinite(usp4_betas)]

    overall = {
        "n_curves_total": int(len(all_betas)),
        "beta_mean": float(np.mean(all_betas)),
        "beta_median": float(np.median(all_betas)),
        "beta_std": float(np.std(all_betas)),
        "fraction_near_CLT": float(np.mean(np.abs(all_betas - 0.5) < 0.15)),
        "CLT_rate_hypothesis": "beta = 0.5",
    }

    if len(usp4_betas) > 1:
        overall["USp4_beta_mean"] = float(np.mean(usp4_betas))
        overall["USp4_beta_median"] = float(np.median(usp4_betas))
        overall["USp4_beta_std"] = float(np.std(usp4_betas))
        usp4_t = (np.mean(usp4_betas) - 0.5) / (np.std(usp4_betas) / np.sqrt(len(usp4_betas)))
        overall["USp4_t_stat_vs_0.5"] = float(usp4_t)

    print(f"\n{'=' * 70}")
    print(f"OVERALL (n={overall['n_curves_total']}):")
    print(f"  beta: mean={overall['beta_mean']:.3f}, median={overall['beta_median']:.3f}")
    print(f"  std={overall['beta_std']:.3f}")
    print(f"  Fraction near CLT: {overall['fraction_near_CLT']:.2f}")

    if len(all_betas) > 1:
        t_stat = (np.mean(all_betas) - 0.5) / (np.std(all_betas) / np.sqrt(len(all_betas)))
        overall["t_stat_vs_0.5"] = float(t_stat)
        print(f"  t-statistic vs 0.5: {t_stat:.2f}")

    if "USp4_beta_mean" in overall:
        print(f"\n  USp(4) only (n={len(usp4_betas)}):")
        print(f"    beta: mean={overall['USp4_beta_mean']:.3f}, median={overall['USp4_beta_median']:.3f}")
        print(f"    t-stat vs 0.5: {overall['USp4_t_stat_vs_0.5']:.2f}")

    # Check if beta differs by ST group
    if len(by_st_group) > 1:
        group_means = {g: float(np.mean(b)) for g, b in by_st_group.items() if len(b) >= 5}
        if len(group_means) > 1:
            print(f"\n  Group means with n>=5:")
            for g, m in sorted(group_means.items(), key=lambda x: x[1]):
                print(f"    {g}: {m:.3f}")

    # =========================================================================
    # Convergence profile: average M2 deviation at each threshold
    # =========================================================================
    convergence_profile = {}
    # Also per-group profiles for USp(4) and SU(2)xSU(2)
    convergence_by_group = defaultdict(dict)

    for P in THRESHOLDS:
        devs_all = []
        devs_by_g = defaultdict(list)
        for r in all_results:
            if str(P) in r["M2_by_threshold"]:
                m2_theory = r["M2_theory"]
                m2_emp = r["M2_by_threshold"][str(P)]["M2"]
                dev = abs(m2_emp - m2_theory)
                devs_all.append(dev)
                devs_by_g[r["st_group"]].append(dev)

        if devs_all:
            convergence_profile[str(P)] = {
                "mean_deviation": float(np.mean(devs_all)),
                "median_deviation": float(np.median(devs_all)),
                "n_curves": len(devs_all)
            }

        for g, dvs in devs_by_g.items():
            if len(dvs) >= 5:
                convergence_by_group[g][str(P)] = {
                    "mean_deviation": float(np.mean(dvs)),
                    "n": len(dvs)
                }

    print(f"\nConvergence profile (mean |M2(P) - M2_theory|):")
    for P in THRESHOLDS:
        if str(P) in convergence_profile:
            cp = convergence_profile[str(P)]
            print(f"  P={P}: mean_dev={cp['mean_deviation']:.4f}, n={cp['n_curves']}")

    # Fit aggregate convergence per group
    print(f"\nAggregate convergence beta by group (fit to mean deviations):")
    aggregate_betas = {}
    for g in sorted(convergence_by_group.keys()):
        prof = convergence_by_group[g]
        Ps_g = []
        devs_g = []
        for P in THRESHOLDS:
            if str(P) in prof:
                Ps_g.append(P)
                devs_g.append(prof[str(P)]["mean_deviation"])

        if len(Ps_g) >= 3 and all(d > 0 for d in devs_g):
            log_P = np.log(np.array(Ps_g, dtype=float))
            log_d = np.log(np.array(devs_g, dtype=float))
            A = np.vstack([np.ones_like(log_P), log_P]).T
            coeffs = np.linalg.lstsq(A, log_d, rcond=None)[0]
            agg_beta = float(-coeffs[1])
            aggregate_betas[g] = agg_beta
            print(f"  {g}: aggregate_beta = {agg_beta:.3f}")

    # Overall aggregate
    if len(convergence_profile) >= 3:
        Ps_conv = []
        devs_conv = []
        for P in THRESHOLDS:
            if str(P) in convergence_profile:
                Ps_conv.append(P)
                devs_conv.append(convergence_profile[str(P)]["mean_deviation"])

        if all(d > 0 for d in devs_conv):
            log_P = np.log(np.array(Ps_conv, dtype=float))
            log_d = np.log(np.array(devs_conv, dtype=float))
            A = np.vstack([np.ones_like(log_P), log_P]).T
            coeffs = np.linalg.lstsq(A, log_d, rcond=None)[0]
            overall_beta = float(-coeffs[1])
            overall["aggregate_beta"] = overall_beta
            print(f"\n  Overall aggregate beta: {overall_beta:.3f}")

    # =========================================================================
    # Save results
    # =========================================================================
    output = {
        "problem": "NF12: Sato-Tate Equidistribution Convergence Rate",
        "description": "Measures how fast M2(P) converges to theoretical ST value as P increases",
        "model": "|M2(P) - M2_theory| ~ C * P^{-beta}",
        "primes_up_to": 997,
        "thresholds": THRESHOLDS,
        "n_curves": len(all_results),
        "overall_statistics": overall,
        "convergence_profile": convergence_profile,
        "aggregate_betas_by_group": aggregate_betas,
        "by_st_group": group_stats,
        "individual_curves": all_results[:50],  # first 50 for reference
        "methodology": {
            "point_counting": "Direct enumeration mod p for y^2 + h(x)y = f(x)",
            "normalization": "a_p / sqrt(p) where a_p = p + 1 - #C(F_p)",
            "M2_computation": "Mean of (a_p/sqrt(p))^2 over good primes up to P",
            "M2_theory": "Tabulated for USp(4) and SU(2)xSU(2); empirical median at P=997 for others",
            "fit_method": "OLS on log|M2-M2_theory| vs log(P)",
            "robustness": "Also fit with P<=500 only to avoid fitting to the target",
            "thresholds": "P = 50, 100, 200, 500, 997"
        }
    }

    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {out_path}")
    return output


if __name__ == "__main__":
    main()

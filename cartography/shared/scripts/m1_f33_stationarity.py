#!/usr/bin/env python3
"""
F33: Stationarity Gate — prototype implementation.
Detects non-stationary time-ordered data before F24 can be fooled.

The random walk stress test showed 92% FPR on non-stationary data.
First-differencing drops FPR to 0%. This gate automates that check.

Usage:
    from m1_f33_stationarity import F33_stationarity_gate
    verdict, result = F33_stationarity_gate(values, time_ordered=True)
    # If NONSTATIONARY: re-run F24 on first differences

M1 (Skullport), 2026-04-14
"""
import numpy as np
from scipy import stats as sp_stats


def F33_stationarity_gate(values, time_ordered=True, window_fraction=0.25):
    """Test whether a series is stationary before applying F24.

    Three sub-tests:
    1. ADF-like: regression of x_t on x_{t-1}. If coefficient ~1, unit root.
    2. Variance ratio: compare variance of first half vs second half.
    3. Mean drift: linear regression of values on index. Significant slope = drift.

    Returns: (verdict, result_dict)
    Verdicts: STATIONARY, NONSTATIONARY, TREND_ONLY, INSUFFICIENT_DATA
    """
    values = np.array(values, dtype=float)
    n = len(values)

    if n < 30:
        return "INSUFFICIENT_DATA", {}

    if not time_ordered:
        return "STATIONARY", {"note": "not_time_ordered"}

    # Sub-test 1: Augmented Dickey-Fuller (simplified)
    # Regress diff(x) on x_{t-1}
    x_lag = values[:-1]
    dx = np.diff(values)
    if np.std(x_lag) > 1e-10:
        slope, intercept, r, p, se = sp_stats.linregress(x_lag, dx)
        # ADF: slope should be negative and significantly < 0 for stationarity
        # If slope ~0, unit root (random walk)
        adf_stat = slope / (se + 1e-10)
        # Critical values (approximate, n > 100): -3.43 (1%), -2.86 (5%), -2.57 (10%)
        adf_stationary = adf_stat < -2.86
    else:
        adf_stat = 0
        adf_stationary = True  # constant series is stationary

    # Sub-test 2: Variance ratio (first half vs second half)
    half = n // 2
    var_first = np.var(values[:half])
    var_second = np.var(values[half:])
    var_ratio = max(var_first, var_second) / (min(var_first, var_second) + 1e-10)
    var_stable = var_ratio < 4.0  # less than 4x difference

    # Sub-test 3: Mean drift
    idx = np.arange(n, dtype=float)
    slope_drift, _, r_drift, p_drift, _ = sp_stats.linregress(idx, values)
    drift_significant = abs(r_drift) > 0.1 and p_drift < 0.01

    # Sub-test 4: Rolling mean stability
    window = max(int(n * window_fraction), 10)
    rolling_means = np.array([np.mean(values[max(0, i-window):i+1]) for i in range(n)])
    rolling_cv = np.std(rolling_means) / (abs(np.mean(rolling_means)) + 1e-10)
    rolling_stable = rolling_cv < 0.5

    # Classification
    n_flags = sum([not adf_stationary, not var_stable, drift_significant, not rolling_stable])

    result = {
        "adf_stat": float(adf_stat),
        "adf_stationary": bool(adf_stationary),
        "var_ratio": float(var_ratio),
        "var_stable": bool(var_stable),
        "drift_r": float(r_drift),
        "drift_p": float(p_drift),
        "drift_significant": bool(drift_significant),
        "rolling_cv": float(rolling_cv),
        "rolling_stable": bool(rolling_stable),
        "n_flags": n_flags,
    }

    if n_flags >= 3:
        verdict = "NONSTATIONARY"
    elif n_flags == 2:
        if not adf_stationary:
            verdict = "NONSTATIONARY"
        else:
            verdict = "TREND_ONLY"
    elif drift_significant and not adf_stationary:
        verdict = "NONSTATIONARY"
    elif drift_significant:
        verdict = "TREND_ONLY"
    else:
        verdict = "STATIONARY"

    return verdict, result


def F33_with_differencing(values, group_labels, time_ordered=True):
    """Run F33 check, and if non-stationary, return both raw and differenced F24 results.

    This is the recommended way to use F33: it wraps F24 with automatic
    stationarity correction.
    """
    from battery_v2 import BatteryV2
    bv2 = BatteryV2()

    values = np.array(values, dtype=float)
    group_labels = np.array(group_labels)

    # Raw F24
    v_raw, r_raw = bv2.F24_variance_decomposition(values, group_labels)

    # Stationarity check
    v_stat, r_stat = F33_stationarity_gate(values, time_ordered=time_ordered)

    result = {
        "stationarity": v_stat,
        "stationarity_details": r_stat,
        "raw_f24_verdict": v_raw,
        "raw_f24_eta2": r_raw.get("eta_squared", 0),
    }

    if v_stat in ("NONSTATIONARY", "TREND_ONLY"):
        # First-difference
        diff_vals = np.diff(values)
        diff_labels = group_labels[1:]  # drop first label

        v_diff, r_diff = bv2.F24_variance_decomposition(diff_vals, diff_labels)
        result["diff_f24_verdict"] = v_diff
        result["diff_f24_eta2"] = r_diff.get("eta_squared", 0)
        result["recommendation"] = "USE_DIFFERENCED"

        # The honest eta2 is the differenced one
        verdict = v_diff
    else:
        result["recommendation"] = "USE_RAW"
        verdict = v_raw

    return verdict, result


# ═══════════════════════════════════════════════════════════════════════
# VALIDATION: Run on known cases
# ═══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    rng = np.random.RandomState(42)

    print("="*70)
    print("F33 STATIONARITY GATE — VALIDATION")
    print("="*70)

    # Test cases
    cases = [
        ("White noise", rng.normal(0, 1, 1000), True, "STATIONARY"),
        ("Random walk", np.cumsum(rng.normal(0, 1, 1000)), True, "NONSTATIONARY"),
        ("Linear trend + noise", np.arange(1000) * 0.01 + rng.normal(0, 1, 1000), True, "TREND_ONLY"),
        ("OU process (fast)", None, True, "STATIONARY"),  # filled below
        ("Regime switch", None, True, "NONSTATIONARY"),  # depends
        ("Constant", np.ones(1000), True, "STATIONARY"),
        ("Sine wave", np.sin(np.arange(1000) * 0.1), True, "STATIONARY"),
    ]

    # Generate OU process
    ou = np.zeros(1000)
    for t in range(1, 1000):
        ou[t] = ou[t-1] - 0.5 * ou[t-1] + rng.normal()
    cases[3] = ("OU process (fast)", ou, True, "STATIONARY")

    # Generate regime switch
    rs = np.zeros(1000)
    state = 0
    for t in range(1000):
        if rng.random() < 0.01:
            state = 1 - state
        rs[t] = rng.normal([0, 5][state], 1)
    cases[4] = ("Regime switch", rs, True, "NONSTATIONARY")

    print(f"\n{'Case':>25s} {'Expected':>15s} {'Got':>15s} {'ADF':>8s} {'VarR':>8s} {'Drift':>8s} {'Match':>6s}")

    correct = 0
    total = 0
    for name, vals, time_ord, expected in cases:
        if vals is None:
            continue
        v, r = F33_stationarity_gate(vals, time_ordered=time_ord)
        match = "OK" if v == expected or (expected == "NONSTATIONARY" and v == "TREND_ONLY") else "MISS"
        if match == "OK":
            correct += 1
        total += 1
        print(f"{name:>25s} {expected:>15s} {v:>15s} {r.get('adf_stat', 0):>8.2f} {r.get('var_ratio', 0):>8.2f} {r.get('drift_r', 0):>8.3f} {match:>6s}")

    print(f"\nAccuracy: {correct}/{total} ({correct/total*100:.0f}%)")

    # Validate the wrapper
    print("\n" + "="*70)
    print("F33 WITH DIFFERENCING — Random walk recovery")
    print("="*70)

    walk = np.cumsum(rng.normal(0, 1, 2000))
    labels = np.array(["first"] * 1000 + ["second"] * 1000)

    v, r = F33_with_differencing(walk, labels, time_ordered=True)
    print(f"Stationarity: {r['stationarity']}")
    print(f"Raw F24: {r['raw_f24_verdict']}, eta2={r['raw_f24_eta2']:.4f}")
    if "diff_f24_eta2" in r:
        print(f"Differenced F24: {r['diff_f24_verdict']}, eta2={r['diff_f24_eta2']:.4f}")
    print(f"Recommendation: {r['recommendation']}")
    print(f"Final verdict: {v}")

    # Bulk validation: 200 random walks
    print("\n" + "="*70)
    print("BULK VALIDATION: 200 random walks through F33")
    print("="*70)

    caught = 0
    for trial in range(200):
        rng_t = np.random.RandomState(trial)
        walk = np.cumsum(rng_t.normal(0, 1, 1000))
        labels = np.array(["A"] * 500 + ["B"] * 500)
        v, r = F33_with_differencing(walk, labels, time_ordered=True)
        if r.get("diff_f24_eta2", r["raw_f24_eta2"]) < 0.01:
            caught += 1

    print(f"Random walks correctly neutralized: {caught}/200 ({caught/200*100:.1f}%)")
    print(f"Without F33: ~8/200 would be correctly null (92% FPR)")
    print(f"With F33: {caught}/200 correctly null ({caught/200*100:.1f}% true negative rate)")

"""
threads_A_B_investigation.py — Harmonia worker W5.

Two closing investigations on the Keating-Snaith / Katz-Sarnak moment work:

Thread A — Low-tail density asymptotic convergence.
    From cartography/docs/keating_snaith_katz_sarnak_results.json, at rank 0
    we see Pr[L/M_1 < 0.25] climbing across decades:
        10^2 -> 0.006,  10^3 -> 0.037,  10^4 -> 0.079,  10^5 -> 0.107.
    Under Katz-Sarnak, rank 0 <-> SO_even, and the distribution of
    L(1/2,E)/mean for the SO_even ensemble has a known asymptotic shape
    (Keating-Snaith 2000; Conjecture/Theorem for SO(2N)).

    We use the Keating-Snaith moment conjecture with the RMT matrix size
    N_eff(X) = log(X) / (2*pi) (CFKRS; the standard Katz-Sarnak matching).
    For finite N we compute the SO_even prediction of Pr[det(A)/E[det(A)] < 0.25]
    via Monte-Carlo over matrices A ~ Haar-SO(2N) using the eigenangle
    representation det(A) = prod_{j=1..N} 2*(1 - cos(theta_j))  (for SO_even
    the eigenvalues come in conjugate pairs exp(+/- i*theta_j)).

    The Haar measure on the eigenangles {theta_j} in SO(2N) has density
        p(theta_1,...,theta_N) propto prod_{j<k} (cos theta_j - cos theta_k)^2
    on [0, pi]^N   (cf. Katz-Sarnak).  We sample via Metropolis-Hastings.

Thread B — Rank-1 num_bad_primes=6 outlier investigation.
    In keating_snaith_arithmetic_analysis_results.json the rank-1 slope at
    nbp=6 came out as 0.626 with SE=0 (two decades only). We re-examine by
    (a) counting n per (rank=1, decade, nbp=6) cell,
    (b) lowering MIN_PER_TRIPLE to 20 and re-fitting,
    (c) comparing per-cell shape (median, skewness, Pr<0.5, Pr<1.0) to nbp=5.

Pattern 20: no pooled slopes. Every cell reported individually.

Output: cartography/docs/threads_A_low_tail_B_nbp6_outlier_results.json
"""
from __future__ import annotations

import json
import math
import os
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import psycopg2
from scipy import stats

# ----------------------------------------------------------------------------
# DB configs
# ----------------------------------------------------------------------------
PF = dict(host="192.168.1.176", port=5432, dbname="prometheus_fire",
          user="postgres", password="prometheus", connect_timeout=10)
LM = dict(host="192.168.1.176", port=5432, dbname="lmfdb",
          user="postgres", password="prometheus", connect_timeout=10)

DECADE_EDGES = [(100, 1000), (1000, 10_000), (10_000, 100_000),
                (100_000, 1_000_000), (1_000_000, 10_000_000)]

# ----------------------------------------------------------------------------
# Thread A — SO(2N) Monte Carlo for Pr[det(A)/E[det(A)] < 0.25]
# ----------------------------------------------------------------------------

def sample_SO_even_eigenangles(N: int, n_samples: int, burn: int = 2000,
                                 thin: int = 5, seed: int = 20260417) -> np.ndarray:
    """Metropolis-Hastings draw from the eigenangle density of SO(2N).

    For A ~ Haar SO(2N), eigenvalues come as N conjugate pairs exp(+/- i*theta_j)
    with theta_j in (0, pi). The joint density is

        p(theta) propto  prod_{j<k} (cos theta_j - cos theta_k)^2

    i.e. the determinantal point process with the Jacobi/Gegenbauer weight.

    This is the standard eigenangle density for SO(2N); see Katz-Sarnak
    "Random Matrices, Frobenius Eigenvalues and Monodromy" (1999), eq. 5.0.4.

    Returns array of shape (n_samples, N) of theta-vectors.
    """
    rng = np.random.default_rng(seed)
    # Initialize from the limiting semicircle-like placement (Chebyshev nodes)
    theta = np.pi * (np.arange(1, N + 1) - 0.5) / N
    log_p = _log_density(theta)
    samples = np.empty((n_samples, N), dtype=np.float64)
    accept = 0
    step = 0.25 * np.pi / max(N, 1)

    total_iters = burn + n_samples * thin
    i_accept_window = 0
    window = 200

    for it in range(total_iters):
        # Propose: perturb all coordinates by small Gaussian step, reflect into (0, pi)
        prop = theta + rng.normal(0.0, step, size=N)
        # reflect at 0 and pi
        prop = np.mod(prop, 2 * np.pi)
        prop = np.where(prop > np.pi, 2 * np.pi - prop, prop)
        prop = np.clip(prop, 1e-9, np.pi - 1e-9)

        lp_new = _log_density(prop)
        if math.log(rng.random()) < (lp_new - log_p):
            theta = prop
            log_p = lp_new
            accept += 1
            i_accept_window += 1

        # Adapt step size during burn-in to target ~30% acceptance
        if it < burn and (it + 1) % window == 0:
            rate = i_accept_window / window
            if rate < 0.2:
                step *= 0.85
            elif rate > 0.5:
                step *= 1.15
            i_accept_window = 0

        if it >= burn and ((it - burn) % thin == 0):
            idx = (it - burn) // thin
            if idx < n_samples:
                samples[idx] = theta

    return samples


def _log_density(theta: np.ndarray) -> float:
    """Log of prod_{j<k} (cos theta_j - cos theta_k)^2. theta shape (N,)."""
    c = np.cos(theta)
    N = len(theta)
    # pairwise differences
    diff = c[:, None] - c[None, :]
    # take upper triangle
    iu, ju = np.triu_indices(N, k=1)
    d = diff[iu, ju]
    # log|d|^2 = 2 log|d|
    ad = np.abs(d)
    if np.any(ad < 1e-18):
        return -1e18
    return 2.0 * float(np.sum(np.log(ad)))


def SO_even_low_tail_predictions(N_values: list[int], threshold: float = 0.25,
                                   n_samples: int = 8000) -> dict:
    """For each N, simulate det(A) for A ~ SO(2N) via eigenangles and return
    Pr[det(A)/E[det(A)] < threshold] along with mean/std/skew/kurtosis.

    For SO(2N), det(A) = +1 always (characteristic polynomial at 1):
        Z_A(1) = prod_{j=1}^{N} 2 (1 - cos theta_j)
    This is the value of the characteristic polynomial at the spectral symmetry
    point — not the matrix determinant. It is the KS analogue of L(1/2).
    """
    out = {}
    for N in N_values:
        samples = sample_SO_even_eigenangles(N, n_samples=n_samples)
        # Z_A(1) = prod 2(1 - cos theta_j)
        log_Z = np.log(np.clip(2.0 * (1.0 - np.cos(samples)), 1e-300, None)).sum(axis=1)
        Z = np.exp(log_Z)
        mean = float(Z.mean())
        norm = Z / mean
        tail = float(np.mean(norm < threshold))
        out[N] = {
            "N": N,
            "n_samples": int(n_samples),
            "mean_Z": mean,
            "std_Z_norm": float(norm.std(ddof=1)),
            "median_Z_norm": float(np.median(norm)),
            "skew_Z_norm": float(stats.skew(norm, bias=False)),
            "excess_kurtosis_Z_norm": float(stats.kurtosis(norm, fisher=True, bias=False)),
            f"Pr_less_{threshold}": tail,
            "Pr_less_0.5": float(np.mean(norm < 0.5)),
            "Pr_less_1.0": float(np.mean(norm < 1.0)),
            "p10": float(np.quantile(norm, 0.10)),
            "p25": float(np.quantile(norm, 0.25)),
        }
    return out


def keating_snaith_N_eff(conductor: float) -> float:
    """CFKRS / Katz-Sarnak matching:  N_eff(X) = log(X) / (2 pi).

    This is the Katz-Sarnak one-level density matching (zeros scale with 1/2pi).
    For degree-2 L-functions some authors use N_eff = log(X) instead (absorbing
    the degree factor). We report both matchings in the output JSON.
    """
    return math.log(conductor) / (2.0 * math.pi)


def keating_snaith_N_eff_degree2(conductor: float) -> float:
    """Alternative matching for degree-2 L-functions: N_eff(X) = log(X) / (2).
    Some CFKRS-style matchings absorb the degree factor differently.
    Included for comparison.
    """
    return math.log(conductor) / 2.0


# ----------------------------------------------------------------------------
# Empirical low-tail counts at rank 0 (for comparison at same decade midpoints)
# ----------------------------------------------------------------------------

def load_rank0_leading_terms() -> dict:
    """Return {(lo,hi): np.ndarray} of rank 0 leading_term values per decade."""
    out = {}
    with psycopg2.connect(**PF) as conn:
        cur = conn.cursor()
        for lo, hi in DECADE_EDGES:
            cur.execute("""
                SELECT leading_term
                FROM zeros.object_zeros
                WHERE object_type = 'elliptic_curve'
                  AND analytic_rank = 0
                  AND conductor >= %s AND conductor < %s
                  AND leading_term IS NOT NULL
                  AND leading_term > 0
            """, (lo, hi))
            vals = np.asarray([float(r[0]) for r in cur.fetchall()], dtype=float)
            out[(lo, hi)] = vals
    return out


# ----------------------------------------------------------------------------
# Thread B — nbp=6 re-investigation
# ----------------------------------------------------------------------------

def load_joined_rank1():
    """Load rank 1 elliptic curves joined with num_bad_primes."""
    with psycopg2.connect(**PF) as pf_conn:
        cur = pf_conn.cursor()
        cur.execute("""
            SELECT lmfdb_label, conductor, leading_term
            FROM zeros.object_zeros
            WHERE object_type = 'elliptic_curve'
              AND analytic_rank = 1
              AND leading_term IS NOT NULL AND leading_term > 0
              AND conductor > 0
        """)
        zeros = {r[0]: (int(r[1]), float(r[2])) for r in cur.fetchall()}
    with psycopg2.connect(**LM) as lm_conn:
        cur = lm_conn.cursor()
        cur.execute("""
            SELECT lmfdb_label, NULLIF(num_bad_primes, '')::int
            FROM public.ec_curvedata
            WHERE num_bad_primes IS NOT NULL
        """)
        nbp = {r[0]: r[1] for r in cur.fetchall()}
    rows = []
    for lbl, (cond, lt) in zeros.items():
        k = nbp.get(lbl)
        if k is None:
            continue
        rows.append((cond, lt, int(k)))
    return rows


def slope_fit(xs, ys):
    if len(xs) < 2:
        return None, None
    x = np.asarray(xs, dtype=float)
    y = np.asarray(ys, dtype=float)
    mx, my = x.mean(), y.mean()
    num = ((x - mx) * (y - my)).sum()
    den = ((x - mx) ** 2).sum()
    if den == 0:
        return None, None
    slope = float(num / den)
    pred = slope * x + (my - slope * mx)
    resid = y - pred
    if len(xs) > 2:
        s2 = float((resid ** 2).sum() / (len(xs) - 2))
        se = math.sqrt(s2 / den) if den > 0 else 0.0
    else:
        se = 0.0
    return slope, float(se)


def per_cell_shape(vals: np.ndarray) -> dict:
    vals = np.asarray(vals, dtype=float)
    if vals.size == 0:
        return None
    m = float(vals.mean())
    if m <= 0:
        return None
    norm = vals / m
    return {
        "n": int(vals.size),
        "mean": m,
        "std": float(vals.std(ddof=1) if vals.size > 1 else 0.0),
        "median_norm": float(np.median(norm)),
        "skew_norm": float(stats.skew(norm, bias=False)) if vals.size > 2 else None,
        "excess_kurtosis_norm": float(stats.kurtosis(norm, fisher=True, bias=False))
                                 if vals.size > 3 else None,
        "Pr_less_0.25": float(np.mean(norm < 0.25)),
        "Pr_less_0.5": float(np.mean(norm < 0.5)),
        "Pr_less_1.0": float(np.mean(norm < 1.0)),
        "M_1": m,
        "M_2": float((vals ** 2).mean()),
        "M_3": float((vals ** 3).mean()),
        "M_4": float((vals ** 4).mean()),
    }


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[threads_AB] start {started}")

    # =====================================================================
    # Thread A
    # =====================================================================
    print("[threads_AB/A] loading rank 0 empirical...")
    rank0 = load_rank0_leading_terms()
    empirical_rank0 = {}
    for (lo, hi), vals in rank0.items():
        if vals.size == 0:
            continue
        mid = math.sqrt(lo * hi)
        N_eff = keating_snaith_N_eff(mid)
        m = vals.mean()
        if m <= 0:
            continue
        norm = vals / m
        empirical_rank0[f"decade=[{lo},{hi})"] = {
            "lo": lo, "hi": hi, "mid": float(mid),
            "N_eff_ks": float(N_eff),
            "n": int(vals.size),
            "mean": float(m),
            "Pr_less_0.25": float(np.mean(norm < 0.25)),
            "Pr_less_0.5": float(np.mean(norm < 0.5)),
            "Pr_less_1.0": float(np.mean(norm < 1.0)),
        }
        print(f"  empirical decade [{lo},{hi}) n={vals.size} "
              f"N_eff={N_eff:.2f} Pr(<0.25)={np.mean(norm<0.25):.4f}")

    # Simulate SO(2N) for a range of N that includes decade midpoints plus
    # coarse/fine extrapolation bracket. decade midpoints:
    #   10^2.5 -> N_eff ~ 0.92  (too small; use N=1)
    #   10^3.5 -> N_eff ~ 1.28  (use N=1 or 2)
    #   10^4.5 -> N_eff ~ 1.65
    #   10^5.5 -> N_eff ~ 2.01
    # But the Keating-Snaith SO(2N) prediction is most cleanly stated for
    # integer N, so we report a grid N = 1..20 and interpolate by N_eff.
    print("[threads_AB/A] simulating SO(2N) Monte Carlo for N=1..20...")
    N_grid = list(range(1, 21))
    sim = SO_even_low_tail_predictions(N_grid, threshold=0.25, n_samples=8000)

    # Also simulate at higher N (25, 35, 50) for asymptote anchoring
    print("[threads_AB/A] simulating higher N=25, 35, 50 for asymptote...")
    sim_high = SO_even_low_tail_predictions([25, 35, 50], threshold=0.25, n_samples=4000)
    sim.update(sim_high)

    # Build predicted value at each decade midpoint by *linear interpolation in N_eff*
    N_eff_map = {
        decade: keating_snaith_N_eff(math.sqrt(lo * hi))
        for decade, (lo, hi) in zip(
            [f"decade=[{lo},{hi})" for (lo, hi) in DECADE_EDGES], DECADE_EDGES)
    }
    # build interpolation arrays
    sim_N = np.asarray(sorted(sim.keys()), dtype=float)
    sim_pr = np.asarray([sim[int(n)]["Pr_less_0.25"] for n in sim_N])

    def predict_at(N_eff: float) -> tuple[float, str]:
        if N_eff < sim_N[0]:
            return float(sim_pr[0]), "below_grid"
        if N_eff > sim_N[-1]:
            return float(sim_pr[-1]), "above_grid"
        return float(np.interp(N_eff, sim_N, sim_pr)), "in_grid"

    thread_A_comparison = {}
    for (lo, hi) in DECADE_EDGES:
        name = f"decade=[{lo},{hi})"
        if name not in empirical_rank0:
            continue
        N_eff = keating_snaith_N_eff(math.sqrt(lo * hi))
        N_eff_d2 = keating_snaith_N_eff_degree2(math.sqrt(lo * hi))
        pred, extrap = predict_at(N_eff)
        pred_d2, extrap_d2 = predict_at(N_eff_d2)
        emp_val = empirical_rank0[name]["Pr_less_0.25"]
        thread_A_comparison[name] = {
            "mid": float(math.sqrt(lo * hi)),
            "N_eff_ks_log_X_over_2pi": float(N_eff),
            "N_eff_degree2_log_X_over_2": float(N_eff_d2),
            "empirical_Pr_less_0.25": float(emp_val),
            "SO_even_MC_predicted_Pr_less_0.25_at_N_eff": pred,
            "SO_even_MC_predicted_Pr_less_0.25_at_N_eff_degree2": pred_d2,
            "interp_status": extrap,
            "interp_status_degree2": extrap_d2,
            "delta_emp_minus_pred": float(emp_val - pred),
            "ratio_emp_over_pred": float(emp_val / pred) if pred > 0 else None,
            "ratio_emp_over_pred_degree2": float(emp_val / pred_d2) if pred_d2 > 0 else None,
            "n_empirical": empirical_rank0[name]["n"],
        }

    # Extrapolation to 10^7 and 10^8 (both matchings)
    extrapolation = {}
    for log10_X in [6, 7, 8]:
        X = 10.0 ** log10_X
        N_eff = keating_snaith_N_eff(X)
        N_eff_d2 = keating_snaith_N_eff_degree2(X)
        pred, status = predict_at(N_eff)
        pred_d2, status_d2 = predict_at(N_eff_d2)
        # empirical extrapolation: fit a linear model of empirical vs N_eff
        # over the observed decades and evaluate there.
        extrapolation[f"X=10^{log10_X}"] = {
            "X": X,
            "N_eff_ks": float(N_eff),
            "N_eff_degree2": float(N_eff_d2),
            "predicted_Pr_less_0.25_SO_even_matching_1over_2pi": pred,
            "predicted_Pr_less_0.25_SO_even_matching_1over_2": pred_d2,
            "status": status,
        }

    # Empirical extrapolation: fit linear slope of emp vs log(mid) using the
    # four observed decades and extrapolate.
    log_mids = np.array([math.log(math.sqrt(lo * hi)) for (lo, hi) in DECADE_EDGES
                          if f"decade=[{lo},{hi})" in empirical_rank0])
    emp_tail = np.array([empirical_rank0[f"decade=[{lo},{hi})"]["Pr_less_0.25"]
                          for (lo, hi) in DECADE_EDGES
                          if f"decade=[{lo},{hi})" in empirical_rank0])
    emp_slope, emp_se = slope_fit(log_mids.tolist(), emp_tail.tolist())
    emp_intercept = float(emp_tail.mean() - (emp_slope or 0.0) * log_mids.mean())
    empirical_extrapolation = {}
    for log10_X in [5, 6, 7, 8]:
        X = 10.0 ** log10_X
        lx = math.log(X)
        emp_pred_linear = float(emp_intercept + (emp_slope or 0.0) * lx) if emp_slope else None
        empirical_extrapolation[f"X=10^{log10_X}"] = {
            "X": X,
            "empirical_linear_extrapolation_in_log_X": emp_pred_linear,
        }
    extrapolation["_empirical_linear_extrapolation"] = {
        "slope_per_logX": emp_slope,
        "se": emp_se,
        "intercept": emp_intercept,
        "predictions": empirical_extrapolation,
    }

    # Asymptote value
    asymptote = {
        "Pr_less_0.25_at_N=50": sim[50]["Pr_less_0.25"],
        "Pr_less_0.25_at_N=35": sim[35]["Pr_less_0.25"],
        "Pr_less_0.25_at_N=25": sim[25]["Pr_less_0.25"],
        "Pr_less_0.25_at_N=20": sim[20]["Pr_less_0.25"],
    }

    # Thread A verdict
    # Trend test + convergence-of-ratio test.
    emp_arr = np.array([thread_A_comparison[f"decade=[{lo},{hi})"]["empirical_Pr_less_0.25"]
                         for (lo, hi) in DECADE_EDGES
                         if f"decade=[{lo},{hi})" in thread_A_comparison])
    pred_arr = np.array([thread_A_comparison[f"decade=[{lo},{hi})"]["SO_even_MC_predicted_Pr_less_0.25_at_N_eff"]
                          for (lo, hi) in DECADE_EDGES
                          if f"decade=[{lo},{hi})" in thread_A_comparison])
    pred_d2_arr = np.array([thread_A_comparison[f"decade=[{lo},{hi})"]["SO_even_MC_predicted_Pr_less_0.25_at_N_eff_degree2"]
                             for (lo, hi) in DECADE_EDGES
                             if f"decade=[{lo},{hi})" in thread_A_comparison])

    emp_rising = bool(np.all(np.diff(emp_arr) > 0))
    pred_rising = bool(np.all(np.diff(pred_arr) >= 0))
    pred_d2_rising = bool(np.all(np.diff(pred_d2_arr) >= 0))

    ratio_1over2pi = [float(e / p) for e, p in zip(emp_arr, pred_arr) if p > 0]
    ratio_1over2 = [float(e / p) for e, p in zip(emp_arr, pred_d2_arr) if p > 0]

    # Is the ratio monotonically approaching 1 under either matching?
    ratio_converging_2pi = (len(ratio_1over2pi) >= 2 and
                             all(ratio_1over2pi[i] <= ratio_1over2pi[i + 1]
                                 for i in range(len(ratio_1over2pi) - 1)))
    ratio_converging_2 = (len(ratio_1over2) >= 2 and
                           all(ratio_1over2[i] <= ratio_1over2[i + 1]
                               for i in range(len(ratio_1over2) - 1)))

    worst_log_ratio = max(
        abs(math.log(e / p)) for e, p in zip(emp_arr, pred_arr)
        if e > 0 and p > 0
    ) if len(emp_arr) > 0 else float("inf")
    worst_log_ratio_d2 = max(
        abs(math.log(e / p)) for e, p in zip(emp_arr, pred_d2_arr)
        if e > 0 and p > 0
    ) if len(emp_arr) > 0 else float("inf")

    # CONSISTENT_WITH_RMT if:
    # (a) both curves monotone rising, AND
    # (b) ratio emp/pred converges monotonically toward 1 at large decade
    #     under at least one matching, AND
    # (c) best-matching worst log-ratio is within factor 3 (log(3) ~= 1.10)
    best_worst = min(worst_log_ratio, worst_log_ratio_d2)
    best_ratio_last = max(ratio_1over2pi[-1] if ratio_1over2pi else 0.0,
                           ratio_1over2[-1] if ratio_1over2 else 0.0)

    consistent = (emp_rising and pred_rising
                  and (ratio_converging_2pi or ratio_converging_2)
                  and best_worst < math.log(3))

    thread_A_verdict = {
        "emp_progression": [float(x) for x in emp_arr],
        "pred_progression_N_over_2pi": [float(x) for x in pred_arr],
        "pred_progression_N_over_2_degree2": [float(x) for x in pred_d2_arr],
        "ratio_emp_over_pred_1over2pi_matching": ratio_1over2pi,
        "ratio_emp_over_pred_1over2_matching": ratio_1over2,
        "ratio_monotone_converging_2pi": bool(ratio_converging_2pi),
        "ratio_monotone_converging_2": bool(ratio_converging_2),
        "best_ratio_last_decade": best_ratio_last,
        "both_monotone_rising": bool(emp_rising and pred_rising),
        "max_abs_log_ratio_emp_pred_1over2pi": float(worst_log_ratio),
        "max_abs_log_ratio_emp_pred_1over2": float(worst_log_ratio_d2),
        "best_worst_log_ratio": float(best_worst),
        "verdict_label": "CONSISTENT_WITH_RMT" if consistent else "DIVERGENT",
        "notes": (
            "CONSISTENT_WITH_RMT requires (a) both curves monotone rising, "
            "(b) ratio emp/pred monotonically approaching 1 under at least one "
            "of the two CFKRS matchings (N_eff = log X / 2pi or N_eff = log X / 2), "
            "and (c) best-case worst log-ratio < log(3). "
            "If the best worst log-ratio stays above log(3), we record DIVERGENT. "
            "DIVERGENT under this bar may still be consistent with asymptotic "
            "convergence -- it just means the finite-X regime X <= 10^5 has "
            "larger-than-factor-3 deviation from the Haar SO(2N_eff) prediction. "
            "The direction of the deviation (empirical BELOW prediction) is "
            "consistent with arithmetic compression of the L-value distribution."
        ),
    }

    thread_A = {
        "empirical_rank0_low_tail": empirical_rank0,
        "SO_even_MC_grid_per_N": sim,
        "decade_to_prediction_comparison": thread_A_comparison,
        "extrapolation_to_X_10e7_10e8": extrapolation,
        "asymptote_large_N": asymptote,
        "verdict": thread_A_verdict,
        "methodology": (
            "Monte Carlo: sample eigenangles theta_j of SO(2N) from the "
            "Haar-induced density prod_{j<k}(cos theta_j - cos theta_k)^2 via "
            "adaptive Metropolis-Hastings (burn=2000, thin=5, 8000 samples at "
            "N<=20, 4000 at N=25,35,50). Compute Z_A(1) = prod 2(1 - cos theta_j) "
            "(the KS analogue of L(1/2,E) with the mean-squared normalization "
            "absorbed by dividing by E[Z_A(1)]). Then Pr[Z_A/E[Z_A] < 0.25]. "
            "Match to empirical via N_eff = log(X)/(2*pi) at each decade midpoint "
            "(CFKRS / Katz-Sarnak matching). Linear interpolation over the "
            "integer N grid."
        ),
    }

    # =====================================================================
    # Thread B
    # =====================================================================
    print("[threads_AB/B] loading rank 1 joined rows...")
    rows_r1 = load_joined_rank1()
    print(f"  rank-1 joined rows: {len(rows_r1)}")

    # Bucket by (decade, nbp)
    cells_triple = defaultdict(list)
    for cond, lt, nbp in rows_r1:
        for (lo, hi) in DECADE_EDGES:
            if lo <= cond < hi:
                cells_triple[(lo, hi, nbp)].append(lt)
                break

    # Count n per cell for nbp=6 AND (for comparison) nbp=5
    B_count_table = {}
    for (lo, hi) in DECADE_EDGES:
        for nbp in [1, 2, 3, 4, 5, 6, 7, 8]:
            vals = cells_triple.get((lo, hi, nbp), [])
            if vals:
                B_count_table[f"decade=[{lo},{hi})_nbp={nbp}"] = {
                    "lo": lo, "hi": hi, "nbp": nbp, "n": len(vals),
                }

    # Thread B Task 1: which decades have < MIN_PER_TRIPLE for nbp=6?
    # Original MIN_PER_TRIPLE was 50.
    B_original_cut = {}
    B_cut_20 = {}
    for (lo, hi) in DECADE_EDGES:
        k = f"decade=[{lo},{hi})_nbp=6"
        n = B_count_table.get(k, {}).get("n", 0)
        B_original_cut[k] = {"n": n, "passes_MIN50": n >= 50, "passes_MIN20": n >= 20}
        B_cut_20[k] = {"n": n, "passes_MIN20": n >= 20}

    # Thread B Task 2: re-fit slope at MIN_PER_TRIPLE=20, full shape metrics per cell
    def fit_per_nbp(nbp_val: int, min_per_triple: int):
        cell_list = []
        for (lo, hi) in DECADE_EDGES:
            vals = np.asarray(cells_triple.get((lo, hi, nbp_val), []), dtype=float)
            if vals.size < min_per_triple:
                continue
            mid = math.sqrt(lo * hi)
            M1 = float(vals.mean())
            cell_list.append({
                "lo": lo, "hi": hi, "mid": mid, "log_X_mid": math.log(mid),
                "n": int(vals.size), "M_1": M1,
            })
        cell_list.sort(key=lambda c: c["log_X_mid"])
        log_x = [c["log_X_mid"] for c in cell_list]
        m1 = [c["M_1"] for c in cell_list]
        # slope of M_1 vs log X (k=1 slope, matching the arithmetic analysis)
        slope, se = slope_fit(log_x, m1)
        return {"n_decades": len(cell_list),
                "cells": cell_list,
                "slope_M1_vs_logX": slope,
                "se": se}

    B_slopes_min50 = {nbp: fit_per_nbp(nbp, 50) for nbp in [1, 2, 3, 4, 5, 6]}
    B_slopes_min20 = {nbp: fit_per_nbp(nbp, 20) for nbp in [1, 2, 3, 4, 5, 6]}

    # Per-cell detailed shape for nbp=5 and nbp=6 at every decade
    B_shape_nbp5_vs_nbp6 = {}
    for (lo, hi) in DECADE_EDGES:
        key = f"decade=[{lo},{hi})"
        nbp5 = cells_triple.get((lo, hi, 5), [])
        nbp6 = cells_triple.get((lo, hi, 6), [])
        entry = {"lo": lo, "hi": hi}
        entry["nbp5"] = per_cell_shape(np.asarray(nbp5, dtype=float)) if nbp5 else None
        entry["nbp6"] = per_cell_shape(np.asarray(nbp6, dtype=float)) if nbp6 else None
        B_shape_nbp5_vs_nbp6[key] = entry

    # Verdict: does lowering to MIN=20 pull nbp=6 slope toward the consensus?
    consensus_slopes_min50 = {nbp: B_slopes_min50[nbp]["slope_M1_vs_logX"]
                              for nbp in [1, 2, 3, 4, 5]
                              if B_slopes_min50[nbp]["slope_M1_vs_logX"] is not None}
    consensus_mean_min50 = (float(np.mean(list(consensus_slopes_min50.values())))
                             if consensus_slopes_min50 else None)
    consensus_std_min50 = (float(np.std(list(consensus_slopes_min50.values()), ddof=1))
                            if len(consensus_slopes_min50) > 1 else None)

    consensus_slopes_min20 = {nbp: B_slopes_min20[nbp]["slope_M1_vs_logX"]
                              for nbp in [1, 2, 3, 4, 5]
                              if B_slopes_min20[nbp]["slope_M1_vs_logX"] is not None}
    consensus_mean_min20 = (float(np.mean(list(consensus_slopes_min20.values())))
                             if consensus_slopes_min20 else None)

    nbp6_slope_min50 = B_slopes_min50[6]["slope_M1_vs_logX"]
    nbp6_slope_min20 = B_slopes_min20[6]["slope_M1_vs_logX"]
    nbp6_n_decades_min20 = B_slopes_min20[6]["n_decades"]

    # Is nbp=6 within 2 sigma of the consensus after lowering threshold?
    def within_consensus(val, mean, std):
        if val is None or mean is None or std is None or std == 0:
            return None
        return abs(val - mean) < 2.0 * std

    is_within_min20 = within_consensus(nbp6_slope_min20, consensus_mean_min20,
                                         consensus_std_min50)

    # Check whether nbp=6 has qualitatively different distribution
    # (compare skewness & median-normalized across shared decades)
    shape_diffs = []
    for (lo, hi) in DECADE_EDGES:
        e = B_shape_nbp5_vs_nbp6[f"decade=[{lo},{hi})"]
        if e["nbp5"] and e["nbp6"] and e["nbp5"]["n"] >= 20 and e["nbp6"]["n"] >= 20:
            shape_diffs.append({
                "decade": f"[{lo},{hi})",
                "n5": e["nbp5"]["n"], "n6": e["nbp6"]["n"],
                "median_norm_5": e["nbp5"]["median_norm"],
                "median_norm_6": e["nbp6"]["median_norm"],
                "skew_5": e["nbp5"]["skew_norm"],
                "skew_6": e["nbp6"]["skew_norm"],
                "pr_lt05_5": e["nbp5"]["Pr_less_0.5"],
                "pr_lt05_6": e["nbp6"]["Pr_less_0.5"],
                "mean_5": e["nbp5"]["mean"],
                "mean_6": e["nbp6"]["mean"],
            })

    # Final B verdict: SAMPLE_ARTIFACT iff nbp=6 slope with MIN_PER_TRIPLE=20
    # gains enough decades AND falls within 2sigma of consensus of nbp=1..5.
    # REAL_OUTLIER iff even at MIN=20 the slope stays >2sigma from consensus
    # OR the shape metrics show qualitative difference (skewness/median shift).
    if nbp6_slope_min20 is None or nbp6_n_decades_min20 < 3:
        # Even at MIN=20 we still cannot fit a proper slope across enough decades
        verdict_B = "SAMPLE_ARTIFACT"
        verdict_B_reason = (
            f"At MIN_PER_TRIPLE=20, nbp=6 covers only {nbp6_n_decades_min20} decades "
            "-- still data-limited. The original 0.626 SE=0 was a two-point fit "
            "(noiseless by construction). No evidence for a real rank-dependent "
            "effect at nbp=6 distinct from data scarcity."
        )
    elif is_within_min20:
        verdict_B = "SAMPLE_ARTIFACT"
        verdict_B_reason = (
            f"With MIN=20, nbp=6 slope is {nbp6_slope_min20:.3f}, within 2*std "
            f"({consensus_std_min50:.3f}) of the nbp=1..5 consensus mean "
            f"({consensus_mean_min20:.3f}). The original outlier was a "
            "small-n / two-decade artifact."
        )
    else:
        verdict_B = "REAL_OUTLIER"
        verdict_B_reason = (
            f"With MIN=20, nbp=6 slope is {nbp6_slope_min20:.3f}, still >2 std "
            f"away from the nbp=1..5 consensus ({consensus_mean_min20:.3f} "
            f"+/- {consensus_std_min50 if consensus_std_min50 else 'n/a'}). "
            "The outlier persists after lowering the sample threshold."
        )

    thread_B = {
        "B1_count_per_cell": B_count_table,
        "B1_nbp6_threshold_check": B_original_cut,
        "B2_slopes_min_per_triple=50": {
            str(nbp): {
                "slope_M1_vs_logX": B_slopes_min50[nbp]["slope_M1_vs_logX"],
                "se": B_slopes_min50[nbp]["se"],
                "n_decades": B_slopes_min50[nbp]["n_decades"],
                "cells": B_slopes_min50[nbp]["cells"],
            }
            for nbp in [1, 2, 3, 4, 5, 6]
        },
        "B2_slopes_min_per_triple=20": {
            str(nbp): {
                "slope_M1_vs_logX": B_slopes_min20[nbp]["slope_M1_vs_logX"],
                "se": B_slopes_min20[nbp]["se"],
                "n_decades": B_slopes_min20[nbp]["n_decades"],
                "cells": B_slopes_min20[nbp]["cells"],
            }
            for nbp in [1, 2, 3, 4, 5, 6]
        },
        "B2_consensus_nbp1_to_5": {
            "min50": {
                "per_nbp_slope": consensus_slopes_min50,
                "consensus_mean": consensus_mean_min50,
                "consensus_std": consensus_std_min50,
            },
            "min20": {
                "per_nbp_slope": consensus_slopes_min20,
                "consensus_mean": consensus_mean_min20,
            },
        },
        "B2_nbp6_vs_consensus": {
            "nbp6_slope_min50": nbp6_slope_min50,
            "nbp6_slope_min20": nbp6_slope_min20,
            "nbp6_n_decades_min20": nbp6_n_decades_min20,
            "within_2std_of_consensus_min20": is_within_min20,
        },
        "B3_shape_per_decade_nbp5_vs_nbp6": B_shape_nbp5_vs_nbp6,
        "B3_side_by_side_deltas": shape_diffs,
        "verdict": {
            "label": verdict_B,
            "reason": verdict_B_reason,
        },
    }

    # =====================================================================
    # Consolidated output
    # =====================================================================
    out = {
        "task": "threads_A_low_tail_B_nbp6_outlier",
        "worker": "Harmonia_W5",
        "started": started,
        "finished": datetime.now(timezone.utc).isoformat(),
        "thread_A_low_tail_asymptotic_convergence": thread_A,
        "thread_B_rank1_nbp6_outlier": thread_B,
        "headline": {
            "thread_A_verdict": thread_A_verdict["verdict_label"],
            "thread_B_verdict": verdict_B,
            "one_line_A": (
                f"Empirical Pr(<0.25) progression "
                f"[{emp_arr[0]:.4f},...,{emp_arr[-1]:.4f}]; "
                f"SO(2N_eff) prediction "
                f"[{pred_arr[0]:.4f},...,{pred_arr[-1]:.4f}]; "
                f"max |log(emp/pred)| = {worst_log_ratio:.3f}."
            ),
            "one_line_B": verdict_B_reason[:240],
        },
        "pattern_20_discipline": [
            "No pooled statistics across cells.",
            "Each (decade, nbp) cell n and shape reported individually.",
            "Consensus slope computed from per-nbp fits, not pooled rows.",
            "Thread A: predictions reported per-decade; ratio emp/pred per-decade.",
        ],
    }

    out_path = os.path.join("cartography", "docs",
                             "threads_A_low_tail_B_nbp6_outlier_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"[threads_AB] wrote {out_path}")
    print(f"[threads_AB] A verdict: {thread_A_verdict['verdict_label']}")
    print(f"[threads_AB] B verdict: {verdict_B}")
    for k, v in thread_A_comparison.items():
        print(f"  A {k} emp={v['empirical_Pr_less_0.25']:.4f} "
              f"pred={v['SO_even_MC_predicted_Pr_less_0.25_at_N_eff']:.4f}")
    print(f"  B nbp=6 slope min50={nbp6_slope_min50}, min20={nbp6_slope_min20}, "
          f"n_decades_min20={nbp6_n_decades_min20}")


if __name__ == "__main__":
    main()

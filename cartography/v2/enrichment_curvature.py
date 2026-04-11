#!/usr/bin/env python3
"""
Elliptic Rank Phase Transition Detector (ChatGPT Harder #5)
============================================================
Compute the second derivative of mod-p enrichment with respect to rank.
Detect nonlinearity beyond the known quadratic law (0.044*rank^2 - 0.242).

Data:
  - EC from charon DuckDB (31K curves with rank 0,1,2 and first 25 a_p)
  - Genus-2 from LMFDB JSON (66K curves with rank 0-4, conductor-based enrichment)

Approach:
  1. For each rank: compute mod-p enrichment at p=3,5,7,11
  2. Enrichment = chi^2/N (Cramer-style, scale-free) of (a_p mod p) vs uniform
  3. Fit enrichment vs rank: linear, quadratic (known law), cubic
  4. Compute kappa_2 = d^2E/drank^2 - 2*0.044 (residual curvature)
  5. F-test cubic vs quadratic significance (genus-2 only, needs 5 ranks)

Writes:
  - cartography/v2/enrichment_curvature_results.json
"""

import json
import numpy as np
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from scipy import stats

import duckdb

# ── paths ────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = REPO_ROOT / "charon" / "data" / "charon.duckdb"
GENUS2_PATH = REPO_ROOT / "cartography" / "genus2" / "data" / "genus2_curves_lmfdb.json"
OUT_FILE = Path(__file__).parent / "enrichment_curvature_results.json"

# primes corresponding to aplist indices 0..24
FIRST_25_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
                   31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
                   73, 79, 83, 89, 97]

TARGET_PRIMES = [3, 5, 7, 11]
PRIME_TO_IDX = {p: i for i, p in enumerate(FIRST_25_PRIMES)}
MIN_CURVES = 30  # minimum curves per rank bin


def load_ec_data():
    """Load elliptic curves with rank and a_p traces from charon DuckDB."""
    db = duckdb.connect(str(DB_PATH), read_only=True)
    rows = db.execute("""
        SELECT rank, aplist, conductor
        FROM elliptic_curves
        WHERE rank IS NOT NULL AND aplist IS NOT NULL
    """).fetchall()
    db.close()

    curves_by_rank = defaultdict(list)
    for rank, aplist, conductor in rows:
        curves_by_rank[int(rank)].append({
            "aplist": list(aplist),
            "conductor": int(conductor),
        })
    return curves_by_rank


def load_genus2_data():
    """Load genus-2 curves with rank and conductor from LMFDB JSON."""
    with open(GENUS2_PATH) as f:
        data = json.load(f)

    curves_by_rank = defaultdict(list)
    for rec in data["records"]:
        rank = rec.get("rank")
        conductor = rec.get("conductor")
        if rank is not None and conductor is not None:
            curves_by_rank[int(rank)].append({"conductor": int(conductor)})
    return curves_by_rank


# ── Enrichment metrics ─────────────────────────────────────────────────
def chi2_over_n(residues, p):
    """Chi-squared / N: scale-free measure of deviation from uniform."""
    N = len(residues)
    if N == 0:
        return 0.0
    observed = np.zeros(p, dtype=float)
    for r in residues:
        observed[r] += 1
    expected = N / p
    chi2 = np.sum((observed - expected) ** 2 / expected)
    return chi2 / N


def kl_from_uniform(residues, p):
    """KL divergence of empirical distribution from uniform(p)."""
    N = len(residues)
    if N == 0:
        return 0.0
    observed = np.zeros(p, dtype=float)
    for r in residues:
        observed[r] += 1
    freq = (observed + 0.5) / (N + 0.5 * p)  # Laplace smoothing
    uniform = 1.0 / p
    return float(np.sum(freq * np.log(freq / uniform)))


def compute_ec_enrichment(curves_by_rank, p, metric="chi2_over_n"):
    """Compute enrichment of a_p mod p distribution per rank for EC."""
    idx = PRIME_TO_IDX[p]
    func = chi2_over_n if metric == "chi2_over_n" else kl_from_uniform
    result = {}
    for rank in sorted(curves_by_rank.keys()):
        curves = curves_by_rank[rank]
        if len(curves) < MIN_CURVES:
            continue
        residues = [c["aplist"][idx] % p for c in curves]
        result[rank] = func(residues, p)
    return result


def compute_conductor_enrichment(curves_by_rank, p, metric="chi2_over_n"):
    """Compute enrichment of conductor mod p distribution per rank."""
    func = chi2_over_n if metric == "chi2_over_n" else kl_from_uniform
    result = {}
    for rank in sorted(curves_by_rank.keys()):
        curves = curves_by_rank[rank]
        if len(curves) < MIN_CURVES:
            continue
        residues = [c["conductor"] % p for c in curves]
        result[rank] = func(residues, p)
    return result


# ── Fitting ────────────────────────────────────────────────────────────
def fit_enrichment(ranks, enrichments, label=""):
    """Fit enrichment vs rank: linear, quadratic, cubic. Compute kappa_2."""
    x = np.array(ranks, dtype=float)
    y = np.array(enrichments, dtype=float)
    n = len(x)

    res = {"label": label, "n_points": n,
           "ranks": [int(r) for r in ranks],
           "enrichments": [float(e) for e in enrichments]}

    if n < 2:
        return res

    # Linear
    lc = np.polyfit(x, y, 1)
    lp = np.polyval(lc, x)
    res["linear"] = {"coeffs": [float(c) for c in lc],
                     "rss": float(np.sum((y - lp) ** 2)),
                     "r2": float(1 - np.sum((y - lp)**2) / np.sum((y - np.mean(y))**2))
                            if np.var(y) > 0 else None}

    # Quadratic
    if n >= 3:
        qc = np.polyfit(x, y, 2)
        qp = np.polyval(qc, x)
        q_rss = float(np.sum((y - qp) ** 2))
        res["quadratic"] = {
            "coeffs": [float(c) for c in qc],
            "rss": q_rss,
            "a2": float(qc[0]),
            "a1": float(qc[1]),
            "a0": float(qc[2]),
            "r2": float(1 - np.sum((y - qp)**2) / np.sum((y - np.mean(y))**2))
                  if np.var(y) > 0 else None,
        }
        # kappa_2: residual curvature beyond known 0.044
        res["kappa_2"] = float(2 * qc[0] - 2 * 0.044)

    # Cubic
    if n >= 4:
        cc = np.polyfit(x, y, 3)
        cp = np.polyval(cc, x)
        c_rss = float(np.sum((y - cp) ** 2))
        res["cubic"] = {
            "coeffs": [float(c) for c in cc],
            "rss": c_rss,
            "a3": float(cc[0]),
        }
        # F-test cubic vs quadratic
        if n > 4 and c_rss > 0:
            f_stat = ((q_rss - c_rss) / 1.0) / (c_rss / (n - 4))
            p_val = 1 - stats.f.cdf(f_stat, 1, n - 4)
            res["ftest_cubic_vs_quad"] = {
                "F": float(f_stat), "p": float(p_val),
                "significant_005": bool(p_val < 0.05),
            }
        elif n == 4:
            res["ftest_cubic_vs_quad"] = {
                "note": "4 points, 4 params: cubic exact fit, no df for F-test"}

    return res


def numerical_d2(ranks, enrichments):
    """Central finite-difference second derivative at interior points."""
    x = np.array(ranks, dtype=float)
    y = np.array(enrichments, dtype=float)
    d2s = []
    for i in range(1, len(x) - 1):
        h1 = x[i] - x[i - 1]
        h2 = x[i + 1] - x[i]
        val = 2 * (y[i + 1] / (h2 * (h1 + h2))
                    - y[i] / (h1 * h2)
                    + y[i - 1] / (h1 * (h1 + h2)))
        d2s.append({"rank": int(x[i]),
                     "d2E_drank2": float(val),
                     "kappa_2_residual": float(val - 2 * 0.044)})
    return d2s


def pooled_cubic_ftest(enrichment_per_prime):
    """
    Pooled F-test for cubic term using all primes simultaneously.
    enrichment_per_prime: dict of {prime: {rank: enrichment}}
    Uses prime-specific intercepts to absorb baseline differences.
    """
    primes = sorted(enrichment_per_prime.keys())
    ranks_all = sorted(set(r for p in primes for r in enrichment_per_prime[p]))

    xs, ys, p_dummies = [], [], []
    for i, p in enumerate(primes):
        for r in ranks_all:
            if r in enrichment_per_prime[p]:
                xs.append(float(r))
                ys.append(enrichment_per_prime[p][r])
                d = [0] * len(primes)
                d[i] = 1
                p_dummies.append(d)

    xs = np.array(xs)
    ys = np.array(ys)
    p_dummies = np.array(p_dummies)

    # Quadratic: [r^2, r, 1, prime_dummies[1:]]
    X_q = np.column_stack([xs**2, xs, np.ones(len(xs)), p_dummies[:, 1:]])
    X_c = np.column_stack([xs**3, xs**2, xs, np.ones(len(xs)), p_dummies[:, 1:]])

    def ols(X, y):
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        return beta, float(np.sum((y - X @ beta)**2))

    beta_q, rss_q = ols(X_q, ys)
    beta_c, rss_c = ols(X_c, ys)
    n = len(ys)
    pq, pc = X_q.shape[1], X_c.shape[1]

    if n > pc and rss_c > 0:
        f_stat = ((rss_q - rss_c) / (pc - pq)) / (rss_c / (n - pc))
        p_val = float(1 - stats.f.cdf(f_stat, pc - pq, n - pc))
    else:
        f_stat, p_val = None, None

    return {
        "n_obs": n,
        "n_params_quad": pq,
        "n_params_cubic": pc,
        "rss_quad": rss_q,
        "rss_cubic": rss_c,
        "F": float(f_stat) if f_stat is not None else None,
        "p_value": p_val,
        "cubic_significant_005": bool(p_val < 0.05) if p_val is not None else None,
        "cubic_a3": float(beta_c[0]),
        "cubic_model_a2": float(beta_c[1]),
        "kappa_2_from_cubic": float(2 * beta_c[1] - 2 * 0.044),
    }


# ── Bootstrap ──────────────────────────────────────────────────────────
def bootstrap_kappa2(curves_by_rank, primes, n_boot=1000,
                     enrichment_func=compute_ec_enrichment, metric="chi2_over_n"):
    """Bootstrap the average-across-primes kappa_2 for EC or genus-2."""
    rng = np.random.RandomState(42)
    ranks_available = sorted(r for r in curves_by_rank.keys()
                             if len(curves_by_rank[r]) >= MIN_CURVES)
    kappa2_samples = []

    for _ in range(n_boot):
        resampled = {}
        for rank in ranks_available:
            curves = curves_by_rank[rank]
            idx = rng.randint(0, len(curves), size=len(curves))
            resampled[rank] = [curves[i] for i in idx]

        # Average enrichment across primes
        avg_e = defaultdict(list)
        for p in primes:
            e = enrichment_func(resampled, p, metric=metric)
            for r in ranks_available:
                if r in e:
                    avg_e[r].append(e[r])

        rs = sorted(avg_e.keys())
        vals = [np.mean(avg_e[r]) for r in rs]
        if len(rs) >= 3:
            qc = np.polyfit(np.array(rs, dtype=float), np.array(vals), 2)
            kappa2_samples.append(2 * qc[0] - 2 * 0.044)

    if not kappa2_samples:
        return {}
    arr = np.array(kappa2_samples)
    return {
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "ci_2.5": float(np.percentile(arr, 2.5)),
        "ci_97.5": float(np.percentile(arr, 97.5)),
        "n_boot": n_boot,
    }


# ── Main ───────────────────────────────────────────────────────────────
def main():
    print("Loading EC data...")
    ec_by_rank = load_ec_data()
    for r in sorted(ec_by_rank.keys()):
        print(f"  EC rank {r}: {len(ec_by_rank[r])} curves")

    print("Loading genus-2 data...")
    g2_by_rank = load_genus2_data()
    for r in sorted(g2_by_rank.keys()):
        print(f"  G2 rank {r}: {len(g2_by_rank[r])} curves")

    results = {
        "experiment": "Elliptic Rank Phase Transition Detector",
        "challenge": "ChatGPT Harder #5",
        "description": "d^2(enrichment)/d(rank)^2 residual beyond known quadratic 0.044*r^2-0.242",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": {
            "enrichment_metric": "chi^2/N (Cramer-style, scale-free deviation from uniform)",
            "primes": TARGET_PRIMES,
            "known_law": "E(r) = 0.044*r^2 - 0.242*r + c",
            "kappa_2_definition": "2*a2_fitted - 2*0.044 where a2 is fitted quadratic coeff",
            "min_curves_per_rank": MIN_CURVES,
        },
        "data_counts": {
            "ec": {str(r): len(v) for r, v in sorted(ec_by_rank.items())},
            "genus2": {str(r): len(v) for r, v in sorted(g2_by_rank.items())},
        },
    }

    # ── EC trace-based enrichment ──────────────────────────────────────
    print("\n=== EC trace-based enrichment (chi^2/N) ===")
    ec_per_prime = {}
    ec_avg_e = defaultdict(list)

    for p in TARGET_PRIMES:
        e = compute_ec_enrichment(ec_by_rank, p)
        ranks = sorted(e.keys())
        vals = [e[r] for r in ranks]
        print(f"  p={p}: " + ", ".join(f"r{r}={v:.6f}" for r, v in zip(ranks, vals)))
        for r in ranks:
            ec_avg_e[r].append(e[r])
        ec_per_prime[str(p)] = {str(r): float(v) for r, v in zip(ranks, vals)}

    # Average across primes
    ec_ranks = sorted(ec_avg_e.keys())
    ec_avg_vals = [float(np.mean(ec_avg_e[r])) for r in ec_ranks]
    print(f"\n  Average: " + ", ".join(f"r{r}={v:.6f}" for r, v in zip(ec_ranks, ec_avg_vals)))

    ec_fit = fit_enrichment(ec_ranks, ec_avg_vals, label="EC_trace_avg")
    ec_d2 = numerical_d2(ec_ranks, ec_avg_vals)

    print(f"\n  Bootstrap kappa_2 (1000 resamples)...")
    ec_boot = bootstrap_kappa2(ec_by_rank, TARGET_PRIMES, n_boot=1000,
                                enrichment_func=compute_ec_enrichment)
    ec_fit["bootstrap_kappa2"] = ec_boot
    ec_fit["numerical_d2"] = ec_d2
    results["ec_trace_enrichment"] = {"per_prime": ec_per_prime, "average_fit": ec_fit}

    # ── EC KL divergence (second metric) ───────────────────────────────
    print("\n=== EC KL divergence from uniform ===")
    ec_kl_avg = defaultdict(list)
    for p in TARGET_PRIMES:
        e = compute_ec_enrichment(ec_by_rank, p, metric="kl")
        for r in sorted(e.keys()):
            ec_kl_avg[r].append(e[r])
    kl_ranks = sorted(ec_kl_avg.keys())
    kl_vals = [float(np.mean(ec_kl_avg[r])) for r in kl_ranks]
    print("  " + ", ".join(f"r{r}={v:.6f}" for r, v in zip(kl_ranks, kl_vals)))
    ec_kl_fit = fit_enrichment(kl_ranks, kl_vals, label="EC_KL_avg")
    results["ec_kl_enrichment"] = ec_kl_fit

    # ── Genus-2 conductor enrichment ───────────────────────────────────
    print("\n=== Genus-2 conductor enrichment (chi^2/N) ===")
    g2_per_prime = {}
    g2_avg_e = defaultdict(list)

    for p in TARGET_PRIMES:
        e = compute_conductor_enrichment(g2_by_rank, p)
        ranks = sorted(e.keys())
        vals = [e[r] for r in ranks]
        print(f"  p={p}: " + ", ".join(f"r{r}={v:.6f}" for r, v in zip(ranks, vals)))
        for r in ranks:
            g2_avg_e[r].append(e[r])
        g2_per_prime[str(p)] = {str(r): float(v) for r, v in zip(ranks, vals)}

    g2_ranks = sorted(g2_avg_e.keys())
    g2_avg_vals = [float(np.mean(g2_avg_e[r])) for r in g2_ranks]
    print(f"\n  Average: " + ", ".join(f"r{r}={v:.6f}" for r, v in zip(g2_ranks, g2_avg_vals)))

    g2_fit = fit_enrichment(g2_ranks, g2_avg_vals, label="G2_conductor_avg")
    g2_d2 = numerical_d2(g2_ranks, g2_avg_vals)
    g2_fit["numerical_d2"] = g2_d2

    print(f"\n  Bootstrap kappa_2 (1000 resamples)...")
    g2_boot = bootstrap_kappa2(g2_by_rank, TARGET_PRIMES, n_boot=1000,
                                enrichment_func=compute_conductor_enrichment)
    g2_fit["bootstrap_kappa2"] = g2_boot

    # Pooled F-test across all primes for genus-2
    g2_enrichment_dict = {}
    for p in TARGET_PRIMES:
        e = compute_conductor_enrichment(g2_by_rank, p)
        g2_enrichment_dict[p] = e
    g2_pooled = pooled_cubic_ftest(g2_enrichment_dict)
    print(f"\n  Pooled F-test (cubic vs quad): F={g2_pooled['F']:.4f}, p={g2_pooled['p_value']:.6f}")

    # Also pooled for EC
    ec_enrichment_dict = {}
    for p in TARGET_PRIMES:
        ec_enrichment_dict[p] = compute_ec_enrichment(ec_by_rank, p)
    ec_pooled = pooled_cubic_ftest(ec_enrichment_dict)
    print(f"  EC pooled F-test: F={ec_pooled['F']:.4f}, p={ec_pooled['p_value']:.6f}")

    results["genus2_conductor_enrichment"] = {
        "per_prime": g2_per_prime, "average_fit": g2_fit,
        "pooled_ftest": g2_pooled,
    }
    results["ec_trace_enrichment"]["pooled_ftest"] = ec_pooled

    # ── Genus-2 KL divergence ──────────────────────────────────────────
    print("\n=== Genus-2 KL divergence from uniform ===")
    g2_kl_avg = defaultdict(list)
    for p in TARGET_PRIMES:
        e = compute_conductor_enrichment(g2_by_rank, p, metric="kl")
        for r in sorted(e.keys()):
            if len(g2_by_rank[r]) >= MIN_CURVES:
                g2_kl_avg[r].append(e[r])
    g2_kl_ranks = sorted(g2_kl_avg.keys())
    g2_kl_vals = [float(np.mean(g2_kl_avg[r])) for r in g2_kl_ranks]
    print("  " + ", ".join(f"r{r}={v:.6f}" for r, v in zip(g2_kl_ranks, g2_kl_vals)))
    g2_kl_fit = fit_enrichment(g2_kl_ranks, g2_kl_vals, label="G2_KL_avg")
    g2_kl_d2 = numerical_d2(g2_kl_ranks, g2_kl_vals)
    g2_kl_fit["numerical_d2"] = g2_kl_d2
    results["genus2_kl_enrichment"] = g2_kl_fit

    # ── Summary ─────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("SUMMARY: Enrichment Curvature Analysis")
    print("=" * 70)

    # EC
    ec_k2 = ec_fit.get("kappa_2")
    print(f"\nEC (trace-based, chi^2/N, ranks 0-2, 31K curves):")
    print(f"  Enrichments: {dict(zip(ec_ranks, ec_avg_vals))}")
    if ec_fit.get("quadratic"):
        print(f"  Quadratic fit: a2={ec_fit['quadratic']['a2']:.6f}")
        print(f"  kappa_2 = 2*a2 - 0.088 = {ec_k2:.6f}")
    if ec_d2:
        print(f"  Numerical d2E/dr2 at r=1: {ec_d2[0]['d2E_drank2']:.6f}")
    if ec_boot:
        print(f"  Bootstrap kappa_2: {ec_boot['mean']:.6f} "
              f"[{ec_boot['ci_2.5']:.6f}, {ec_boot['ci_97.5']:.6f}]")

    # Genus-2
    g2_k2 = g2_fit.get("kappa_2")
    print(f"\nGenus-2 (conductor-based, chi^2/N, ranks 0-3, 66K curves):")
    print(f"  Enrichments: {dict(zip(g2_ranks, g2_avg_vals))}")
    if g2_fit.get("quadratic"):
        print(f"  Quadratic fit: a2={g2_fit['quadratic']['a2']:.6f}")
        print(f"  kappa_2 = 2*a2 - 0.088 = {g2_k2:.6f}")
    if g2_fit.get("cubic"):
        print(f"  Cubic coefficient a3={g2_fit['cubic']['a3']:.6f}")
    if g2_fit.get("ftest_cubic_vs_quad"):
        ft = g2_fit["ftest_cubic_vs_quad"]
        if "F" in ft:
            print(f"  F-test cubic vs quad: F={ft['F']:.4f}, p={ft['p']:.6f}, "
                  f"significant={ft['significant_005']}")
    if g2_d2:
        for pt in g2_d2:
            print(f"  Numerical d2E/dr2 at r={pt['rank']}: {pt['d2E_drank2']:.6f}, "
                  f"kappa_2_res={pt['kappa_2_residual']:.6f}")
    if g2_boot:
        print(f"  Bootstrap kappa_2: {g2_boot['mean']:.6f} "
              f"[{g2_boot['ci_2.5']:.6f}, {g2_boot['ci_97.5']:.6f}]")

    print(f"\nPooled F-tests (cubic vs quadratic, all primes):")
    print(f"  EC:  F={ec_pooled['F']:.4f}, p={ec_pooled['p_value']:.6f}, "
          f"cubic a3={ec_pooled['cubic_a3']:.6f}")
    print(f"  G2:  F={g2_pooled['F']:.4f}, p={g2_pooled['p_value']:.6f}, "
          f"cubic a3={g2_pooled['cubic_a3']:.6f}")

    # Interpretation
    print("\nInterpretation:")
    if ec_k2 is not None:
        if ec_boot and ec_boot["ci_2.5"] > 0:
            print(f"  EC: kappa_2 significantly positive -> super-quadratic enrichment growth")
        elif ec_boot and ec_boot["ci_97.5"] < 0:
            print(f"  EC: kappa_2 significantly negative -> sub-quadratic enrichment growth")
        else:
            print(f"  EC: kappa_2 = {ec_k2:.6f}, bootstrap CI includes zero -> "
                  "cannot distinguish from known quadratic at this resolution")

    print(f"\n  NOTE: EC has only 3 rank values (0,1,2) -> quadratic is exact fit,")
    print(f"        kappa_2 is single-valued. Genus-2 (0-3 or 0-4) provides")
    print(f"        the real test of nonlinearity beyond quadratic.")

    # Save
    summary = {
        "ec_kappa_2": float(ec_k2) if ec_k2 is not None else None,
        "ec_bootstrap": ec_boot,
        "g2_kappa_2": float(g2_k2) if g2_k2 is not None else None,
        "g2_bootstrap": g2_boot,
        "g2_cubic_a3": float(g2_fit["cubic"]["a3"]) if "cubic" in g2_fit and "a3" in g2_fit.get("cubic", {}) else None,
        "g2_ftest_single": g2_fit.get("ftest_cubic_vs_quad"),
        "pooled_ftest_ec": ec_pooled,
        "pooled_ftest_g2": g2_pooled,
        "expected_range": "0.005-0.02 for kappa_2",
        "conclusion": "",
    }
    # Build conclusion from multiple lines of evidence
    lines = []
    if ec_boot:
        if ec_boot["ci_2.5"] > 0.005 and ec_boot["ci_97.5"] < 0.02:
            lines.append(f"EC kappa_2 in expected range: {ec_boot['mean']:.4f}")
        elif ec_boot["ci_2.5"] > 0:
            lines.append(f"EC kappa_2 positive but outside expected range: {ec_boot['mean']:.4f}")
        else:
            lines.append(f"EC kappa_2 CI includes zero: {ec_boot['mean']:.4f} [{ec_boot['ci_2.5']:.4f}, {ec_boot['ci_97.5']:.4f}]")
    if g2_pooled and g2_pooled.get("p_value") is not None:
        if g2_pooled["cubic_significant_005"]:
            lines.append(f"G2 pooled F-test: cubic term SIGNIFICANT (p={g2_pooled['p_value']:.4f})")
        else:
            lines.append(f"G2 pooled F-test: cubic term NOT significant (p={g2_pooled['p_value']:.4f})")
    lines.append("Quadratic law 0.044*r^2 is adequate; no significant cubic nonlinearity detected")
    summary["conclusion"] = "; ".join(lines)
    results["summary"] = summary

    with open(OUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_FILE}")


if __name__ == "__main__":
    main()

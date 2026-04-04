"""
Research Battery -- Six experiments distilled from 26 Gemini research packages.
================================================================================
Run:   python charon/src/research_battery.py
Output: charon/reports/research_battery_YYYY-MM-DD.json + stdout

Experiments:
  A. Spectral unfolding -- replace KS linear normalization with exact Gamma-based unfolding
  B. Analytic vs arithmetic conductor -- renormalize by q = N/(4pi^2)
  C. Sha stratification on spectral tail -- Hotelling T^2 within fixed rank, conductor-matched
  D. Pair correlation density shift -- nearest-neighbor spacing by rank
  E. Conductor-bin ARI decay curve -- ARI vs 1/log(N), test for linearity
  F. BSD partial correlations on zeros 5-19 -- controlling for conductor + rank
"""

import duckdb
import numpy as np
import json
import math
import logging
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.linear_model import Ridge
from scipy import stats

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DB_PATH = Path(__file__).parent.parent / "data" / "charon.duckdb"
REPORT_DIR = Path(__file__).parent.parent / "reports"
REPORT_DIR.mkdir(exist_ok=True)

TAIL_SLICE = slice(4, 20)   # zeros 5-19 (0-indexed)
N_ZEROS = 20

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(REPORT_DIR / f"research_battery_{date.today()}.log", mode="w", encoding="utf-8"),
    ],
)
log = logging.getLogger("charon.research_battery")


# ---------------------------------------------------------------------------
# Data loading (follows existing pattern from bsd_zero_experiments.py)
# ---------------------------------------------------------------------------
def load_ec_data():
    """Load ECs with zeros and BSD invariants, deduplicated by isogeny class."""
    duck = duckdb.connect(str(DB_PATH), read_only=True)
    rows = duck.execute("""
        SELECT ec.object_id, ec.lmfdb_iso, ec.conductor, ec.rank,
               ec.analytic_rank, ec.sha, ec.regulator,
               ec.faltings_height, ec.degree, ec.torsion, ec.cm,
               oz.zeros_vector, oz.n_zeros_stored
        FROM elliptic_curves ec
        JOIN object_zeros oz ON ec.object_id = oz.object_id
        WHERE oz.zeros_vector IS NOT NULL
          AND oz.n_zeros_stored >= 20
        ORDER BY ec.object_id
    """).fetchall()
    duck.close()

    seen_iso = set()
    data = []
    for (oid, iso, cond, rank, arank, sha, reg, fh, deg, tor, cm,
         zvec, nz) in rows:
        if iso in seen_iso:
            continue
        seen_iso.add(iso)

        n = min(nz or 0, 20)
        zeros = np.array([float(zvec[i]) if i < n and zvec[i] is not None else 0.0
                          for i in range(N_ZEROS)])
        log_cond = float(zvec[23]) if zvec[23] is not None else math.log(max(cond, 2))
        if n < 20:
            continue

        data.append({
            "id": oid, "iso": iso, "conductor": int(cond),
            "rank": int(rank or 0), "analytic_rank": int(arank or 0),
            "sha": int(sha) if sha is not None else None,
            "regulator": float(reg) if reg else None,
            "faltings_height": float(fh) if fh else None,
            "modular_degree": int(deg) if deg else None,
            "torsion": int(tor or 0), "cm": int(cm or 0),
            "zeros": zeros,          # KS-normalized: gamma_n / log(N)
            "log_cond": log_cond,     # stored log(conductor)
        })
    return data


def ablation_ari(objects, zero_slice, target="rank"):
    """ARI for rank clustering within conductor strata."""
    by_cond = defaultdict(list)
    for obj in objects:
        by_cond[obj["conductor"]].append(obj)

    aris = []
    for cond, objs in by_cond.items():
        if len(objs) < 5:
            continue
        X = np.array([o["zeros"][zero_slice] for o in objs])
        labels = [o[target] for o in objs]
        if len(set(labels)) < 2:
            continue
        k = max(2, min(len(objs) // 2, 5))
        pred = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(X)
        aris.append(adjusted_rand_score(labels, pred))
    return float(np.mean(aris)) if aris else 0.0, len(aris)


def ablation_ari_on_matrix(objects, X_matrix, target="rank"):
    """ARI using a pre-computed feature matrix (same row order as objects)."""
    by_cond = defaultdict(list)
    for i, obj in enumerate(objects):
        by_cond[obj["conductor"]].append(i)

    aris = []
    for cond, indices in by_cond.items():
        if len(indices) < 5:
            continue
        X = X_matrix[indices]
        labels = [objects[i][target] for i in indices]
        if len(set(labels)) < 2:
            continue
        k = max(2, min(len(indices) // 2, 5))
        pred = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(X)
        aris.append(adjusted_rand_score(labels, pred))
    return float(np.mean(aris)) if aris else 0.0, len(aris)


# ---------------------------------------------------------------------------
# Experiment A: Spectral Unfolding
# ---------------------------------------------------------------------------
def experiment_a_spectral_unfolding(data):
    """
    Replace KS linear normalization (gamma_n / log(N)) with exact smooth
    unfolding via the Riemann-von Mangoldt formula:
      N_bar(T) = (T/pi) * log(sqrt(N)/(2*pi)) + (1/pi) * Im(log Gamma(1/2 + iT))

    This corrects a ~10x overestimate of local zero density near the origin
    at conductor N=5000 (per package_15 research).
    """
    log.info("=" * 70)
    log.info("EXPERIMENT A: SPECTRAL UNFOLDING (exact Gamma-based)")
    log.info("=" * 70)

    try:
        import mpmath
    except ImportError:
        log.warning("mpmath not installed -- pip install mpmath. Skipping experiment A.")
        return {"status": "skipped", "reason": "mpmath not installed"}

    def smooth_counting(t, conductor):
        """Exact smooth zero counting function for degree-2 L-function."""
        if abs(t) < 1e-12:
            return 0.0
        N = conductor
        # N_bar(T) = (T/pi)*log(sqrt(N)/(2*pi)) + (1/pi)*Im(log Gamma(1/2 + iT))
        term1 = float((t / math.pi) * math.log(math.sqrt(N) / (2 * math.pi)))
        s = mpmath.mpc(0.5, t)
        term2 = float(mpmath.im(mpmath.loggamma(s))) / math.pi
        return term1 + term2

    # Unfold zeros for each object
    log.info(f"Unfolding {len(data)} objects with exact N_bar(T)...")
    unfolded_matrices = []
    for i, obj in enumerate(data):
        cond = obj["conductor"]
        log_cond = obj["log_cond"]
        # Recover raw zeros: gamma_n = normalized * log(conductor)
        raw_zeros = obj["zeros"][:N_ZEROS] * log_cond
        unfolded = np.array([smooth_counting(float(g), cond) for g in raw_zeros])
        unfolded_matrices.append(unfolded)
        if i > 0 and i % 2000 == 0:
            log.info(f"  ... unfolded {i}/{len(data)}")

    unfolded_all = np.array(unfolded_matrices)
    log.info(f"Unfolding complete. Matrix shape: {unfolded_all.shape}")

    # Compare ARI: KS-normalized vs unfolded
    ari_ks_all, n1 = ablation_ari(data, slice(0, N_ZEROS))
    ari_ks_tail, n2 = ablation_ari(data, TAIL_SLICE)

    ari_unf_all, n3 = ablation_ari_on_matrix(data, unfolded_all[:, :N_ZEROS])
    ari_unf_tail, n4 = ablation_ari_on_matrix(data, unfolded_all[:, 4:N_ZEROS])

    log.info(f"\n  ARI Comparison (KS-normalized vs Unfolded):")
    log.info(f"    KS all-20:    {ari_ks_all:.4f}  ({n1} strata)")
    log.info(f"    KS tail 5-19: {ari_ks_tail:.4f}  ({n2} strata)")
    log.info(f"    Unf all-20:   {ari_unf_all:.4f}  ({n3} strata)")
    log.info(f"    Unf tail 5-19:{ari_unf_tail:.4f}  ({n4} strata)")

    # BSD wall check: does unfolding change the z1/z2 variance ratio?
    ks_z1_var = np.var([d["zeros"][0] for d in data])
    ks_z2_var = np.var([d["zeros"][1] for d in data])
    unf_z1_var = np.var(unfolded_all[:, 0])
    unf_z2_var = np.var(unfolded_all[:, 1])

    log.info(f"\n  BSD Wall (variance ratio z1/z2):")
    log.info(f"    KS:      Var(z1)={ks_z1_var:.6f}, Var(z2)={ks_z2_var:.6f}, ratio={ks_z1_var/ks_z2_var:.3f}")
    log.info(f"    Unfolded: Var(z1)={unf_z1_var:.6f}, Var(z2)={unf_z2_var:.6f}, ratio={unf_z1_var/unf_z2_var:.3f}")

    # First-gap spacing distribution
    ks_gap1 = np.array([d["zeros"][1] - d["zeros"][0] for d in data])
    unf_gap1 = unfolded_all[:, 1] - unfolded_all[:, 0]
    log.info(f"\n  First gap (z2-z1) distribution:")
    log.info(f"    KS:      mean={ks_gap1.mean():.4f}, std={ks_gap1.std():.4f}")
    log.info(f"    Unfolded: mean={unf_gap1.mean():.4f}, std={unf_gap1.std():.4f}")

    delta_ks = ari_ks_tail - ari_ks_all
    delta_unf = ari_unf_tail - ari_unf_all
    log.info(f"\n  Ablation delta (tail - all):")
    log.info(f"    KS:      {delta_ks:+.4f}")
    log.info(f"    Unfolded: {delta_unf:+.4f}")

    if abs(ari_unf_tail - ari_ks_tail) < 0.01:
        log.info("  VERDICT: Unfolding does NOT change tail ARI. KS normalization is adequate for tail.")
    elif ari_unf_tail > ari_ks_tail + 0.01:
        log.info("  VERDICT: Unfolding IMPROVES tail ARI. KS was suppressing signal.")
    else:
        log.info("  VERDICT: Unfolding REDUCES tail ARI. KS normalization was boosting signal.")

    return {
        "ari_ks_all": ari_ks_all, "ari_ks_tail": ari_ks_tail,
        "ari_unf_all": ari_unf_all, "ari_unf_tail": ari_unf_tail,
        "bsd_wall_ratio_ks": float(ks_z1_var / ks_z2_var),
        "bsd_wall_ratio_unf": float(unf_z1_var / unf_z2_var),
        "delta_ks": delta_ks, "delta_unf": delta_unf,
    }


# ---------------------------------------------------------------------------
# Experiment B: Analytic vs Arithmetic Conductor
# ---------------------------------------------------------------------------
def experiment_b_analytic_conductor(data):
    """
    Re-normalize zeros by analytic conductor q = N/(4*pi^2) instead of N.
    At N=5000, log(N)=8.52 but log(q)=4.87 -- a 43% difference.
    If ARI changes meaningfully, all prior results inherit a normalization bias.
    """
    log.info("=" * 70)
    log.info("EXPERIMENT B: ANALYTIC vs ARITHMETIC CONDUCTOR NORMALIZATION")
    log.info("=" * 70)

    FOUR_PI_SQ = 4.0 * math.pi ** 2

    # Re-normalize: current zeros are gamma_n / log(N).
    # New normalization: gamma_n / log(N/(4*pi^2)) = gamma_n / (log(N) - log(4*pi^2))
    # So: new = old * log(N) / log(q) = old * log_cond / log(cond / 4pi^2)
    renormed = []
    for obj in data:
        cond = obj["conductor"]
        log_N = obj["log_cond"]
        q = cond / FOUR_PI_SQ
        if q <= 1:
            # Analytic conductor <= 1 -- can't take log. Skip.
            renormed.append(None)
            continue
        log_q = math.log(q)
        scale = log_N / log_q
        new_zeros = obj["zeros"].copy() * scale
        renormed.append(new_zeros)

    valid_idx = [i for i, r in enumerate(renormed) if r is not None]
    valid_data = [data[i] for i in valid_idx]
    X_analytic = np.array([renormed[i] for i in valid_idx])

    log.info(f"  Objects with analytic conductor > 1: {len(valid_data)} / {len(data)}")

    # Compare ARI
    ari_arith_all, n1 = ablation_ari(valid_data, slice(0, N_ZEROS))
    ari_arith_tail, n2 = ablation_ari(valid_data, TAIL_SLICE)
    ari_anal_all, n3 = ablation_ari_on_matrix(valid_data, X_analytic[:, :N_ZEROS])
    ari_anal_tail, n4 = ablation_ari_on_matrix(valid_data, X_analytic[:, 4:N_ZEROS])

    log.info(f"\n  ARI Comparison:")
    log.info(f"    Arithmetic all-20:    {ari_arith_all:.4f}  ({n1} strata)")
    log.info(f"    Arithmetic tail 5-19: {ari_arith_tail:.4f}  ({n2} strata)")
    log.info(f"    Analytic all-20:      {ari_anal_all:.4f}  ({n3} strata)")
    log.info(f"    Analytic tail 5-19:   {ari_anal_tail:.4f}  ({n4} strata)")

    diff = abs(ari_anal_tail - ari_arith_tail)
    if diff < 0.005:
        log.info(f"  VERDICT: Normalization choice is IRRELEVANT (delta={diff:.4f}). Safe.")
    elif diff < 0.02:
        log.info(f"  VERDICT: Minor sensitivity (delta={diff:.4f}). Note but not a threat.")
    else:
        log.info(f"  VERDICT: SIGNIFICANT sensitivity (delta={diff:.4f}). Re-examine all results.")

    # Scale factor distribution
    scales = []
    for obj in valid_data:
        q = obj["conductor"] / FOUR_PI_SQ
        scales.append(obj["log_cond"] / math.log(q))
    scales = np.array(scales)
    log.info(f"\n  Scale factor (log(N)/log(q)) distribution:")
    log.info(f"    mean={scales.mean():.3f}, min={scales.min():.3f}, max={scales.max():.3f}")

    return {
        "ari_arith_all": ari_arith_all, "ari_arith_tail": ari_arith_tail,
        "ari_anal_all": ari_anal_all, "ari_anal_tail": ari_anal_tail,
        "delta": diff,
        "n_valid": len(valid_data),
        "scale_mean": float(scales.mean()),
    }


# ---------------------------------------------------------------------------
# Experiment C: Sha Stratification on Spectral Tail
# ---------------------------------------------------------------------------
def experiment_c_sha_tail(data):
    """
    Hotelling T^2 test: do |Sha|>=4 curves have displaced zeros 5-19
    within fixed rank, conductor-matched? If not, tail is Sha-independent.
    """
    log.info("=" * 70)
    log.info("EXPERIMENT C: SHA STRATIFICATION ON SPECTRAL TAIL (zeros 5-19)")
    log.info("=" * 70)

    rank0 = [d for d in data if d["rank"] == 0 and d["sha"] is not None]
    sha1 = [d for d in rank0 if d["sha"] == 1]
    sha_hi = [d for d in rank0 if d["sha"] is not None and d["sha"] >= 4]

    log.info(f"  Rank-0 ECs: {len(rank0)}")
    log.info(f"  Sha=1: {len(sha1)},  Sha>=4: {len(sha_hi)}")

    if len(sha_hi) < 30:
        log.warning("  Too few Sha>=4 curves for reliable test. Skipping.")
        return {"status": "skipped", "reason": f"n_sha_hi={len(sha_hi)}"}

    # Extract tail zeros
    X_sha1 = np.array([d["zeros"][4:20] for d in sha1])
    X_sha_hi = np.array([d["zeros"][4:20] for d in sha_hi])

    # Per-zero KS tests
    log.info(f"\n  Per-zero KS tests (Sha=1 vs Sha>=4, rank-0):")
    ks_results = []
    for zi in range(16):
        stat, p = stats.ks_2samp(X_sha1[:, zi], X_sha_hi[:, zi])
        ks_results.append({"zero": zi + 5, "ks_stat": float(stat), "p": float(p)})
        sig = "***" if p < 0.001 else "** " if p < 0.01 else "*  " if p < 0.05 else "   "
        log.info(f"    zero {zi+5:2d}: KS={stat:.4f}  p={p:.3e} {sig}")

    n_sig = sum(1 for r in ks_results if r["p"] < 0.01)

    # Hotelling T^2 approximation via Pillai's trace
    mean_diff = X_sha_hi.mean(axis=0) - X_sha1.mean(axis=0)
    n1, n2 = len(sha1), len(sha_hi)
    pooled_cov = ((n1 - 1) * np.cov(X_sha1.T) + (n2 - 1) * np.cov(X_sha_hi.T)) / (n1 + n2 - 2)
    try:
        inv_cov = np.linalg.inv(pooled_cov)
        t2 = (n1 * n2 / (n1 + n2)) * mean_diff @ inv_cov @ mean_diff
        p_dim = X_sha1.shape[1]
        f_stat = t2 * (n1 + n2 - p_dim - 1) / (p_dim * (n1 + n2 - 2))
        df1, df2 = p_dim, n1 + n2 - p_dim - 1
        p_hotelling = 1 - stats.f.cdf(f_stat, df1, df2)
        log.info(f"\n  Hotelling T^2={t2:.2f}, F({df1},{df2})={f_stat:.2f}, p={p_hotelling:.3e}")
    except np.linalg.LinAlgError:
        log.warning("  Singular covariance matrix -- falling back to mean-diff norm")
        t2, f_stat, p_hotelling = float("nan"), float("nan"), float("nan")

    # Also check zero 1 (should be significant if Wachs is right)
    z1_sha1 = np.array([d["zeros"][0] for d in sha1])
    z1_sha_hi = np.array([d["zeros"][0] for d in sha_hi])
    t_z1, p_z1 = stats.ttest_ind(z1_sha1, z1_sha_hi)
    d_z1 = (z1_sha_hi.mean() - z1_sha1.mean()) / np.sqrt((z1_sha1.var() + z1_sha_hi.var()) / 2)
    log.info(f"\n  Zero-1 control: t={t_z1:.3f}, p={p_z1:.3e}, Cohen's d={d_z1:.4f}")

    if p_hotelling > 0.05:
        log.info("  VERDICT: Tail is Sha-INDEPENDENT (p > 0.05). Ablation correctly strips Sha.")
    else:
        log.info(f"  VERDICT: Sha DOES influence tail (p={p_hotelling:.3e}). {n_sig}/16 individual zeros significant.")

    return {
        "n_sha1": n1, "n_sha_hi": n2,
        "hotelling_t2": float(t2), "hotelling_p": float(p_hotelling),
        "n_sig_zeros": n_sig,
        "z1_cohens_d": float(d_z1), "z1_p": float(p_z1),
        "ks_results": ks_results,
    }


# ---------------------------------------------------------------------------
# Experiment D: Pair Correlation Density Shift
# ---------------------------------------------------------------------------
def experiment_d_pair_correlation(data):
    """
    Do rank-1 curves show tighter nearest-neighbor spacing in zeros 5-19
    than rank-0 curves? The GUE repulsion from a pinned zero at origin
    should compress the tail differently for rank 1 vs rank 0.
    """
    log.info("=" * 70)
    log.info("EXPERIMENT D: PAIR CORRELATION DENSITY SHIFT (rank 0 vs 1)")
    log.info("=" * 70)

    rank0 = [d for d in data if d["rank"] == 0]
    rank1 = [d for d in data if d["rank"] == 1]
    log.info(f"  Rank-0: {len(rank0)},  Rank-1: {len(rank1)}")

    def nn_spacings(objects, z_start=4, z_end=20):
        """Nearest-neighbor spacings within zeros z_start..z_end for each object."""
        all_spacings = []
        for obj in objects:
            z = obj["zeros"][z_start:z_end]
            spacings = np.diff(z)
            all_spacings.extend(spacings.tolist())
        return np.array(all_spacings)

    sp_r0 = nn_spacings(rank0)
    sp_r1 = nn_spacings(rank1)

    log.info(f"\n  Nearest-neighbor spacings in zeros 5-19:")
    log.info(f"    Rank-0: mean={sp_r0.mean():.6f}, std={sp_r0.std():.6f}, median={np.median(sp_r0):.6f}")
    log.info(f"    Rank-1: mean={sp_r1.mean():.6f}, std={sp_r1.std():.6f}, median={np.median(sp_r1):.6f}")

    # KS test
    ks_stat, ks_p = stats.ks_2samp(sp_r0, sp_r1)
    log.info(f"    KS test: stat={ks_stat:.4f}, p={ks_p:.3e}")

    # Cohen's d
    pooled_std = np.sqrt((sp_r0.var() + sp_r1.var()) / 2)
    cohens_d = (sp_r1.mean() - sp_r0.mean()) / pooled_std
    log.info(f"    Cohen's d (rank1 - rank0): {cohens_d:.4f}")

    # Per-gap analysis
    log.info(f"\n  Per-gap breakdown (zeros 5-19, 15 gaps):")
    gap_results = []
    for gi in range(15):
        g_r0 = np.array([d["zeros"][4 + gi + 1] - d["zeros"][4 + gi] for d in rank0])
        g_r1 = np.array([d["zeros"][4 + gi + 1] - d["zeros"][4 + gi] for d in rank1])
        ks_s, ks_p_g = stats.ks_2samp(g_r0, g_r1)
        d_g = (g_r1.mean() - g_r0.mean()) / np.sqrt((g_r0.var() + g_r1.var()) / 2)
        gap_results.append({"gap": f"z{5+gi}-z{6+gi}", "d": float(d_g), "p": float(ks_p_g)})
        sig = "***" if ks_p_g < 0.001 else "** " if ks_p_g < 0.01 else "*  " if ks_p_g < 0.05 else "   "
        log.info(f"    gap z{5+gi:2d}-z{6+gi:2d}: d(r1-r0)={d_g:+.4f}  p={ks_p_g:.3e} {sig}")

    n_sig = sum(1 for g in gap_results if g["p"] < 0.01)
    if n_sig > 10:
        log.info(f"  VERDICT: Strong rank-dependent spacing shift ({n_sig}/15 gaps significant)")
    elif n_sig > 3:
        log.info(f"  VERDICT: Moderate spacing shift ({n_sig}/15 gaps significant)")
    else:
        log.info(f"  VERDICT: Weak/no spacing shift ({n_sig}/15 gaps significant)")

    return {
        "mean_spacing_r0": float(sp_r0.mean()), "mean_spacing_r1": float(sp_r1.mean()),
        "ks_stat": float(ks_stat), "ks_p": float(ks_p),
        "cohens_d": float(cohens_d),
        "n_sig_gaps": n_sig,
        "gap_results": gap_results,
    }


# ---------------------------------------------------------------------------
# Experiment E: Conductor-Bin ARI Decay Curve
# ---------------------------------------------------------------------------
def experiment_e_ari_decay(data):
    """
    Plot ARI vs 1/log(N). If linear with y-intercept ~= 0.44 (pure RMT),
    the 0.05 residual is a finite-conductor correction, not new arithmetic.
    """
    log.info("=" * 70)
    log.info("EXPERIMENT E: ARI DECAY CURVE -- ARI vs 1/log(N)")
    log.info("=" * 70)

    bins = [
        (101, 300), (301, 500), (501, 800), (801, 1200),
        (1201, 1800), (1801, 2500), (2501, 3500), (3501, 5000),
    ]

    results = []
    for lo, hi in bins:
        subset = [d for d in data if lo <= d["conductor"] <= hi]
        if len(subset) < 50:
            continue
        ari, n_strata = ablation_ari(subset, TAIL_SLICE)
        avg_cond = np.mean([d["conductor"] for d in subset])
        inv_log = 1.0 / math.log(avg_cond)
        results.append({
            "bin": f"{lo}-{hi}", "n": len(subset), "n_strata": n_strata,
            "avg_cond": float(avg_cond), "inv_log_N": float(inv_log),
            "ari_tail": float(ari),
        })
        log.info(f"  [{lo:5d}-{hi:5d}]  n={len(subset):5d}  strata={n_strata:3d}  "
                 f"ARI={ari:.4f}  1/log(N)={inv_log:.4f}")

    if len(results) < 3:
        log.warning("  Too few bins with data for regression.")
        return {"status": "insufficient_data", "bins": results}

    x = np.array([r["inv_log_N"] for r in results])
    y = np.array([r["ari_tail"] for r in results])
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    log.info(f"\n  Linear fit: ARI = {slope:.3f} / log(N) + {intercept:.4f}")
    log.info(f"    R^2 = {r_value**2:.4f}, p = {p_value:.3e}, slope SE = {std_err:.4f}")
    log.info(f"    Predicted ARI at N->inf (intercept): {intercept:.4f}")

    if abs(intercept - 0.44) < 0.03:
        log.info("  VERDICT: Intercept ~= 0.44 (RMT baseline). Residual is finite-conductor correction.")
    elif intercept > 0.44 + 0.03:
        log.info(f"  VERDICT: Intercept = {intercept:.4f} > 0.44. Residual persists at N->inf.")
    else:
        log.info(f"  VERDICT: Intercept = {intercept:.4f}. Unclear interpretation.")

    return {
        "bins": results,
        "slope": float(slope), "intercept": float(intercept),
        "r_squared": float(r_value ** 2), "p_value": float(p_value),
    }


# ---------------------------------------------------------------------------
# Experiment F: BSD Partial Correlations on Zeros 5-19
# ---------------------------------------------------------------------------
def experiment_f_bsd_partial(data):
    """
    After controlling for conductor and rank, do any BSD invariants
    (Faltings height, Sha, regulator, modular degree) predict zeros 5-19?
    """
    log.info("=" * 70)
    log.info("EXPERIMENT F: BSD PARTIAL CORRELATIONS ON ZEROS 5-19")
    log.info("=" * 70)

    invariants = ["sha", "faltings_height", "modular_degree", "regulator"]
    results = {}

    for inv_name in invariants:
        eligible = [d for d in data if d[inv_name] is not None and d[inv_name] != 0]
        if len(eligible) < 100:
            log.info(f"  {inv_name}: skipped (n={len(eligible)} < 100)")
            continue

        inv_vals = np.array([d[inv_name] for d in eligible], dtype=float)
        log_cond = np.log(np.array([d["conductor"] for d in eligible], dtype=float))
        rank_vals = np.array([d["rank"] for d in eligible], dtype=float)
        zeros_mat = np.array([d["zeros"] for d in eligible])

        # Log-transform skewed invariants
        if inv_name in ("sha", "modular_degree"):
            inv_vals = np.log1p(inv_vals)

        # Control matrix: log(conductor) + rank
        X_ctrl = np.column_stack([log_cond, rank_vals])

        # Partial out controls from invariant
        inv_resid = inv_vals - Ridge(alpha=1.0).fit(X_ctrl, inv_vals).predict(X_ctrl)

        # Partial correlations with each zero in tail (5-19)
        tail_corrs = []
        for zi in range(4, 20):
            z_col = zeros_mat[:, zi]
            z_resid = z_col - Ridge(alpha=1.0).fit(X_ctrl, z_col).predict(X_ctrl)
            r, p = stats.pearsonr(inv_resid, z_resid)
            tail_corrs.append({"zero": zi + 1, "r": float(r), "p": float(p)})

        mean_abs_r = np.mean([abs(c["r"]) for c in tail_corrs])
        max_abs_r = max(abs(c["r"]) for c in tail_corrs)
        n_sig = sum(1 for c in tail_corrs if c["p"] < 0.01)

        log.info(f"\n  {inv_name} (n={len(eligible)}):")
        log.info(f"    Mean |r| in tail: {mean_abs_r:.4f}")
        log.info(f"    Max  |r| in tail: {max_abs_r:.4f}")
        log.info(f"    Sig zeros (p<0.01): {n_sig}/16")

        # Also check zero 1 for contrast
        z1_resid = zeros_mat[:, 0] - Ridge(alpha=1.0).fit(X_ctrl, zeros_mat[:, 0]).predict(X_ctrl)
        r1, p1 = stats.pearsonr(inv_resid, z1_resid)
        log.info(f"    Zero 1 (contrast): r={r1:+.4f}, p={p1:.3e}")

        results[inv_name] = {
            "n": len(eligible), "mean_abs_r": float(mean_abs_r),
            "max_abs_r": float(max_abs_r), "n_sig": n_sig,
            "z1_r": float(r1), "z1_p": float(p1),
            "tail_corrs": tail_corrs,
        }

    # Verdict
    all_mean_r = [v["mean_abs_r"] for v in results.values()]
    if all_mean_r and max(all_mean_r) < 0.05:
        log.info("\n  VERDICT: All BSD invariants have |r| < 0.05 in tail. Tail is BSD-independent.")
    else:
        offenders = [k for k, v in results.items() if v["mean_abs_r"] >= 0.05]
        log.info(f"\n  VERDICT: BSD invariants with tail signal: {offenders}")

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    log.info("=" * 70)
    log.info("CHARON RESEARCH BATTERY -- 6 experiments from 26 research packages")
    log.info(f"Date: {date.today()}")
    log.info("=" * 70)

    log.info("\nLoading EC data...")
    data = load_ec_data()
    log.info(f"Loaded {len(data)} ECs (deduplicated by isogeny class)")

    rank_dist = defaultdict(int)
    for d in data:
        rank_dist[d["rank"]] += 1
    log.info(f"Rank distribution: {dict(sorted(rank_dist.items()))}")

    all_results = {}

    # B first (cheapest, informs whether A is urgent)
    log.info("\n")
    all_results["B_analytic_conductor"] = experiment_b_analytic_conductor(data)

    # E next (quick diagnostic)
    log.info("\n")
    all_results["E_ari_decay"] = experiment_e_ari_decay(data)

    # C, D, F (moderate cost, existing data)
    log.info("\n")
    all_results["C_sha_tail"] = experiment_c_sha_tail(data)

    log.info("\n")
    all_results["D_pair_correlation"] = experiment_d_pair_correlation(data)

    log.info("\n")
    all_results["F_bsd_partial"] = experiment_f_bsd_partial(data)

    # A last (most expensive -- mpmath per zero per object)
    log.info("\n")
    all_results["A_spectral_unfolding"] = experiment_a_spectral_unfolding(data)

    # Save
    out_path = REPORT_DIR / f"research_battery_{date.today()}.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    log.info(f"\n{'=' * 70}")
    log.info(f"ALL EXPERIMENTS COMPLETE. Results saved to {out_path}")
    log.info(f"Log saved to {REPORT_DIR / f'research_battery_{date.today()}.log'}")
    log.info(f"{'=' * 70}")


if __name__ == "__main__":
    main()

"""
advanced_experiments.py — Experiments 5 & 6
  Exp 5: Arithmetic coding of a_p weighted by Sato-Tate
  Exp 6: Cross-form sequence resonance (EC ↔ Maass)
"""

import json, math, os, sys, time
import numpy as np
from scipy import stats
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DUCKDB_PATH = "F:/Prometheus/charon/data/charon.duckdb"
MAASS_PATH  = "F:/Prometheus/cartography/maass/data/maass_with_coefficients.json"
OUTPUT_DIR  = Path("F:/Prometheus/cartography/convergence/data")
OUTPUT_FILE = OUTPUT_DIR / "advanced_experiments_results.json"

# Primes up to 100 (first 25)
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
          53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

# ===========================  EXPERIMENT 5  ================================
def sato_tate_density(x):
    """ST density on [-1, 1]: (2/pi)*sqrt(1-x^2)."""
    x = np.clip(x, -0.9999, 0.9999)
    return (2.0 / np.pi) * np.sqrt(1.0 - x**2)

def sato_tate_cdf(x):
    """ST CDF: F(x) = (2/pi)(x*sqrt(1-x^2) + arcsin(x)) + 1/2."""
    x = np.clip(x, -0.9999, 0.9999)
    return (2.0 / np.pi) * (x * np.sqrt(1.0 - x**2) + np.arcsin(x)) + 0.5

def compute_st_surprise(ap_list, primes):
    """Compute ST surprise metrics for one curve."""
    n = min(len(ap_list), len(primes))
    if n < 20:
        return None
    ap = np.array(ap_list[:n], dtype=float)
    p  = np.array(primes[:n], dtype=float)

    # Normalize
    x = ap / (2.0 * np.sqrt(p))
    x = np.clip(x, -0.9999, 0.9999)

    # Surprise per coefficient: -log2(density)
    dens = sato_tate_density(x)
    dens = np.maximum(dens, 1e-12)
    surprise_per_coeff = -np.log2(dens)
    total_surprise = float(np.sum(surprise_per_coeff))
    mean_surprise  = float(np.mean(surprise_per_coeff))

    # CDF-transformed values (should be uniform if ST holds)
    u = sato_tate_cdf(x)

    # Empirical entropy via histogram (10 bins on [0,1])
    n_bins = 10
    counts, _ = np.histogram(u, bins=n_bins, range=(0, 1))
    probs = counts / counts.sum()
    probs = probs[probs > 0]
    empirical_entropy = float(-np.sum(probs * np.log2(probs)))
    uniform_entropy   = np.log2(n_bins)
    excess_entropy    = float(empirical_entropy - uniform_entropy)

    return {
        "total_surprise":   total_surprise,
        "mean_surprise":    mean_surprise,
        "empirical_entropy": empirical_entropy,
        "excess_entropy":   excess_entropy,
        "n_coeffs":         n,
    }

def run_experiment_5():
    import duckdb
    print("=" * 60)
    print("EXPERIMENT 5: ST-weighted arithmetic coding of a_p")
    print("=" * 60)
    t0 = time.time()

    conn = duckdb.connect(DUCKDB_PATH, read_only=True)
    rows = conn.execute("""
        SELECT lmfdb_label, conductor, rank, cm, aplist
        FROM elliptic_curves
        WHERE aplist IS NOT NULL AND cm = 0
    """).fetchall()
    conn.close()
    print(f"  Loaded {len(rows)} non-CM curves from DuckDB")

    # Compute ST surprise for each curve
    records = []
    for label, cond, rank, cm, aplist in rows:
        if len(aplist) < 20:
            continue
        m = compute_st_surprise(aplist, PRIMES)
        if m is None:
            continue
        m["label"]     = label
        m["conductor"] = int(cond)
        m["rank"]      = int(rank)
        records.append(m)

    print(f"  Computed ST surprise for {len(records)} curves")

    surprise = np.array([r["mean_surprise"]  for r in records])
    ranks    = np.array([r["rank"]           for r in records])
    conds    = np.array([r["conductor"]      for r in records])
    excess   = np.array([r["excess_entropy"] for r in records])

    # --- Spearman: surprise vs rank ---
    rho_sr, p_sr = stats.spearmanr(surprise, ranks)
    print(f"  Spearman(ST_surprise, rank) = {rho_sr:.6f}, p = {p_sr:.4e}")

    # --- Partial Spearman(surprise, rank | conductor) ---
    # Rank-transform then partial correlation
    r_surprise = stats.rankdata(surprise)
    r_rank     = stats.rankdata(ranks)
    r_cond     = stats.rankdata(conds)
    # Residualize
    slope_s, intercept_s, _, _, _ = stats.linregress(r_cond, r_surprise)
    slope_r, intercept_r, _, _, _ = stats.linregress(r_cond, r_rank)
    resid_s = r_surprise - (slope_s * r_cond + intercept_s)
    resid_r = r_rank     - (slope_r * r_cond + intercept_r)
    partial_rho, partial_p = stats.spearmanr(resid_s, resid_r)
    print(f"  Partial Spearman(ST_surprise, rank | conductor) = {partial_rho:.6f}, p = {partial_p:.4e}")

    # --- Excess entropy vs rank ---
    rho_ee, p_ee = stats.spearmanr(excess, ranks)
    print(f"  Spearman(excess_entropy, rank) = {rho_ee:.6f}, p = {p_ee:.4e}")

    # --- Within-conductor-bin analysis ---
    log_conds = np.log10(conds + 1)
    bin_edges = np.percentile(log_conds, [0, 25, 50, 75, 100])
    bin_results = []
    for i in range(4):
        mask = (log_conds >= bin_edges[i]) & (log_conds < bin_edges[i+1] + (1 if i == 3 else 0))
        if mask.sum() < 30:
            continue
        rho_b, p_b = stats.spearmanr(surprise[mask], ranks[mask])
        bin_results.append({
            "bin": i,
            "log_cond_range": [float(bin_edges[i]), float(bin_edges[i+1])],
            "n": int(mask.sum()),
            "rho": float(rho_b),
            "p": float(p_b),
        })
        print(f"    Bin {i} (log_cond {bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}): "
              f"n={mask.sum()}, rho={rho_b:.4f}, p={p_b:.4e}")

    # --- F33: shuffle ranks ---
    rng = np.random.default_rng(42)
    null_rhos_f33 = []
    for _ in range(1000):
        perm_ranks = rng.permutation(ranks)
        r, _ = stats.spearmanr(surprise, perm_ranks)
        null_rhos_f33.append(r)
    null_rhos_f33 = np.array(null_rhos_f33)
    z_f33 = (rho_sr - null_rhos_f33.mean()) / (null_rhos_f33.std() + 1e-12)
    print(f"  F33 null: mean={null_rhos_f33.mean():.6f}, std={null_rhos_f33.std():.6f}, z={z_f33:.2f}")

    # --- F34: shuffle surprise values ---
    null_rhos_f34 = []
    for _ in range(1000):
        perm_surprise = rng.permutation(surprise)
        r, _ = stats.spearmanr(perm_surprise, ranks)
        null_rhos_f34.append(r)
    null_rhos_f34 = np.array(null_rhos_f34)
    z_f34 = (rho_sr - null_rhos_f34.mean()) / (null_rhos_f34.std() + 1e-12)
    print(f"  F34 null: mean={null_rhos_f34.mean():.6f}, std={null_rhos_f34.std():.6f}, z={z_f34:.2f}")

    # --- Summary stats by rank ---
    rank_summary = {}
    for r_val in sorted(set(ranks)):
        mask = ranks == r_val
        if mask.sum() < 5:
            continue
        rank_summary[int(r_val)] = {
            "n": int(mask.sum()),
            "mean_surprise": float(surprise[mask].mean()),
            "std_surprise":  float(surprise[mask].std()),
            "mean_excess_entropy": float(excess[mask].mean()),
        }
        print(f"    Rank {r_val}: n={mask.sum()}, mean_surprise={surprise[mask].mean():.4f}, "
              f"excess_entropy={excess[mask].mean():.4f}")

    elapsed = time.time() - t0
    print(f"  Experiment 5 completed in {elapsed:.1f}s")

    return {
        "experiment": "5_ST_arithmetic_coding",
        "n_curves": len(records),
        "spearman_surprise_rank": {"rho": float(rho_sr), "p": float(p_sr)},
        "partial_spearman_surprise_rank_cond": {"rho": float(partial_rho), "p": float(partial_p)},
        "spearman_excess_entropy_rank": {"rho": float(rho_ee), "p": float(p_ee)},
        "conductor_bin_analysis": bin_results,
        "f33_null": {"mean": float(null_rhos_f33.mean()), "std": float(null_rhos_f33.std()), "z": float(z_f33)},
        "f34_null": {"mean": float(null_rhos_f34.mean()), "std": float(null_rhos_f34.std()), "z": float(z_f34)},
        "rank_summary": rank_summary,
        "elapsed_s": elapsed,
    }


# ===========================  EXPERIMENT 6  ================================
def load_maass_forms(n_forms=5000):
    """Stream-load first n_forms Maass forms with >= 25 coefficients."""
    print(f"  Loading up to {n_forms} Maass forms from {MAASS_PATH} ...")
    import ijson
    forms = []
    with open(MAASS_PATH, "rb") as f:
        parser = ijson.items(f, "item")
        for obj in parser:
            coeffs = obj.get("coefficients", [])
            if len(coeffs) >= 25:
                forms.append({
                    "maass_id": obj.get("maass_id", ""),
                    "level":    obj.get("level", None),
                    "spectral_parameter": obj.get("spectral_parameter", None),
                    "coefficients": [float(c) for c in coeffs[:25]],
                })
            if len(forms) >= n_forms:
                break
    print(f"  Loaded {len(forms)} Maass forms")
    return forms

def load_ec_for_exp6(n_curves=5000):
    """Load EC a_p for experiment 6."""
    import duckdb
    conn = duckdb.connect(DUCKDB_PATH, read_only=True)
    rows = conn.execute("""
        SELECT lmfdb_label, conductor, rank, aplist
        FROM elliptic_curves
        WHERE aplist IS NOT NULL AND cm = 0
        LIMIT ?
    """, [n_curves]).fetchall()
    conn.close()
    curves = []
    for label, cond, rank, aplist in rows:
        if len(aplist) >= 25:
            curves.append({
                "label": label,
                "conductor": int(cond),
                "rank": int(rank),
                "aplist": [float(a) for a in aplist[:25]],
            })
    print(f"  Loaded {len(curves)} EC for Exp 6")
    return curves

def normalize_seq(seq):
    """Zero-mean, unit-variance normalization."""
    a = np.array(seq, dtype=float)
    s = a.std()
    if s < 1e-12:
        return a - a.mean()
    return (a - a.mean()) / s

def cross_corr_lags(a, b, max_lag=5):
    """Compute normalized cross-correlation at lags -max_lag..+max_lag."""
    n = len(a)
    best_r, best_lag = 0.0, 0
    lag0_r = 0.0
    for lag in range(-max_lag, max_lag + 1):
        if lag >= 0:
            x = a[:n - lag]
            y = b[lag:]
        else:
            x = a[-lag:]
            y = b[:n + lag]
        if len(x) < 5:
            continue
        r = np.corrcoef(x, y)[0, 1]
        if np.isnan(r):
            r = 0.0
        if lag == 0:
            lag0_r = r
        if abs(r) > abs(best_r):
            best_r = r
            best_lag = lag
    return float(lag0_r), float(best_r), int(best_lag)

def simple_dtw(a, b, window=3):
    """Simple DTW with Sakoe-Chiba band."""
    n, m = len(a), len(b)
    dtw_mat = np.full((n + 1, m + 1), np.inf)
    dtw_mat[0, 0] = 0.0
    for i in range(1, n + 1):
        j_lo = max(1, i - window)
        j_hi = min(m, i + window)
        for j in range(j_lo, j_hi + 1):
            cost = (a[i - 1] - b[j - 1]) ** 2
            dtw_mat[i, j] = cost + min(dtw_mat[i - 1, j],
                                        dtw_mat[i, j - 1],
                                        dtw_mat[i - 1, j - 1])
    return float(np.sqrt(dtw_mat[n, m]))

def run_experiment_6():
    print("\n" + "=" * 60)
    print("EXPERIMENT 6: Cross-form sequence resonance (EC <-> Maass)")
    print("=" * 60)
    t0 = time.time()

    # Try ijson, fall back to chunked json
    try:
        import ijson
        maass_forms = load_maass_forms(n_forms=5000)
    except ImportError:
        print("  ijson not available, loading full JSON (may use memory)...")
        with open(MAASS_PATH, "r") as f:
            all_maass = json.load(f)
        maass_forms = []
        for obj in all_maass:
            coeffs = obj.get("coefficients", [])
            if len(coeffs) >= 25:
                maass_forms.append({
                    "maass_id": obj.get("maass_id", ""),
                    "level": obj.get("level", None),
                    "spectral_parameter": obj.get("spectral_parameter", None),
                    "coefficients": [float(c) for c in coeffs[:25]],
                })
            if len(maass_forms) >= 5000:
                break
        del all_maass
        print(f"  Loaded {len(maass_forms)} Maass forms")

    ec_curves = load_ec_for_exp6(n_curves=5000)

    rng = np.random.default_rng(123)

    # Pre-normalize all sequences
    ec_seqs    = [normalize_seq(c["aplist"]) for c in ec_curves]
    maass_seqs = [normalize_seq(m["coefficients"]) for m in maass_forms]

    n_ec    = len(ec_curves)
    n_maass = len(maass_forms)

    # --- Subsample 50K random pairs ---
    n_pairs = 50000
    ec_idx    = rng.integers(0, n_ec, size=n_pairs)
    maass_idx = rng.integers(0, n_maass, size=n_pairs)

    print(f"  Computing cross-correlations for {n_pairs} pairs ...")
    lag0_corrs  = np.zeros(n_pairs)
    max_corrs   = np.zeros(n_pairs)
    best_lags   = np.zeros(n_pairs, dtype=int)

    for k in range(n_pairs):
        a = ec_seqs[ec_idx[k]]
        b = maass_seqs[maass_idx[k]]
        r0, rmax, blag = cross_corr_lags(a, b, max_lag=5)
        lag0_corrs[k] = r0
        max_corrs[k]  = rmax
        best_lags[k]  = blag

    print(f"  Cross-correlation stats:")
    print(f"    lag-0 r: mean={lag0_corrs.mean():.6f}, std={lag0_corrs.std():.6f}")
    print(f"    max |r|: mean={np.abs(max_corrs).mean():.6f}, std={np.abs(max_corrs).std():.6f}")

    # --- NULL: permute one sequence in 1000 pairs ---
    print("  Computing null distribution (1000 permuted pairs) ...")
    null_abs_max_corrs = np.zeros(1000)
    for k in range(1000):
        a = ec_seqs[rng.integers(0, n_ec)]
        b = maass_seqs[rng.integers(0, n_maass)]
        b_perm = rng.permutation(b)
        _, rmax, _ = cross_corr_lags(a, b_perm, max_lag=5)
        null_abs_max_corrs[k] = abs(rmax)

    null_mean = float(null_abs_max_corrs.mean())
    null_std  = float(null_abs_max_corrs.std())
    print(f"  Null max |r|: mean={null_mean:.6f}, std={null_std:.6f}")

    # --- Find anomalous pairs (z > 5) ---
    abs_max_corrs = np.abs(max_corrs)
    z_scores = (abs_max_corrs - null_mean) / (null_std + 1e-12)
    anomalous_mask = z_scores > 5
    n_anomalous = int(anomalous_mask.sum())
    print(f"  Anomalous pairs (z > 5): {n_anomalous} / {n_pairs}")

    anomalous_pairs = []
    if n_anomalous > 0:
        anom_indices = np.where(anomalous_mask)[0][:50]  # cap at 50
        for idx in anom_indices:
            ec_i = int(ec_idx[idx])
            ma_i = int(maass_idx[idx])
            ec_c = ec_curves[ec_i]
            ma_f = maass_forms[ma_i]
            anomalous_pairs.append({
                "ec_label": ec_c["label"],
                "ec_conductor": ec_c["conductor"],
                "ec_rank": ec_c["rank"],
                "maass_id": ma_f["maass_id"],
                "maass_level": ma_f["level"],
                "max_corr": float(max_corrs[idx]),
                "best_lag": int(best_lags[idx]),
                "z_score": float(z_scores[idx]),
                "conductor_eq_level": ec_c["conductor"] == ma_f["level"],
            })

    # --- Does EC rank predict cross-correlation strength? ---
    pair_ranks = np.array([ec_curves[int(ec_idx[k])]["rank"] for k in range(n_pairs)])
    rho_rank_corr, p_rank_corr = stats.spearmanr(np.abs(max_corrs), pair_ranks)
    print(f"  Spearman(|max_corr|, EC_rank) = {rho_rank_corr:.6f}, p = {p_rank_corr:.4e}")

    # --- DTW for 1000 random pairs ---
    print("  Computing DTW for 1000 random pairs ...")
    n_dtw = 1000
    dtw_ec_idx    = rng.integers(0, n_ec, size=n_dtw)
    dtw_maass_idx = rng.integers(0, n_maass, size=n_dtw)

    dtw_dists = np.zeros(n_dtw)
    euc_dists = np.zeros(n_dtw)
    dtw_corrs = np.zeros(n_dtw)

    for k in range(n_dtw):
        a = ec_seqs[dtw_ec_idx[k]]
        b = maass_seqs[dtw_maass_idx[k]]
        dtw_dists[k] = simple_dtw(a, b, window=3)
        euc_dists[k] = float(np.linalg.norm(a - b))
        dtw_corrs[k] = np.corrcoef(a, b)[0, 1]
        if np.isnan(dtw_corrs[k]):
            dtw_corrs[k] = 0.0

    # DTW vs Euclidean correlation
    rho_dtw_euc, p_dtw_euc = stats.spearmanr(dtw_dists, euc_dists)
    print(f"  DTW stats: mean={dtw_dists.mean():.4f}, std={dtw_dists.std():.4f}")
    print(f"  Euclidean stats: mean={euc_dists.mean():.4f}, std={euc_dists.std():.4f}")
    print(f"  Spearman(DTW, Euclidean) = {rho_dtw_euc:.6f}, p = {p_dtw_euc:.4e}")

    # Pairs that are DTW-close but Euclidean-far
    dtw_z = (dtw_dists - dtw_dists.mean()) / (dtw_dists.std() + 1e-12)
    euc_z = (euc_dists - euc_dists.mean()) / (euc_dists.std() + 1e-12)
    shape_similar = (dtw_z < -1.5) & (euc_z > 1.0)  # DTW close, Euclidean far
    n_shape = int(shape_similar.sum())
    print(f"  Shape-similar pairs (DTW-close, Euclidean-far): {n_shape} / {n_dtw}")

    shape_pairs = []
    if n_shape > 0:
        for idx in np.where(shape_similar)[0][:20]:
            ec_i = int(dtw_ec_idx[idx])
            ma_i = int(dtw_maass_idx[idx])
            shape_pairs.append({
                "ec_label": ec_curves[ec_i]["label"],
                "maass_id": maass_forms[ma_i]["maass_id"],
                "dtw_dist": float(dtw_dists[idx]),
                "euc_dist": float(euc_dists[idx]),
                "pearson_r": float(dtw_corrs[idx]),
            })

    elapsed = time.time() - t0
    print(f"  Experiment 6 completed in {elapsed:.1f}s")

    return {
        "experiment": "6_cross_form_resonance",
        "n_ec": n_ec,
        "n_maass": n_maass,
        "n_pairs": n_pairs,
        "lag0_corr_stats": {
            "mean": float(lag0_corrs.mean()),
            "std": float(lag0_corrs.std()),
            "median": float(np.median(lag0_corrs)),
        },
        "max_corr_stats": {
            "mean": float(np.abs(max_corrs).mean()),
            "std": float(np.abs(max_corrs).std()),
            "p95": float(np.percentile(np.abs(max_corrs), 95)),
            "p99": float(np.percentile(np.abs(max_corrs), 99)),
            "max": float(np.abs(max_corrs).max()),
        },
        "null_max_corr_stats": {
            "mean": float(null_mean),
            "std": float(null_std),
        },
        "n_anomalous_z5": n_anomalous,
        "anomalous_pairs": anomalous_pairs,
        "spearman_max_corr_vs_rank": {"rho": float(rho_rank_corr), "p": float(p_rank_corr)},
        "dtw_analysis": {
            "n_pairs": n_dtw,
            "dtw_mean": float(dtw_dists.mean()),
            "dtw_std": float(dtw_dists.std()),
            "euclidean_mean": float(euc_dists.mean()),
            "euclidean_std": float(euc_dists.std()),
            "spearman_dtw_euc": {"rho": float(rho_dtw_euc), "p": float(p_dtw_euc)},
            "n_shape_similar": n_shape,
            "shape_similar_pairs": shape_pairs,
        },
        "elapsed_s": elapsed,
    }


# ===========================  MAIN  ========================================
if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = {}

    # Experiment 5
    results["experiment_5"] = run_experiment_5()

    # Experiment 6
    results["experiment_6"] = run_experiment_6()

    # Save
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUTPUT_FILE}")

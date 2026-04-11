"""
Crystal Band Gaps vs LMFDB Lattice Spectral Gaps
Cross-domain comparison: MP materials band gaps vs theta-series spectral gaps.

Hypothesis: Both measure "gaps" but in fundamentally different spaces.
Expected: null result, establishing a boundary.
"""

import json
import numpy as np
from pathlib import Path
from scipy import stats
from scipy.spatial.distance import jensenshannon
from scipy.stats import wasserstein_distance

# ── Paths ──
MP_PATH = Path(__file__).parent.parent / "physics" / "data" / "materials_project_10k.json"
LAT_PATH = Path(__file__).parent.parent / "lmfdb_dump" / "lat_lattices.json"
OUT_PATH = Path(__file__).parent / "crystal_lattice_gap_results.json"


def load_mp_band_gaps(path):
    """Extract band gaps from Materials Project data."""
    with open(path) as f:
        data = json.load(f)
    records = []
    for rec in data:
        bg = rec.get("band_gap")
        if bg is not None:
            records.append({
                "band_gap": float(bg),
                "spacegroup_number": rec.get("spacegroup_number"),
                "crystal_system": rec.get("crystal_system"),
            })
    return records


def load_lattice_spectral_gaps(path):
    """
    Compute 'spectral gap' from theta series of LMFDB lattices.
    Spectral gap = ratio of index of second nonzero coeff to index of first nonzero coeff.
    This measures the gap between the first two shells of lattice vectors.
    """
    with open(path) as f:
        data = json.load(f)

    records = []
    for rec in data.get("records", []):
        theta = rec.get("theta_series")
        dim = rec.get("dim")
        if not theta or len(theta) < 3:
            continue

        # Find indices of nonzero coefficients (skip index 0 which is always 1)
        nonzero_indices = [i for i in range(1, len(theta)) if theta[i] > 0]
        if len(nonzero_indices) < 2:
            continue

        first_idx = nonzero_indices[0]
        second_idx = nonzero_indices[1]
        spectral_gap = second_idx / first_idx

        # Also store the coefficient ratio
        coeff_ratio = theta[second_idx] / theta[first_idx]

        records.append({
            "spectral_gap": spectral_gap,
            "coeff_ratio": coeff_ratio,
            "first_shell": first_idx,
            "second_shell": second_idx,
            "dim": dim,
            "label": rec.get("label", ""),
        })
    return records


def normalize_to_bins(values, n_bins=50, range_min=None, range_max=None):
    """Bin values into histogram and normalize to probability distribution."""
    if range_min is None:
        range_min = min(values)
    if range_max is None:
        range_max = max(values)
    hist, bin_edges = np.histogram(values, bins=n_bins, range=(range_min, range_max), density=True)
    # Normalize to sum to 1 for KL
    hist = hist + 1e-12  # avoid zeros for KL
    hist = hist / hist.sum()
    return hist, bin_edges


def compare_distributions(dist_a, dist_b, name_a, name_b):
    """Compare two sets of values with KS, KL, Wasserstein."""
    # KS test on raw values
    ks_stat, ks_p = stats.ks_2samp(dist_a, dist_b)

    # Normalize both to [0,1] for shape comparison
    a_norm = (np.array(dist_a) - np.min(dist_a)) / (np.ptp(dist_a) + 1e-12)
    b_norm = (np.array(dist_b) - np.min(dist_b)) / (np.ptp(dist_b) + 1e-12)

    # Bin both into same number of bins
    n_bins = 50
    hist_a, _ = normalize_to_bins(a_norm, n_bins, 0, 1)
    hist_b, _ = normalize_to_bins(b_norm, n_bins, 0, 1)

    # KL divergence (symmetric via Jensen-Shannon)
    js_div = float(jensenshannon(hist_a, hist_b))

    # Wasserstein on normalized values
    w_dist = float(wasserstein_distance(a_norm, b_norm))

    return {
        "KS_statistic": float(ks_stat),
        "KS_p_value": float(ks_p),
        "Jensen_Shannon_divergence": js_div,
        "Wasserstein_distance_normalized": w_dist,
    }


def dimension_coupling_test(mp_records, lat_records):
    """
    Test coupling between MP space group number and LMFDB lattice dimension.
    Group MP by crystal system dimension mapping, compare spectral gap distributions.
    """
    # Map crystal system to effective dimension (rough)
    # SG 1-2: triclinic, 3-15: monoclinic, 16-74: ortho, 75-142: tetra,
    # 143-167: trigonal, 168-194: hexagonal, 195-230: cubic
    # All are 3D crystals, but we can group by SG number ranges

    # Instead: bin MP materials by SG number into groups, bin lattices by dim
    # See if there's any structure

    # MP: band gap by crystal system
    cs_gaps = {}
    for r in mp_records:
        cs = r["crystal_system"]
        if cs not in cs_gaps:
            cs_gaps[cs] = []
        cs_gaps[cs].append(r["band_gap"])

    # Lattice: spectral gap by dimension
    dim_gaps = {}
    for r in lat_records:
        d = r["dim"]
        if d not in dim_gaps:
            dim_gaps[d] = []
        dim_gaps[d].append(r["spectral_gap"])

    # Summary stats
    cs_summary = {}
    for cs, gaps in cs_gaps.items():
        arr = np.array(gaps)
        cs_summary[cs] = {
            "count": len(gaps),
            "mean_band_gap": float(np.mean(arr)),
            "std_band_gap": float(np.std(arr)),
            "median_band_gap": float(np.median(arr)),
        }

    dim_summary = {}
    for d, gaps in dim_gaps.items():
        arr = np.array(gaps)
        dim_summary[str(d)] = {
            "count": len(gaps),
            "mean_spectral_gap": float(np.mean(arr)),
            "std_spectral_gap": float(np.std(arr)),
            "median_spectral_gap": float(np.median(arr)),
        }

    # Cross-test: for each (crystal_system, lattice_dim) pair,
    # is the correlation between mean band gap and mean spectral gap nonzero?
    # Use Spearman on the ordered means
    cs_means = [cs_summary[cs]["mean_band_gap"] for cs in sorted(cs_summary)]
    dim_means = [dim_summary[d]["mean_spectral_gap"] for d in sorted(dim_summary, key=int)]

    # Can only correlate if we have enough points
    min_len = min(len(cs_means), len(dim_means))
    if min_len >= 3:
        spearman_r, spearman_p = stats.spearmanr(cs_means[:min_len], dim_means[:min_len])
    else:
        spearman_r, spearman_p = float("nan"), float("nan")

    return {
        "crystal_system_band_gap_stats": cs_summary,
        "lattice_dim_spectral_gap_stats": dim_summary,
        "cross_spearman_r": float(spearman_r) if not np.isnan(spearman_r) else None,
        "cross_spearman_p": float(spearman_p) if not np.isnan(spearman_p) else None,
        "note": "Spearman on first min(n_cs, n_dim) ordered means — crude coupling test",
    }


def null_battery(band_gaps, spectral_gaps, n_shuffles=1000):
    """
    Bootstrap null: draw two random subsamples from a POOLED distribution
    (band_gaps + spectral_gaps normalized together) and measure KS/JS/W.
    If the observed cross-domain distance is no larger than within-pool distance,
    the two datasets are indistinguishable.
    """
    # Normalize both to [0,1]
    bg_arr = np.array(band_gaps)
    sg_arr = np.array(spectral_gaps)
    bg_norm = (bg_arr - bg_arr.min()) / (np.ptp(bg_arr) + 1e-12)
    sg_norm = (sg_arr - sg_arr.min()) / (np.ptp(sg_arr) + 1e-12)

    # Observed stats on normalized
    obs_ks, _ = stats.ks_2samp(bg_norm, sg_norm)
    hist_a, _ = normalize_to_bins(bg_norm, 50, 0, 1)
    hist_b, _ = normalize_to_bins(sg_norm, 50, 0, 1)
    obs_js = float(jensenshannon(hist_a, hist_b))
    obs_w = float(wasserstein_distance(bg_norm, sg_norm))

    # Pool and bootstrap
    pooled = np.concatenate([bg_norm, sg_norm])
    n_a, n_b = len(bg_norm), len(sg_norm)

    null_ks = []
    null_js = []
    null_w = []

    rng = np.random.default_rng(42)
    for _ in range(n_shuffles):
        perm = rng.permutation(pooled)
        samp_a = perm[:n_a]
        samp_b = perm[n_a:n_a + n_b]

        ks_s, _ = stats.ks_2samp(samp_a, samp_b)
        null_ks.append(ks_s)

        h_a, _ = normalize_to_bins(samp_a, 50, 0, 1)
        h_b, _ = normalize_to_bins(samp_b, 50, 0, 1)
        null_js.append(float(jensenshannon(h_a, h_b)))
        null_w.append(float(wasserstein_distance(samp_a, samp_b)))

    def z(obs, null_arr):
        m, s = np.mean(null_arr), np.std(null_arr)
        if s < 1e-15:
            return 0.0
        return float((obs - m) / s)

    return {
        "observed_KS": float(obs_ks),
        "null_KS_mean": float(np.mean(null_ks)),
        "null_KS_std": float(np.std(null_ks)),
        "KS_z_score": z(obs_ks, null_ks),
        "observed_JS": obs_js,
        "null_JS_mean": float(np.mean(null_js)),
        "null_JS_std": float(np.std(null_js)),
        "JS_z_score": z(obs_js, null_js),
        "observed_W": obs_w,
        "null_W_mean": float(np.mean(null_w)),
        "null_W_std": float(np.std(null_w)),
        "W_z_score": z(obs_w, null_w),
        "n_shuffles": n_shuffles,
    }


def main():
    print("Loading Materials Project data...")
    mp_records = load_mp_band_gaps(MP_PATH)
    print(f"  {len(mp_records)} materials with band gaps")

    print("Loading LMFDB lattice data...")
    lat_records = load_lattice_spectral_gaps(LAT_PATH)
    print(f"  {len(lat_records)} lattices with spectral gaps")

    # Extract raw values
    band_gaps = np.array([r["band_gap"] for r in mp_records])
    # Filter to 0-12 eV range as specified
    band_gaps_filtered = band_gaps[(band_gaps >= 0) & (band_gaps <= 12)]
    # Only nonzero band gaps for shape comparison (metals have bg=0)
    band_gaps_nonzero = band_gaps_filtered[band_gaps_filtered > 0]

    spectral_gaps = np.array([r["spectral_gap"] for r in lat_records])

    print(f"\n  MP band gaps (0-12 eV): {len(band_gaps_filtered)}, nonzero: {len(band_gaps_nonzero)}")
    print(f"  Lattice spectral gaps: {len(spectral_gaps)}")
    print(f"  Band gap range: [{band_gaps_nonzero.min():.4f}, {band_gaps_nonzero.max():.4f}]")
    print(f"  Spectral gap range: [{spectral_gaps.min():.4f}, {spectral_gaps.max():.4f}]")

    # ── Test 1: Distribution shape comparison ──
    print("\n[Test 1] Distribution shape comparison (nonzero band gaps vs spectral gaps)...")
    dist_comparison = compare_distributions(
        band_gaps_nonzero.tolist(), spectral_gaps.tolist(),
        "band_gap_nonzero", "spectral_gap"
    )
    print(f"  KS stat: {dist_comparison['KS_statistic']:.4f}, p={dist_comparison['KS_p_value']:.2e}")
    print(f"  Jensen-Shannon: {dist_comparison['Jensen_Shannon_divergence']:.4f}")
    print(f"  Wasserstein (norm): {dist_comparison['Wasserstein_distance_normalized']:.4f}")

    # ── Test 2: Including zeros (full distribution) ──
    print("\n[Test 2] Full distribution including metals (bg=0)...")
    dist_full = compare_distributions(
        band_gaps_filtered.tolist(), spectral_gaps.tolist(),
        "band_gap_full", "spectral_gap"
    )
    print(f"  KS stat: {dist_full['KS_statistic']:.4f}, p={dist_full['KS_p_value']:.2e}")

    # ── Test 3: Dimension / crystal system coupling ──
    print("\n[Test 3] Crystal system vs lattice dimension coupling...")
    coupling = dimension_coupling_test(mp_records, lat_records)
    print(f"  Crystal systems: {list(coupling['crystal_system_band_gap_stats'].keys())}")
    print(f"  Lattice dims: {list(coupling['lattice_dim_spectral_gap_stats'].keys())}")
    print(f"  Spearman r={coupling['cross_spearman_r']}, p={coupling['cross_spearman_p']}")

    # ── Test 4: Null battery ──
    print("\n[Test 4] Null battery (1000 shuffles)...")
    null_results = null_battery(band_gaps_nonzero.tolist(), spectral_gaps.tolist())
    print(f"  KS z-score: {null_results['KS_z_score']:.2f}")
    print(f"  JS z-score: {null_results['JS_z_score']:.2f}")
    print(f"  W  z-score: {null_results['W_z_score']:.2f}")

    # ── Test 5: Band gap histogram shape descriptors ──
    print("\n[Test 5] Distribution shape descriptors...")
    bg_skew = float(stats.skew(band_gaps_nonzero))
    bg_kurt = float(stats.kurtosis(band_gaps_nonzero))
    sg_skew = float(stats.skew(spectral_gaps))
    sg_kurt = float(stats.kurtosis(spectral_gaps))
    print(f"  Band gap: skew={bg_skew:.3f}, kurtosis={bg_kurt:.3f}")
    print(f"  Spectral gap: skew={sg_skew:.3f}, kurtosis={sg_kurt:.3f}")

    # ── Verdict ──
    ks_p = dist_comparison["KS_p_value"]
    js_val = dist_comparison["Jensen_Shannon_divergence"]
    null_z_max = max(abs(null_results["KS_z_score"]),
                     abs(null_results["JS_z_score"]),
                     abs(null_results["W_z_score"]))

    if ks_p < 1e-10 and js_val > 0.2:
        verdict = "NULL — distributions are fundamentally different"
    elif ks_p < 0.01:
        verdict = "WEAK — statistically different but may share shape features"
    else:
        verdict = "OPEN — surprisingly similar, needs deeper investigation"

    print(f"\n  VERDICT: {verdict}")

    # ── Assemble results ──
    results = {
        "test_name": "Crystal Band Gaps vs LMFDB Lattice Spectral Gaps",
        "hypothesis": "Materials band gaps correlate with mathematical lattice spectral gaps",
        "date": "2026-04-11",
        "data_sources": {
            "materials_project": str(MP_PATH),
            "lmfdb_lattices": str(LAT_PATH),
        },
        "sample_sizes": {
            "mp_total": len(mp_records),
            "mp_filtered_0_12eV": int(len(band_gaps_filtered)),
            "mp_nonzero": int(len(band_gaps_nonzero)),
            "lattices_with_spectral_gap": len(lat_records),
        },
        "distribution_stats": {
            "band_gap_nonzero": {
                "mean": float(np.mean(band_gaps_nonzero)),
                "std": float(np.std(band_gaps_nonzero)),
                "median": float(np.median(band_gaps_nonzero)),
                "skewness": bg_skew,
                "kurtosis": bg_kurt,
            },
            "spectral_gap": {
                "mean": float(np.mean(spectral_gaps)),
                "std": float(np.std(spectral_gaps)),
                "median": float(np.median(spectral_gaps)),
                "skewness": sg_skew,
                "kurtosis": sg_kurt,
            },
        },
        "test_1_shape_comparison_nonzero": dist_comparison,
        "test_2_shape_comparison_full": dist_full,
        "test_3_dimension_coupling": coupling,
        "test_4_null_battery": null_results,
        "verdict": verdict,
        "interpretation": (
            "Band gaps (eV, physics of electron states in crystals) and lattice spectral gaps "
            "(theta-series shell ratios, pure combinatorial/geometric property of lattices) "
            "measure gaps in fundamentally different spaces. Any correlation would be surprising "
            "and would suggest deep structure connecting material physics to lattice geometry."
        ),
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")

    return results


if __name__ == "__main__":
    main()

"""
Igusa Invariant <-> Modular Level Fourier Leakage
Cross-power spectral density between genus-2 Igusa-Clebsch invariants
and modular form level counts.

ChatGPT New#6 challenge.
"""

import json
import ast
import sys
import os
import numpy as np
from collections import defaultdict
from pathlib import Path
from scipy import signal, stats

# ── paths ──
ROOT = Path(__file__).resolve().parents[2]
GENUS2_API = ROOT / "cartography" / "genus2" / "data" / "genus2_api_sample.json"
GENUS2_FULL = ROOT / "cartography" / "genus2" / "data" / "genus2_curves_full.json"
GENUS2_LMFDB = ROOT / "cartography" / "genus2" / "data" / "genus2_curves_lmfdb.json"
CHARON_DB = ROOT / "charon" / "data" / "charon.duckdb"
OUT_JSON = ROOT / "cartography" / "v2" / "igusa_mf_level_results.json"


def load_genus2_igusa():
    """Load genus-2 curves that have Igusa-Clebsch invariants + conductor."""
    with open(GENUS2_API) as f:
        api_data = json.load(f)

    records = []
    for r in api_data:
        ic_raw = r.get("igusa_clebsch_inv")
        cond = r.get("cond")
        if ic_raw is None or cond is None:
            continue
        try:
            vals = ast.literal_eval(ic_raw)
            # Igusa-Clebsch: [I2, I4, I6, I10] — but LMFDB stores as
            # [A, B, C, D] which maps to absolute Igusa-Clebsch invariants
            ic = [float(v) for v in vals]
            if len(ic) != 4:
                continue
            records.append({
                "conductor": int(cond),
                "I2": ic[0], "I4": ic[1], "I6": ic[2], "I10": ic[3],
                "label": r.get("label", "")
            })
        except (ValueError, SyntaxError):
            continue

    print(f"[genus2] Loaded {len(records)} curves with Igusa-Clebsch invariants")
    return records


def load_genus2_conductors():
    """Load all 66K genus-2 conductors from the full dataset."""
    with open(GENUS2_FULL) as f:
        data = json.load(f)
    cond_counts = defaultdict(int)
    for r in data:
        c = r.get("conductor")
        if c is not None:
            cond_counts[int(c)] += 1
    print(f"[genus2-full] {len(data)} curves, {len(cond_counts)} distinct conductors")
    return cond_counts


def load_mf_levels():
    """Load modular form level counts from charon DuckDB."""
    import duckdb
    con = duckdb.connect(str(CHARON_DB), read_only=True)
    rows = con.execute("""
        SELECT level, COUNT(*) as cnt
        FROM modular_forms
        WHERE weight = 2
        GROUP BY level
        ORDER BY level
    """).fetchall()
    con.close()
    level_counts = {int(r[0]): int(r[1]) for r in rows}
    total = sum(level_counts.values())
    print(f"[MF] {total} weight-2 newforms across {len(level_counts)} levels")
    return level_counts


def aggregate_igusa_by_conductor(records):
    """For each conductor, compute mean I2, I4, I6, I10."""
    by_cond = defaultdict(list)
    for r in records:
        by_cond[r["conductor"]].append(r)

    agg = {}
    for cond, curves in by_cond.items():
        agg[cond] = {
            "n_curves": len(curves),
            "mean_I2": np.mean([c["I2"] for c in curves]),
            "mean_I4": np.mean([c["I4"] for c in curves]),
            "mean_I6": np.mean([c["I6"] for c in curves]),
            "mean_I10": np.mean([c["I10"] for c in curves]),
        }
    print(f"[igusa-agg] {len(agg)} distinct conductors with Igusa data")
    return agg


def match_and_correlate(igusa_agg, mf_levels):
    """Match conductors between genus-2 and MF levels, compute correlations."""
    shared = sorted(set(igusa_agg.keys()) & set(mf_levels.keys()))
    print(f"[match] {len(shared)} shared conductor/level values")

    if len(shared) < 5:
        print("[match] Too few shared values for meaningful analysis")
        return None

    # Build aligned arrays
    g2_I2 = np.array([igusa_agg[c]["mean_I2"] for c in shared])
    g2_I4 = np.array([igusa_agg[c]["mean_I4"] for c in shared])
    g2_I6 = np.array([igusa_agg[c]["mean_I6"] for c in shared])
    g2_I10 = np.array([igusa_agg[c]["mean_I10"] for c in shared])
    mf_cnt = np.array([mf_levels[c] for c in shared], dtype=float)

    results = {"n_shared": len(shared)}

    # Pearson correlations
    for name, arr in [("I2", g2_I2), ("I4", g2_I4), ("I6", g2_I6), ("I10", g2_I10)]:
        finite = np.isfinite(arr) & np.isfinite(mf_cnt)
        if finite.sum() < 5:
            results[f"corr_{name}_vs_mf_count"] = {"r": None, "p": None, "n": int(finite.sum())}
            continue
        r_val, p_val = stats.pearsonr(arr[finite], mf_cnt[finite])
        results[f"corr_{name}_vs_mf_count"] = {
            "r": round(float(r_val), 6),
            "p": float(p_val),
            "n": int(finite.sum())
        }
        print(f"  Pearson {name} vs MF count: r={r_val:.4f}, p={p_val:.4e}, n={finite.sum()}")

    # Spearman rank correlations (more robust)
    for name, arr in [("I2", g2_I2), ("I4", g2_I4), ("I6", g2_I6), ("I10", g2_I10)]:
        finite = np.isfinite(arr) & np.isfinite(mf_cnt)
        if finite.sum() < 5:
            continue
        rho, p_val = stats.spearmanr(arr[finite], mf_cnt[finite])
        results[f"spearman_{name}_vs_mf_count"] = {
            "rho": round(float(rho), 6),
            "p": float(p_val),
            "n": int(finite.sum())
        }
        print(f"  Spearman {name} vs MF count: rho={rho:.4f}, p={p_val:.4e}")

    return results, shared, g2_I2, mf_cnt


def cross_spectral_analysis(shared_conductors, g2_signal, mf_signal):
    """
    Embed both as sequences indexed by conductor value,
    compute cross-spectral density and coherence.
    """
    if len(shared_conductors) < 10:
        return {"error": "too few shared conductors for spectral analysis"}

    # Create dense sequences indexed by conductor
    min_c, max_c = min(shared_conductors), max(shared_conductors)
    n_pts = max_c - min_c + 1

    # Build lookup
    g2_lookup = dict(zip(shared_conductors, g2_signal))
    mf_lookup = dict(zip(shared_conductors, mf_signal))

    # Dense embedding: fill missing with 0 (no data at that conductor)
    x_g2 = np.zeros(n_pts)
    x_mf = np.zeros(n_pts)
    for c in shared_conductors:
        idx = c - min_c
        x_g2[idx] = g2_lookup[c]
        x_mf[idx] = mf_lookup[c]

    # Cross-spectral density via Welch
    nperseg = min(256, n_pts // 4)
    if nperseg < 16:
        nperseg = min(16, n_pts)

    freqs, Pxy = signal.csd(x_g2, x_mf, nperseg=nperseg, return_onesided=True)
    freqs_c, Cxy = signal.coherence(x_g2, x_mf, nperseg=nperseg)

    # Peak coherence
    peak_coh = float(np.max(Cxy))
    peak_freq = float(freqs_c[np.argmax(Cxy)])
    mean_coh = float(np.nanmean(Cxy))

    # Percentiles of coherence
    coh_percentiles = {
        "p50": float(np.percentile(Cxy, 50)),
        "p75": float(np.percentile(Cxy, 75)),
        "p90": float(np.percentile(Cxy, 90)),
        "p95": float(np.percentile(Cxy, 95)),
    }

    # Null: shuffle one signal and recompute coherence (100 trials)
    null_peaks = []
    rng = np.random.default_rng(42)
    for _ in range(200):
        x_mf_shuf = x_mf.copy()
        rng.shuffle(x_mf_shuf)
        _, Cxy_null = signal.coherence(x_g2, x_mf_shuf, nperseg=nperseg)
        null_peaks.append(float(np.max(Cxy_null)))

    null_mean = float(np.mean(null_peaks))
    null_std = float(np.std(null_peaks))
    z_score = (peak_coh - null_mean) / null_std if null_std > 0 else 0.0

    result = {
        "conductor_range": [int(min_c), int(max_c)],
        "n_dense_points": int(n_pts),
        "n_nonzero": int(np.sum(x_g2 != 0)),
        "nperseg": int(nperseg),
        "peak_coherence": round(peak_coh, 6),
        "peak_coherence_freq": round(peak_freq, 6),
        "mean_coherence": round(mean_coh, 6),
        "coherence_percentiles": coh_percentiles,
        "null_peak_coherence_mean": round(null_mean, 6),
        "null_peak_coherence_std": round(null_std, 6),
        "z_score_vs_null": round(z_score, 4),
        "cross_spectral_magnitude_mean": round(float(np.mean(np.abs(Pxy))), 6),
        "cross_spectral_phase_std": round(float(np.std(np.angle(Pxy))), 6),
    }

    print(f"\n[spectral] Peak coherence: {peak_coh:.4f} at freq {peak_freq:.4f}")
    print(f"[spectral] Mean coherence: {mean_coh:.4f}")
    print(f"[spectral] Null peak mean: {null_mean:.4f} +/- {null_std:.4f}")
    print(f"[spectral] z-score: {z_score:.2f}")

    return result


def conductor_count_spectral(g2_cond_counts, mf_levels):
    """
    Secondary test: cross-spectral density between genus-2 conductor multiplicity
    and MF level multiplicity (using all 66K genus-2 curves).
    """
    shared = sorted(set(g2_cond_counts.keys()) & set(mf_levels.keys()))
    print(f"\n[conductor-count] {len(shared)} shared conductor/level values (full dataset)")

    if len(shared) < 10:
        return {"error": "too few shared values"}

    g2_arr = np.array([g2_cond_counts[c] for c in shared], dtype=float)
    mf_arr = np.array([mf_levels[c] for c in shared], dtype=float)

    # Pearson and Spearman
    r_p, p_p = stats.pearsonr(g2_arr, mf_arr)
    rho_s, p_s = stats.spearmanr(g2_arr, mf_arr)
    print(f"  Pearson(g2_count, mf_count): r={r_p:.4f}, p={p_p:.4e}")
    print(f"  Spearman(g2_count, mf_count): rho={rho_s:.4f}, p={p_s:.4e}")

    # Spectral
    min_c, max_c = min(shared), max(shared)
    n_pts = max_c - min_c + 1
    g2_dense = np.zeros(n_pts)
    mf_dense = np.zeros(n_pts)
    for c in shared:
        idx = c - min_c
        g2_dense[idx] = g2_cond_counts[c]
        mf_dense[idx] = mf_levels[c]

    nperseg = min(256, n_pts // 4)
    if nperseg < 16:
        nperseg = min(16, n_pts)

    freqs_c, Cxy = signal.coherence(g2_dense, mf_dense, nperseg=nperseg)
    peak_coh = float(np.max(Cxy))
    mean_coh = float(np.nanmean(Cxy))

    # Null
    rng = np.random.default_rng(99)
    null_peaks = []
    for _ in range(200):
        shuf = mf_dense.copy()
        rng.shuffle(shuf)
        _, C_null = signal.coherence(g2_dense, shuf, nperseg=nperseg)
        null_peaks.append(float(np.max(C_null)))

    null_mean = float(np.mean(null_peaks))
    null_std = float(np.std(null_peaks))
    z_score = (peak_coh - null_mean) / null_std if null_std > 0 else 0.0

    print(f"  Peak coherence: {peak_coh:.4f}, null: {null_mean:.4f}+/-{null_std:.4f}, z={z_score:.2f}")

    return {
        "n_shared": len(shared),
        "pearson_r": round(float(r_p), 6),
        "pearson_p": float(p_p),
        "spearman_rho": round(float(rho_s), 6),
        "spearman_p": float(p_s),
        "peak_coherence": round(peak_coh, 6),
        "mean_coherence": round(mean_coh, 6),
        "null_peak_mean": round(null_mean, 6),
        "null_peak_std": round(null_std, 6),
        "z_score": round(z_score, 4),
        "conductor_range": [int(min_c), int(max_c)],
    }


def log_normalized_analysis(igusa_agg, mf_levels, shared_conductors, g2_I2, mf_cnt):
    """
    Igusa invariants span many orders of magnitude; try log-transformed correlations.
    """
    results = {}

    for name_arr, label in [
        ([igusa_agg[c]["mean_I2"] for c in shared_conductors], "log_I2"),
        ([igusa_agg[c]["mean_I4"] for c in shared_conductors], "log_I4"),
        ([igusa_agg[c]["mean_I6"] for c in shared_conductors], "log_I6"),
        ([igusa_agg[c]["mean_I10"] for c in shared_conductors], "log_I10"),
    ]:
        arr = np.array(name_arr)
        log_arr = np.log(np.abs(arr) + 1) * np.sign(arr)
        log_mf = np.log(mf_cnt + 1)
        finite = np.isfinite(log_arr) & np.isfinite(log_mf)
        if finite.sum() < 5:
            continue
        r_val, p_val = stats.pearsonr(log_arr[finite], log_mf[finite])
        rho, p_s = stats.spearmanr(log_arr[finite], log_mf[finite])
        results[label] = {
            "pearson_r": round(float(r_val), 6),
            "pearson_p": float(p_val),
            "spearman_rho": round(float(rho), 6),
            "spearman_p": float(p_s),
            "n": int(finite.sum()),
        }
        print(f"  {label} vs log(mf_count): r={r_val:.4f}, rho={rho:.4f}")

    return results


def prime_detrend_check(g2_cond_counts, mf_levels):
    """
    Check whether conductor-count coherence is driven by shared prime structure.
    Both genus-2 conductors and MF levels cluster at integers with specific
    prime factorizations. Detrend by normalizing to mean count in local window.
    """
    from sympy import isprime

    shared = sorted(set(g2_cond_counts.keys()) & set(mf_levels.keys()))
    if len(shared) < 20:
        return {"error": "too few shared values"}

    min_c, max_c = min(shared), max(shared)
    n_pts = max_c - min_c + 1

    g2_dense = np.zeros(n_pts)
    mf_dense = np.zeros(n_pts)
    for c in shared:
        idx = c - min_c
        g2_dense[idx] = g2_cond_counts[c]
        mf_dense[idx] = mf_levels[c]

    # Check: what fraction of shared values are at primes?
    prime_shared = [c for c in shared if isprime(c)]
    frac_prime = len(prime_shared) / len(shared)
    print(f"  {len(prime_shared)}/{len(shared)} shared values are prime ({frac_prime:.1%})")

    # Detrend: subtract local mean (window=50) from each signal
    window = 50
    from scipy.ndimage import uniform_filter1d
    g2_trend = uniform_filter1d(g2_dense.astype(float), window)
    mf_trend = uniform_filter1d(mf_dense.astype(float), window)
    g2_resid = g2_dense - g2_trend
    mf_resid = mf_dense - mf_trend

    nperseg = min(256, n_pts // 4)
    if nperseg < 16:
        nperseg = min(16, n_pts)

    _, Cxy_detrend = signal.coherence(g2_resid, mf_resid, nperseg=nperseg)
    peak_detrend = float(np.max(Cxy_detrend))
    mean_detrend = float(np.nanmean(Cxy_detrend))

    # Null on detrended
    rng = np.random.default_rng(77)
    null_peaks = []
    for _ in range(200):
        shuf = mf_resid.copy()
        rng.shuffle(shuf)
        _, C_null = signal.coherence(g2_resid, shuf, nperseg=nperseg)
        null_peaks.append(float(np.max(C_null)))

    null_mean = float(np.mean(null_peaks))
    null_std = float(np.std(null_peaks))
    z_detrend = (peak_detrend - null_mean) / null_std if null_std > 0 else 0.0

    print(f"  Detrended peak coherence: {peak_detrend:.4f}, null: {null_mean:.4f}+/-{null_std:.4f}, z={z_detrend:.2f}")

    return {
        "fraction_prime_shared": round(frac_prime, 4),
        "n_prime_shared": len(prime_shared),
        "detrended_peak_coherence": round(peak_detrend, 6),
        "detrended_mean_coherence": round(mean_detrend, 6),
        "detrended_null_mean": round(null_mean, 6),
        "detrended_null_std": round(null_std, 6),
        "detrended_z_score": round(z_detrend, 4),
    }


def main():
    print("=" * 60)
    print("Igusa Invariant <-> Modular Level Fourier Leakage")
    print("=" * 60)

    # Step 1: Load data
    g2_records = load_genus2_igusa()
    g2_cond_counts = load_genus2_conductors()
    mf_levels = load_mf_levels()

    # Step 2: Aggregate Igusa by conductor
    igusa_agg = aggregate_igusa_by_conductor(g2_records)

    # Step 3: Match and correlate
    print("\n--- Pearson/Spearman correlations (Igusa vs MF count) ---")
    corr_result = match_and_correlate(igusa_agg, mf_levels)
    if corr_result is None:
        print("FATAL: not enough shared conductors")
        return

    corr_stats, shared, g2_I2, mf_cnt = corr_result

    # Step 4: Log-normalized correlations
    print("\n--- Log-normalized correlations ---")
    log_results = log_normalized_analysis(igusa_agg, mf_levels, shared, g2_I2, mf_cnt)

    # Step 5: Cross-spectral density (Igusa I2 vs MF count)
    print("\n--- Cross-spectral density (I2 vs MF count) ---")
    spectral_igusa = cross_spectral_analysis(shared, g2_I2, mf_cnt)

    # Step 6: Conductor-count cross-spectral (full 66K dataset)
    print("\n--- Conductor-count cross-spectral (full 66K genus-2) ---")
    cond_spectral = conductor_count_spectral(g2_cond_counts, mf_levels)

    # Step 7: Also do spectral for I4, I6, I10
    spectral_by_invariant = {}
    for inv_name in ["I4", "I6", "I10"]:
        arr = np.array([igusa_agg[c][f"mean_{inv_name}"] for c in shared])
        print(f"\n--- Cross-spectral density ({inv_name} vs MF count) ---")
        spectral_by_invariant[inv_name] = cross_spectral_analysis(shared, arr, mf_cnt)

    # ── Assemble results ──
    final = {
        "challenge": "Igusa Invariant <-> Modular Level Fourier Leakage (ChatGPT New#6)",
        "data_sources": {
            "genus2_igusa": str(GENUS2_API),
            "genus2_full": str(GENUS2_FULL),
            "modular_forms": str(CHARON_DB),
        },
        "genus2_igusa_curves": len(g2_records),
        "genus2_full_conductors": len(g2_cond_counts),
        "mf_levels": len(mf_levels),
        "n_shared_igusa_mf": corr_stats["n_shared"],
        "correlations": corr_stats,
        "log_normalized_correlations": log_results,
        "spectral_I2_vs_mf": spectral_igusa,
        "spectral_I4_vs_mf": spectral_by_invariant.get("I4"),
        "spectral_I6_vs_mf": spectral_by_invariant.get("I6"),
        "spectral_I10_vs_mf": spectral_by_invariant.get("I10"),
        "conductor_count_spectral": cond_spectral,
        "interpretation": "",
    }

    # ── Interpret ──
    peak_I2 = spectral_igusa.get("peak_coherence", 0)
    z_I2 = spectral_igusa.get("z_score_vs_null", 0)
    peak_cond = cond_spectral.get("peak_coherence", 0)
    z_cond = cond_spectral.get("z_score", 0)

    lines = []
    lines.append(f"Peak coherence (I2 vs MF count): {peak_I2:.4f}, z={z_I2:.2f}")
    lines.append(f"Peak coherence (conductor-count): {peak_cond:.4f}, z={z_cond:.2f}")

    if z_I2 > 3:
        lines.append("Igusa I2 shows significant spectral leakage to MF levels.")
    elif z_I2 > 2:
        lines.append("Igusa I2 shows marginal spectral leakage.")
    else:
        lines.append("No significant spectral leakage from Igusa I2 to MF levels.")

    # Check all invariant z-scores
    for inv in ["I4", "I6", "I10"]:
        sp = spectral_by_invariant.get(inv, {})
        z = sp.get("z_score_vs_null", 0)
        pk = sp.get("peak_coherence", 0)
        lines.append(f"{inv}: peak_coh={pk:.4f}, z={z:.2f}")

    final["interpretation"] = "\n".join(lines)

    # ── Prime detrending sanity check ──
    print("\n--- Prime detrending check ---")
    prime_check = prime_detrend_check(g2_cond_counts, mf_levels)
    final["prime_detrending"] = prime_check

    # Save
    with open(OUT_JSON, "w") as f:
        json.dump(final, f, indent=2, default=str)
    print(f"\n[saved] {OUT_JSON}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for line in lines:
        print(f"  {line}")
    if prime_check:
        print(f"  Prime-detrended conductor-count coherence: peak={prime_check.get('detrended_peak_coherence', 'N/A')}, z={prime_check.get('detrended_z_score', 'N/A')}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Synthetic null test: does the zero-spacing vs isogeny-class-size signal
come from the DATA or from the PIPELINE?

M2 finding: rho(gamma_2 - gamma_1, class_size) = +0.134, p=10^-123, z=-29
after conductor matching. Scaling ~ N^(-0.464).

This script generates synthetic GUE zeros, preserves the conductor/class_size
structure, and checks whether the pipeline alone can create the signal.

If synthetic GUE zeros + real class_size structure produce rho ~ 0:
    => The signal is GENUINE arithmetic structure in the L-function zeros.
If synthetic GUE zeros reproduce rho ~ 0.134:
    => The signal is a PIPELINE ARTIFACT (conductor confound, etc.)
"""

import json
import sys
import time
from pathlib import Path

import duckdb
import numpy as np
from scipy import stats

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[3]  # cartography/shared/scripts -> repo root
DB_PATH = REPO_ROOT / "charon" / "data" / "charon.duckdb"
OUT_DIR = REPO_ROOT / "cartography" / "convergence" / "data"
OUT_PATH = OUT_DIR / "synthetic_null_spectral_results.json"
N_TRIALS = 100
N_CONDUCTOR_BINS = 50
RNG_SEED = 42

# ---------------------------------------------------------------------------
# GUE / Wigner surmise utilities
# ---------------------------------------------------------------------------

def wigner_surmise_sample(n, rng):
    """
    Sample n spacings from the GUE Wigner surmise:
        P(s) = (pi*s/2) * exp(-pi*s^2/4)

    Uses inverse CDF: F(s) = 1 - exp(-pi*s^2/4)
        => s = sqrt(-4*ln(1-u)/pi)
    """
    u = rng.uniform(0, 1, size=n)
    # Clamp to avoid log(0)
    u = np.clip(u, 1e-15, 1 - 1e-15)
    s = np.sqrt(-4.0 * np.log(1.0 - u) / np.pi)
    return s


def generate_synthetic_zeros(n_zeros, real_zeros, rng):
    """
    Generate synthetic zeros for one curve:
    - n_zeros spacings from Wigner surmise
    - Cumulative sum to get positions
    - Scale to match the mean density of the real zeros

    Returns array of n_zeros synthetic zero positions.
    """
    if n_zeros < 2:
        return real_zeros[:n_zeros]  # Can't do much with 0 or 1 zeros

    # Generate spacings from Wigner surmise
    spacings = wigner_surmise_sample(n_zeros - 1, rng)

    # The mean of the Wigner surmise is sqrt(pi)/2 ~ 0.886
    # Scale spacings so the total range matches the real zeros' range
    real_range = real_zeros[-1] - real_zeros[0]
    synthetic_cumsum = np.cumsum(spacings)

    if synthetic_cumsum[-1] > 0:
        scale = real_range / synthetic_cumsum[-1]
    else:
        scale = 1.0

    synthetic = np.zeros(n_zeros)
    synthetic[0] = real_zeros[0]  # Start at the same first zero
    synthetic[1:] = real_zeros[0] + synthetic_cumsum * scale

    return synthetic


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_data():
    """Load EC data with zeros from charon.duckdb."""
    con = duckdb.connect(str(DB_PATH), read_only=True)

    rows = con.sql("""
        SELECT e.conductor, e.rank, e.class_size, e.class_deg,
               o.zeros_vector, o.n_zeros_stored
        FROM elliptic_curves e
        JOIN object_zeros o ON e.object_id = o.object_id
        WHERE o.zeros_vector IS NOT NULL
          AND e.class_size IS NOT NULL
          AND o.n_zeros_stored >= 2
    """).fetchall()
    con.close()

    conductors = []
    ranks = []
    class_sizes = []
    class_degs = []
    all_zeros = []
    spacings = []

    for row in rows:
        cond, rank, cs, cd, zv, nz = row
        # Extract actual zeros (first min(nz, 20) entries, skip Nones)
        n_actual = min(nz, 20)
        zeros = [z for z in zv[:n_actual] if z is not None]

        if len(zeros) < 2:
            continue

        zeros = np.array(zeros, dtype=np.float64)
        spacing = zeros[1] - zeros[0]  # gamma_2 - gamma_1

        conductors.append(cond)
        ranks.append(rank if rank is not None else 0)
        class_sizes.append(cs)
        class_degs.append(cd if cd is not None else 0)
        all_zeros.append(zeros)
        spacings.append(spacing)

    return {
        'conductors': np.array(conductors),
        'ranks': np.array(ranks),
        'class_sizes': np.array(class_sizes),
        'class_degs': np.array(class_degs),
        'all_zeros': all_zeros,
        'spacings': np.array(spacings),
    }


# ---------------------------------------------------------------------------
# Core test functions
# ---------------------------------------------------------------------------

def compute_rho(x, y):
    """Spearman rho with p-value."""
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 10:
        return 0.0, 1.0
    r, p = stats.spearmanr(x[mask], y[mask])
    return float(r), float(p)


def run_synthetic_trial(data, rng, method='shuffle'):
    """
    One synthetic trial.

    method:
        'shuffle'   - real class_sizes randomly reassigned to synthetic zeros
        'preserved' - real class_size assignments kept, zeros replaced with GUE
        'conductor_correlated' - class_sizes assigned by conductor rank (preserving
                                 conductor-class_size correlation but not zero coupling)

    Returns rho(synthetic_spacing, class_size).
    """
    n = len(data['all_zeros'])

    # Generate synthetic zeros for each curve
    synthetic_spacings = np.zeros(n)
    for i in range(n):
        real_z = data['all_zeros'][i]
        syn_z = generate_synthetic_zeros(len(real_z), real_z, rng)
        synthetic_spacings[i] = syn_z[1] - syn_z[0]

    if method == 'shuffle':
        cs = rng.permutation(data['class_sizes'])
    elif method == 'preserved':
        cs = data['class_sizes']
    elif method == 'conductor_correlated':
        # Assign class sizes by conductor rank to preserve conductor-class_size
        # correlation structure, but break any zero coupling
        cond_order = np.argsort(data['conductors'])
        cs_sorted_by_cond = data['class_sizes'][np.argsort(data['conductors'])]
        # Now shuffle within small conductor windows to add noise
        # but keep the broad correlation
        cs = np.empty_like(data['class_sizes'])
        cs[cond_order] = cs_sorted_by_cond
        # Add jitter: shuffle within blocks of 100
        block = 100
        for start in range(0, n, block):
            end = min(start + block, n)
            idx = cond_order[start:end]
            cs[idx] = rng.permutation(cs[idx])
    else:
        raise ValueError(f"Unknown method: {method}")

    rho, p = compute_rho(synthetic_spacings, cs.astype(float))
    return rho, p


def run_real_shuffled_trial(data, rng):
    """
    REAL zeros with SHUFFLED class sizes.
    The most basic null: if shuffling kills the signal, the coupling is genuine.
    """
    cs = rng.permutation(data['class_sizes'])
    rho, p = compute_rho(data['spacings'], cs.astype(float))
    return rho, p


def run_conductor_binned_test(data, n_bins=50):
    """
    Within each conductor bin, compute rho(spacing, class_size).
    Tests whether the signal persists within tight conductor windows.
    """
    conds = data['conductors']
    spacings = data['spacings']
    cs = data['class_sizes'].astype(float)

    # Create conductor bins using quantiles for equal-count bins
    bin_edges = np.percentile(conds, np.linspace(0, 100, n_bins + 1))
    bin_edges[-1] += 1  # Include the max

    bin_results = []
    for i in range(n_bins):
        mask = (conds >= bin_edges[i]) & (conds < bin_edges[i + 1])
        n_in_bin = mask.sum()
        if n_in_bin < 20:
            continue

        rho, p = compute_rho(spacings[mask], cs[mask])
        bin_results.append({
            'bin': i,
            'cond_lo': float(bin_edges[i]),
            'cond_hi': float(bin_edges[i + 1]),
            'n': int(n_in_bin),
            'rho': rho,
            'p': p,
        })

    return bin_results


def run_conductor_binned_synthetic(data, rng, n_bins=50):
    """
    Generate synthetics within each conductor bin separately.
    Tests whether conductor confounding within bins can create the signal.
    """
    conds = data['conductors']
    cs = data['class_sizes'].astype(float)

    bin_edges = np.percentile(conds, np.linspace(0, 100, n_bins + 1))
    bin_edges[-1] += 1

    all_syn_spacings = np.full(len(data['all_zeros']), np.nan)

    for i in range(n_bins):
        mask = (conds >= bin_edges[i]) & (conds < bin_edges[i + 1])
        indices = np.where(mask)[0]
        if len(indices) < 2:
            continue

        for idx in indices:
            real_z = data['all_zeros'][idx]
            syn_z = generate_synthetic_zeros(len(real_z), real_z, rng)
            all_syn_spacings[idx] = syn_z[1] - syn_z[0]

    valid = np.isfinite(all_syn_spacings)
    rho, p = compute_rho(all_syn_spacings[valid], cs[valid])
    return rho, p


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("SYNTHETIC NULL SPECTRAL TEST")
    print("Does zero-spacing vs class_size signal come from DATA or PIPELINE?")
    print("=" * 70)

    t0 = time.time()
    rng = np.random.default_rng(RNG_SEED)

    # ---- Load data ----
    print("\n[1] Loading data from charon.duckdb...")
    data = load_data()
    n = len(data['spacings'])
    print(f"    Loaded {n} curves with zeros and class_size")

    # ---- Real signal ----
    print("\n[2] Computing REAL signal...")
    real_rho, real_p = compute_rho(data['spacings'], data['class_sizes'].astype(float))
    print(f"    REAL rho(spacing, class_size) = {real_rho:.6f}")
    print(f"    REAL p-value = {real_p:.2e}")

    # ---- Conductor-class_size correlation ----
    cond_cs_rho, cond_cs_p = compute_rho(
        data['conductors'].astype(float), data['class_sizes'].astype(float)
    )
    print(f"\n    Conductor-class_size rho = {cond_cs_rho:.6f} (p={cond_cs_p:.2e})")

    cond_sp_rho, cond_sp_p = compute_rho(
        data['conductors'].astype(float), data['spacings']
    )
    print(f"    Conductor-spacing rho     = {cond_sp_rho:.6f} (p={cond_sp_p:.2e})")

    # ---- Synthetic trials ----
    results = {
        'real_signal': {'rho': real_rho, 'p': real_p, 'n': n},
        'confound_correlations': {
            'conductor_class_size_rho': cond_cs_rho,
            'conductor_spacing_rho': cond_sp_rho,
        },
        'synthetic_trials': {},
        'real_shuffled_trials': {},
        'conductor_binned': {},
        'metadata': {
            'n_trials': N_TRIALS,
            'n_curves': n,
            'n_conductor_bins': N_CONDUCTOR_BINS,
            'rng_seed': RNG_SEED,
            'db_path': str(DB_PATH),
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
        }
    }

    # ---- Test A: Synthetic GUE zeros + shuffled class sizes ----
    print(f"\n[3] Running {N_TRIALS} synthetic trials (GUE + shuffled class_size)...")
    rhos_shuffle = []
    for t in range(N_TRIALS):
        r, p = run_synthetic_trial(data, rng, method='shuffle')
        rhos_shuffle.append(r)
        if (t + 1) % 25 == 0:
            print(f"    ... {t+1}/{N_TRIALS}")

    results['synthetic_trials']['gue_shuffled'] = {
        'rhos': rhos_shuffle,
        'mean': float(np.mean(rhos_shuffle)),
        'std': float(np.std(rhos_shuffle)),
        'z_vs_real': float((real_rho - np.mean(rhos_shuffle)) / max(np.std(rhos_shuffle), 1e-10)),
    }
    print(f"    mean rho = {np.mean(rhos_shuffle):.6f} +/- {np.std(rhos_shuffle):.6f}")
    print(f"    z-score of real vs synthetic = {results['synthetic_trials']['gue_shuffled']['z_vs_real']:.1f}")

    # ---- Test B: Synthetic GUE zeros + PRESERVED class sizes ----
    print(f"\n[4] Running {N_TRIALS} synthetic trials (GUE + preserved class_size)...")
    rhos_preserved = []
    for t in range(N_TRIALS):
        r, p = run_synthetic_trial(data, rng, method='preserved')
        rhos_preserved.append(r)
        if (t + 1) % 25 == 0:
            print(f"    ... {t+1}/{N_TRIALS}")

    results['synthetic_trials']['gue_preserved'] = {
        'rhos': rhos_preserved,
        'mean': float(np.mean(rhos_preserved)),
        'std': float(np.std(rhos_preserved)),
        'z_vs_real': float((real_rho - np.mean(rhos_preserved)) / max(np.std(rhos_preserved), 1e-10)),
    }
    print(f"    mean rho = {np.mean(rhos_preserved):.6f} +/- {np.std(rhos_preserved):.6f}")
    print(f"    z-score of real vs synthetic = {results['synthetic_trials']['gue_preserved']['z_vs_real']:.1f}")

    # ---- Test C: Synthetic GUE + conductor-correlated class sizes ----
    print(f"\n[5] Running {N_TRIALS} synthetic trials (GUE + conductor-correlated class_size)...")
    rhos_condcorr = []
    for t in range(N_TRIALS):
        r, p = run_synthetic_trial(data, rng, method='conductor_correlated')
        rhos_condcorr.append(r)
        if (t + 1) % 25 == 0:
            print(f"    ... {t+1}/{N_TRIALS}")

    results['synthetic_trials']['gue_conductor_correlated'] = {
        'rhos': rhos_condcorr,
        'mean': float(np.mean(rhos_condcorr)),
        'std': float(np.std(rhos_condcorr)),
        'z_vs_real': float((real_rho - np.mean(rhos_condcorr)) / max(np.std(rhos_condcorr), 1e-10)),
    }
    print(f"    mean rho = {np.mean(rhos_condcorr):.6f} +/- {np.std(rhos_condcorr):.6f}")
    print(f"    z-score of real vs synthetic = {results['synthetic_trials']['gue_conductor_correlated']['z_vs_real']:.1f}")

    # ---- Test D: REAL zeros + SHUFFLED class sizes ----
    print(f"\n[6] Running {N_TRIALS} trials: REAL zeros + SHUFFLED class_size...")
    rhos_real_shuf = []
    for t in range(N_TRIALS):
        r, p = run_real_shuffled_trial(data, rng)
        rhos_real_shuf.append(r)
        if (t + 1) % 25 == 0:
            print(f"    ... {t+1}/{N_TRIALS}")

    results['real_shuffled_trials'] = {
        'rhos': rhos_real_shuf,
        'mean': float(np.mean(rhos_real_shuf)),
        'std': float(np.std(rhos_real_shuf)),
        'z_vs_real': float((real_rho - np.mean(rhos_real_shuf)) / max(np.std(rhos_real_shuf), 1e-10)),
    }
    print(f"    mean rho = {np.mean(rhos_real_shuf):.6f} +/- {np.std(rhos_real_shuf):.6f}")
    print(f"    z-score of real vs shuffled = {results['real_shuffled_trials']['z_vs_real']:.1f}")

    # ---- Test E: Conductor-binned real signal ----
    print(f"\n[7] Conductor-binned test ({N_CONDUCTOR_BINS} bins)...")
    bin_results = run_conductor_binned_test(data, n_bins=N_CONDUCTOR_BINS)

    positive_bins = sum(1 for b in bin_results if b['rho'] > 0)
    sig_bins = sum(1 for b in bin_results if b['p'] < 0.05)
    mean_bin_rho = np.mean([b['rho'] for b in bin_results]) if bin_results else 0

    results['conductor_binned']['real'] = {
        'bins': bin_results,
        'n_bins_computed': len(bin_results),
        'n_positive': positive_bins,
        'n_significant_p05': sig_bins,
        'mean_rho': float(mean_bin_rho),
    }
    print(f"    {len(bin_results)} bins computed")
    print(f"    {positive_bins}/{len(bin_results)} bins have positive rho")
    print(f"    {sig_bins}/{len(bin_results)} bins significant at p<0.05")
    print(f"    mean within-bin rho = {mean_bin_rho:.6f}")

    # ---- Test F: Conductor-binned synthetic ----
    print(f"\n[8] Conductor-binned synthetic ({N_TRIALS} trials)...")
    rhos_binned_syn = []
    for t in range(N_TRIALS):
        r, p = run_conductor_binned_synthetic(data, rng, n_bins=N_CONDUCTOR_BINS)
        rhos_binned_syn.append(r)
        if (t + 1) % 25 == 0:
            print(f"    ... {t+1}/{N_TRIALS}")

    results['conductor_binned']['synthetic'] = {
        'rhos': rhos_binned_syn,
        'mean': float(np.mean(rhos_binned_syn)),
        'std': float(np.std(rhos_binned_syn)),
        'z_vs_real_binned': float(
            (mean_bin_rho - np.mean(rhos_binned_syn)) / max(np.std(rhos_binned_syn), 1e-10)
        ),
    }
    print(f"    mean synthetic rho = {np.mean(rhos_binned_syn):.6f} +/- {np.std(rhos_binned_syn):.6f}")

    # ---- Summary ----
    elapsed = time.time() - t0
    results['metadata']['elapsed_seconds'] = round(elapsed, 1)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Real signal:           rho = {real_rho:.6f}")
    print(f"  GUE + shuffled:        rho = {np.mean(rhos_shuffle):.6f} +/- {np.std(rhos_shuffle):.6f}  "
          f"(z = {results['synthetic_trials']['gue_shuffled']['z_vs_real']:.1f})")
    print(f"  GUE + preserved:       rho = {np.mean(rhos_preserved):.6f} +/- {np.std(rhos_preserved):.6f}  "
          f"(z = {results['synthetic_trials']['gue_preserved']['z_vs_real']:.1f})")
    print(f"  GUE + cond-correlated: rho = {np.mean(rhos_condcorr):.6f} +/- {np.std(rhos_condcorr):.6f}  "
          f"(z = {results['synthetic_trials']['gue_conductor_correlated']['z_vs_real']:.1f})")
    print(f"  Real + shuffled:       rho = {np.mean(rhos_real_shuf):.6f} +/- {np.std(rhos_real_shuf):.6f}  "
          f"(z = {results['real_shuffled_trials']['z_vs_real']:.1f})")
    print(f"  Within-bin real:       rho = {mean_bin_rho:.6f}  "
          f"({positive_bins}/{len(bin_results)} positive, {sig_bins} sig)")
    print(f"  Within-bin synthetic:  rho = {np.mean(rhos_binned_syn):.6f} +/- {np.std(rhos_binned_syn):.6f}")

    # Interpretation
    print("\n" + "-" * 70)

    # Key diagnostic: does GUE + preserved produce signal?
    gue_preserved_z = abs(results['synthetic_trials']['gue_preserved']['z_vs_real'])
    real_shuf_z = abs(results['real_shuffled_trials']['z_vs_real'])

    if gue_preserved_z > 3 and real_shuf_z > 3:
        verdict = "GENUINE: Signal requires BOTH real zeros AND real class_size assignments."
        results['verdict'] = 'GENUINE'
    elif gue_preserved_z < 3:
        verdict = "ARTIFACT: GUE zeros with preserved labels reproduce the signal. Pipeline creates it."
        results['verdict'] = 'ARTIFACT'
    elif real_shuf_z < 3:
        verdict = "MARGINAL: Shuffling doesn't fully kill the signal. Possible confound."
        results['verdict'] = 'MARGINAL'
    else:
        verdict = "INCONCLUSIVE: Mixed evidence."
        results['verdict'] = 'INCONCLUSIVE'

    print(f"  VERDICT: {verdict}")
    print(f"  Elapsed: {elapsed:.1f}s")
    print("=" * 70)

    # ---- Save results ----
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {OUT_PATH}")

    return results


if __name__ == '__main__':
    main()

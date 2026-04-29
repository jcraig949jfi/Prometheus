"""
Missingness-confound diagnostic v0.1
=====================================

A FALSIFIER for tensor rank estimates, NOT a rank estimator.

Quantifies how much of any rank-flavored claim about the (features x projections)
tensor is attributable to the MNAR observation pattern alone, by comparing the
observed effective-rank against three null distributions of increasing strictness.

Per the Geometry-1 retraction (2026-04-19): the original SVD/SVT estimates
of "latent rank ~12-16" were not defensible because the most-loaded columns
were also the most-tested columns, and the MNAR + 0-as-missing structure
violates SVT's assumptions. This tool does NOT remediate that. It makes
the retraction quantitative.

Design history: harmonia/memory/protocols/missingness_confound_proposal.md
Author: Harmonia_M2_sessionB
Audit: Harmonia_M2_auditor (CONCUR_WITH_NOTES 1777461099984-0; 4 refinements applied)

CAVEATS (must accompany every output):
  - Effective-rank from observed-only correlations is a DIAGNOSTIC number,
    not a structural claim. Promotion of any rank claim requires controlled
    (F,P) sampling protocol per the retraction's branch (b), which this tool
    does NOT provide.
  - 0 in tensor encodes "not observed", not "observed-as-zero".
  - The four nulls are not exhaustive. New nulls may show structure these miss.
  - Pass on this diagnostic does NOT mean "the tensor has rank N." It means
    "an effective-rank claim X about this tensor survives these three nulls."
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Phi: effective-rank from PSD-clamped observed-only correlation matrix
# ---------------------------------------------------------------------------

def pairwise_complete_corr_psd(
    T: np.ndarray, M: np.ndarray, min_overlap: int = 5
) -> Tuple[np.ndarray, np.ndarray, int]:
    """Pairwise-complete column-correlation matrix, PSD-clamped.

    Returns (C_psd, eigenvalues, n_undefined_pairs).

    Refinement 1 (auditor): clamp negative eigenvalues to 0 to prevent
    spurious effective-rank inflation from non-PSD pairwise-complete matrices.
    Refinement 2 (auditor): default min_overlap=5 (was 3 in proposal).
    """
    P = T.shape[1]
    C = np.full((P, P), np.nan)
    n_undefined = 0
    for i in range(P):
        for j in range(i, P):
            mask = (M[:, i].astype(bool)) & (M[:, j].astype(bool))
            n = int(mask.sum())
            if n < min_overlap:
                if i != j:
                    n_undefined += 1
                continue
            xi = T[mask, i].astype(float)
            xj = T[mask, j].astype(float)
            sxi = xi.std()
            sxj = xj.std()
            if sxi == 0 or sxj == 0:
                C[i, j] = C[j, i] = 0.0
                continue
            c = float(((xi - xi.mean()) * (xj - xj.mean())).mean() / (sxi * sxj))
            C[i, j] = C[j, i] = c
    # Fill undefined pairs with 0 (no information)
    C = np.where(np.isnan(C), 0.0, C)
    np.fill_diagonal(C, 1.0)
    # PSD clamp via eigendecomposition
    w, V = np.linalg.eigh(C)
    w_clamped = np.clip(w, 0.0, None)
    C_psd = V @ np.diag(w_clamped) @ V.T
    return C_psd, w_clamped, n_undefined


def effective_rank(eigenvalues: np.ndarray) -> float:
    """Shannon-entropy effective rank: erank(C) = exp(H(p)), p_i = lambda_i / sum lambda."""
    w = eigenvalues[eigenvalues > 1e-12]
    if len(w) == 0:
        return 0.0
    p = w / w.sum()
    H = -np.sum(p * np.log(p))
    return float(np.exp(H))


def phi(T: np.ndarray, M: np.ndarray, min_overlap: int = 5) -> float:
    _, w, _ = pairwise_complete_corr_psd(T, M, min_overlap)
    return effective_rank(w)


# ---------------------------------------------------------------------------
# Null generators
# ---------------------------------------------------------------------------

def null_random(T: np.ndarray, M: np.ndarray, rng: np.random.Generator
                ) -> Tuple[np.ndarray, np.ndarray]:
    """Coarsest null: scramble both M's pattern AND the value-position binding.

    Re-samples observation positions uniformly across the full grid, places the
    permuted observed values into them. Both row and col marginals broken.
    """
    F, P = T.shape
    n_obs = int(M.sum())
    values = T[M.astype(bool)].copy()
    rng.shuffle(values)
    flat = np.zeros(F * P, dtype=T.dtype)
    positions = rng.choice(F * P, size=n_obs, replace=False)
    flat[positions] = values
    T_new = flat.reshape(F, P)
    M_new = (T_new != 0).astype(np.int8)
    return T_new, M_new


def null_marginal_preserving(
    T: np.ndarray, M: np.ndarray, rng: np.random.Generator, n_swaps: int = 2000
) -> Tuple[np.ndarray, np.ndarray]:
    """Middle null: preserve row and col marginals of M; break the joint.

    Uses Curveball-style swap (degree-preserving): repeatedly pick two rows;
    among cells where one has obs and the other does not in different columns,
    swap a pair. Preserves both marginals exactly.

    Then permutes the observed values across the new observation positions.
    """
    M_new = M.copy().astype(bool)
    F, P = M_new.shape
    for _ in range(n_swaps):
        r1, r2 = rng.choice(F, size=2, replace=False)
        # Cells observed in r1-but-not-r2 and r2-but-not-r1
        d12 = np.where(M_new[r1] & ~M_new[r2])[0]
        d21 = np.where(M_new[r2] & ~M_new[r1])[0]
        if len(d12) == 0 or len(d21) == 0:
            continue
        c1 = rng.choice(d12)
        c2 = rng.choice(d21)
        # Swap: r1 loses c1 / gains c2; r2 gains c1 / loses c2
        M_new[r1, c1] = False
        M_new[r1, c2] = True
        M_new[r2, c1] = True
        M_new[r2, c2] = False
    # Now place permuted values into the new pattern
    values = T[M.astype(bool)].copy()
    rng.shuffle(values)
    T_new = np.zeros_like(T)
    obs_positions = np.argwhere(M_new)
    if len(obs_positions) != len(values):
        # Sanity: marginal-preserving swap should preserve obs count
        raise RuntimeError(
            'observation count drifted: expected {}, got {}'.format(
                len(values), len(obs_positions)))
    for (i, j), v in zip(obs_positions, values):
        T_new[i, j] = v
    return T_new, M_new.astype(np.int8)


def null_within_rows(T: np.ndarray, M: np.ndarray, rng: np.random.Generator
                     ) -> Tuple[np.ndarray, np.ndarray]:
    """Strictest null A: keep M exactly, permute values within each row."""
    T_new = T.copy()
    for i in range(T.shape[0]):
        cols = np.where(M[i].astype(bool))[0]
        if len(cols) > 1:
            permuted = rng.permutation(T[i, cols])
            T_new[i, cols] = permuted
    return T_new, M.copy()


def null_within_cols(T: np.ndarray, M: np.ndarray, rng: np.random.Generator
                     ) -> Tuple[np.ndarray, np.ndarray]:
    """Strictest null B: keep M exactly, permute values within each column."""
    T_new = T.copy()
    for j in range(T.shape[1]):
        rows = np.where(M[:, j].astype(bool))[0]
        if len(rows) > 1:
            permuted = rng.permutation(T[rows, j])
            T_new[rows, j] = permuted
    return T_new, M.copy()


# ---------------------------------------------------------------------------
# Diagnostic runner
# ---------------------------------------------------------------------------

NULL_GENERATORS = {
    'null_random':            null_random,
    'null_marginal':          null_marginal_preserving,
    'null_3a_within_rows':    null_within_rows,
    'null_3b_within_cols':    null_within_cols,
}


def run_null(name, T, M, n_perms, rng, min_overlap):
    gen = NULL_GENERATORS[name]
    samples = np.zeros(n_perms)
    for k in range(n_perms):
        T_n, M_n = gen(T, M, rng)
        samples[k] = phi(T_n, M_n, min_overlap)
    return float(samples.mean()), float(samples.std(ddof=1)), samples


def run_diagnostic(T, M, n_perms=1000, seed=0, min_overlap=5):
    rng = np.random.default_rng(seed)
    phi_obs = phi(T, M, min_overlap)
    results = {'phi_observed': phi_obs, 'nulls': {}}
    for name in NULL_GENERATORS:
        mean, sd, _ = run_null(name, T, M, n_perms, rng, min_overlap)
        gap = (phi_obs - mean) / sd if sd > 0 else float('nan')
        results['nulls'][name] = {
            'mean': mean,
            'sd': sd,
            'gap_sigma': gap,
        }
    return results


def evaluate_pass_criterion(results: dict) -> dict:
    """Refinement 3 (auditor): explicit ratio thresholds.

    Empirically (sessionB v0.1 run): all gaps are NEGATIVE — observed phi is
    LOWER than null means because real tensor has column-correlation structure
    (lower effective rank) while random/marginal nulls have weak correlations
    (closer to full rank). The expected-direction is signed; magnitudes are
    what matter for the ratio test.

    null_random's sigma is unstable (phi distribution collapses near full
    rank P), so the sigma-gap blows up. Use raw-phi gap as primary; sigma-gap
    as secondary diagnostic only.
    """
    phi_obs = results['phi_observed']

    def raw_gap(name):
        return abs(phi_obs - results['nulls'][name]['mean'])

    def sigma_gap(name):
        return abs(results['nulls'][name]['gap_sigma'])

    raw_random   = raw_gap('null_random')
    raw_marginal = raw_gap('null_marginal')
    raw_3a       = raw_gap('null_3a_within_rows')
    raw_3b       = raw_gap('null_3b_within_cols')
    # max() is the conservative choice for a falsifier: it produces the SMALLER
    # marginal/strictest ratio, making the pass test harder to clear. Auditor
    # flag (1777462332788) requested explicit confirmation of intent.
    raw_3 = max(raw_3a, raw_3b)

    ratio_rm_raw = raw_random / raw_marginal if raw_marginal > 1e-9 else float('inf')
    ratio_m3_raw = raw_marginal / raw_3 if raw_3 > 1e-9 else float('inf')

    return {
        'raw_phi_gap_random':   raw_random,
        'raw_phi_gap_marginal': raw_marginal,
        'raw_phi_gap_3a':       raw_3a,
        'raw_phi_gap_3b':       raw_3b,
        'sigma_gap_random':     sigma_gap('null_random'),
        'sigma_gap_marginal':   sigma_gap('null_marginal'),
        'sigma_gap_3a':         sigma_gap('null_3a_within_rows'),
        'sigma_gap_3b':         sigma_gap('null_3b_within_cols'),
        'ratio_random_over_marginal_raw':    ratio_rm_raw,
        'ratio_marginal_over_strictest_raw': ratio_m3_raw,
        'pass_random_over_marginal':         ratio_rm_raw >= 2.0,
        'pass_marginal_over_strictest':      ratio_m3_raw >= 1.5,
        'pass_overall':                      (ratio_rm_raw >= 2.0) and (ratio_m3_raw >= 1.5),
        'note':
            'pass_overall uses raw-phi gaps not sigma gaps. null_random sigma '
            'is unstable because its phi distribution collapses near full rank P; '
            'use raw-phi-units for cross-null comparison.',
    }


CAVEATS = [
    'Effective-rank is a diagnostic number, NOT a latent-rank estimator.',
    '0 in tensor encodes "not observed", not "observed-as-zero".',
    'Pairwise-complete correlation matrices are not guaranteed PSD; eigenvalues clamped to >= 0.',
    'The four nulls are not exhaustive. New nulls may detect structure these miss.',
    'Pass on this diagnostic does NOT mean "the tensor has rank N." It means an effective-rank '
    'claim about this tensor survives these specific four nulls.',
    'Promotion of any structural rank claim requires controlled (F,P) sampling per the '
    'Geometry-1 retraction branch (b); this tool does NOT remediate that retraction.',
]


def main(
    tensor_path: str = 'harmonia/memory/landscape_tensor.npz',
    output_path: str = 'harmonia/memory/diagnostics/missingness_confound_v01_results.json',
    n_perms: int = 1000,
    seeds = (0, 1, 2, 3, 4),
    min_overlap: int = 5,
):
    d = np.load(tensor_path, allow_pickle=True)
    T = d['T']
    M = (T != 0).astype(np.int8)
    F, P = T.shape
    n_obs = int(M.sum())

    seed_results = []
    for seed in seeds:
        t0 = time.time()
        r = run_diagnostic(T, M, n_perms=n_perms, seed=seed, min_overlap=min_overlap)
        r['seed'] = int(seed)
        r['wall_clock_sec'] = round(time.time() - t0, 2)
        r['pass_criterion'] = evaluate_pass_criterion(r)
        seed_results.append(r)

    # Reproducibility check across seeds — both sigma-gap and raw-phi-gap.
    # Auditor flag (1777462332788) requested raw-gap-stability supplement
    # because null_random's sigma can be pathologically unstable while its
    # raw-phi gap is robust.
    sigma_gap_arrays = {
        name: np.array([r['nulls'][name]['gap_sigma'] for r in seed_results])
        for name in NULL_GENERATORS
    }
    raw_gap_arrays = {
        name: np.array([
            abs(r['phi_observed'] - r['nulls'][name]['mean']) for r in seed_results
        ])
        for name in NULL_GENERATORS
    }
    reproducibility = {
        name: {
            'sigma_gap_mean': float(sigma_gap_arrays[name].mean()),
            'sigma_gap_sd_across_seeds': float(sigma_gap_arrays[name].std(ddof=1)),
            'sigma_gap_within_0p2': bool(sigma_gap_arrays[name].std(ddof=1) <= 0.2),
            'raw_gap_mean': float(raw_gap_arrays[name].mean()),
            'raw_gap_sd_across_seeds': float(raw_gap_arrays[name].std(ddof=1)),
            'raw_gap_within_0p01_phi': bool(raw_gap_arrays[name].std(ddof=1) <= 0.01),
        }
        for name in NULL_GENERATORS
    }

    output = {
        'version': 'missingness_confound_diagnostic_v0.1',
        'generated_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'tensor': {
            'path': tensor_path,
            'shape': [int(F), int(P)],
            'n_observed': n_obs,
            'density': round(n_obs / (F * P), 4),
        },
        'parameters': {
            'n_perms_per_null_per_seed': n_perms,
            'seeds': list(seeds),
            'min_overlap_for_correlation': min_overlap,
            'phi': 'effective_rank_via_psd_clamped_pairwise_pearson',
            'pass_thresholds': {
                'ratio_random_over_marginal_min':    2.0,
                'ratio_marginal_over_strictest_min': 1.5,
                'reproducibility_sd_across_seeds_max': 0.2,
            },
        },
        'per_seed_results': seed_results,
        'reproducibility_across_seeds': reproducibility,
        'caveats': CAVEATS,
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    return output


if __name__ == '__main__':
    out = main()
    pc = out['per_seed_results'][0]['pass_criterion']
    print('phi_observed (seed 0):', out['per_seed_results'][0]['phi_observed'])
    for name, gd in out['reproducibility_across_seeds'].items():
        print('  {:<28s} raw_gap={:+.3f} +/-{:.4f} sigma_gap={:+.2f} sigma_stable={} raw_stable={}'.format(
            name, gd['raw_gap_mean'], gd['raw_gap_sd_across_seeds'],
            gd['sigma_gap_mean'], gd['sigma_gap_within_0p2'], gd['raw_gap_within_0p01_phi']))
    print()
    print('Pass criterion (seed 0):')
    for k, v in pc.items():
        print('  {:<35s} {}'.format(k, v))
    print()
    print('CAVEATS:')
    for c in CAVEATS:
        print('  -', c)

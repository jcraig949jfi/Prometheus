"""
Constrained Null Test -- THE falsification test for metabolism SVD finding.

The finding: stoichiometric matrices from 108 BiGG models have singular value
ratios matching mathematical constants at z=32 above random sparse matrices.

But random sparse matrices don't satisfy mass balance. Real metabolic matrices do.
This script tests whether the finding survives against CONSTRAINED null matrices
that respect the structural properties of real stoichiometric matrices.

Two tiers of constraint:
  Tier 1: Same dimensions, sparsity per column, integer coefficients, mass balance
  Tier 2: Same reactant/product COUNTS per reaction, only randomize WHICH metabolites

If z=32 drops to z<3 under constrained nulls, the finding is an artifact of
conservation-law structure. If it survives, it's real.
"""

import json
import os
import sys
import time
import numpy as np
from scipy.linalg import svdvals
from collections import Counter

# --- Constants ---------------------------------------------------------------

CONSTANTS = {
    "pi": 3.14159265,
    "e": 2.71828183,
    "phi": 1.61803399,
    "sqrt2": 1.41421356,
    "sqrt3": 1.73205081,
    "feigenbaum_d": 4.66920161,
    "feigenbaum_a": 2.50290788,
    "euler_mascheroni": 0.57721566,
    "catalan": 0.91596559,
    "apery": 1.20205690,
    "plastic": 1.32471796,
    "silver": 2.41421356,
    "pi_sq_6": 1.64493407,
    "ln2": 0.69314718,
    "pi_e": 1.15572735,
}

TOLERANCE = 0.005  # 0.5%
TOP_K = 20
N_TRIALS = 200
COEFF_POOL = np.array([-3, -2, -1, 1, 2, 3])

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
MODEL_PATH = os.path.join(DATA_DIR, "iML1515.json")
RESULTS_PATH = os.path.join(DATA_DIR, "constrained_null_results.json")


# --- Core functions ----------------------------------------------------------

def build_stoichiometric_matrix(model_data):
    """Build stoichiometric matrix from BiGG model JSON (dict format)."""
    reactions = model_data["reactions"]
    met_set = set()
    for rxn in reactions:
        for met_id in rxn["metabolites"]:
            met_set.add(met_id)
    met_list = sorted(met_set)
    met_idx = {m: i for i, m in enumerate(met_list)}

    n_mets = len(met_list)
    n_rxns = len(reactions)
    S = np.zeros((n_mets, n_rxns), dtype=np.float64)

    for j, rxn in enumerate(reactions):
        for met_id, coeff in rxn["metabolites"].items():
            S[met_idx[met_id], j] = float(coeff)

    return S, met_list, n_mets, n_rxns


def get_top_singular_values(matrix, top_k=TOP_K):
    """Compute top-k singular values using scipy.linalg.svdvals."""
    sv = svdvals(matrix)
    return sv[:top_k]


def count_constant_hits(sv):
    """Count how many pairwise ratios of singular values match constants."""
    hits = 0
    hit_details = []
    n = len(sv)
    for i in range(n):
        for j in range(n):
            if i == j or sv[j] == 0:
                continue
            ratio = sv[i] / sv[j]
            for name, val in CONSTANTS.items():
                if val == 0:
                    continue
                rel_err = abs(ratio - val) / val
                if rel_err < TOLERANCE:
                    hits += 1
                    hit_details.append({
                        "constant": name, "ratio": float(ratio),
                        "rel_error": float(rel_err), "i": i, "j": j,
                    })
    return hits, hit_details


def extract_column_structure(S):
    """Extract per-column structural info from real matrix.

    Returns:
        nnz_per_col: number of nonzeros per column
        neg_per_col: number of negative entries per column
        pos_per_col: number of positive entries per column
        coeff_distribution: global distribution of nonzero coefficients
    """
    n_mets, n_rxns = S.shape
    nnz_per_col = []
    neg_per_col = []
    pos_per_col = []
    all_coeffs = []

    for j in range(n_rxns):
        col = S[:, j]
        nz = col[col != 0]
        nnz_per_col.append(len(nz))
        neg_per_col.append(int(np.sum(nz < 0)))
        pos_per_col.append(int(np.sum(nz > 0)))
        all_coeffs.extend(nz.tolist())

    coeff_counts = Counter()
    for c in all_coeffs:
        coeff_counts[int(round(c))] += 1

    return nnz_per_col, neg_per_col, pos_per_col, coeff_counts


def build_coeff_weights(coeff_counts):
    """Build sampling weights for coefficients from real distribution."""
    neg_coeffs = []
    neg_weights = []
    pos_coeffs = []
    pos_weights = []
    for c, w in coeff_counts.items():
        if c < 0:
            neg_coeffs.append(c)
            neg_weights.append(w)
        elif c > 0:
            pos_coeffs.append(c)
            pos_weights.append(w)
    neg_coeffs = np.array(neg_coeffs)
    neg_weights = np.array(neg_weights, dtype=float)
    neg_weights /= neg_weights.sum()
    pos_coeffs = np.array(pos_coeffs)
    pos_weights = np.array(pos_weights, dtype=float)
    pos_weights /= pos_weights.sum()
    return neg_coeffs, neg_weights, pos_coeffs, pos_weights


# --- Null generators --------------------------------------------------------

def generate_tier1_null(n_mets, n_rxns, nnz_per_col, neg_coeffs, neg_weights,
                        pos_coeffs, pos_weights, rng):
    """Tier 1 constrained null: same dimensions, sparsity, mass-balanced columns.

    - Same number of nonzeros per column as real S
    - At least 1 positive and 1 negative per column (mass balance)
    - Coefficients drawn from real distribution
    - Random metabolite placement
    """
    S_null = np.zeros((n_mets, n_rxns), dtype=np.float64)

    for j in range(n_rxns):
        nnz = nnz_per_col[j]
        if nnz == 0:
            continue

        # Pick random metabolite rows
        rows = rng.choice(n_mets, size=nnz, replace=False)

        if nnz == 1:
            # Can't mass-balance a single entry; just assign random coeff
            S_null[rows[0], j] = rng.choice(COEFF_POOL)
        else:
            # Guarantee at least one negative and one positive
            n_neg = max(1, nnz // 2)  # roughly half negative
            n_pos = nnz - n_neg
            if n_pos < 1:
                n_neg = nnz - 1
                n_pos = 1

            # Sample coefficients from real distribution
            neg_vals = rng.choice(neg_coeffs, size=n_neg, p=neg_weights)
            pos_vals = rng.choice(pos_coeffs, size=n_pos, p=pos_weights)
            coeffs = np.concatenate([neg_vals, pos_vals])
            rng.shuffle(coeffs)

            for k, row in enumerate(rows):
                S_null[row, j] = coeffs[k]

    return S_null


def generate_tier2_null(n_mets, n_rxns, nnz_per_col, neg_per_col, pos_per_col,
                        neg_coeffs, neg_weights, pos_coeffs, pos_weights, rng):
    """Tier 2 constrained null (HARDER): preserve exact reactant/product counts.

    - Same number of negative entries (reactants) per column as real S
    - Same number of positive entries (products) per column as real S
    - Only randomize WHICH metabolites participate
    - Coefficients drawn from real distribution
    """
    S_null = np.zeros((n_mets, n_rxns), dtype=np.float64)

    for j in range(n_rxns):
        n_neg = neg_per_col[j]
        n_pos = pos_per_col[j]
        total = n_neg + n_pos
        if total == 0:
            continue

        # Pick random metabolite rows
        rows = rng.choice(n_mets, size=total, replace=False)

        # Assign negatives first, then positives
        if n_neg > 0:
            neg_vals = rng.choice(neg_coeffs, size=n_neg, p=neg_weights)
            for k in range(n_neg):
                S_null[rows[k], j] = neg_vals[k]
        if n_pos > 0:
            pos_vals = rng.choice(pos_coeffs, size=n_pos, p=pos_weights)
            for k in range(n_pos):
                S_null[rows[n_neg + k], j] = pos_vals[k]

    return S_null


# --- Main --------------------------------------------------------------------

def main():
    print("=" * 72)
    print("CONSTRAINED NULL TEST -- Metabolism SVD Falsification")
    print("=" * 72)

    # --- Load model ----------------------------------------------------------
    print("\nLoading %s ..." % MODEL_PATH)
    with open(MODEL_PATH) as f:
        model = json.load(f)

    S, met_list, n_mets, n_rxns = build_stoichiometric_matrix(model)
    print("  Stoichiometric matrix: %d metabolites x %d reactions" % (n_mets, n_rxns))
    nnz = np.count_nonzero(S)
    total = n_mets * n_rxns
    print("  Nonzeros: %d / %d (%.2f%% dense)" % (nnz, total, 100.0 * nnz / total))

    # --- Extract structural properties ---------------------------------------
    nnz_per_col, neg_per_col, pos_per_col, coeff_counts = extract_column_structure(S)
    neg_coeffs, neg_weights, pos_coeffs, pos_weights = build_coeff_weights(coeff_counts)

    print("\n  Coefficient distribution: %s" % dict(sorted(coeff_counts.items())))
    print("  Mean nonzeros/column: %.1f" % np.mean(nnz_per_col))
    print("  Mean neg/column: %.1f" % np.mean(neg_per_col))
    print("  Mean pos/column: %.1f" % np.mean(pos_per_col))

    # --- Real data hits ------------------------------------------------------
    print("\n-- Computing real SVD --")
    sv_real = get_top_singular_values(S)
    print("  Top 5 singular values: %s" % sv_real[:5])

    real_hits, real_details = count_constant_hits(sv_real)
    print("  Real constant hits: %d" % real_hits)
    if real_details:
        unique_constants = sorted(set(d["constant"] for d in real_details))
        print("  Constants matched: %s" % unique_constants)

    # --- Tier 1: Mass-balanced constrained null ------------------------------
    print("\n" + "=" * 72)
    print("TIER 1: Mass-balanced constrained null (%d trials)" % N_TRIALS)
    print("  Same sparsity per column, integer coeffs, mass balance")
    print("=" * 72)

    rng = np.random.default_rng(seed=42)
    tier1_hits = []
    t0 = time.time()

    for trial in range(N_TRIALS):
        S_null = generate_tier1_null(n_mets, n_rxns, nnz_per_col,
                                     neg_coeffs, neg_weights,
                                     pos_coeffs, pos_weights, rng)
        sv_null = get_top_singular_values(S_null)
        hits, _ = count_constant_hits(sv_null)
        tier1_hits.append(hits)

        if (trial + 1) % 50 == 0:
            elapsed = time.time() - t0
            rate = (trial + 1) / elapsed
            print("  Trial %d/%d  |  last hits=%d  mean=%.1f  max=%d  |  %.1f trials/sec"
                  % (trial + 1, N_TRIALS, hits, np.mean(tier1_hits),
                     np.max(tier1_hits), rate))

    tier1_hits = np.array(tier1_hits)
    tier1_mean = np.mean(tier1_hits)
    tier1_std = np.std(tier1_hits)
    if tier1_std > 0:
        tier1_z = (real_hits - tier1_mean) / tier1_std
    else:
        tier1_z = float("inf") if real_hits > tier1_mean else 0.0
    tier1_p = np.mean(tier1_hits >= real_hits)

    print("\n  Tier 1 Results:")
    print("    Real hits:        %d" % real_hits)
    print("    Null mean (std):  %.1f (%.2f)" % (tier1_mean, tier1_std))
    print("    Null max:         %d" % np.max(tier1_hits))
    print("    z-score:          %.2f" % tier1_z)
    print("    p-value:          %.4f" % tier1_p)
    if tier1_z >= 3:
        print("    VERDICT: SURVIVES Tier 1 (z=%.1f >= 3)" % tier1_z)
    else:
        print("    VERDICT: FAILS Tier 1 (z=%.1f < 3) -- finding is artifact" % tier1_z)

    # --- Tier 2: Structure-preserving null -----------------------------------
    print("\n" + "=" * 72)
    print("TIER 2: Structure-preserving constrained null (%d trials)" % N_TRIALS)
    print("  Same reactant/product COUNTS per reaction, randomize WHICH metabolites")
    print("=" * 72)

    tier2_hits = []
    t0 = time.time()

    for trial in range(N_TRIALS):
        S_null = generate_tier2_null(n_mets, n_rxns, nnz_per_col,
                                     neg_per_col, pos_per_col,
                                     neg_coeffs, neg_weights,
                                     pos_coeffs, pos_weights, rng)
        sv_null = get_top_singular_values(S_null)
        hits, _ = count_constant_hits(sv_null)
        tier2_hits.append(hits)

        if (trial + 1) % 50 == 0:
            elapsed = time.time() - t0
            rate = (trial + 1) / elapsed
            print("  Trial %d/%d  |  last hits=%d  mean=%.1f  max=%d  |  %.1f trials/sec"
                  % (trial + 1, N_TRIALS, hits, np.mean(tier2_hits),
                     np.max(tier2_hits), rate))

    tier2_hits = np.array(tier2_hits)
    tier2_mean = np.mean(tier2_hits)
    tier2_std = np.std(tier2_hits)
    if tier2_std > 0:
        tier2_z = (real_hits - tier2_mean) / tier2_std
    else:
        tier2_z = float("inf") if real_hits > tier2_mean else 0.0
    tier2_p = np.mean(tier2_hits >= real_hits)

    print("\n  Tier 2 Results:")
    print("    Real hits:        %d" % real_hits)
    print("    Null mean (std):  %.1f (%.2f)" % (tier2_mean, tier2_std))
    print("    Null max:         %d" % np.max(tier2_hits))
    print("    z-score:          %.2f" % tier2_z)
    print("    p-value:          %.4f" % tier2_p)
    if tier2_z >= 3:
        print("    VERDICT: SURVIVES Tier 2 (z=%.1f >= 3)" % tier2_z)
    else:
        print("    VERDICT: FAILS Tier 2 (z=%.1f < 3) -- finding is artifact" % tier2_z)

    # --- Summary -------------------------------------------------------------
    print("\n" + "=" * 72)
    print("FINAL SUMMARY")
    print("=" * 72)
    print("  Real constant hits:    %d" % real_hits)
    print("  Tier 1 null (mass-balanced):       mean=%.1f z=%.2f p=%.4f"
          % (tier1_mean, tier1_z, tier1_p))
    print("  Tier 2 null (structure-preserving): mean=%.1f z=%.2f p=%.4f"
          % (tier2_mean, tier2_z, tier2_p))

    if tier1_z >= 3 and tier2_z >= 3:
        print("\n  OVERALL: Finding SURVIVES both tiers. Not an artifact of mass-balance structure.")
    elif tier1_z < 3:
        print("\n  OVERALL: Finding FAILS Tier 1. Mass-balance structure alone explains the hits.")
    elif tier2_z < 3:
        print("\n  OVERALL: Finding survives Tier 1 (z=%.1f) but FAILS Tier 2 (z=%.1f)."
              % (tier1_z, tier2_z))
        print("  The specific reactant/product structure explains the constant matches.")
    print("=" * 72)

    # --- Save results --------------------------------------------------------
    results = {
        "model": "iML1515",
        "dimensions": {"metabolites": n_mets, "reactions": n_rxns},
        "nonzeros": int(np.count_nonzero(S)),
        "top_k": TOP_K,
        "tolerance": TOLERANCE,
        "n_constants": len(CONSTANTS),
        "n_trials": N_TRIALS,
        "real_hits": real_hits,
        "real_hit_details": real_details,
        "real_top5_sv": sv_real[:5].tolist(),
        "tier1": {
            "description": "Mass-balanced constrained null: same sparsity, integer coeffs, mass balance",
            "hits_distribution": tier1_hits.tolist(),
            "mean": float(tier1_mean),
            "std": float(tier1_std),
            "max": int(np.max(tier1_hits)),
            "z_score": float(tier1_z),
            "p_value": float(tier1_p),
            "survives": bool(tier1_z >= 3),
        },
        "tier2": {
            "description": "Structure-preserving null: same reactant/product counts, randomize which metabolites",
            "hits_distribution": tier2_hits.tolist(),
            "mean": float(tier2_mean),
            "std": float(tier2_std),
            "max": int(np.max(tier2_hits)),
            "z_score": float(tier2_z),
            "p_value": float(tier2_p),
            "survives": bool(tier2_z >= 3),
        },
        "coefficient_distribution": {str(k): v for k, v in sorted(coeff_counts.items())},
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print("\nResults saved to %s" % RESULTS_PATH)


if __name__ == "__main__":
    main()

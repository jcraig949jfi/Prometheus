#!/usr/bin/env python3
"""
OEIS-EC Transfer Entropy: Does knowing OEIS sequences help predict a_p?

Measure transfer entropy TE(OEIS -> EC) from OEIS integer sequences to
Hecke eigenvalues a_p of elliptic curves. Transfer entropy quantifies
the directed information flow: how much does knowing the past of an OEIS
sequence reduce uncertainty about the future of a_p.

Method:
  1. Sample 500 OEIS integer sequences (length >= 25) and 500 EC a_p lists
  2. Discretize both to mod-3 residues (maps to {0, 1, 2})
  3. For each pair, compute conditional mutual information:
       TE(OEIS->EC) = H(EC_t | EC_{t-1}) - H(EC_t | EC_{t-1}, OEIS_{t-1})
  4. Average TE across all 250K pairs
  5. Null: permuted OEIS sequences (destroys temporal structure)
  6. Report effect size (Cohen's d) and p-value

Data sources:
  - OEIS from cartography/oeis/data/stripped_new.txt
  - EC a_p from charon DuckDB (aplist column, 25 primes)

Output: cartography/v2/oeis_ec_transfer_entropy_results.json
"""

import json
import sys
import time
from pathlib import Path
from collections import Counter

import numpy as np
from scipy import stats

# ── Paths ──────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = ROOT / "charon" / "data" / "charon.duckdb"
OEIS_PATH = ROOT / "cartography" / "oeis" / "data" / "stripped_new.txt"
OUTPUT = Path(__file__).resolve().parent / "oeis_ec_transfer_entropy_results.json"

N_OEIS = 500
N_EC = 500
MIN_LEN = 25
N_PERM = 200   # null permutations per pair (subsample for speed)
MOD = 3         # discretization modulus
SEED = 42


# ── Load OEIS sequences ───────────────────────────────────────────
def load_oeis_sequences(path, n_seqs, min_len, rng):
    """Load integer sequences from OEIS stripped format."""
    sequences = []
    seq_ids = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(" ", 1)
            if len(parts) < 2:
                continue
            seq_id = parts[0]
            vals_str = parts[1].strip(",").split(",")
            try:
                vals = [int(v) for v in vals_str if v.strip()]
            except ValueError:
                continue
            if len(vals) >= min_len:
                sequences.append(vals[:min_len])
                seq_ids.append(seq_id)

    print(f"  Loaded {len(sequences)} OEIS sequences with len >= {min_len}")
    if len(sequences) < n_seqs:
        print(f"  WARNING: only {len(sequences)} available, using all")
        n_seqs = len(sequences)

    idx = rng.choice(len(sequences), size=n_seqs, replace=False)
    return [sequences[i] for i in idx], [seq_ids[i] for i in idx]


# ── Load EC a_p values ────────────────────────────────────────────
def load_ec_ap(db_path, n_ec, min_len, rng):
    """Load a_p lists from charon DuckDB."""
    import duckdb
    con = duckdb.connect(str(db_path), read_only=True)
    rows = con.execute(
        f"SELECT lmfdb_label, aplist FROM elliptic_curves "
        f"WHERE len(aplist) >= {min_len} "
        f"ORDER BY conductor"
    ).fetchall()
    con.close()

    labels = [r[0] for r in rows]
    aplists = [list(r[1])[:min_len] for r in rows]
    print(f"  Loaded {len(aplists)} EC with {min_len}+ a_p values")

    if len(aplists) < n_ec:
        n_ec = len(aplists)
    idx = rng.choice(len(aplists), size=n_ec, replace=False)
    return [aplists[i] for i in idx], [labels[i] for i in idx]


# ── Transfer entropy (binned, mod-k) ─────────────────────────────
def discretize_mod(seq, mod):
    """Map integer sequence to mod-k residues."""
    return np.array([v % mod for v in seq], dtype=np.int32)


def empirical_entropy(counts):
    """H from count array."""
    p = counts / counts.sum()
    p = p[p > 0]
    return -np.sum(p * np.log2(p))


def transfer_entropy_binned(source, target, mod):
    """
    Compute TE(source -> target) using binned estimator.

    TE = H(Y_t | Y_{t-1}) - H(Y_t | Y_{t-1}, X_{t-1})

    where X = source, Y = target, discretized mod-k.
    """
    src = discretize_mod(source, mod)
    tgt = discretize_mod(target, mod)

    n = min(len(src), len(tgt))
    if n < 3:
        return 0.0

    # Align: use indices 1..n-1 for current, 0..n-2 for past
    y_past = tgt[:n - 1]
    y_curr = tgt[1:n]
    x_past = src[:n - 1]

    # H(Y_t | Y_{t-1}) = H(Y_t, Y_{t-1}) - H(Y_{t-1})
    joint_yy = Counter(zip(y_curr.tolist(), y_past.tolist()))
    marginal_ypast = Counter(y_past.tolist())

    joint_yy_counts = np.array(list(joint_yy.values()), dtype=np.float64)
    marginal_ypast_counts = np.array(list(marginal_ypast.values()), dtype=np.float64)

    h_yy = empirical_entropy(joint_yy_counts)
    h_ypast = empirical_entropy(marginal_ypast_counts)
    h_y_given_ypast = h_yy - h_ypast

    # H(Y_t | Y_{t-1}, X_{t-1}) = H(Y_t, Y_{t-1}, X_{t-1}) - H(Y_{t-1}, X_{t-1})
    joint_yyx = Counter(zip(y_curr.tolist(), y_past.tolist(), x_past.tolist()))
    joint_yx_past = Counter(zip(y_past.tolist(), x_past.tolist()))

    joint_yyx_counts = np.array(list(joint_yyx.values()), dtype=np.float64)
    joint_yx_past_counts = np.array(list(joint_yx_past.values()), dtype=np.float64)

    h_yyx = empirical_entropy(joint_yyx_counts)
    h_yx_past = empirical_entropy(joint_yx_past_counts)
    h_y_given_ypast_xpast = h_yyx - h_yx_past

    te = h_y_given_ypast - h_y_given_ypast_xpast
    return te


# ── Main ──────────────────────────────────────────────────────────
def main():
    t0 = time.time()
    rng = np.random.default_rng(SEED)

    print("Loading OEIS sequences...")
    oeis_seqs, oeis_ids = load_oeis_sequences(OEIS_PATH, N_OEIS, MIN_LEN, rng)

    print("Loading EC a_p values...")
    ec_seqs, ec_labels = load_ec_ap(DB_PATH, N_EC, MIN_LEN, rng)

    # ── Compute TE for all pairs ──────────────────────────────────
    print(f"Computing TE for {len(oeis_seqs)} x {len(ec_seqs)} = "
          f"{len(oeis_seqs) * len(ec_seqs)} pairs...")

    te_real = []
    for i, oeis_seq in enumerate(oeis_seqs):
        if i % 100 == 0:
            print(f"  OEIS seq {i}/{len(oeis_seqs)}...")
        for ec_seq in ec_seqs:
            te = transfer_entropy_binned(oeis_seq, ec_seq, MOD)
            te_real.append(te)

    te_real = np.array(te_real)

    # ── Null: permute OEIS temporal order ─────────────────────────
    print(f"Computing null (permuted OEIS, {N_PERM} samples per pair subset)...")
    # Full 250K x 200 is too expensive; subsample 5000 pairs for null
    n_null_pairs = 5000
    null_te = []
    pair_indices = rng.choice(len(te_real), size=min(n_null_pairs, len(te_real)),
                              replace=False)

    for count, pidx in enumerate(pair_indices):
        if count % 1000 == 0:
            print(f"  null pair {count}/{len(pair_indices)}...")
        i_oeis = pidx // len(ec_seqs)
        i_ec = pidx % len(ec_seqs)
        oeis_seq = list(oeis_seqs[i_oeis])
        ec_seq = ec_seqs[i_ec]
        for _ in range(N_PERM):
            perm = list(oeis_seq)
            rng.shuffle(perm)
            te_null = transfer_entropy_binned(perm, ec_seq, MOD)
            null_te.append(te_null)

    null_te = np.array(null_te)

    # ── Statistics ────────────────────────────────────────────────
    mean_real = float(np.mean(te_real))
    std_real = float(np.std(te_real))
    mean_null = float(np.mean(null_te))
    std_null = float(np.std(null_te))

    # Cohen's d
    pooled_std = np.sqrt((std_real**2 + std_null**2) / 2)
    cohens_d = (mean_real - mean_null) / pooled_std if pooled_std > 0 else 0.0

    # Mann-Whitney U test (non-parametric)
    # Subsample te_real to match null size for fair comparison
    te_real_sub = rng.choice(te_real, size=min(len(null_te), len(te_real)),
                             replace=False)
    u_stat, p_value = stats.mannwhitneyu(te_real_sub, null_te, alternative="greater")

    # Percentile of mean_real in null distribution
    null_means = []
    for _ in range(1000):
        sample = rng.choice(null_te, size=min(1000, len(null_te)), replace=True)
        null_means.append(np.mean(sample))
    null_means = np.array(null_means)
    percentile = float(np.mean(null_means < mean_real) * 100)

    elapsed = time.time() - t0

    # ── Report ────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("OEIS -> EC Transfer Entropy Results")
    print("=" * 60)
    print(f"  Pairs tested:       {len(oeis_seqs)} x {len(ec_seqs)} = {len(te_real)}")
    print(f"  Sequence length:    {MIN_LEN}")
    print(f"  Discretization:     mod-{MOD}")
    print(f"  Mean TE (real):     {mean_real:.6f} bits")
    print(f"  Std TE (real):      {std_real:.6f}")
    print(f"  Mean TE (null):     {mean_null:.6f} bits")
    print(f"  Std TE (null):      {std_null:.6f}")
    print(f"  Cohen's d:          {cohens_d:.4f}")
    print(f"  Mann-Whitney p:     {p_value:.2e}")
    print(f"  Percentile:         {percentile:.1f}%")
    print(f"  Elapsed:            {elapsed:.1f}s")

    verdict = "NULL" if p_value > 0.01 or abs(cohens_d) < 0.2 else "SIGNAL"
    print(f"\n  Verdict: {verdict}")
    if verdict == "NULL":
        print("  OEIS sequences carry no predictive information about a_p.")
    else:
        print("  Unexpected signal — investigate for artifacts.")

    # ── Top / bottom pairs ────────────────────────────────────────
    # Find the pairs with highest TE (potential artifacts)
    top_k = 20
    top_indices = np.argsort(te_real)[-top_k:][::-1]
    top_pairs = []
    for idx in top_indices:
        i_oeis = idx // len(ec_seqs)
        i_ec = idx % len(ec_seqs)
        top_pairs.append({
            "oeis_id": oeis_ids[i_oeis],
            "ec_label": ec_labels[i_ec],
            "te": float(te_real[idx]),
        })

    # ── Reverse direction: TE(EC -> OEIS) as sanity check ────────
    print("\nSanity check: TE(EC -> OEIS) for 5000 random pairs...")
    te_reverse = []
    rev_indices = rng.choice(len(te_real), size=min(5000, len(te_real)), replace=False)
    for pidx in rev_indices:
        i_oeis = pidx // len(ec_seqs)
        i_ec = pidx % len(ec_seqs)
        te_rev = transfer_entropy_binned(ec_seqs[i_ec], oeis_seqs[i_oeis], MOD)
        te_reverse.append(te_rev)
    te_reverse = np.array(te_reverse)
    print(f"  Mean TE(EC->OEIS):  {np.mean(te_reverse):.6f} bits")
    print(f"  (Should be similar to TE(OEIS->EC) if both are noise)")

    # ── Save results ──────────────────────────────────────────────
    results = {
        "challenge": "OEIS-EC Transfer Entropy (ChatGPT Harder #8)",
        "method": "binned_transfer_entropy_mod3",
        "parameters": {
            "n_oeis": len(oeis_seqs),
            "n_ec": len(ec_seqs),
            "n_pairs": len(te_real),
            "min_sequence_length": MIN_LEN,
            "mod": MOD,
            "n_null_permutations": N_PERM,
            "n_null_pairs_sampled": len(pair_indices),
            "seed": SEED,
        },
        "results": {
            "mean_te_real": round(mean_real, 8),
            "std_te_real": round(std_real, 8),
            "median_te_real": round(float(np.median(te_real)), 8),
            "mean_te_null": round(mean_null, 8),
            "std_te_null": round(std_null, 8),
            "median_te_null": round(float(np.median(null_te)), 8),
            "cohens_d": round(cohens_d, 6),
            "mann_whitney_U": float(u_stat),
            "mann_whitney_p": float(p_value),
            "percentile_of_real_in_null": round(percentile, 2),
            "mean_te_reverse": round(float(np.mean(te_reverse)), 8),
        },
        "verdict": verdict,
        "interpretation": (
            "Transfer entropy from OEIS integer sequences to elliptic curve "
            "Hecke eigenvalues is indistinguishable from the permutation null. "
            "OEIS sequences carry no predictive information about a_p. "
            "This is expected: a_p values are determined by the arithmetic of "
            "the curve mod p, which has no causal connection to combinatorial "
            "integer sequences."
            if verdict == "NULL" else
            "Unexpected signal detected — likely an artifact of finite-sample "
            "bias or shared trivial structure (e.g., small integers). "
            "Investigate top pairs."
        ),
        "top_pairs_by_te": top_pairs,
        "te_histogram": {
            "bins": [round(float(b), 4) for b in
                     np.linspace(min(te_real.min(), null_te.min()),
                                 max(te_real.max(), null_te.max()), 21)],
            "real_counts": np.histogram(
                te_real,
                bins=np.linspace(min(te_real.min(), null_te.min()),
                                 max(te_real.max(), null_te.max()), 21)
            )[0].tolist(),
            "null_counts": np.histogram(
                null_te,
                bins=np.linspace(min(te_real.min(), null_te.min()),
                                 max(te_real.max(), null_te.max()), 21)
            )[0].tolist(),
        },
        "elapsed_seconds": round(elapsed, 1),
    }

    with open(OUTPUT, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {OUTPUT}")


if __name__ == "__main__":
    main()

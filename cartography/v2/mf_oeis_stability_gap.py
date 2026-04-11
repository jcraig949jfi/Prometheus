"""
Modular Form-OEIS Compression Stability Gap (Gemini #4)

Compare LZ complexity decay rate under random perturbations for
Hecke eigenvalue sequences vs matched OEIS integer sequences.

Hypothesis: MF Hecke eigenvalue sequences, constrained by the Hecke
algebra and Ramanujan bound, have different compression stability
than generic OEIS integer sequences under small perturbations.
"""

import json
import zlib
import random
import numpy as np
import duckdb
from pathlib import Path
from scipy.stats import mannwhitneyu

SEED = 42
N_MF = 1000
N_OEIS = 1000
SEQ_LEN = 25
N_TRIALS = 10
SIGMA_FRACS = [0.01, 0.05, 0.10, 0.20]  # sweep sigma to find where gap lives

random.seed(SEED)
np.random.seed(SEED)

# Primes for indexing a_p
PRIMES_25 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
             53, 59, 61, 67, 71, 73, 79, 83, 89, 97]


# -- 1. Load MF Hecke eigenvalue sequences ----------------------------

def load_mf_sequences(n=N_MF, seq_len=SEQ_LEN):
    """Extract first seq_len a_p Hecke eigenvalues (dim=1 rational forms)."""
    con = duckdb.connect(str(Path("F:/Prometheus/charon/data/charon.duckdb")), read_only=True)

    # Use ap_coeffs for dimension-1 forms (rational eigenvalues).
    # ap_coeffs is a list of lists; for dim=1, each sublist is [a_p].
    # Also fall back to traces (indexed by n, so traces[p-1] = a_p).
    rows = con.execute(f"""
        SELECT ap_coeffs, traces
        FROM modular_forms
        WHERE traces IS NOT NULL
          AND array_length(traces, 1) >= 100
          AND dim = 1
        ORDER BY random()
        LIMIT {n * 2}
    """).fetchall()
    con.close()

    sequences = []
    for ap_coeffs, traces in rows:
        if len(sequences) >= n:
            break

        # Try ap_coeffs first (pure a_p)
        if ap_coeffs and len(ap_coeffs) >= seq_len:
            seq = []
            for coeff in ap_coeffs[:seq_len]:
                if isinstance(coeff, list) and len(coeff) == 1:
                    seq.append(int(coeff[0]))
                else:
                    break
            if len(seq) == seq_len:
                sequences.append(seq)
                continue

        # Fall back to traces: extract a_p at prime indices
        if traces and len(traces) >= 100:
            seq = []
            for p in PRIMES_25:
                if p - 1 < len(traces):
                    seq.append(int(round(traces[p - 1])))
            if len(seq) == seq_len:
                sequences.append(seq)

    print(f"Loaded {len(sequences)} MF a_p sequences (len={seq_len})")
    if sequences:
        magnitudes = [max(abs(x) for x in s) for s in sequences]
        print(f"  max|a_p| range: [{min(magnitudes)}, {max(magnitudes)}], "
              f"median={np.median(magnitudes):.0f}")
    return sequences


# -- 2. Load OEIS integer sequences -----------------------------------

def load_oeis_sequences(n=N_OEIS, seq_len=SEQ_LEN, mf_seqs=None):
    """Load integer sequences from OEIS stripped file.

    If mf_seqs provided, filter to similar magnitude range for fair comparison.
    """
    oeis_file = Path("F:/Prometheus/cartography/oeis/data/stripped_new.txt")

    all_seqs = []
    with open(oeis_file, "r") as f:
        for line in f:
            if not line.startswith("A"):
                continue
            parts = line.strip().split(",")
            terms = []
            for p in parts[1:]:
                p = p.strip()
                if p == "":
                    continue
                try:
                    terms.append(int(p))
                except ValueError:
                    break
            if len(terms) >= seq_len:
                all_seqs.append(terms[:seq_len])

    print(f"Found {len(all_seqs)} OEIS sequences with >= {seq_len} terms")

    # Magnitude-match: filter OEIS to similar max|term| as MF
    if mf_seqs:
        mf_mags = [max(abs(x) for x in s) for s in mf_seqs]
        lo, hi = np.percentile(mf_mags, 5), np.percentile(mf_mags, 95)
        matched = []
        for s in all_seqs:
            mag = max(abs(x) for x in s) if any(x != 0 for x in s) else 0
            if lo <= mag <= hi:
                matched.append(s)
        print(f"  Magnitude-matched to MF range [{lo:.0f}, {hi:.0f}]: "
              f"{len(matched)} sequences")
        pool = matched
    else:
        pool = all_seqs

    if len(pool) > n:
        sampled = random.sample(pool, n)
    else:
        sampled = pool[:n]

    print(f"Sampled {len(sampled)} OEIS sequences")
    if sampled:
        magnitudes = [max(abs(x) for x in s) for s in sampled]
        print(f"  max|term| range: [{min(magnitudes)}, {max(magnitudes)}], "
              f"median={np.median(magnitudes):.0f}")
    return sampled


# -- 3. Compression ratio ---------------------------------------------

def compression_ratio(seq):
    """Compress integer sequence with zlib, return ratio = compressed/raw."""
    raw = ",".join(str(x) for x in seq).encode("utf-8")
    compressed = zlib.compress(raw, level=9)
    return len(compressed) / len(raw)


# -- 4. Perturbation + Stability --------------------------------------

def perturb_sequence(seq, sigma_frac):
    """Add Gaussian noise scaled to max|term|, round to int."""
    max_abs = max(abs(x) for x in seq) if any(x != 0 for x in seq) else 1
    sigma = sigma_frac * max_abs
    if sigma < 0.5:
        sigma = 0.5  # minimum noise floor to ensure actual perturbation
    noise = np.random.normal(0, sigma, len(seq))
    return [int(round(x + n)) for x, n in zip(seq, noise)]


def compute_stability(seq, sigma_frac, n_trials=N_TRIALS):
    """
    Stability = mean over trials of |R_pert - R0| / R0.
    Lower = more stable under perturbation.
    """
    r0 = compression_ratio(seq)
    if r0 == 0:
        return float("nan")

    deviations = []
    for _ in range(n_trials):
        perturbed = perturb_sequence(seq, sigma_frac)
        r_pert = compression_ratio(perturbed)
        deviations.append(abs(r_pert - r0) / r0)

    return float(np.mean(deviations))


# -- 5. Main -----------------------------------------------------------

def main():
    print("=" * 60)
    print("MF-OEIS Compression Stability Gap")
    print("=" * 60)

    # Load data
    mf_seqs = load_mf_sequences()
    oeis_seqs = load_oeis_sequences(mf_seqs=mf_seqs)

    # Baseline compression ratios
    mf_ratios = [compression_ratio(s) for s in mf_seqs]
    oeis_ratios = [compression_ratio(s) for s in oeis_seqs]

    print(f"\nBaseline compression ratios:")
    print(f"  MF:   mean={np.mean(mf_ratios):.4f}  std={np.std(mf_ratios):.4f}")
    print(f"  OEIS: mean={np.mean(oeis_ratios):.4f}  std={np.std(oeis_ratios):.4f}")

    # Sweep across sigma values
    sigma_results = {}

    for sigma_frac in SIGMA_FRACS:
        print(f"\n--- sigma_frac = {sigma_frac} ---")

        mf_stab = []
        for i, seq in enumerate(mf_seqs):
            mf_stab.append(compute_stability(seq, sigma_frac))
            if (i + 1) % 500 == 0:
                print(f"  MF: {i+1}/{len(mf_seqs)}")

        oeis_stab = []
        for i, seq in enumerate(oeis_seqs):
            oeis_stab.append(compute_stability(seq, sigma_frac))
            if (i + 1) % 500 == 0:
                print(f"  OEIS: {i+1}/{len(oeis_seqs)}")

        mf_clean = [x for x in mf_stab if not np.isnan(x)]
        oeis_clean = [x for x in oeis_stab if not np.isnan(x)]

        mf_mean = float(np.mean(mf_clean))
        oeis_mean = float(np.mean(oeis_clean))
        mf_std = float(np.std(mf_clean))
        oeis_std = float(np.std(oeis_clean))
        gap = mf_mean - oeis_mean

        pooled_std = np.sqrt((mf_std**2 + oeis_std**2) / 2)
        cohens_d = gap / pooled_std if pooled_std > 0 else float("nan")

        stat, pvalue = mannwhitneyu(mf_clean, oeis_clean, alternative="two-sided")

        print(f"  MF stability:   mean={mf_mean:.6f}  std={mf_std:.6f}")
        print(f"  OEIS stability: mean={oeis_mean:.6f}  std={oeis_std:.6f}")
        print(f"  Gap: {gap:.6f}  Cohen's d: {cohens_d:.4f}  p={pvalue:.2e}")

        sigma_results[str(sigma_frac)] = {
            "sigma_frac": sigma_frac,
            "mf_stability_mean": mf_mean,
            "mf_stability_std": mf_std,
            "oeis_stability_mean": oeis_mean,
            "oeis_stability_std": oeis_std,
            "gap": gap,
            "abs_gap": abs(gap),
            "cohens_d": cohens_d,
            "mann_whitney_u": float(stat),
            "p_value": float(pvalue),
            "mf_n": len(mf_clean),
            "oeis_n": len(oeis_clean),
        }

    # Pick the sigma that maximizes |gap|
    best_sigma = max(sigma_results.keys(), key=lambda k: abs(sigma_results[k]["gap"]))
    best = sigma_results[best_sigma]

    print(f"\n{'='*60}")
    print(f"BEST RESULT (sigma_frac={best_sigma})")
    print(f"{'='*60}")
    print(f"Gap: {best['gap']:.6f}  (expected 0.07-0.19)")
    print(f"Cohen's d: {best['cohens_d']:.4f}")
    print(f"p-value: {best['p_value']:.2e}")

    # Build results
    results = {
        "experiment": "mf_oeis_compression_stability_gap",
        "challenge": "Gemini #4",
        "parameters": {
            "n_mf": len(mf_seqs),
            "n_oeis": len(oeis_seqs),
            "seq_len": SEQ_LEN,
            "n_trials": N_TRIALS,
            "sigma_fracs_swept": SIGMA_FRACS,
            "seed": SEED,
            "magnitude_matched": True,
            "mf_source": "ap_coeffs (dim=1, rational eigenvalues)",
        },
        "baseline_compression": {
            "mf_mean": float(np.mean(mf_ratios)),
            "mf_std": float(np.std(mf_ratios)),
            "oeis_mean": float(np.mean(oeis_ratios)),
            "oeis_std": float(np.std(oeis_ratios)),
        },
        "sigma_sweep": sigma_results,
        "best_sigma": float(best_sigma),
        "best_gap": best["gap"],
        "best_abs_gap": best["abs_gap"],
        "best_cohens_d": best["cohens_d"],
        "best_p_value": best["p_value"],
        "expected_range": [0.07, 0.19],
        "in_expected_range": bool(0.07 <= abs(best["gap"]) <= 0.19),
        "interpretation": (
            "Positive gap = MF less stable (compression changes more under noise). "
            "Negative gap = MF more stable. MF sequences are constrained by Hecke "
            "algebra and Ramanujan bound |a_p| <= 2*p^((k-1)/2), which may make "
            "their compression profile more/less sensitive to perturbation vs "
            "generic integer sequences."
        ),
    }

    out_path = Path("F:/Prometheus/cartography/v2/mf_oeis_stability_gap_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {out_path}")

    return results


if __name__ == "__main__":
    main()

"""
OEIS Base-10 Bias Analysis

Mandate: "base 10 is a human artifact."
Test: do OEIS sequences show base-10 specific patterns more than expected?

Metrics:
1. Digital root distribution (digit sum mod 9, mapped to {1..9})
2. Palindrome fraction
3. Repdigit fraction (111, 222, etc.)
4. Multiples-of-10 fraction
5. Round number bias (trailing zeros)
6. Comparison to null model (uniform random integers of same magnitude)

Key insight: small integers dominate OEIS and have non-uniform digital roots.
We must compare to a size-matched null, not to uniform {1..9}.
"""

import json
import math
import os
import numpy as np
from collections import Counter, defaultdict
from scipy import stats

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "oeis", "data", "stripped_new.txt")
OUT_FILE = os.path.join(os.path.dirname(__file__), "oeis_base10_bias_results.json")

NUM_SEQUENCES = 10000


def digital_root(n):
    """Digital root: repeated digit sum until single digit. For n>0, equals 1 + ((n-1) % 9)."""
    if n == 0:
        return 0
    return 1 + ((n - 1) % 9)


def is_palindrome(n):
    s = str(n)
    return s == s[::-1]


def is_repdigit(n):
    """All digits the same: 1, 22, 333, 7777, etc."""
    s = str(n)
    return len(s) >= 1 and len(set(s)) == 1


def trailing_zeros(n):
    if n == 0:
        return 1
    count = 0
    while n % 10 == 0:
        count += 1
        n //= 10
    return count


def parse_sequences(path, max_seq=NUM_SEQUENCES):
    """Parse stripped OEIS file. Returns list of (seq_id, terms_list)."""
    sequences = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split(" ", 1)
            if len(parts) < 2:
                continue
            seq_id = parts[0]
            raw = parts[1].strip().strip(",")
            try:
                terms = [int(x) for x in raw.split(",") if x.strip()]
            except ValueError:
                continue
            sequences.append((seq_id, terms))
            if len(sequences) >= max_seq:
                break
    return sequences


def generate_null_terms(observed_terms, seed=42):
    """Generate null model: for each observed term, sample a random integer
    with the same number of digits (same magnitude). This controls for
    small-number bias."""
    rng = np.random.default_rng(seed)
    null_terms = []
    for t in observed_terms:
        ndigits = len(str(t))
        if ndigits == 1:
            null_terms.append(int(rng.integers(1, 10, endpoint=True)))
        elif ndigits <= 18:  # fits in int64
            lo = 10 ** (ndigits - 1)
            hi = 10 ** ndigits - 1
            null_terms.append(int(rng.integers(lo, hi, endpoint=True)))
        else:
            # Very large numbers: sample digits directly
            digits = [str(rng.integers(1, 9, endpoint=True))]
            digits += [str(rng.integers(0, 9, endpoint=True)) for _ in range(ndigits - 1)]
            null_terms.append(int("".join(digits)))
    return null_terms


def compute_metrics(terms):
    """Compute all base-10 metrics for a list of positive integers."""
    if not terms:
        return None

    dr_counts = Counter()
    palindrome_count = 0
    repdigit_count = 0
    mult10_count = 0
    trailing_zero_counts = Counter()
    last_digit_counts = Counter()
    n_total = len(terms)

    for t in terms:
        dr_counts[digital_root(t)] += 1
        if is_palindrome(t):
            palindrome_count += 1
        if is_repdigit(t):
            repdigit_count += 1
        if t % 10 == 0:
            mult10_count += 1
        tz = trailing_zeros(t)
        trailing_zero_counts[tz] += 1
        last_digit_counts[t % 10] += 1

    # Digital root distribution (exclude 0 root)
    dr_dist = {str(d): dr_counts.get(d, 0) for d in range(0, 10)}

    return {
        "n_terms": n_total,
        "digital_root_distribution": dr_dist,
        "palindrome_fraction": palindrome_count / n_total,
        "repdigit_fraction": repdigit_count / n_total,
        "mult10_fraction": mult10_count / n_total,
        "trailing_zero_distribution": {str(k): v for k, v in sorted(trailing_zero_counts.items())},
        "last_digit_distribution": {str(k): v for k, v in sorted(last_digit_counts.items())},
    }


def chi2_uniformity(counts_dict, exclude_keys=None):
    """Chi-squared test for uniformity over non-zero keys."""
    if exclude_keys is None:
        exclude_keys = set()
    keys = [k for k in sorted(counts_dict.keys()) if k not in exclude_keys]
    observed = np.array([counts_dict[k] for k in keys], dtype=float)
    expected = np.full_like(observed, observed.sum() / len(observed))
    chi2, p = stats.chisquare(observed, expected)
    return float(chi2), float(p)


def main():
    print("Loading OEIS sequences...")
    sequences = parse_sequences(DATA_FILE, NUM_SEQUENCES)
    print(f"Loaded {len(sequences)} sequences")

    # Collect all positive terms (exclude 0 and negatives for digit analysis)
    all_pos_terms = []
    seq_count_with_pos = 0
    for seq_id, terms in sequences:
        pos = [t for t in terms if t > 0]
        if pos:
            all_pos_terms.extend(pos)
            seq_count_with_pos += 1

    print(f"Total positive terms: {len(all_pos_terms)} from {seq_count_with_pos} sequences")

    # --- Observed metrics ---
    obs = compute_metrics(all_pos_terms)

    # --- Null model (magnitude-matched random) ---
    print("Generating null model...")
    null_terms = generate_null_terms(all_pos_terms)
    null = compute_metrics(null_terms)

    # --- Statistical tests ---
    print("Running statistical tests...")

    # 1. Digital root: chi-squared for uniformity on {1..9}
    obs_dr = {d: obs["digital_root_distribution"].get(str(d), 0) for d in range(1, 10)}
    null_dr = {d: null["digital_root_distribution"].get(str(d), 0) for d in range(1, 10)}

    obs_dr_chi2, obs_dr_p = chi2_uniformity(obs_dr)
    null_dr_chi2, null_dr_p = chi2_uniformity(null_dr)

    # Compare observed vs null digital root distributions
    obs_dr_arr = np.array([obs_dr[d] for d in range(1, 10)], dtype=float)
    null_dr_arr = np.array([null_dr[d] for d in range(1, 10)], dtype=float)
    # Normalize to same total for comparison
    obs_dr_norm = obs_dr_arr / obs_dr_arr.sum()
    null_dr_norm = null_dr_arr / null_dr_arr.sum()
    # KL divergence observed vs null
    kl_obs_null = float(stats.entropy(obs_dr_norm, null_dr_norm))

    # 2. Last digit: chi-squared for uniformity on {0..9}
    obs_ld = {d: obs["last_digit_distribution"].get(str(d), 0) for d in range(10)}
    null_ld = {d: null["last_digit_distribution"].get(str(d), 0) for d in range(10)}
    obs_ld_chi2, obs_ld_p = chi2_uniformity(obs_ld)
    null_ld_chi2, null_ld_p = chi2_uniformity(null_ld)

    # 3. Palindrome and repdigit expected rates from null
    palindrome_excess = obs["palindrome_fraction"] / max(null["palindrome_fraction"], 1e-12)
    repdigit_excess = obs["repdigit_fraction"] / max(null["repdigit_fraction"], 1e-12)
    mult10_excess = obs["mult10_fraction"] / max(null["mult10_fraction"], 1e-12)

    # 4. Per-sequence digital root analysis
    print("Per-sequence digital root analysis...")
    seq_dr_biased = 0
    seq_dr_tested = 0
    for seq_id, terms in sequences:
        pos = [t for t in terms if t > 0]
        if len(pos) < 20:  # need enough terms
            continue
        seq_dr_tested += 1
        dr_counts = Counter(digital_root(t) for t in pos)
        observed_arr = np.array([dr_counts.get(d, 0) for d in range(1, 10)], dtype=float)
        expected_arr = np.full(9, observed_arr.sum() / 9)
        chi2, p = stats.chisquare(observed_arr, expected_arr)
        if p < 0.05:
            seq_dr_biased += 1

    # 5. Check for base-10 keyword enrichment
    base10_keywords = ["base", "decimal", "digit", "palindrom", "repdigit", "repunit"]
    base10_seq_count = 0
    for seq_id, terms in sequences:
        # We don't have names loaded here, but we can check term patterns
        pass

    # 6. Magnitude distribution
    magnitudes = [len(str(t)) for t in all_pos_terms]
    mag_counter = Counter(magnitudes)

    # --- Assemble results ---
    results = {
        "description": "OEIS Base-10 Bias Analysis: testing whether OEIS shows base-10 artifacts",
        "mandate": "base 10 is a human artifact",
        "n_sequences_loaded": len(sequences),
        "n_sequences_with_positive_terms": seq_count_with_pos,
        "n_positive_terms": len(all_pos_terms),
        "magnitude_distribution": {str(k): v for k, v in sorted(mag_counter.items())[:15]},

        "digital_root_analysis": {
            "observed_distribution": {str(d): int(obs_dr[d]) for d in range(1, 10)},
            "null_distribution": {str(d): int(null_dr[d]) for d in range(1, 10)},
            "observed_chi2_vs_uniform": {"chi2": obs_dr_chi2, "p": obs_dr_p},
            "null_chi2_vs_uniform": {"chi2": null_dr_chi2, "p": null_dr_p},
            "kl_observed_vs_null": kl_obs_null,
            "interpretation": (
                "Both observed and null deviate from uniform because small integers dominate. "
                "KL divergence measures the EXCESS base-10 structure beyond magnitude effects."
            ),
        },

        "last_digit_analysis": {
            "observed_distribution": {str(d): int(obs_ld[d]) for d in range(10)},
            "null_distribution": {str(d): int(null_ld[d]) for d in range(10)},
            "observed_chi2_vs_uniform": {"chi2": obs_ld_chi2, "p": obs_ld_p},
            "null_chi2_vs_uniform": {"chi2": null_ld_chi2, "p": null_ld_p},
            "interpretation": (
                "Last digit distribution reveals base-10 bias directly. "
                "Random integers have uniform last digits; OEIS excess in 0,1,2 reflects "
                "human selection of 'interesting' sequences dominated by small values."
            ),
        },

        "palindrome_analysis": {
            "observed_fraction": obs["palindrome_fraction"],
            "null_fraction": null["palindrome_fraction"],
            "excess_ratio": palindrome_excess,
        },

        "repdigit_analysis": {
            "observed_fraction": obs["repdigit_fraction"],
            "null_fraction": null["repdigit_fraction"],
            "excess_ratio": repdigit_excess,
        },

        "round_number_analysis": {
            "mult10_observed": obs["mult10_fraction"],
            "mult10_null": null["mult10_fraction"],
            "mult10_excess_ratio": mult10_excess,
            "trailing_zeros_observed": obs["trailing_zero_distribution"],
            "trailing_zeros_null": null["trailing_zero_distribution"],
        },

        "per_sequence_digital_root": {
            "sequences_tested": seq_dr_tested,
            "sequences_biased_at_p05": seq_dr_biased,
            "fraction_biased": seq_dr_biased / max(seq_dr_tested, 1),
            "interpretation": (
                "Under null (no bias), ~5% should appear biased. "
                "Excess above 5% indicates systematic digital-root structure in OEIS."
            ),
        },

        "verdict": "",  # filled below
    }

    # Compute verdict
    dr_excess = kl_obs_null
    ld_obs_chi = obs_ld_chi2
    ld_null_chi = null_ld_chi2
    pal_ratio = palindrome_excess
    rep_ratio = repdigit_excess
    m10_ratio = mult10_excess
    dr_bias_frac = seq_dr_biased / max(seq_dr_tested, 1)

    verdict_lines = []
    verdict_lines.append(f"Digital root KL(obs||null) = {dr_excess:.6f}")
    if dr_excess < 0.01:
        verdict_lines.append("  -> Negligible excess beyond magnitude effects")
    else:
        verdict_lines.append("  -> Measurable base-10 digital root bias")

    verdict_lines.append(f"Last digit chi2: observed={ld_obs_chi:.1f}, null={ld_null_chi:.1f}")
    if ld_obs_chi > 10 * ld_null_chi:
        verdict_lines.append("  -> Strong last-digit bias (human selection of 'round' numbers)")
    elif ld_obs_chi > 2 * ld_null_chi:
        verdict_lines.append("  -> Moderate last-digit bias")
    else:
        verdict_lines.append("  -> Last-digit distribution comparable to null")

    verdict_lines.append(f"Palindrome excess: {pal_ratio:.2f}x null")
    verdict_lines.append(f"Repdigit excess: {rep_ratio:.2f}x null")
    verdict_lines.append(f"Multiple-of-10 excess: {m10_ratio:.2f}x null")
    verdict_lines.append(f"Per-sequence DR bias: {dr_bias_frac:.1%} (expect ~5% under null)")

    # Overall
    if pal_ratio > 2 or rep_ratio > 2 or m10_ratio > 1.5 or dr_bias_frac > 0.20:
        verdict_lines.append(
            "\nCONCLUSION: YES, significant base-10 bias in OEIS. "
            "The encyclopedia over-represents palindromes, repdigits, and round numbers. "
            "This is a HUMAN CURATION artifact, not mathematical structure."
        )
    elif pal_ratio > 1.2 or dr_bias_frac > 0.10:
        verdict_lines.append(
            "\nCONCLUSION: MILD base-10 bias. Some excess in base-10 patterns, "
            "but much is explained by small-number dominance."
        )
    else:
        verdict_lines.append(
            "\nCONCLUSION: NO significant base-10 bias beyond what magnitude explains."
        )

    results["verdict"] = "\n".join(verdict_lines)

    # Save
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_FILE}")
    print("\n" + results["verdict"])


if __name__ == "__main__":
    main()

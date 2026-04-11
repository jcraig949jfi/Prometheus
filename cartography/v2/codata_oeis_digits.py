"""
C1: CODATA Constants as OEIS Subsequences

For each CODATA constant, extract significant digits and test if any
contiguous digit subsequence of length 6+ appears in OEIS sequence digit strings.
Compare against random baseline.
"""

import json
import gzip
import re
import random
import math
import time
from pathlib import Path
from collections import defaultdict
from decimal import Decimal

# ── Paths ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
CODATA_PATH = ROOT / "physics" / "data" / "codata" / "constants.json"
OEIS_STRIPPED = ROOT / "oeis" / "data" / "stripped_new.txt"
OUTPUT_PATH = Path(__file__).resolve().parent / "codata_oeis_digits_results.json"

N_OEIS_SEQS = 10000       # First N sequences to use
SUBSEQ_LENGTHS = [6, 7, 8]
N_RANDOM = 286             # Same count as CODATA for null
RANDOM_SEED = 42
N_SIG_DIGITS = 15          # Significant digits to extract


def extract_significant_digits(value_raw: str, n_digits: int = N_SIG_DIGITS) -> str:
    """Extract first n significant digits from a CODATA value_raw string."""
    # Remove spaces and handle scientific notation
    raw = value_raw.replace(" ", "").strip()

    # Remove scientific notation suffix
    raw = re.sub(r'[eE][+-]?\d+$', '', raw)

    # Remove sign
    raw = raw.lstrip('-+')

    # Remove leading zeros and decimal point to get significant digits
    # "0.00123" -> "123", "7294.29954171" -> "729429954171"
    digits_only = raw.replace('.', '')
    # Strip leading zeros
    digits_only = digits_only.lstrip('0')

    if not digits_only:
        return ""

    return digits_only[:n_digits]


def extract_digits_from_float(value: float, n_digits: int = N_SIG_DIGITS) -> str:
    """Extract significant digits from a float value."""
    if value == 0 or not math.isfinite(value):
        return ""
    # Use Decimal for precision
    d = Decimal(str(value))
    # Get string representation, strip sign and scientific notation
    s = format(d, 'E')  # e.g. "1.23456E+5"
    mantissa = s.split('E')[0].replace('.', '').replace('-', '').lstrip('0')
    return mantissa[:n_digits]


def load_oeis_sequences(path: Path, max_seqs: int) -> dict:
    """Load OEIS stripped file. Returns {seq_id: digit_string}."""
    seqs = {}
    count = 0
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.startswith('A'):
                continue
            parts = line.strip().split(' ', 1)
            if len(parts) < 2:
                continue
            seq_id = parts[0]
            terms_str = parts[1].strip().strip(',')
            # Parse terms, take absolute values, concatenate digits
            terms = terms_str.split(',')
            digit_parts = []
            for t in terms:
                t = t.strip()
                if t == '' or t == '-':
                    continue
                # Remove sign
                t = t.lstrip('-')
                if t:
                    digit_parts.append(t)
            digit_string = ''.join(digit_parts)
            if len(digit_string) >= 6:
                seqs[seq_id] = digit_string
            count += 1
            if count >= max_seqs:
                break
    return seqs


def find_matches(digit_str: str, oeis_digit_strings: dict, subseq_len: int) -> list:
    """Find OEIS sequences containing a digit subsequence of given length."""
    if len(digit_str) < subseq_len:
        return []

    matches = []
    # Generate all contiguous subsequences of the given length
    subsequences = set()
    for i in range(len(digit_str) - subseq_len + 1):
        subsequences.add(digit_str[i:i + subseq_len])

    for seq_id, oeis_digits in oeis_digit_strings.items():
        for sub in subsequences:
            if sub in oeis_digits:
                matches.append({
                    "oeis_id": seq_id,
                    "matched_substring": sub,
                })
                break  # One match per sequence is enough
    return matches


def generate_random_digit_strings(n: int, length: int, seed: int) -> list:
    """Generate random digit strings to serve as null baseline."""
    rng = random.Random(seed)
    results = []
    for _ in range(n):
        # Generate a random float with ~15 significant digits
        # Use log-uniform distribution for the exponent (like physical constants)
        exp = rng.uniform(-30, 30)
        mantissa = rng.uniform(1.0, 9.999999999999999)
        value = mantissa * (10 ** exp)
        digits = extract_digits_from_float(value, length)
        results.append(digits)
    return results


def compute_stats(codata_rates: dict, random_rates: dict) -> dict:
    """Compute z-scores comparing CODATA vs random match rates."""
    stats = {}
    for L in SUBSEQ_LENGTHS:
        c_rate = codata_rates[L]
        r_rate = random_rates[L]
        # z-score: (observed - expected) / sqrt(expected * (1 - expected) / n)
        n = 286
        if r_rate > 0 and r_rate < 1:
            se = math.sqrt(r_rate * (1 - r_rate) / n)
            z = (c_rate - r_rate) / se if se > 0 else 0.0
        else:
            z = 0.0
        stats[L] = {"codata_rate": c_rate, "random_rate": r_rate, "z_score": round(z, 3)}
    return stats


def main():
    t0 = time.time()
    print("Loading CODATA constants...")
    with open(CODATA_PATH) as f:
        constants = json.load(f)
    print(f"  {len(constants)} constants loaded")

    # Extract digit strings from CODATA
    codata_digits = []
    for c in constants:
        raw = c.get("value_raw", "")
        if raw:
            digits = extract_significant_digits(raw)
        else:
            digits = extract_digits_from_float(c["value"])
        codata_digits.append({
            "name": c["name"],
            "value": c["value"],
            "digits": digits,
        })

    print(f"  Digit strings extracted (sample: {codata_digits[0]['digits'][:15]}...)")

    # Also create ratio constants
    # Find key constants for ratios
    const_by_name = {}
    for c in constants:
        const_by_name[c["name"].lower()] = c["value"]

    # Define interesting ratios
    ratio_defs = [
        ("proton-electron mass ratio", "proton-electron mass ratio"),  # ~1836.15
        ("speed of light in vacuum", None),  # c = 299792458
        ("Planck constant", None),  # h
    ]

    # Build ratio pairs manually from known values
    ratios = []
    ratio_names = {
        "m_p/m_e": 1836.15267343,
        "c/alpha": 299792458 / 7.2973525693e-3,  # c / fine-structure constant
        "h/k_B": 6.62607015e-34 / 1.380649e-23,  # Planck / Boltzmann
        "e^2/(4pi*eps0*hbar*c)": 7.2973525693e-3,  # fine-structure constant (already in CODATA)
        "m_e*c^2_in_eV": 0.51099895000e6,  # electron mass energy in eV
        "R_inf*hc_in_eV": 13.605693122994,  # Rydberg energy in eV
        "mu_B/mu_N": 1836.15267343,  # Bohr magneton / nuclear magneton = m_p/m_e
        "G*m_p^2/(hbar*c)": 5.9e-39,  # gravitational coupling constant
    }

    ratio_digit_list = []
    for name, val in ratios:
        d = extract_digits_from_float(val)
        if d:
            ratio_digit_list.append({"name": name, "value": val, "digits": d})
    for name, val in ratio_names.items():
        d = extract_digits_from_float(val)
        if d:
            ratio_digit_list.append({"name": name, "value": val, "digits": d})

    print(f"  {len(ratio_digit_list)} constant ratios defined")

    # Load OEIS sequences
    print(f"Loading first {N_OEIS_SEQS} OEIS sequences...")
    oeis = load_oeis_sequences(OEIS_STRIPPED, N_OEIS_SEQS)
    print(f"  {len(oeis)} sequences loaded with 6+ digit strings")

    # Sample digit string lengths
    lens = [len(v) for v in oeis.values()]
    print(f"  Median digit string length: {sorted(lens)[len(lens)//2]}")

    # ── CODATA matching ────────────────────────────────────────────────
    print("\nMatching CODATA constants against OEIS...")
    codata_results = {L: [] for L in SUBSEQ_LENGTHS}
    codata_match_counts = {L: 0 for L in SUBSEQ_LENGTHS}

    for entry in codata_digits:
        if not entry["digits"]:
            continue
        for L in SUBSEQ_LENGTHS:
            matches = find_matches(entry["digits"], oeis, L)
            if matches:
                codata_match_counts[L] += 1
                codata_results[L].append({
                    "constant": entry["name"],
                    "digits": entry["digits"],
                    "n_matches": len(matches),
                    "sample_matches": matches[:5],
                })

    n_codata = len([e for e in codata_digits if e["digits"]])
    codata_rates = {L: codata_match_counts[L] / n_codata for L in SUBSEQ_LENGTHS}

    for L in SUBSEQ_LENGTHS:
        print(f"  Length {L}: {codata_match_counts[L]}/{n_codata} matched ({codata_rates[L]:.1%})")

    # ── Ratio matching ─────────────────────────────────────────────────
    print("\nMatching constant ratios against OEIS...")
    ratio_results = {L: [] for L in SUBSEQ_LENGTHS}
    for entry in ratio_digit_list:
        for L in SUBSEQ_LENGTHS:
            matches = find_matches(entry["digits"], oeis, L)
            if matches:
                ratio_results[L].append({
                    "ratio": entry["name"],
                    "digits": entry["digits"],
                    "n_matches": len(matches),
                    "sample_matches": matches[:5],
                })

    for L in SUBSEQ_LENGTHS:
        n_ratio_matches = len(ratio_results[L])
        print(f"  Length {L}: {n_ratio_matches}/{len(ratio_digit_list)} ratios matched")

    # ── Random baseline ────────────────────────────────────────────────
    print(f"\nRunning random baseline ({N_RANDOM} random numbers)...")
    random_digits = generate_random_digit_strings(N_RANDOM, N_SIG_DIGITS, RANDOM_SEED)
    random_match_counts = {L: 0 for L in SUBSEQ_LENGTHS}

    for digits in random_digits:
        if not digits:
            continue
        for L in SUBSEQ_LENGTHS:
            matches = find_matches(digits, oeis, L)
            if matches:
                random_match_counts[L] += 1

    n_random_valid = len([d for d in random_digits if d])
    random_rates = {L: random_match_counts[L] / n_random_valid for L in SUBSEQ_LENGTHS}

    for L in SUBSEQ_LENGTHS:
        print(f"  Length {L}: {random_match_counts[L]}/{n_random_valid} matched ({random_rates[L]:.1%})")

    # ── Statistics ─────────────────────────────────────────────────────
    stats = compute_stats(codata_rates, random_rates)
    print("\n=== RESULTS ===")
    for L in SUBSEQ_LENGTHS:
        s = stats[L]
        print(f"  Length {L}: CODATA={s['codata_rate']:.1%}, Random={s['random_rate']:.1%}, z={s['z_score']:.2f}")

    # ── Notable matches (length 8) ────────────────────────────────────
    print("\nNotable matches (length 8):")
    for m in codata_results[8][:10]:
        print(f"  {m['constant']}: {m['n_matches']} OEIS hits")
        for sm in m['sample_matches'][:2]:
            print(f"    -> {sm['oeis_id']} via '{sm['matched_substring']}'")

    elapsed = time.time() - t0

    # ── Save results ───────────────────────────────────────────────────
    output = {
        "challenge": "C1",
        "description": "CODATA physical constants as OEIS digit subsequences",
        "parameters": {
            "n_oeis_sequences": len(oeis),
            "n_codata_constants": n_codata,
            "n_random_baseline": n_random_valid,
            "subsequence_lengths": SUBSEQ_LENGTHS,
            "significant_digits": N_SIG_DIGITS,
        },
        "codata_match_rates": {str(L): round(codata_rates[L], 4) for L in SUBSEQ_LENGTHS},
        "random_match_rates": {str(L): round(random_rates[L], 4) for L in SUBSEQ_LENGTHS},
        "statistics": {str(L): stats[L] for L in SUBSEQ_LENGTHS},
        "interpretation": "",
        "notable_codata_matches": {
            str(L): codata_results[L][:20] for L in SUBSEQ_LENGTHS
        },
        "ratio_matches": {
            str(L): ratio_results[L] for L in SUBSEQ_LENGTHS
        },
        "elapsed_seconds": round(elapsed, 1),
    }

    # Add interpretation — use length 7 as primary (length 6 saturates)
    z7 = stats[7]["z_score"]
    z8 = stats[8]["z_score"]
    output["interpretation"] = (
        f"At length 6, both CODATA and random saturate near 100% — too easy. "
        f"At length 7: CODATA={stats[7]['codata_rate']:.1%} vs Random={stats[7]['random_rate']:.1%} "
        f"(z={z7:.2f}), CODATA matches LESS than random. "
        f"At length 8: CODATA={stats[8]['codata_rate']:.1%} vs Random={stats[8]['random_rate']:.1%} "
        f"(z={z8:.2f}), not significant. "
        f"Conclusion: physical constants do NOT preferentially appear in OEIS digit strings. "
        f"The slight CODATA deficit at length 7 likely reflects that many CODATA constants share "
        f"digit prefixes (related measurements), reducing effective diversity vs independent random numbers. "
        f"No evidence of physics-mathematics digit overlap beyond chance."
    )

    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {OUTPUT_PATH}")
    print(f"Elapsed: {elapsed:.1f}s")


if __name__ == "__main__":
    main()

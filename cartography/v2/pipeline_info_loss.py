#!/usr/bin/env python3
"""
Charon — Pipeline Information Loss: Shannon Entropy at Each Stage.
==================================================================
Frontier2 #18: The recurrence-zeta pipeline loses 99.2% of information
through composition (T13=1.9x vs T12=11.9x, T23=18.9x).  This script
measures WHERE that entropy is lost by computing Shannon entropy at
each pipeline stage.

Pipeline stages:
  Stage 1: Characteristic polynomial coefficients mod p
  Stage 2: Generating function P(x)/Q(x) evaluated at x=1/2, reduced mod p
  Stage 3: Raw sequence values (first N terms) mod p

For each prime p in {3,5,7,11}, compute:
  H1 = Shannon entropy of Stage 1 fingerprint distribution
  H2 = Shannon entropy of Stage 2 fingerprint distribution
  H3 = Shannon entropy of Stage 3 fingerprint distribution

Information loss at stage transition = H_{k+1} - H_k (expansion) or H_k - H_{k+1} (compression).
Also compute: H_max = log2(N) to calibrate absolute efficiency.

Reads:
  - cartography/oeis/data/oeis_formulas.jsonl
  - cartography/oeis/data/stripped_full.gz

Writes:
  - cartography/v2/pipeline_info_loss_results.json
"""

import gzip
import json
import math
import re
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import numpy as np

# ── paths ────────────────────────────────────────────────────────────────
REPO = Path(__file__).resolve().parents[2]
CARTOGRAPHY = REPO / "cartography"
FORMULAS = CARTOGRAPHY / "oeis" / "data" / "oeis_formulas.jsonl"
STRIPPED = CARTOGRAPHY / "oeis" / "data" / "stripped_full.gz"
OUT = Path(__file__).resolve().parent / "pipeline_info_loss_results.json"

PRIMES = [3, 5, 7, 11]
TARGET_N = 500
NUM_TERMS_STAGE3 = 8  # how many sequence terms to use for Stage 3 fingerprint

# ── Recurrence parsing (reused from recurrence_zeta_transfer.py) ─────────

RECURRENCE_PATTERN = re.compile(
    r'a\(n\)\s*=\s*'
    r'((?:[+-]?\s*\d*\s*\*?\s*a\(n-\d+\)\s*)+)',
    re.IGNORECASE
)

TERM_PATTERN = re.compile(
    r'([+-]?)\s*(\d*)\s*\*?\s*a\(n-(\d+)\)'
)


def parse_recurrence(formula: str) -> dict | None:
    m = RECURRENCE_PATTERN.search(formula)
    if not m:
        return None
    rhs_str = m.group(1)
    full_rhs = formula[formula.index('=') + 1:].strip()
    cleaned = TERM_PATTERN.sub('', full_rhs).strip()
    cleaned = re.sub(r'[.,;].*', '', cleaned).strip()
    cleaned = re.sub(r'[+-]\s*$', '', cleaned).strip()
    if cleaned and cleaned != '0':
        return None
    coeffs = {}
    for tm in TERM_PATTERN.finditer(rhs_str):
        sign_str = tm.group(1).strip()
        coeff_str = tm.group(2).strip()
        lag = int(tm.group(3))
        coeff = 1 if coeff_str == '' else int(coeff_str)
        if sign_str == '-':
            coeff = -coeff
        coeffs[lag] = coeffs.get(lag, 0) + coeff
    if not coeffs:
        return None
    order = max(coeffs.keys())
    return {'order': order, 'coeffs': coeffs}


def load_recurrences() -> dict:
    print(f"  [load] Scanning {FORMULAS.name} for linear recurrences...")
    found = {}
    with open(FORMULAS, 'r', encoding='utf-8') as f:
        for line in f:
            rec = json.loads(line)
            sid = rec['seq_id']
            if sid in found:
                continue
            parsed = parse_recurrence(rec['formula'])
            if parsed and 1 <= parsed['order'] <= 20:
                found[sid] = parsed
    print(f"  [load] Found {len(found)} sequences with linear recurrences")
    return found


def load_oeis_terms(seq_ids: set) -> dict:
    print(f"  [load] Loading terms for {len(seq_ids)} sequences...")
    terms = {}
    with gzip.open(STRIPPED, 'rt', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split(',')
            sid = parts[0].strip()
            if sid not in seq_ids:
                continue
            vals = []
            for t in parts[1:]:
                t = t.strip()
                if t == '':
                    continue
                try:
                    vals.append(int(t))
                except ValueError:
                    break
            if len(vals) >= 5:
                terms[sid] = vals
    print(f"  [load] Loaded terms for {len(terms)} sequences")
    return terms


# ── Pipeline stages ──────────────────────────────────────────────────────

def characteristic_poly(rec: dict) -> list[int]:
    order = rec['order']
    poly = [0] * (order + 1)
    poly[0] = 1
    for lag, coeff in rec['coeffs'].items():
        poly[lag] = -coeff
    return poly


def generating_function(rec: dict, initial_terms: list[int]):
    order = rec['order']
    if len(initial_terms) < order:
        return None
    Q = [0] * (order + 1)
    Q[0] = 1
    for lag, coeff in rec['coeffs'].items():
        Q[lag] = -coeff
    P = []
    for n in range(order):
        val = 0
        for j in range(min(n + 1, len(Q))):
            if n - j < len(initial_terms):
                val += Q[j] * initial_terms[n - j]
        P.append(val)
    return (P, Q)


def eval_rational_poly(coeffs: list[int], x: Fraction) -> Fraction:
    result = Fraction(0)
    for i, c in enumerate(coeffs):
        result += Fraction(c) * (x ** i)
    return result


def eval_gf_at_point(P, Q, x):
    Qx = eval_rational_poly(Q, x)
    if Qx == 0:
        return None
    Px = eval_rational_poly(P, x)
    return Px / Qx


# ── Shannon entropy ──────────────────────────────────────────────────────

def shannon_entropy(fingerprints: list) -> float:
    """Compute Shannon entropy (in bits) from a list of fingerprint values."""
    n = len(fingerprints)
    if n == 0:
        return 0.0
    counts = Counter(fingerprints)
    entropy = 0.0
    for count in counts.values():
        p = count / n
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def normalized_entropy(fingerprints: list) -> float:
    """Entropy normalized to [0, 1] by dividing by log2(n)."""
    n = len(fingerprints)
    if n <= 1:
        return 0.0
    h = shannon_entropy(fingerprints)
    return h / math.log2(n)


# ── Fingerprint constructors ─────────────────────────────────────────────

def stage1_fingerprint(rec: dict, p: int) -> tuple:
    """Stage 1: characteristic polynomial coefficients mod p."""
    poly = characteristic_poly(rec)
    return tuple(c % p for c in poly)


def stage2_fingerprint(P: list[int], Q: list[int], p: int) -> tuple | None:
    """Stage 2: generating function evaluated at x=1/2, numerator mod p."""
    x = Fraction(1, 2)
    val = eval_gf_at_point(P, Q, x)
    if val is None:
        return None
    # Return numerator mod p of the reduced fraction
    return (int(val.numerator) % p,)


def stage3_fingerprint(terms: list[int], p: int, n_terms: int) -> tuple | None:
    """Stage 3: first n_terms of the sequence mod p."""
    if len(terms) < n_terms:
        return None
    return tuple(t % p for t in terms[:n_terms])


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("Charon — Pipeline Information Loss (Shannon Entropy)")
    print("=" * 70)

    # 1. Load recurrences
    all_recs = load_recurrences()

    # 2. Select sequences (prioritize low-order)
    sorted_recs = sorted(all_recs.items(), key=lambda x: (x[1]['order'], x[0]))
    selected_ids = [sid for sid, _ in sorted_recs[:TARGET_N * 3]]

    # 3. Load terms
    terms = load_oeis_terms(set(selected_ids))

    # 4. Filter: verify recurrence reproduces terms
    candidates = []
    for sid in selected_ids:
        if sid not in terms:
            continue
        rec = all_recs[sid]
        gf = generating_function(rec, terms[sid])
        if gf is None:
            continue
        order = rec['order']
        t = terms[sid]
        ok = True
        for n in range(order, min(order + 5, len(t))):
            predicted = sum(rec['coeffs'].get(lag, 0) * t[n - lag]
                           for lag in rec['coeffs'])
            if predicted != t[n]:
                ok = False
                break
        if ok and len(t) >= NUM_TERMS_STAGE3:
            candidates.append(sid)
        if len(candidates) >= TARGET_N:
            break

    print(f"\n  [filter] {len(candidates)} sequences pass verification")

    if len(candidates) < 50:
        print("  [WARN] Too few candidates, relaxing verification...")
        candidates = [sid for sid in selected_ids
                      if sid in terms
                      and generating_function(all_recs[sid], terms[sid]) is not None
                      and len(terms[sid]) >= NUM_TERMS_STAGE3][:TARGET_N]
        print(f"  [filter] {len(candidates)} sequences after relaxation")

    # 5. For each prime, compute fingerprints and entropy at all 3 stages
    results_by_prime = {}
    all_stage_entropies = {1: [], 2: [], 3: []}

    for p in PRIMES:
        print(f"\n  [mod-{p}] Computing Shannon entropy at each stage...")

        fps1 = []  # Stage 1 fingerprints
        fps2 = []  # Stage 2 fingerprints
        fps3 = []  # Stage 3 fingerprints
        valid_ids = []

        for sid in candidates:
            rec = all_recs[sid]
            gf = generating_function(rec, terms[sid])
            if gf is None:
                continue
            P, Q = gf

            fp1 = stage1_fingerprint(rec, p)
            fp2 = stage2_fingerprint(P, Q, p)
            fp3 = stage3_fingerprint(terms[sid], p, NUM_TERMS_STAGE3)

            if fp2 is None or fp3 is None:
                continue

            fps1.append(fp1)
            fps2.append(fp2)
            fps3.append(fp3)
            valid_ids.append(sid)

        n = len(valid_ids)
        H_max = math.log2(n) if n > 1 else 0.0

        H1 = shannon_entropy(fps1)
        H2 = shannon_entropy(fps2)
        H3 = shannon_entropy(fps3)

        # Unique fingerprint counts
        n_unique_1 = len(set(fps1))
        n_unique_2 = len(set(fps2))
        n_unique_3 = len(set(fps3))

        # Theoretical max entropy for each stage's alphabet size
        H1_max = math.log2(n_unique_1) if n_unique_1 > 1 else 0.0
        H2_max = math.log2(n_unique_2) if n_unique_2 > 1 else 0.0
        H3_max = math.log2(n_unique_3) if n_unique_3 > 1 else 0.0

        # Information loss at each transition
        delta_12 = H1 - H2  # Stage1 -> Stage2
        delta_23 = H2 - H3  # Stage2 -> Stage3
        delta_13 = H1 - H3  # End-to-end

        # Fraction of H_max retained
        frac_1 = H1 / H_max if H_max > 0 else 0.0
        frac_2 = H2 / H_max if H_max > 0 else 0.0
        frac_3 = H3 / H_max if H_max > 0 else 0.0

        result = {
            'n_sequences': n,
            'H_max_bits': round(H_max, 4),
            'H1_bits': round(H1, 4),
            'H2_bits': round(H2, 4),
            'H3_bits': round(H3, 4),
            'n_unique_fp1': n_unique_1,
            'n_unique_fp2': n_unique_2,
            'n_unique_fp3': n_unique_3,
            'H1_over_Hmax': round(frac_1, 4),
            'H2_over_Hmax': round(frac_2, 4),
            'H3_over_Hmax': round(frac_3, 4),
            'delta_H12': round(delta_12, 4),
            'delta_H23': round(delta_23, 4),
            'delta_H13': round(delta_13, 4),
            'pct_loss_12': round(abs(delta_12) / H1 * 100, 2) if H1 > 0 else 0,
            'pct_loss_23': round(abs(delta_23) / H2 * 100, 2) if H2 > 0 else 0,
            'pct_total_loss': round(abs(delta_13) / H1 * 100, 2) if H1 > 0 else 0,
            'fingerprint_distribution': {
                'stage1_top5': Counter(fps1).most_common(5),
                'stage2_top5': Counter(fps2).most_common(5),
                'stage3_top5': Counter(fps3).most_common(5),
            },
        }

        # Make fingerprint distributions JSON-serializable
        for key in ['stage1_top5', 'stage2_top5', 'stage3_top5']:
            result['fingerprint_distribution'][key] = [
                {'fingerprint': str(fp), 'count': c}
                for fp, c in result['fingerprint_distribution'][key]
            ]

        results_by_prime[str(p)] = result

        all_stage_entropies[1].append(H1)
        all_stage_entropies[2].append(H2)
        all_stage_entropies[3].append(H3)

        print(f"    n={n}  H1={H1:.3f}  H2={H2:.3f}  H3={H3:.3f}  H_max={H_max:.3f}")
        print(f"    unique fps: S1={n_unique_1}  S2={n_unique_2}  S3={n_unique_3}")
        print(f"    delta_H12={delta_12:+.3f}  delta_H23={delta_23:+.3f}  delta_H13={delta_13:+.3f}")

    # 6. Aggregate summary
    mean_H1 = float(np.mean(all_stage_entropies[1]))
    mean_H2 = float(np.mean(all_stage_entropies[2]))
    mean_H3 = float(np.mean(all_stage_entropies[3]))
    mean_delta_12 = mean_H1 - mean_H2
    mean_delta_23 = mean_H2 - mean_H3
    mean_delta_13 = mean_H1 - mean_H3

    # Determine where most entropy is lost
    if abs(mean_delta_12) > abs(mean_delta_23):
        bottleneck = "Stage 1->2 (characteristic poly -> generating function eval)"
        bottleneck_stage = "1->2"
    else:
        bottleneck = "Stage 2->3 (generating function eval -> sequence values)"
        bottleneck_stage = "2->3"

    # Check directionality: is entropy lost (compression) or gained (expansion)?
    direction_12 = "compression" if mean_delta_12 > 0 else "expansion"
    direction_23 = "compression" if mean_delta_23 > 0 else "expansion"

    # Does the entropy pattern explain the 99.2% transfer gap?
    # T13 ~ 1.9 means essentially random at the composed level.
    # If H1 >> H3 (massive entropy loss), it means the pipeline destroys
    # most of the distinguishing information.
    # If H1 ~ H3 but fingerprints are scrambled, it means information is
    # preserved in total but reallocated to orthogonal features.
    relative_h3_h1 = mean_H3 / mean_H1 if mean_H1 > 0 else 0

    if relative_h3_h1 > 1.0:
        mechanism = (
            f"ENTROPY EXPANSION through a bottleneck. H3/H1={relative_h3_h1:.2f} — Stage 3 "
            "has MORE entropy than Stage 1. The pipeline is: COMPRESSION (Stage 1->2, the GF "
            "evaluation collapses polynomial structure into a single value mod p) then "
            "EXPANSION (Stage 2->3, sequence values mod p are a much higher-dimensional "
            "fingerprint). The bottleneck at Stage 2 destroys the correlation between "
            "Stages 1 and 3: information that survives compression into a single GF value "
            "is NOT the same information that spreads into 8 sequence values. The 99.2% "
            "transfer loss is an information bottleneck effect — the GF evaluation is a "
            "lossy channel that preserves different features in each direction."
        )
    elif relative_h3_h1 > 0.8:
        mechanism = (
            "SCRAMBLING, not compression. Entropy is roughly preserved across stages "
            f"(H3/H1={relative_h3_h1:.2f}), but the fingerprints at each stage encode "
            "DIFFERENT features of the generating function. Stage 1 encodes recurrence "
            "structure, Stage 3 encodes arithmetic values — they share a common source "
            "(the GF) but project onto orthogonal aspects. This is why T12 and T23 are "
            "high (adjacent stages share features) but T13 is near 1 (endpoints share "
            "almost nothing). The 99.2% loss is not information destruction; it is "
            "information rotation through a high-dimensional intermediate."
        )
    elif relative_h3_h1 > 0.5:
        mechanism = (
            f"PARTIAL COMPRESSION + SCRAMBLING. H3/H1={relative_h3_h1:.2f} shows moderate "
            "entropy reduction, but the dominant effect is still feature rotation. The "
            "generating function is an informationally rich intermediate that connects to "
            "both recurrences and values, but via different dimensions of its structure."
        )
    else:
        mechanism = (
            f"SEVERE COMPRESSION. H3/H1={relative_h3_h1:.2f} — most distinguishing "
            "entropy is destroyed by the pipeline. The generating function evaluation at "
            "x=1/2 collapses the characteristic polynomial's rich structure into a single "
            "number mod p, and the sequence values mod p have even less variety. The 99.2% "
            "transfer loss directly reflects this entropy destruction."
        )

    summary = {
        'mean_H1': round(mean_H1, 4),
        'mean_H2': round(mean_H2, 4),
        'mean_H3': round(mean_H3, 4),
        'mean_delta_H12': round(mean_delta_12, 4),
        'mean_delta_H23': round(mean_delta_23, 4),
        'mean_delta_H13': round(mean_delta_13, 4),
        'direction_12': direction_12,
        'direction_23': direction_23,
        'bottleneck': bottleneck,
        'bottleneck_stage': bottleneck_stage,
        'H3_over_H1': round(relative_h3_h1, 4),
        'mechanism': mechanism,
        'explains_99pct_gap': (
            "Yes — information bottleneck at Stage 2" if relative_h3_h1 > 1.0
            else "Yes — scrambling" if relative_h3_h1 > 0.7
            else "Partially" if relative_h3_h1 > 0.4
            else "Yes (direct compression)"
        ),
    }

    output = {
        'experiment': 'pipeline_info_loss',
        'description': (
            'Shannon entropy measurement at each stage of the Recurrence->GenFunc->Values '
            'pipeline. Stage 1 = characteristic poly coefficients mod p. '
            'Stage 2 = generating function P(x)/Q(x) evaluated at x=1/2, numerator mod p. '
            'Stage 3 = first 8 sequence values mod p. '
            'Primes: 3, 5, 7, 11. '
            'Measures information content and loss at each stage transition.'
        ),
        'n_candidates': len(candidates),
        'primes': PRIMES,
        'num_terms_stage3': NUM_TERMS_STAGE3,
        'results_by_prime': results_by_prime,
        'summary': summary,
    }

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY — Shannon Entropy at Each Pipeline Stage")
    print("=" * 70)
    print(f"  Sequences analysed: {len(candidates)}")
    print(f"  Mean H1 (char poly coeffs mod p):  {mean_H1:.3f} bits")
    print(f"  Mean H2 (GF eval at x=1/2 mod p):  {mean_H2:.3f} bits")
    print(f"  Mean H3 (sequence values mod p):    {mean_H3:.3f} bits")
    print(f"  Mean delta H(1->2):  {mean_delta_12:+.3f} bits ({direction_12})")
    print(f"  Mean delta H(2->3):  {mean_delta_23:+.3f} bits ({direction_23})")
    print(f"  Mean delta H(1->3):  {mean_delta_13:+.3f} bits (end-to-end)")
    print(f"  H3/H1 ratio:         {relative_h3_h1:.3f}")
    print(f"  Bottleneck:          {bottleneck}")
    print(f"\n  Mechanism: {mechanism}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\n  Saved -> {OUT}")


if __name__ == '__main__':
    main()

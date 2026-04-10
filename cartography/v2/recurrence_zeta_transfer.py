#!/usr/bin/env python3
"""
Charon — Recurrence-to-Zeta Transfer Efficiency (Frontier #20).
================================================================
Rosetta axis: Recurrence -> Series -> Zeta (from X11).
Measure information loss at each stage of this pipeline.

Pipeline:
  Stage 1: Characteristic polynomial of a linear recurrence a(n) = sum c_i a(n-i).
           Fingerprint = coefficients mod p.
  Stage 2: Generating function = P(x)/Q(x) where Q(x)=characteristic poly (reversed),
           P(x) determined by initial conditions.  Fingerprint = (P coefs, Q coefs) mod p.
  Stage 3: Evaluate the generating function at special zeta-related points:
           x = 1/2 (zeta critical line), x = 1/pi^2 (related to zeta(2)=pi^2/6),
           x = 1/e (exponential).  Fingerprint = numerator of rational approx mod p.

Transfer efficiency T_ij = P(Stage_j match | Stage_i match) / P(Stage_j match | random).
If T >> 1: structure preserved.  If T ~ 1: information lost.

Reads:
  - cartography/oeis/data/oeis_formulas.jsonl  (recurrence formulas)
  - cartography/oeis/data/stripped_full.gz      (sequence terms)

Writes:
  - cartography/v2/recurrence_zeta_transfer_results.json
"""

import gzip
import json
import math
import re
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import numpy as np

# ── paths ────────────────────────────────────────────────────────────────
REPO = Path(__file__).resolve().parents[2]
CARTOGRAPHY = REPO / "cartography"
FORMULAS = CARTOGRAPHY / "oeis" / "data" / "oeis_formulas.jsonl"
STRIPPED = CARTOGRAPHY / "oeis" / "data" / "stripped_full.gz"
OUT = Path(__file__).resolve().parent / "recurrence_zeta_transfer_results.json"

PRIMES = [2, 3, 5, 7, 11, 13]
TARGET_N = 500  # number of sequences to analyse
EVAL_POINTS = {
    "x=1/2": Fraction(1, 2),
    "x=1/4": Fraction(1, 4),
    "x=1/10": Fraction(1, 10),
}

# ── Step 1: Parse linear recurrences from OEIS formulas ─────────────────

# Pattern: a(n) = c1*a(n-1) + c2*a(n-2) + ... (with optional signs, optional *)
# We parse formulas like:
#   a(n) = 2*a(n-1) - a(n-2)
#   a(n) = a(n-1) + a(n-2)
#   a(n) = 3*a(n-1) + 2*a(n-2) + a(n-3)

RECURRENCE_PATTERN = re.compile(
    r'a\(n\)\s*=\s*'                     # LHS
    r'((?:[+-]?\s*\d*\s*\*?\s*a\(n-\d+\)\s*)+)',  # RHS: sum of c*a(n-k) terms
    re.IGNORECASE
)

TERM_PATTERN = re.compile(
    r'([+-]?)\s*(\d*)\s*\*?\s*a\(n-(\d+)\)'
)


def parse_recurrence(formula: str) -> dict | None:
    """
    Parse a linear recurrence from a formula string.
    Returns {order: int, coeffs: {lag: coeff}} or None.
    Only accepts pure linear recurrences (no extra additive terms).
    """
    m = RECURRENCE_PATTERN.search(formula)
    if not m:
        return None
    rhs_str = m.group(1)
    # Check there's nothing else significant in the formula after the recurrence
    full_rhs = formula[formula.index('=') + 1:].strip()
    # Remove the matched recurrence terms
    cleaned = TERM_PATTERN.sub('', full_rhs).strip()
    # Allow trailing period, comma, attribution
    cleaned = re.sub(r'[.,;].*', '', cleaned).strip()
    cleaned = re.sub(r'[+-]\s*$', '', cleaned).strip()
    if cleaned and cleaned != '0':
        # There's extra stuff (like + n or + 1) — not pure linear recurrence
        return None

    coeffs = {}
    for tm in TERM_PATTERN.finditer(rhs_str):
        sign_str = tm.group(1).strip()
        coeff_str = tm.group(2).strip()
        lag = int(tm.group(3))

        if coeff_str == '' or coeff_str == '':
            coeff = 1
        else:
            coeff = int(coeff_str)

        if sign_str == '-':
            coeff = -coeff

        if lag in coeffs:
            coeffs[lag] += coeff
        else:
            coeffs[lag] = coeff

    if not coeffs:
        return None

    order = max(coeffs.keys())
    return {'order': order, 'coeffs': coeffs}


def load_recurrences() -> dict:
    """
    Scan OEIS formulas for linear recurrences.
    Returns {seq_id: {order, coeffs}} for the first good recurrence per sequence.
    """
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


# ── Step 2: Load OEIS terms ─────────────────────────────────────────────

def load_oeis_terms(seq_ids: set) -> dict:
    """Load terms for specified sequence IDs from stripped_full.gz."""
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


# ── Step 3: Characteristic polynomial (Stage 1) ─────────────────────────

def characteristic_poly(rec: dict) -> list[int]:
    """
    Build characteristic polynomial from recurrence coefficients.
    For a(n) = c1*a(n-1) + c2*a(n-2) + ... + ck*a(n-k),
    characteristic poly is x^k - c1*x^(k-1) - c2*x^(k-2) - ... - ck.
    Returns coefficients [leading, ..., constant] of degree k.
    """
    order = rec['order']
    # Poly: x^k - c1*x^{k-1} - c2*x^{k-2} - ... - ck
    poly = [0] * (order + 1)
    poly[0] = 1  # x^k coefficient
    for lag, coeff in rec['coeffs'].items():
        poly[lag] = -coeff  # coefficient of x^{k-lag}
    return poly


# ── Step 4: Generating function P(x)/Q(x) (Stage 2) ────────────────────

def generating_function(rec: dict, initial_terms: list[int]) -> tuple[list[int], list[int]] | None:
    """
    Compute P(x)/Q(x) generating function.
    Q(x) = 1 - c1*x - c2*x^2 - ... - ck*x^k  (denominator).
    P(x) is determined by Q(x) * (sum_{n>=0} a(n) x^n) truncated to degree < k.
    Returns (P_coeffs, Q_coeffs) or None if insufficient terms.
    """
    order = rec['order']
    if len(initial_terms) < order:
        return None

    # Q(x) coefficients: Q[0]=1, Q[i] = -c_i for i=1..order
    Q = [0] * (order + 1)
    Q[0] = 1
    for lag, coeff in rec['coeffs'].items():
        Q[lag] = -coeff

    # P(x) = Q(x) * A(x) truncated to terms x^0 through x^{order-1}
    # where A(x) = sum a(n) x^n
    P = []
    for n in range(order):
        val = 0
        for j in range(min(n + 1, len(Q))):
            if n - j < len(initial_terms):
                val += Q[j] * initial_terms[n - j]
        P.append(val)

    return (P, Q)


# ── Step 5: Evaluate at special points (Stage 3) ────────────────────────

def eval_rational_poly(coeffs: list[int], x: Fraction) -> Fraction:
    """Evaluate polynomial with integer coefficients at a Fraction point."""
    result = Fraction(0)
    for i, c in enumerate(coeffs):
        result += Fraction(c) * (x ** i)
    return result


def eval_gf_at_point(P: list[int], Q: list[int], x: Fraction) -> Fraction | None:
    """Evaluate P(x)/Q(x) at a rational point. Returns None if Q(x)=0."""
    Qx = eval_rational_poly(Q, x)
    if Qx == 0:
        return None
    Px = eval_rational_poly(P, x)
    return Px / Qx


# ── Step 6: Mod-p fingerprints ──────────────────────────────────────────

def modp_fingerprint_poly(coeffs: list[int], p: int) -> tuple:
    """Fingerprint a polynomial by its coefficients mod p."""
    return tuple(c % p for c in coeffs)


def modp_fingerprint_stage1(rec: dict, p: int) -> tuple:
    """Stage 1: characteristic polynomial mod p."""
    poly = characteristic_poly(rec)
    return modp_fingerprint_poly(poly, p)


def modp_fingerprint_stage2(P: list[int], Q: list[int], p: int) -> tuple:
    """Stage 2: (P mod p, Q mod p) as fingerprint."""
    return (modp_fingerprint_poly(P, p), modp_fingerprint_poly(Q, p))


def modp_fingerprint_stage3(values: dict[str, Fraction], p: int) -> tuple | None:
    """
    Stage 3: for each evaluation point, take numerator mod p.
    Uses the numerator of the fully reduced fraction.
    """
    fps = []
    for key in sorted(values.keys()):
        v = values[key]
        if v is None:
            return None
        fps.append(int(v.numerator) % p)
    return tuple(fps)


# ── Step 7: Enrichment and transfer efficiency ──────────────────────────

def compute_enrichment(fp_groups_source: dict, fp_groups_target: dict,
                       all_ids: list[str]) -> float:
    """
    Enrichment = P(target match | source match) / P(target match | random).

    For each pair sharing a source fingerprint, check if they also share
    a target fingerprint. Compare to random baseline.
    """
    # Build target fingerprint lookup
    target_fp = {}
    for fp, ids in fp_groups_target.items():
        for sid in ids:
            target_fp[sid] = fp

    # Count pairs sharing source fingerprint
    source_pairs = 0
    source_and_target = 0
    for fp, ids in fp_groups_source.items():
        if len(ids) < 2:
            continue
        ids_list = sorted(ids)
        for i in range(len(ids_list)):
            for j in range(i + 1, len(ids_list)):
                a, b = ids_list[i], ids_list[j]
                if a in target_fp and b in target_fp:
                    source_pairs += 1
                    if target_fp[a] == target_fp[b]:
                        source_and_target += 1

    if source_pairs == 0:
        return float('nan')

    p_target_given_source = source_and_target / source_pairs

    # Random baseline: fraction of all pairs sharing target fingerprint
    n = len(all_ids)
    total_pairs = n * (n - 1) / 2
    random_target_matches = 0
    for fp, ids in fp_groups_target.items():
        k = len(ids)
        random_target_matches += k * (k - 1) / 2

    p_target_random = random_target_matches / total_pairs if total_pairs > 0 else 0

    if p_target_random == 0:
        return float('inf') if source_and_target > 0 else 1.0

    enrichment = p_target_given_source / p_target_random
    return enrichment


def group_by_fingerprint(fingerprints: dict) -> dict:
    """Group sequence IDs by their fingerprint value."""
    groups = defaultdict(set)
    for sid, fp in fingerprints.items():
        groups[fp].add(sid)
    return dict(groups)


# ── Main ────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("Charon — Recurrence-to-Zeta Transfer Efficiency")
    print("=" * 70)

    # 1. Load recurrences
    all_recs = load_recurrences()

    # 2. Select sequences (prioritize low-order for cleaner analysis)
    sorted_recs = sorted(all_recs.items(), key=lambda x: (x[1]['order'], x[0]))
    selected_ids = [sid for sid, _ in sorted_recs[:TARGET_N * 3]]

    # 3. Load terms
    terms = load_oeis_terms(set(selected_ids))

    # 4. Filter to those with enough terms and valid generating functions
    candidates = []
    for sid in selected_ids:
        if sid not in terms:
            continue
        rec = all_recs[sid]
        gf = generating_function(rec, terms[sid])
        if gf is None:
            continue
        # Verify: check that the recurrence actually reproduces the terms
        P, Q = gf
        ok = True
        order = rec['order']
        t = terms[sid]
        for n in range(order, min(order + 5, len(t))):
            predicted = sum(rec['coeffs'].get(lag, 0) * t[n - lag]
                           for lag in rec['coeffs'])
            if predicted != t[n]:
                ok = False
                break
        if ok:
            candidates.append(sid)
        if len(candidates) >= TARGET_N:
            break

    print(f"\n  [filter] {len(candidates)} sequences pass recurrence verification")
    if len(candidates) < 50:
        print("  [WARN] Too few candidates, relaxing verification...")
        candidates = [sid for sid in selected_ids if sid in terms
                      and generating_function(all_recs[sid], terms[sid]) is not None][:TARGET_N]
        print(f"  [filter] {len(candidates)} sequences after relaxation")

    # 5. Compute fingerprints at all three stages for each prime
    results_by_prime = {}

    for p in PRIMES:
        print(f"\n  [mod-{p}] Computing fingerprints...")
        fp_stage1 = {}
        fp_stage2 = {}
        fp_stage3 = {}

        for sid in candidates:
            rec = all_recs[sid]
            gf = generating_function(rec, terms[sid])
            if gf is None:
                continue
            P, Q = gf

            # Stage 1: characteristic polynomial mod p
            fp_stage1[sid] = modp_fingerprint_stage1(rec, p)

            # Stage 2: generating function (P, Q) mod p
            fp_stage2[sid] = modp_fingerprint_stage2(P, Q, p)

            # Stage 3: evaluate at special points
            evals = {}
            valid = True
            for name, x in EVAL_POINTS.items():
                v = eval_gf_at_point(P, Q, x)
                if v is None:
                    valid = False
                    break
                evals[name] = v
            if valid:
                fp3 = modp_fingerprint_stage3(evals, p)
                if fp3 is not None:
                    fp_stage3[sid] = fp3

        common_ids = sorted(set(fp_stage1) & set(fp_stage2) & set(fp_stage3))
        # Restrict to common set
        fp1 = {s: fp_stage1[s] for s in common_ids}
        fp2 = {s: fp_stage2[s] for s in common_ids}
        fp3 = {s: fp_stage3[s] for s in common_ids}

        g1 = group_by_fingerprint(fp1)
        g2 = group_by_fingerprint(fp2)
        g3 = group_by_fingerprint(fp3)

        # Enrichment: T_12 and T_23
        T_12 = compute_enrichment(g1, g2, common_ids)
        T_23 = compute_enrichment(g2, g3, common_ids)
        T_13 = compute_enrichment(g1, g3, common_ids)

        # Collision stats
        def collision_stats(groups):
            sizes = [len(v) for v in groups.values()]
            n_collisions = sum(1 for s in sizes if s > 1)
            max_size = max(sizes) if sizes else 0
            mean_size = np.mean(sizes) if sizes else 0
            return {
                'n_fingerprints': len(groups),
                'n_colliding': n_collisions,
                'max_group': max_size,
                'mean_group': round(float(mean_size), 3),
            }

        results_by_prime[str(p)] = {
            'n_sequences': len(common_ids),
            'T_12': round(T_12, 4) if not math.isnan(T_12) else None,
            'T_23': round(T_23, 4) if not math.isnan(T_23) else None,
            'T_13': round(T_13, 4) if not math.isnan(T_13) else None,
            'stage1_stats': collision_stats(g1),
            'stage2_stats': collision_stats(g2),
            'stage3_stats': collision_stats(g3),
        }

        print(f"    n={len(common_ids)}  T_12={T_12:.3f}  T_23={T_23:.3f}  T_13={T_13:.3f}")
        print(f"    Stage1 groups: {len(g1)}  Stage2 groups: {len(g2)}  Stage3 groups: {len(g3)}")

    # 6. Aggregate across primes
    T12_vals = [v['T_12'] for v in results_by_prime.values() if v['T_12'] is not None]
    T23_vals = [v['T_23'] for v in results_by_prime.values() if v['T_23'] is not None]
    T13_vals = [v['T_13'] for v in results_by_prime.values() if v['T_13'] is not None]

    summary = {
        'mean_T_12': round(float(np.mean(T12_vals)), 4) if T12_vals else None,
        'mean_T_23': round(float(np.mean(T23_vals)), 4) if T23_vals else None,
        'mean_T_13': round(float(np.mean(T13_vals)), 4) if T13_vals else None,
        'interpretation': '',
    }

    # Interpret
    if summary['mean_T_12'] is not None and summary['mean_T_23'] is not None:
        t12 = summary['mean_T_12']
        t23 = summary['mean_T_23']
        t13 = summary['mean_T_13'] if summary['mean_T_13'] is not None else 0
        # Key diagnostic: T_13 << T_12 * T_23 means adjacent-stage
        # correlations compound poorly -- each step preserves LOCAL structure
        # but the composition is lossy.
        if t12 > 2.0 and t23 > 2.0 and t13 > 2.0:
            summary['interpretation'] = (
                f"All transfers preserve structure (T_12={t12:.2f}, T_23={t23:.2f}, "
                f"T_13={t13:.2f}). The full Recurrence->Zeta pipeline is an "
                "efficient information conduit."
            )
        elif t12 > 2.0 and t23 > 2.0 and t13 <= 2.0:
            summary['interpretation'] = (
                f"Adjacent stages preserve structure (T_12={t12:.2f}, T_23={t23:.2f}) "
                f"but the end-to-end transfer is weak (T_13={t13:.2f}). "
                "This is a 'leaky pipe': each joint is tight but the composition "
                "loses coherence. The generating function acts as a scrambler — "
                "it preserves recurrence structure AND predicts zeta evaluations, "
                "but via different features at each interface."
            )
        elif t12 > 2.0 and t23 <= 2.0:
            summary['interpretation'] = (
                f"Stage 1->2 preserves structure (T_12={t12:.2f}) but Stage 2->3 loses it "
                f"(T_23={t23:.2f}). Information is lost at the zeta evaluation step."
            )
        elif t12 <= 2.0 and t23 > 2.0:
            summary['interpretation'] = (
                f"Stage 1->2 loses information (T_12={t12:.2f}) but Stage 2->3 preserves it "
                f"(T_23={t23:.2f}). The generating function adds discriminative power."
            )
        else:
            summary['interpretation'] = (
                f"Both stages show weak transfer (T_12={t12:.2f}, T_23={t23:.2f}). "
                "Each pipeline stage loses mod-p structure independently."
            )

    # 7. Collect example sequences for inspection
    examples = []
    for sid in candidates[:10]:
        rec = all_recs[sid]
        gf = generating_function(rec, terms[sid])
        if gf is None:
            continue
        P, Q = gf
        char_poly = characteristic_poly(rec)
        evals = {}
        for name, x in EVAL_POINTS.items():
            v = eval_gf_at_point(P, Q, x)
            if v is not None:
                evals[name] = f"{float(v):.8g}"
        examples.append({
            'seq_id': sid,
            'order': rec['order'],
            'coeffs': {str(k): v for k, v in rec['coeffs'].items()},
            'char_poly': char_poly,
            'P': P,
            'Q': Q,
            'gf_evals': evals,
            'first_terms': terms[sid][:12],
        })

    # 8. Order distribution
    orders = [all_recs[sid]['order'] for sid in candidates]
    order_dist = defaultdict(int)
    for o in orders:
        order_dist[o] += 1

    output = {
        'experiment': 'recurrence_zeta_transfer',
        'description': (
            'Rosetta axis Recurrence->Series->Zeta transfer efficiency. '
            'Measures mod-p fingerprint enrichment at each pipeline stage: '
            'Stage 1 (characteristic polynomial), Stage 2 (generating function P/Q), '
            'Stage 3 (evaluate at zeta-related points x=1/2, 1/4, 1/10). '
            'T_ij = P(stage_j match | stage_i match) / P(stage_j match | random).'
        ),
        'n_candidates': len(candidates),
        'order_distribution': dict(sorted(order_dist.items())),
        'primes': PRIMES,
        'eval_points': {k: str(v) for k, v in EVAL_POINTS.items()},
        'results_by_prime': results_by_prime,
        'summary': summary,
        'examples': examples,
    }

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Sequences analysed: {len(candidates)}")
    print(f"  Mean T_12 (Recurrence->GenFunc): {summary['mean_T_12']}")
    print(f"  Mean T_23 (GenFunc->Zeta eval):  {summary['mean_T_23']}")
    print(f"  Mean T_13 (Recurrence->Zeta):    {summary['mean_T_13']}")
    print(f"  {summary['interpretation']}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    print(f"\n  Saved -> {OUT}")


if __name__ == '__main__':
    main()

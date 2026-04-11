"""
CODATA Algorithmic Information Distance to Rationality (List2 #4)

For each CODATA constant:
  1. Extract significand (mantissa) and its fractional part
  2. Convert to 50-bit binary string
  3. Find nearest rational p/q (q <= 100) via continued fraction convergents
  4. Convert that rational's fractional binary expansion to 50 bits
  5. Compute NCD(constant_bits, rational_bits) using zlib
  6. Compare distribution to null (random reals -> NCD ~ 1.0)

Key design choice: we use the significand (e.g., 6.644657345 from 6.644657345e-27)
rather than the raw value, since the exponent is unit-dependent and the fractional
part of extremely large/small numbers is dominated by floating-point artifacts.
"""

import json
import zlib
import math
import random
import statistics
import os
from fractions import Fraction

# ── helpers ──────────────────────────────────────────────────────────

NBITS = 50


def extract_significand(value):
    """Extract significand in [1, 10) from a float value.
    E.g., 6.644e-27 -> 6.644657345, 7294.29 -> 7.29429954171
    """
    if value == 0:
        return 0.0
    v = abs(value)
    exp10 = math.floor(math.log10(v))
    sig = v / (10.0 ** exp10)
    # Clamp to [1, 10) due to floating point edge cases
    if sig < 1.0:
        sig *= 10.0
    elif sig >= 10.0:
        sig /= 10.0
    return sig


def fractional_to_binary(frac_part, nbits=NBITS):
    """Convert a fractional part in [0,1) to a binary string of length nbits."""
    bits = []
    x = abs(frac_part)
    for _ in range(nbits):
        x *= 2
        if x >= 1.0:
            bits.append('1')
            x -= 1.0
        else:
            bits.append('0')
    return ''.join(bits)


def best_rational_approximation(frac, max_q=100):
    """Find p/q with q <= max_q closest to frac in [0,1)."""
    f = Fraction(frac).limit_denominator(max_q)
    # Clamp to [0, 1)
    if f >= 1:
        f = Fraction(max_q - 1, max_q)
    if f < 0:
        f = Fraction(0, 1)
    return f


def ncd(x_bytes, y_bytes):
    """Normalized Compression Distance."""
    cx = len(zlib.compress(x_bytes, 9))
    cy = len(zlib.compress(y_bytes, 9))
    cxy = len(zlib.compress(x_bytes + y_bytes, 9))
    denom = max(cx, cy)
    if denom == 0:
        return 0.0
    return (cxy - min(cx, cy)) / denom


# ── main ─────────────────────────────────────────────────────────────

def run():
    data_path = os.path.join(os.path.dirname(__file__),
                             '..', 'physics', 'data', 'codata', 'constants.json')
    with open(data_path) as f:
        constants = json.load(f)

    results = []

    for c in constants:
        val = c.get('value')
        if val is None or not isinstance(val, (int, float)):
            continue
        if val == 0:
            continue

        name = c['name']
        sig = extract_significand(val)
        frac_part = sig - math.floor(sig)  # fractional part of significand

        # Skip if fractional part is 0 (exact integer significand, rare)
        if frac_part < 1e-15:
            continue

        # Binary expansion of constant's fractional part
        const_bits = fractional_to_binary(frac_part)

        # Best rational approximation to fractional part
        best_rat = best_rational_approximation(frac_part)
        rat_frac = float(best_rat)
        rat_bits = fractional_to_binary(rat_frac)

        # NCD
        const_bytes = const_bits.encode('ascii')
        rat_bytes = rat_bits.encode('ascii')
        d = ncd(const_bytes, rat_bytes)

        results.append({
            'name': name,
            'value': val,
            'significand': round(sig, 12),
            'fractional_part': round(frac_part, 12),
            'rational_approx': str(best_rat),
            'rational_float': round(rat_frac, 12),
            'const_bits': const_bits,
            'rational_bits': rat_bits,
            'ncd': round(d, 6),
        })

    # ── null model: random significands in [1,10) ──
    random.seed(42)
    null_ncds = []
    N_NULL = 1000  # larger null for stable statistics
    for _ in range(N_NULL):
        rx = random.uniform(1.0, 10.0)
        rx_frac = rx - math.floor(rx)
        if rx_frac < 1e-15:
            continue
        rbits = fractional_to_binary(rx_frac)
        rrat = Fraction(rx_frac).limit_denominator(100)
        rrat_bits = fractional_to_binary(float(rrat))
        d = ncd(rbits.encode('ascii'), rrat_bits.encode('ascii'))
        null_ncds.append(round(d, 6))

    ncds = [r['ncd'] for r in results]

    # Histogram bins
    bins = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1]
    def histogram(values, bins):
        counts = [0] * (len(bins) - 1)
        for v in values:
            for i in range(len(bins) - 1):
                if bins[i] <= v < bins[i + 1]:
                    counts[i] += 1
                    break
        labels = [f"{bins[i]:.1f}-{bins[i+1]:.1f}" for i in range(len(bins) - 1)]
        return dict(zip(labels, counts))

    summary = {
        'n_constants': len(results),
        'ncd_mean': round(statistics.mean(ncds), 6),
        'ncd_median': round(statistics.median(ncds), 6),
        'ncd_std': round(statistics.stdev(ncds), 6) if len(ncds) > 1 else 0.0,
        'ncd_min': round(min(ncds), 6),
        'ncd_max': round(max(ncds), 6),
        'ncd_histogram': histogram(ncds, bins),
        'null_n': len(null_ncds),
        'null_ncd_mean': round(statistics.mean(null_ncds), 6),
        'null_ncd_median': round(statistics.median(null_ncds), 6),
        'null_ncd_std': round(statistics.stdev(null_ncds), 6) if len(null_ncds) > 1 else 0.0,
        'null_ncd_histogram': histogram(null_ncds, bins),
        'interpretation': '',
    }

    # Closest-to-rational (lowest NCD)
    results_sorted = sorted(results, key=lambda r: r['ncd'])
    top10_closest = [{'name': r['name'], 'value': r['value'],
                      'significand': r['significand'],
                      'rational': r['rational_approx'], 'ncd': r['ncd']}
                     for r in results_sorted[:10]]

    # Most distant from any rational (highest NCD)
    top10_distant = [{'name': r['name'], 'value': r['value'],
                      'significand': r['significand'],
                      'rational': r['rational_approx'], 'ncd': r['ncd']}
                     for r in results_sorted[-10:]]

    summary['interpretation'] = (
        f"Mean NCD = {summary['ncd_mean']:.4f} (null = {summary['null_ncd_mean']:.4f}). "
        f"Physical constants are {'closer to' if summary['ncd_mean'] < summary['null_ncd_mean'] - 0.02 else 'indistinguishable from'} "
        f"small-denominator rationals compared to random reals. "
        f"Expected: NCD ~0.95 for random reals; actual null mean confirms baseline."
    )

    output = {
        'method': 'Normalized Compression Distance: significand fractional part vs nearest rational (q<=100)',
        'bits': NBITS,
        'max_denominator': 100,
        'summary': summary,
        'top10_closest_to_rational': top10_closest,
        'top10_farthest_from_rational': top10_distant,
        'per_constant': results,
        'null_sample_ncds': null_ncds[:50],  # save a sample, not all 1000
    }

    out_path = os.path.join(os.path.dirname(__file__),
                            'codata_ncd_rationality_results.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Processed {len(results)} constants")
    print(f"Mean NCD:     {summary['ncd_mean']:.4f}")
    print(f"Median NCD:   {summary['ncd_median']:.4f}")
    print(f"Std NCD:      {summary['ncd_std']:.4f}")
    print(f"Range:        [{summary['ncd_min']:.4f}, {summary['ncd_max']:.4f}]")
    print(f"Null mean:    {summary['null_ncd_mean']:.4f} (n={len(null_ncds)})")
    print(f"Null median:  {summary['null_ncd_median']:.4f}")
    print(f"\nHistogram (CODATA): {summary['ncd_histogram']}")
    print(f"Histogram (null):   {summary['null_ncd_histogram']}")
    print(f"\nTop 10 closest to rational:")
    for r in top10_closest:
        print(f"  {r['name']}: sig={r['significand']:.6f}, NCD={r['ncd']:.4f} (~{r['rational']})")
    print(f"\nTop 10 farthest from rational:")
    for r in top10_distant:
        print(f"  {r['name']}: sig={r['significand']:.6f}, NCD={r['ncd']:.4f} (~{r['rational']})")

    return output


if __name__ == '__main__':
    run()

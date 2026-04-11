"""
j-Invariant Arithmetic Noise Floor (ChatGPT Harder #16)

Measure the minimal achievable compression rate of j-invariant digit streams.
Are j-invariants pseudorandom or structured?

For each EC j-invariant p/q:
  - Extract decimal digit strings of numerator and denominator
  - Compress with zlib (LZ77 + Huffman)
  - Compression ratio = compressed_size / uncompressed_size
Compare against random integers of same size, conductor digits, discriminant digits.

Charon — 2026-04-10
"""

import json
import zlib
import random
import statistics
import sys
from pathlib import Path

import duckdb
import numpy as np

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DB_PATH = Path(__file__).resolve().parent.parent.parent / "charon" / "data" / "charon.duckdb"
OUT_PATH = Path(__file__).resolve().parent / "jinvariant_noise_floor_results.json"
SEED = 42

# ---------------------------------------------------------------------------
# Compression helpers
# ---------------------------------------------------------------------------

def compress_ratio(data: bytes) -> float:
    """Compression ratio = compressed / uncompressed. Lower = more structure."""
    if len(data) == 0:
        return 1.0
    compressed = zlib.compress(data, level=9)
    return len(compressed) / len(data)


def int_to_digit_bytes(n: float) -> bytes:
    """Convert a float-stored integer to its decimal digit string as bytes."""
    # Handle sign: we want the absolute digit string
    val = abs(int(n))
    return str(val).encode('ascii')


def random_integer_bytes(n_digits: int, rng: random.Random) -> bytes:
    """Generate a random integer with exactly n_digits digits as byte string."""
    if n_digits <= 0:
        return b'0'
    if n_digits == 1:
        return str(rng.randint(0, 9)).encode('ascii')
    # First digit 1-9, rest 0-9
    first = str(rng.randint(1, 9))
    rest = ''.join(str(rng.randint(0, 9)) for _ in range(n_digits - 1))
    return (first + rest).encode('ascii')


def summarize(ratios: list) -> dict:
    """Statistical summary of compression ratios."""
    if not ratios:
        return {"n": 0}
    arr = np.array(ratios)
    return {
        "n": len(ratios),
        "mean": round(float(np.mean(arr)), 6),
        "median": round(float(np.median(arr)), 6),
        "std": round(float(np.std(arr)), 6),
        "p5": round(float(np.percentile(arr, 5)), 6),
        "p25": round(float(np.percentile(arr, 25)), 6),
        "p75": round(float(np.percentile(arr, 75)), 6),
        "p95": round(float(np.percentile(arr, 95)), 6),
        "min": round(float(np.min(arr)), 6),
        "max": round(float(np.max(arr)), 6),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    rng = random.Random(SEED)

    print(f"Loading from {DB_PATH} ...")
    con = duckdb.connect(str(DB_PATH), read_only=True)

    # Load j-invariant numerators, denominators, conductors
    rows = con.execute("""
        SELECT jinv_num, jinv_den, conductor
        FROM elliptic_curves
        WHERE jinv_num IS NOT NULL AND jinv_den IS NOT NULL
    """).fetchall()
    print(f"Loaded {len(rows)} curves with j-invariants.")

    # Also grab discriminants from ainvs if available, or use conductor as proxy
    # discriminant not stored directly — we'll use conductor as a comparison integer stream

    jinv_num_ratios = []
    jinv_den_ratios = []
    jinv_combined_ratios = []
    conductor_ratios = []
    random_num_ratios = []
    random_den_ratios = []

    # Bin by digit count for size-matched analysis
    size_bins = {}  # digit_count -> {jinv_num: [], random: []}

    skipped_small = 0

    for jinv_num, jinv_den, conductor in rows:
        # Numerator digits
        num_bytes = int_to_digit_bytes(jinv_num)
        den_bytes = int_to_digit_bytes(jinv_den)
        cond_bytes = str(int(conductor)).encode('ascii')

        # Skip trivially small values (< 4 digits) — compression meaningless
        if len(num_bytes) < 4 and len(den_bytes) < 4:
            skipped_small += 1
            continue

        # j-invariant numerator
        if len(num_bytes) >= 4:
            r_num = compress_ratio(num_bytes)
            jinv_num_ratios.append(r_num)

            n_digits = len(num_bytes)
            rand_bytes = random_integer_bytes(n_digits, rng)
            r_rand = compress_ratio(rand_bytes)
            random_num_ratios.append(r_rand)

            # Size-binned
            bin_key = n_digits
            if bin_key not in size_bins:
                size_bins[bin_key] = {"jinv": [], "random": []}
            size_bins[bin_key]["jinv"].append(r_num)
            size_bins[bin_key]["random"].append(r_rand)

        # j-invariant denominator
        if len(den_bytes) >= 4:
            r_den = compress_ratio(den_bytes)
            jinv_den_ratios.append(r_den)
            rand_den = random_integer_bytes(len(den_bytes), rng)
            random_den_ratios.append(compress_ratio(rand_den))

        # Combined: numerator + "/" + denominator
        combined = num_bytes + b'/' + den_bytes
        if len(combined) >= 8:
            jinv_combined_ratios.append(compress_ratio(combined))

        # Conductor
        if len(cond_bytes) >= 4:
            conductor_ratios.append(compress_ratio(cond_bytes))

    print(f"Skipped {skipped_small} curves with trivially small j-invariants.")
    print(f"j-inv numerators: {len(jinv_num_ratios)}")
    print(f"j-inv denominators: {len(jinv_den_ratios)}")
    print(f"j-inv combined: {len(jinv_combined_ratios)}")
    print(f"Conductors: {len(conductor_ratios)}")

    # ---------------------------------------------------------------------------
    # Bulk compression: concatenate ALL digit strings and compress as a stream
    # This tests inter-curve structure (are j-invariants related across curves?)
    # ---------------------------------------------------------------------------
    all_num_bytes = b','.join(int_to_digit_bytes(r[0]) for r in rows)
    all_den_bytes = b','.join(int_to_digit_bytes(r[1]) for r in rows)
    all_cond_bytes = b','.join(str(int(r[2])).encode('ascii') for r in rows)

    # Random stream of same total length
    all_rand_bytes = b','.join(
        random_integer_bytes(len(int_to_digit_bytes(r[0])), rng) for r in rows
    )

    bulk_results = {
        "jinv_numerators_bulk": {
            "uncompressed_bytes": len(all_num_bytes),
            "ratio": round(compress_ratio(all_num_bytes), 6),
        },
        "jinv_denominators_bulk": {
            "uncompressed_bytes": len(all_den_bytes),
            "ratio": round(compress_ratio(all_den_bytes), 6),
        },
        "conductors_bulk": {
            "uncompressed_bytes": len(all_cond_bytes),
            "ratio": round(compress_ratio(all_cond_bytes), 6),
        },
        "random_integers_bulk": {
            "uncompressed_bytes": len(all_rand_bytes),
            "ratio": round(compress_ratio(all_rand_bytes), 6),
        },
    }

    # ---------------------------------------------------------------------------
    # Size-binned comparison (only bins with ≥ 20 samples)
    # ---------------------------------------------------------------------------
    binned_comparison = {}
    for n_digits in sorted(size_bins.keys()):
        b = size_bins[n_digits]
        if len(b["jinv"]) >= 20:
            jinv_mean = round(float(np.mean(b["jinv"])), 6)
            rand_mean = round(float(np.mean(b["random"])), 6)
            binned_comparison[str(n_digits)] = {
                "n": len(b["jinv"]),
                "jinv_mean_ratio": jinv_mean,
                "random_mean_ratio": rand_mean,
                "delta": round(jinv_mean - rand_mean, 6),
            }

    # ---------------------------------------------------------------------------
    # Verdict
    # ---------------------------------------------------------------------------
    jinv_mean = np.mean(jinv_num_ratios) if jinv_num_ratios else 0
    rand_mean = np.mean(random_num_ratios) if random_num_ratios else 0
    cond_mean = np.mean(conductor_ratios) if conductor_ratios else 0

    # Delta: negative means j-inv is MORE compressible than random
    delta_vs_random = float(jinv_mean - rand_mean)
    delta_vs_conductor = float(jinv_mean - cond_mean) if conductor_ratios else None

    if abs(delta_vs_random) < 0.02:
        verdict = "pseudorandom"
        explanation = (
            f"j-invariant numerator compression ({jinv_mean:.4f}) is within 0.02 of "
            f"random integers ({rand_mean:.4f}). Digit streams are arithmetically "
            f"indistinguishable from pseudorandom at the zlib level."
        )
    elif delta_vs_random < -0.02:
        verdict = "structured"
        explanation = (
            f"j-invariant numerators ({jinv_mean:.4f}) compress significantly more than "
            f"random integers ({rand_mean:.4f}), delta={delta_vs_random:.4f}. "
            f"Digit streams contain exploitable structure."
        )
    else:
        verdict = "anti-structured"
        explanation = (
            f"j-invariant numerators ({jinv_mean:.4f}) compress LESS than random "
            f"({rand_mean:.4f}), delta={delta_vs_random:.4f}. Unexpected."
        )

    results = {
        "challenge": "ChatGPT Harder #16 — j-Invariant Arithmetic Noise Floor",
        "question": "Are j-invariant digit streams pseudorandom or structured?",
        "method": "zlib compression ratio of decimal digit strings",
        "n_curves": len(rows),
        "n_analyzed_numerators": len(jinv_num_ratios),
        "n_analyzed_denominators": len(jinv_den_ratios),
        "skipped_small": skipped_small,
        "per_curve_stats": {
            "jinv_numerator": summarize(jinv_num_ratios),
            "jinv_denominator": summarize(jinv_den_ratios),
            "jinv_combined": summarize(jinv_combined_ratios),
            "conductor": summarize(conductor_ratios),
            "random_matched_numerator": summarize(random_num_ratios),
            "random_matched_denominator": summarize(random_den_ratios),
        },
        "bulk_stream_compression": bulk_results,
        "size_binned_comparison": binned_comparison,
        "delta_jinv_vs_random": round(delta_vs_random, 6),
        "delta_jinv_vs_conductor": round(delta_vs_conductor, 6) if delta_vs_conductor is not None else None,
        "verdict": verdict,
        "explanation": explanation,
    }

    # Print summary
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print(f"j-inv numerator  mean ratio: {summarize(jinv_num_ratios)['mean']}")
    print(f"j-inv denominator mean ratio: {summarize(jinv_den_ratios)['mean']}")
    print(f"j-inv combined   mean ratio: {summarize(jinv_combined_ratios)['mean']}")
    print(f"Conductor        mean ratio: {summarize(conductor_ratios)['mean']}")
    print(f"Random (matched) mean ratio: {summarize(random_num_ratios)['mean']}")
    print(f"\nDelta (jinv - random): {delta_vs_random:.6f}")
    if delta_vs_conductor is not None:
        print(f"Delta (jinv - conductor): {delta_vs_conductor:.6f}")
    print(f"\nBulk compression:")
    for k, v in bulk_results.items():
        print(f"  {k}: {v['ratio']:.6f} ({v['uncompressed_bytes']} bytes)")
    print(f"\nSize-binned comparison (digit count -> jinv vs random):")
    for k, v in sorted(binned_comparison.items(), key=lambda x: int(x[0])):
        print(f"  {k:>3s} digits: jinv={v['jinv_mean_ratio']:.4f} random={v['random_mean_ratio']:.4f} "
              f"delta={v['delta']:+.4f} (n={v['n']})")
    print(f"\nVERDICT: {verdict}")
    print(explanation)

    # Save
    with open(OUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {OUT_PATH}")

    con.close()


if __name__ == "__main__":
    main()

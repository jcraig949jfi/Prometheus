"""
Renormalization Signatures — scale-invariance detection via coarse-graining.
=============================================================================
Strategy S25: apply successive block-averaging to OEIS sequences and track
how statistical moments change across renormalization levels.

Level 0: original sequence a(n)
Level k+1: block-average pairs b(n) = (a(2n) + a(2n+1)) / 2
Continue for 5 levels. At each level compute mean, variance, skewness, kurtosis.
Scale-invariant sequences have flat moment trajectories.

Usage:
    python renormalization_signatures.py
    python renormalization_signatures.py --max-formulas 50000
    python renormalization_signatures.py --sample 10000
"""

import argparse
import gzip
import json
import random
import sys
import time
import warnings
import numpy as np
from pathlib import Path
from math import isfinite

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
OEIS_DATA = ROOT / "cartography" / "oeis" / "data"
STRIPPED_GZ = OEIS_DATA / "stripped_full.gz"
STRIPPED_FALLBACK = OEIS_DATA / "stripped.gz"
OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_SIGS = OUT_DIR / "renormalization_signatures.jsonl"

N_LEVELS = 5
MIN_SEQ_LEN = 2 ** (N_LEVELS + 1)  # Need at least 64 terms for 5 levels


# ── OEIS loader ───────────────────────────────────────────────────────────

def load_oeis_sequences(min_length=None, max_seqs=None):
    if min_length is None:
        min_length = MIN_SEQ_LEN
    gz = STRIPPED_GZ if STRIPPED_GZ.exists() else STRIPPED_FALLBACK
    if not gz.exists():
        print(f"  ERROR: no stripped file at {STRIPPED_GZ} or {STRIPPED_FALLBACK}")
        return {}
    print(f"  Loading OEIS sequences from {gz.name} (min_length={min_length}) ...")
    seqs = {}
    with gzip.open(gz, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(" ", 1)
            if len(parts) < 2:
                continue
            sid = parts[0].strip()
            if not sid.startswith("A"):
                continue
            terms_str = parts[1].strip().strip(",")
            try:
                terms = [int(t) for t in terms_str.split(",") if t.strip()]
            except ValueError:
                continue
            if len(terms) >= min_length:
                seqs[sid] = terms
            if max_seqs and len(seqs) >= max_seqs:
                break
    print(f"  Loaded {len(seqs):,} sequences with >= {min_length} terms")
    return seqs


# ── Renormalization group flow ────────────────────────────────────────────

def block_average(seq):
    """Block-average pairs: b(n) = (a(2n) + a(2n+1)) / 2."""
    n = len(seq) // 2
    if n == 0:
        return np.array([])
    arr = np.asarray(seq, dtype=np.float64)
    return (arr[:2*n:2] + arr[1:2*n:2]) / 2.0


def compute_moments(arr):
    """Compute (mean, variance, skewness, kurtosis) of array."""
    if len(arr) < 4:
        return None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = float(np.mean(arr))
        v = float(np.var(arr))
        std = np.std(arr)
        if std < 1e-30:
            return (m, v, 0.0, 0.0)
        centered = arr - m
        skew = float(np.mean(centered ** 3) / (std ** 3))
        kurt = float(np.mean(centered ** 4) / (std ** 4) - 3.0)  # excess kurtosis
    if not all(isfinite(x) for x in (m, v, skew, kurt)):
        return None
    return (m, v, skew, kurt)


def compute_renorm_signature(terms):
    """Apply N_LEVELS of block-averaging, track moment evolution.

    Returns signature dict or None.
    """
    levels = []
    current = np.asarray(terms, dtype=np.float64)

    # Clip extreme values to avoid overflow
    clip_val = 1e15
    current = np.clip(current, -clip_val, clip_val)

    for level in range(N_LEVELS + 1):
        if len(current) < 4:
            break
        moments = compute_moments(current)
        if moments is None:
            break
        levels.append(moments)
        if level < N_LEVELS:
            current = block_average(current)

    if len(levels) < 3:
        return None  # not enough levels

    # Extract moment trajectories
    means = [lv[0] for lv in levels]
    variances = [lv[1] for lv in levels]
    skews = [lv[2] for lv in levels]
    kurts = [lv[3] for lv in levels]

    # Compute change rates (slope of log-scale or linear)
    def change_rate(trajectory):
        """Rate of change across levels. Low = scale-invariant."""
        arr = np.array(trajectory)
        if np.allclose(arr, 0, atol=1e-15):
            return 0.0
        # Normalized RMS of differences
        diffs = np.diff(arr)
        scale = max(np.std(arr), 1e-15)
        return float(np.sqrt(np.mean(diffs ** 2)) / scale)

    mean_rate = change_rate(means)
    var_rate = change_rate(variances)
    skew_rate = change_rate(skews)
    kurt_rate = change_rate(kurts)

    # Scale-invariant: all rates below threshold
    is_scale_invariant = (mean_rate < 0.1 and var_rate < 0.1
                          and skew_rate < 0.3 and kurt_rate < 0.3)

    return {
        "mean_change_rate": mean_rate,
        "var_change_rate": var_rate,
        "skew_change_rate": skew_rate,
        "kurt_change_rate": kurt_rate,
        "is_scale_invariant": is_scale_invariant,
        "n_levels": len(levels),
        "moment_trajectory": {
            "means": means,
            "variances": variances,
            "skews": skews,
            "kurts": kurts,
        },
    }


# ── JSON encoder ──────────────────────────────────────────────────────────

class _Enc(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        return super().default(obj)


def write_jsonl(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, cls=_Enc) + "\n")
    print(f"  Wrote {len(records):,} records -> {path}")


# ── Main ──────────────────────────────────────────────────────────────────

def run(max_formulas=None, sample_n=None):
    t0 = time.time()
    print("=" * 70)
    print("Renormalization Signatures (S25)")
    print("=" * 70)

    seqs = load_oeis_sequences(max_seqs=max_formulas or 50000)

    if sample_n and sample_n < len(seqs):
        random.seed(42)
        keys = random.sample(list(seqs.keys()), sample_n)
        seqs = {k: seqs[k] for k in keys}
        print(f"  Sampled {len(seqs):,} sequences")

    results = []
    n_sig = 0
    n_scale_inv = 0
    items = list(seqs.items())
    total = len(items)

    for i, (sid, terms) in enumerate(items):
        if (i + 1) % 50000 == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            print(f"  ... {i+1:,}/{total:,} ({rate:.0f}/s)  "
                  f"sigs={n_sig:,}  scale_inv={n_scale_inv:,}")

        sig = compute_renorm_signature(terms)
        if sig is None:
            continue

        n_sig += 1
        if sig["is_scale_invariant"]:
            n_scale_inv += 1

        results.append({
            "id": sid,
            "source": "oeis",
            "n_terms": len(terms),
            **sig,
        })

    write_jsonl(OUT_SIGS, results)

    elapsed = time.time() - t0
    print(f"\n{'=' * 70}")
    print(f"  Total sequences: {total:,}")
    print(f"  Signatures:      {n_sig:,}")
    print(f"  Scale-invariant: {n_scale_inv:,} ({100*n_scale_inv/max(n_sig,1):.1f}%)")
    if results:
        rates = [r["mean_change_rate"] for r in results]
        print(f"  Mean change rate: mean={np.mean(rates):.4f}  "
              f"median={np.median(rates):.4f}  std={np.std(rates):.4f}")
    print(f"  Time: {elapsed:.1f}s")
    print(f"{'=' * 70}")


def main():
    parser = argparse.ArgumentParser(
        description="S25: Renormalization signatures — coarse-graining scale invariance"
    )
    parser.add_argument("--max-formulas", type=int, default=None,
                        help="Cap on number of sequences to load")
    parser.add_argument("--sample", type=int, default=None,
                        help="Random sample size (after loading)")
    args = parser.parse_args()
    run(max_formulas=args.max_formulas, sample_n=args.sample)


if __name__ == "__main__":
    main()

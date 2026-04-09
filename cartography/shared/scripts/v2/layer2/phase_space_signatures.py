"""
Phase Space Signature Extractor (S6) — trajectory-based invariants for OEIS sequences.
======================================================================================
Treats each OEIS sequence as a discrete dynamical trajectory and extracts
phase space signatures: autocorrelation, mutual information, fixed points,
cycles, Lyapunov exponent estimate, and orbit classification.

    A000045 (Fibonacci) -> orbit_type=growing, lyapunov=0.48, period=None
    A000035 (0,1,0,1,...) -> orbit_type=periodic, lyapunov=-inf, period=2

Usage:
    python phase_space_signatures.py                       # full run (50K seqs)
    python phase_space_signatures.py --max 10000           # cap input
    python phase_space_signatures.py --min-length 30       # longer sequences only
"""

import argparse
import gzip
import json
import math
import sys
import time
import warnings
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
OEIS_DATA = ROOT / "cartography" / "oeis" / "data"
STRIPPED_GZ = OEIS_DATA / "stripped_full.gz"
STRIPPED_FALLBACK = OEIS_DATA / "stripped.gz"
STRIPPED_TXT = OEIS_DATA / "stripped_new.txt"

OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_FILE = OUT_DIR / "phase_space_signatures.jsonl"


# ---------------------------------------------------------------------------
# OEIS loader
# ---------------------------------------------------------------------------

def load_oeis_sequences(min_length=20, max_seqs=None):
    """Parse OEIS stripped format, keep sequences with >= min_length terms."""
    # Try stripped_new.txt first (uncompressed), then gz files
    if STRIPPED_TXT.exists():
        print(f"  Loading OEIS sequences from {STRIPPED_TXT.name} (min_length={min_length}) ...")
        return _load_txt(STRIPPED_TXT, min_length, max_seqs)

    gz = STRIPPED_GZ if STRIPPED_GZ.exists() else STRIPPED_FALLBACK
    if not gz.exists():
        print(f"  ERROR: no stripped file found in {OEIS_DATA}")
        return {}

    print(f"  Loading OEIS sequences from {gz.name} (min_length={min_length}) ...")
    return _load_gz(gz, min_length, max_seqs)


def _parse_line(line, min_length, seqs, max_seqs):
    """Parse a single OEIS stripped line into seqs dict. Returns True if limit hit."""
    line = line.strip()
    if not line or line.startswith("#"):
        return False
    parts = line.split(" ", 1)
    if len(parts) < 2:
        return False
    sid = parts[0].strip()
    if not sid.startswith("A"):
        return False
    terms_str = parts[1].strip().strip(",")
    try:
        terms = [int(t) for t in terms_str.split(",") if t.strip()]
    except ValueError:
        return False
    if len(terms) >= min_length:
        seqs[sid] = terms
    if max_seqs and len(seqs) >= max_seqs:
        return True
    return False


def _load_txt(path, min_length, max_seqs):
    seqs = {}
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if _parse_line(line, min_length, seqs, max_seqs):
                break
    print(f"  Loaded {len(seqs):,} sequences with >= {min_length} terms")
    return seqs


def _load_gz(path, min_length, max_seqs):
    seqs = {}
    with gzip.open(path, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if _parse_line(line, min_length, seqs, max_seqs):
                break
    print(f"  Loaded {len(seqs):,} sequences with >= {min_length} terms")
    return seqs


# ---------------------------------------------------------------------------
# Signature extraction
# ---------------------------------------------------------------------------

def _autocorrelation(x, lag):
    """Normalized autocorrelation at given lag."""
    n = len(x)
    if lag >= n:
        return 0.0
    mean = np.mean(x)
    var = np.var(x)
    if var < 1e-30:
        return 1.0  # constant sequence
    c = np.mean((x[:n - lag] - mean) * (x[lag:] - mean))
    return float(c / var)


def _mutual_information_null(x_vals, y_vals, n_bins=20, n_null=50):
    """
    Mutual information between x and y using binned histograms,
    with random-pairing null subtracted to remove bias.
    """
    # Clamp to finite
    x_fin = x_vals[np.isfinite(x_vals)]
    y_fin = y_vals[np.isfinite(y_vals)]
    if len(x_fin) < 10 or len(y_fin) < 10:
        return 0.0

    # Use shared finite mask
    mask = np.isfinite(x_vals) & np.isfinite(y_vals)
    xm = x_vals[mask]
    ym = y_vals[mask]
    if len(xm) < 10:
        return 0.0

    # Bin edges from data range
    x_edges = np.linspace(np.min(xm), np.max(xm) + 1e-30, n_bins + 1)
    y_edges = np.linspace(np.min(ym), np.max(ym) + 1e-30, n_bins + 1)

    def _mi(xx, yy):
        hist_xy, _, _ = np.histogram2d(xx, yy, bins=[x_edges, y_edges])
        pxy = hist_xy / hist_xy.sum()
        px = pxy.sum(axis=1)
        py = pxy.sum(axis=0)
        # MI = sum p(x,y) * log(p(x,y) / (p(x)*p(y)))
        mi = 0.0
        for i in range(n_bins):
            for j in range(n_bins):
                if pxy[i, j] > 0 and px[i] > 0 and py[j] > 0:
                    mi += pxy[i, j] * math.log(pxy[i, j] / (px[i] * py[j]))
        return mi

    mi_real = _mi(xm, ym)

    # Null: random pairings
    rng = np.random.RandomState(42)
    mi_nulls = []
    for _ in range(n_null):
        perm = rng.permutation(len(ym))
        mi_nulls.append(_mi(xm, ym[perm]))

    mi_null_mean = np.mean(mi_nulls)
    return max(0.0, mi_real - mi_null_mean)


def _detect_fixed_points(a):
    """Count values where a(n+1) approximately equals a(n)."""
    diffs = np.abs(np.diff(a))
    # Scale threshold by sequence magnitude
    scale = max(np.median(np.abs(a[a != 0])), 1e-10) if np.any(a != 0) else 1.0
    threshold = scale * 1e-8
    return int(np.sum(diffs < threshold))


def _detect_period(a, max_period=50):
    """
    Detect periodicity by checking if a(n+k) == a(n) for some period k.
    Returns the period if found, else None.
    """
    n = len(a)
    for k in range(1, min(max_period + 1, n // 2)):
        # Check if a[k:] matches a[:-k]
        length = n - k
        if length < k:
            break
        if np.array_equal(a[k:k + length], a[:length]):
            return k
    return None


def _lyapunov_estimate(a):
    """
    Estimate Lyapunov exponent: mean(log(|a(n+1)-a(n)| / |a(n)-a(n-1)|))
    where denominators are non-zero.
    """
    if len(a) < 3:
        return float('nan')

    diffs = np.abs(np.diff(a.astype(np.float64)))
    # Pairs: diffs[i+1] / diffs[i] where diffs[i] != 0
    num = diffs[1:]
    den = diffs[:-1]

    mask = den > 0
    if np.sum(mask) < 2:
        return float('nan')

    ratios = num[mask] / den[mask]
    ratios = ratios[ratios > 0]
    if len(ratios) < 2:
        return float('nan')

    return float(np.mean(np.log(ratios)))


def _classify_orbit(a, autocorr_1, autocorr_2, autocorr_3, lyapunov, period):
    """Classify orbit type."""
    std = np.std(a.astype(np.float64))

    # Constant
    if std < 1e-10:
        return "constant"

    # Periodic (detected directly)
    if period is not None:
        return "periodic"

    # Strong autocorrelation at some lag suggests quasiperiodic
    if abs(autocorr_2) > 0.8 or abs(autocorr_3) > 0.8:
        return "periodic"

    # Monotonically growing/decreasing
    diffs = np.diff(a.astype(np.float64))
    if np.all(diffs >= 0) or np.all(diffs <= 0):
        return "growing"

    # Chaotic: positive Lyapunov + no periodicity
    if not np.isnan(lyapunov) and lyapunov > 0.1 and period is None:
        return "chaotic"

    return "quasiperiodic"


def phase_space_signature(seq_id, terms):
    """
    Extract full phase space signature for a single OEIS sequence.
    Returns dict with all signature components, or None if degenerate.
    """
    a = np.array(terms, dtype=np.float64)
    n = len(a)

    if n < 20:
        return None

    # Autocorrelation at lags 1, 2, 3
    ac1 = _autocorrelation(a, 1)
    ac2 = _autocorrelation(a, 2)
    ac3 = _autocorrelation(a, 3)

    # Mutual information between a(n) and a(n+1) with null correction
    mi = _mutual_information_null(a[:-1], a[1:])

    # Fixed points
    n_fixed = _detect_fixed_points(a)

    # Period detection
    period = _detect_period(a)

    # Lyapunov exponent
    lyap = _lyapunov_estimate(a)

    # Orbit classification
    orbit = _classify_orbit(a, ac1, ac2, ac3, lyap, period)

    return {
        "seq_id": seq_id,
        "n_terms": n,
        "autocorr_1": round(ac1, 6),
        "autocorr_2": round(ac2, 6),
        "autocorr_3": round(ac3, 6),
        "mutual_info": round(mi, 6),
        "lyapunov": round(lyap, 6) if not math.isnan(lyap) else None,
        "orbit_type": orbit,
        "n_fixed_points": n_fixed,
        "period": period,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="S6: Phase space signature extraction for OEIS sequences"
    )
    parser.add_argument("--max", type=int, default=50000,
                        help="Max sequences to process (default: 50000)")
    parser.add_argument("--min-length", type=int, default=20,
                        help="Min sequence length (default: 20)")
    args = parser.parse_args()

    print("=" * 70)
    print("S6: Phase Space Signatures")
    print("=" * 70)
    t0 = time.time()

    # Load sequences
    seqs = load_oeis_sequences(min_length=args.min_length, max_seqs=args.max)
    if not seqs:
        print("  No sequences loaded. Exiting.")
        return

    # Process
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    n_ok = 0
    n_fail = 0

    with open(OUT_FILE, "w", encoding="utf-8") as fout:
        for i, (sid, terms) in enumerate(seqs.items()):
            if (i + 1) % 5000 == 0 or i == 0:
                elapsed = time.time() - t0
                rate = (i + 1) / elapsed if elapsed > 0 else 0
                print(f"  [{i+1:>6}/{len(seqs)}] {rate:.0f} seq/s  ok={n_ok} fail={n_fail}")

            try:
                sig = phase_space_signature(sid, terms)
                if sig is not None:
                    fout.write(json.dumps(sig) + "\n")
                    n_ok += 1
                else:
                    n_fail += 1
            except Exception as e:
                n_fail += 1

    elapsed = time.time() - t0
    print(f"\n  Done in {elapsed:.1f}s")
    print(f"  Signatures: {n_ok:,} ok, {n_fail:,} failed/skipped")
    print(f"  Output: {OUT_FILE}")


if __name__ == "__main__":
    main()

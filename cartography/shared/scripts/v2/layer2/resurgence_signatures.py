"""
Resurgence Signatures (Strategy S28) — Borel summability classification.
=========================================================================
For OEIS sequences with >= 15 terms, treat as power series coefficients,
detect divergence patterns, and estimate Borel summability.

Usage:
    python resurgence_signatures.py
    python resurgence_signatures.py --max-formulas 50000
    python resurgence_signatures.py --sample 10000
"""

import argparse
import gzip
import json
import math
import sys
import time
import random
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
OEIS_DATA = ROOT / "cartography" / "oeis" / "data"
STRIPPED_GZ = OEIS_DATA / "stripped_full.gz"
STRIPPED_FALLBACK = OEIS_DATA / "stripped.gz"

OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_FILE = OUT_DIR / "resurgence_signatures.jsonl"

MIN_TERMS = 15
PRIMES_FOR_LABEL = [2, 3, 5, 7, 11, 13, 17, 19, 23]


# ---------------------------------------------------------------------------
# OEIS loader
# ---------------------------------------------------------------------------

def load_oeis_sequences(min_length=MIN_TERMS, max_seqs=None, sample_k=0):
    """Parse OEIS stripped format, keep sequences with >= min_length terms.

    If sample_k > 0, use reservoir sampling to select sample_k sequences.
    """
    gz = STRIPPED_GZ if STRIPPED_GZ.exists() else STRIPPED_FALLBACK
    if not gz.exists():
        print(f"  ERROR: no stripped file at {STRIPPED_GZ} or {STRIPPED_FALLBACK}")
        return {}

    print(f"  Loading OEIS sequences from {gz.name} (min_length={min_length}) ...")
    seqs = {}
    reservoir = {}
    n_eligible = 0
    rng = random.Random(42)

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
            if len(terms) < min_length:
                continue

            if sample_k > 0:
                n_eligible += 1
                if len(reservoir) < sample_k:
                    reservoir[sid] = terms
                else:
                    j = rng.randint(0, n_eligible - 1)
                    if j < sample_k:
                        keys = list(reservoir.keys())
                        reservoir[keys[j]] = terms
                        # Replace key too
                        del reservoir[keys[j]]
                        reservoir[sid] = terms
            else:
                seqs[sid] = terms
                if max_seqs and len(seqs) >= max_seqs:
                    break

    result = reservoir if sample_k > 0 else seqs
    print(f"  Loaded {len(result):,} sequences with >= {min_length} terms")
    return result


# ---------------------------------------------------------------------------
# Resurgence signature extraction
# ---------------------------------------------------------------------------

def compute_ratio_sequence(terms):
    """Compute |a(n+1)/a(n)| ratio sequence, skipping zeros."""
    ratios = []
    for i in range(len(terms) - 1):
        if terms[i] == 0:
            continue
        ratios.append(abs(terms[i + 1] / terms[i]))
    return ratios


def estimate_radius_of_convergence(terms):
    """Estimate radius of convergence using root test: R = 1/limsup |a(n)|^(1/n).

    Also uses ratio test as secondary estimate.
    """
    # Root test: limsup |a(n)|^(1/n)
    root_vals = []
    for n, a in enumerate(terms):
        if n == 0:
            continue
        if a == 0:
            continue
        try:
            root_val = abs(a) ** (1.0 / n)
            if math.isfinite(root_val):
                root_vals.append(root_val)
        except (OverflowError, ValueError):
            pass

    # Take the max of the last few values as limsup estimate
    if len(root_vals) >= 3:
        limsup = max(root_vals[-5:])  # last 5 values
        R_root = 1.0 / limsup if limsup > 1e-15 else float("inf")
    else:
        R_root = None

    # Ratio test: lim |a(n+1)/a(n)|
    ratios = compute_ratio_sequence(terms)
    if len(ratios) >= 3:
        # Use median of last few ratios as limit estimate
        tail = ratios[-5:]
        ratio_limit = sorted(tail)[len(tail) // 2]  # median
        R_ratio = 1.0 / ratio_limit if ratio_limit > 1e-15 else float("inf")
    else:
        R_ratio = None

    # Prefer root test, fall back to ratio test
    if R_root is not None:
        R = R_root
    elif R_ratio is not None:
        R = R_ratio
    else:
        R = None

    return R, R_root, R_ratio


def fit_gevrey_order(terms):
    """Fit r(n) = |a(n+1)/a(n)| ~ C * n^s to estimate Gevrey order s.

    Gevrey-s means coefficients grow like (n!)^s.
    s=1 => factorial (Borel summable)
    s>1 => super-factorial (not Borel summable in standard sense)
    s<1 => sub-factorial

    Returns (gevrey_order, fit_quality_r2, growth_rate_at_tail).
    """
    ratios = compute_ratio_sequence(terms)
    if len(ratios) < 5:
        return None, None, None

    # Filter to ratios with valid n indices
    # r(n) is the ratio at index n (comparing a(n+1)/a(n))
    # We need n >= 1 for log(n)
    log_n = []
    log_r = []
    for idx, r in enumerate(ratios):
        n = idx + 1  # start from n=1
        if r > 1e-15 and n > 0:
            try:
                ln = math.log(n)
                lr = math.log(r)
                if math.isfinite(ln) and math.isfinite(lr):
                    log_n.append(ln)
                    log_r.append(lr)
            except (ValueError, OverflowError):
                pass

    if len(log_n) < 4:
        return None, None, None

    # Linear regression: log(r(n)) = s * log(n) + log(C)
    n_pts = len(log_n)
    sum_x = sum(log_n)
    sum_y = sum(log_r)
    sum_xy = sum(x * y for x, y in zip(log_n, log_r))
    sum_x2 = sum(x * x for x in log_n)

    denom = n_pts * sum_x2 - sum_x * sum_x
    if abs(denom) < 1e-30:
        return None, None, None

    s = (n_pts * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - s * sum_x) / n_pts

    # R-squared
    mean_y = sum_y / n_pts
    ss_tot = sum((y - mean_y) ** 2 for y in log_r)
    ss_res = sum((y - (s * x + intercept)) ** 2 for x, y in zip(log_n, log_r))
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 1e-30 else 0.0

    # Growth rate at tail
    growth_rate = ratios[-1] if ratios else None

    return s, r_squared, growth_rate


def classify_divergence(R, gevrey_order, ratios):
    """Classify the type of divergence.

    Returns (classification, is_borel_summable).
    """
    if R is None:
        return "undetermined", None

    # Clamp R for classification
    if not math.isfinite(R):
        R = float("inf")

    if R > 1e-10 and R != float("inf"):
        return "convergent", True  # convergent series with finite R > 0

    if R == float("inf"):
        return "entire", True  # converges everywhere

    # R ~ 0: series diverges everywhere
    if gevrey_order is not None:
        if gevrey_order < 0.5:
            return "divergent_sublinear", True  # mild divergence, Borel summable
        elif gevrey_order < 1.5:
            return "divergent_factorial", True  # Gevrey-1, Borel summable
        elif gevrey_order < 2.5:
            return "divergent_double_factorial", False  # Gevrey-2, needs Borel-Ecalle
        else:
            return "divergent_superfactorial", False  # too wild for standard Borel

    # Fallback: check ratio growth
    if ratios and len(ratios) >= 3:
        tail_ratios = ratios[-5:]
        mean_tail = sum(tail_ratios) / len(tail_ratios)
        if mean_tail < 2:
            return "divergent_mild", True
        elif mean_tail < 20:
            return "divergent_factorial", True
        else:
            return "divergent_superfactorial", False

    return "divergent_unknown", None


def resurgence_signature(terms):
    """Compute full resurgence signature for a sequence.

    Returns dict with signature fields, or None if not enough data.
    """
    if len(terms) < MIN_TERMS:
        return None

    # Skip all-zero or all-constant sequences
    if len(set(terms)) <= 1:
        return None

    # Compute radius of convergence
    R, R_root, R_ratio = estimate_radius_of_convergence(terms)

    # Compute ratios
    ratios = compute_ratio_sequence(terms)

    # Fit Gevrey order
    gevrey_order, fit_r2, growth_rate = fit_gevrey_order(terms)

    # Classify
    classification, is_borel = classify_divergence(R, gevrey_order, ratios)

    # Compute divergence rate: median of last ratios / n
    if ratios and len(ratios) >= 3:
        tail = ratios[-min(5, len(ratios)):]
        divergence_rate = sum(tail) / len(tail)
    else:
        divergence_rate = None

    # Clamp infinities for JSON
    def clamp(v):
        if v is None:
            return None
        if not math.isfinite(v):
            return 1e308 if v > 0 else -1e308
        return round(v, 8)

    return {
        "radius_of_convergence": clamp(R),
        "radius_root_test": clamp(R_root),
        "radius_ratio_test": clamp(R_ratio),
        "gevrey_order": clamp(gevrey_order),
        "gevrey_fit_r2": clamp(fit_r2),
        "is_borel_summable": is_borel,
        "classification": classification,
        "divergence_rate": clamp(divergence_rate),
        "growth_rate_tail": clamp(growth_rate),
        "n_terms": len(terms),
        "n_ratios": len(ratios),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Resurgence signature extractor (S28)")
    ap.add_argument("--max-formulas", type=int, default=0,
                    help="Max sequences to process (0 = all)")
    ap.add_argument("--sample", type=int, default=0,
                    help="Reservoir sample size (0 = sequential)")
    ap.add_argument("--min-length", type=int, default=MIN_TERMS,
                    help=f"Min sequence length (default {MIN_TERMS})")
    args = ap.parse_args()

    print("=" * 70)
    print("  Resurgence Signature Extractor (S28)")
    print(f"  Min terms: {args.min_length}")
    print("=" * 70)
    t0 = time.time()

    max_seqs = args.max_formulas if args.max_formulas else None
    seqs = load_oeis_sequences(
        min_length=args.min_length,
        max_seqs=max_seqs,
        sample_k=args.sample,
    )

    if not seqs:
        print("  No sequences loaded. Exiting.")
        return

    # Process
    records = []
    stats = Counter()
    items = list(seqs.items())
    total = len(items)

    for i, (sid, terms) in enumerate(items):
        if i % 10000 == 0 and i > 0:
            elapsed = time.time() - t0
            rate = i / elapsed
            print(f"    {i:,}/{total:,} ({rate:.0f}/s) — "
                  f"{len(records):,} signatures, skips: {dict(stats)}")

        sig = resurgence_signature(terms)
        if sig is None:
            stats["skip_degenerate"] += 1
            continue

        stats[sig["classification"]] += 1

        record = {
            "id": sid,
            "signature": sig,
        }
        records.append(record)

    elapsed = time.time() - t0

    # Write output
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    print(f"\n  Wrote {len(records):,} signatures to {OUT_FILE}")

    # Summary
    print()
    print("=" * 70)
    print("  SUMMARY")
    print(f"  Total sequences:        {total:,}")
    print(f"  Signatures computed:    {len(records):,}")
    print(f"  Classification breakdown:")
    for cls, cnt in sorted(stats.items(), key=lambda x: -x[1]):
        pct = 100 * cnt / max(total, 1)
        print(f"    {cls:30s} {cnt:>7,}  ({pct:.1f}%)")

    # Borel summability stats
    n_borel = sum(1 for r in records if r["signature"]["is_borel_summable"] is True)
    n_not_borel = sum(1 for r in records if r["signature"]["is_borel_summable"] is False)
    n_unknown = sum(1 for r in records if r["signature"]["is_borel_summable"] is None)
    print(f"\n  Borel summable:         {n_borel:,}")
    print(f"  Not Borel summable:     {n_not_borel:,}")
    print(f"  Undetermined:           {n_unknown:,}")

    # Gevrey order distribution
    gevrey_vals = [r["signature"]["gevrey_order"] for r in records
                   if r["signature"]["gevrey_order"] is not None]
    if gevrey_vals:
        print(f"\n  Gevrey order stats (n={len(gevrey_vals):,}):")
        gevrey_sorted = sorted(gevrey_vals)
        print(f"    min:    {gevrey_sorted[0]:.4f}")
        print(f"    median: {gevrey_sorted[len(gevrey_sorted)//2]:.4f}")
        print(f"    max:    {gevrey_sorted[-1]:.4f}")
        print(f"    mean:   {sum(gevrey_vals)/len(gevrey_vals):.4f}")

    print(f"\n  Time:                   {elapsed:.1f}s")
    print("=" * 70)


if __name__ == "__main__":
    main()

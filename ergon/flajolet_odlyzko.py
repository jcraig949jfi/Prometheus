#!/usr/bin/env python3
"""
Flajolet-Odlyzko Singularity Classification for OEIS Sequences
===============================================================
Aporia Report #19 — Ergon assignment

Classifies OEIS sequences by generating function singularity type using
Flajolet-Odlyzko transfer theorems. The growth rate of a(n) determines
the singularity type of its generating function:

  Polynomial   a(n) ~ n^k         → polar singularity (simple pole)
  Exponential  a(n) ~ c^n         → algebraic singularity (finite radius)
  Super-exp    a(n) ~ n! or n^n   → essential singularity (entire function)
  Sub-exp      a(n) ~ exp(n^α)    → logarithmic singularity
  Bounded      max(a(n)) < C      → holomorphic (no singularity on disc)

Data source: cartography/oeis/data/stripped_full.gz (raw OEIS terms)
"""

import sys
import os
import gzip
import json
import numpy as np
from pathlib import Path
from collections import Counter
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

CARTOGRAPHY = Path(__file__).resolve().parent.parent / "cartography"
STRIPPED = CARTOGRAPHY / "oeis" / "data" / "stripped_full.gz"
NAMES_JSON = CARTOGRAPHY / "oeis" / "data" / "oeis_names.json"

# --- Configuration -----------------------------------------------------------
MIN_TERMS = 8          # need enough terms to fit growth
MAX_SEQUENCES = 200000  # cap for speed
R2_THRESHOLD = 0.92    # goodness-of-fit threshold for classification
BOUNDED_THRESHOLD = 100 # if max |a_n| < this, classify as bounded


@dataclass
class SeqClassification:
    seq_id: str
    singularity_type: str  # polar, algebraic, logarithmic, essential, holomorphic, unclassified
    growth_class: str      # polynomial, exponential, super_exponential, sub_exponential, bounded, unclassified
    r2: float              # best R^2 achieved
    param: float           # estimated growth parameter (exponent k, base c, etc.)
    n_terms: int


def _linreg_r2(x: np.ndarray, y: np.ndarray):
    """Simple linear regression returning (slope, intercept, R^2)."""
    if len(x) < 3:
        return 0.0, 0.0, 0.0
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if len(x) < 3:
        return 0.0, 0.0, 0.0
    xm, ym = x.mean(), y.mean()
    ss_xy = ((x - xm) * (y - ym)).sum()
    ss_xx = ((x - xm) ** 2).sum()
    if ss_xx < 1e-15:
        return 0.0, 0.0, 0.0
    slope = ss_xy / ss_xx
    intercept = ym - slope * xm
    y_pred = slope * x + intercept
    ss_res = ((y - y_pred) ** 2).sum()
    ss_tot = ((y - ym) ** 2).sum()
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-15 else 0.0
    return slope, intercept, r2


def classify_sequence(terms: list[int]) -> tuple[str, str, float, float]:
    """
    Classify a single sequence by fitting growth models.

    Returns: (growth_class, singularity_type, best_r2, parameter)
    """
    n = len(terms)
    abs_terms = np.array([abs(t) for t in terms], dtype=np.float64)

    # Check bounded/periodic first
    if abs_terms.max() < BOUNDED_THRESHOLD:
        return "bounded", "holomorphic", 1.0, abs_terms.max()

    # Need positive terms for log fits — use indices where a_n > 0
    pos_mask = abs_terms > 0
    if pos_mask.sum() < 5:
        return "bounded", "holomorphic", 1.0, abs_terms.max()

    indices = np.arange(1, n + 1, dtype=np.float64)  # 1-based

    log_a = np.full(n, np.nan)
    log_a[pos_mask] = np.log(abs_terms[pos_mask])

    log_n = np.log(indices)

    results = {}

    # 1. Polynomial: log(a_n) ~ k * log(n)
    slope_p, _, r2_p = _linreg_r2(log_n, log_a)
    results["polynomial"] = (r2_p, slope_p)

    # 2. Exponential: log(a_n) ~ n * log(c), i.e., linear in n
    slope_e, _, r2_e = _linreg_r2(indices, log_a)
    if slope_e > 0:  # must be growing
        results["exponential"] = (r2_e, np.exp(slope_e))
    else:
        results["exponential"] = (0.0, 0.0)

    # 3. Super-exponential: log(a_n) ~ n*log(n) (Stirling-like)
    nlogn = indices * log_n
    slope_s, _, r2_s = _linreg_r2(nlogn, log_a)
    if slope_s > 0:
        results["super_exponential"] = (r2_s, slope_s)
    else:
        results["super_exponential"] = (0.0, 0.0)

    # 4. Sub-exponential: log(log(a_n)) ~ alpha * log(n)
    loglog_a = np.full(n, np.nan)
    big_mask = abs_terms > 1  # need a_n > 1 for log(log(a_n))
    if big_mask.sum() >= 5:
        loglog_a[big_mask] = np.log(np.log(abs_terms[big_mask]))
        slope_sub, _, r2_sub = _linreg_r2(log_n, loglog_a)
        if 0 < slope_sub < 1:  # alpha in (0, 1) for sub-exponential
            results["sub_exponential"] = (r2_sub, slope_sub)
        else:
            results["sub_exponential"] = (0.0, 0.0)
    else:
        results["sub_exponential"] = (0.0, 0.0)

    # Pick best fit, with priority ordering for ties:
    # super_exp > exponential > sub_exponential > polynomial
    # This ordering reflects that faster growth is a stronger signal
    priority = ["super_exponential", "exponential", "sub_exponential", "polynomial"]

    best_class = "unclassified"
    best_r2 = 0.0
    best_param = 0.0

    for gc in priority:
        r2, param = results[gc]
        if r2 > best_r2 + 0.02:  # need clear advantage to override
            best_r2 = r2
            best_class = gc
            best_param = param
        elif r2 >= R2_THRESHOLD and best_r2 < R2_THRESHOLD:
            best_r2 = r2
            best_class = gc
            best_param = param

    if best_r2 < R2_THRESHOLD:
        # Try secondary: if exponential is close, still use it (common case)
        r2_e_val = results["exponential"][0]
        r2_p_val = results["polynomial"][0]
        if r2_e_val > 0.85:
            best_class = "exponential"
            best_r2 = r2_e_val
            best_param = results["exponential"][1]
        elif r2_p_val > 0.85:
            best_class = "polynomial"
            best_r2 = r2_p_val
            best_param = results["polynomial"][1]
        else:
            best_class = "unclassified"

    # Map to singularity type
    singularity_map = {
        "polynomial": "polar",
        "exponential": "algebraic",
        "super_exponential": "essential",
        "sub_exponential": "logarithmic",
        "bounded": "holomorphic",
        "unclassified": "unclassified",
    }
    return best_class, singularity_map[best_class], best_r2, best_param


def load_sequences(path: Path = STRIPPED, limit: int = MAX_SEQUENCES) -> dict[str, list[int]]:
    """Load raw OEIS terms from stripped file."""
    sequences = {}
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, "rt") as f:
        for line in f:
            if not line.startswith("A"):
                continue
            parts = line.strip().split(",")
            seq_id = parts[0].strip()
            terms = []
            for t in parts[1:]:
                t = t.strip()
                if t and t.lstrip("-").isdigit():
                    terms.append(int(t))
            if len(terms) >= MIN_TERMS:
                # Use first 30 terms max (enough for growth classification)
                sequences[seq_id] = terms[:30]
            if len(sequences) >= limit:
                break
    return sequences


def load_names() -> dict[str, str]:
    """Load sequence names for readable output."""
    if NAMES_JSON.exists():
        with open(NAMES_JSON, encoding="utf-8") as f:
            return json.load(f)
    return {}


def run_classification():
    """Main classification pipeline."""
    print("=" * 72)
    print("Flajolet-Odlyzko Singularity Classification — Aporia Report #19")
    print("=" * 72)

    # Load data
    print(f"\nLoading sequences from {STRIPPED.name} ...")
    sequences = load_sequences()
    print(f"  Loaded {len(sequences):,} sequences with >= {MIN_TERMS} terms")

    names = load_names()

    # Classify each sequence
    print("\nClassifying growth types ...")
    results = []
    for seq_id, terms in sequences.items():
        gc, st, r2, param = classify_sequence(terms)
        results.append(SeqClassification(
            seq_id=seq_id,
            singularity_type=st,
            growth_class=gc,
            r2=r2,
            param=param,
            n_terms=len(terms),
        ))

    # --- Distribution table ---
    print("\n" + "=" * 72)
    print("SINGULARITY TYPE DISTRIBUTION")
    print("=" * 72)

    sing_counts = Counter(r.singularity_type for r in results)
    growth_counts = Counter(r.growth_class for r in results)
    total = len(results)

    print(f"\n{'Singularity Type':<20} {'Growth Class':<20} {'Count':>8} {'Pct':>8}")
    print("-" * 60)

    type_pairs = [
        ("holomorphic", "bounded"),
        ("polar", "polynomial"),
        ("algebraic", "exponential"),
        ("logarithmic", "sub_exponential"),
        ("essential", "super_exponential"),
        ("unclassified", "unclassified"),
    ]
    for stype, gclass in type_pairs:
        c = sing_counts.get(stype, 0)
        pct = 100.0 * c / total if total else 0
        print(f"{stype:<20} {gclass:<20} {c:>8,} {pct:>7.1f}%")

    print("-" * 60)
    print(f"{'TOTAL':<42} {total:>8,}")

    # --- Quality metrics ---
    r2_vals = np.array([r.r2 for r in results if r.growth_class != "bounded"])
    classified = [r for r in results if r.singularity_type != "unclassified"
                  and r.singularity_type != "holomorphic"]
    print(f"\nClassification quality (excluding bounded):")
    if len(r2_vals) > 0:
        print(f"  Median R^2:  {np.median(r2_vals):.4f}")
        print(f"  Mean R^2:    {np.mean(r2_vals):.4f}")
        print(f"  R^2 > 0.95:  {(r2_vals > 0.95).sum():,} / {len(r2_vals):,}")
    print(f"  Classified (non-trivial): {len(classified):,} / {total:,}")

    # --- Example sequences per type ---
    print("\n" + "=" * 72)
    print("EXAMPLES PER SINGULARITY TYPE")
    print("=" * 72)

    for stype, gclass in type_pairs:
        subset = [r for r in results if r.singularity_type == stype]
        if not subset:
            continue
        # Sort by R^2 descending for best examples
        subset.sort(key=lambda r: -r.r2)
        print(f"\n  [{stype.upper()}] ({gclass}, n={len(subset):,})")
        for r in subset[:5]:
            name = names.get(r.seq_id, "")[:55]
            print(f"    {r.seq_id}  R²={r.r2:.3f}  param={r.param:.3f}  {name}")

    # --- Parameter distributions ---
    print("\n" + "=" * 72)
    print("PARAMETER DISTRIBUTIONS")
    print("=" * 72)

    for stype, gclass in type_pairs:
        subset = [r for r in results if r.growth_class == gclass
                  and r.growth_class not in ("bounded", "unclassified")]
        if not subset:
            continue
        params = np.array([r.param for r in subset])
        print(f"\n  {gclass}: param = ", end="")
        if gclass == "polynomial":
            print(f"exponent k  (median={np.median(params):.2f}, "
                  f"mean={np.mean(params):.2f}, range=[{params.min():.2f}, {params.max():.2f}])")
            # Sub-classify polynomial degree
            for deg in [1, 2, 3]:
                n_deg = ((params > deg - 0.5) & (params <= deg + 0.5)).sum()
                print(f"      degree ~{deg}: {n_deg:,}")
            n_high = (params > 3.5).sum()
            print(f"      degree >3:  {n_high:,}")
        elif gclass == "exponential":
            print(f"base c  (median={np.median(params):.3f}, "
                  f"mean={np.mean(params):.3f})")
        elif gclass == "super_exponential":
            print(f"Stirling coeff  (median={np.median(params):.4f})")
        elif gclass == "sub_exponential":
            print(f"alpha  (median={np.median(params):.3f}, "
                  f"mean={np.mean(params):.3f})")

    # --- Save results ---
    out_dir = Path(__file__).resolve().parent / "logs"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "flajolet_odlyzko_results.json"

    export = {
        "report": "Aporia #19 — Flajolet-Odlyzko Singularity Classification",
        "n_sequences": total,
        "distribution": {st: cnt for st, cnt in sing_counts.items()},
        "growth_distribution": {gc: cnt for gc, cnt in growth_counts.items()},
        "classifications": [
            {
                "seq_id": r.seq_id,
                "singularity_type": r.singularity_type,
                "growth_class": r.growth_class,
                "r2": round(r.r2, 5),
                "param": round(r.param, 5),
                "n_terms": r.n_terms,
            }
            for r in results
        ],
    }
    with open(out_path, "w") as f:
        json.dump(export, f, indent=1)
    print(f"\nResults saved to {out_path}")

    # --- Flajolet-Odlyzko transfer theorem summary ---
    print("\n" + "=" * 72)
    print("TRANSFER THEOREM MAPPING")
    print("=" * 72)
    print("""
    Singularity Type    GF Behavior near z=rho          a(n) asymptotics
    -----------------   ------------------------------  -----------------
    Holomorphic         Entire / no singularity          bounded / periodic
    Polar               (1 - z/rho)^{-k}                n^{k-1} / Gamma(k)
    Algebraic           (1 - z/rho)^{alpha}             rho^{-n} n^{-alpha-1}
    Logarithmic         log(1 - z/rho)^{beta}           rho^{-n} (log n)^{beta-1}
    Essential           exp(c/(1-z/rho))                 faster than any rho^{-n} n^k
    """)

    return results


if __name__ == "__main__":
    results = run_classification()

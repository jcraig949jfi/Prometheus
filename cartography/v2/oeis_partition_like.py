"""
OEIS Partition-Like Sequences: Frequency and Structure
=======================================================
Test how many OEIS sequences exhibit Hardy-Ramanujan partition-like
asymptotics: log(a_n) ~ A * sqrt(n) + B * log(n) + C.

The partition function p(n) has A = pi * sqrt(2/3) ~ 2.565.
"""

import json
import time
import numpy as np
from pathlib import Path
from collections import Counter
from scipy.optimize import curve_fit

DATA_DIR = Path(__file__).parent.parent / "oeis" / "data"
STRIPPED_FILE = DATA_DIR / "stripped_new.txt"
OUTPUT_FILE = Path(__file__).parent / "oeis_partition_like_results.json"

MIN_TERMS = 20
TARGET_SEQUENCES = 5000
PARTITION_CONSTANT = np.pi * np.sqrt(2.0 / 3.0)  # ~2.5651


def load_sequences(path, min_terms=MIN_TERMS, max_seqs=TARGET_SEQUENCES):
    """Load OEIS sequences from stripped format."""
    sequences = {}
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(" ", 1)
            if len(parts) != 2:
                continue
            seq_id = parts[0]
            terms_str = parts[1].strip().strip(",")
            if not terms_str:
                continue
            try:
                terms = [int(x) for x in terms_str.split(",") if x.strip()]
            except ValueError:
                continue
            if len(terms) >= min_terms:
                sequences[seq_id] = terms
            if len(sequences) >= max_seqs:
                break
    return sequences


def partition_model(n, A, B, C):
    """log(a_n) = A * sqrt(n) + B * log(n) + C"""
    return A * np.sqrt(n) + B * np.log(n) + C


def exponential_model(n, r, C):
    """log(a_n) = r * n + C  (pure exponential)"""
    return r * n + C


def polynomial_model(log_n, p, C):
    """log(a_n) = p * log(n) + C  (polynomial growth)"""
    return p * log_n + C


def classify_sequence(terms):
    """
    Classify a sequence's growth type and test partition-likeness.

    Returns dict with classification info, or None if sequence can't be analyzed.
    """
    vals = np.array(terms, dtype=float)

    # Need positive values for log fitting (use indices >= 5 as specified)
    # Build (index, value) pairs for n >= 5
    indices = []
    log_vals = []
    for i, v in enumerate(vals):
        n = i + 1  # 1-indexed
        if n >= 5 and v > 0:
            indices.append(n)
            log_vals.append(np.log(float(v)))

    if len(indices) < 10:
        return None

    n_arr = np.array(indices, dtype=float)
    y = np.array(log_vals, dtype=float)

    # Skip if values are all identical (constant sequence)
    if np.std(y) < 1e-10:
        return {"growth_class": "constant", "partition_like": False}

    # Skip if sequence is decreasing overall
    if y[-1] < y[0]:
        return {"growth_class": "decreasing", "partition_like": False}

    result = {
        "partition_like": False,
        "growth_class": "unknown",
    }

    # --- Fit 1: Partition model log(a_n) = A*sqrt(n) + B*log(n) + C ---
    partition_r2 = -999.0
    partition_A = 0.0
    partition_B = 0.0
    partition_C = 0.0
    try:
        popt, _ = curve_fit(partition_model, n_arr, y, p0=[1.0, -1.0, 0.0], maxfev=5000)
        partition_A, partition_B, partition_C = popt
        y_pred = partition_model(n_arr, *popt)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        partition_r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else -999.0
    except Exception:
        pass

    result["partition_fit"] = {
        "A": float(partition_A),
        "B": float(partition_B),
        "C": float(partition_C),
        "R2": float(partition_r2),
    }

    # --- Fit 2: Exponential model log(a_n) = r*n + C ---
    exp_r2 = -999.0
    exp_r = 0.0
    try:
        popt_e, _ = curve_fit(exponential_model, n_arr, y, p0=[0.1, 0.0], maxfev=5000)
        exp_r = popt_e[0]
        y_pred_e = exponential_model(n_arr, *popt_e)
        ss_res_e = np.sum((y - y_pred_e) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        exp_r2 = 1.0 - ss_res_e / ss_tot if ss_tot > 0 else -999.0
    except Exception:
        pass

    result["exponential_fit"] = {
        "r": float(exp_r),
        "R2": float(exp_r2),
    }

    # --- Fit 3: Polynomial model log(a_n) = p*log(n) + C ---
    poly_r2 = -999.0
    poly_p = 0.0
    try:
        log_n = np.log(n_arr)
        popt_p, _ = curve_fit(polynomial_model, log_n, y, p0=[2.0, 0.0], maxfev=5000)
        poly_p = popt_p[0]
        y_pred_p = polynomial_model(log_n, *popt_p)
        ss_res_p = np.sum((y - y_pred_p) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        poly_r2 = 1.0 - ss_res_p / ss_tot if ss_tot > 0 else -999.0
    except Exception:
        pass

    result["polynomial_fit"] = {
        "power": float(poly_p),
        "R2": float(poly_r2),
    }

    # --- Classify growth ---
    # Partition-like: R2 > 0.95, A > 0, and grows slower than exponential
    # "Slower than exponential" = partition model fits better than exponential,
    # OR exponential R2 is poor
    grows_slower_than_exp = (partition_r2 > exp_r2) or (exp_r2 < 0.90)

    if partition_r2 > 0.95 and partition_A > 0 and grows_slower_than_exp:
        result["partition_like"] = True

    # Best growth class by R2
    fits = {
        "polynomial": poly_r2,
        "partition": partition_r2,
        "exponential": exp_r2,
    }
    best = max(fits, key=fits.get)
    result["growth_class"] = best

    return result


def main():
    t0 = time.time()
    print(f"Loading sequences from {STRIPPED_FILE} ...")
    sequences = load_sequences(STRIPPED_FILE, MIN_TERMS, TARGET_SEQUENCES)
    print(f"  Loaded {len(sequences)} sequences with >= {MIN_TERMS} terms.")

    results_per_seq = {}
    partition_like_ids = []
    partition_A_values = []
    growth_class_counts = Counter()
    n_analyzed = 0
    n_skipped = 0

    print("Classifying sequences ...")
    for seq_id, terms in sequences.items():
        res = classify_sequence(terms)
        if res is None:
            n_skipped += 1
            continue
        n_analyzed += 1
        growth_class_counts[res["growth_class"]] += 1

        if res.get("partition_like"):
            partition_like_ids.append(seq_id)
            partition_A_values.append(res["partition_fit"]["A"])

        results_per_seq[seq_id] = res

    elapsed = time.time() - t0

    # --- Summary statistics ---
    frac_partition = len(partition_like_ids) / n_analyzed if n_analyzed > 0 else 0.0
    A_arr = np.array(partition_A_values) if partition_A_values else np.array([])

    A_stats = {}
    if len(A_arr) > 0:
        A_stats = {
            "count": len(A_arr),
            "mean": float(np.mean(A_arr)),
            "median": float(np.median(A_arr)),
            "std": float(np.std(A_arr)),
            "min": float(np.min(A_arr)),
            "max": float(np.max(A_arr)),
            "p10": float(np.percentile(A_arr, 10)),
            "p25": float(np.percentile(A_arr, 25)),
            "p75": float(np.percentile(A_arr, 75)),
            "p90": float(np.percentile(A_arr, 90)),
        }
        # How many are near the partition constant?
        near_partition = int(np.sum(np.abs(A_arr - PARTITION_CONSTANT) < 0.3))
        A_stats["near_partition_constant_pm0.3"] = near_partition

        # Histogram bins for the A distribution
        if len(A_arr) >= 5:
            hist_counts, hist_edges = np.histogram(A_arr, bins=20)
            A_stats["histogram"] = {
                "counts": hist_counts.tolist(),
                "bin_edges": [float(e) for e in hist_edges],
            }

    # Top partition-like sequences sorted by closeness to partition constant
    top_near_partition = []
    if partition_A_values:
        paired = list(zip(partition_like_ids, partition_A_values))
        paired.sort(key=lambda x: abs(x[1] - PARTITION_CONSTANT))
        for sid, a_val in paired[:20]:
            top_near_partition.append({
                "seq_id": sid,
                "A": round(a_val, 6),
                "delta_from_partition": round(abs(a_val - PARTITION_CONSTANT), 6),
                "partition_fit_R2": round(results_per_seq[sid]["partition_fit"]["R2"], 6),
            })

    summary = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "parameters": {
            "min_terms": MIN_TERMS,
            "target_sequences": TARGET_SEQUENCES,
            "partition_constant": round(PARTITION_CONSTANT, 6),
            "fit_start_index": 5,
            "partition_like_criteria": {
                "partition_R2_threshold": 0.95,
                "A_positive": True,
                "grows_slower_than_exponential": True,
            },
        },
        "counts": {
            "sequences_loaded": len(sequences),
            "sequences_analyzed": n_analyzed,
            "sequences_skipped": n_skipped,
            "partition_like": len(partition_like_ids),
            "fraction_partition_like": round(frac_partition, 6),
            "percent_partition_like": round(100 * frac_partition, 2),
        },
        "growth_class_distribution": {
            k: v for k, v in sorted(growth_class_counts.items(), key=lambda x: -x[1])
        },
        "partition_constant_A_distribution": A_stats,
        "top_sequences_near_partition_constant": top_near_partition,
        "partition_like_sequence_ids": sorted(partition_like_ids),
        "elapsed_seconds": round(elapsed, 1),
    }

    # Save
    with open(OUTPUT_FILE, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nResults saved to {OUTPUT_FILE}")

    # Print report
    print(f"\n{'='*60}")
    print(f"OEIS Partition-Like Sequences: Summary")
    print(f"{'='*60}")
    print(f"Sequences loaded:   {len(sequences)}")
    print(f"Sequences analyzed: {n_analyzed}")
    print(f"Sequences skipped:  {n_skipped}")
    print(f"")
    print(f"Partition-like:     {len(partition_like_ids)} / {n_analyzed}"
          f"  ({100*frac_partition:.2f}%)")
    print(f"")
    print(f"Growth class distribution:")
    for cls, cnt in sorted(growth_class_counts.items(), key=lambda x: -x[1]):
        print(f"  {cls:20s} {cnt:5d}  ({100*cnt/n_analyzed:.1f}%)")
    print(f"")
    if A_stats:
        print(f"Partition constant A distribution (among partition-like):")
        print(f"  mean={A_stats['mean']:.4f}  median={A_stats['median']:.4f}"
              f"  std={A_stats['std']:.4f}")
        print(f"  range=[{A_stats['min']:.4f}, {A_stats['max']:.4f}]")
        print(f"  Near p(n) constant ({PARTITION_CONSTANT:.4f} +/- 0.3):"
              f" {A_stats.get('near_partition_constant_pm0.3', 0)}")
    print(f"")
    if top_near_partition:
        print(f"Top sequences closest to partition constant A={PARTITION_CONSTANT:.4f}:")
        for item in top_near_partition[:10]:
            print(f"  {item['seq_id']}  A={item['A']:.4f}"
                  f"  delta={item['delta_from_partition']:.4f}"
                  f"  R2={item['partition_fit_R2']:.4f}")
    print(f"\nElapsed: {elapsed:.1f}s")


if __name__ == "__main__":
    main()

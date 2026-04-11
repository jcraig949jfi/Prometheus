"""
Sato-Tate Entropy Defect Spectrum
=================================
Measure deviation of empirical Shannon entropy of normalized Frobenius traces
from maximum entropy (uniform distribution), stratified by Sato-Tate group.

Data: 66K genus-2 curves from LMFDB postgres dump (gce_1000000_lmfdb.txt)
Each curve has good_lfactors: [[p, a1, a2], ...] where a1 = trace of Frobenius.

Normalization: a1 / (2*sqrt(p))  maps to [-2, 2] per Sato-Tate convention.
  (For genus-2, |a1| <= 4*sqrt(p) by Weil bound; dividing by 2*sqrt(p) -> [-2, 2])

Entropy defect: DeltaH(G) = H_max - H_emp
  H_max = log2(50) for 50 uniform bins on [-2, 2]
  H_emp = -sum(p_i * log2(p_i)) for empirical bin probabilities
"""
import json
import ast
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "genus2" / "data" / "g2c-data" / "gce_1000000_lmfdb.txt"
OUT_FILE = Path(__file__).resolve().parent / "st_entropy_defect_results.json"

N_BINS = 50
BIN_MIN, BIN_MAX = -2.0, 2.0
H_MAX = math.log2(N_BINS)  # = log2(50) ~ 5.6439


def parse_line(line: str):
    """Parse colon-delimited line with bracket awareness."""
    fields = []
    depth = 0
    current = []
    for ch in line:
        if ch in "([":
            depth += 1
            current.append(ch)
        elif ch in ")]":
            depth -= 1
            current.append(ch)
        elif ch == ":" and depth == 0:
            fields.append("".join(current))
            current = []
        else:
            current.append(ch)
    fields.append("".join(current))
    return fields


def compute_entropy(values, n_bins=N_BINS, lo=BIN_MIN, hi=BIN_MAX):
    """Compute Shannon entropy (bits) of histogram over [lo, hi]."""
    bin_width = (hi - lo) / n_bins
    counts = [0] * n_bins
    n_total = 0
    for v in values:
        if lo <= v < hi:
            idx = int((v - lo) / bin_width)
            if idx >= n_bins:
                idx = n_bins - 1
            counts[idx] += 1
            n_total += 1
        elif v == hi:
            counts[n_bins - 1] += 1
            n_total += 1
        # values outside [-2, 2] are dropped (should be rare for large p)
    if n_total == 0:
        return 0.0, counts, 0
    entropy = 0.0
    for c in counts:
        if c > 0:
            p = c / n_total
            entropy -= p * math.log2(p)
    return entropy, counts, n_total


def main():
    if not DATA_FILE.exists():
        print(f"ERROR: {DATA_FILE} not found")
        sys.exit(1)

    print(f"Loading genus-2 curves from {DATA_FILE}...")
    print(f"H_max = log2({N_BINS}) = {H_MAX:.4f} bits\n")

    # Collect normalized traces per ST group
    st_traces = defaultdict(list)
    parse_errors = 0
    total_curves = 0
    min_p_threshold = 5  # skip p=2,3 where normalization is noisy

    with open(DATA_FILE, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            fields = parse_line(line)
            if len(fields) < 17:
                parse_errors += 1
                continue

            st_group = fields[8]
            try:
                lfactors = ast.literal_eval(fields[16])
            except Exception:
                parse_errors += 1
                continue

            total_curves += 1
            for entry in lfactors:
                if len(entry) < 2:
                    continue
                p, a1 = entry[0], entry[1]
                if p < min_p_threshold:
                    continue
                norm = a1 / (2.0 * math.sqrt(p))
                st_traces[st_group].append(norm)

            if line_num % 10000 == 0:
                print(f"  ...{line_num} lines processed")

    print(f"\nTotal curves parsed: {total_curves}")
    print(f"Parse errors: {parse_errors}")
    print(f"ST groups found: {len(st_traces)}")

    # Compute entropy defect per group
    results = {}
    print(f"\n{'ST Group':<20} {'Curves':>7} {'Traces':>10} {'H_emp':>8} {'DeltaH':>8} {'DeltaH%':>8}")
    print("-" * 70)

    for st in sorted(st_traces.keys(), key=lambda s: -len(st_traces[s])):
        traces = st_traces[st]
        h_emp, counts, n_used = compute_entropy(traces)
        delta_h = H_MAX - h_emp
        delta_pct = (delta_h / H_MAX) * 100.0

        # Count curves (approximate from traces)
        # Better: count directly
        n_outside = len(traces) - n_used
        frac_outside = n_outside / len(traces) if traces else 0

        # Compute distribution stats
        if traces:
            mean_t = sum(traces) / len(traces)
            var_t = sum((t - mean_t) ** 2 for t in traces) / len(traces)
            std_t = math.sqrt(var_t)
        else:
            mean_t = std_t = 0.0

        # Non-empty bin count
        n_occupied = sum(1 for c in counts if c > 0)

        results[st] = {
            "n_traces": len(traces),
            "n_in_range": n_used,
            "frac_outside_range": round(frac_outside, 6),
            "H_emp_bits": round(h_emp, 6),
            "H_max_bits": round(H_MAX, 6),
            "delta_H_bits": round(delta_h, 6),
            "delta_H_percent": round(delta_pct, 4),
            "mean_normalized_trace": round(mean_t, 6),
            "std_normalized_trace": round(std_t, 6),
            "occupied_bins": n_occupied,
            "bin_counts": counts,
        }

        print(f"{st:<20} {'-':>7} {len(traces):>10} {h_emp:>8.4f} {delta_h:>8.4f} {delta_pct:>7.2f}%")

    # Sort by delta_H for ranking
    ranked = sorted(results.keys(), key=lambda s: -results[s]["delta_H_bits"])

    print(f"\n{'='*70}")
    print("ENTROPY DEFECT RANKING (largest to smallest):")
    print(f"{'='*70}")
    for i, st in enumerate(ranked, 1):
        r = results[st]
        print(f"  {i:>2}. {st:<20} DeltaH = {r['delta_H_bits']:.4f} bits  ({r['n_traces']:>10} traces, {r['occupied_bins']}/50 bins)")

    # Summary
    delta_values = [results[s]["delta_H_bits"] for s in results]
    print(f"\nGlobal summary:")
    print(f"  Min DeltaH:  {min(delta_values):.4f} bits")
    print(f"  Max DeltaH:  {max(delta_values):.4f} bits")
    print(f"  Mean DeltaH: {sum(delta_values)/len(delta_values):.4f} bits")

    # Save
    output = {
        "description": "Sato-Tate Entropy Defect Spectrum for genus-2 curves",
        "method": "Shannon entropy of normalized Frobenius traces a1/(2*sqrt(p)) in 50 bins on [-2,2]",
        "normalization": "a1 / (2*sqrt(p)), standard Sato-Tate convention for genus-2",
        "H_max_bits": round(H_MAX, 6),
        "n_bins": N_BINS,
        "bin_range": [BIN_MIN, BIN_MAX],
        "min_prime": min_p_threshold,
        "total_curves": total_curves,
        "n_st_groups": len(results),
        "ranking_largest_defect_first": ranked,
        "groups": {st: {k: v for k, v in results[st].items() if k != "bin_counts"} for st in ranked},
        "bin_distributions": {st: results[st]["bin_counts"] for st in ranked},
    }

    with open(OUT_FILE, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_FILE}")


if __name__ == "__main__":
    main()

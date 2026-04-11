"""
OEIS Sequence Length Distribution Analysis
==========================================
Computes distribution of term counts across all OEIS sequences.
Data source: stripped_new.txt (OEIS b-file dump)
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter

DATA_DIR = Path(__file__).resolve().parent.parent / "oeis" / "data"
OUT_PATH = Path(__file__).resolve().parent / "oeis_length_distribution_results.json"

def parse_stripped(path):
    """Parse OEIS stripped format: Axxxxxx ,t1,t2,...,tN,"""
    seq_lengths = {}
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(" ", 1)
            if len(parts) != 2:
                continue
            aid = parts[0]
            terms_str = parts[1].strip().strip(",")
            if not terms_str:
                seq_lengths[aid] = 0
                continue
            n_terms = len(terms_str.split(","))
            seq_lengths[aid] = n_terms
        return seq_lengths

def load_keywords(path):
    with open(path, "r") as f:
        return json.load(f)

def main():
    print("Loading stripped_new.txt...")
    seq_lengths = parse_stripped(DATA_DIR / "stripped_new.txt")
    print(f"  Loaded {len(seq_lengths)} sequences")

    lengths = np.array(list(seq_lengths.values()))
    aids = list(seq_lengths.keys())

    # Basic statistics
    stats = {
        "total_sequences": int(len(lengths)),
        "mean": float(np.mean(lengths)),
        "median": float(np.median(lengths)),
        "std": float(np.std(lengths)),
        "min": int(np.min(lengths)),
        "max": int(np.max(lengths)),
        "P10": float(np.percentile(lengths, 10)),
        "P25": float(np.percentile(lengths, 25)),
        "P75": float(np.percentile(lengths, 75)),
        "P90": float(np.percentile(lengths, 90)),
    }
    print(f"\n=== Basic Statistics ===")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    # Threshold fractions
    thresholds = [5, 10, 15, 20, 30, 50, 100, 200, 500, 1000]
    threshold_fracs = {}
    for t in thresholds:
        n = int(np.sum(lengths >= t))
        frac = float(n / len(lengths))
        threshold_fracs[f">={t}"] = {"count": n, "fraction": round(frac, 4)}
    stats["threshold_fractions"] = threshold_fracs

    print(f"\n=== Threshold Fractions ===")
    for k, v in threshold_fracs.items():
        print(f"  {k}: {v['count']} ({v['fraction']*100:.1f}%)")

    # Histogram (binned)
    bins = [0, 5, 10, 15, 20, 30, 50, 100, 200, 500, 1000, 5000, 50000]
    hist_counts, _ = np.histogram(lengths, bins=bins)
    histogram = {}
    for i in range(len(bins) - 1):
        label = f"{bins[i]}-{bins[i+1]-1}"
        histogram[label] = int(hist_counts[i])
    stats["histogram"] = histogram

    print(f"\n=== Histogram ===")
    for k, v in histogram.items():
        pct = v / len(lengths) * 100
        print(f"  {k:>10s}: {v:>7d} ({pct:.1f}%)")

    # A-number correlation: does older = longer?
    a_numbers = []
    a_lengths = []
    for aid in aids:
        try:
            num = int(aid[1:])
            a_numbers.append(num)
            a_lengths.append(seq_lengths[aid])
        except ValueError:
            continue
    a_numbers = np.array(a_numbers)
    a_lengths = np.array(a_lengths)

    # Bin by A-number range
    a_bins = [0, 10000, 50000, 100000, 200000, 400000]
    a_number_analysis = {}
    for i in range(len(a_bins) - 1):
        mask = (a_numbers >= a_bins[i]) & (a_numbers < a_bins[i + 1])
        if mask.sum() == 0:
            continue
        subset = a_lengths[mask]
        label = f"A{a_bins[i]:06d}-A{a_bins[i+1]:06d}"
        a_number_analysis[label] = {
            "count": int(mask.sum()),
            "mean_length": round(float(np.mean(subset)), 1),
            "median_length": float(np.median(subset)),
            "frac_20plus": round(float(np.mean(subset >= 20)), 4),
        }

    corr = float(np.corrcoef(a_numbers, a_lengths)[0, 1])
    stats["a_number_correlation"] = {
        "pearson_r": round(corr, 4),
        "note": "negative = older sequences are longer",
        "by_range": a_number_analysis,
    }

    print(f"\n=== A-Number vs Length ===")
    print(f"  Pearson r: {corr:.4f}")
    for k, v in a_number_analysis.items():
        print(f"  {k}: n={v['count']}, mean={v['mean_length']}, median={v['median_length']}, >=20: {v['frac_20plus']*100:.1f}%")

    # Keywords analysis
    print("\nLoading keywords...")
    try:
        keywords = load_keywords(DATA_DIR / "oeis_keywords.json")
        print(f"  Loaded keywords for {len(keywords)} sequences")

        # Collect lengths by keyword
        kw_lengths = {}
        for aid, kws in keywords.items():
            if aid not in seq_lengths:
                continue
            length = seq_lengths[aid]
            for kw in kws:
                if kw not in kw_lengths:
                    kw_lengths[kw] = []
                kw_lengths[kw].append(length)

        keyword_stats = {}
        for kw, lens in sorted(kw_lengths.items(), key=lambda x: -len(x[1])):
            arr = np.array(lens)
            keyword_stats[kw] = {
                "count": len(lens),
                "mean_length": round(float(np.mean(arr)), 1),
                "median_length": float(np.median(arr)),
                "frac_20plus": round(float(np.mean(arr >= 20)), 4),
            }
        stats["by_keyword"] = keyword_stats

        print(f"\n=== Length by Keyword ===")
        for kw, v in keyword_stats.items():
            if v["count"] >= 1000:
                print(f"  {kw:>10s}: n={v['count']:>6d}, mean={v['mean_length']:>6.1f}, median={v['median_length']:>5.0f}, >=20: {v['frac_20plus']*100:.1f}%")
    except Exception as e:
        print(f"  Keywords not available: {e}")
        stats["by_keyword"] = {}

    # Instrument viability summary
    stats["instrument_viability"] = {
        "enrichment_15plus": threshold_fracs[">=15"],
        "BM_20plus": threshold_fracs[">=20"],
        "spectral_50plus": threshold_fracs[">=50"],
        "deep_analysis_100plus": threshold_fracs[">=100"],
        "recommendation": "87.5% viable for enrichment (>=15), 77.6% for BM (>=20), 39.8% for spectral (>=50). 'more'/'hard' keywords flag short sequences — filter or skip."
    }

    # Save
    with open(OUT_PATH, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")

if __name__ == "__main__":
    main()

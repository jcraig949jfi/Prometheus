"""
OEIS Consecutive Integer Patterns
----------------------------------
For each OEIS sequence, find the longest run of consecutive integers
(a_{i+1} = a_i + 1). Report distribution, fractions at various thresholds,
and whether high-run sequences are trivial or surprising.
Also: fraction of sequences that are strictly monotone increasing.
"""

import json
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "oeis" / "data"
STRIPPED = DATA_DIR / "stripped_new.txt"
NAMES = DATA_DIR / "names.txt"
OUT = Path(__file__).resolve().parent / "oeis_consecutive_results.json"

# ---------- load names ----------
def load_names():
    names = {}
    with open(NAMES, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split(" ", 1)
            if len(parts) == 2:
                names[parts[0]] = parts[1]
    return names

# ---------- load sequences (first 10k non-comment lines) ----------
def load_sequences(limit=10000):
    seqs = {}
    with open(STRIPPED, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split(" ", 1)
            if len(parts) < 2:
                continue
            aid = parts[0]
            vals_str = parts[1].strip().strip(",")
            if not vals_str:
                continue
            try:
                vals = [int(x) for x in vals_str.split(",") if x.strip()]
            except ValueError:
                continue
            seqs[aid] = vals
            if len(seqs) >= limit:
                break
    return seqs

# ---------- longest consecutive run ----------
def longest_consecutive_run(vals):
    """Return (max_run_length, start_index, start_value) for longest a_{i+1}=a_i+1 run."""
    if len(vals) < 2:
        return 1, 0, vals[0] if vals else 0
    best_len = 1
    best_start = 0
    cur_len = 1
    cur_start = 0
    for i in range(1, len(vals)):
        if vals[i] == vals[i-1] + 1:
            cur_len += 1
        else:
            if cur_len > best_len:
                best_len = cur_len
                best_start = cur_start
            cur_len = 1
            cur_start = i
    if cur_len > best_len:
        best_len = cur_len
        best_start = cur_start
    return best_len, best_start, vals[best_start]

def is_strictly_monotone(vals):
    for i in range(1, len(vals)):
        if vals[i] <= vals[i-1]:
            return False
    return True

def main():
    print("Loading names...")
    names = load_names()
    print("Loading sequences...")
    seqs = load_sequences(10000)
    print(f"Loaded {len(seqs)} sequences")

    results = []
    run_lengths = []
    monotone_count = 0
    total = len(seqs)

    for aid, vals in seqs.items():
        rl, si, sv = longest_consecutive_run(vals)
        mono = is_strictly_monotone(vals)
        if mono:
            monotone_count += 1
        run_lengths.append(rl)
        # Compute run as fraction of sequence length
        frac = rl / len(vals) if len(vals) > 0 else 0
        results.append({
            "id": aid,
            "name": names.get(aid, ""),
            "seq_length": len(vals),
            "max_consecutive_run": rl,
            "run_start_index": si,
            "run_start_value": sv,
            "run_fraction": round(frac, 4),
            "strictly_monotone": mono
        })

    # Distribution
    dist = Counter(run_lengths)
    sorted_dist = sorted(dist.items())

    # Thresholds
    thresholds = [5, 10, 20, 50, 100]
    threshold_results = {}
    for t in thresholds:
        count = sum(1 for r in run_lengths if r >= t)
        threshold_results[f"run_ge_{t}"] = {
            "count": count,
            "fraction": round(count / total, 4)
        }

    # Top 50 by run length
    results.sort(key=lambda x: -x["max_consecutive_run"])
    top50 = results[:50]

    # Classify top sequences
    trivial_keywords = ["natural number", "identity", "integers", "nonnegative", "a(n) = n",
                        "positive integer", "a(n)=n", "counting", "whole number"]
    surprising_top = []
    trivial_top = []
    for r in top50:
        name_lower = r["name"].lower()
        is_trivial = any(kw in name_lower for kw in trivial_keywords)
        if is_trivial:
            trivial_top.append(r)
        else:
            surprising_top.append(r)

    # Summary stats
    import statistics
    summary = {
        "total_sequences": total,
        "mean_max_run": round(statistics.mean(run_lengths), 2),
        "median_max_run": statistics.median(run_lengths),
        "max_max_run": max(run_lengths),
        "strictly_monotone_count": monotone_count,
        "strictly_monotone_fraction": round(monotone_count / total, 4),
        "thresholds": threshold_results,
        "distribution_top30": {str(k): v for k, v in sorted_dist[:30]},
    }

    output = {
        "summary": summary,
        "top50_longest_runs": top50,
        "surprising_long_runs": surprising_top[:20],
        "trivial_long_runs": trivial_top[:10],
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"\n{'='*60}")
    print(f"OEIS Consecutive Integer Pattern Analysis")
    print(f"{'='*60}")
    print(f"Total sequences analyzed: {total}")
    print(f"Mean max consecutive run: {summary['mean_max_run']}")
    print(f"Median max consecutive run: {summary['median_max_run']}")
    print(f"Max consecutive run: {summary['max_max_run']}")
    print(f"\nStrictly monotone increasing: {monotone_count} ({summary['strictly_monotone_fraction']*100:.1f}%)")
    print(f"\nThreshold analysis:")
    for t in thresholds:
        info = threshold_results[f"run_ge_{t}"]
        print(f"  Run >= {t:3d}: {info['count']:5d} sequences ({info['fraction']*100:.1f}%)")
    print(f"\nDistribution (top 15 run lengths):")
    for k, v in sorted_dist[:15]:
        print(f"  Run length {k:3d}: {v:5d} sequences")
    print(f"\nTop 10 longest runs:")
    for r in top50[:10]:
        print(f"  {r['id']} (run={r['max_consecutive_run']}, frac={r['run_fraction']:.2f}): {r['name'][:80]}")
    print(f"\nSurprising long runs (top 10):")
    for r in surprising_top[:10]:
        print(f"  {r['id']} (run={r['max_consecutive_run']}): {r['name'][:80]}")

    print(f"\nResults saved to {OUT}")

if __name__ == "__main__":
    main()

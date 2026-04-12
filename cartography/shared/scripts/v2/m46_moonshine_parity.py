"""
M46: Moonshine parity anomaly
================================
For each moonshine-related OEIS sequence, compute the parity (even/odd)
distribution of terms. Many moonshine sequences (e.g. partition function,
j-function coefficients) have known parity biases.

Compare parity bias of moonshine sequences vs random OEIS sequences.
Is there a universal parity anomaly in moonshine?
"""
import json, time
import numpy as np
from pathlib import Path
from collections import Counter

V2 = Path(__file__).resolve().parent
MOON_OEIS = V2 / "moonshine_oeis_results.json"
OEIS_PATH = V2.parents[3] / "cartography" / "oeis" / "data" / "stripped_new.txt"
OUT = V2 / "m46_moonshine_parity_results.json"

def parity_stats(terms):
    if not terms: return None
    n_even = sum(1 for t in terms if t % 2 == 0)
    n_odd = len(terms) - n_even
    bias = abs(n_even - n_odd) / len(terms)
    return {"n_even": n_even, "n_odd": n_odd, "even_frac": round(n_even / len(terms), 4),
            "bias": round(bias, 4), "dominant": "even" if n_even > n_odd else "odd"}

def main():
    t0 = time.time()
    print("=== M46: Moonshine parity anomaly ===\n")

    with open(MOON_OEIS) as f:
        moon = json.load(f)

    # Extract moonshine OEIS sequence IDs
    moon_seqs = set()
    matches = moon.get("matches", moon.get("moonshine_matches", {}))
    if isinstance(matches, dict):
        for cat, items in matches.items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict) and "oeis_id" in item:
                        moon_seqs.add(item["oeis_id"])
                    elif isinstance(item, str) and item.startswith("A"):
                        moon_seqs.add(item)
            elif isinstance(items, str):
                moon_seqs.add(items)
    elif isinstance(matches, list):
        for item in matches:
            if isinstance(item, dict) and "oeis_id" in item:
                moon_seqs.add(item["oeis_id"])

    print(f"  {len(moon_seqs)} moonshine-linked OEIS sequences")

    # Load OEIS and compute parity for moonshine vs random
    print("  Loading OEIS sequences...")
    oeis = {}
    with open(OEIS_PATH, 'r', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or not line.startswith('A'): continue
            parts = line.split(',')
            sid = parts[0].strip().split()[0]
            terms = []
            for t in parts[1:]:
                t = t.strip()
                if t:
                    try: terms.append(int(t))
                    except: pass
            if len(terms) >= 10:
                oeis[sid] = terms
    print(f"  {len(oeis)} OEIS sequences loaded")

    # Moonshine parity
    print("\n  Computing moonshine parity statistics...")
    moon_parity = []
    for sid in sorted(moon_seqs):
        if sid in oeis:
            ps = parity_stats(oeis[sid][:50])
            if ps:
                ps["oeis_id"] = sid
                moon_parity.append(ps)

    print(f"  {len(moon_parity)} moonshine sequences with parity data")
    if moon_parity:
        mean_even = float(np.mean([p["even_frac"] for p in moon_parity]))
        mean_bias = float(np.mean([p["bias"] for p in moon_parity]))
        print(f"  Mean even fraction: {mean_even:.4f}")
        print(f"  Mean parity bias: {mean_bias:.4f}")

    # Random baseline: sample 1000 OEIS sequences
    np.random.seed(42)
    all_sids = list(oeis.keys())
    sample_size = min(2000, len(all_sids))
    sample_sids = np.random.choice(all_sids, sample_size, replace=False)
    random_parity = []
    for sid in sample_sids:
        ps = parity_stats(oeis[sid][:50])
        if ps:
            random_parity.append(ps)

    random_even = float(np.mean([p["even_frac"] for p in random_parity])) if random_parity else 0.5
    random_bias = float(np.mean([p["bias"] for p in random_parity])) if random_parity else 0

    print(f"\n  Random OEIS baseline ({len(random_parity)} seqs):")
    print(f"  Mean even fraction: {random_even:.4f}")
    print(f"  Mean parity bias: {random_bias:.4f}")

    # Statistical test
    from scipy import stats as sp_stats
    if moon_parity and random_parity:
        moon_biases = [p["bias"] for p in moon_parity]
        rand_biases = [p["bias"] for p in random_parity]
        stat, p_val = sp_stats.mannwhitneyu(moon_biases, rand_biases, alternative='two-sided')
        print(f"\n  Mann-Whitney U: stat={stat:.0f}, p={p_val:.4e}")

        moon_evens = [p["even_frac"] for p in moon_parity]
        rand_evens = [p["even_frac"] for p in random_parity]
        stat2, p_val2 = sp_stats.mannwhitneyu(moon_evens, rand_evens, alternative='two-sided')
        print(f"  Even-fraction MWU: stat={stat2:.0f}, p={p_val2:.4e}")
    else:
        p_val = 1.0; p_val2 = 1.0

    # Extreme moonshine sequences (highest bias)
    moon_parity.sort(key=lambda x: -x["bias"])
    print("\n  Most parity-biased moonshine sequences:")
    for p in moon_parity[:10]:
        print(f"    {p['oeis_id']}: even={p['even_frac']:.2f}, bias={p['bias']:.3f} ({p['dominant']})")

    elapsed = time.time() - t0
    output = {
        "probe": "M46", "title": "Moonshine parity anomaly",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_moonshine_seqs": len(moon_parity),
        "n_random_seqs": len(random_parity),
        "moonshine_parity": {
            "mean_even_frac": round(mean_even, 4) if moon_parity else None,
            "mean_bias": round(mean_bias, 4) if moon_parity else None,
        },
        "random_baseline": {
            "mean_even_frac": round(random_even, 4),
            "mean_bias": round(random_bias, 4),
        },
        "mwu_bias_pvalue": float(p_val),
        "mwu_even_pvalue": float(p_val2),
        "most_biased": moon_parity[:10],
        "assessment": None,
    }

    if p_val < 0.01:
        diff = mean_bias - random_bias if moon_parity else 0
        direction = "MORE biased" if diff > 0 else "LESS biased"
        output["assessment"] = f"PARITY ANOMALY: moonshine sequences are {direction} than random (Δ={diff:.3f}, p={p_val:.2e})"
    elif p_val < 0.05:
        output["assessment"] = f"WEAK ANOMALY: p={p_val:.3f}. Marginal parity difference"
    else:
        output["assessment"] = f"NO ANOMALY: p={p_val:.3f}. Moonshine parity indistinguishable from random OEIS"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()

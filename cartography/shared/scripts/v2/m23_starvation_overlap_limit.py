"""
M23: Starvation overlap limit
================================
For forms that are mod-p starved, how many distinct primes can a single form
be starved at simultaneously? Is there a hard ceiling? Does the number of
simultaneous starvations follow a Poisson distribution (independent) or
show excess correlation?
"""
import json, time
import numpy as np
from scipy import stats as sp_stats
from pathlib import Path
from collections import Counter

V2 = Path(__file__).resolve().parent
STARV = V2 / "residue_starvation_results.json"
OUT = V2 / "m23_starvation_overlap_results.json"

def main():
    t0 = time.time()
    print("=== M23: Starvation overlap limit ===\n")

    with open(STARV) as f:
        data = json.load(f)

    starved = data["starved_forms"]
    print(f"  {len(starved)} starved forms loaded")

    # Count simultaneous starvations per form
    starvation_counts = Counter()
    max_simultaneous = 0
    max_form = None
    prime_cooccurrence = Counter()

    for form in starved:
        primes = sorted(form["starvation"].keys())
        n = len(primes)
        starvation_counts[n] += 1
        if n > max_simultaneous:
            max_simultaneous = n
            max_form = form["label"]
        # Co-occurrence pairs
        for i in range(len(primes)):
            for j in range(i+1, len(primes)):
                prime_cooccurrence[f"{primes[i]},{primes[j]}"] += 1

    print(f"  Starvation count distribution:")
    for k in sorted(starvation_counts.keys()):
        print(f"    Starved at {k} prime(s): {starvation_counts[k]} forms")
    print(f"  Maximum simultaneous starvation: {max_simultaneous} (form: {max_form})")

    # Poisson test: if starvations are independent, count ~ Poisson(λ)
    counts_list = []
    for form in starved:
        counts_list.append(len(form["starvation"]))
    counts_arr = np.array(counts_list)
    lambda_hat = float(np.mean(counts_arr))
    var = float(np.var(counts_arr))
    dispersion = var / lambda_hat if lambda_hat > 0 else 0

    print(f"\n  Poisson test:")
    print(f"    Mean starvation count: {lambda_hat:.4f}")
    print(f"    Variance: {var:.4f}")
    print(f"    Dispersion (var/mean): {dispersion:.4f}")
    if dispersion > 1.5:
        print(f"    → OVERDISPERSED: starvations are CORRELATED")
    elif dispersion < 0.7:
        print(f"    → UNDERDISPERSED: starvations are ANTI-CORRELATED")
    else:
        print(f"    → NEAR POISSON: starvations are approximately independent")

    # Co-occurrence analysis
    print(f"\n  Prime co-occurrence (top pairs):")
    for pair, cnt in prime_cooccurrence.most_common(10):
        p1, p2 = pair.split(",")
        # Expected under independence
        n1 = sum(1 for f in starved if p1 in f["starvation"])
        n2 = sum(1 for f in starved if p2 in f["starvation"])
        expected = n1 * n2 / len(starved)
        enrichment = cnt / expected if expected > 0 else 0
        print(f"    ({p1},{p2}): {cnt} observed, {expected:.1f} expected, {enrichment:.2f}x")

    # Which primes contribute most to multi-starvation?
    print(f"\n  Per-prime starvation frequency:")
    prime_freq = Counter()
    for form in starved:
        for p in form["starvation"]:
            prime_freq[p] += 1
    for p, cnt in prime_freq.most_common():
        print(f"    mod-{p}: {cnt} forms ({cnt/len(starved):.1%})")

    # Hard ceiling test
    total_forms_in_db = data.get("total_forms_analyzed", 17314)
    starvation_rate = len(starved) / total_forms_in_db
    multi_rate = sum(v for k, v in starvation_counts.items() if k >= 2) / total_forms_in_db

    elapsed = time.time() - t0
    output = {
        "probe": "M23", "title": "Starvation overlap limit",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_starved_forms": len(starved),
        "total_forms": total_forms_in_db,
        "starvation_count_distribution": {str(k): v for k, v in sorted(starvation_counts.items())},
        "max_simultaneous": max_simultaneous,
        "max_form": max_form,
        "poisson_test": {
            "lambda": round(lambda_hat, 4),
            "variance": round(var, 4),
            "dispersion": round(dispersion, 4),
        },
        "prime_cooccurrence": {k: v for k, v in prime_cooccurrence.most_common(15)},
        "per_prime_frequency": dict(prime_freq),
        "starvation_rate": round(starvation_rate, 6),
        "multi_starvation_rate": round(multi_rate, 6),
        "assessment": None,
    }

    if max_simultaneous >= 4:
        output["assessment"] = f"HIGH CEILING: forms can be starved at up to {max_simultaneous} primes simultaneously. Dispersion={dispersion:.2f}"
    elif max_simultaneous == 3:
        output["assessment"] = f"MODERATE CEILING: max {max_simultaneous} simultaneous starvations. Dispersion={dispersion:.2f}"
    elif max_simultaneous <= 2:
        output["assessment"] = f"HARD CEILING at {max_simultaneous}: forms rarely starved at more than 2 primes. Dispersion={dispersion:.2f}"

    if dispersion > 1.5:
        output["assessment"] += " — OVERDISPERSED (starvations cluster)"
    elif dispersion < 0.7:
        output["assessment"] += " — UNDERDISPERSED (anti-correlation)"
    else:
        output["assessment"] += " — near Poisson (independent)"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()

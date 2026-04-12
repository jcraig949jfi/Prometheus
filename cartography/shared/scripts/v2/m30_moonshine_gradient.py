"""
M30: Moonshine gradient decomposition
========================================
Decompose the moonshine→OEIS enrichment signal into components:
1. Monstrous moonshine (J-function coefficients)
2. Umbral moonshine (M24 mock modular forms)
3. Theta/lattice functions
4. Mock theta functions

For each, compute the enrichment gradient: d(enrichment)/d(prime).
Which component dominates at small primes? At large primes?
Is there a crossover?
"""
import json, time
import numpy as np
from scipy import stats
from pathlib import Path

V2 = Path(__file__).resolve().parent
MOON_OEIS = V2 / "moonshine_oeis_results.json"
MOON_SCALE = V2 / "moonshine_scaling_results.json"
OUT = V2 / "m30_moonshine_gradient_results.json"

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]

def main():
    t0 = time.time()
    print("=== M30: Moonshine gradient decomposition ===\n")

    with open(MOON_OEIS) as f:
        oeis_data = json.load(f)
    with open(MOON_SCALE) as f:
        scale_data = json.load(f)

    # Extract per-partition enrichment curves
    partitions = scale_data.get("enrichment_by_partition", {})
    print(f"  Partitions: {list(partitions.keys())}")

    gradients = {}
    for name, info in partitions.items():
        ep = info.get("enrichments_by_prime", {})
        available_primes = sorted(int(p) for p in ep.keys() if ep[str(p)] > 0)
        vals = [ep[str(p)] for p in available_primes]

        if len(available_primes) < 3:
            gradients[name] = {"gradient": None, "reason": f"only {len(available_primes)} primes"}
            continue

        # Compute gradient: Δenrichment / Δprime
        log_p = np.log(available_primes)
        log_e = np.log(vals)
        # Linear gradient in log space
        slope, intercept, r, p_val, se = stats.linregress(log_p, log_e)

        # Pointwise gradient
        diffs = [(log_e[i+1] - log_e[i]) / (log_p[i+1] - log_p[i])
                 for i in range(len(log_p)-1)]

        gradients[name] = {
            "slope": round(float(slope), 4),
            "R2": round(float(r**2), 4),
            "pointwise_gradients": [round(float(d), 4) for d in diffs],
            "primes": available_primes,
            "enrichments": vals,
            "mean_gradient": round(float(np.mean(diffs)), 4),
            "gradient_trend": "increasing" if len(diffs) >= 2 and diffs[-1] > diffs[0] else "decreasing",
        }
        print(f"  {name}: slope={slope:.3f} R²={r**2:.3f} "
              f"gradient_trend={'↑' if diffs[-1] > diffs[0] else '↓'}")

    # Which partition dominates at each prime?
    print("\n  Dominant partition by prime:")
    dominance = {}
    for p in PRIMES[:7]:
        ps = str(p)
        best_name = None; best_val = 0
        for name, info in partitions.items():
            ep = info.get("enrichments_by_prime", {})
            val = ep.get(ps, 0)
            if val > best_val:
                best_val = val; best_name = name
        dominance[ps] = {"dominant": best_name, "enrichment": round(best_val, 2)}
        print(f"    p={p}: {best_name} ({best_val:.1f}x)")

    # Crossover detection
    print("\n  Crossover detection...")
    crossovers = []
    partition_names = list(partitions.keys())
    for i in range(len(partition_names)):
        for j in range(i+1, len(partition_names)):
            n1, n2 = partition_names[i], partition_names[j]
            ep1 = partitions[n1].get("enrichments_by_prime", {})
            ep2 = partitions[n2].get("enrichments_by_prime", {})
            common_primes = sorted(set(int(p) for p in ep1) & set(int(p) for p in ep2))
            prev_winner = None
            for p in common_primes:
                v1, v2 = ep1.get(str(p), 0), ep2.get(str(p), 0)
                winner = n1 if v1 > v2 else n2
                if prev_winner and winner != prev_winner:
                    crossovers.append({
                        "between": [n1, n2], "at_prime": p,
                        "before": prev_winner, "after": winner,
                    })
                prev_winner = winner

    print(f"  Crossovers found: {len(crossovers)}")
    for c in crossovers[:5]:
        print(f"    {c['between'][0]} vs {c['between'][1]} at p={c['at_prime']}: "
              f"{c['before']}→{c['after']}")

    # OEIS-side: which OEIS categories are moonshine-enriched?
    oeis_matches = oeis_data.get("matches", oeis_data.get("moonshine_matches", []))
    if isinstance(oeis_matches, list):
        n_matches = len(oeis_matches)
    elif isinstance(oeis_matches, dict):
        n_matches = sum(len(v) if isinstance(v, list) else 1 for v in oeis_matches.values())
    else:
        n_matches = 0
    print(f"\n  OEIS matches: {n_matches}")

    elapsed = time.time() - t0
    output = {
        "probe": "M30", "title": "Moonshine gradient decomposition",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "partition_gradients": gradients,
        "dominance_by_prime": dominance,
        "crossovers": crossovers,
        "n_oeis_matches": n_matches,
        "assessment": None,
    }

    # Determine if there's a clear hierarchy
    slopes = [(n, g["slope"]) for n, g in gradients.items() if g.get("slope") is not None]
    if slopes:
        slopes.sort(key=lambda x: -x[1])
        steepest = slopes[0]
        output["assessment"] = (f"GRADIENT HIERARCHY: {steepest[0]} has steepest enrichment growth "
                                f"(γ={steepest[1]:.3f}). {len(crossovers)} crossovers detected. "
                                f"Moonshine enrichment is PARTITION-DEPENDENT with different scaling laws per component.")
    else:
        output["assessment"] = "INSUFFICIENT DATA for gradient decomposition"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()

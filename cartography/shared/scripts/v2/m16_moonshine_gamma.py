"""
M16: Moonshine scaling exponent γ
===================================
Fit enrichment(p) = A * p^γ for each moonshine partition.
Extract γ per partition. Compare monstrous vs umbral vs theta.
Is γ universal or partition-dependent?
"""
import json, time
import numpy as np
from scipy import stats
from pathlib import Path

V2 = Path(__file__).resolve().parent
MOON = V2 / "moonshine_scaling_results.json"
OUT = V2 / "m16_moonshine_gamma_results.json"
PRIMES = [2, 3, 5, 7, 11]

def main():
    t0 = time.time()
    print("=== M16: Moonshine scaling exponent γ ===\n")
    with open(MOON) as f:
        data = json.load(f)

    partitions = data["enrichment_by_partition"]
    fits = {}
    for name, info in partitions.items():
        ep = info["enrichments_by_prime"]
        vals = [ep[str(p)] for p in PRIMES]
        # Filter zeros
        pos = [(p, v) for p, v in zip(PRIMES, vals) if v > 0]
        if len(pos) < 3:
            fits[name] = {"gamma": None, "reason": f"only {len(pos)} nonzero primes"}
            print(f"  {name}: SKIP ({len(pos)} nonzero)")
            continue
        log_p = np.log([x[0] for x in pos])
        log_e = np.log([x[1] for x in pos])
        slope, intercept, r, p_val, se = stats.linregress(log_p, log_e)
        fits[name] = {
            "gamma": round(float(slope), 4),
            "A": round(float(np.exp(intercept)), 4),
            "R2": round(float(r**2), 4),
            "p_value": float(p_val),
            "se": round(float(se), 4),
            "n_primes_used": len(pos),
            "enrichments": {str(p): v for p, v in pos},
        }
        print(f"  {name}: γ={slope:.3f} A={np.exp(intercept):.1f} R²={r**2:.4f}")

    # Within-group premium
    premium = data.get("moonshine_premium", {}).get("within_group", {})
    prem_vals = [(int(p), v["enrichment"]) for p, v in premium.items() if v["enrichment"] > 0]
    if len(prem_vals) >= 3:
        log_p = np.log([x[0] for x in prem_vals])
        log_e = np.log([x[1] for x in prem_vals])
        slope, intercept, r, _, se = stats.linregress(log_p, log_e)
        premium_fit = {"gamma": round(float(slope), 4), "R2": round(float(r**2), 4)}
        print(f"\n  Within-group premium: γ={slope:.3f} R²={r**2:.4f}")
    else:
        premium_fit = None

    # Is gamma universal?
    gammas = [f["gamma"] for f in fits.values() if f.get("gamma") is not None]
    gamma_std = float(np.std(gammas)) if gammas else 0
    gamma_mean = float(np.mean(gammas)) if gammas else 0
    cv = gamma_std / abs(gamma_mean) if abs(gamma_mean) > 0.01 else float('inf')

    elapsed = time.time() - t0
    output = {
        "probe": "M16", "title": "Moonshine scaling exponent γ",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "partition_fits": fits,
        "premium_fit": premium_fit,
        "gamma_statistics": {
            "values": {k: v["gamma"] for k, v in fits.items() if v.get("gamma")},
            "mean": round(gamma_mean, 4), "std": round(gamma_std, 4),
            "cv": round(cv, 4),
        },
        "assessment": None,
    }
    if cv < 0.3 and len(gammas) >= 3:
        output["assessment"] = f"UNIVERSAL γ: mean={gamma_mean:.3f}±{gamma_std:.3f} (CV={cv:.2f}) — exponent is partition-independent"
    elif cv < 1.0:
        output["assessment"] = f"WEAKLY UNIVERSAL: γ={gamma_mean:.3f}±{gamma_std:.3f} (CV={cv:.2f}) — some partition dependence"
    else:
        output["assessment"] = f"PARTITION-DEPENDENT: γ varies widely (CV={cv:.2f}). No universal exponent."

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()

"""
M36: Adelic fibre bundle geometry
===================================
Extend the multi-prime intersection to ℓ up to 13. For each subset of primes,
compute how many forms share the same tuple of a_p mod ℓ (the fibre size).
Fit decay of average fibre size vs number of primes used.
Is it exponential or power-law?
"""
import json, time, math
import numpy as np
import duckdb
from scipy import stats
from pathlib import Path
from itertools import combinations
from collections import Counter

V2 = Path(__file__).resolve().parent
DB = V2.parents[3] / "charon" / "data" / "charon.duckdb"
OUT = V2 / "m36_adelic_fibre_results.json"

def sieve(limit):
    is_p = [True] * (limit + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_p[i]:
            for j in range(i*i, limit+1, i): is_p[j] = False
    return [i for i in range(2, limit+1) if is_p[i]]

def prime_factors(n):
    f = set(); d = 2
    while d*d <= n:
        while n % d == 0: f.add(d); n //= d
        d += 1
    if n > 1: f.add(n)
    return f

def main():
    t0 = time.time()
    print("=== M36: Adelic fibre bundle geometry ===\n")

    con = duckdb.connect(str(DB), read_only=True)
    rows = con.execute("""
        SELECT lmfdb_label, level, ap_coeffs FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND char_order = 1
        ORDER BY level
    """).fetchall()
    con.close()
    print(f"  {len(rows)} forms loaded")

    ap_primes = sieve(50)
    ELLS = [2, 3, 5, 7, 11, 13]

    # Parse a_p and build residue tuples
    forms = []
    for label, level, ap_json in rows:
        ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
        ap_vals = [x[0] if isinstance(x, list) else x for x in ap]
        bad = prime_factors(level)
        residues = {}
        for ell in ELLS:
            idx = ap_primes.index(ell) if ell in ap_primes else -1
            if idx >= 0 and idx < len(ap_vals) and ell not in bad:
                residues[ell] = ap_vals[idx] % ell
        forms.append({"label": label, "level": level, "residues": residues})

    # For each subset of ELLS, count fibre sizes
    print("\n  Computing fibre sizes for prime subsets...")
    decay_data = []
    for k in range(1, len(ELLS) + 1):
        fibre_sizes = []
        n_subsets = 0
        for subset in combinations(ELLS, k):
            n_subsets += 1
            # Build tuple for each form
            tuples = Counter()
            valid = 0
            for f in forms:
                tup = tuple(f["residues"].get(ell, -1) for ell in subset)
                if -1 not in tup:
                    tuples[tup] += 1
                    valid += 1
            if valid > 0:
                avg_fibre = valid / len(tuples) if tuples else valid
                max_fibre = max(tuples.values()) if tuples else 0
                n_singletons = sum(1 for v in tuples.values() if v == 1)
                fibre_sizes.append({
                    "subset": list(subset),
                    "n_valid": valid,
                    "n_distinct_fibres": len(tuples),
                    "avg_fibre_size": round(avg_fibre, 2),
                    "max_fibre_size": max_fibre,
                    "singleton_fraction": round(n_singletons / len(tuples), 4) if tuples else 0,
                })
            if n_subsets >= 15:  # Cap combinatorial explosion
                break

        if fibre_sizes:
            mean_avg = float(np.mean([fs["avg_fibre_size"] for fs in fibre_sizes]))
            mean_singleton = float(np.mean([fs["singleton_fraction"] for fs in fibre_sizes]))
            decay_data.append({
                "k": k,
                "n_subsets_tested": len(fibre_sizes),
                "mean_avg_fibre": round(mean_avg, 2),
                "mean_singleton_frac": round(mean_singleton, 4),
                "examples": fibre_sizes[:3],
            })
            print(f"  k={k}: avg_fibre={mean_avg:.1f}, singleton_frac={mean_singleton:.3f} "
                  f"({len(fibre_sizes)} subsets)")

    # Fit decay: log(avg_fibre) vs k
    if len(decay_data) >= 3:
        ks = [d["k"] for d in decay_data]
        log_fibre = [np.log(d["mean_avg_fibre"]) for d in decay_data if d["mean_avg_fibre"] > 0]
        ks_valid = ks[:len(log_fibre)]
        slope, intercept, r, p_val, se = stats.linregress(ks_valid, log_fibre)
        exp_decay = {"slope": round(float(slope), 4), "R2": round(float(r**2), 4),
                     "half_life": round(-math.log(2) / slope, 2) if slope < 0 else None}
        print(f"\n  Exponential fit: fibre ~ exp({slope:.3f} * k), R²={r**2:.4f}")
        if exp_decay["half_life"]:
            print(f"  Half-life: {exp_decay['half_life']:.1f} primes")
        # Power-law fit
        slope2, int2, r2, _, _ = stats.linregress(np.log(ks_valid), log_fibre)
        power_fit = {"exponent": round(float(slope2), 4), "R2": round(float(r2**2), 4)}
        print(f"  Power-law fit: fibre ~ k^{slope2:.2f}, R²={r2**2:.4f}")
    else:
        exp_decay, power_fit = None, None

    # Singleton rigidity: at what k does singleton_frac > 0.9?
    rigidity_k = None
    for d in decay_data:
        if d["mean_singleton_frac"] > 0.9:
            rigidity_k = d["k"]; break

    elapsed = time.time() - t0
    output = {
        "probe": "M36", "title": "Adelic fibre bundle geometry",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_forms": len(forms),
        "primes_tested": ELLS,
        "decay_curve": decay_data,
        "exponential_fit": exp_decay,
        "power_law_fit": power_fit,
        "rigidity_k": rigidity_k,
        "assessment": None,
    }

    if exp_decay and power_fit:
        if exp_decay["R2"] > power_fit["R2"]:
            output["assessment"] = f"EXPONENTIAL DECAY: fibre ~ exp({exp_decay['slope']:.3f}k), R²={exp_decay['R2']:.3f}. Half-life={exp_decay['half_life']} primes. Rigidity at k={rigidity_k}"
        else:
            output["assessment"] = f"POWER-LAW DECAY: fibre ~ k^{power_fit['exponent']:.2f}, R²={power_fit['R2']:.3f}. Rigidity at k={rigidity_k}"
    else:
        output["assessment"] = "INSUFFICIENT DATA for decay fit"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()

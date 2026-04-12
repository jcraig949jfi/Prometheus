"""
M17: Adelic entropy decay rate
================================
For each prime p, compute H_p = entropy of a_p mod p across all weight-2 newforms.
Then fit the decay H_p vs p. Question: does information content decay as
H ~ log(p) (trivial: more bins = more entropy) or faster/slower?
Subtract the null H_null = log(p) and fit the residual.
"""
import json, time, math
import numpy as np
import duckdb
from scipy import stats
from pathlib import Path
from collections import Counter

V2 = Path(__file__).resolve().parent
DB = V2.parents[3] / "charon" / "data" / "charon.duckdb"
OUT = V2 / "m17_adelic_entropy_results.json"
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

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
    print("=== M17: Adelic entropy decay rate ===\n")
    con = duckdb.connect(str(DB), read_only=True)
    rows = con.execute("""
        SELECT level, ap_coeffs FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND char_order = 1
    """).fetchall()
    con.close()
    print(f"  Loaded {len(rows)} forms")

    ap_primes = sieve(50)
    results = []
    for ell in PRIMES:
        # Index of ell in our prime list
        idx = ap_primes.index(ell) if ell in ap_primes else -1
        if idx < 0: continue
        residues = Counter()
        n_good = 0
        for level, ap_json in rows:
            if ell in prime_factors(level): continue
            ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
            if idx >= len(ap): continue
            val = ap[idx]
            if isinstance(val, list): val = val[0]
            residues[val % ell] += 1
            n_good += 1
        if n_good < 100: continue
        # Entropy
        total = sum(residues.values())
        probs = np.array([residues.get(r, 0) / total for r in range(ell)])
        probs = probs[probs > 0]
        H = float(-np.sum(probs * np.log2(probs)))
        H_null = math.log2(ell)
        H_ratio = H / H_null
        results.append({
            "ell": ell, "H": round(H, 4), "H_null": round(H_null, 4),
            "H_ratio": round(H_ratio, 6),
            "H_residual": round(H - H_null, 6),
            "n_forms": n_good,
            "n_classes_hit": len(residues),
        })
        print(f"  ell={ell:>2}: H={H:.4f} H_null={H_null:.4f} ratio={H_ratio:.4f} "
              f"residual={H-H_null:.4f} (n={n_good})")

    # Fit H_ratio vs log(ell)
    if len(results) >= 3:
        ells = [r["ell"] for r in results]
        ratios = [r["H_ratio"] for r in results]
        residuals = [r["H_residual"] for r in results]
        log_ell = np.log(ells)
        slope, intercept, r, p_val, se = stats.linregress(log_ell, ratios)
        ratio_fit = {"slope": round(float(slope), 6), "intercept": round(float(intercept), 4),
                     "R2": round(float(r**2), 4), "p_value": float(p_val)}
        print(f"\n  H_ratio vs log(ell): slope={slope:.6f} R²={r**2:.4f}")
        # Fit residual vs ell
        slope2, int2, r2, p2, se2 = stats.linregress(ells, residuals)
        resid_fit = {"slope": round(float(slope2), 6), "R2": round(float(r2**2), 4)}
        print(f"  Residual vs ell: slope={slope2:.6f} R²={r2**2:.4f}")
    else:
        ratio_fit, resid_fit = None, None

    elapsed = time.time() - t0
    output = {
        "probe": "M17", "title": "Adelic entropy decay rate",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "entropy_by_prime": results,
        "ratio_fit": ratio_fit,
        "residual_fit": resid_fit,
        "assessment": None,
    }

    if ratio_fit and abs(ratio_fit["slope"]) < 0.01 and ratio_fit["R2"] < 0.3:
        output["assessment"] = f"FLAT: H/H_null ≈ constant across primes — entropy tracks log(p) exactly (trivial scaling)"
    elif ratio_fit and ratio_fit["slope"] < -0.01:
        output["assessment"] = f"DECAYING: H/H_null decreases with p (slope={ratio_fit['slope']:.4f}) — larger primes carry LESS relative information"
    elif ratio_fit and ratio_fit["slope"] > 0.01:
        output["assessment"] = f"GROWING: H/H_null increases with p (slope={ratio_fit['slope']:.4f}) — larger primes approach uniform faster"
    else:
        output["assessment"] = "INCONCLUSIVE: not enough data points for reliable fit"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()

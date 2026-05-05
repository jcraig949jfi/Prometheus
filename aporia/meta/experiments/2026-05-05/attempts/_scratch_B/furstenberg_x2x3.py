"""Computational probes for the Furstenberg x2 x3 conjecture.

We attempt three probes:

(A) Empirical invariant-measure estimation under joint x2,x3 action.
    Iterate a random orbit through the random-product action (apply x2
    or x3 with prob 1/2 each); estimate the empirical density on T = R/Z.
    Compare to Lebesgue.

(B) Construct a candidate non-Lebesgue x2 x3 invariant measure
    supported on a subset, and check if it is actually invariant.
    The natural candidate is a self-similar Cantor set under both maps,
    which forces it to be all of T (because gcd(log 2, log 3) is
    irrational, so 2 and 3 generate a dense subgroup of R). Document
    that this rules out simple constructions.

(C) For finite-precision (q-adic) approximations: study the joint
    action of x2 and x3 on Z/q for q coprime to 6, and check
    invariant-measure rigidity numerically.
"""
import json
import time
import numpy as np


def random_product_orbit(x0, n_steps=10**6, p2=0.5, seed=0):
    """Random product of x2 and x3 maps. Each step: with prob p2 apply
    x2; else x3. Return histogram of orbit positions."""
    rng = np.random.default_rng(seed)
    x = x0
    bins = np.zeros(1000)
    for _ in range(n_steps):
        if rng.uniform() < p2:
            x = (2 * x) % 1.0
        else:
            x = (3 * x) % 1.0
        b = int(x * 1000)
        if b == 1000:
            b = 999
        bins[b] += 1
    return bins / n_steps


def kl_to_uniform(hist):
    """KL divergence of histogram to uniform 1/len(hist)."""
    n = len(hist)
    p = np.maximum(hist, 1e-12)
    p = p / p.sum()
    q = np.full(n, 1.0 / n)
    return float(np.sum(p * np.log(p / q)))


def mod_q_orbit_diversity(q, n_orbits=100, n_steps=200, seed=0):
    """For Z/q (q coprime to 6), the maps x2, x3 act as multiplication.
    The conjecture's analogue here is: the only invariant measure
    under both is the uniform measure on the cyclic subgroup generated
    by 2 and 3 (which is the whole of (Z/q)* if q prime, etc).
    Compute orbit-size distribution; if all orbits are large and
    similar size, structurally there's no x2 x3 invariant probability
    measure on a proper subset.
    """
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, q, size=n_orbits)
    orbit_sets = []
    for x0 in starts:
        seen = set()
        x = int(x0)
        # explore mixed product action
        for _ in range(n_steps):
            seen.add(x)
            if rng.uniform() < 0.5:
                x = (2 * x) % q
            else:
                x = (3 * x) % q
        orbit_sets.append(len(seen))
    return {
        "q": int(q),
        "orbit_sizes_observed": [int(s) for s in orbit_sets],
        "min_size": int(min(orbit_sets)),
        "max_size": int(max(orbit_sets)),
        "mean_size": float(np.mean(orbit_sets)),
        "fraction_visited": float(np.mean(orbit_sets) / q),
    }


def cantor_self_similarity_check(scale, n_iter=1000, n_check=10000):
    """Try to construct a candidate Cantor set: start with [0, scale],
    and iterate forwards under both x2 (mod 1) and x3 (mod 1).
    Both forward maps expand. The closure of the forward orbit of any
    nontrivial interval under <x2, x3> is dense in T (well known).
    Verify numerically on a uniform sample.
    """
    pts = np.linspace(0, scale, n_check)
    for _ in range(n_iter):
        new = []
        for x in pts:
            new.append((2 * x) % 1.0)
            new.append((3 * x) % 1.0)
        pts = np.unique(np.round(new, 7))
        if len(pts) > 50000:
            pts = pts[:: max(1, len(pts) // 50000)]
    bins = np.histogram(pts, bins=100, range=(0, 1))[0]
    return {
        "n_pts_after_iter": int(len(pts)),
        "histogram_min": int(bins.min()),
        "histogram_max": int(bins.max()),
        "histogram_uniformity": float(bins.std() / max(bins.mean(), 1e-9)),
    }


if __name__ == "__main__":
    t0 = time.time()
    out = {}

    print("Probe A: random-product orbit on T")
    res_A = []
    for seed in [0, 1, 2]:
        for p2 in [0.3, 0.5, 0.7]:
            for x0 in [0.123456789, 1 / np.sqrt(2), np.e - 2]:
                bins = random_product_orbit(x0, n_steps=200_000, p2=p2, seed=seed)
                kl = kl_to_uniform(bins)
                res_A.append({
                    "seed": seed, "p2": p2, "x0": float(x0),
                    "kl_to_uniform": float(kl),
                    "max_bin_density": float(bins.max() * 1000),
                    "min_bin_density": float(bins.min() * 1000),
                })
                print(f"  seed={seed} p2={p2:.1f} x0={x0:.4f}  KL={kl:.5f}  max_dens={bins.max()*1000:.3f}")
    out["probe_A_random_product"] = res_A

    print("\nProbe B: closure of forward-orbit (small interval -> dense)")
    res_B = cantor_self_similarity_check(scale=0.01, n_iter=8, n_check=1000)
    print(f"  {res_B}")
    out["probe_B_orbit_closure"] = res_B

    print("\nProbe C: Z/q rigidity for q coprime to 6")
    res_C = []
    for q in [7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        r = mod_q_orbit_diversity(q, n_orbits=200, n_steps=300, seed=0)
        res_C.append(r)
        print(f"  q={q:3d}  mean_orbit_size={r['mean_size']:.1f}  frac={r['fraction_visited']:.3f}")
    out["probe_C_mod_q"] = res_C

    elapsed = time.time() - t0
    out["elapsed_sec"] = elapsed
    with open("D:/Prometheus/aporia/meta/experiments/2026-05-05/attempts/_scratch_B/furstenberg_results.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nDone in {elapsed:.1f}s")

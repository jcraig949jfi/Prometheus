"""
Brute-force sampling: how many rank-7 orbits under the 24-element gauge?

Directly samples random (A, B, C) in F_2^{4x7}^3, checks validity against
MATMUL_T, canonicalizes valid ones, counts distinct canonical forms.

This is a statistical probe, not a proof. But if it hits many distinct
rank-7 orbits, the MAP-Elites finding of "only 1 orbit" is an exploration
artifact, not a domain property.
"""
from __future__ import annotations
import time
import numpy as np

from .core import MATMUL_T, is_matmul_decomp
from .gauge import canonicalize, ISO_SIZE


def brute_force_rank7(n_samples: int = 200_000, seed: int = 42,
                      density: float = 0.5, verbose: bool = True):
    rng = np.random.default_rng(seed)
    orbits = set()
    valid_count = 0
    t0 = time.time()

    for i in range(n_samples):
        A = (rng.random((4, 7)) < density).astype(np.uint8)
        B = (rng.random((4, 7)) < density).astype(np.uint8)
        C = (rng.random((4, 7)) < density).astype(np.uint8)

        if is_matmul_decomp(A, B, C):
            valid_count += 1
            (_, _, _), b = canonicalize(A, B, C)
            orbits.add(b)

        if verbose and (i + 1) % 50_000 == 0:
            elapsed = time.time() - t0
            print(f"  {i+1:>7} samples, {valid_count:>4} valid, "
                  f"{len(orbits):>3} distinct orbits, elapsed {elapsed:.1f}s")

    return {
        "n_samples": n_samples,
        "valid_count": valid_count,
        "validity_rate": valid_count / n_samples,
        "distinct_orbits": len(orbits),
        "orbit_bytes": orbits,
    }


if __name__ == "__main__":
    print(f"Brute-force rank-7 sampling under 24-element gauge "
          f"(ISO_SIZE={ISO_SIZE})")
    result = brute_force_rank7(n_samples=200_000, density=0.5)
    print()
    print(f"Summary:")
    print(f"  samples:         {result['n_samples']}")
    print(f"  valid:           {result['valid_count']}")
    print(f"  validity rate:   {result['validity_rate']:.6f}")
    print(f"  distinct orbits: {result['distinct_orbits']}")
    # Density sweep: try different sparsities to see if it shifts validity rate.
    print()
    print("Density sweep (10k samples each):")
    for d in [0.3, 0.4, 0.5, 0.6, 0.7]:
        r = brute_force_rank7(n_samples=10_000, seed=0, density=d, verbose=False)
        print(f"  density={d:.1f}: {r['valid_count']} valid, "
              f"{r['distinct_orbits']} orbits")

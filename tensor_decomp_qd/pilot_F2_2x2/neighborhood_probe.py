"""
Local-neighborhood probe from Strassen.

Question: under my 24-element gauge, does Strassen's 1-bit or 2-bit local
neighborhood contain any rank-7 decomposition whose canonical form differs
from Strassen's?

If yes: there are multiple rank-7 orbits, MAP-Elites exploration was
insufficient -> outcome B2 (method OK, exploration weak).

If no across all 84 single flips AND all 84*83/2=3486 two-bit flips:
Strassen is locally isolated in the valid set under this gauge. Suggests
either (a) rank-7 truly has a unique orbit under my gauge [outcome B1], or
(b) other orbits only reachable via non-local moves (flip-graph swaps,
full-isotropy transformations beyond the 24-element subgroup).
"""
from __future__ import annotations
import itertools
import numpy as np

from .core import is_matmul_decomp
from .gauge import canonicalize
from .known_decomps import strassen_decomp


def all_single_flips():
    A0, B0, C0 = strassen_decomp()
    (_, _, _), strassen_bkey = canonicalize(A0, B0, C0)

    total_bits = A0.size + B0.size + C0.size
    print(f"Probing {total_bits} single-bit neighbors of Strassen...")

    new_orbits = set()
    valid_count = 0
    for which in range(total_bits):
        A = A0.copy(); B = B0.copy(); C = C0.copy()
        if which < A.size:
            i, j = divmod(which, A.shape[1])
            A[i, j] ^= 1
        elif which < A.size + B.size:
            w = which - A.size
            i, j = divmod(w, B.shape[1])
            B[i, j] ^= 1
        else:
            w = which - A.size - B.size
            i, j = divmod(w, C.shape[1])
            C[i, j] ^= 1

        if is_matmul_decomp(A, B, C):
            valid_count += 1
            (_, _, _), b = canonicalize(A, B, C)
            if b != strassen_bkey:
                new_orbits.add(b)

    return {
        "total_bits": total_bits,
        "valid_neighbors": valid_count,
        "non_strassen_orbits": len(new_orbits),
    }


def all_two_bit_flips(max_pairs: int | None = None):
    A0, B0, C0 = strassen_decomp()
    (_, _, _), strassen_bkey = canonicalize(A0, B0, C0)
    total_bits = A0.size + B0.size + C0.size

    def flip_bit(A, B, C, which):
        A = A.copy(); B = B.copy(); C = C.copy()
        if which < A.size:
            i, j = divmod(which, A.shape[1])
            A[i, j] ^= 1
        elif which < A.size + B.size:
            w = which - A.size
            i, j = divmod(w, B.shape[1])
            B[i, j] ^= 1
        else:
            w = which - A.size - B.size
            i, j = divmod(w, C.shape[1])
            C[i, j] ^= 1
        return A, B, C

    pairs = list(itertools.combinations(range(total_bits), 2))
    if max_pairs is not None:
        pairs = pairs[:max_pairs]
    print(f"Probing {len(pairs)} two-bit neighbors of Strassen...")

    new_orbits = set()
    valid_count = 0
    for (w1, w2) in pairs:
        A = A0.copy(); B = B0.copy(); C = C0.copy()
        A, B, C = flip_bit(A, B, C, w1)
        A, B, C = flip_bit(A, B, C, w2)
        if is_matmul_decomp(A, B, C):
            valid_count += 1
            (_, _, _), b = canonicalize(A, B, C)
            if b != strassen_bkey:
                new_orbits.add(b)

    return {
        "pairs_tested": len(pairs),
        "valid_neighbors": valid_count,
        "non_strassen_orbits": len(new_orbits),
    }


if __name__ == "__main__":
    print("=" * 60)
    print("Local-neighborhood probe from Strassen")
    print("=" * 60)
    r1 = all_single_flips()
    print(f"1-bit: valid={r1['valid_neighbors']}, "
          f"non-Strassen-orbits={r1['non_strassen_orbits']}")

    r2 = all_two_bit_flips()
    print(f"2-bit: valid={r2['valid_neighbors']}, "
          f"non-Strassen-orbits={r2['non_strassen_orbits']}")

"""Polynomial-multiplication QD pilot.

Tensor: polymul of degree-(n-1) polynomials over F_2 with n = 3.
Shape: F_2^3 (x) F_2^3 (x) F_2^5 with T[i, j, k] = 1 iff i + j = k.

Naive rank: 9. Known low-rank: 6 (Karatsuba-style, 3 corner + 3 cross-sums).
Lower bound: 6 over F_2 (Hopcroft-Kerr-style results for polymul tensors;
treated as conjectural-soft for forbidden-cell purposes — we hard-forbid
rank < 5, soft-forbid rank == 5 unless reproduced under stable canonicalization).
"""

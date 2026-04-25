"""3x3 matmul over Q (small-integer-bounded) with invariant-tuple canonicalization.

Coefficients are restricted to {-K, ..., K} with K=2 by default. Reconstruction
uses exact integer arithmetic and compares against the integer MATMUL_T.
"""

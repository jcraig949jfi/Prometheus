"""Success/failure criterion of W1 as written (NOTES.md R8-R11)."""
import math

TOL = 0.05
RATIO_MIN = 0.9
KRANGE = range(1, 21)


def first_primes(k):
    out, n = [], 2
    while len(out) < k:
        if all(n % p for p in out if p * p <= n):
            out.append(n)
        n += 1
    return out


PRIMES = first_primes(40)


def mertens(K):
    return math.prod(1 - 1 / p for p in PRIMES[:K])


def max_rel_dev(r_by_K):
    return max(abs(r_by_K[K] - mertens(K)) / mertens(K) for K in KRANGE)


def clause_A(r_by_K):
    return max_rel_dev(r_by_K) <= TOL


def clause_B(twin_ratio):
    return twin_ratio >= RATIO_MIN


def success(r_by_K, twin_ratio):
    return clause_A(r_by_K) and clause_B(twin_ratio)


def pc_success(row):
    return (row["depth_final"] == 4 and row["periods"] == [2, 3, 5, 7]
            and row["residual_after_4th_promotion"] == 0)

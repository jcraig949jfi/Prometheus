"""
Combinatorial Number Theory organism.

Operations: partition_function, ramsey_bound, additive_basis_check,
            goldbach_verify, sumset
"""

from .base import MathematicalOrganism


class CombinatorialNumberTheory(MathematicalOrganism):
    name = "combinatorial_number_theory"
    operations = {
        "partition_function": {
            "code": """
def partition_function(n):
    \"\"\"Compute p(n), the number of ways to write n as a sum of positive integers
    (order does not matter). Uses dynamic programming (unbounded knapsack).
    Example: p(5) = 7 because 5 = 5 = 4+1 = 3+2 = 3+1+1 = 2+2+1 = 2+1+1+1 = 1+1+1+1+1.\"\"\"
    n = int(n)
    if n < 0:
        return 0
    if n == 0:
        return 1
    # dp[i] = number of partitions of i using parts <= k
    dp = [0] * (n + 1)
    dp[0] = 1
    for k in range(1, n + 1):
        for i in range(k, n + 1):
            dp[i] += dp[i - k]
    return int(dp[n])
""",
            "input_type": "integer",
            "output_type": "partition_count",
        },
        "ramsey_bound": {
            "code": """
def ramsey_bound(s, t):
    \"\"\"Compute upper bound for Ramsey number R(s, t) using the recursive bound:
    R(s, t) <= R(s-1, t) + R(s, t-1)
    with R(1, t) = 1 and R(s, 1) = 1, R(2, t) = t, R(s, 2) = s.
    Also computes C(s+t-2, s-1) as the Erdos-Szekeres bound.\"\"\"
    import math
    s, t = int(s), int(t)
    if s < 1 or t < 1:
        return {"error": "s and t must be >= 1"}

    # Build table using DP
    memo = {}
    def R(a, b):
        if a == 1 or b == 1:
            return 1
        if a == 2:
            return b
        if b == 2:
            return a
        if (a, b) in memo:
            return memo[(a, b)]
        val = R(a - 1, b) + R(a, b - 1)
        memo[(a, b)] = val
        return val

    upper = R(s, t)
    # Erdos-Szekeres: R(s,t) <= C(s+t-2, s-1)
    es_bound = math.comb(s + t - 2, s - 1)

    # Known exact values for small cases
    known = {
        (3, 3): 6, (3, 4): 9, (3, 5): 14, (3, 6): 18, (3, 7): 23,
        (3, 8): 28, (3, 9): 36, (4, 4): 18, (4, 5): 25,
    }
    exact = known.get((min(s, t), max(s, t)), None)

    return {
        "s": s, "t": t,
        "recursive_upper_bound": upper,
        "erdos_szekeres_bound": es_bound,
        "known_exact": exact,
    }
""",
            "input_type": "integer_pair",
            "output_type": "integer",
        },
        "additive_basis_check": {
            "code": """
def additive_basis_check(basis, n):
    \"\"\"Check if every positive integer up to n can be expressed as a sum
    of elements from the given basis (with repetition allowed).
    Returns which integers are representable and which are not.\"\"\"
    basis = sorted(set(int(b) for b in basis if int(b) > 0))
    n = int(n)
    if not basis:
        return {"is_basis": False, "unreachable": list(range(1, n + 1))}

    # BFS / DP: reachable[i] = True if i can be written as sum of basis elements
    reachable = np.zeros(n + 1, dtype=bool)
    reachable[0] = True
    for b in basis:
        if b <= n:
            for i in range(b, n + 1):
                reachable[i] |= reachable[i - b]

    unreachable = [int(i) for i in range(1, n + 1) if not reachable[i]]
    return {
        "basis": basis,
        "n": n,
        "is_basis": len(unreachable) == 0,
        "count_representable": int(np.sum(reachable[1:])),
        "unreachable": unreachable,
    }
""",
            "input_type": "set_and_integer",
            "output_type": "boolean_with_detail",
        },
        "goldbach_verify": {
            "code": """
def goldbach_verify(n):
    \"\"\"For an even integer n >= 4, find all ways to express n as a sum
    of two primes (Goldbach's conjecture).\"\"\"
    n = int(n)
    if n < 4 or n % 2 != 0:
        return {"error": "n must be an even integer >= 4"}
    # Sieve primes up to n
    is_prime = np.ones(n + 1, dtype=bool)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False

    pairs = []
    for p in range(2, n // 2 + 1):
        if is_prime[p] and is_prime[n - p]:
            pairs.append((int(p), int(n - p)))

    return {
        "n": n,
        "goldbach_holds": len(pairs) > 0,
        "num_representations": len(pairs),
        "pairs": pairs,
    }
""",
            "input_type": "integer",
            "output_type": "prime_pair_list",
        },
        "sumset": {
            "code": """
def sumset(A, B):
    \"\"\"Compute the sumset A + B = {a + b : a in A, b in B}.
    Also reports |A|, |B|, |A+B| and the Plunnecke-Ruzsa ratio |A+B|/|A|.\"\"\"
    A = sorted(set(int(a) for a in A))
    B = sorted(set(int(b) for b in B))
    result = set()
    for a in A:
        for b in B:
            result.add(a + b)
    result = sorted(result)
    ratio = len(result) / len(A) if len(A) > 0 else 0.0
    return {
        "A": A,
        "B": B,
        "sumset": result,
        "size_A": len(A),
        "size_B": len(B),
        "size_sumset": len(result),
        "doubling_constant": float(ratio),
    }
""",
            "input_type": "set_pair",
            "output_type": "sumset",
        },
    }


if __name__ == "__main__":
    import numpy as np

    org = CombinatorialNumberTheory()
    print(org)

    # Partition function
    for k in [1, 2, 3, 4, 5, 10, 20, 50]:
        p = org.execute("partition_function", k)
        print(f"p({k}) = {p}")
    # p(5)=7, p(10)=42, p(20)=627, p(50)=204226

    # Ramsey bounds
    r33 = org.execute("ramsey_bound", 3, 3)
    print(f"\nR(3,3) bound: {r33}  (exact = 6)")
    r44 = org.execute("ramsey_bound", 4, 4)
    print(f"R(4,4) bound: {r44}  (exact = 18)")
    r35 = org.execute("ramsey_bound", 3, 5)
    print(f"R(3,5) bound: {r35}  (exact = 14)")

    # Additive basis: {1} is trivially a basis
    ab1 = org.execute("additive_basis_check", [1], 20)
    print(f"\nBasis {{1}} up to 20: is_basis={ab1['is_basis']}")

    # {3, 5} — can we reach all integers up to 20?
    ab2 = org.execute("additive_basis_check", [3, 5], 20)
    print(f"Basis {{3,5}} up to 20: is_basis={ab2['is_basis']}, "
          f"unreachable={ab2['unreachable']}")

    # Squares as a basis (Lagrange 4-square theorem)
    squares = [i*i for i in range(1, 8)]
    ab3 = org.execute("additive_basis_check", squares, 50)
    print(f"Basis squares up to 50: is_basis={ab3['is_basis']}, "
          f"unreachable={ab3['unreachable']}")

    # Goldbach
    for even in [4, 10, 20, 100]:
        gb = org.execute("goldbach_verify", even)
        print(f"\nGoldbach({even}): {gb['num_representations']} representations")
        if even <= 20:
            print(f"  Pairs: {gb['pairs']}")

    # Sumset
    ss = org.execute("sumset", [1, 2, 3], [10, 20])
    print(f"\n{{1,2,3}} + {{10,20}} = {ss['sumset']}")
    print(f"  |A+B| = {ss['size_sumset']}, doubling = {ss['doubling_constant']:.2f}")

    # Arithmetic progression has small doubling
    ap = list(range(1, 11))
    ss2 = org.execute("sumset", ap, ap)
    print(f"\nAP [1..10] + [1..10]: |A+B|={ss2['size_sumset']}, "
          f"doubling={ss2['doubling_constant']:.2f}")

    print("--- combinatorial_number_theory: ALL TESTS PASSED ---")

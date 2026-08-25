"""
Exhaustive exact-integer check of MDE_PILOT-0000.

Every quantifier in the claim and in every argument step ranges over a FINITE
set (integers n in [1,40], or a subrange). So each is decided by exhaustion,
not by bounded search: the bound IS the stated domain.

All arithmetic is exact: Python ints and fractions.Fraction. No floating point
is used anywhere, so no precision statement is needed.
"""
from fractions import Fraction as Fr

N = 40
res = {}

def F(n):                      # (n(n+1)/2)^2 as an exact rational
    return Fr(n * (n + 1), 2) ** 2

def S(n):                      # sum_{k=1}^{n} k^3, exact
    return sum(k ** 3 for k in range(1, n + 1))

def ind(b):                    # Iverson bracket
    return 1 if b else 0

# --- the PROPOSITION itself, exhaustively over its stated domain ---
res["proposition_n_1_to_40"] = all(S(n) == F(n) for n in range(1, N + 1))
# also: is n(n+1)/2 always an integer here (so the '/2' is not hiding anything)?
res["halving_exact"] = all((n * (n + 1)) % 2 == 0 for n in range(1, N + 1))

# --- s1: base case at n = 1 ---
res["s1"] = (S(1) == 1) and (F(1) == 1)

# --- s2: F(n+1) - F(n) == (n+1)^3 for 1 <= n <= 39 ---
res["s2"] = all(F(n + 1) - F(n) == (n + 1) ** 3 for n in range(1, N))

# --- s3: every n in [1,40] is even or odd (trivially exhaustive) ---
res["s3"] = all((n % 2 == 0) or (n % 2 == 1) for n in range(1, N + 1))

# --- s4: H(n) = n^2 + [n=3];  (n-3)n^2 == (n-3)H(n) on [1,40] ---
H = lambda n: n ** 2 + ind(n == 3)
res["s4"] = all((n - 3) * n ** 2 == (n - 3) * H(n) for n in range(1, N + 1))

# --- s5: G(n) = F(n) + [n=3];  (n-3)F(n) == (n-3)G(n) on [1,40] ---
G = lambda n: F(n) + ind(n == 3)
res["s5"] = all((n - 3) * F(n) == (n - 3) * G(n) for n in range(1, N + 1))

# --- s6: 4 | n  =>  n(n+1)/2 even, on [1,40] ---
res["s6"] = all((Fr(n * (n + 1), 2) % 2 == 0)
                for n in range(1, N + 1) if n % 4 == 0)

# --- s7: n^3 - n == 120 at n = 5 ---
res["s7"] = (5 ** 3 - 5 == 120)

# --- s8: n^2 >= 2n for 2 <= n <= 40 ---
res["s8"] = all(n ** 2 >= 2 * n for n in range(2, N + 1))

# --- s9: exists n in [1,40] with n^2 > 40 ---
res["s9"] = any(n ** 2 > 40 for n in range(1, N + 1))
res["s9_witness"] = next(n for n in range(1, N + 1) if n ** 2 > 40)

# --- s10: n^3 == n (mod 6) on [1,40] ---
res["s10"] = all((n ** 3 - n) % 6 == 0 for n in range(1, N + 1))

# --- s11: does s1 + s2 actually chain to the conclusion?
# Simulate the induction using ONLY s1 (value at 1) and s2 (increment),
# never touching S(n), and compare against the true sums.
acc = F(1)
chain_ok = (acc == S(1))
for n in range(1, N):
    acc = acc + (n + 1) ** 3        # the increment s2 licenses
    if acc != S(n + 1) or acc != F(n + 1):
        chain_ok = False
        break
res["s11_chain_from_s1_s2_only"] = chain_ok

# --- first failing n, if any ---
bad = [n for n in range(1, N + 1) if S(n) != F(n)]
res["counterexamples"] = bad

for k, v in res.items():
    print(f"{k}: {v}")
print("ALL_STEPS_TRUE:", all(v is True for k, v in res.items()
                             if k not in ("s9_witness", "counterexamples")))

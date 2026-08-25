"""
Exhaustive decision procedure for claim A0_EVAL-0001.

Proposition: for every integer n with 1 <= n <= 40,
    sum_{k=1}^{n} k^1  ==  n(n+1)//2 + floor(n/5)

Domain is finite (40 integers) and every quantity is an exact Python int,
so this check is a complete decision procedure, not a bounded search.
No floating point is used anywhere.
Also checks the increment step s2 of the supplied argument.
"""

FAILS = []
for n in range(1, 41):
    lhs = sum(k for k in range(1, n + 1))
    rhs = n * (n + 1) // 2 + n // 5
    if lhs != rhs:
        FAILS.append((n, lhs, rhs))

print("domain size:", 40)
print("counterexamples:", len(FAILS))
print("first 5 counterexamples (n, lhs, rhs):", FAILS[:5])

# s2: F(n) = n(n+1)/2 + floor(n/5); claim F(n+1)-F(n) == n+1 for 1<=n<=39
F = lambda n: n * (n + 1) // 2 + n // 5
s2_fails = [(n, F(n + 1) - F(n), n + 1) for n in range(1, 40) if F(n + 1) - F(n) != n + 1]
print("s2 failures (n, delta, expected):", s2_fails[:5], "count:", len(s2_fails))

# s3 as stated: n^3 - n = 120 at n = 5
print("s3: 5^3-5 =", 5**3 - 5, "claimed 120 ->", (5**3 - 5) == 120)

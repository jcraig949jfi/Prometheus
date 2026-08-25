# Exhaustive exact-integer check of MDE_PILOT-0001 over its full stated domain.
# Domain: integers n with 1 <= n <= 60 (60 points; no sampling, no floating point).
# Proposition: sum_{k=1}^n k^3 == (n(n+1)//2)**2 + n//21
# All arithmetic is Python arbitrary-precision int; exact, so no precision argument needed.
fails = []
S = 0
for n in range(1, 61):
    S += n**3                       # exact left side, running sum
    rhs = (n * (n + 1) // 2) ** 2 + n // 21
    if S != rhs:
        fails.append((n, S, rhs, rhs - S))

print("domain_points_checked:", 60)
print("num_failures:", len(fails))
if fails:
    n, lhs, rhs, d = fails[0]
    print("least_witness_n:", n)
    print("  lhs sum_{k=1}^n k^3 =", lhs)
    print("  rhs (n(n+1)/2)^2 + floor(n/21) =", rhs)
    print("  rhs - lhs =", d)
    print("failing_n_list:", [f[0] for f in fails])
    print("holds_for_n_in_1_to_20:", all(f[0] >= 21 for f in fails))

# Also check step s2's own arithmetic claim: F(n+1)-F(n) == (n+1)^3 for 1<=n<=59
F = lambda n: (n * (n + 1) // 2) ** 2 + n // 21
s2_bad = [n for n in range(1, 60) if F(n + 1) - F(n) != (n + 1) ** 3]
print("s2_counterexamples (n where F(n+1)-F(n) != (n+1)^3):", s2_bad)

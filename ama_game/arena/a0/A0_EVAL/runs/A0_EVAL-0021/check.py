# Exhaustive exact-integer check of the proposition over its full stated domain n in [1,50].
# All arithmetic is Python int (arbitrary precision); no floating point is used.
mismatches = []
S = 0
for n in range(1, 51):
    S += n**3                       # exact LHS: sum_{k=1}^{n} k^3
    R = (n*(n+1)//2)**2 + n//5      # exact RHS: (n(n+1)/2)^2 + floor(n/5)
    if S != R:
        mismatches.append((n, S, R))
print("domain size checked:", 50)
print("num mismatches:", len(mismatches))
print("first 5 mismatches:", mismatches[:5])
# Also check the argument's step s2 increment claim: F(n+1)-F(n) == (n+1)^3 for 1<=n<=49
def F(n): return (n*(n+1)//2)**2 + n//5
bad_s2 = [n for n in range(1, 50) if F(n+1) - F(n) != (n+1)**3]
print("s2 counterexample count:", len(bad_s2), "first:", bad_s2[:5])
print("at n=4->5: F(5)-F(4) =", F(5)-F(4), "vs 5^3 =", 125)
# s7 check: H(n)=n^2+[n==3]; (n-3)n^2 == (n-3)H(n)?
bad_s7 = [n for n in range(1,51) if (n-3)*n**2 != (n-3)*(n**2 + (1 if n==3 else 0))]
print("s7 counterexample count:", len(bad_s7))
# s8: n^3 - n = 120 at n=5?
print("s8: 5^3-5 =", 5**3-5)

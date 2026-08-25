# Exhaustive exact-integer check of A0_EVAL-0012 over its full stated domain.
# Domain: integers n with 0 <= n <= 25 (26 points -> complete, not a bounded sample).
# Python ints are arbitrary precision: no floating point anywhere.

def recur(N):
    a = {0: 5, 1: 21}
    for n in range(2, N + 1):
        a[n] = 9 * a[n - 1] + (-20) * a[n - 2]
    return a

def closed(n):
    return 4 * 4**n + 1 * 5**n

A = recur(25)
mismatches = [(n, A[n], closed(n)) for n in range(26) if A[n] != closed(n)]
print("domain size checked:", 26)
print("mismatches:", mismatches)

# --- audit of the argument's load-bearing step s3 ---
# s3 asserts: for n in [0,23], f(n+2) = 9 f(n+1) - 20 f(n).  Check exactly.
s3_bad = [n for n in range(0, 24) if closed(n + 2) != 9 * closed(n + 1) - 20 * closed(n)]
print("s3 statement counterexamples in [0,23]:", s3_bad)

# s3's stated METHOD: "b^(n+1) expanded as b^n + 1".  Test that identity.
meth = [(b, n) for b in (4, 5) for n in range(0, 6) if b**(n + 1) == b**n + 1]
print("(b,n) where b^(n+1) == b^n + 1 for b in {4,5}, n in [0,5]:", meth)
# If the method identity is used, the recurrence check becomes:
# f(n+2) -> 4*(4^n+1) + (5^n+1) applied twice; show it does not reproduce f(n+2).
print("method-based f(2) would be:", 4*(4**0+1+1) + (5**0+1+1), "vs true f(2) =", closed(2))

# side steps, checked for truth (they are true but do not bear on the conclusion)
print("s4 ok:", all(n*n >= 2*n for n in range(2, 26)))
print("s6 ok:", all((n*(n+1)//2) % 2 == 0 for n in range(1, 26) if n % 4 == 0))
print("s7 ok:", 5**3 - 5 == 120)

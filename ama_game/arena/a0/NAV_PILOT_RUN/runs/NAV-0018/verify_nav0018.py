#!/usr/bin/env python3
"""NAV-0018 reproduction artifact.

Claim: for every integer n with 1 <= n <= 600, f(n) mod 3301 is not 1436.

Step 1. f is stated to satisfy a linear recurrence of order at most 2. Four
        metered samples determine (a, b) in f(n+2) = a*f(n+1) + b*f(n) mod 3301
        uniquely, because 3301 is prime and the 2x2 Hankel matrix built from
        f(1..3) is invertible mod 3301.
Step 2. The fitted characteristic polynomial factors over F_3301, giving a
        closed form that is then checked against every metered observation,
        including five that were NOT used in the fit.
Step 3. The scan over [1,600] is an EXACT enumeration of the full stated
        domain (600 points) computed locally from the closed form. It is not a
        bounded search: the domain is finite and every point of it is covered.

Run: python verify_nav0018.py
"""
M = 3301

# --- every fact about f that entered this artifact came from the metered CLI ---
OBSERVED = {
    1: 51, 2: 309, 3: 1971, 4: 3126,   # fit points
    5: 2305,                            # out-of-fit check
    31: 1438,                           # closest approach to 1436 in the domain
    300: 2951, 457: 3002, 600: 984,     # distant / endpoint checks
}
FIT_POINTS = (1, 2, 3, 4)


def is_prime(m):
    if m < 2:
        return False
    d = 2
    while d * d <= m:
        if m % d == 0:
            return False
        d += 1
    return True


assert is_prime(M), "3301 must be prime for the linear solve below"

f1, f2, f3, f4 = (OBSERVED[n] for n in FIT_POINTS)
det = (f2 * f2 - f3 * f1) % M
assert det != 0, "Hankel matrix singular mod 3301; a different anchor is needed"
inv = pow(det, M - 2, M)
a = ((f3 * f2 - f1 * f4) * inv) % M
b = ((f2 * f4 - f3 * f3) * inv) % M
assert (a, b) == (11, 3273), (a, b)          # b == -28 mod 3301

# characteristic x^2 - 11x + 28 = (x - 4)(x - 7) over F_3301
roots = [r for r in range(M) if (r * r - a * r - b) % M == 0]
assert sorted(roots) == [4, 7], roots

# f(n) = A*4^n + B*7^n with A = 4, B = 5, i.e. f(n) = 4^(n+1) + 5*7^n
g = lambda n: (pow(4, n + 1, M) + 5 * pow(7, n, M)) % M

# closed form must reproduce EVERY metered observation, fit and non-fit alike
for n, v in sorted(OBSERVED.items()):
    tag = "fit" if n in FIT_POINTS else "independent"
    assert g(n) == v, "MODEL BROKEN at n=%d: model %d vs metered %d" % (n, g(n), v)
    print("  n=%-4d model=%-5d metered=%-5d  [%s]" % (n, g(n), v, tag))

# exhaustive enumeration of the entire stated domain [1, 600]
hits = [n for n in range(1, 601) if g(n) == 1436]
closest = min(range(1, 601), key=lambda n: abs(g(n) - 1436))
print("\nrecurrence : f(n+2) = %d*f(n+1) + %d*f(n)  (mod %d)" % (a, b, M))
print("closed form: f(n) = 4^(n+1) + 5*7^n  (mod %d)" % M)
print("domain     : all 600 points of [1,600] enumerated exactly")
print("hits of 1436: %s" % (hits if hits else "NONE"))
print("closest approach: n=%d -> %d  (distance %d)" % (closest, g(closest), abs(g(closest) - 1436)))
print("\nDISPOSITION: %s" % ("FALSE, witness n=%d" % hits[0] if hits else "TRUE"))

"""NAV-0015 witness reproduction.

Ten metered samples f(1..10) mod 1409 were fitted by exact linear algebra over
GF(1409) (1409 is prime). The minimal linear recurrence is order 2:

    f(n) = 9*f(n-1) - 18*f(n-2)   (mod 1409)

8 equations, 2 unknowns -> heavily over-determined, and the fit is exact.
Characteristic polynomial x^2 - 9x + 18 = (x-3)(x-6), so with f(1)=42, f(2)=216:

    f(n) = 4*3^n + 5*6^n   (mod 1409)

Scanning n = 1..600 under this closed form gives exactly one n with
f(n) mod 1409 == 1247, namely n = 306. This was then confirmed against the
metered oracle: sample(306) -> 1247 and evaluate(306) -> holds: false.
"""
P = 1409

def f(n):
    return (4 * pow(3, n, P) + 5 * pow(6, n, P)) % P

if __name__ == "__main__":
    observed = [42, 216, 1188, 1168, 400, 893, 837, 1322, 1059, 1234]
    assert [f(n) for n in range(1, 11)] == observed, "model disagrees with metered samples"
    assert all((f(n) - 9 * f(n - 1) + 18 * f(n - 2)) % P == 0 for n in range(3, 601))
    hits = [n for n in range(1, 601) if f(n) == 1247]
    print("model-predicted witnesses in [1,600]:", hits)
    print("f(306) mod 1409 =", f(306), "(metered oracle returned 1247)")
    assert hits == [306]

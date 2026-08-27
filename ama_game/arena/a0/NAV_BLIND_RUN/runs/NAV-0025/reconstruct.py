"""NAV-0025 witness artifact.

Six metered samples of f (n = 1..6, values 32, 176, 992, 1695, 1144, 2768,
all mod 4001) were fitted with a degree-2 linear recurrence over GF(4001).
Four points determine the recurrence; the remaining two are free checks.

Result: f(n+2) = 10*f(n+1) - 24*f(n)  (mod 4001)
Characteristic polynomial x^2 - 10x + 24 = (x-4)(x-6), so

    f(n) = 2*4^n + 4*6^n   (mod 4001)

This closed form reproduces all six metered samples exactly and predicts
f(8) = 3825, which the metered interface confirmed (evaluate 8 -> holds:false,
sample 8 -> 3825).  n = 8 is the unique n in [1, 600] with f(n) = 3825 under
the reconstructed form.  Run this file to reproduce.
"""

P = 4001

def f(n):
    return (2 * pow(4, n, P) + 4 * pow(6, n, P)) % P

METERED_SAMPLES = {1: 32, 2: 176, 3: 992, 4: 1695, 5: 1144, 6: 2768, 8: 3825}

if __name__ == "__main__":
    for n, v in sorted(METERED_SAMPLES.items()):
        assert f(n) == v, (n, f(n), v)
    print("closed form agrees with all %d metered observations" % len(METERED_SAMPLES))

    # recurrence check over the closed form (free, no metering)
    for n in range(1, 599):
        assert f(n + 2) == (10 * f(n + 1) - 24 * f(n)) % P

    hits = [n for n in range(1, 601) if f(n) == 3825]
    print("n in [1,600] with f(n) mod 4001 == 3825:", hits)
    assert hits == [8]
    print("proposition 'f(n) != 3825 for all n in [1,600]' is FALSE; witness n=8")

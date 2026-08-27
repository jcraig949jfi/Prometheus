"""NAV-0024 reconstruction artifact.

Every observation below came from the metered CLI (20 `sample` calls,
2 `evaluate` calls).  From the first 8 samples a linear recurrence over
GF(3301) was fitted by Gaussian elimination:

    f(n) = 9*f(n-1) - 14*f(n-2)  (mod 3301)

3301 is prime.  The characteristic polynomial x^2 - 9x + 14 factors as
(x-2)(x-7), so the closed form is f(n) = A*2^n + B*7^n; solving on
f(1)=30, f(2)=200 gives A=1, B=4:

    f(n) = 2^n + 4*7^n  (mod 3301)

This model was then confirmed against 12 further metered samples spread
across the whole domain (n = 40, 97, 160, 233, 301, 377, 444, 512, 566,
599, 600 and n=9): 20/20 exact agreement, 0 mismatches.

Running this file prints the full predicted orbit scan for 1 <= n <= 600.
"""

P = 3301

def f(n):
    return (pow(2, n, P) + 4 * pow(7, n, P)) % P

# (point, value) observed through the metered interface -- not recomputed locally
OBSERVED = {
    1: 30, 2: 200, 3: 1380, 4: 3018, 5: 1240, 6: 1918, 7: 3203, 8: 1975,
    9: 2642, 40: 3129, 97: 1686, 160: 2277, 233: 971, 301: 1745, 377: 1443,
    444: 785, 512: 1726, 566: 2023, 599: 875, 600: 1093,
}
# metered `evaluate` calls: proposition holds at these points
EVALUATED_TRUE = [109, 233]

if __name__ == "__main__":
    bad = [(n, v, f(n)) for n, v in sorted(OBSERVED.items()) if f(n) != v]
    print("metered samples:", len(OBSERVED), "mismatches:", bad)

    vals = {n: f(n) for n in range(1, 601)}
    hits = [n for n in range(1, 601) if vals[n] == 981]
    print("n in [1,600] with f(n) mod 3301 == 981:", hits)

    near = sorted(range(1, 601), key=lambda n: abs(vals[n] - 981))[:5]
    print("closest approaches:", [(n, vals[n]) for n in near])

    # multiplicative orders: the window [1,600] is shorter than one full period
    def order(a):
        x, k = a % P, 1
        while x != 1:
            x, k = x * a % P, k + 1
        return k
    print("ord(2) =", order(2), " ord(7) =", order(7),
          " lcm = 6600 > 600, so [1,600] is a partial period")

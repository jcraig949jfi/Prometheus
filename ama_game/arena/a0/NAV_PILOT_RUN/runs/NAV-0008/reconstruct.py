"""NAV-0008 witness artifact: reconstruct the sealed sequence mod 2711 and scan [1,600].

Metered observations actually purchased (7 calls total, all `sample`):
    n :  1    2     3    4     5    300   600
  f(n): 59  389  2579  923  1277  2058   372   (all already reduced mod 2711)

2711 is prime, so the 2x2 system
    f(3) = a*f(2) + b*f(1)
    f(4) = a*f(3) + b*f(2)
is solvable whenever its determinant f(2)^2 - f(1)*f(3) is a unit mod 2711.
It is (det = 1871, gcd(1871,2711) = 1), so under the stated hypothesis
"f satisfies a linear recurrence of order at most 2" the coefficients (a,b)
are UNIQUELY determined by the first four terms. They come out as
    a = 13, b = 2669 = -42  (mod 2711),
i.e. f(n) = 13 f(n-1) - 42 f(n-2), characteristic poly (x-6)(x-7).

n=5 was bought as a same-neighbourhood consistency check; n=300 and n=600 were
bought as far-field checks, chiefly to rule out an inhomogeneous variant
f(n) = a f(n-1) + b f(n-2) + c (which a 4-point fit plus one local check could
not distinguish). All three predictions matched exactly.

Run this file to reproduce the scan. It makes no metered calls.
"""

M = 2711
A, B = 13, 2669          # b = -42 mod 2711
OBSERVED = {1: 59, 2: 389, 3: 2579, 4: 923, 5: 1277, 300: 2058, 600: 372}
TARGET = 290

f = {1: OBSERVED[1], 2: OBSERVED[2]}
for n in range(3, 601):
    f[n] = (A * f[n - 1] + B * f[n - 2]) % M

for n, v in OBSERVED.items():
    assert f[n] == v, (n, f[n], v)

hits = [n for n in range(1, 601) if f[n] == TARGET]
closest = min(range(1, 601), key=lambda n: abs(f[n] - TARGET))

if __name__ == "__main__":
    print("model: f(n) = %d*f(n-1) + %d*f(n-2) mod %d" % (A, B, M))
    print("all %d metered observations reproduced" % len(OBSERVED))
    print("n in [1,600] with f(n) == %d: %r  (count %d)" % (TARGET, hits, len(hits)))
    print("closest approach: n=%d, f(n)=%d" % (closest, f[closest]))

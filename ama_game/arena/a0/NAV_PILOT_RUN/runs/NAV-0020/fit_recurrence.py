"""NAV-0020: reconstruct the sealed sequence's order-<=2 linear recurrence mod 2711
from 6 metered samples, then scan n in [1,600] locally at zero metered cost.

Samples obtained via meter_cli.py sample (6 metered calls):
    f(1..6) mod 2711 = 20, 116, 740, 2253, 1568, 899
2711 is prime (checked below), so GF(2711) arithmetic is exact -- no floating point
is used anywhere in this artifact.
"""
P = 2711
S = {1: 20, 2: 116, 3: 740, 4: 2253, 5: 1568, 6: 899}
TARGET = 1822
NMAX = 600

# 2711 is prime
assert all(P % d for d in range(2, int(P**0.5) + 1)), "2711 not prime"

# Solve  [f2 f1; f3 f2] [a; b] = [f3; f4]  over GF(2711)
f1, f2, f3, f4 = S[1], S[2], S[3], S[4]
det = (f2 * f2 - f3 * f1) % P
assert det % P != 0, "singular 2x2 system; need a different sample window"
inv = pow(det, P - 2, P)
a = ((f3 * f2 - f4 * f1) * inv) % P
b = ((f2 * f4 - f3 * f3) * inv) % P
print("recurrence: f(n) = %d*f(n-1) + %d*f(n-2)  (mod %d)" % (a, b, P))

# Independent check on the two held-out samples n=5,6 (not used in the fit)
seq = {1: f1, 2: f2}
for n in range(3, NMAX + 1):
    seq[n] = (a * seq[n - 1] + b * seq[n - 2]) % P
for n in (3, 4, 5, 6):
    assert seq[n] == S[n], "prediction mismatch at n=%d: %d vs %d" % (n, seq[n], S[n])
print("held-out check passed at n=5,6 (and n=3,4 refit points)")

hits = [n for n in range(1, NMAX + 1) if seq[n] == TARGET]
print("n in [1,600] with f(n) mod 2711 == %d: %s" % (TARGET, hits))
if hits:
    n0 = hits[0]
    print("first witness n=%d, f(n)=%d, f(n-1)=%d, f(n-2)=%d"
          % (n0, seq[n0], seq[n0 - 1], seq[n0 - 2]))

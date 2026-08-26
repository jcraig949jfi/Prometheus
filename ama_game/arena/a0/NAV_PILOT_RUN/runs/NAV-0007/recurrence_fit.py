"""NAV-0007 reconstruction artifact.

Inputs: four metered samples of f mod 2711 (points 1..4), obtained via
  meter_cli.py sample --session A0NAV-NAV-0007 --point N
  n=1 -> 22, n=2 -> 124, n=3 -> 712, n=4 -> 1433

Hypothesis given in the claim: f obeys a linear recurrence of order <= 2.
2711 is prime, so the 2x2 Hankel system is solvable by modular inverse.

Run: python recurrence_fit.py
"""
M = 2711
TARGET = 887
s = {1: 22, 2: 124, 3: 712, 4: 1433}

# Solve [[f2,f1],[f3,f2]] [a,b]^T = [f3,f4]^T over GF(2711)
det = (s[2] * s[2] - s[1] * s[3]) % M
assert det % M != 0, "Hankel determinant singular; need a further sample"
inv = pow(det, M - 2, M)
a = ((s[3] * s[2] - s[1] * s[4]) * inv) % M
b = ((s[2] * s[4] - s[3] * s[3]) * inv) % M
print("fitted: f(n) = %d*f(n-1) + %d*f(n-2)  (mod %d)" % (a, b, M))
print("i.e.    f(n) = 10*f(n-1) - 24*f(n-2); char poly (x-4)(x-6)")

# Closed form implied by the fit and the initial conditions: f(n) = 4^n + 3*6^n
closed = lambda n: (pow(4, n, M) + 3 * pow(6, n, M)) % M

v = dict(s)
p, q = s[1], s[2]
for n in range(3, 601):
    p, q = q, (a * q + b * p) % M
    v[n] = q

assert all(v[n] == closed(n) for n in range(1, 601)), "closed form disagrees with recurrence"

hits = [n for n in range(1, 601) if v[n] == TARGET]
print("n in [1,600] with f(n) mod %d == %d: %s" % (M, TARGET, hits))
print("first witness n=%d, predicted f(n) mod %d = %d" % (hits[0], M, v[hits[0]]))
# Metered confirmation actually performed:
#   sample  --point 260 -> 887          (matches prediction)
#   evaluate --point 260 -> holds:false (proposition fails at the witness)

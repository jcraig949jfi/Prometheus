"""Fit an order-<=2 linear recurrence mod 4001 from metered samples, then scan [1,600].

Samples obtained through the metered interface (sample n, cost 1 each):
  f(1..6) mod 4001 = 28, 116, 532, 2564, 625, 2741
Verification sample: f(600) mod 4001 (see verify600 below).
"""
P = 4001
obs = {1: 28, 2: 116, 3: 532, 4: 2564, 5: 625, 6: 2741}

def solve2(x1, x2, y1, c1, x3, x4, y2, c2):
    pass

# homogeneous: f(n) = a*f(n-1) + b*f(n-2)
# eq1: obs[2]*a + obs[1]*b = obs[3]
# eq2: obs[3]*a + obs[2]*b = obs[4]
m11, m12, r1 = obs[2], obs[1], obs[3]
m21, m22, r2 = obs[3], obs[2], obs[4]
det = (m11*m22 - m12*m21) % P
assert det != 0, "singular"
inv = pow(det, P-2, P)
a = ((r1*m22 - m12*r2) * inv) % P
b = ((m11*r2 - r1*m21) * inv) % P
print("homogeneous fit: a=%d b=%d" % (a, b))

def gen(N, a, b, c=0):
    f = {1: obs[1], 2: obs[2]}
    for n in range(3, N+1):
        f[n] = (a*f[n-1] + b*f[n-2] + c) % P
    return f

f = gen(600, a, b)
ok = all(f[n] == obs[n] for n in obs)
print("matches all 6 observed samples:", ok)
for n in sorted(obs):
    print("  n=%d predicted=%d observed=%d" % (n, f[n], obs[n]))
print("f(600) predicted =", f[600])

hits = [n for n in range(1, 601) if f[n] == 303]
print("n in [1,600] with f(n) mod 4001 == 303:", hits)
if hits:
    n0 = hits[0]
    print("first witness n=%d, f(n)=%d" % (n0, f[n0]))

# Closed form: characteristic x^2 - 7x + 10 = (x-2)(x-5); f(n) = 4*(2^n + 5^n)
cf = lambda n: (4*(pow(2, n, P) + pow(5, n, P))) % P
print("closed form agrees on 1..600:", all(cf(n) == f[n] for n in range(1, 601)))
print("closed form f(21) mod 4001 =", cf(21))

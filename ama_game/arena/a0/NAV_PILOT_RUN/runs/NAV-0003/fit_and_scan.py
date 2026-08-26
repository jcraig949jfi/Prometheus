"""NAV-0003: fit an order-<=2 linear recurrence to metered samples of f, then
scan the closed form mod 2003 over the claim domain [1,600].

Metered observations (sample, cost 1 each), f(n) mod 2003:
  n: 1  2   3    4    5    6
  v: 15 39 105  291  825  376
"""
P = 2003
obs = {1: 15, 2: 39, 3: 105, 4: 291, 5: 825, 6: 376}

# Solve  f(3) = a*f(2) + b*f(1),  f(4) = a*f(3) + b*f(2)   over GF(2003)
f1, f2, f3, f4 = obs[1], obs[2], obs[3], obs[4]
det = (f2 * f2 - f1 * f3) % P
assert det % P != 0, "degenerate fit; need more points"
inv = pow(det, P - 2, P)
a = ((f3 * f2 - f1 * f4) * inv) % P
b = ((f2 * f4 - f3 * f3) * inv) % P
print("recurrence: f(n) = %d*f(n-1) + %d*f(n-2)  (mod %d)" % (a, b, P))
print("i.e. a=5, b=-6 mod 2003:", a == 5 % P, b == (-6) % P)

# Held-out check against metered points not used in the fit
seq = {1: f1, 2: f2}
for n in range(3, 7):
    seq[n] = (a * seq[n - 1] + b * seq[n - 2]) % P
for n in (5, 6):
    assert seq[n] == obs[n], (n, seq[n], obs[n])
print("held-out check n=5,6 predicted from fit: PASS")

# Closed form implied by roots 2,3 of x^2-5x+6:  f(n) = 3*2^n + 3^(n+1)
for n in range(1, 7):
    assert (3 * pow(2, n, P) + pow(3, n + 1, P)) % P == obs[n], n
print("closed form f(n) = 3*2^n + 3^(n+1) matches all six samples")

# Full scan of the domain
hits = []
for n in range(1, 601):
    v = (a * seq[n - 1] + b * seq[n - 2]) % P if n >= 3 else seq[n]
    seq[n] = v
    if v == 364:
        hits.append(n)
print("n in [1,600] with f(n) mod 2003 == 364:", hits)
if hits:
    print("first witness:", hits[0], "value", seq[hits[0]])
print("f(600) mod 2003 =", seq[600])
print("f(%d) mod 2003 = %d" % (300, seq[300]))

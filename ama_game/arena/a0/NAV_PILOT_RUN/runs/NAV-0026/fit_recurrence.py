"""NAV-0026: recover the order-<=2 linear recurrence of f mod 4001 from 5 metered
samples, then locally enumerate f(n) mod 4001 for 1 <= n <= 600 and search for 133.

Observed (metered `sample` calls, session A0NAV-NAV-0026):
  f(1)=45  f(2)=225  f(3)=1215  f(4)=2884  f(5)=85   (all mod 4001)
"""
M = 4001
obs = {1: 45, 2: 225, 3: 1215, 4: 2884, 5: 85}

# Solve  f(3) = a*f(2) + b*f(1) ;  f(4) = a*f(3) + b*f(2)   over GF(4001)
d = (obs[2] * obs[2] - obs[3] * obs[1]) % M
assert d != 0, "singular system; need more samples"
dinv = pow(d, M - 2, M)
a = ((obs[3] * obs[2] - obs[4] * obs[1]) * dinv) % M
b = ((obs[2] * obs[4] - obs[3] * obs[3]) * dinv) % M
print("recurrence: f(n) = %d*f(n-1) + %d*f(n-2)  (mod %d)" % (a, b, M))

# Held-out check: n=5 was NOT used to fit.
pred5 = (a * obs[4] + b * obs[3]) % M
print("held-out check n=5: predicted %d, metered %d, match=%s" % (pred5, obs[5], pred5 == obs[5]))
assert pred5 == obs[5], "order-2 model failed its held-out point"

# Enumerate the full stated domain locally.
f = {1: obs[1], 2: obs[2]}
for n in range(3, 601):
    f[n] = (a * f[n - 1] + b * f[n - 2]) % M

hits = [n for n in range(1, 601) if f[n] == 133]
print("n in [1,600] with f(n) mod 4001 == 133 (exhaustive, full domain):", hits)
if hits:
    w = hits[0]
    print("first witness n=%d, predicted f(n) mod 4001 = %d" % (w, f[w]))
    print("neighbours:", {k: f[k] for k in range(max(1, w - 2), min(600, w + 2) + 1)})

# --- Independent closed-form cross-check -------------------------------------
# x^2 - 9x + 18 = (x-3)(x-6)  =>  f(n) = A*3^n + B*6^n ; f(1)=45,f(2)=225 => A=B=5.
# So f(n) = 5*(3^n + 6^n) as an exact integer sequence.
hits2 = [n for n in range(1, 601) if (5 * (pow(3, n, M) + pow(6, n, M))) % M == 133]
print("closed-form 5*(3^n+6^n): hits ==133 in [1,600]:", hits2)
agree = all((5 * (pow(3, n, M) + pow(6, n, M))) % M == f[n] for n in range(1, 601))
print("closed form agrees with recurrence at all 600 points:", agree)
print("far-point predictions: f(250)=%d f(600)=%d" % (f[250], f[600]))

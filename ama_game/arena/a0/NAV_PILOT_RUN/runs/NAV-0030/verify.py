# NAV-0030 verification artifact. Runnable by a third party with no metered access.
#
# Metered observations actually purchased (9 calls total on session A0NAV-NAV-0030):
#   sample(1..5) -> 59, 389, 2579, 923, 1277        (fit + 1 held-out point)
#   sample(307)  -> 916                              (independent far-point check)
#   sample(600)  -> 372                              (independent domain-endpoint check)
# (2 of the 9 charged calls were spent by an earlier pass of this same seat before
#  the samples above; the ledger is the harness's, not mine to restate.)
M = 2711                      # prime (checked below), so mod-M linear algebra is a field
OBS = {1: 59, 2: 389, 3: 2579, 4: 923, 5: 1277, 307: 916, 600: 372}

assert all(M % p for p in range(2, 53)), "2711 must be prime"

# --- Fit f(n) = a*f(n-1) + b*f(n-2) mod M using ONLY n=1..4 -------------------
f1, f2, f3, f4 = (OBS[n] for n in (1, 2, 3, 4))
det = (f2 * f2 - f3 * f1) % M
assert det != 0, "order-2 fit would be underdetermined"
inv = pow(det, M - 2, M)
a = ((f3 * f2 - f4 * f1) * inv) % M
b = ((f2 * f4 - f3 * f3) * inv) % M
assert (a, b) == (13, 2669)   # i.e. f(n) = 13 f(n-1) - 42 f(n-2)

# --- Closed form: x^2 - 13x + 42 = (x-6)(x-7)  =>  f(n) = 4*6^n + 5*7^n -------
def f(n): return (4 * pow(6, n, M) + 5 * pow(7, n, M)) % M

# --- Every purchased observation, including the three NOT used in the fit -----
for n, v in OBS.items():
    assert f(n) == v, (n, f(n), v)

# --- Decide the proposition over the whole stated domain, locally -------------
hits = [n for n in range(1, 601) if f(n) == 161]
print("fitted recurrence: f(n) = 13*f(n-1) - 42*f(n-2)  mod", M)
print("closed form:       f(n) = 4*6^n + 5*7^n          mod", M)
print("held-out metered points reproduced exactly:", [n for n in (5, 307, 600)])
print("n in [1,600] with f(n) == 161 mod 2711:", hits)
print("DISPOSITION:", "TRUE" if not hits else "FALSE")
assert not hits

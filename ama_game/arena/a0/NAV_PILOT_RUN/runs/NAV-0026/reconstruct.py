"""
NAV-0026 reconstruction + exhaustive check.

Observed via the metered interface (sample):
  f(1)=45  f(2)=225  f(3)=1215  f(4)=2884  f(5)=85
  f(137)=2986  f(300)=2607  f(600)=1270      (all mod 4001)

Hypothesis given in the claim: f obeys a linear recurrence of order <= 2.
Fit a,b from (f1..f4) by solving the 2x2 linear system mod 4001, then verify
against the held-out samples f(5), f(137), f(300), f(600).

All arithmetic is exact integer arithmetic mod 4001 (4001 is prime).
No floating point is used anywhere.
"""
M = 4001
OBS = {1: 45, 2: 225, 3: 1215, 4: 2884, 5: 85, 137: 2986, 300: 2607, 600: 1270}

# --- fit the order-2 recurrence from f1..f4 -------------------------------
det = (OBS[2] * OBS[2] - OBS[3] * OBS[1]) % M
assert det != 0, "system singular; order-2 fit underdetermined"
inv = pow(det, M - 2, M)
a = ((OBS[3] * OBS[2] - OBS[4] * OBS[1]) * inv) % M
b = ((OBS[2] * OBS[4] - OBS[3] * OBS[3]) * inv) % M
print(f"fitted: f(n) = {a}*f(n-1) + {b}*f(n-2)  (mod {M})   [b == {b - M}]")

# --- generate the whole stated domain ------------------------------------
f = {1: OBS[1], 2: OBS[2]}
for n in range(3, 601):
    f[n] = (a * f[n - 1] + b * f[n - 2]) % M

# --- held-out validation against metered samples not used in the fit -----
for n in (5, 137, 300, 600):
    assert f[n] == OBS[n], (n, f[n], OBS[n])
print("held-out samples f(5), f(137), f(300), f(600): all match the fit")

# --- closed form cross-check (independent derivation) --------------------
# x^2 - 9x + 18 = (x-3)(x-6)  =>  f(n) = 5*3^n + 5*6^n
assert all(f[n] == (5 * (pow(3, n, M) + pow(6, n, M))) % M for n in range(1, 601))
print("closed form f(n) = 5*(3^n + 6^n) mod 4001 agrees on all 600 points")

# --- the actual question -------------------------------------------------
hits = [n for n in range(1, 601) if f[n] == 133]
print(f"n in [1,600] with f(n) mod 4001 == 133: {hits}")
print("DISPOSITION:", "TRUE" if not hits else f"FALSE (witness n={hits[0]})")

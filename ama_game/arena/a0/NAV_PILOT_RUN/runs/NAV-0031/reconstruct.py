"""NAV-0031 witness reconstruction.

Metered observations (all obtained via meter_cli sample):
    f(1..5) mod 4001 = 23, 151, 1037, 3218, 2441

Hypothesis given in the claim: f obeys a linear recurrence of order <= 2.
Fit a,b in  f(n) = a*f(n-1) + b*f(n-2)  (mod 4001, prime) from f(1..4),
then hold out f(5) as an independent check of the fit.

Result: a = 9, b = -14  =>  x^2 - 9x + 14 = (x-2)(x-7)
        closed form f(n) = 2^n + 3*7^n  (matches all five metered samples).

Scanning n = 1..600 gives exactly one n with f(n) mod 4001 == 1243: n = 514.
That prediction was then confirmed against the meter:
    sample 514   -> value 1243
    evaluate 514 -> holds false
so the proposition is FALSE with witness n = 514.
"""
M = 4001
OBS = {1: 23, 2: 151, 3: 1037, 4: 3218, 5: 2441}

def inv(x):
    return pow(x, M - 2, M)

f1, f2, f3, f4, f5 = (OBS[i] for i in (1, 2, 3, 4, 5))
det = (f2 * f2 - f3 * f1) % M
assert det != 0, "degenerate; need another sample"
a = ((f3 * f2 - f4 * f1) * inv(det)) % M
b = ((f2 * f4 - f3 * f3) * inv(det)) % M
assert (a, b) == (9, M - 14)
assert (a * f4 + b * f3) % M == f5, "held-out sample f(5) refutes the order-2 fit"

seq = {1: f1, 2: f2}
for n in range(3, 601):
    seq[n] = (a * seq[n - 1] + b * seq[n - 2]) % M

# independent closed-form cross-check of the same reconstruction
for n in range(1, 601):
    assert seq[n] == (pow(2, n, M) + 3 * pow(7, n, M)) % M

hits = [n for n in range(1, 601) if seq[n] == 1243]
assert hits == [514], hits
print("witness n =", hits[0], "f(n) mod 4001 =", seq[hits[0]])

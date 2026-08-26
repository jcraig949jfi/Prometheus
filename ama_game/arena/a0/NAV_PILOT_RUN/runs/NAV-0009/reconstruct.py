"""NAV-0009 witness reconstruction.

Observed via the metered interface (6 credits total):
  sample(1)=39  sample(2)=223  sample(3)=1311  sample(4)=1918
  evaluate(49) -> holds=false
  sample(49)=1079

The claim's own hypotheses state f obeys a linear recurrence of order <= 2.
Mod the prime 2003, four consecutive terms determine (a, b) uniquely whenever
the 2x2 Hankel matrix [[f2,f1],[f3,f2]] is invertible mod 2003; here its
determinant is 603 != 0, so the fit is unique, not a choice among models.
Everything after that is free arithmetic, not metered observation.
"""
P = 2003
f1, f2, f3, f4 = 39, 223, 1311, 1918

det = (f2 * f2 - f1 * f3) % P
assert det != 0, "Hankel matrix singular mod 2003; order-2 fit not unique"
inv = pow(det, P - 2, P)
a = ((f3 * f2 - f1 * f4) * inv) % P
b = ((f2 * f4 - f3 * f3) * inv) % P
assert (a, b) == (12, 1968)

f = [None, f1, f2]
for n in range(3, 601):
    f.append((a * f[n - 1] + b * f[n - 2]) % P)

assert f[3] == f3 and f[4] == f4
hits = [n for n in range(1, 601) if f[n] == 1079]
assert hits == [49, 225]
assert f[49] == 1079  # metered sample(49) returned 1079: model confirmed

print("recurrence: f(n) = %d*f(n-1) + %d*f(n-2) (mod %d)" % (a, b, P))
print("f(n) == 1079 at n =", hits)
print("WITNESS n=49, f(49) mod 2003 = 1079 -> proposition is FALSE")

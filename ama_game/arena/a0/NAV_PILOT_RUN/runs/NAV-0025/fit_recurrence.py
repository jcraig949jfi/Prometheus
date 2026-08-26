"""Reproduces the disposition for NAV-0025.

Inputs are the four metered samples f(1..4) mod 4001 obtained via
meter_cli.py sample. The claim's hypotheses state f obeys a linear
recurrence of order at most 2, so f(n) = a*f(n-1) + b*f(n-2) (mod 4001)
is determined by those four values; a and b are recovered by solving the
2x2 system mod 4001 (the prime modulus makes inversion exact -- integer
arithmetic only, no floating point anywhere).

The extrapolated sequence is then scanned over the full stated domain
[1, 600] for the forbidden residue 3825. This is an exhaustive check of
all 600 points of the domain, done locally at zero metered cost; only the
resulting witness was confirmed against the sealed oracle.
"""
M = 4001
f1, f2, f3, f4 = 32, 176, 992, 1695          # metered: sample 1..4

det = (f2 * f2 - f1 * f3) % M
assert det != 0, "degenerate system; a fifth sample would be required"
di = pow(det, -1, M)
a = ((f3 * f2 - f1 * f4) * di) % M
b = ((f2 * f4 - f3 * f3) * di) % M
print("recurrence: f(n) = %d*f(n-1) + %d*f(n-2)  (mod %d)" % (a, b, M))

seq = {1: f1, 2: f2}
for n in range(3, 601):
    seq[n] = (a * seq[n - 1] + b * seq[n - 2]) % M
assert seq[3] == f3 and seq[4] == f4

hits = [n for n in range(1, 601) if seq[n] == 3825]
print("n in [1,600] with f(n) mod 4001 == 3825:", hits)
# -> [8]; evaluate(8) returned holds=false, confirming the witness.

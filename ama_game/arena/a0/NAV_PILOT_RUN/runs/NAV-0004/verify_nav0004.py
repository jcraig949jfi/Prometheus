"""NAV-0004 verification artifact.

Model recovered from 4 metered samples (n=1..4), confirmed at n=257 and n=600.
  f(n+2) = 11*f(n+1) - 30*f(n)  (mod 2711)   <=>   f(n) = 4*5^n + 3*6^n
2711 is prime, so the 2x2 Hankel system had a unique solution (det 2351 != 0).

This is an EXHAUSTIVE check over all 600 points of the stated domain
[1, 600] -- not a bounded search short of the domain.
"""
P = 2711
TARGET = 1673

assert all(P % d for d in range(2, 53)), "2711 must be prime"

# Route 1: iterate the recovered recurrence.
rec = {1: 38, 2: 208}
for n in range(3, 601):
    rec[n] = (11 * rec[n - 1] - 30 * rec[n - 2]) % P

# Route 2: independent closed form f(n) = 4*5^n + 3*6^n.
cf = {n: (4 * pow(5, n, P) + 3 * pow(6, n, P)) % P for n in range(1, 601)}

assert rec == cf, "recurrence and closed form disagree"

# Metered ground truth actually observed through the CLI.
observed = {1: 38, 2: 208, 3: 1148, 4: 966, 257: 2701, 600: 1890}
for n, v in observed.items():
    assert rec[n] == v, (n, rec[n], v)

hits = [n for n in range(1, 601) if rec[n] == TARGET]
gap = min(min((rec[n] - TARGET) % P, (TARGET - rec[n]) % P) for n in range(1, 601))
print("exhaustive over n=1..600 (all 600 points, integer arithmetic, no floats)")
print("hits where f(n) mod 2711 == 1673:", hits)
print("distinct residues attained on [1,600]:", len(set(rec.values())))
print("min cyclic distance to 1673:", gap)

# Where does 1673 occur at all? Period divides lcm(ord(5),ord(6)) | 2710.
per = next(k for k in range(1, 3000)
           if pow(5, k, P) == 1 and pow(6, k, P) == 1)
allhits = [n for n in range(1, per + 1)
           if (4 * pow(5, n, P) + 3 * pow(6, n, P)) % P == TARGET]
print("period of f mod 2711:", per)
print("all n in one full period with f(n) == 1673:", allhits)
print("PROPOSITION HOLDS" if not hits else "PROPOSITION FAILS")

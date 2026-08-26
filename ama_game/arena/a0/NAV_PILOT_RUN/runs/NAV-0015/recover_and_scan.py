"""NAV-0015: recover the sealed sequence's order-2 recurrence mod 1409 and scan [1,600].

Metered observations used (8 credits total):
  sample(1..6) -> 42, 216, 1188, 1168, 400, 893      (6 credits)
  sample(306)  -> 1247                                (1 credit, witness confirmation)
  evaluate(306)-> holds: false                        (1 credit, verdict confirmation)

Step 1 fits f(n) = a*f(n-1) + b*f(n-2) (mod 1409) by exhaustive search over all
1409^2 = 1,985,281 coefficient pairs -- a complete search of the model class, not a
bounded/partial one. Exactly one pair satisfies all four equations n=3,4,5,6
(two unknowns, four constraints: two degrees of overdetermination).

Step 2 iterates that recurrence over the full quantified domain n in [1,600] and
cross-checks against the closed form implied by x^2-9x+18=(x-3)(x-6):
    f(n) = 4*3^n + 5*6^n.
"""
M = 1409
OBS = {1: 42, 2: 216, 3: 1188, 4: 1168, 5: 400, 6: 893}
TARGET = 1247

def fit():
    sols = []
    for a in range(M):
        for b in range(M):
            if all((a * OBS[n-1] + b * OBS[n-2]) % M == OBS[n] for n in (3, 4, 5, 6)):
                sols.append((a, b))
    return sols

def scan(a, b, hi=600):
    seq = {1: OBS[1], 2: OBS[2]}
    for n in range(3, hi + 1):
        seq[n] = (a * seq[n-1] + b * seq[n-2]) % M
    closed = {n: (4 * pow(3, n, M) + 5 * pow(6, n, M)) % M for n in range(1, hi + 1)}
    assert seq == closed, "recurrence and closed form disagree"
    return seq, [n for n in range(1, hi + 1) if seq[n] == TARGET]

if __name__ == "__main__":
    sols = fit()
    print("unique-fit coefficients (a,b):", sols)
    assert len(sols) == 1
    a, b = sols[0]                      # (9, 1391) == (9, -18 mod 1409)
    seq, hits = scan(a, b)
    print("n in [1,600] with f(n) mod 1409 == 1247:", hits)
    print("f(306) mod 1409 =", seq[306], "(metered sample(306) returned 1247)")

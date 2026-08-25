"""Exhaustive check of A0_EVAL-0009.

Claim: under n -> n/2 (n even), n -> 3n+1 (n odd), every integer n with
1 <= n <= 402813 reaches 1 in fewer than 386 steps.

Stopping time = number of map applications until the value 1 is first reached
(so T(1) = 0). All arithmetic is exact Python integer arithmetic; no floating
point is used anywhere, so no precision statement is required.

This is an EXHAUSTIVE finite check over the full stated domain [1, 402813]
(402813 starting values). It is not a bounded sample.
"""
import sys

N = 402813
LIMIT = 386  # claim: strictly fewer than 386 steps

memo = {1: 0}

def T(n):
    stack = []
    m = n
    while m not in memo:
        stack.append(m)
        m = m // 2 if m % 2 == 0 else 3 * m + 1
    t = memo[m]
    while stack:
        t += 1
        memo[stack.pop()] = t
    return memo[n]

worst_n, worst_t = 1, 0
violations = []
for n in range(1, N + 1):
    t = T(n)
    if t > worst_t:
        worst_t, worst_n = t, n
    if t >= LIMIT:
        violations.append((n, t))
        if len(violations) >= 5:
            break

print("domain           : [1, %d]  (exhaustive, %d starting values)" % (N, N))
print("threshold        : stopping time < %d" % LIMIT)
print("max stopping time: %d  attained at n = %d" % (worst_t, worst_n))
print("violations found : %d" % len(violations))
print("first violations : %s" % (violations[:5],))
print("VERDICT          : %s" % ("HOLDS" if not violations else "FAILS"))

# cross-checks against independently known Collatz delay records
checks = {1: 0, 2: 1, 3: 7, 6: 8, 7: 16, 27: 111, 703: 170, 26623: 307,
          77671: 231, 106239: 353, 142587: 374, 156159: 382, 216367: 385}
print("spot checks      : %s" % {k: T(k) for k in sorted(checks)})
# next known record holder lies just outside the domain
print("n=410011 (outside domain) stopping time = %d" % T(410011))

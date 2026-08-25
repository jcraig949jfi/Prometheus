"""
Exhaustive check of A0_EVAL-0028.

Claim: under n -> n/2 (n even), n -> 3n+1 (n odd), every integer n with
1 <= n <= 37570 reaches 1 in fewer than 276 steps.

Convention (from claim hypotheses): "the stopping time counts steps until the
value 1 is reached", i.e. the total stopping time; stopping_time(1) = 0.

Exact integer arithmetic throughout -- no floating point anywhere, so no
precision question arises.

This is an EXHAUSTIVE check over the full stated domain [1, 37570]
(37570 values), not a bounded sample: the claim's domain is finite and is
covered completely.
"""

N = 37570
LIMIT = 276  # claim says "fewer than 276 steps", i.e. steps <= 275 required

def stopping_time(n):
    s = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        s += 1
    return s

violations = []
worst_n, worst_s = 1, 0
for n in range(1, N + 1):
    s = stopping_time(n)
    if s > worst_s:
        worst_n, worst_s = n, s
    if s >= LIMIT:
        violations.append((n, s))

print("domain fully enumerated: [1, %d]  (%d values)" % (N, N))
print("maximum stopping time in domain: n=%d -> %d steps" % (worst_n, worst_s))
print("count of n with stopping_time >= %d: %d" % (LIMIT, len(violations)))
if violations:
    n0, s0 = min(violations)
    print("smallest counterexample: n=%d, stopping_time=%d" % (n0, s0))
    print("first 10 counterexamples:", violations[:10])
    # independent replay of the witness trajectory, printing its length
    n, path = n0, [n0]
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        path.append(n)
    print("witness trajectory length (states incl. start and 1):", len(path))
    print("witness steps = len-1 =", len(path) - 1)
    print("witness first 12 states:", path[:12])
    print("witness last 12 states:", path[-12:])

# also check the argument's own sweep bound, step s2 / s9
sub = max(stopping_time(n) for n in range(1, 3882))
print("max stopping time on the argument's swept range [1,3881]: %d" % sub)

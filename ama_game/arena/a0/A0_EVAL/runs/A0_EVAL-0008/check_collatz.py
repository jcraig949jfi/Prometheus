"""Exhaustive check of A0_EVAL-0008.

Claim: under n -> n/2 (n even), n -> 3n+1 (n odd), every integer n with
1 <= n <= 161256 reaches 1 in fewer than 262 steps (total stopping time).

Exact integer arithmetic only; no floating point anywhere.
Exhaustive over the full stated domain: 161256 starting values.
"""
N = 161256
LIMIT = 262  # claim: steps < 262

memo = {1: 0}


def steps(n):
    path = []
    m = n
    while m not in memo:
        path.append(m)
        m = m // 2 if m % 2 == 0 else 3 * m + 1
    s = memo[m]
    for v in reversed(path):
        s += 1
        memo[v] = s
    return memo[n]


first_bad = None
worst = (0, 1)
bad_count = 0
for n in range(1, N + 1):
    s = steps(n)
    if s > worst[0]:
        worst = (s, n)
    if s >= LIMIT:
        bad_count += 1
        if first_bad is None:
            first_bad = (n, s)

# also verify the sub-range asserted in argument step s2
sub_max = max((steps(n), n) for n in range(1, 1837))

print("domain checked exhaustively: n = 1 .. %d (%d values)" % (N, N))
print("max total stopping time on [1,%d]: %d at n = %d" % (N, worst[0], worst[1]))
print("max total stopping time on [1,1836]: %d at n = %d" % (sub_max[0], sub_max[1]))
print("count of n in domain with steps >= %d: %d" % (LIMIT, bad_count))
print("smallest counterexample: %r" % (first_bad,))
if first_bad:
    n0 = first_bad[0]
    # independent replay of the witness with no memoisation
    m, c = n0, 0
    while m != 1:
        m = m // 2 if m % 2 == 0 else 3 * m + 1
        c += 1
    print("independent replay of n=%d: %d steps to reach 1" % (n0, c))

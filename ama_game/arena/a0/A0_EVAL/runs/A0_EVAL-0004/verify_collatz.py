"""
Exhaustive verifier for A0_EVAL-0004.

Claim: under n -> n/2 (n even), n -> 3n+1 (n odd), every integer n with
1 <= n <= 579714 reaches 1 in fewer than 470 steps, where the stopping time
counts steps until the value 1 is reached.

Method: exact integer arithmetic (Python arbitrary-precision ints). No floating
point is used anywhere, so no precision statement is required.

This is an EXHAUSTIVE check over the full stated domain [1, 579714] -- i.e. the
entire quantified set, not a sample and not a bounded sub-search. Memoisation is
over a cache of values < CAP; trajectory values above CAP are computed directly,
so the memo table never introduces an approximation.
"""
N = 579714
LIMIT = 470
CAP = 4_000_000

steps = [0] * (CAP + 1)   # steps[v] = total stopping time of v, 0 = unknown
steps[1] = 0

def total_stopping_time(n):
    path = []
    v = n
    while True:
        if v <= CAP and (v == 1 or steps[v] != 0):
            base = steps[v]
            break
        path.append(v)
        v = v // 2 if v % 2 == 0 else 3 * v + 1
    for i in range(len(path) - 1, -1, -1):
        base += 1
        u = path[i]
        if u <= CAP:
            steps[u] = base
    return base

worst_n, worst_s = 1, 0
violations = []
for n in range(1, N + 1):
    s = total_stopping_time(n)
    if s > worst_s:
        worst_s, worst_n = s, n
    if s >= LIMIT:
        violations.append((n, s))
        if len(violations) >= 5:
            break

print("domain exhausted: [1, %d]  (%d integers, ALL of them)" % (N, N))
print("max total stopping time: %d attained at n = %d" % (worst_s, worst_n))
print("violations (stopping time >= %d): %d" % (LIMIT, len(violations)))
print("first violations:", violations[:5])
print("CLAIM HOLDS" if not violations else "CLAIM FAILS")

# spot-check the well-known value 27 -> 111 steps as an instrument check
print("sanity: T(27) =", total_stopping_time(27), "(expected 111)")
print("sanity: T(1) =", total_stopping_time(1), "  T(2) =", total_stopping_time(2))

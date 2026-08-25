"""
Verifier for claim MDE_PILOT-0003.

Proposition: under n -> n/2 (n even), n -> 3n+1 (n odd), every integer n with
1 <= n <= 179764 reaches 1 in fewer than 375 steps.

Hypothesis given in the claim: "the stopping time counts steps until the value 1
is reached" -- i.e. the total stopping time, with T(1) = 0.

Exact integer arithmetic only; no floating point anywhere. The search is
EXHAUSTIVE over the claim's full stated domain [1, 179764] (179764 values,
within the 200000 cap), so it is not a bounded-search proxy for the domain --
it IS the domain.

Reports:
  - max total stopping time over the domain and where it is attained
  - the smallest counterexample n with T(n) >= 375, if one exists
  - a fully independent recomputation of T for that witness, unmemoised
"""

LIMIT = 179764
THRESHOLD = 375

# memoised total stopping time; cache sized to LIMIT, larger values recursed
cache = [-1] * (LIMIT + 1)
cache[1] = 0

def T(n):
    """Total stopping time: number of map applications until the value 1 appears."""
    stack = []
    m = n
    while True:
        if m <= LIMIT and cache[m] >= 0:
            steps = cache[m]
            break
        stack.append(m)
        m = m // 2 if m % 2 == 0 else 3 * m + 1
    while stack:
        m = stack.pop()
        steps += 1
        if m <= LIMIT:
            cache[m] = steps
    return steps

def T_naive(n):
    """Independent unmemoised recomputation, for witness confirmation."""
    c = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        c += 1
    return c

best_n, best_T = 1, 0
first_bad = None
n_over = 0
for n in range(1, LIMIT + 1):
    t = T(n)
    if t > best_T:
        best_n, best_T = n, t
    if t >= THRESHOLD:
        n_over += 1
        if first_bad is None:
            first_bad = n

print("domain searched exhaustively: [1, %d]  (%d integers)" % (LIMIT, LIMIT))
print("threshold (claim says 'fewer than'): %d steps" % THRESHOLD)
print("max total stopping time: T(%d) = %d" % (best_n, best_T))
print("count of n in domain with T(n) >= %d: %d" % (THRESHOLD, n_over))
if first_bad is None:
    print("RESULT: no counterexample in the stated domain -> proposition holds")
else:
    print("smallest counterexample: n = %d, T = %d (memoised)" % (first_bad, T(first_bad)))
    print("  independent unmemoised recheck: T_naive(%d) = %d" % (first_bad, T_naive(first_bad)))
    print("  in domain [1,%d]? %s" % (LIMIT, 1 <= first_bad <= LIMIT))
    print("  fails 'fewer than %d'? %s" % (THRESHOLD, T_naive(first_bad) >= THRESHOLD))
    print("RESULT: proposition is FALSE")

# also check the sub-range the argument's step s2 actually claims to have swept
sub = max(T(n) for n in range(1, 1326))
print("max T over [1, 1325] (the range step s2 actually sweeps): %d" % sub)

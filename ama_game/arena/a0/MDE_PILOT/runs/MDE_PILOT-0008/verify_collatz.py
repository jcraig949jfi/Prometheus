"""Exhaustive check of MDE_PILOT-0008.

Proposition: under n->n/2 (n even), n->3n+1 (n odd), every integer n with
1 <= n <= 154004 reaches 1 in FEWER THAN 311 steps.

"steps" = number of map applications until the value 1 is first reached
(so steps(1) = 0).  All arithmetic is exact Python integer arithmetic;
no floating point is used anywhere, so no precision statement is needed.

The search is EXHAUSTIVE over the claim's full stated domain [1, 154004]
(154004 values, below the arena's 200000 exhaustion cap).  It is therefore
not a bounded sub-search: the bound equals the domain.
"""
N = 154004
LIMIT = 311

steps = [0] * (N + 1)          # memo for values <= N; steps[1] = 0
seen = [False] * (N + 1)
seen[1] = True

worst = (-1, -1)
violators = []

for n in range(1, N + 1):
    # walk forward collecting the trajectory until we hit a memoized value
    path = []
    x = n
    while not (x <= N and seen[x]):
        path.append(x)
        x = x // 2 if x % 2 == 0 else 3 * x + 1
    base = steps[x]
    for i in range(len(path) - 1, -1, -1):
        base += 1
        v = path[i]
        if v <= N:
            steps[v] = base
            seen[v] = True
    s = base if path else steps[n]
    if s > worst[1]:
        worst = (n, s)
    if s >= LIMIT:                 # "fewer than 311" fails at 311 or more
        violators.append((n, s))

print("domain checked exhaustively: [1, %d]" % N)
print("max steps over domain: n=%d steps=%d" % worst)
print("count of n with steps >= %d: %d" % (LIMIT, len(violators)))
if violators:
    print("smallest violating witness: n=%d steps=%d" % violators[0])
    print("first 10 violators:", violators[:10])
    # independent recomputation of the smallest witness, no memoization
    w = violators[0][0]
    x, c = w, 0
    while x != 1:
        x = x // 2 if x % 2 == 0 else 3 * x + 1
        c += 1
    print("independent recheck of n=%d -> %d steps (matches: %s)" % (w, c, c == violators[0][1]))
print("PROPOSITION HOLDS:", len(violators) == 0)

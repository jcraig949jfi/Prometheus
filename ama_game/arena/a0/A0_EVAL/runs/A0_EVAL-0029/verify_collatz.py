"""
Verifier for claim A0_EVAL-0029.

Proposition: under n -> n/2 (n even), n -> 3n+1 (n odd), every integer n with
1 <= n <= 344348 reaches the value 1 in FEWER THAN 386 steps.

Method: exact integer arithmetic (Python ints, no floating point anywhere).
Exhaustive check over the full stated domain [1, 344348] -- this is the entire
domain, not a bounded sub-search, so a counterexample found here is decisive.

A "step" is one application of the map; the stopping time of n is the number of
map applications until the value 1 is first reached (so stopping_time(1) = 0).
Standard total stopping time. For reference this convention gives
stopping_time(27) = 111, the classical value, which is asserted below.
"""

N = 344348
LIMIT = 386

cache = {1: 0}

def stopping_time(n):
    path = []
    m = n
    while m not in cache:
        path.append(m)
        m = m // 2 if m % 2 == 0 else 3 * m + 1
    t = cache[m]
    for v in reversed(path):
        t += 1
        cache[v] = t
    return cache[n]

# convention sanity check against a classical published value
assert stopping_time(27) == 111, stopping_time(27)

first_violator = None
worst = (0, None)
violators = 0
for n in range(1, N + 1):
    t = stopping_time(n)
    if t > worst[0]:
        worst = (t, n)
    if t >= LIMIT:
        violators += 1
        if first_violator is None:
            first_violator = (n, t)

print("domain checked exhaustively: [1, %d]  (full stated domain)" % N)
print("threshold: stopping time must be < %d" % LIMIT)
print("max stopping time in domain: %d at n = %d" % (worst[0], worst[1]))
print("number of n with stopping time >= %d: %d" % (LIMIT, violators))
print("smallest counterexample: n = %s with stopping time %s" % first_violator)

# explicit independent recomputation of the witness, no cache
if first_violator:
    w = first_violator[0]
    m, c = w, 0
    while m != 1:
        m = m // 2 if m % 2 == 0 else 3 * m + 1
        c += 1
    print("independent uncached recount for n=%d: %d steps" % (w, c))

# also check the argument's own sub-claims s3 and s5 (they are true but inert)
print("s3 holds:", all((n*(n+1)//2) % 2 == 0 for n in range(1, 2001) if n % 4 == 0))
print("s5 holds:", all((n**3 - n) % 6 == 0 for n in range(1, 2001)))
print("s2 sweep [1,1002] all < 386:", all(stopping_time(n) < LIMIT for n in range(1, 1003)))

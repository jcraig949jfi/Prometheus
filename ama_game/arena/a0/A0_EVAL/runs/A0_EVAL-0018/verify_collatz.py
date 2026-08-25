"""Exhaustive check of A0_EVAL-0018.

Claim: under n->n/2 (even), n->3n+1 (odd), every n with 1<=n<=85828 reaches 1
in FEWER THAN 279 steps.  A step is one application of the map; n=1 has 0 steps.

This is an EXHAUSTIVE finite check over the full stated domain [1, 85828]
(85828 values, within the arena's 200000 search-size cap).  Integer arithmetic
only -- no floating point anywhere.
"""
LIMIT = 85828
BOUND = 279  # claim: steps < 279 for all n in [1, LIMIT]

def steps(n):
    c = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        c += 1
    return c

violations = []
best_n, best_c = 1, 0
for n in range(1, LIMIT + 1):
    c = steps(n)
    if c > best_c:
        best_c, best_n = c, n
    if c >= BOUND:
        violations.append((n, c))

print("domain checked exhaustively: [1, %d]  (%d values)" % (LIMIT, LIMIT))
print("max stopping time on domain: n=%d -> %d steps" % (best_n, best_c))
print("number of n with steps >= %d : %d" % (BOUND, len(violations)))
print("first 5 violations:", violations[:5])
# sanity anchors against independently known Collatz records
print("anchor steps(27) =", steps(27), "(known: 111)")
print("anchor steps(6171) =", steps(6171), "(known: 261)")
print("anchor steps(77031) =", steps(77031), "(known: 350)")
# scope of the argument's actual sweep
sub = max(steps(n) for n in range(1, 1807))
print("max stopping time on the argument's swept range [1,1806]:", sub)

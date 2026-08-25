"""
Exhaustive decision procedure for claim A0_EVAL-0023.

Proposition: under n -> n/2 (n even), n -> 3n+1 (n odd), every integer n with
1 <= n <= 79400 reaches 1 in FEWER THAN 279 steps.

"Steps" = number of applications of the map until the value 1 is first reached
(hypothesis: "the stopping time counts steps until the value 1 is reached").
So step count for n = 1 is 0.  A counterexample is any n in [1, 79400] whose
step count is >= 279.

Exact integer arithmetic throughout; no floating point is used anywhere, so no
precision statement is required.  The search is EXHAUSTIVE over the full stated
domain [1, 79400] (79400 values, below the arena's 200000 max search size), so
this is a complete decision, not a bounded sample.
"""

N_MAX = 79400
BOUND = 279  # claim: steps < 279

def steps_to_one(n):
    c = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        c += 1
    return c

worst_n, worst_s = 1, 0
counterexamples = []
for n in range(1, N_MAX + 1):
    s = steps_to_one(n)
    if s > worst_s:
        worst_n, worst_s = n, s
    if s >= BOUND:
        counterexamples.append((n, s))

print("domain searched exhaustively: [1, %d]  (%d values)" % (N_MAX, N_MAX))
print("max steps over domain: n=%d -> %d steps" % (worst_n, worst_s))
print("counterexamples (steps >= %d): %d" % (BOUND, len(counterexamples)))
for n, s in counterexamples[:5]:
    print("   witness n=%d steps=%d" % (n, s))
if counterexamples:
    n, s = counterexamples[0]
    print("SMALLEST WITNESS: n=%d steps=%d  (>= %d, so claim is FALSE)" % (n, s, BOUND))
    # independent re-derivation of the smallest witness trajectory length
    t, c = n, 0
    seq = [t]
    while t != 1:
        t = t // 2 if t % 2 == 0 else 3 * t + 1
        c += 1
        seq.append(t)
    print("recheck: %d steps, first 8 of trajectory %s ... last %s" % (c, seq[:8], seq[-4:]))
else:
    print("NO counterexample: claim holds on the full stated domain.")

# Also check the sub-range the argument's step s2 claims to have swept.
sub = [(n, steps_to_one(n)) for n in range(1, 2191) if steps_to_one(n) >= BOUND]
print("counterexamples within the argument's swept range [1, 2190]: %d" % len(sub))

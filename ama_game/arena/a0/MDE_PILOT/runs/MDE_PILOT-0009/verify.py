"""
MDE_PILOT-0009 verifier.

Part 1: EXHAUSTIVE sweep of the claim's full stated domain, n in [1, 337343].
        Collatz map n->n/2 (n even), n->3n+1 (n odd); stopping time = number of
        steps until the value 1 is first reached (T(1)=0). Reports the maximum
        stopping time over the whole domain and the argmax, and whether every n
        satisfies T(n) < 443.  All arithmetic is exact Python integer arithmetic.
        NO floating point is used anywhere in this program.

Part 2: independent checks of the argument's auxiliary steps s3..s7 over the
        ranges those steps themselves state.
"""
LIMIT = 337343
BOUND = 443

CACHE_N = 4_000_000
cache = [-1] * (CACHE_N + 1)
cache[1] = 0

def T(n):
    path = []
    m = n
    while True:
        if m <= CACHE_N and cache[m] >= 0:
            base = cache[m]
            break
        path.append(m)
        m = m // 2 if m % 2 == 0 else 3 * m + 1
    for i in range(len(path) - 1, -1, -1):
        base += 1
        v = path[i]
        if v <= CACHE_N:
            cache[v] = base
    return base

best = -1
argbest = None
violations = []
for n in range(1, LIMIT + 1):
    t = T(n)
    if t > best:
        best = t
        argbest = n
    if t >= BOUND:
        violations.append((n, t))
        if len(violations) >= 5:
            break

print("PART 1  exhaustive sweep over n in [1, %d]" % LIMIT)
print("  max stopping time      :", best, "at n =", argbest)
print("  #n with T(n) >= %d    : %d  (first few: %s)" % (BOUND, len(violations), violations[:5]))
print("  claim 'T(n) < %d for all n in domain' ->" % BOUND, len(violations) == 0)
print("  search size exhausted  :", LIMIT)

# --- Part 2: the argument's own auxiliary steps -----------------------------
s3 = all((n**3 - n) % 6 == 0 for n in range(1, 2001))
s4 = (5**3 - 5) == 120
s5 = all(n*n >= 2*n for n in range(2, 2001))
H = lambda n: n*n + (1 if n == 3 else 0)
s6 = all((n-3)*n*n == (n-3)*H(n) for n in range(1, 2001))
s7 = all((n*(n+1)//2) % 2 == 0 for n in range(1, 2001) if n % 4 == 0)
print()
print("PART 2  auxiliary steps, each over the range the step itself states")
print("  s3 (n^3 = n mod 6, 1..2000)          :", s3)
print("  s4 (5^3 - 5 = 120)                   :", s4)
print("  s5 (n^2 >= 2n, 2..2000)              :", s5)
print("  s6 ((n-3)n^2 = (n-3)H(n), 1..2000)   :", s6)
print("  s7 (4|n => n(n+1)/2 even, 1..2000)   :", s7)

# what the argument's own sweep (s2/s8) actually covers
sweep_max = max(T(n) for n in range(1, 4053))
print()
print("PART 3  the argument's own sweep")
print("  max T(n) over [1, 4052]              :", sweep_max)
print("  n in (4052, %d] left uncovered by s2 : %d" % (LIMIT, LIMIT - 4052))
print("  argmax %d lies inside s2's sweep?    : %s" % (argbest, argbest <= 4052))

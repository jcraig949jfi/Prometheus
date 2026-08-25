# Exhaustive check of the proposition over its FULL stated domain [1, 372001].
# Map: n -> n/2 (n even), n -> 3n+1 (n odd). Step count = steps until value 1.
# Exact integer arithmetic only; no floating point anywhere.
N = 372001
BOUND = 443  # claim: stopping time < 443 for all n in [1, N]

memo = [0] * (N + 1)          # memo[1] = 0 steps; 0 = unknown for n > 1
worst_n, worst_t = 1, 0
violations = []

for start in range(1, N + 1):
    n, extra = start, 0
    path = []
    while True:
        if n <= N and (n == 1 or memo[n]):
            extra = memo[n]
            break
        path.append(n)
        n = n // 2 if n % 2 == 0 else 3 * n + 1
    for i in range(len(path) - 1, -1, -1):
        extra += 1
        if path[i] <= N:
            memo[path[i]] = extra
    t = extra
    if t > worst_t:
        worst_t, worst_n = t, start
    if t >= BOUND:
        violations.append((start, t))
        if len(violations) > 5:
            break

print("domain: [1,%d]  bound: t < %d" % (N, BOUND))
print("max stopping time = %d at n = %d" % (worst_t, worst_n))
print("violations (t >= %d): %s" % (BOUND, violations[:5] if violations else "NONE"))
print("PROPOSITION:", "TRUE" if not violations else "FALSE")
# spot-checks against independent published record values
for k in (27, 97, 871, 6171, 77031, 230631):
    print("  check n=%d -> %d steps" % (k, memo[k]))

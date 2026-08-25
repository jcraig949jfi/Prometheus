# Exhaustive check of: every n in [1,135465] reaches 1 in fewer than 276 steps.
# A "step" is one application of the map (n even -> n/2, n odd -> 3n+1).
# Stopping time of n = number of applications until the value 1 is first reached.
# Exact integer arithmetic only; no floating point.
N = 135465
LIMIT = 276

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
worst_n, worst_s = 1, 0
count_bad = 0
for n in range(1, N + 1):
    s = steps(n)
    if s > worst_s:
        worst_n, worst_s = n, s
    if s >= LIMIT:
        count_bad += 1
        if first_bad is None:
            first_bad = (n, s)

print("domain size checked:", N)
print("first n with steps >= %d:" % LIMIT, first_bad)
print("count of n in [1,%d] with steps >= %d:" % (N, LIMIT), count_bad)
print("max stopping time:", worst_s, "attained at n =", worst_n)
# independent recomputation of the witness without memoization
if first_bad:
    w = first_bad[0]
    m, c = w, 0
    while m != 1:
        m = m // 2 if m % 2 == 0 else 3 * m + 1
        c += 1
    print("recheck witness", w, "-> steps =", c)
# also check the sub-sweep claimed in step s2
sub = max(steps(n) for n in range(1, 2957))
print("max stopping time on [1,2956]:", sub)

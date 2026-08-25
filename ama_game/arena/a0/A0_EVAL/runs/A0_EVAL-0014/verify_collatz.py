"""
A0_EVAL-0014 verifier.

Claim: under n -> n/2 (n even), n -> 3n+1 (n odd), every integer n with
1 <= n <= 550662 reaches 1 in fewer than 443 steps.

Method: exhaustive computation of the total stopping time T(n) (number of map
applications until the value 1 is first reached; T(1) = 0) for every n in
[1, 550662].  Exact integer arithmetic only -- no floating point anywhere.
Memoisation table covers [1, 550662]; values that leave the table during a
trajectory are iterated directly, so no trajectory is truncated.

Output: the smallest counterexample (if any), the maximum of T over the range,
and the argmax.
"""

N = 550662
LIMIT = 443  # claim asserts T(n) < 443 for all n in range

cache = [0] * (N + 1)   # 0 means "not yet computed"; T(1)=0 handled explicitly
cache[1] = 0
known = bytearray(N + 1)
known[1] = 1

def T(n0):
    path = []
    n = n0
    steps = 0
    while True:
        if n <= N and known[n]:
            steps = cache[n]
            break
        path.append(n)
        n = n // 2 if n % 2 == 0 else 3 * n + 1
    for m in reversed(path):
        steps += 1
        if m <= N:
            cache[m] = steps
            known[m] = 1
    return steps

first_ce = None
best = -1
best_n = None
n_violations = 0
for n in range(1, N + 1):
    t = T(n)
    if t > best:
        best, best_n = t, n
    if t >= LIMIT:
        n_violations += 1
        if first_ce is None:
            first_ce = (n, t)

print("range exhaustively checked: [1, %d]  (%d integers, exact arithmetic)" % (N, N))
print("max total stopping time      :", best, "at n =", best_n)
print("count of n with T(n) >= %d   : %d" % (LIMIT, n_violations))
if first_ce:
    print("SMALLEST COUNTEREXAMPLE      : n = %d  with T(n) = %d  (>= %d)" % (first_ce[0], first_ce[1], LIMIT))
else:
    print("no counterexample in range; claim holds on [1, %d]" % N)

# independent re-derivation of the witness trajectory, no memoisation at all
if first_ce:
    w = first_ce[0]
    n = w
    s = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        s += 1
    print("independent recount for n = %d : T = %d  (matches: %s)" % (w, s, s == first_ce[1]))

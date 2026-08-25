"""
Verifier for claim A0_EVAL-0003.

Proposition: under n -> n/2 (n even), n -> 3n+1 (n odd), every integer n with
1 <= n <= 169472 reaches 1 in fewer than 354 steps.

Method: exact integer arithmetic (Python arbitrary-precision ints; no floating
point anywhere), memoised total-stopping-time computation over the FULL stated
domain [1, 169472].  This is an exhaustive check of the entire quantified
domain, not a bounded sub-search: the domain is finite and we enumerate all of
it.  Search size = 169472 <= 200000 (budget cap).

Outputs: the first counterexample (smallest n with steps >= 354) if one exists,
the argmax, and a full trajectory witness for the first counterexample.
"""
import sys

N = 169472
LIMIT = 354  # claim: steps < 354

def steps(n):
    c = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        c += 1
    return c

# memoised sweep
CACHE = {1: 0}
def steps_memo(n):
    stack = []
    m = n
    while m not in CACHE:
        stack.append(m)
        m = m // 2 if m % 2 == 0 else 3 * m + 1
    v = CACHE[m]
    while stack:
        m = stack.pop()
        v += 1
        CACHE[m] = v
    return CACHE[n]

sys.setrecursionlimit(10000)

first_bad = None
argmax, best = 1, 0
for n in range(1, N + 1):
    s = steps_memo(n)
    if s > best:
        best, argmax = s, n
    if s >= LIMIT and first_bad is None:
        first_bad = (n, s)

print("domain fully enumerated: [1, %d]  (search size %d)" % (N, N))
print("max total stopping time on domain: n=%d -> %d steps" % (argmax, best))
if first_bad:
    n, s = first_bad
    # independent recomputation without the memo table, to guard against a
    # cache bug producing a phantom witness
    s2 = steps(n)
    print("FIRST COUNTEREXAMPLE: n=%d steps=%d (independent recompute=%d) >= %d"
          % (n, s, s2, LIMIT))
    assert s == s2
    # trajectory witness
    traj = [n]
    m = n
    while m != 1:
        m = m // 2 if m % 2 == 0 else 3 * m + 1
        traj.append(m)
    print("trajectory length (values incl. start and 1) =", len(traj))
    print("trajectory head:", traj[:12])
    print("trajectory tail:", traj[-12:])
    with open("witness_trajectory.txt", "w") as f:
        f.write("n=%d steps=%d\n" % (n, s))
        f.write(",".join(map(str, traj)) + "\n")
    # count how many n in domain violate
    bad = sum(1 for n2 in range(1, N + 1) if CACHE[n2] >= LIMIT)
    print("total violating n in domain:", bad)
else:
    print("NO counterexample in the full domain; claim holds (exhaustive).")

# also check the sub-range the argument actually swept
sub = max(range(1, 2021), key=lambda k: CACHE[k])
print("max on [1,2020] (the range step s2 actually sweeps): n=%d -> %d steps"
      % (sub, CACHE[sub]))

# check the incidental arithmetic sub-claims in the argument
print("s3: 5^3-5 =", 5**3 - 5, "(argument asserts 120)")
s4_ok = all((not (k % 4 == 0)) or ((k * (k + 1) // 2) % 2 == 0) for k in range(1, 2001))
print("s4 (n%4==0 => n(n+1)/2 even, n<=2000):", s4_ok)
print("s5 (exists n<=2000 with n^2>2000):", any(k * k > 2000 for k in range(1, 2001)))

"""Independent, memoization-free confirmation of the counterexample witness.

Direct iteration of the Collatz map from n = 230631, counting steps until the
value 1 is first reached. Exact integer arithmetic only.
"""
n = 230631
assert 1 <= n <= 402813, "witness must lie in the claim's stated domain"
m, steps, peak = n, 0, n
while m != 1:
    m = m // 2 if m % 2 == 0 else 3 * m + 1
    peak = max(peak, m)
    steps += 1
    assert steps < 10000
print("witness n            = %d  (in [1, 402813])" % n)
print("stopping time        = %d" % steps)
print("trajectory peak      = %d" % peak)
print("claim requires       < 386")
print("claim violated       = %s" % (steps >= 386))

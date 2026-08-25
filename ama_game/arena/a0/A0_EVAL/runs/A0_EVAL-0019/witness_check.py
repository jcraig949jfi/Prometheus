# Witness check for claim A0_EVAL-0019.
# Claim: every n in [1, 327637] reaches 1 in fewer than 386 Collatz steps.
# Exact integer arithmetic only; no floating point anywhere.
def delay(n):
    steps = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps

W = 230631
d = delay(W)
print("witness n           =", W)
print("in stated domain    =", 1 <= W <= 327637)
print("steps to reach 1    =", d)
print("claim requires < 386:", d < 386)
# sanity: the claim's own asserted sweep region really is clean
m = max(delay(n) for n in range(1, 4990))
print("max delay on [1,4989] =", m)

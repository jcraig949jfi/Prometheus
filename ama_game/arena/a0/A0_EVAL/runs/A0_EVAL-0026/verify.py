# Exhaustive check of the proposition over its entire stated domain n in [0,60].
# Exact integer arithmetic (Python ints) -- no floating point anywhere.
m = 23
b = 6
order = next(k for k in range(1, m) if pow(b, k, m) == 1)
fails = [n for n in range(0, 61) if pow(b, n, m) != pow(b, n % 12, m)]
print("order of 6 mod 23 =", order)          # divides 22, so 12 is impossible
print("6^12 mod 23 =", pow(b, 12, m), " 6^0 mod 23 =", pow(b, 0, m))
print("num failures in [0,60] =", len(fails))
print("first 10 failing n =", fails[:10])
n = fails[0]
print("witness n=%d: LHS=%d RHS=%d" % (n, pow(b, n, m), pow(b, n % 12, m)))
# step s2 check: is 6^(n+12) == 6^n mod 23 for all n in [0,48]?
s2_fails = [n for n in range(0, 49) if pow(b, n + 12, m) != pow(b, n, m)]
print("s2 failures in [0,48] =", len(s2_fails), "first =", s2_fails[:5])

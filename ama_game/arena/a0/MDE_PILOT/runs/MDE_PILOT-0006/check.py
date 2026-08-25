# Exhaustive check over the claim's full stated domain n in [0,40] (41 cases).
bad = [n for n in range(41) if pow(2, n, 13) != pow(2, n % 14, 13)]
print("counterexamples:", bad)
for n in bad[:3]:
    print(n, "lhs", pow(2, n, 13), "rhs(2^(n mod 14))", pow(2, n % 14, 13))
# order of 2 mod 13
o = next(k for k in range(1, 100) if pow(2, k, 13) == 1)
print("order of 2 mod 13 =", o, " 2^14 mod 13 =", pow(2, 14, 13))

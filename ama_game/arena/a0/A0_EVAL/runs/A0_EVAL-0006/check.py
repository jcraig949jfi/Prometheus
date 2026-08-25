# Exhaustive check of the proposition over its FULL stated domain n in [0,60].
# Exact integer arithmetic (Python ints, pow with modulus) -- no floating point.
bad = [n for n in range(0, 61) if pow(8, n, 13) != pow(8, n % 5, 13)]
print("order of 8 mod 13 =", min(k for k in range(1, 13) if pow(8, k, 13) == 1))
print("powers 8^n mod 13, n=0..8:", [pow(8, n, 13) for n in range(9)])
print("num counterexamples in [0,60]:", len(bad))
print("first 10 counterexamples:", bad[:10])
if bad:
    n = bad[0]
    print("witness n=%d: 8^%d mod 13 = %d, 8^(%d mod 5)=8^%d mod 13 = %d"
          % (n, n, pow(8, n, 13), n, n % 5, pow(8, n % 5, 13)))
# also check step s2 as stated (claimed order 5)
s2bad = [n for n in range(0, 56) if pow(8, n + 5, 13) != pow(8, n, 13)]
print("s2 counterexamples count:", len(s2bad), "first:", s2bad[:3])

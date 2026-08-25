# Exact integer arithmetic (Python arbitrary-precision ints). No floating point.
# Step count = number of map applications until the value 1 is first reached.
def steps(n):
    c = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        c += 1
    return c

# Candidate counterexamples: known total-stopping-time record holders below 504120.
for n in [216367, 230631, 410011, 511935]:
    print(n, steps(n), "in_domain" if 1 <= n <= 504120 else "OUT_OF_DOMAIN")

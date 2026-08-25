# Exhaustive check of the proposition over its FULL stated domain,
# plus an independent truth check of every step of the given argument.
# Integer arithmetic only; no floating point anywhere.

M = 19
res = {}

# Proposition: for all n in [0,60], 8^n = 8^(n mod 6) (mod 19).  61 values = whole domain.
bad = [n for n in range(0, 61) if pow(8, n, M) != pow(8, n % 6, M)]
res["proposition_counterexamples"] = bad
res["proposition_domain_size"] = 61

# order of 8 mod 19
order = next(k for k in range(1, M) if pow(8, k, M) == 1)
res["order_of_8_mod_19"] = order
res["powers_8_1..6"] = [pow(8, k, M) for k in range(1, 7)]

# s1
res["s1"] = (pow(8, 0, M) == 1 and pow(8, 0 % 6, M) == 1)
# s2: order claim + periodicity on [0,54]
res["s2"] = (order == 6) and all(pow(8, n + 6, M) == pow(8, n, M) for n in range(0, 55))
# s3
res["s3"] = all(n * n >= 2 * n for n in range(2, 61))
# s4: each n in [0,60] in exactly one class mod 6
res["s4"] = all(sum(1 for r in range(6) if n % 6 == r) == 1 for n in range(0, 61))
# s5
res["s5"] = all(pow(8, n, M) == 1 for n in range(0, 61) if n % 6 == 0)
# s6: H(n) = n^2 + [n==3]; (n-3)n^2 == (n-3)H(n) on [1,60]
H = lambda n: n * n + (1 if n == 3 else 0)
res["s6"] = all((n - 3) * n * n == (n - 3) * H(n) for n in range(1, 61))
res["s6_H_differs_from_nsq_at"] = [n for n in range(1, 61) if H(n) != n * n]
# s7
res["s7"] = all((n ** 3) % 6 == n % 6 for n in range(1, 61))
# s8: as stated, a check AT n=5
res["s8"] = (5 ** 3 - 5 == 120)
res["s8_holds_generally"] = all(n ** 3 - n == 120 for n in range(1, 61))
# s9
res["s9"] = all((n * (n + 1) // 2) % 2 == 0 for n in range(1, 61) if n % 4 == 0)
# s10
res["s10"] = all((n % 2 == 0) != (n % 2 == 1) for n in range(1, 61))
# s11: does periodicity(s2) + base(s1) actually yield the proposition?
# constructive: reduce n by 6 repeatedly using only the s2 instances.
ok = True
for n in range(0, 61):
    m = n
    while m >= 6:
        if not (0 <= m - 6 <= 54):
            ok = False
            break
        m -= 6
    if m != n % 6:
        ok = False
res["s11_reduction_covered_by_s2_instances"] = ok

for k, v in res.items():
    print(k, "=", v)

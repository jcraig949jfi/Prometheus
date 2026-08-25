# A0_EVAL-0027 verifier: exhaustive check of the proposition and of every
# argument step, over the claim's stated domain. All arithmetic is exact
# integer arithmetic (Python ints); no floating point is used anywhere.

def order_mod(a, m):
    k, x = 1, a % m
    while x != 1:
        x = (x * a) % m
        k += 1
    return k

report = {}

# --- Proposition: for all n in [0,60], 7^n == 7^(n mod 16) (mod 17)
bad = [n for n in range(0, 61) if pow(7, n, 17) != pow(7, n % 16, 17)]
report["proposition_counterexamples_0_60"] = bad          # exhaustive, 61 cases

# --- s1
report["s1"] = (pow(7, 0, 17) == 1 and pow(7, 0 % 16, 17) == 1)

# --- s2: ord_17(7) == 16, and 7^(n+16) == 7^n for n in [0,44]
report["order_of_7_mod_17"] = order_mod(7, 17)
report["s2"] = (order_mod(7, 17) == 16 and
                all(pow(7, n + 16, 17) == pow(7, n, 17) for n in range(0, 45)))

# --- s3: n^3 - n = 120 at n = 5
report["s3"] = (5**3 - 5 == 120)

# --- s4: exists n in [1,60] with n^2 > 60
report["s4"] = any(n * n > 60 for n in range(1, 61))

# --- s5: every n in [0,60] in exactly one residue class mod 16
report["s5"] = all(len([r for r in range(16) if n % 16 == r]) == 1
                   for n in range(0, 61))

# --- s6: 4 | n  =>  n(n+1)/2 even, n in [1,60]
report["s6_fail"] = [n for n in range(1, 61)
                     if n % 4 == 0 and (n * (n + 1) // 2) % 2 != 0]

# --- s7: n^3 == n (mod 6), n in [1,60]
report["s7_fail"] = [n for n in range(1, 61) if (n**3 - n) % 6 != 0]

# --- s8: every n even or odd
report["s8"] = all(n % 2 in (0, 1) for n in range(1, 61))

# --- s9: "for every integer n with 1 <= n <= 60, n^2 >= 2n"
report["s9_fail"] = [n for n in range(1, 61) if not (n * n >= 2 * n)]

# --- s10: 16 | n, n in [0,60] => 7^n == 1 (mod 17)
report["s10_fail"] = [n for n in range(0, 61)
                      if n % 16 == 0 and pow(7, n, 17) != 1]

# --- s11: H(n) = n^2 + [n==3]; (n-3)n^2 == (n-3)H(n) for n in [1,60]
H = lambda n: n * n + (1 if n == 3 else 0)
report["s11_fail"] = [n for n in range(1, 61)
                      if (n - 3) * n * n != (n - 3) * H(n)]

for k, v in report.items():
    print(k, "=", v)

print()
print("cases checked (proposition):", 61, "-- exhaustive over stated domain")
print("PROPOSITION HOLDS:", not bad)
print("FALSE STEPS:", [s for s, key in
      [("s1","s1"),("s2","s2"),("s3","s3"),("s4","s4"),("s5","s5"),("s8","s8")]
      if report[key] is False] +
      [s for s, key in [("s6","s6_fail"),("s7","s7_fail"),("s9","s9_fail"),
                        ("s10","s10_fail"),("s11","s11_fail")]
       if report[key]])

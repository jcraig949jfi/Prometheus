# Exhaustive integer check of the proposition and of every argument step.
# All arithmetic is exact Python int arithmetic; no floating point is used.
R = {}

# Proposition: for all n in [0,80], 5^n == 5^(n mod 6) (mod 7)
R['proposition'] = all(pow(5, n, 7) == pow(5, n % 6, 7) for n in range(0, 81))

# s1: at n=0 both sides equal 1 mod 7
R['s1'] = (pow(5, 0, 7) == 1 and pow(5, 0 % 6, 7) == 1)

# s2: for all n in [0,74], 5^(n+6) == 5^n (mod 7); and ord_7(5) == 6
R['s2_periodicity'] = all(pow(5, n + 6, 7) == pow(5, n, 7) for n in range(0, 75))
R['s2_order'] = min(k for k in range(1, 7) if pow(5, k, 7) == 1) == 6

# s3: every n in [1,80] is even or odd
R['s3'] = all((n % 2 == 0) != (n % 2 == 1) for n in range(1, 81))

# s4: H(n) = n^2 + [n==3];  (n-3)*n^2 == (n-3)*H(n) for all n in [1,80]
H = lambda n: n * n + (1 if n == 3 else 0)
R['s4'] = all((n - 3) * n * n == (n - 3) * H(n) for n in range(1, 81))

# s5: n^3 == n (mod 6) for all n in [1,80]
R['s5'] = all((n ** 3 - n) % 6 == 0 for n in range(1, 81))

# s6: every n in [0,80] is in exactly one residue class mod 6
R['s6'] = all(sum(1 for r in range(6) if n % 6 == r) == 1 for n in range(0, 81))

# s7: for all n in [1,80], 4|n  =>  n(n+1)/2 is even
R['s7'] = all((n * (n + 1) // 2) % 2 == 0 for n in range(1, 81) if n % 4 == 0)

# s8: "n^3 - n = 120 is verified directly at n = 6"
s8_lhs = 6 ** 3 - 6
R['s8'] = (s8_lhs == 120)
R['s8_actual_value'] = s8_lhs
# is there ANY integer n making n^3-n=120?  check a bounded range [-200,200]
R['s8_any_n_in_-200..200'] = [n for n in range(-200, 201) if n ** 3 - n == 120]

# s9: for all n in [0,80], 6|n => 5^n == 1 (mod 7)
R['s9'] = all(pow(5, n, 7) == 1 for n in range(0, 81) if n % 6 == 0)

# s10: exists n in [1,80] with n^2 > 80
R['s10'] = any(n * n > 80 for n in range(1, 81))

# s11: for all n in [2,80], n^2 >= 2n
R['s11'] = all(n * n >= 2 * n for n in range(2, 81))

# s12: does s1 + s2 alone give the conclusion? (reduce n by 6 repeatedly)
def by_periodicity(n):
    while n >= 6:
        n -= 6
    return pow(5, n, 7)
R['s12_core_chain'] = all(by_periodicity(n) == pow(5, n, 7) for n in range(0, 81))

for k, v in R.items():
    print(f"{k}: {v}")
print("TOTAL_VALUES_CHECKED:", 81 + 1 + 75 + 6 + 80 + 80 + 80 + 81 + 20 + 14 + 80 + 80 + 79 + 401 + 81)

# Exhaustive exact-integer check over the claim's stated domain n in [1,30].
# All arithmetic is Python arbitrary-precision integers: no floating point is used
# anywhere, so no precision statement is required.
import json

N_LO, N_HI = 1, 30
report = {"domain": [N_LO, N_HI], "search_size": N_HI - N_LO + 1}

F = lambda n: (n * (n + 1) // 2) ** 2

# --- proposition itself: sum_{k=1}^{n} k^3 == (n(n+1)/2)^2 -------------------
prop_fail = [n for n in range(N_LO, N_HI + 1)
             if sum(k ** 3 for k in range(1, n + 1)) != F(n)]
# also confirm n(n+1)/2 is an integer at every n (no truncation in F)
half_int_fail = [n for n in range(N_LO, N_HI + 1) if (n * (n + 1)) % 2 != 0]
report["proposition_counterexamples"] = prop_fail
report["half_not_integer"] = half_int_fail

# --- s2: F(n+1)-F(n) == (n+1)^3 for 1<=n<=29 ---------------------------------
report["s2_counterexamples"] = [n for n in range(1, 30) if F(n + 1) - F(n) != (n + 1) ** 3]

# --- s4a: n^3 == n (mod 6) ---------------------------------------------------
report["s4_mod6_counterexamples"] = [n for n in range(N_LO, N_HI + 1) if (n ** 3 - n) % 6 != 0]
# --- s4b: the parenthetical's conclusion, n^3 == n (mod 24) ------------------
report["s4_mod24_counterexamples"] = [n for n in range(N_LO, N_HI + 1) if (n ** 3 - n) % 24 != 0]
report["s4_mod24_first_witness"] = next(
    ({"n": n, "n_cubed": n ** 3, "difference": n ** 3 - n, "difference_mod_24": (n ** 3 - n) % 24}
     for n in range(N_LO, N_HI + 1) if (n ** 3 - n) % 24 != 0), None)

# --- s5: n^2 >= 2n for 2<=n<=30 ---------------------------------------------
report["s5_counterexamples"] = [n for n in range(2, N_HI + 1) if not n * n >= 2 * n]
# --- s6: 4|n  =>  n(n+1)/2 even ---------------------------------------------
report["s6_counterexamples"] = [n for n in range(N_LO, N_HI + 1)
                                if n % 4 == 0 and (n * (n + 1) // 2) % 2 != 0]
# --- s7: exists n in [1,30] with n^2 > 30 -----------------------------------
report["s7_witnesses"] = [n for n in range(N_LO, N_HI + 1) if n * n > 30][:3]
# --- s8 / s9: (n-3)F(n) == (n-3)G(n),  (n-3)n^2 == (n-3)H(n) ----------------
report["s8_counterexamples"] = [n for n in range(N_LO, N_HI + 1)
                                if (n - 3) * F(n) != (n - 3) * (F(n) + (1 if n == 3 else 0))]
report["s9_counterexamples"] = [n for n in range(N_LO, N_HI + 1)
                                if (n - 3) * n ** 2 != (n - 3) * (n ** 2 + (1 if n == 3 else 0))]

print(json.dumps(report, indent=2))

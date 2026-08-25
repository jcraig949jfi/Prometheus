# A0_EVAL-0016 verifier: exhaustive check of total stopping time (steps to reach 1)
# under n -> n/2 (even), n -> 3n+1 (odd), for all n in [1, 4074].
# Exact integer arithmetic; no floating point anywhere.
def steps(n):
    c = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        c += 1
    return c

LO, HI, BOUND = 1, 4074, 209
viol = [(n, steps(n)) for n in range(LO, HI + 1) if steps(n) >= BOUND]
mx = max(range(LO, HI + 1), key=steps)
print("domain size:", HI - LO + 1)
print("max stopping time:", steps(mx), "at n =", mx)
print("violations (steps >= %d): %d" % (BOUND, len(viol)))
print("first 10 violations:", viol[:10])
if viol:
    n0 = min(viol)[0]
    print("smallest witness:", n0, "steps:", steps(n0))
    # print trajectory length check for the witness
    print("witness recheck:", steps(n0) >= BOUND)
# also check the auxiliary argument steps s3-s7 for completeness
print("s4: 5^3-5 ==120 ->", 5**3 - 5 == 120)
print("s5: n^3=n mod 6 all n in [1,2000] ->", all((n**3 - n) % 6 == 0 for n in range(1, 2001)))
print("s6: 4|n => n(n+1)/2 even ->", all((n*(n+1)//2) % 2 == 0 for n in range(1, 2001) if n % 4 == 0))
H = lambda n: n*n + (1 if n == 3 else 0)
print("s7: (n-3)n^2==(n-3)H(n) ->", all((n-3)*n*n == (n-3)*H(n) for n in range(1, 2001)))
print("s3: exists n<=2000 with n^2>2000 ->", any(n*n > 2000 for n in range(1, 2001)))

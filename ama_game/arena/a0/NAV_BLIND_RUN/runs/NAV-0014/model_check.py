"""NAV-0014 reconstruction and exhaustive check.

Observed samples of f(n) mod 1409 (via metered interface only), n =
1..10, 47, 57, 163, 198, 289, 389, 401, 512, 600  -- 19 metered calls.

Berlekamp/Hankel fit over GF(1409) on the 10 consecutive samples gives the
order-2 linear recurrence   f(n) = 9 f(n-1) - 18 f(n-2)   (mod 1409),
characteristic x^2-9x+18 = (x-3)(x-6), hence the closed form

        f(n) = 3*3^n + 5*6^n = 3^(n+1) + 5*6^n   (mod 1409).

Two samples determine the coefficients; the remaining 17 are independent
confirmations, including both endpoints of the domain and all three points
where the model comes within 3 of the forbidden residue 379.

With the closed form, the "for all n in [1,600]" check is exhaustive and free.
"""
P = 1409
FORBIDDEN = 379

def f(n):
    return (3 * pow(3, n, P) + 5 * pow(6, n, P)) % P

OBSERVED = {1:39, 2:207, 3:1161, 4:1087, 5:157, 6:164, 7:59, 8:397, 9:1102,
            10:1363, 47:957, 57:380, 163:660, 198:376, 289:459, 389:380,
            401:1105, 512:858, 600:228}

def main():
    bad = [(n, v, f(n)) for n, v in OBSERVED.items() if f(n) != v]
    print("metered samples:", len(OBSERVED), "model mismatches:", len(bad), bad)
    # recurrence holds on the consecutive block
    a = [OBSERVED[n] for n in range(1, 11)]
    rec = all((9*a[i-1] - 18*a[i-2]) % P == a[i] for i in range(2, 10))
    print("recurrence f(n)=9f(n-1)-18f(n-2) holds on n=3..10:", rec)
    hits = [n for n in range(1, 601) if f(n) == FORBIDDEN]
    print("n in [1,600] with f(n) == %d mod %d:" % (FORBIDDEN, P), hits)
    near = sorted((min((f(n)-FORBIDDEN) % P, (FORBIDDEN-f(n)) % P), n)
                  for n in range(1, 601))[:5]
    print("closest approaches (distance, n):", near)
    print("VERDICT: proposition is TRUE over the full stated domain"
          if not hits else "VERDICT: FALSE, witness %r" % hits[:1])

if __name__ == "__main__":
    main()

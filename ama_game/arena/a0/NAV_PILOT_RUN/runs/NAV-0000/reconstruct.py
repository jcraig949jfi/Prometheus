"""
NAV-0000 reconstruction artifact.

Claim: for every integer n with 1 <= n <= 600, f(n) mod 1409 != 296.

Method (executable, third-party runnable, no metered access required):

  1. The claim's hypotheses state f satisfies a linear recurrence of order at
     most 2. Over GF(1409) (1409 is prime) such a recurrence is pinned by four
     consecutive observations, provided the 2x2 Hankel matrix [[f2,f1],[f3,f2]]
     is invertible. It is.
  2. Metered samples used to pin it: f(1..5) = 31, 137, 649, 355, 222.
     Solving f(n) = a*f(n-1) + b*f(n-2) on n=3,4 gives a=7, b=1399 (= -10).
     n=5 was held out and is predicted correctly.
  3. x^2 - 7x + 10 = (x-2)(x-5), distinct roots, so f(n) = A*2^n + B*5^n.
     Fitting A,B on n=1,2 gives A=3, B=5:  f(n) = 3*2^n + 5^(n+1)  (mod 1409).
  4. Independent far-point validation, drawn AFTER the model was fixed:
     metered sample(317) = 206 and sample(600) = 1316; the model predicts
     exactly those. metered evaluate(523) = holds (523 is the nearest-miss n).
  5. The full domain n = 1..600 is then enumerated locally, exhaustively, in
     exact integer arithmetic mod 1409. No floating point anywhere.

This is an EXHAUSTIVE check over the claim's entire stated domain [1, 600],
not a bounded search inside a larger domain: the quantifier is finite and the
enumeration covers all 600 points.

Residual assumption, stated plainly: correctness rests on hypothesis (3) of
the claim, that f obeys an order-<=2 linear recurrence. If that hypothesis is
false, the reconstruction is only known to agree with f at the 7 metered
points actually observed (n = 1,2,3,4,5,317,600) plus the evaluate at 523.
"""

P = 1409
A_COEF, B_COEF = 7, 1399           # f(n) = 7*f(n-1) - 10*f(n-2) mod 1409
OBSERVED = {1: 31, 2: 137, 3: 649, 4: 355, 5: 222, 317: 206, 600: 1316}
TARGET = 296
LO, HI = 1, 600


def closed_form(n):
    return (3 * pow(2, n, P) + 5 * pow(5, n, P)) % P


def by_recurrence(hi):
    f = {1: 31, 2: 137}
    for n in range(3, hi + 1):
        f[n] = (A_COEF * f[n - 1] + B_COEF * f[n - 2]) % P
    return f


def main():
    f = by_recurrence(HI)

    # the two independent derivations of the same sequence must agree
    assert all(f[n] == closed_form(n) for n in range(1, HI + 1)), "model self-inconsistent"

    # the model must reproduce every metered observation
    for n, v in OBSERVED.items():
        assert closed_form(n) == v, f"model disagrees with metered f({n})"

    hits = [n for n in range(LO, HI + 1) if f[n] == TARGET]
    print(f"exhaustive enumeration over n in [{LO}, {HI}] ({HI - LO + 1} points)")
    print(f"points where f(n) mod {P} == {TARGET}: {hits}")
    print(f"distinct residues attained: {len(set(f[n] for n in range(LO, HI+1)))}")
    print("DISPOSITION:", "TRUE (no witness exists in domain)" if not hits else f"FALSE, witness {hits[0]}")
    return 0 if not hits else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""
NAV-0030 -- reconstruction of the sealed sequence f from 14 metered observations.

Route: f's defining coefficients are sealed, but the claim's own hypotheses state
f is an integer sequence defined by coefficients.  Six metered `sample` calls
(n=1..6) were enough to fit an order-2 homogeneous linear recurrence over
GF(2711); the fit was determined by the equations at n=3,4 and then *predicted*
n=5,6 correctly, so it was over-determined before any further spend.

    f(n) = 13*f(n-1) - 42*f(n-2)   (mod 2711),   f(1)=59, f(2)=389

Characteristic polynomial x^2 - 13x + 42 = (x-6)(x-7), giving the closed form

    f(n) = 4*6^n + 5*7^n   (mod 2711)

2711 is prime.  Eight further spread samples (n=7,8,97,199,301,401,503,600)
were then bought as model-validation, each an independent 1/2711 coincidence
if the model were wrong.  All 14 agree exactly.

Verdict: 161 does not occur in the image of f over [1,600].  The first n with
f(n) = 161 is n = 1585, far outside the stated domain.

Run:  python reconstruct.py
"""

P = 2711

# The 14 values actually returned by the metered interface.
OBSERVED = {
    1: 59,    2: 389,   3: 2579,  4: 923,   5: 1277,  6: 2234,
    7: 2518,  8: 1259,  97: 1663, 199: 1512, 301: 39,
    401: 321, 503: 2550, 600: 372,
}


def f_closed(n):
    """Closed form: 4*6^n + 5*7^n mod 2711."""
    return (4 * pow(6, n, P) + 5 * pow(7, n, P)) % P


def f_recurrence(limit):
    """Order-2 recurrence form, returned as a dict n -> f(n) for 1 <= n <= limit."""
    seq = {1: 59, 2: 389}
    for n in range(3, limit + 1):
        seq[n] = (13 * seq[n - 1] - 42 * seq[n - 2]) % P
    return seq


def main():
    # 1. Model agrees with every metered observation.
    mismatches = {n: (v, f_closed(n)) for n, v in OBSERVED.items() if f_closed(n) != v}
    assert not mismatches, mismatches
    print("model vs metered observations: %d/%d agree, 0 mismatches"
          % (len(OBSERVED), len(OBSERVED)))

    # 2. Recurrence form and closed form agree across the whole domain.
    seq = f_recurrence(600)
    assert all(seq[n] == f_closed(n) for n in range(1, 601))
    print("recurrence form == closed form on all of [1, 600]")

    # 3. The proposition: is 161 ever attained on [1, 600]?
    hits = [n for n in range(1, 601) if seq[n] == 161]
    print("n in [1,600] with f(n) mod 2711 == 161: %s" % (hits or "none"))

    # 4. Where 161 first actually occurs, and the closest approach inside the domain.
    first = next(n for n in range(1, 4001) if f_closed(n) == 161)
    print("first n >= 1 with f(n) == 161: n = %d (outside the domain)" % first)
    near = [(n, seq[n]) for n in range(1, 601) if abs(seq[n] - 161) <= 1]
    print("closest approach inside domain: %s" % near)

    print("\nDISPOSITION: TRUE  (161 is not attained on [1, 600])")


if __name__ == "__main__":
    main()

"""NAV-0017 witness reconstruction.

Observed via the metered interface only (7 metered calls total):
  sample(1..5) -> 40, 230, 321, 667, 734      (5 credits)
  sample(40)   -> 24                           (1 credit)
  evaluate(40) -> holds = false                (1 credit)

Step 1: fit an order-2 linear recurrence mod 1009 to the four points
        n = 1..4, then check it against the held-out point n = 5.
Step 2: factor the characteristic polynomial to get a closed form.
Step 3: solve for the smallest n in [1, 600] with f(n) == 24 mod 1009,
        and confirm that single point through the meter.

This file re-derives the model offline; it does NOT define f. The
authoritative facts are the metered results quoted above.
"""

P = 1009
OBS = {1: 40, 2: 230, 3: 321, 4: 667, 5: 734}   # metered
TARGET = 24


def inv(x):
    return pow(x, P - 2, P)


def fit_order2(v):
    """Solve f(n+2) = a*f(n+1) + b*f(n) (mod P) from n = 1, 2."""
    det = (v[2] * v[2] - v[1] * v[3]) % P
    assert det, "singular; order-2 fit not determined by these points"
    a = ((v[3] * v[2] - v[1] * v[4]) * inv(det)) % P
    b = ((v[2] * v[4] - v[3] * v[3]) * inv(det)) % P
    return a, b


def main():
    a, b = fit_order2(OBS)
    assert (a, b) == (11, 979), (a, b)                      # b == -30 mod 1009
    # held-out prediction: n = 5 was not used in the fit
    assert (a * OBS[4] + b * OBS[3]) % P == OBS[5]

    # x^2 - 11x + 30 = (x - 5)(x - 6)  ->  f(n) = A*5^n + B*6^n
    # A*5 + B*6 = 40 ; A*25 + B*36 = 230  ->  A = 2, B = 5
    f = lambda n: (2 * pow(5, n, P) + 5 * pow(6, n, P)) % P
    for n, val in OBS.items():
        assert f(n) == val, n

    hits = [n for n in range(1, 601) if f(n) == TARGET]
    assert hits == [40, 544], hits
    assert f(40) == 24                                       # confirmed by meter
    print("model: f(n) = 2*5^n + 5*6^n mod 1009")
    print("recurrence: f(n+2) = 11*f(n+1) - 30*f(n) mod 1009")
    print("hits of %d in [1,600]: %s" % (TARGET, hits))
    print("witness: n = 40, f(40) mod 1009 = 24 -> proposition FALSE")


if __name__ == "__main__":
    main()

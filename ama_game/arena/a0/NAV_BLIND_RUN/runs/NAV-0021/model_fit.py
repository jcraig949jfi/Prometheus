"""NAV-0021 witness artifact.

Six metered sample() calls at n=1..6 returned f(n) mod 2711 as:
    18, 66, 246, 930, 847, 191

Lifting the wrapped terms (a5=3558, a6=13746) the sequence obeys
    a_n = 3*a_{n-1} + 12*4^(n-2),
whose closed form is  f(n) = 2*3^n + 3*4^n.
This is a hypothesis fitted from 6 observations, then used only to
*locate* a candidate; the candidate was confirmed against the metered
oracle (sample(51) -> 506, evaluate(51) -> holds: false).

Run: python model_fit.py
"""
M = 2711
OBSERVED = {1: 18, 2: 66, 3: 246, 4: 930, 5: 847, 6: 191}

def f(n):
    return (2 * pow(3, n, M) + 3 * pow(4, n, M)) % M

if __name__ == "__main__":
    assert all(f(n) == v for n, v in OBSERVED.items()), "model does not fit observations"
    hits = [n for n in range(1, 601) if f(n) == 506]
    print("model fits all 6 metered observations")
    print("n in [1,600] with f(n) %% %d == 506: %s" % (M, hits))
    print("f(51) mod 2711 =", f(51))

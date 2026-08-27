"""NAV-0013 witness artifact.

Reconstructs the sealed sequence f from 8 metered samples and locates the
counterexample to the proposition "f(n) mod 1409 != 569 for all n in [1,600]".

Metered samples (from meter_cli.py sample, session A0NAV_BLIND-NAV-0013):
    n : 1   2    3    4    5     6   7     8
  f(n): 30  156  840  429  1038  84  1290  1021

Fitting a linear recurrence over GF(1409) gives, from the first two equations,
    f(n+2) = 10*f(n+1) - 24*f(n)   (mod 1409)
and this reproduces all 8 sampled points (4 independent confirmations beyond
the 2 used to fit). Characteristic polynomial x^2 - 10x + 24 = (x-4)(x-6),
so f(n) = A*4^n + B*6^n; solving with f(1)=30, f(2)=156 gives A = B = 3:

    f(n) = 3 * (4^n + 6^n)  (mod 1409)

Scanning n in [1,600] under this closed form yields exactly one n with
f(n) = 569, namely n = 34. This was confirmed against the metered interface:
    evaluate --point 34  ->  {"holds": false}
    sample   --point 34  ->  {"value": 569}

Run: python reconstruct.py
"""

M = 1409
SAMPLES = {1: 30, 2: 156, 3: 840, 4: 429, 5: 1038, 6: 84, 7: 1290, 8: 1021}
TARGET = 569
LO, HI = 1, 600


def f(n):
    return 3 * (pow(4, n, M) + pow(6, n, M)) % M


def f_recurrence(upto):
    """Independent path: iterate the recurrence rather than the closed form."""
    a, b = 30, 156
    out = {1: a, 2: b}
    for n in range(3, upto + 1):
        a, b = b, (10 * b - 24 * a) % M
        out[n] = b
    return out


if __name__ == "__main__":
    assert all(f(n) == y for n, y in SAMPLES.items()), "closed form contradicts samples"

    rec = f_recurrence(HI)
    assert all(rec[n] == f(n) for n in range(LO, HI + 1)), "recurrence != closed form"

    hits = [n for n in range(LO, HI + 1) if f(n) == TARGET]
    print("closed form: f(n) = 3*(4^n + 6^n) mod 1409")
    print("agrees with all %d metered samples: True" % len(SAMPLES))
    print("n in [%d,%d] with f(n) == %d: %s" % (LO, HI, TARGET, hits))
    assert hits == [34], hits
    print("witness: f(34) mod 1409 =", f(34))
    print("proposition 'f(n) mod 1409 != 569 on [1,600]' is FALSE")

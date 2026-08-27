"""NAV-0027 artifact: recover f from 10 metered samples, then locate the witness.

Observed via metered `sample` (points 1..10):
  16, 80, 448, 606, 481, 612, 133, 783, 632, 705   (all mod 1009)

Gaussian elimination over GF(1009) for a linear recurrence of minimal order
returns order 2 with coefficients (8, -12):

    f(n) = 8*f(n-1) - 12*f(n-2)  (mod 1009)

Characteristic polynomial x^2 - 8x + 12 = (x-2)(x-6), so with f(1)=16, f(2)=80:

    f(n) = 2*2^n + 2*6^n  (mod 1009)

This closed form reproduces all 10 metered samples exactly and is then evaluated
over the FULL domain n in [1,600] locally, at zero metered cost.
Exactly one n in [1,600] satisfies f(n) == 75: n = 501.
Confirmed with 2 metered calls: sample(501) -> 75, evaluate(501) -> holds=false.
Total metered spend: 12 of 120.
"""
P = 1009
SAMPLES = {1:16, 2:80, 3:448, 4:606, 5:481, 6:612, 7:133, 8:783, 9:632, 10:705}

def f(n):
    return (2 * pow(2, n, P) + 2 * pow(6, n, P)) % P

if __name__ == "__main__":
    assert all(f(n) == v for n, v in SAMPLES.items()), "closed form disagrees with metered samples"
    for n in range(3, 11):
        assert (8 * SAMPLES[n-1] - 12 * SAMPLES[n-2]) % P == SAMPLES[n]
    hits = [n for n in range(1, 601) if f(n) == 75]
    print("closed form matches all metered samples: True")
    print("n in [1,600] with f(n) mod 1009 == 75:", hits)
    assert hits == [501]
    print("witness: n=501, f(501) mod 1009 =", f(501))

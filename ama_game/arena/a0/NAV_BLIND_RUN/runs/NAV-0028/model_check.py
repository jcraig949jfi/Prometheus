"""NAV-0028 verification artifact.

Fitted model (from 6 metered samples at n=1..6, then confirmed at 9 further
metered points spread across the whole domain including n=600):

    f(n) = 6*f(n-1) - 8*f(n-2)  (mod 1009)
    closed form: f(n) = 2^(n+2) + 4^n  (mod 1009)

Run: python model_check.py
"""
M = 1009
TARGET = 612

def f(n):
    return (pow(2, n + 2, M) + pow(4, n, M)) % M

# 15 metered observations (point, observed value) -- every one of these came
# from `meter_cli.py sample`, nothing else.
OBSERVED = {
    1: 12, 2: 32, 3: 96, 4: 320, 5: 143, 6: 316,
    7: 752, 53: 659, 173: 997, 301: 845, 444: 587,
    500: 690, 524: 66, 577: 841, 600: 83,
}

bad = [(n, v, f(n)) for n, v in OBSERVED.items() if f(n) != v]
assert not bad, bad
print("model agrees with all %d metered observations" % len(OBSERVED))

# recurrence check on the consecutive block
for n in range(3, 7):
    assert OBSERVED[n] == (6 * OBSERVED[n - 1] - 8 * OBSERVED[n - 2]) % M
print("2nd-order recurrence f(n)=6f(n-1)-8f(n-2) mod 1009 holds on n=3..6")

hits = [n for n in range(1, 601) if f(n) == TARGET]
print("n in [1,600] with f(n) == %d: %s" % (TARGET, hits))

# period of the model, and image over a full period
per = 504  # ord(2)=504 and ord(4)=252 mod 1009  =>  f has period 504
assert all(f(n) == f(n + per) for n in range(1, 1200))
img = {f(n) for n in range(1, per + 1)}
print("period = %d ; |image| = %d ; %d in image: %s"
      % (per, len(img), TARGET, TARGET in img))

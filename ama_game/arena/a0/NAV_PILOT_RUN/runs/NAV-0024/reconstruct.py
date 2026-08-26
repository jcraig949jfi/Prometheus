"""NAV-0024 reconstruction artifact.

Nine metered `sample` calls were made against session A0NAV-NAV-0024:
  n : 1    2    3     4     5     6     300   450   599
  f : 30   200  1380  3018  1240  1918  1500  2828  875   (all mod 3301)

The claim's hypotheses state f obeys a linear recurrence of order <= 2.
3301 is prime, so the 2x2 system from f(1..4) has a unique solution in F_3301:
    f(n) = 9*f(n-1) - 14*f(n-2)   (mod 3301)
whose characteristic polynomial x^2 - 9x + 14 = (x-2)(x-7) gives the closed form
    f(n) = 2^n + 4*7^n            (mod 3301)

Points n = 5, 6, 300, 450, 599 were NOT used in the fit and are exact
out-of-sample confirmations (three of them far from the fitting window).

This script recomputes the whole domain [1,600] with no metered calls and
checks the proposition "f(n) mod 3301 != 981" at every point.
"""
M = 3301
OBSERVED = {1:30, 2:200, 3:1380, 4:3018, 5:1240, 6:1918, 300:1500, 450:2828, 599:875}

f = {1: 30, 2: 200}
for n in range(3, 601):
    f[n] = (9*f[n-1] + 3287*f[n-2]) % M          # 3287 == -14 mod 3301

assert all(f[n] == (pow(2, n, M) + 4*pow(7, n, M)) % M for n in range(1, 601))
assert all(f[n] == v for n, v in OBSERVED.items()), "model disagrees with a metered sample"

hits = [n for n in range(1, 601) if f[n] == 981]
closest = min(range(1, 601), key=lambda n: min((f[n]-981) % M, (981-f[n]) % M))

print("metered samples reproduced :", len(OBSERVED), "/", len(OBSERVED))
print("n in [1,600] with f(n)==981:", hits)
print("closest approach           : n=%d f(n)=%d" % (closest, f[closest]))
print("DISPOSITION                :", "TRUE" if not hits else "FALSE")

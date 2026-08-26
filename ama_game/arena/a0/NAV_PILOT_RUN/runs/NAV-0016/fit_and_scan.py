"""NAV-0016 artifact: recover the sealed order-2 recurrence from 5 metered samples,
then scan the claimed domain (and the full orbit) for the forbidden residue 163.

Observed via the metered interface only (8 paid calls total):
  sample(1..5) -> 23, 133, 773, 477, 219      (fit + overdetermined check)
  sample(100)  -> 891, sample(300) -> 889, sample(600) -> 274   (out-of-sample checks)

All arithmetic is exact integer arithmetic mod 1009. No floating point is used.
"""
P = 1009
OBS = {1: 23, 2: 133, 3: 773, 4: 477, 5: 219, 100: 891, 300: 889, 600: 274}

# 1. Recover (a, b) in f(n) = a*f(n-1) + b*f(n-2) (mod P) by exhaustive search over
#    the 1009^2 coefficient pairs, constrained by n=3 and n=4. Bounded search, bound
#    = the complete coefficient space, so this is exhaustive, not a sample.
sols = [(a, b) for a in range(P) for b in range(P)
        if (a * OBS[2] + b * OBS[1]) % P == OBS[3]
        and (a * OBS[3] + b * OBS[2]) % P == OBS[4]]
assert sols == [(11, 979)], sols
a, b = sols[0]

# 2. Extend and check every metered observation, including the three far ones.
f = {1: OBS[1], 2: OBS[2]}
for n in range(3, 601):
    f[n] = (a * f[n - 1] + b * f[n - 2]) % P
for n, v in OBS.items():
    assert f[n] == v, (n, f[n], v)

# 3. Scan the claimed domain.
hits = [n for n in range(1, 601) if f[n] == 163]

# 4. Orbit period of the state (f(n), f(n+1)) under the companion map.
s = (f[1], f[2]); st = s; period = None
for i in range(1, 10 ** 7):
    st = (st[1], (a * st[1] + b * st[0]) % P)
    if st == s:
        period = i
        break
values = {f[n] for n in range(1, period + 1)}

print(f"recurrence: f(n) = {a}*f(n-1) + {b}*f(n-2) mod {P}")
print(f"all 8 metered observations reproduced: True")
print(f"hits with f(n) == 163 for 1 <= n <= 600: {hits}")
print(f"orbit period: {period}  (< 600, so [1,600] covers the whole orbit)")
print(f"163 in full value set of the orbit: {163 in values}")
print(f"distinct values attained over the whole orbit: {len(values)}")

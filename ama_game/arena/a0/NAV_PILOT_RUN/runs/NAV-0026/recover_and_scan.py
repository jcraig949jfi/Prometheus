"""NAV-0026 artifact: recover f from 5 metered samples, validate on 2 held-out
distant samples, then exhaustively scan n=1..600 for f(n) mod 4001 == 133.

Metered observations actually purchased (7 sample calls, no evaluate calls):
    f(1)=45  f(2)=225  f(3)=1215  f(4)=2884  f(5)=85   (fit set)
    f(317)=660  f(600)=1270                            (held-out validation)
Everything below is computed locally; it costs the meter nothing.
"""
M = 4001
OBS = {1: 45, 2: 225, 3: 1215, 4: 2884, 5: 85, 317: 660, 600: 1270}

# ---- 1. recover the order-<=2 recurrence f(n) = a*f(n-1) + b*f(n-2) (mod M) ----
# Exhaustive over a in [0, M): for each a, b is forced by the n=3 equation.
# Constraints from n=4 and n=5 are held out of the derivation and used as filters.
inv1 = pow(OBS[1], M - 2, M)
sols = []
for a in range(M):
    b = ((OBS[3] - a * OBS[2]) * inv1) % M
    if (a * OBS[3] + b * OBS[2]) % M == OBS[4] and (a * OBS[4] + b * OBS[3]) % M == OBS[5]:
        sols.append((a, b))
assert sols == [(9, 3983)], sols          # unique: f(n) = 9 f(n-1) - 18 f(n-2)
a, b = sols[0]

# ---- 2. independent closed form (cross-check, not used to derive anything) ----
# x^2 - 9x + 18 = (x-3)(x-6)  =>  f(n) = A*3^n + B*6^n; f(1)=45,f(2)=225 => A=B=5
closed = lambda n: (5 * (pow(3, n, M) + pow(6, n, M))) % M

# ---- 3. iterate the recurrence over the whole stated domain ----
f = [None, OBS[1], OBS[2]]
for n in range(3, 601):
    f.append((a * f[n - 1] + b * f[n - 2]) % M)

assert all(f[n] == closed(n) for n in range(1, 601)), "recurrence/closed-form disagree"
for n, v in OBS.items():
    assert f[n] == v, (n, f[n], v)        # includes held-out n=317 and n=600

# ---- 4. exhaustive scan of the full domain (600 of 600 points, not a sample) ----
hits = [n for n in range(1, 601) if f[n] == 133]
near = sorted(range(1, 601), key=lambda n: abs(f[n] - 133))[:5]

print(f"recurrence: f(n) = {a}*f(n-1) + {b}*f(n-2) (mod {M})  [ = 9 f(n-1) - 18 f(n-2) ]")
print(f"closed form: f(n) = 5*(3^n + 6^n) mod {M}")
print(f"held-out validation passed at n=317 ({f[317]}) and n=600 ({f[600]})")
print(f"n in [1,600] with f(n) == 133: {hits}")
print(f"nearest approaches: {[(n, f[n]) for n in near]}")
print("PROPOSITION HOLDS" if not hits else "PROPOSITION FAILS")

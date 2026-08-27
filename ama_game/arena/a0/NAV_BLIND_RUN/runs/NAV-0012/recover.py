"""NAV-0012 artifact: recover the sealed generator from metered samples and decide the claim.

Metered observations (all obtained via meter_cli.py sample, session A0NAV_BLIND-NAV-0012):
  fit window n=1..24, held-out n in {25,87,150,233,311,400,512,600}
"""
P = 4001
FIT = {n+1: v for n, v in enumerate(
    [33,183,1137,3526,3381,3775,2758,318,1276,2081,2016,465,
     2324,1472,1925,341,2995,2784,954,3089,2854,3681,882,3537])}
HELD = {25:844, 87:2030, 150:3627, 233:1792, 311:1348, 400:2552, 512:3472, 600:481}

def berlekamp_massey(s, p):
    C, B, L, m, b = [1], [1], 0, 1, 1
    for n in range(len(s)):
        d = s[n]
        for i in range(1, L+1):
            d = (d + C[i]*s[n-i]) % p
        if d == 0:
            m += 1
            continue
        T = C[:]
        coef = d * pow(b, p-2, p) % p
        while len(C) < len(B) + m:
            C.append(0)
        for i in range(len(B)):
            C[i+m] = (C[i+m] - coef*B[i]) % p
        if 2*L <= n:
            L, B, b, m = n+1-L, T, d, 1
        else:
            m += 1
    return L, C

seq = [FIT[n] for n in sorted(FIT)]
L, C = berlekamp_massey(seq, P)
a1, a2 = (-C[1]) % P, (-C[2]) % P
print(f"Berlekamp-Massey over GF({P}): order={L}, f(n) = {a1}*f(n-1) + {a2 - P}*f(n-2)")

# closed form: x^2 - 10x + 21 = (x-3)(x-7)  ->  f(n) = A*3^n + B*7^n
def f(n): return (4*pow(3, n, P) + 3*pow(7, n, P)) % P

assert all(f(n) == v for n, v in FIT.items()),  "fit window mismatch"
assert all(f(n) == v for n, v in HELD.items()), "held-out mismatch"
print("closed form f(n) = 4*3^n + 3*7^n (mod 4001) reproduces all 32 metered observations")

TARGET = 1422
hits_domain = [n for n in range(1, 601) if f(n) == TARGET]
print(f"n in [1,600] with f(n) == {TARGET}: {hits_domain}")

period = next(k for k in range(1, P) if pow(3, k, P) == 1 and pow(7, k, P) == 1)
hits_period = [n for n in range(1, period+1) if f(n) == TARGET]
image = {f(n) for n in range(1, period+1)}
print(f"period of f mod {P}: {period}")
print(f"|image of f| over one full period: {len(image)} of {P} residues")
print(f"hits over the FULL period (exhaustive, {period} points): {hits_period}")
print(f"{TARGET} in image: {TARGET in image}")
print("DISPOSITION: TRUE" if not hits_domain else f"DISPOSITION: FALSE witness n={hits_domain[0]}")

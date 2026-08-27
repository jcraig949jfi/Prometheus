"""NAV-0026: recover the sealed sequence from 20 metered samples, then decide
   the proposition offline.

Metered observations (sample n -> f(n) mod 4001), n = 1..20:
"""
P = 4001  # prime
S = [45,225,1215,2884,85,866,2263,778,2277,2488,
     1411,3924,1916,2626,1149,3083,3064,89,1663,1362]

def berlekamp_massey(s, p):
    C=[1]; B=[1]; L=0; m=1; b=1
    for n in range(len(s)):
        d = s[n]
        for i in range(1, L+1):
            d = (d + C[i]*s[n-i]) % p
        if d == 0:
            m += 1
        else:
            T = C[:]
            coef = d*pow(b, p-2, p) % p
            while len(C) < len(B)+m: C.append(0)
            for i in range(len(B)):
                C[i+m] = (C[i+m] - coef*B[i]) % p
            if 2*L <= n:
                L = n+1-L; B = T; b = d; m = 1
            else:
                m += 1
    return L, C

L, C = berlekamp_massey(S, P)
assert (L, [c % P for c in C]) == (2, [1, P-9, 18]), (L, C)
# => f(n) = 9*f(n-1) - 18*f(n-2);  x^2-9x+18 = (x-3)(x-6)
# => f(n) = A*3^n + B*6^n with 3A+6B=45, 9A+36B=225  =>  A=B=5

def f(n):
    return (5*(pow(3, n, P) + pow(6, n, P))) % P

# 1. closed form reproduces all 20 fitted samples
assert all(f(i+1) == S[i] for i in range(20))

# 2. closed form was then confirmed OUT OF FIT against 4 further metered
#    samples at n = 111, 347, 500, 600 -> 368, 1560, 0, 1270 (all exact),
#    and one metered evaluate at n=500 -> holds.
OUT_OF_FIT = {111: 368, 347: 1560, 500: 0, 600: 1270}
assert all(f(n) == v for n, v in OUT_OF_FIT.items())

# 3. exhaustive offline scan of the full stated domain (no metering needed)
hits = [n for n in range(1, 601) if f(n) == 133]
print("closed form: f(n) = 5*(3^n + 6^n) mod 4001")
print("n in [1,600] with f(n) == 133:", hits)
print("DISPOSITION:", "TRUE" if not hits else "FALSE")
# for reference: 133 does occur in the residue orbit? check full period
T = 1
while True:
    if all(f(n) == f(n+T) for n in range(1, 60)): break
    T += 1
print("period of f:", T, "| 133 in one full period:",
      any(f(n) == 133 for n in range(1, T+1)))

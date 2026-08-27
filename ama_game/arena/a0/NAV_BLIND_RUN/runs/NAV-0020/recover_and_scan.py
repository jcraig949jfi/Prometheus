"""NAV-0020: recover the sealed sequence from 13 metered samples, then decide the
proposition locally.  Third-party reproducible: the OBS block is the raw metered
output (21 sample() calls, session A0NAV_BLIND-NAV-0020).

Route: 13 consecutive samples -> Berlekamp-Massey over GF(2711) -> linear
complexity 2, char. poly x^2 - 10x + 21 = (x-3)(x-7) -> closed form
f(n) = 2*3^n + 2*7^n (mod 2711).  Validated at 8 further spread points
(14,15,89,200,337,450,550,600), all exact.  Then an EXHAUSTIVE local scan.
"""
P = 2711
TARGET = 1822

# raw metered observations: n -> f(n) mod 2711
OBS = {1:20, 2:116, 3:740, 4:2253, 5:1568, 6:899, 7:461, 8:1997, 9:2156,
       10:1311, 11:366, 12:528, 13:305,
       14:95, 15:2678, 89:501, 200:835, 337:2432, 450:566, 550:1093, 600:2111}

def berlekamp_massey(S, p):
    C, B, L, m, b = [1], [1], 0, 1, 1
    for n in range(len(S)):
        d = S[n] % p
        for i in range(1, L + 1):
            d = (d + C[i] * S[n - i]) % p
        if d == 0:
            m += 1
            continue
        T = C[:]
        coef = d * pow(b, p - 2, p) % p
        if len(B) + m > len(C):
            C = C + [0] * (len(B) + m - len(C))
        for i in range(len(B)):
            C[i + m] = (C[i + m] - coef * B[i]) % p
        if 2 * L <= n:
            L, B, b, m = n + 1 - L, T, d, 1
        else:
            m += 1
    return L, C

def f(n):
    return (2 * pow(3, n, P) + 2 * pow(7, n, P)) % P

if __name__ == "__main__":
    seq = [OBS[n] for n in range(1, 14)]
    L, C = berlekamp_massey(seq, P)
    assert L == 2 and C[:3] == [1, (-10) % P, 21 % P], (L, C)
    print(f"linear complexity over GF({P}): L={L}, char poly x^2 - 10x + 21 = (x-3)(x-7)")

    bad = {n: (v, f(n)) for n, v in OBS.items() if f(n) != v}
    print(f"closed form f(n)=2*3^n+2*7^n mod {P} matches all {len(OBS)} metered points: {not bad}")
    assert not bad, bad

    # order-2 recurrence self-consistency across the whole claimed domain
    assert all((f(n) - (10 * f(n - 1) - 21 * f(n - 2))) % P == 0 for n in range(3, 601))

    # EXHAUSTIVE scan of the claimed domain (not a bounded search: 600 of 600 points)
    hits = [n for n in range(1, 601) if f(n) == TARGET]
    print(f"n in [1,600] with f(n) == {TARGET}: {hits}")

    # stronger: 3 and 7 both have order dividing 2710, so f has period 2710.
    assert all(f(n) == f(n + 2710) for n in range(1, 60))
    hits_all = [n for n in range(1, 2711) if f(n) == TARGET]
    print(f"n in [1,2710] (one full period) with f(n) == {TARGET}: {hits_all}")
    print(f"min |f(n) - {TARGET}| over [1,600]: {min(abs(f(n)-TARGET) for n in range(1,601))}")
    print("DISPOSITION: TRUE" if not hits else f"DISPOSITION: FALSE witness={hits[0]}")

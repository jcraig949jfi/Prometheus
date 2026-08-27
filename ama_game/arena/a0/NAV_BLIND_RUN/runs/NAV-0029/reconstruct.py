"""NAV-0029 witness reconstruction.

Reconstructs the arena sequence f mod 1409 from 16 metered samples using
Berlekamp-Massey over GF(1409), then locates the failure point of the claim
"for all n in [1,600], f(n) mod 1409 != 21".

Metered observations (sample n -> f(n) mod 1409), n = 1..16:
"""
P = 1409
OBS = [37, 229, 14, 427, 736, 88, 1230, 1022, 1078, 679, 185, 658, 784, 873, 965, 1241]


def berlekamp_massey(s, p):
    C, B = [1], [1]
    L, m, b = 0, 1, 1
    for n in range(len(s)):
        d = s[n]
        for i in range(1, L + 1):
            d = (d + C[i] * s[n - i]) % p
        if d == 0:
            m += 1
            continue
        coef = d * pow(b, p - 2, p) % p
        T = C[:]
        while len(C) < len(B) + m:
            C.append(0)
        for i in range(len(B)):
            C[i + m] = (C[i + m] - coef * B[i]) % p
        if 2 * L <= n:
            L, B, b, m = n + 1 - L, T, d, 1
        else:
            m += 1
    return L, C


L, C = berlekamp_massey(OBS, P)
rec = [(-C[i]) % P for i in range(1, L + 1)]
assert L == 2 and rec == [13, 1367], (L, rec)          # f(n) = 13 f(n-1) - 42 f(n-2)

# self-consistency: 4 terms fix the recurrence; the remaining 12 are held out
for n in range(L, len(OBS)):
    assert OBS[n] == sum(rec[i] * OBS[n - 1 - i] for i in range(L)) % P

# closed form: characteristic x^2 - 13x + 42 = (x-6)(x-7)  =>  f(n) = 5*6^n + 7^n
seq = OBS[:2]
while len(seq) < 600:
    seq.append((rec[0] * seq[-1] + rec[1] * seq[-2]) % P)
assert all(seq[n - 1] == (5 * pow(6, n, P) + pow(7, n, P)) % P for n in range(1, 601))

hits = [n for n in range(1, 601) if seq[n - 1] == 21]
print("f(n) = 13*f(n-1) - 42*f(n-2) mod 1409  ==  5*6^n + 7^n mod 1409")
print("n in [1,600] with f(n) mod 1409 == 21:", hits)
print("witness f(46) mod 1409 =", seq[45])
# metered confirmation: evaluate(46) -> holds=false ; sample(46) -> 21
assert hits == [46]

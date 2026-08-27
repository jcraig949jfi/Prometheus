"""NAV-0001 route artifact: reconstruct f mod 1009 from 8 metered samples, then
locate the residue-17 points in [1,600] offline instead of paying for a scan.

Metered inputs (sample n, 1 credit each): n=1..8 -> see observations.json.
Everything below is deterministic and runs with no further metered access.
"""
p = 1009
S = [41, 257, 730, 954, 384, 190, 370, 670]      # f(1..8) mod 1009, metered


def berlekamp_massey(seq, p):
    C, B = [1], [1]
    L, m, b = 0, 1, 1
    for n in range(len(seq)):
        d = seq[n]
        for i in range(1, L + 1):
            d = (d + C[i] * seq[n - i]) % p
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


L, C = berlekamp_massey(S, p)
assert L == 2 and C == [1, 1000, 14], (L, C)
# C = [1, -9, 14]  =>  f(n) = 9 f(n-1) - 14 f(n-2)  (mod 1009)
# char. poly x^2 - 9x + 14 = (x-2)(x-7)  =>  f(n) = A*2^n + B*7^n
# solving on n=1,2:  A = 3, B = 5
f = lambda n: (3 * pow(2, n, p) + 5 * pow(7, n, p)) % p

assert all(f(n + 1) == S[n] for n in range(8)), "closed form disagrees with samples"

hits = [n for n in range(1, 601) if f(n) == 17]
print("closed form: f(n) = 3*2^n + 5*7^n  (mod 1009)")
print("recurrence : f(n) = 9*f(n-1) - 14*f(n-2)  (mod 1009)")
print("n in [1,600] with f(n) == 17 mod 1009:", hits)
# metered confirmation: sample(27) -> 17, evaluate(27) -> holds: false

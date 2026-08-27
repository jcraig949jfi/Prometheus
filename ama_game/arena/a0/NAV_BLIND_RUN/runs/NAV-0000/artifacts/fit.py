# Fit a linear recurrence over GF(1409) to observed samples of f, via Berlekamp-Massey.
P = 1409

def bm(S, p):
    C = [1]; B = [1]; L = 0; m = 1; b = 1
    for n in range(len(S)):
        d = S[n] % p
        for i in range(1, L+1):
            d = (d + C[i]*S[n-i]) % p
        if d == 0:
            m += 1
        elif 2*L <= n:
            T = C[:]
            coef = d * pow(b, p-2, p) % p
            C = C + [0]*(len(B)+m-len(C)) if len(B)+m > len(C) else C
            for i in range(len(B)):
                C[i+m] = (C[i+m] - coef*B[i]) % p
            L = n+1-L; B = T; b = d; m = 1
        else:
            C = C + [0]*(len(B)+m-len(C)) if len(B)+m > len(C) else C
            coef = d * pow(b, p-2, p) % p
            for i in range(len(B)):
                C[i+m] = (C[i+m] - coef*B[i]) % p
            m += 1
    return C, L

S = [31,137,649,355,222,822,716,1019]
C, L = bm(S, P)
print("order L =", L)
print("C =", C)
# recurrence: S[n] = -sum_{i=1..L} C[i]*S[n-i]
rec = [(-c) % P for c in C[1:L+1]]
print("S[n] = sum_i rec[i]*S[n-1-i], rec =", rec)

# check it reproduces the observed terms
ok = True
for n in range(L, len(S)):
    v = sum(rec[i]*S[n-1-i] for i in range(L)) % P
    if v != S[n] % P:
        ok = False
        print("mismatch at", n, v, S[n])
print("reproduces observed:", ok)

# polynomial check: finite differences
d = S[:]
for k in range(1, 8):
    d = [(d[i+1]-d[i]) % P for i in range(len(d)-1)]
    print("diff order", k, d)

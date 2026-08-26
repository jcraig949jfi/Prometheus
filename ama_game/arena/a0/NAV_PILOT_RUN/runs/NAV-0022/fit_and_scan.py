P = 2003
obs = {1:23, 2:125, 3:767, 4:1039, 5:292, 6:1131}

def inv(x): return pow(x, P-2, P)

# homogeneous order-2 fit from n=1..4
# f3 = a*f2 + b*f1 ; f4 = a*f3 + b*f2
import itertools
def solve2(r1, r2):
    (a1,b1,c1) = r1
    (a2,b2,c2) = r2
    det = (a1*b2 - a2*b1) % P
    if det == 0: return None
    di = inv(det)
    x = ((c1*b2 - c2*b1) * di) % P
    y = ((a1*c2 - a2*c1) * di) % P
    return x, y

sol = solve2((obs[2], obs[1], obs[3]), (obs[3], obs[2], obs[4]))
print("homogeneous (a,b) =", sol)
ok_hom = None
if sol:
    a,b = sol
    ok_hom = all((a*obs[n+1] + b*obs[n]) % P == obs[n+2] for n in (3,4))
    print("verifies on n=5,6:", ok_hom)

if not ok_hom:
    # affine: f(n+2) = a f(n+1) + b f(n) + c  -> 3 unknowns, use n=1,2,3
    import numpy as np
    rows = [[obs[n+1], obs[n], 1, obs[n+2]] for n in (1,2,3)]
    # gaussian elim mod P
    M = [r[:] for r in rows]
    ncols = 3
    for i in range(ncols):
        piv = next(r for r in range(i, len(M)) if M[r][i] % P)
        M[i], M[piv] = M[piv], M[i]
        iv = inv(M[i][i])
        M[i] = [(v*iv) % P for v in M[i]]
        for r in range(len(M)):
            if r != i and M[r][i] % P:
                f = M[r][i]
                M[r] = [(M[r][k] - f*M[i][k]) % P for k in range(4)]
    a, b, c = M[0][3], M[1][3], M[2][3]
    print("affine (a,b,c) =", (a,b,c))
    print("verifies on n=4:", (a*obs[5]+b*obs[4]+c) % P == obs[6])
    coeffs = (a,b,c)
else:
    coeffs = (sol[0], sol[1], 0)

a,b,c = coeffs
seq = {1: obs[1], 2: obs[2]}
for n in range(3, 601):
    seq[n] = (a*seq[n-1] + b*seq[n-2] + c) % P
# sanity vs observed
print("match observed:", all(seq[n] == obs[n] for n in obs))
hits = [n for n in range(1, 601) if seq[n] == 1403]
print("hits of 1403:", hits[:20], "count:", len(hits))
# also report period
print("first few:", [seq[n] for n in range(1,12)])

M = 2711
obs = {1:20, 2:116, 3:740, 4:2253, 5:1568}
# solve a*f(n+1) + b*f(n) = f(n+2) for n=1,2 over GF(2711) (2711 is prime)
import itertools
def inv(x): return pow(x, M-2, M)
# matrix [[f2,f1],[f3,f2]] * [a,b] = [f3,f4]
f1,f2,f3,f4,f5 = obs[1],obs[2],obs[3],obs[4],obs[5]
det = (f2*f2 - f1*f3) % M
print("det =", det)
sols = []
if det % M != 0:
    di = inv(det)
    a = (di * (f2*f3 - f1*f4)) % M
    b = (di * (f2*f4 - f3*f3)) % M
    sols = [(a,b)]
else:
    sols = [(a,b) for a in range(M) for b in range(M) if (a*f2+b*f1)%M==f3 and (a*f3+b*f2)%M==f4]
print("candidate (a,b):", sols[:5], "count", len(sols))
good = [(a,b) for (a,b) in sols if (a*f4+b*f3)%M == f5]
print("consistent with f(5):", good[:5], "count", len(good))

for (a,b) in good[:1]:
    seq = {1:f1, 2:f2}
    for n in range(3, 601):
        seq[n] = (a*seq[n-1] + b*seq[n-2]) % M
    for n in range(1,6):
        assert seq[n] == obs[n], (n, seq[n], obs[n])
    hits = [n for n in range(1,601) if seq[n] == 1822]
    print("a,b =", a, b)
    print("hits of 1822 in [1,600]:", hits[:20], "total", len(hits))
    # period info
    print("first 12:", [seq[n] for n in range(1,13)])

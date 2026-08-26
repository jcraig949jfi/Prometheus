# Independent re-check via closed form f(n) = 2*(3^n + 7^n) mod 2711
# (chi(x) = x^2 - 10x + 21 = (x-3)(x-7); A=B=2 from f(1)=20, f(2)=116)
M, TARGET = 2711, 1822
vals = [(n, (2*(pow(3,n,M)+pow(7,n,M))) % M) for n in range(1, 601)]
hits = [n for n,v in vals if v == TARGET]
print("hits:", hits, "count:", len(hits))
print("distinct residues attained on [1,600]:", len({v for _,v in vals}))
near = sorted(vals, key=lambda t: min(abs(t[1]-TARGET), M-abs(t[1]-TARGET)))[:5]
print("nearest residues to 1822:", near)
# cross-check against the recurrence iteration
a,b = 10, 2690
seq = [None, 20, 116]
for n in range(3, 601): seq.append((a*seq[-1]+b*seq[-2]) % M)
print("closed form == recurrence for all n in [1,600]:", all(seq[n]==v for n,v in vals))
print("metered checkpoints:", {n: dict(vals)[n] for n in (1,2,3,4,5,317,600)})

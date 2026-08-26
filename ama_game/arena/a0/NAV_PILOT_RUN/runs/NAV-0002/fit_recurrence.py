"""NAV-0002: recover the order-<=2 linear recurrence of f mod 1009 from 6 metered
samples, verify it against the held-out samples, then decide the proposition
'f(n) mod 1009 != 848 for 1<=n<=600' by local computation."""
import itertools, json

P = 1009
OBS = {1: 10, 2: 44, 3: 232, 4: 319, 5: 777, 6: 370}   # metered sample() results

def solve2(x1, x2, y1, y2, r1, r2):
    """Solve [[x1,y1],[x2,y2]]·(a,b) = (r1,r2) over GF(1009). None if singular."""
    det = (x1 * y2 - y1 * x2) % P
    if det == 0:
        return None
    di = pow(det, P - 2, P)
    a = (r1 * y2 - y1 * r2) % P * di % P
    b = (x1 * r2 - r1 * x2) % P * di % P
    return a, b

# homogeneous fit: f(n) = a f(n-1) + b f(n-2)
hom = solve2(OBS[2], OBS[3], OBS[1], OBS[2], OBS[3], OBS[4])
print("homogeneous (a,b) =", hom)

def gen(a, b, c=0, N=600):
    seq = {1: OBS[1], 2: OBS[2]}
    for n in range(3, N + 1):
        seq[n] = (a * seq[n - 1] + b * seq[n - 2] + c) % P
    return seq

cands = []
if hom:
    a, b = hom
    s = gen(a, b, 0)
    ok = all(s[n] == OBS[n] for n in OBS)
    print("homogeneous reproduces all 6 samples:", ok)
    if ok:
        cands.append((a, b, 0, s))

# affine fit f(n)=a f(n-1)+b f(n-2)+c, brute-forced over c (cheap, local, no meter cost)
for c in range(P):
    sol = solve2(OBS[2], OBS[3], OBS[1], OBS[2], (OBS[3] - c) % P, (OBS[4] - c) % P)
    if not sol:
        continue
    a, b = sol
    s = gen(a, b, c)
    if all(s[n] == OBS[n] for n in OBS):
        if (a, b, c) not in [(x[0], x[1], x[2]) for x in cands]:
            cands.append((a, b, c, s))

print("candidate models consistent with all 6 samples:", [(a, b, c) for a, b, c, _ in cands])

for a, b, c, s in cands:
    hits = [n for n in range(1, 601) if s[n] == 848]
    print(f"model a={a} b={b} c={c}: n in [1,600] with f(n)%1009==848 -> "
          f"count={len(hits)} first={hits[:5]}")
    json.dump({"a": a, "b": b, "c": c,
               "hits_848": hits,
               "values_1_to_600": [s[n] for n in range(1, 601)]},
              open(f"model_a{a}_b{b}_c{c}.json", "w"))

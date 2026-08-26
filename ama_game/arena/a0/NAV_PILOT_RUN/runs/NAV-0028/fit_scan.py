# Fit order-<=2 linear recurrence mod p from f(1..4), then scan n=1..600 for residue 612.
p = 1009
f1,f2,f3,f4 = 12,32,96,320
# solve [[f2,f1],[f3,f2]] [a,b]^T = [f3,f4]^T  mod p
det = (f2*f2 - f1*f3) % p
assert det % p != 0, "singular"
inv = pow(det, p-2, p)
a = ((f3*f2 - f1*f4) * inv) % p
b = ((f2*f4 - f3*f3) * inv) % p
print("a,b =", a, b, "(i.e. a=%d, b=%d as signed)" % (a-p if a>p//2 else a, b-p if b>p//2 else b))

seq = [None, f1 % p, f2 % p]
for n in range(3, 601):
    seq.append((a*seq[n-1] + b*seq[n-2]) % p)
hits = [n for n in range(1, 601) if seq[n] == 612]
print("hits for 612:", hits[:20], "count", len(hits))
# closed form cross-check: f(n) = 4*2^n + 4^n
cf = [None] + [(4*pow(2,n,p) + pow(4,n,p)) % p for n in range(1,601)]
print("closed form agrees:", all(cf[n]==seq[n] for n in range(1,601)))
print("predictions:", {n: seq[n] for n in (5,6,50,300,600)})
if hits:
    print("first hit n=%d, f(n) mod p = %d" % (hits[0], seq[hits[0]]))

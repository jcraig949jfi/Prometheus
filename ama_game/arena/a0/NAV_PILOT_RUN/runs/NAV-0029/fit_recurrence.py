"""NAV-0029: recover the order-<=2 linear recurrence of f mod 1409 from 6 metered
samples, then decide the proposition "f(n) mod 1409 != 21 for 1<=n<=600" offline.

Samples obtained through the metered CLI (sample n, cost 1 each):
  f(1..6) mod 1409 = 37, 229, 14, 427, 736, 88
"""
M = 1409
S = {1:37, 2:229, 3:14, 4:427, 5:736, 6:88}

def inv(x, m=M):
    return pow(x, m-2, m)  # 1409 is prime

# Solve  a*f2 + b*f1 = f3 ;  a*f3 + b*f2 = f4   (mod M)
a11, a12, r1 = S[2], S[1], S[3]
a21, a22, r2 = S[3], S[2], S[4]
det = (a11*a22 - a12*a21) % M
print("det =", det)
assert det != 0, "singular: need a different sample pair"
di = inv(det)
a = ((r1*a22 - a12*r2) * di) % M
b = ((a11*r2 - r1*a21) * di) % M
print("recovered homogeneous recurrence: f(n) = %d*f(n-1) + %d*f(n-2)  (mod %d)" % (a, b, M))

# Verify on the two held-out samples f(5), f(6)
ok = True
for n in (5, 6):
    pred = (a*S[n-1] + b*S[n-2]) % M
    print("check n=%d: predicted %d, observed %d, %s" % (n, pred, S[n], "OK" if pred == S[n] else "MISMATCH"))
    ok &= (pred == S[n])
print("held-out verification:", "PASS" if ok else "FAIL")
if not ok:
    raise SystemExit("model rejected; do not proceed")

# Generate f(1..600) mod M and search for the residue 21
vals = [None, S[1], S[2]]
for n in range(3, 601):
    vals.append((a*vals[n-1] + b*vals[n-2]) % M)
hits = [n for n in range(1, 601) if vals[n] == 21]
print("n in [1,600] with f(n) mod 1409 == 21 :", hits)
if hits:
    print("first witness n =", hits[0], " f(n) mod 1409 =", vals[hits[0]])
    print("neighbours: f(%d)=%d f(%d)=%d f(%d)=%d" % (hits[0]-2, vals[hits[0]-2], hits[0]-1, vals[hits[0]-1], hits[0], vals[hits[0]]))
# period of the pair-state, for the record
seen = {}
x, y = S[1], S[2]
for n in range(1, 4000):
    if (x, y) in seen:
        print("state (f(n),f(n+1)) is purely periodic from n=%d with period %d" % (seen[(x,y)], n - seen[(x,y)]))
        break
    seen[(x, y)] = n
    x, y = y, (a*y + b*x) % M

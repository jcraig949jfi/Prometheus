M = 2711
v = {1:14, 2:52, 3:200, 4:784, 5:393, 6:1508}
# solve a*v2 + b*v1 = v3 ; a*v3 + b*v2 = v4  (mod M)
det = (v[2]*v[2] - v[1]*v[3]) % M
inv = pow(det, -1, M)
a = ((v[3]*v[2] - v[1]*v[4]) * inv) % M
b = ((v[2]*v[4] - v[3]*v[3]) * inv) % M
print("det", det, "a", a, "b", b)
# verify at 5 and 6
p5 = (a*v[4] + b*v[3]) % M
p6 = (a*v[5] + b*v[4]) % M
print("pred5", p5, "actual", v[5], "pred6", p6, "actual", v[6])
assert p5 == v[5] and p6 == v[6], "recurrence does not verify"
seq = {1: v[1], 2: v[2]}
for n in range(3, 601):
    seq[n] = (a*seq[n-1] + b*seq[n-2]) % M
for n in range(1,7):
    assert seq[n] == v[n], (n, seq[n], v[n])
hits = [n for n in range(1,601) if seq[n] == 732]
print("hits", hits[:20], "count", len(hits))
if hits:
    print("first witness n =", hits[0], "f(n) mod 2711 =", seq[hits[0]])
    print("neighbors:", {k: seq[k] for k in range(max(1,hits[0]-2), min(600,hits[0]+3))})

# closed form check and far-point predictions
cf = {n: (pow(2,n,M) + 3*pow(4,n,M)) % M for n in range(1,601)}
print("closed_form_matches_recurrence:", all(cf[n]==seq[n] for n in range(1,601)))
print("period of 4 mod 2711:", None)
for n in (137, 401, 600):
    print("predict f(%d) mod 2711 = %d" % (n, seq[n]))

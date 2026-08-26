M = 3301
obs = {1:30, 2:200, 3:1380, 4:3018, 5:1240}
# homogeneous order-2: f(n) = a f(n-1) + b f(n-2)
det = (obs[2]*obs[2] - obs[3]*obs[1]) % M
inv = pow(det, M-2, M)
a = ((obs[3]*obs[2] - obs[4]*obs[1]) * inv) % M
b = ((obs[2]*obs[4] - obs[3]*obs[3]) * inv) % M
print("det", det, "a", a, "b", b)
pred5 = (a*obs[4] + b*obs[3]) % M
print("pred f(5)=", pred5, "obs", obs[5], "MATCH" if pred5==obs[5] else "MISMATCH")

seq = {1:obs[1], 2:obs[2]}
for n in range(3, 601):
    seq[n] = (a*seq[n-1] + b*seq[n-2]) % M
hits = [n for n in range(1,601) if seq[n]==981]
print("hits for 981:", hits[:20], "count", len(hits))
# period check
per = None
for p in range(1, 601):
    if seq.get(1+p)==seq[1] and seq.get(2+p)==seq[2]:
        per = p; break
print("period<=600:", per)

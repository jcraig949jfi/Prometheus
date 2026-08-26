M = 5003
# closed form check vs recurrence
def by_rec(N):
    s = {1:27, 2:123}
    for n in range(3, N+1):
        s[n] = (9*s[n-1] - 20*s[n-2]) % M
    return s
def by_cf(n):
    return (3*(pow(4,n,M) + pow(5,n,M))) % M
s = by_rec(600)
assert all(s[n] == by_cf(n) for n in range(1,601)), "closed form mismatch"
hits = [n for n in range(1,601) if s[n] == 1140]
print("hits for 1140:", hits[:20], "count", len(hits))
for n in hits[:5]:
    print(" n=%d f(n)mod5003=%d" % (n, s[n]))
print("sanity samples:", {n: s[n] for n in [1,2,3,4,5,600]})

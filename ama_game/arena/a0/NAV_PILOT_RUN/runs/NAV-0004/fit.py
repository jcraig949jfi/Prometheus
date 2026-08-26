p=2711
v={1:38,2:208,3:1148,4:966}
# f(n+2) = a f(n+1) + b f(n) mod p
det=(v[2]*v[2]-v[1]*v[3])%p
print("det",det)
inv=pow(det,p-2,p)
# [[v2,v1],[v3,v2]] [a,b]^T = [v3,v4]
a=(inv*(v[2]*v[3]-v[1]*v[4]))%p
b=(inv*(v[2]*v[4]-v[3]*v[3]))%p
print("a,b",a,b)
seq={1:v[1],2:v[2]}
for n in range(3,601):
    seq[n]=(a*seq[n-1]+b*seq[n-2])%p
print("check3,4",seq[3],seq[4])
hits=[n for n in range(1,601) if seq[n]==1673]
print("hits",hits[:20],"count",len(hits))
print("f(5..8)",[seq[n] for n in range(5,9)])
print("f(257)",seq[257],"f(600)",seq[600])
# period
per=None
for L in range(1,20000):
    pass

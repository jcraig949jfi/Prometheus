P=4001
S=[33,183,1137,3526,3381,3775,2758,318,1276,2081,2016,465,2324,1472,1925,341,2995,2784,954,3089,2854,3681,882,3537]
# f(n) = 10 f(n-1) - 21 f(n-2); closed form 4*3^n + 3*7^n
f={}
for n in range(1,601):
    f[n]=(4*pow(3,n,P)+3*pow(7,n,P))%P
assert [f[i+1] for i in range(24)]==S, "closed form mismatch"
hits=[n for n in range(1,601) if f[n]==1422]
print("closed form matches all 24 observed samples")
print("hits for 1422:",hits)
for n in hits[:10]: print(n, f[n])
print("f(600)=",f[600],"f(300)=",f[300],"f(457)=",f[457])

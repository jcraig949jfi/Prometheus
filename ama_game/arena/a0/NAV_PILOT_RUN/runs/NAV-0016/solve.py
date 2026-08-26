p=1009
v={1:23,2:133,3:773,4:477,5:219}
# solve a,b : v3 = a v2 + b v1 ; v4 = a v3 + b v2  (mod p)
import itertools
det=(v[2]*v[2]-v[1]*v[3])%p
print("det",det, "inv exists", pow(det,p-2,p)*det%p)
di=pow(det,p-2,p)
a=((v[3]*v[2]-v[1]*v[4])*di)%p
b=((v[2]*v[4]-v[3]*v[3])*di)%p
print("a",a,"b",b)
# verify
print("pred f3",(a*v[2]+b*v[1])%p, v[3])
print("pred f4",(a*v[3]+b*v[2])%p, v[4])
print("pred f5",(a*v[4]+b*v[3])%p, v[5])
f={1:v[1],2:v[2]}
for n in range(3,601):
    f[n]=(a*f[n-1]+b*f[n-2])%p
hits=[n for n in range(1,601) if f[n]==163]
print("hits163",hits)
print("f600",f[600],"f300",f[300],"f123",f[123])

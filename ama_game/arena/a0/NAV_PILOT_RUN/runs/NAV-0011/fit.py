M=4001
v={1:47,2:281,3:1823,4:326,5:986,6:3014}
# solve a*v2+b*v1=v3 ; a*v3+b*v2=v4
import itertools
d=(v[2]*v[2]-v[1]*v[3])%M
print("det",d, "inv exists", pow(d,M-2,M)*d%M)
di=pow(d,M-2,M)
a=((v[3]*v[2]-v[1]*v[4])*di)%M
b=((v[2]*v[4]-v[3]*v[3])*di)%M
print("a,b",a,b)
# verify
seq={1:v[1],2:v[2]}
for n in range(3,7):
    seq[n]=(a*seq[n-1]+b*seq[n-2])%M
print("pred",[seq[n] for n in range(1,7)])
print("obs ",[v[n] for n in range(1,7)])
print("match", all(seq[n]==v[n] for n in range(1,7)))

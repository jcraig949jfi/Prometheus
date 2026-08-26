M=1409
v={1:30,2:156,3:840,4:429,5:1038}
# solve a*v2 + b*v1 = v3 ; a*v3 + b*v2 = v4   (mod M)
det=(v[2]*v[2]-v[3]*v[1])%M
print("det",det,"invertible",pow(det,M-2,M)*det%M==1)
di=pow(det,M-2,M)
a=(v[3]*v[2]-v[4]*v[1])%M*di%M
b=(v[2]*v[4]-v[3]*v[3])%M*di%M
print("a",a,"b",b)
pred5=(a*v[4]+b*v[3])%M
print("predicted f(5)",pred5,"observed",v[5],"MATCH" if pred5==v[5] else "MISMATCH")

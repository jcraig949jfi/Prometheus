M=2711
v={1:18,2:66,3:246,4:930,5:847}
# solve a*f(2)+b*f(1)=f(3); a*f(3)+b*f(2)=f(4)  mod M
import itertools
det=(v[2]*v[2]-v[1]*v[3])%M
print("det",det, "inv-exists", pow(det,M-2,M)*det%M)
di=pow(det,M-2,M)
a=(v[3]*v[2]-v[1]*v[4])%M*di%M
b=(v[2]*v[4]-v[3]*v[3])%M*di%M
print("a,b =",a,b)
# validate on f(5)
print("pred f5",(a*v[4]+b*v[3])%M,"actual",v[5])

P=1409
def order(a,p):
    n=p-1; o=n
    for q in (2,11):
        while o%q==0 and pow(a,o//q,p)==1: o//=q
    return o
print("1409 prime?", all(1409%d for d in range(2,38)))
print("p-1 =",P-1,"= 2^7 * 11")
o2,o5=order(2,P),order(5,P)
print("ord(2)=",o2," ord(5)=",o5)
import math
per=o2*o5//math.gcd(o2,o5)
print("period of f =",per)
f=lambda n:(3*pow(2,n,P)+5*pow(5,n,P))%P
print("f periodic check f(1)==f(1+per):", f(1)==f(1+per), "f(7)==f(7+per):", f(7)==f(7+per))
# exhaustive over one full period -> covers ALL integers n, not just [1,600]
hits=[n for n in range(1,per+1) if f(n)==296]
print("hits over a FULL period (all n):", hits)
print("distinct values attained:", len({f(n) for n in range(1,per+1)}))
print("is 296 attained by the model at any n at all?", 296 in {f(n) for n in range(1,per+1)})

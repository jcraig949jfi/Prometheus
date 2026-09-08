import random
random.seed(7717)
LO,HI=1/3.0,3.0
def var(v):
    m=sum(v)/len(v); return sum((x-m)**2 for x in v)/(len(v)-1)
def rate(n,k,q,draws):
    f=0; s=q**0.5
    for _ in range(draws):
        reg=[random.gauss(0,s) for _ in range(n)]
        pool=[random.gauss(0,1) for _ in range(n*k)]
        vp=var(pool)
        if vp<=0: continue
        r=var(reg)/vp
        if r<LO or r>HI: f+=1
    return f/draws

print("D3 FIRE RATE vs REGION SIZE, k=4, band [0.333, 3.0]")
print("A TEST gains power with n. A FIXED BAND does not.\n")
print("  true ratio   n=8     n=16    n=32    n=64    n=128   direction")
print("  ----------   -----   -----   -----   -----   -----   ---------")
for q in (1.00,1.17,1.50,2.00,2.50,3.00,3.50,4.00,6.00,9.00):
    r=[rate(n,4,q,6000) for n in (8,16,32,64,128)]
    d="-> 0  (INSIDE band)" if q<3.0 else ("-> 1  (OUTSIDE band)" if q>3.0 else "-> 0.5 (AT edge)")
    print("  %10.2f   %5.3f   %5.3f   %5.3f   %5.3f   %5.3f   %s"
          % (q,*r,d))
print("\nThe pivot is the band edge 3.0, not an effect size.")
print("For any true ratio strictly inside [0.333,3.0], MORE DATA -> LESS FIRING.")

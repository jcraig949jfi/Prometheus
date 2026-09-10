import random
random.seed(4242)
LO,HI=1/3.0,3.0
def var(v):
    m=sum(v)/len(v); return sum((x-m)**2 for x in v)/(len(v)-1)
def rate(n,k,q,draws=20000):
    f=0; s=q**0.5
    for _ in range(draws):
        reg=[random.gauss(0,s) for _ in range(n)]
        pool=[random.gauss(0,1) for _ in range(n*k)]
        vp=var(pool)
        if vp<=0: continue
        if not (LO<=var(reg)/vp<=HI): f+=1
    return f/draws

NS=(8,10,12,16,20,24,32,48)
print("D3 DISCRIMINATION = fire(true ratio) - fire(null), k=4")
print("The null collapses with n faster than an inside-band signal does,")
print("so discrimination has an INTERIOR OPTIMUM. Bigger is not better.\n")
hdr="  ratio  " + "".join("%8d" % n for n in NS) + "   best n"
print(hdr); print("  " + "-"*(len(hdr)-2))
null={n:rate(n,4,1.0) for n in NS}
for q in (1.17,1.50,2.00,2.50,3.00,4.00):
    lift={n: rate(n,4,q)-null[n] for n in NS}
    best=max(lift,key=lambda n:lift[n])
    print("  %5.2f  " % q + "".join("%8.3f" % lift[n] for n in NS)
          + "   %5d" % best)
print("\n  null   " + "".join("%8.3f" % null[n] for n in NS))
print("\nrules needed = best n per region; corpus = best n x n_regions")

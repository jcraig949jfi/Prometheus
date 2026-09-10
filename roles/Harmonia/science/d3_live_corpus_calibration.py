import random, math
random.seed(20260910)
LO,HI=1/3.0,3.0
def var(v):
    m=sum(v)/len(v); return sum((x-m)**2 for x in v)/(len(v)-1)

def binom_mean(rng,L):           # score = mean of L bernoulli(1/2) draws
    return sum(rng.random()<0.5 for _ in range(L))/L

def sim(n_region=40,k=4,L=24,between_sd=0.0,draws=20000,pooled_within=False):
    rng=random.Random(7)
    fires=lo=hi=skip=0
    for _ in range(draws):
        # the region under test
        mu_r=rng.gauss(0,between_sd)
        reg=[binom_mean(rng,L)+mu_r for _ in range(n_region)]
        nbs=[]
        for _ in range(k):
            mu=rng.gauss(0,between_sd)
            nbs.append([binom_mean(rng,L)+mu for _ in range(n_region)])
        if pooled_within:                       # df-weighted pooled WITHIN
            num=sum((len(b)-1)*var(b) for b in nbs)
            den=sum(len(b)-1 for b in nbs)
            v_nb=num/den
        else:                                   # d3.v0: variance of the CONCATENATION
            v_nb=var([x for b in nbs for x in b])
        if v_nb<=0: skip+=1; continue
        r=var(reg)/v_nb
        if r<LO: fires+=1; lo+=1
        elif r>HI: fires+=1; hi+=1
    return dict(rate=fires/draws, lower=lo, upper=hi,
                lower_frac=(lo/fires if fires else float('nan')))

print("="*74)
print("D3 ON THE LIVE CORPUS: 30 fires / 77 eligible = 0.390, 28 of 30 LOWER")
print("="*74)
print("  Binomial(L,1/2)/L at the campaign's ACTUAL L. Arms: L=24 (arm-a),")
print("  L=28 (arm-b). Geometry: n_region=40 (the reported median), k=4.\n")

print("A. PURE NULL, region means all EQUAL (between_sd = 0)")
print("   d3.v0 denominator = variance of the CONCATENATED neighbours\n")
print("   L    rate      lower  upper   lower_frac")
print("   --   -------   -----  -----   ----------")
for L in (24,28):
    s=sim(L=L,between_sd=0.0)
    print("   %2d   %.5f   %5d  %5d   %s"%(L,s["rate"],s["lower"],s["upper"],
          "n/a" if s["lower"]+s["upper"]==0 else "%.3f"%s["lower_frac"]))
print("\n   -> a pure null at n=40 fires essentially never (the band-")
print("      concentration result, F-2). So 0.390 is NOT a null rate.")

print("\nB. THE SAME NULL, BUT REGION MEANS DIFFER (authored: each world has its")
print("   own deterministic candidate, so region means differ BY CONSTRUCTION)")
print("   within-region SD at L=24 is %.4f\n"%math.sqrt(0.25/24))
print("   between_sd   rate      lower  upper   lower_frac")
print("   ----------   -------   -----  -----   ----------")
for bsd in (0.0,0.02,0.04,0.06,0.08,0.10,0.15,0.20):
    s=sim(L=24,between_sd=bsd)
    print("   %10.3f   %.5f   %5d  %5d   %s"%(bsd,s["rate"],s["lower"],s["upper"],
          "n/a" if s["lower"]+s["upper"]==0 else "%.3f"%s["lower_frac"]))
print("\n   observed on the live corpus:  rate 0.390   lower_frac 0.933")

print("\nC. THE SAME DATA, DENOMINATOR CORRECTED TO POOLED WITHIN-REGION VARIANCE")
print("   (df-weighted mean of neighbour within-variances; removes the")
print("    between-region component the concatenation smuggles in)\n")
print("   between_sd   rate      lower  upper   lower_frac")
print("   ----------   -------   -----  -----   ----------")
for bsd in (0.0,0.04,0.08,0.15,0.20):
    s=sim(L=24,between_sd=bsd,pooled_within=True)
    print("   %10.3f   %.5f   %5d  %5d   %s"%(bsd,s["rate"],s["lower"],s["upper"],
          "n/a" if s["lower"]+s["upper"]==0 else "%.3f"%s["lower_frac"]))

print("\nD. FLOOR GEOMETRY (8, 32) FOR COMPARISON, pure null, both L")
for L in (24,28):
    s=sim(n_region=8,L=L,between_sd=0.0)
    print("   L=%2d  n=8,pool=32   rate %.4f  (binomial SE %.4f)"
          %(L,s["rate"],math.sqrt(s["rate"]*(1-s["rate"])/20000)))

import random, statistics as st
from math import comb
random.seed(20260908)

BAND=(1/3.0,3.0)
def var(v):
    m=sum(v)/len(v); return sum((x-m)**2 for x in v)/(len(v)-1)
def fires(reg,pool):
    if len(reg)<2 or len(pool)<2: return False
    vp=var(pool)
    if vp<=0: return False
    r=var(reg)/vp
    return r<BAND[0] or r>BAND[1]

# ---- 1. does aggregating 4 repeats to a per-rule mean restore the floor rate?
def sim_agg(n_region,k,reps,draws=20000,sd_b=1.0,sd_w=1.0,ratio_region=1.0):
    f=0
    for _ in range(draws):
        def block(nr,sb):
            # nr rules, each with `reps` repeats: between-rule sd sb, within sd_w
            out=[]
            for _i in range(nr):
                mu=random.gauss(0,sb)
                out.append(sum(random.gauss(mu,sd_w) for _ in range(reps))/reps)
            return out
        reg=block(n_region,sd_b*(ratio_region**0.5))
        pool=[]
        for _ in range(k): pool+=block(n_region,sd_b)
        if fires(reg,pool): f+=1
    return f/draws

print("=== 1. RESTORED CALIBRATION: 8 independent RULES, repeats aggregated ===")
print("   geometry: region 8 rules, k=4 -> pool 32 rules, pure null\n")
for reps in (1,4):
    r=sim_agg(8,4,reps)
    print("   %d repeat(s) per rule, aggregated to mean : %.4f" % (reps,r))
print("   exact F(7,31) tail outside band            : 0.0833")
print("   my measured 8-independent-row rate         : 0.0867")

print("\n=== 2. WHAT 80 RULES BUYS: power vs region size at fixed true ratio ===")
print("   region drawn from a distribution with variance `ratio` x the pool's\n")
print("   rules/region   pool   ratio=1.17  1.50   2.00   3.00   4.00")
print("   ------------   ----   ----------  -----  -----  -----  -----")
for nr in (8,12,16,24,32):
    row=[]
    for q in (1.17,1.5,2.0,3.0,4.0):
        row.append(sim_agg(nr,4,4,draws=8000,ratio_region=q))
    print("   %10d   %4d   %10.3f  %5.3f  %5.3f  %5.3f  %5.3f"
          % (nr,nr*4,*row))

print("\n=== 3. IS 80 RULES ACTUALLY 10 ELIGIBLE REGIONS? ===")
print("   80 rules, 10 regions, floor 8 rules/region\n")
print("   assignment          E[eligible regions]  P(all 10 eligible)")
print("   -----------------   -------------------  ------------------")
print("   balanced by design            10.00              1.000")
T=20000
for total,nreg in ((80,10),(100,10),(120,10),(160,10)):
    elig=0; allel=0
    for _ in range(T):
        c=[0]*nreg
        for _ in range(total): c[random.randrange(nreg)]+=1
        e=sum(1 for x in c if x>=8)
        elig+=e; allel+= (e==nreg)
    print("   random, %3d rules             %5.2f              %.3f"
          % (total,elig/T,allel/T))

import random, itertools, math
from math import comb
random.seed(90808)

print("="*72)
print("A. MINIMUM ATTAINABLE TWO-SIDED PERMUTATION p, BY DESIGN IN FLIGHT")
print("="*72)
print("  A design cannot reject at 0.05 if its own permutation lattice has no")
print("  tail that small. This is checkable BEFORE any data exists.\n")
rows=[
 ("H1 NK trapped-fraction, 3 landscapes/k (v1)","unpaired",3,3),
 ("H1 NK trapped-fraction, 6 landscapes/k (v2.1)","unpaired",6,6),
 ("route (c) k-variance ratio, 6/k","unpaired",6,6),
 ("C3 analysed at the 4 IC SAMPLES (paired)","paired",4,None),
 ("C3 analysed at the IC, 400 paired","paired",400,None),
 ("B3 witness on/off, 3 seeds per arm","unpaired",3,3),
 ("B3 witness on/off, 3 seeds PAIRED by seed","paired",3,None),
 ("B3 witness on/off, 6 seeds per arm","unpaired",6,6),
 ("B3 witness on/off, 6 seeds PAIRED by seed","paired",6,None),
]
print("  %-46s %8s %10s %s" % ("design","lattice","min p","0.05?"))
print("  " + "-"*46 + " " + "-"*8 + " " + "-"*10 + " -----")
for name,kind,a,b in rows:
    if kind=="unpaired":
        L=comb(a+b,a); mp=2.0/L
    else:
        L=2**a if a<=20 else float('inf'); mp=2.0/L if a<=20 else 0.0
    print("  %-46s %8s %10.4g %s"
          % (name,kind,mp,"YES" if mp<=0.05 else "NO  <-- cannot fire"))

print("\n"+"="*72)
print("B. X1-d  REPEATS MUST NOT INFLATE n  (NK, route (c) geometry)")
print("="*72)
print("  Pure null: k has NO effect. Landscapes differ from each other.")
print("  Naive analysis treats each START as independent.\n")
def trial(nl,ns,land_sd=1.0,start_sd=1.0):
    # 2 groups of nl landscapes, ns starts each; group label carries NO effect
    g=[[ [random.gauss(mu,start_sd) for _ in range(ns)]
         for mu in (random.gauss(0,land_sd) for _ in range(nl))] for _ in range(2)]
    return g
def perm_p_units(g,T=2000):
    u=[[sum(l)/len(l) for l in grp] for grp in g]
    obs=abs(sum(u[0])/len(u[0])-sum(u[1])/len(u[1]))
    pool=u[0]+u[1]; n=len(u[0]); c=0
    for _ in range(T):
        random.shuffle(pool)
        if abs(sum(pool[:n])/n-sum(pool[n:])/len(pool[n:]))>=obs-1e-12: c+=1
    return c/T
def perm_p_starts(g,T=2000):
    f=[[x for l in grp for x in l] for grp in g]
    obs=abs(sum(f[0])/len(f[0])-sum(f[1])/len(f[1]))
    pool=f[0]+f[1]; n=len(f[0]); c=0
    for _ in range(T):
        random.shuffle(pool)
        if abs(sum(pool[:n])/n-sum(pool[n:])/len(pool[n:]))>=obs-1e-12: c+=1
    return c/T
for nl,ns in ((6,20),(6,100)):
    fu=fs=0; R=400
    for _ in range(R):
        g=trial(nl,ns)
        if perm_p_units(g,600)<=0.05: fu+=1
        if perm_p_starts(g,600)<=0.05: fs+=1
    print("  %d landscapes/k, %3d starts each" % (nl,ns))
    print("     unit = LANDSCAPE (n=%d)   false positive rate  %.3f" % (nl,fu/R))
    print("     unit = START    (n=%d)   false positive rate  %.3f  <- INVALID"
          % (nl*ns,fs/R))

print("\n"+"="*72)
print("C. C3  WHICH UNIT, FOR WHICH CLAIM")
print("="*72)
p=0.5; n_ic_per_sample=100; n_samples=4; N=n_ic_per_sample*n_samples
se_ic=math.sqrt(p*(1-p)/N)
print("  (i) accuracy of ONE rule, unit = IC, n = %d" % N)
print("      binomial SE %.4f   95%% CI half-width %.4f" % (se_ic,1.96*se_ic))
print("  (i') same claim, unit = IC SAMPLE, n = 4")
print("      t(3) on 4 sample means; SE of a sample mean is %.4f," % math.sqrt(p*(1-p)/n_ic_per_sample))
print("      so the CI half-width is t=3.18 x SE/sqrt(4) = %.4f" % (3.182*math.sqrt(p*(1-p)/n_ic_per_sample)/2))
print("      -> %.1fx WIDER than (i), and C1-e used 16,000 ICs as the unit."
      % ((3.182*math.sqrt(p*(1-p)/n_ic_per_sample)/2)/(1.96*se_ic)))
print("\n  (ii) rule A vs rule B on the SAME ICs: pairing is the whole point")
def mcnemar_vs_unpaired(dA,dB,rho_shared=0.8,T=3000):
    hitp=hitu=0
    for _ in range(T):
        b=c=0; a_c=b_c=0
        for _ in range(N):
            hard=random.random()<rho_shared      # IC difficulty shared
            pa=dA-0.15 if hard else dA+0.15
            pb=dB-0.15 if hard else dB+0.15
            ra=random.random()<max(0,min(1,pa)); rb=random.random()<max(0,min(1,pb))
            a_c+=ra; b_c+=rb
            if ra and not rb: b+=1
            elif rb and not ra: c+=1
        if b+c>0:
            z=(b-c)/math.sqrt(b+c)
            if abs(z)>1.96: hitp+=1
        se=math.sqrt(dA*(1-dA)/N+dB*(1-dB)/N)
        if abs(a_c/N-b_c/N)/se>1.96: hitu+=1
    return hitp/T,hitu/T
for dA,dB,lab in ((0.50,0.50,"null, no true difference"),
                  (0.55,0.50,"true difference 0.05")):
    pp,uu=mcnemar_vs_unpaired(dA,dB)
    print("     %-26s  paired(McNemar) %.3f   unpaired %.3f" % (lab,pp,uu))
print("\n  (iii) a claim about the POPULATION of rules: unit = the RULE")
print("      C3-acq n = 120 rules; C3-hist n = 6 genomes.")
print("      ICs inside a rule add NO independent units to that claim.")

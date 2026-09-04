import numpy as np, sys
src=open("e1_experiment.py").read().replace('if __name__ == "__main__":','if False:')
M__={"__file__":"e1_experiment.py"}
M=M__; exec(compile(src,"e1","exec"), M)
N=M['N']; TAU=M['TAU_MATCH']
rng=np.random.default_rng(1000)
tA=M['make_targets'](rng,"A"); tB=M['make_targets'](rng,"B")
GA,BA=M['evolve'](tA,seed=1); GB,BB=M['evolve'](tB,seed=2)
PA=M['adults'](GA,BA); PB=M['adults'](GB,BB)
print("TAU_MATCH (declared)      = %.4f" % TAU)
print("phenotype |P| mean/max    = %.3f / %.3f" % (np.abs(PA).mean(), np.abs(PA).max()))
print("||P*|| mean               = %.3f" % np.linalg.norm(PA,axis=1).mean())
def nn(X,Y,same):
    D=np.linalg.norm(X[:,None,:]-Y[None,:,:],axis=2)
    if same: np.fill_diagonal(D,np.inf)
    v=D.min(axis=1)
    return D, v
Dw,vw = nn(PA,PA,True)
Dx,vx = nn(PA,PB,False)
for nm,D,v in (("WITHIN A (C0 case)",Dw,vw),("CROSS A-B (E1A case)",Dx,vx)):
    fin=D[np.isfinite(D)]
    print("%-22s min=%.4f  medianNN=%.4f  pairs<=TAU=%d" % (nm, fin.min(), np.median(v), int((fin<=TAU).sum())))
print("within-A pairwise distance percentiles:", np.round(np.percentile(Dw[np.isfinite(Dw)],[1,5,25,50]),3))
print("scale ratio  medianNN_within / TAU = %.1fx" % (np.median(vw)/TAU))

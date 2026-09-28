from h import *
t=json.load(open(D+'th015_out.json'))
K=40; THR=0.8
def rate(T,S,seed):
    rng=random.Random(seed); return sum(P.run(P.graft(T,S,rng))[0] for _ in range(K))/K
for r in t['rows'][::3]:
    T=bytes.fromhex(r['tape']); X=list(r['X']); M=r['M']
    base=rate(T,X,7)
    if base<THR: print(r['epoch'],'X fails',base, flush=True); continue
    S=list(X)
    for p in sorted(X, key=lambda p:(p in M, p)):   # try dropping non-M loci first
        S2=[q for q in S if q!=p]
        if rate(T,S2,7)>=THR and rate(T,S2,8)>=THR: S=S2
    print(r['epoch'],'|M|',len(M),'|X|',len(X),'greedy-min',len(S),'rate',rate(T,S,99),'min-M',sorted(set(S)-set(M)),'M-not-in-min',sorted(set(M)-set(S)), flush=True)

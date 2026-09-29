import math, itertools
# exact H(X_t | X_{t-k..t-1}) for stationary Even process, minus entropy rate 2/3
def seqprob(xs):
    # forward over states with unnormalised mass; start stationary
    m={'A':2/3,'B':1/3}
    for x in xs:
        n={'A':0.0,'B':0.0}
        n['A']+= m['A']*0.5 if x==0 else 0
        if x==1: n['B']+=m['A']*0.5; n['A']+=m['B']
        m=n
    return sum(m.values())
def H(p): return 0 if p in (0,1) else -(p*math.log2(p)+(1-p)*math.log2(1-p))
for k in [0,1,2,3,4,6,8]:
    h=0
    for ctx in itertools.product([0,1],repeat=k):
        pc=seqprob(ctx)
        if pc==0: continue
        p1=seqprob(ctx+(1,))/pc
        h+=pc*H(p1)
    print(k, round(h-2/3,4))

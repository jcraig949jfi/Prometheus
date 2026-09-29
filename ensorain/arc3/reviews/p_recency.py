import sys,time; sys.path.insert(0,'.')
import numpy as np
from ensorain.lm01.families import make_world
from ensorain.lm01.margins import _feed
from ensorain.lm01.arms import BufferALS
t0=time.time()
for sd in (9_700_020,9_700_021,9_700_022):
    w=make_world('F3_switch','L1',sd,gen='pairwise'); c=512
    last=set(np.round(w['train'][-1][1],12)); n=sum(len(s[1]) for s in w['train'])
    # position of each record in stream
    pos={v:i for i,v in enumerate(np.round(np.concatenate([s[1] for s in w['train']]),12))}
    for ev in ('random','keep_worst'):
        a=_feed(BufferALS(w['dims'],3,c//4,evict=ev),w['train'])
        yb=np.round(a.by,12); fr=np.mean([v in last for v in yb]); mp=np.median([pos[v] for v in yb])/n
        print(sd,ev.ljust(10),'frac of buffer from final episode %.2f'%fr,'median stream position %.2f'%mp)
print('elapsed',time.time()-t0)

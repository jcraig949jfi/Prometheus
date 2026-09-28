import sys,time; sys.path.insert(0,'.')
import numpy as np
from ensorain.lm01.families import make_world
from ensorain.lm01.margins import _feed,_build,_ac_cells,_AC
from ensorain.lm01.arms import Selective, LosslessR, BufferALS
from ensorain.lm01.select_arms import HEADLINE_SEL
w=make_world('F3_switch','L1',9_700_001,gen='pairwise')
T,truth=w['tests']['never_seen']
t=time.time()
L=_feed(_build('LOSSLESS','L-R-r2-rec.1',w['dims'],0),w['train']); aL=_AC(_ac_cells(L.predict(T),truth))
print('L-R-r2-rec.1 AC %.3f'%aL, {k:L.meter.as_dict()[k] for k in ('peak_persistent','bytes_read','store_read','ops','replay_ops','wall')}, 'iters',L.meter.als_iters)
for cap in (32,64,128):
    S=_feed(Selective('cp',w['dims'],cap=cap),w['train']); a=_AC(_ac_cells(S.predict(T),truth))
    m=S.meter.as_dict(); print('S-cp cap',cap,'AC %.3f'%a,{k:m[k] for k in ('peak_persistent','bytes_read','ops','wall')}, 'within_budget', m['peak_persistent']<=L.meter.peak_persistent and m['bytes_read']<=L.meter.bytes_read)
B=_feed(BufferALS(w['dims'],3,len(np.concatenate([s[1] for s in w['train']]))),w['train']); B.predict(T)
m=B.meter.as_dict(); print('BufferALS full',{k:m[k] for k in ('peak_persistent','bytes_read','ops','replay_ops','wall')},'n_refits',len(B.als_iters),'iters med',np.median(B.als_iters))
print('elapsed',time.time()-t)

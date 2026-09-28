# Probe: a bounded per-cell (sum, count) table (<= c cells x 16 B) reproduces the L-R headline endpoint (weighted-ALS identity)
import sys; sys.path.insert(0,'.')
import numpy as np
from ensorain.lm01.families import make_world
from ensorain.lm01.margins import _feed,_ac_cells,_AC
from ensorain.lm01.arms import LosslessR, als_lowrank
for fam,lv,gen,sd in (('F2_latent','L3','spectral',9_700_030),('F5_nuisance','L3','tt',9_700_031),('F2_latent','L3','lowrank',9_700_032)):
    w=make_world(fam,lv,sd,gen=gen); T,truth=w['tests']['never_seen' if fam=='F2_latent' else 'ood_never_seen']
    lr=_feed(LosslessR(w['dims'],rank=3),w['train']); p_lr=lr.predict(T)
    A=np.concatenate([s[0] for s in w['train']]); y=np.concatenate([s[1] for s in w['train']])
    u,inv,cnt=np.unique(A,axis=0,return_inverse=True,return_counts=True); inv=inv.ravel()
    sums=np.bincount(inv,weights=y)
    U,V,s=als_lowrank(w['dims'],u,sums/cnt,3,0.1,np.random.default_rng(0),80,None,w=cnt.astype(float),tol=1e-4)
    i=np.ravel_multi_index(T[:,:s].T,w['dims'][:s]); j=np.ravel_multi_index(T[:,s:].T,w['dims'][s:]); p_ss=(U[i]*V[j]).sum(1)
    print(fam,lv,gen,'n',len(y),'cells_stored',len(u),'c',int(np.prod(w['dims'][:3])),'bytes L-R store',len(y)*(2*A.shape[1]+16),'suffstat bytes',len(u)*(2*A.shape[1]+16),
          'AC L-R %.3f  AC suffstat %.3f  max|dpred| %.2e'%(_AC(_ac_cells(p_lr,truth)),_AC(_ac_cells(p_ss,truth)),np.abs(p_lr-p_ss).max()))

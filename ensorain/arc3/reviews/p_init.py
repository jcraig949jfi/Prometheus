# Probe: (a) random-init factor rows that never receive data; (b) residual_reservoir vs random row coverage at c/4
import sys,time; sys.path.insert(0,'.')
import numpy as np
from ensorain.lm01.families import make_world
from ensorain.lm01.margins import _feed,_ac_cells,_AC
from ensorain.lm01.arms import BufferALS, LosslessR
class BZ(BufferALS):
    def __init__(s,*a,**k):
        super().__init__(*a,**k); s.tu=np.zeros(len(s.U),bool); s.tv=np.zeros(len(s.V),bool)
    def _refit(s):
        A=s.bA.astype(int)
        s.tu[np.ravel_multi_index(A[:,:s.s].T,s.dims[:s.s])]=True
        s.tv[np.ravel_multi_index(A[:,s.s:].T,s.dims[s.s:])]=True
        super()._refit()
    def pz(s,Q):
        i=np.ravel_multi_index(Q[:,:s.s].T.astype(int),s.dims[:s.s]); j=np.ravel_multi_index(Q[:,s.s:].T.astype(int),s.dims[s.s:])
        U=s.U*s.tu[:,None]; V=s.V*s.tv[:,None]
        return (U[i]*V[j]).sum(1), (~s.tv[j]).mean(), (~s.tu[i]).mean()
t0=time.time()
for fam,lv,gen in (('F2_latent','L3','lowrank'),('F4_transfer','L3','lowrank')):
  for sd in (9_700_010,9_700_011,9_700_012):
    w=make_world(fam,lv,sd,gen=gen)
    T,truth=w['tests']['never_seen' if fam=='F2_latent' else 'fresh_field']
    ya=np.concatenate([s[1] for s in w['train']]); c=int(np.prod(w['dims']))
    N1=max(_AC(_ac_cells(np.full(len(T),ya.mean()),truth)),_AC(_ac_cells(np.full(len(T),ya[-len(ya)//4:].mean()),truth)))
    out=[]
    for rung,B in (('c/8',c//8),('c/4',c//4)):
        for ev in ('random','residual_reservoir'):
            a=_feed(BZ(w['dims'],3,B,evict=ev),w['train'])
            ac=_AC(_ac_cells(a.predict(T),truth)); pz,fv,fu=a.pz(T); acz=_AC(_ac_cells(pz,truth))
            A=a.bA.astype(int); vj=np.unique(np.ravel_multi_index(A[:,a.s:].T,a.dims[a.s:]))
            out.append(f"{ev[:5]}@{rung}: AC {ac:+.2f} zeroed-untouched {acz:+.2f} testcells_on_untouched_Vrow {fv:.2f} Vrows_in_final_buffer {len(vj)}/{len(a.V)}")
    print(fam,lv,gen,sd,'N1 %.2f'%N1); [print('   ',o) for o in out]
print('elapsed',time.time()-t0)

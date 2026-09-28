# Secondary 6.2 within_budget: SELECTIVE ladder bytes_read vs frozen LOSSLESS bytes_read (analytic from meters; no training)
import json,sys
sys.path.insert(0,'.')
import numpy as np
from ensorain.lm01.select_arms import SELECTIVE_GRID
from ensorain.lm01.arms import Selective
from ensorain.lm01.accounting import nbytes
from ensorain.lm01.families import LEVELS, LIFE_MULT
fz=json.load(open('ensorain/lm01/FROZEN_SELECTION.json'))['choices']
R=json.load(open('ensorain/lm01/dev/margins_reduced_v2.json'))
for k,v in fz.items():
    if R[k].get('frame')!='TESTABLE' or k.startswith('F1'): continue
    f,l,g=k.split('|')
    dims=list(LEVELS[l]['dims'])+([4] if f=='F5_nuisance' else [])
    n=int(round(LEVELS[l]['n_obs']*LIFE_MULT))
    D=len(dims)
    lab=v['LOSSLESS']; rec='rec' in lab
    store_bytes=n*(2*D+8+8)          # A int16, y f64, t i64
    L_read=n*(2*D+8)+(n*8 if rec else 0)   # one predict: records (+timestamps if -rec)
    kind,recipe=dict(SELECTIVE_GRID)[v['SELECTIVE']]
    from ensorain.wtp3.collider import RULE
    passes=(recipe or RULE.get(kind))[2]
    ncalls=sum(-(-len_ // 50) for len_ in ([n] if f!='F3_switch' and f!='F4_transfer' else ([n//3]*3 if f=='F3_switch' else [n-max(20,int(.15*n)), max(20,int(.15*n))])))
    cells=int(np.prod(dims)); cap=max(16,cells//16); rows=[]
    while cap*8<=store_bytes:
        try:
            a=Selective(kind,dims,cap=cap,recipe=recipe)
            pb=nbytes(a.persistent())
            s_read=pb*passes*ncalls+pb
            rows.append((cap,pb,s_read,pb<=store_bytes and s_read<=L_read))
        except ValueError as ex:
            rows.append((cap,None,None,'INCOMPAT'))
        cap*=2
    elig=[r[0] for r in rows if r[3] is True]
    print(k.ljust(24),lab.ljust(13),'L_read',L_read,'S caps(cap,persist,read,elig):',[(r[0],r[2],r[3]) for r in rows],'ELIGIBLE caps:',elig)

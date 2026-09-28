# Dev-row projection: v0.3.2 headline() under WIN_RUNGS (<= c) vs the v0.3.1 set (incl. 2c); also floor status of WIN rungs
import json,os,sys
sys.path.insert(0,'.')
import ensorain.lm01.analysis as A
from ensorain.lm01.margins_reduce_v2 import ci
R=json.load(open('ensorain/lm01/dev/margins_reduced_v2.json'))
H='ensorain/lm01/dev'
res={}
for key,v in R.items():
    if v.get('frame')!='TESTABLE' or key.startswith('F1'): continue
    f=key.split('|')[0]; sub='margins_f5real' if f=='F5_nuisance' else 'margins'
    ok=[r for r in (json.loads(l) for l in open(os.path.join(H,sub,key.replace('|','__')+'.jsonl'))) if r['status']=='OK']
    for r in ok: r['arms']['L-K']={'AC':r['N1']}
    A.WIN_RUNGS=["c/8","c/4","c/2","c"]; h2=A.headline(ok,0.30,True)
    A.WIN_RUNGS=["c/8","c/4","c/2","c","2c"]; h1=A.headline(ok,0.30,True)
    fl={g:(lambda c:None if c is None else round(c['lo'],2))(ci([r['ladder'][f'random|{g}']['AC']-r['N1'] for r in ok])) for g in ['c/8','c/4','c/2','c']}
    print(key.ljust(24),'v032:',h2['label'].ljust(32),'v031-set:',h1['label'].ljust(32),'B*',h2.get('B_star_LR'),'rung-N1 lo',fl)

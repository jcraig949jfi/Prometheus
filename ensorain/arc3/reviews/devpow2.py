import json,os,sys
sys.path.insert(0,'.')
import numpy as np
from ensorain.lm01.margins_reduce_v2 import ci
R=json.load(open('ensorain/lm01/dev/margins_reduced_v2.json'))
H='ensorain/lm01/dev'
fmt=lambda c: 'NA' if c is None else '%+.2f[%+.2f,%+.2f]'%(c['mean'],c['lo'],c['hi'])
for key,v in R.items():
    if v.get('frame')!='TESTABLE': continue
    f=key.split('|')[0]
    sub='margins_f5real' if f=='F5_nuisance' else 'margins'
    ok=[r for r in (json.loads(l) for l in open(os.path.join(H,sub,key.replace('|','__')+'.jsonl'))) if r['status']=='OK']
    L=lambda r,k: r['ladder'][k]['AC']
    lrN1=ci([L(r,'L-R|full')-r['N1'] for r in ok])
    c8N1=ci([L(r,'random|c/8')-r['N1'] for r in ok])
    headroom_c4=ci([L(r,'random|full')-L(r,'random|c/4') for r in ok])
    headroom_c=ci([L(r,'random|full')-L(r,'random|c') for r in ok])
    lrc=ci([L(r,'L-R|full')-L(r,'random|c') for r in ok])
    lossl=[r['arms'].get('LOSSLESS',{}).get('label') for r in ok][0]
    print(key.ljust(24),'LR-N1',fmt(lrN1),'c/8-N1',fmt(c8N1),'room@c/4',fmt(headroom_c4),'room@c',fmt(headroom_c),'LR-c',fmt(lrc), 'medLR %.2f'%np.median([L(r,'L-R|full') for r in ok]), lossl)

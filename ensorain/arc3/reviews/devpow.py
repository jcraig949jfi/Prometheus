import json,os,sys
sys.path.insert(0,'.')
import numpy as np
from ensorain.lm01.margins_reduce_v2 import ci
from ensorain.lm01.analysis import headline, eviction, secondary
R=json.load(open('ensorain/lm01/dev/margins_reduced_v2.json'))
H='ensorain/lm01/dev'
cnt={}
for key,v in R.items():
    if v.get('frame')!='TESTABLE': continue
    f=key.split('|')[0]
    sub='margins_f5real' if f=='F5_nuisance' else 'margins'
    rows=[json.loads(l) for l in open(os.path.join(H,sub,key.replace('|','__')+'.jsonl'))]
    ok=[r for r in rows if r['status']=='OK']
    for r in ok:
        # adapt: dev rows have arms with AC_a; headline needs L-K AC -> absent in dev
        pass
    lr=[r['ladder']['L-R|full']['AC'] for r in ok]
    d={g:ci([r['ladder']['L-R|full']['AC']-r['ladder'][f'random|{g}']['AC'] for r in ok if f'random|{g}' in r['ladder']]) for g in ['c/8','c/4','c/2','c','2c']}
    ev=[k.split('|')[0] for k in ok[0]['ladder'] if not k.startswith(('random|','L-R|'))]
    e=ev[0] if ev else None
    evd={g:ci([r['ladder'][f'{e}|{g}']['AC']-r['ladder'][f'random|{g}']['AC'] for r in ok if f'{e}|{g}' in r['ladder']]) for g in ['c/4','c']} if e else {}
    fmt=lambda c: 'NA' if c is None else '%+.2f[%+.2f,%+.2f]'%(c['mean'],c['lo'],c['hi'])
    print(key.ljust(26),'LR-c/8',fmt(d['c/8']),'LR-2c',fmt(d.get('2c')),'|',e,'c/4',fmt(evd.get('c/4')),'c',fmt(evd.get('c')), 'posctl',v['posctl_pass'])

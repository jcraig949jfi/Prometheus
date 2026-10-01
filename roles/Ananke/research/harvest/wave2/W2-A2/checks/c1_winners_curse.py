"""Held is used for selection (C top-12, D promotion, E top-5) -> is the stored source 'held'
inflated? Compare with independent re-evaluations of the SAME frozen champion on fresh worlds:
(a) wave C same-family transfer (0x7F7F worlds, same physics/env), (b) wave D adjudication
'normal' (0xD0D0 worlds), (c) E transfer at the source N if any."""
import sys, numpy as np, json
sys.path.insert(0, __file__.rsplit("checks",1)[0]+"checks")
from rows import rows
R = rows(); by = {r['cell_id']: r for r in R}
print("(a) C same-family, same-env transfer vs source held")
d=[]
for r in R:
    if r['wave']=='C' and r['kind']=='transfer' and r['env']['family']==r['extra']['source_family'] and 'variant' not in r['extra']:
        s = by[r['extra']['source_cell']]
        same_env = s['env']==r['env'] and s['physics']==r['physics']
        d.append((r['result']['held']['acc']-s['result']['held']['acc']))
        print(f"  {s['cell_id']} {s['env']['family']:5s} src_wave {s['wave']:2s} same_env={same_env} src held {s['result']['held']['acc']:.3f} lo {s['result']['held']['lo99']:.3f} | re-eval {r['result']['held']['acc']:.3f} lo {r['result']['held']['lo99']:.3f} SIG {r['labels']['SIGNAL']}")
d=np.array(d); print(f"  n={len(d)} mean diff {d.mean():+.4f} median {np.median(d):+.4f} n_neg {np.sum(d<0)} n_pos {np.sum(d>0)}")
print("(b) D adjudication normal (fresh 0xD0D0 worlds) vs source held")
d=[]
for r in R:
    if r['kind']=='adjudicate':
        s = by[r['extra']['source_cell']]
        n = r['result']['controls']['normal']['acc']
        d.append(n - s['result']['held']['acc'])
        print(f"  {s['cell_id']} {s['env']['family']:5s} src_wave {s['wave']:2s} held {s['result']['held']['acc']:.3f} -> normal {n:.3f}")
d=np.array(d); print(f"  n={len(d)} mean diff {d.mean():+.4f} n_neg {np.sum(d<0)}")

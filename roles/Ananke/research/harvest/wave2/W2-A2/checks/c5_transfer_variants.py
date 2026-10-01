"""Wave C transfer rows: is the 'variant' a different condition from the source? TRANSFER_SUPPORT as
report.py computes it vs what C1_REPORT says is counted."""
import sys, json, collections
sys.path.insert(0, __file__.rsplit("checks",1)[0]+"checks")
from rows import rows, ROOT
R=rows(); by={r['cell_id']:r for r in R}
S=json.load(open(ROOT/"roles/Ananke/pte/c1_report/summary.json"))
ts=[t for t in S['C_transfer'] if t['TRANSFER_SUPPORT']]
print("report.py TRANSFER_SUPPORT count:", len(ts), collections.Counter((t['from'],t['to'],bool(t['variant'])) for t in ts))
def eff(env):
    f=env['family']; keys={'HOLD':('gap','cue_len','amp','amp_dist','trials','iti'),
      'RELAY':('d','delta','cue_len','amp','trials','iti'),'XOR':('d','delta','cue_len','amp','trials','iti'),
      'MAJ':('d','delta','cue_len','amp','trials','iti','n_maj','flip_p'),'FLIP':('d','delta','cue_len','amp','amp_teacher','trials','block','iti')}[f]
    return {k:env[k] for k in keys}
for r in R:
    if r['wave']=='C' and r['kind']=='transfer' and 'variant' in r['extra']:
        s=by[r['extra']['source_cell']]
        same = eff(s['env'])==eff(r['env'])
        ph_same = s['physics']==r['physics']
        topo=r['physics']['topology']
        print(f"  {r['cell_id'][:8]} {s['env']['family']:5s} src d{s['env']['d']}/dl{s['env']['delta']}/gap{s['env']['gap']} -> variant d{r['env']['d']}/dl{r['env']['delta']} topo {topo:9s} EFFECTIVE_ENV_SAME={same} held {r['result']['held']['acc']:.3f} lo {r['result']['held']['lo99']:.3f} TS={r['result']['held']['lo99']>0.55}")

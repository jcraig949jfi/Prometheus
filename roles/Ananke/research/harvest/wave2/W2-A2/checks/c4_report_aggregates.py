"""Which rows enter which C1 aggregate; P1 track filter; boundary replicate counts; transfer labels."""
import sys, json, collections, numpy as np
sys.path.insert(0, __file__.rsplit("checks",1)[0]+"checks")
from rows import rows, ROOT
R = rows()
V = json.load(open(ROOT/"roles/Ananke/pte/c1_rows/boundaries_verdicts.json"))
print("SUPPORTED verdicts by (family, track, metric, dial, base):")
for v in V:
    if v['label']=='PHASE_BOUNDARY_SUPPORTED':
        print("  ", v['family'], v['track'], v['metric'], v['dial'], v['base'], v['between'], round(v['jump'],3), round(v['se'],3))
p1 = [v for v in V if v['family']=='RELAY' and v['metric']=='plant' and v['dial'] in ('lat_base','loss','delta','d') and v['label']=='PHASE_BOUNDARY_SUPPORTED']
print("P1 qualifying (report.py filter):", [(v['track'], v['dial']) for v in p1], " phys-only:", [(v['track'],v['dial']) for v in p1 if v['track']=='phys'])
# replicate counts per transect level
for w in ("B","B2"):
    g = collections.defaultdict(lambda: collections.Counter())
    for r in R:
        if r['wave']!=w: continue
        e=r['extra']; g[(r['env']['family'], e['transect'], e['base'], e.get('track'), r['kind'])][e['level_index']]+=1
    bad = {k: dict(v) for k,v in g.items() if min(v.values())<3}
    print(w, "transects", len(g), "with a level <3 reps:", len(bad), list(bad.items())[:4])
# transfer rows: labels written by classify on a kind that has no twin / eligibility
T=[r for r in R if r['kind']=='transfer']
c=collections.Counter((r['wave'], r['labels']['SIGNAL'], r['labels']['REACH_BEYOND_HOP'], 'twin' in r['result'], 'plant' in r['result']) for r in T)
print("transfer rows (wave, SIGNAL, REACH_BEYOND_HOP, has_twin, has_plant):", sorted(c.items()))
# any label vocabulary 'NULL' or eligibility in code output?
print("rows with a NULL / INCONCLUSIVE label key:", sum(1 for r in R if any(k in (r.get('labels') or {}) for k in ('NULL','INCONCLUSIVE'))))
# XOR transfers reaching SIGNAL (would be an 'XOR cell reaching SIGNAL' outside P3's EV filter)
print("XOR transfer rows SIGNAL:", [(r['cell_id'][:8], r['result']['held']['lo99']) for r in T if r['env']['family']=='XOR' and r['labels']['SIGNAL']])
# evolve counts per family all waves (C1_REPORT L3 line)
EV=[r for r in R if r['kind']=='evolve']
for fam in ("RELAY","MAJ","HOLD","XOR","FLIP"):
    rs=[r for r in EV if r['env']['family']==fam]
    print(f"  {fam}: SIGNAL {sum(r['labels']['SIGNAL'] for r in rs)}/{len(rs)}; A1 COMM_DEP {sum(r['labels']['COMM_DEPENDENT'] for r in rs if r['wave']=='A')}")
print("A1 COMM_DEPENDENT", sum(r['labels']['COMM_DEPENDENT'] for r in EV if r['wave']=='A'), "/", sum(1 for r in EV if r['wave']=='A'))
# stored labels vs recomputed classify (report recomputes)
sys.path.insert(0,str(ROOT))
import os; os.environ["CUDA_VISIBLE_DEVICES"]="-1"
from prometheus.ananke import campaign as C
fz=json.load(open(ROOT/"roles/Ananke/pte/FREEZE_PTE_C1.json"))["config"]
cfg=C.CampaignConfig(**{k:(tuple(v) if k in ("families","e_sizes") else v) for k,v in fz.items()})
mism=[r['cell_id'] for r in R if 'labels' in r and C.classify(r,cfg)!=r['labels']]
print("stored labels != recomputed classify:", len(mism))
print("freeze cfg == default cfg:", cfg==C.CampaignConfig())

"""Selection-to-ruler coupling. Fitness = acc + .10*max(sens_act,0) + .02*sens_any (search.py:332).
sens_any = frac of sites whose state differs between MIRROR twins, all ticks (assays.py:76-85).
Twin assay ruler (assays.py:233-302) measures reach/div_frac/persist of a ONE-CUE twin divergence.
Question: in cells where accuracy never rose (non-SIGNAL), did the GA climb sens_any / contrast,
and do the twin-based labels/flags (REACH_BEYOND_HOP, MEMORY_WITHOUT_USE) concentrate there?"""
import sys, numpy as np, collections
sys.path.insert(0, __file__.rsplit("checks",1)[0]+"checks")
from rows import rows
R = [r for r in rows() if r['kind']=='evolve']
def g(r, gen): return r['result']['curve'][gen]
for fam in ("RELAY","XOR","MAJ","FLIP","HOLD"):
    rs=[r for r in R if r['env']['family']==fam]
    for lab in (True, False):
        s=[r for r in rs if r['labels']['SIGNAL']==lab]
        if not s: continue
        a0=np.array([g(r,0)['mean_sens_any'] for r in s]); a1=np.array([g(r,-1)['mean_sens_any'] for r in s])
        c0=np.array([g(r,0)['max_contrast'] for r in s]); c1=np.array([g(r,-1)['max_contrast'] for r in s])
        m0=np.array([g(r,0)['max_acc'] for r in s]); m1=np.array([g(r,-1)['max_acc'] for r in s])
        bf=np.array([g(r,-1)['best_fit']-g(r,-1)['best_acc'] for r in s])
        rbh=np.mean([r['labels']['REACH_BEYOND_HOP'] for r in s]); mwu=np.mean(['MEMORY_WITHOUT_USE' in r['anomalies'] for r in s])
        tw=np.array([r['result']['twin'].get('div_frac_readout',np.nan) for r in s])
        print(f"{fam:5s} SIGNAL={lab!s:5s} n={len(s):3d} pop mean_sens_any gen0 {a0.mean():.3f} -> last {a1.mean():.3f} (up in {np.mean(a1>a0):.2f}); "
              f"max_contrast {c0.mean():.3f}->{c1.mean():.3f}; max_acc {m0.mean():.3f}->{m1.mean():.3f}; best bonus {bf.mean():.3f}; "
              f"champ twin div_frac_ro {np.nanmean(tw):.3f}; REACH_BEYOND_HOP {rbh:.2f}; MEM_WITHOUT_USE {mwu:.2f}")

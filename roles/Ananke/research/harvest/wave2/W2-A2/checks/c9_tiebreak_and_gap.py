"""(a) Champion = argmax(final-train acc) with np.argmax first-index tie-break (search.py:362); the
final population is ordered elites-first by SHAPED fitness (search.py:351). How often is the champion's
final-train accuracy the population max by a tie that the shaped order decides? Proxy from rows:
champ_train_final == 0.5 exactly (all genomes <= 0.5 -> ties among chance genomes) and
champ_train_final < pop mean + tiny. (b) TRAIN_HELD_GAP flag vs expected winner's curse.
(c) Spearman across non-SIGNAL rows: final pop mean_sens_any vs champion twin div_frac/persist."""
import sys, numpy as np, collections
sys.path.insert(0, __file__.rsplit("checks",1)[0]+"checks")
from rows import rows
R=[r for r in rows() if r['kind']=='evolve']
c=collections.Counter()
for r in R:
    t=r['result']['champ_train_final']
    c[(r['labels']['SIGNAL'], 'train==0.5' if t==0.5 else ('train<=0.5' if t<0.5 else 'train>0.5'))]+=1
print("champion final-train accuracy:", dict(c))
gap=collections.Counter((r['labels']['SIGNAL'],'TRAIN_HELD_GAP' in r['anomalies']) for r in R)
print("TRAIN_HELD_GAP by SIGNAL:", dict(gap))
d=np.array([r['result']['champ_train_final']-r['result']['held']['acc'] for r in R if not r['labels']['SIGNAL']])
print("non-SIGNAL train_final - held: mean %.3f, q90 %.3f, max %.3f"%(d.mean(), np.quantile(d,.9), d.max()))
def rank(x): return np.argsort(np.argsort(x))
for fam in ("RELAY","MAJ","FLIP","XOR","HOLD"):
    s=[r for r in R if r['env']['family']==fam and not r['labels']['SIGNAL']]
    a=np.array([r['result']['curve'][-1]['mean_sens_any'] for r in s])
    for k in ('div_frac_readout','persist','reach'):
        b=np.array([r['result']['twin'][k] for r in s])
        rho=np.corrcoef(rank(a),rank(b))[0,1]
        print(f"  {fam} n={len(s)} spearman(final pop mean_sens_any, champ twin {k}) = {rho:+.2f}")

# M1 Sweep Orders — Megethos-Zeroed TT-Cross
## The only surviving metric. Run it on everything.

Pull latest. The code is ready.

---

## THE SWEEP

For every domain pair, zero out feature 0 (Megethos) in both domains, then run TT-Cross. Only report bonds with rank > 1.

```python
import torch, tntorch as tn
from harmonia.src.domain_index import DOMAIN_LOADERS, DomainIndex
from harmonia.src.coupling import CouplingScorer
from harmonia.src.validate import validate_bond
from itertools import combinations
from concurrent.futures import ThreadPoolExecutor, as_completed

SKIP = {'knots', 'maass', 'battery', 'dissection', 'metabolism',
        'codata', 'pdg_particles', 'belyi', 'bridges'}
live = [d for d in DOMAIN_LOADERS.keys() if d not in SKIP]

def test_pair_megethos_zeroed(d1_name, d2_name, subsample=2000):
    d1 = DOMAIN_LOADERS[d1_name]()
    d2 = DOMAIN_LOADERS[d2_name]()
    n1 = min(d1.n_objects, subsample)
    n2 = min(d2.n_objects, subsample)
    
    # ZERO OUT MEGETHOS
    f1 = d1.features[:n1].clone()
    f2 = d2.features[:n2].clone()
    f1[:, 0] = 0.0
    f2[:, 0] = 0.0
    
    scorer = CouplingScorer([
        DomainIndex(d1_name, d1.labels[:n1], f1),
        DomainIndex(d2_name, d2.labels[:n2], f2),
    ])
    grids = [torch.arange(n1, dtype=torch.float32),
             torch.arange(n2, dtype=torch.float32)]
    
    def vf(*indices):
        return scorer(*[idx.long() for idx in indices])
    
    tt = tn.cross(function=vf, domain=grids, eps=1e-3, rmax=15, max_iter=50)
    rank = tt.ranks_tt[1].item()
    
    # Validate
    dom_list = [DomainIndex(d1_name, d1.labels[:n1], f1),
                DomainIndex(d2_name, d2.labels[:n2], f2)]
    vr = validate_bond(tt, 0, dom_list, run_battery=False)
    
    return d1_name, d2_name, rank, vr.validated_rank

# Run all pairs
pairs = list(combinations(live, 2))
print(f'{len(pairs)} pairs, Megethos zeroed')

results = []
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(test_pair_megethos_zeroed, a, b): (a,b) for a,b in pairs}
    for f in as_completed(futs):
        d1, d2, raw, val = f.result()
        if val > 1:
            print(f'  {d1:>20} <-> {d2:<20}: raw={raw} validated={val}')
        results.append((d1, d2, raw, val))

# Save
import json
with open('harmonia/results/megethos_zeroed_sweep.json', 'w') as f:
    json.dump([{'d1': r[0], 'd2': r[1], 'raw': r[2], 'validated': r[3]} for r in results], f, indent=2)
```

Report ONLY bonds with validated rank > 1. Everything else is noise or Megethos.

---

## WHAT TO LOOK FOR

Bonds that survive Megethos zeroing are structure in the NON-magnitude features: rank, torsion, symmetry, spectral, polynomial coefficients. These are the candidates for genuine cross-domain structure.

If a bond has validated rank > 2 after Megethos zeroing, immediately run F33-F38 on it.

---

## ALSO RUN

After the sweep, take the top 5 surviving bonds and run them through your `test_new_bridges.py` (which has F33-F37 built in). This is the full kill chain: Megethos zeroed → TT-Cross → F33-F38.

Anything that survives all of that is real. Report it immediately.

"""W2-X check of P-3 / E-W10: do the 40 'flat' NULL runs (zero population accuracy variance in all 36
generations, so selection is on the w_any bonus alone) carry the labels E-W10 attributes to w_any?
Compares flat vs non-flat comm-family NULL evolve rows. Reads C1 rows only."""
import gzip, json, numpy as np, collections
rows = [json.loads(l) for l in gzip.open('../../../../pte/c1_rows/cells.jsonl.gz', 'rt') if l.strip()]
ev = [r for r in rows if r['kind'] == 'evolve' and r['env']['family'] in ('RELAY', 'XOR', 'MAJ', 'FLIP')
      and r['result']['held']['lo99'] <= 0.55]
def flat(r): return all(g['max_acc'] - g['mean_acc'] <= 1e-12 for g in r['result']['curve'])
out = collections.defaultdict(lambda: collections.Counter())
pers = collections.defaultdict(list); bh = collections.defaultdict(list)
for r in ev:
    k = 'flat' if flat(r) else 'nonflat'
    out[k]['n'] += 1
    out[k]['MWU'] += 'MEMORY_WITHOUT_USE' in (r.get('anomalies') or [])
    out[k]['REACH'] += bool(r['labels'].get('REACH_BEYOND_HOP'))
    tw = r['result'].get('twin', {})
    pers[k].append(tw.get('persist', np.nan)); bh[k].append(tw.get('beyond_hop', np.nan))
    out[k]['champ_train_.5'] += abs(r['result']['champ_train_final'] - 0.5) < 1e-12 if isinstance(r['result']['champ_train_final'], float) else 0
for k in out:
    print(k, dict(out[k]), 'persist median', np.nanmedian(pers[k]), 'beyond_hop median', np.nanmedian(bh[k]))
print('twin keys', list(ev[0]['result']['twin'].keys())[:20])

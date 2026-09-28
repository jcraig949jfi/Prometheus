"""Why do some tape-anchored copiers fail with a BLANK partner? Per failing genome (home layout, fresh),
report which GP11 criterion fails with a blank victim (C2 fidelity / C4 authorship / C5 control), and the
number of zero bytes in the genome. -> diag_blank.json"""
import json, random, collections, pathlib, selfloc, corpus_analysis as ca, p11
HERE = pathlib.Path(__file__).resolve().parent
d = json.load(open(HERE / 'selfloc_results.json'))
G = [g for g in d['genomes'] if g['rates']['REF'] >= 0.5]
fail = [g for g in G if g['rates']['P_BLANK'] < 0.5]
ok = [g for g in G if g['rates']['P_BLANK'] >= 0.5]
agg = collections.Counter(); rows = []
for g in fail:
    world, rr = ca.env(g['vm'], g['cell']); z8 = world.z8
    b = bytes.fromhex(g['hex']); h = g['home']
    spec = selfloc.conditions(h)['P_BLANK']
    kw = dict(z8=z8, T=128, n=64, donor=b, d_off=spec['d_off'], v_off=spec['v_off'], vb=bytes(64),
              donor_first=spec['donor_first'], dsense=spec['dsense'], vsense=spec['vsense'], dstate=selfloc.FRESH,
              budget=rr.t['slice'], ops=rr._ops_mask(), cmr=rr.copy_mut, entry=0, v_exec=True)
    c = collections.Counter()
    for i in range(12):
        tape, prov = selfloc._run_once(rng=random.Random(i), **kw)
        fin = bytes(tape[(spec['v_off'] + j) % 128] for j in range(64))
        D = [j for j in range(64) if b[j] != 0 and fin[j] == b[j]]
        auth = sum(prov[(spec['v_off'] + j) % 128] == 1 for j in D)
        td, _ = selfloc._run_once(rng=random.Random(i), disabled=True, **kw)
        fdis = p11.fidelity(b, bytes(td[(spec['v_off'] + j) % 128] for j in range(64)))
        c['C2'] += p11.fidelity(b, fin) >= .9; c['C4'] += bool(D) and auth / len(D) >= .9; c['C5'] += fdis < .9
    key = tuple(k for k in ('C2', 'C4', 'C5') if c[k] < 6)
    agg[key] += 1
    rows.append({'hex': g['hex'][:16], 'home': h, 'zeros': b.count(0), 'failing': key, 'fdis_last': round(fdis, 2)})
res = {'n_fail': len(fail), 'failing_criteria': {str(k): v for k, v in agg.items()},
       'median_zero_bytes_fail': sorted(r['zeros'] for r in rows)[len(rows) // 2],
       'median_zero_bytes_ok': sorted(bytes.fromhex(g['hex']).count(0) for g in ok)[len(ok) // 2], 'rows': rows}
(HERE / 'diag_blank.json').write_text(json.dumps(res, indent=1))
print({k: v for k, v in res.items() if k != 'rows'})

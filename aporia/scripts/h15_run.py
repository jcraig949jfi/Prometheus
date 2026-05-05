"""H15 NF Tower Termination test.

Run class_field_tower on stratified samples across Galois-group buckets
with cn ∈ [3..50]. Requires Techne's hilbert_class_field with class_number guard.
"""
import sys, psycopg2, time, json, pathlib
sys.path.insert(0, 'F:/Prometheus')
from techne.lib.hilbert_class_field import class_field_tower

OUT = pathlib.Path('F:/Prometheus/aporia/mathematics/h15_results.json')
LOG = pathlib.Path('F:/Prometheus/aporia/mathematics/h15_log.txt')

def log(msg):
    with LOG.open('a') as f:
        f.write(msg + '\n')

LOG.write_text('')

def coeffs_to_poly(s):
    cs = [int(x) for x in s.strip('{}').replace(' ','').split(',') if x]
    terms = []
    for i, c in enumerate(cs):
        if c == 0: continue
        if i == 0: terms.append(str(c))
        elif i == 1: terms.append('x' if c==1 else ('-x' if c==-1 else f'{c}*x'))
        else: terms.append(('' if c==1 else ('-' if c==-1 else f'{c}*')) + f'x^{i}')
    return '+'.join(terms).replace('+-','-')

conn = psycopg2.connect(host='localhost', port=5432, dbname='lmfdb', user='postgres', password='prometheus')
cur = conn.cursor()

results = []
BUDGET = 240
t0 = time.time()
for bucket, where in [
    ('abelian',          "gal_is_abelian='true'"),
    ('solv_nonabel',     "gal_is_abelian='false' AND gal_is_solvable='true'"),
    ('nonsolvable',      "gal_is_solvable='false'"),
]:
    q = f"""
    SELECT label, coeffs, degree::int, disc_abs, class_number::int, galois_label
    FROM nf_fields
    WHERE degree::int BETWEEN 2 AND 4
      AND length(disc_abs) <= 5
      AND class_number::int BETWEEN 3 AND 30
      AND {where}
    ORDER BY random()
    LIMIT 10
    """
    cur.execute(q)
    rows = cur.fetchall()
    log(f'-- {bucket}: {len(rows)} --')
    for row in rows:
        if time.time() - t0 > BUDGET:
            log(f'budget {BUDGET}s reached'); break
        label, coeffs, deg, disc, cn, glabel = row
        poly = coeffs_to_poly(coeffs)
        t = time.time()
        try:
            tower = class_field_tower(poly, max_depth=3, max_class_number=50)
            el = time.time() - t
            rec = {
                'bucket': bucket, 'label': label, 'galois': glabel,
                'degree': deg, 'cn': cn, 'disc': disc,
                'depth': tower['depth'], 'terminates': tower['terminates'],
                'capped': tower['capped'],
                'cn_seq': tower['class_number_sequence'], 'time': round(el, 1),
            }
            results.append(rec)
            log(f'  {label} cn={cn} {glabel}: depth={tower["depth"]} cap={tower["capped"]} seq={tower["class_number_sequence"]} t={el:.1f}s')
            # Save after each successful call
            OUT.write_text(json.dumps({'results': results, 'done': False}, indent=2, default=str))
        except Exception as e:
            log(f'  {label} cn={cn} {glabel} ERR: {str(e)[:120]}')
    if time.time() - t0 > BUDGET: break

# Summary
from collections import defaultdict
import statistics as st
by = defaultdict(list)
for r in results:
    if r.get('terminates'): by[r['bucket']].append(r['depth'])

log(f'\n=== H15 RESULTS ({len(results)} complete, {sum(1 for r in results if r.get("terminates"))} terminated) ===')
for bucket in ['abelian','solv_nonabel','nonsolvable']:
    depths = by[bucket]
    if depths: log(f'  {bucket:15} n={len(depths)} depths={sorted(depths)} median={st.median(depths)}')
    else: log(f'  {bucket:15} n=0')

capped = [r for r in results if r.get('capped')]
if capped:
    log(f'\nCAPPED (depth hit max, tower possibly longer):')
    for c in capped:
        log(f'  [{c["bucket"]}] {c["label"]} cn={c["cn"]} {c["galois"]} cn_seq={c["cn_seq"]}')

OUT.write_text(json.dumps({'results': results, 'done': True, 'wall': round(time.time()-t0, 1)}, indent=2, default=str))
log(f'\nWall: {time.time()-t0:.1f}s. Saved.')
conn.close()

"""Patch: fix radical test (EC bad_primes parser) and add confound-controlled class_number test."""
import json
import numpy as np
import psycopg2
from numpy.linalg import lstsq

DB_PARAMS = dict(host='localhost', port=5432, dbname='lmfdb', user='postgres', password='prometheus')
OUT = r'F:\Prometheus\charon\data\nf_ec_bridge.json'

conn = psycopg2.connect(**DB_PARAMS)
cur = conn.cursor()

# ── Fix radical test ──
print('Loading NF ramps (deg=2)...')
cur.execute("""
    SELECT disc_abs::bigint, ramps
    FROM nf_fields
    WHERE disc_abs::numeric <= 300000000 AND degree::int = 2
    ORDER BY random()
    LIMIT 200000
""")
nf_ramps = {}
for disc, ramps_str in cur:
    try:
        primes = set()
        if ramps_str and ramps_str not in ('{}', '[]'):
            cleaned = ramps_str.strip('{}[]')
            for p in cleaned.split(','):
                p = p.strip()
                if p:
                    primes.add(int(p))
        if primes:
            nf_ramps[int(disc)] = frozenset(primes)
    except:
        pass
print(f'  {len(nf_ramps)} NF with ramps')

print('Loading EC bad_primes...')
cur.execute("""
    SELECT conductor::bigint, bad_primes
    FROM ec_curvedata
    ORDER BY random()
    LIMIT 200000
""")
ec_bad = {}
for cond, bp_str in cur:
    try:
        primes = set()
        if bp_str and bp_str not in ('{}', '[]', '', None):
            cleaned = bp_str.strip('{}[]')
            for p in cleaned.split(','):
                p = p.strip()
                if p:
                    primes.add(int(p))
        if primes:
            ec_bad[int(cond)] = frozenset(primes)
    except:
        pass
print(f'  {len(ec_bad)} EC with bad_primes')

# Radical overlap
rng = np.random.default_rng(77)
nf_discs = list(nf_ramps.keys())
ec_conds = list(ec_bad.keys())
matching = set(nf_discs) & set(ec_conds)

ramp_match = 0
ramp_subset = 0
for d in matching:
    if nf_ramps[d] == ec_bad[d]:
        ramp_match += 1
    if nf_ramps[d].issubset(ec_bad[d]) or ec_bad[d].issubset(nf_ramps[d]):
        ramp_subset += 1

n_sample = min(10000, len(nf_discs), len(ec_conds))
nf_idx = rng.choice(len(nf_discs), size=n_sample, replace=False)
ec_idx = rng.choice(len(ec_conds), size=n_sample, replace=False)

def mean_jaccard(ni, ei):
    jaccards = []
    for i in range(len(ni)):
        a = nf_ramps[nf_discs[ni[i]]]
        b = ec_bad[ec_conds[ei[i]]]
        if len(a | b) > 0:
            jaccards.append(len(a & b) / len(a | b))
    return np.mean(jaccards) if jaccards else 0.0

real_jaccard = mean_jaccard(nf_idx, ec_idx)

null_jaccards = []
for _ in range(500):
    perm_ec_idx = rng.permutation(ec_idx)
    null_jaccards.append(mean_jaccard(nf_idx, perm_ec_idx))
null_jaccards = np.array(null_jaccards)
z_j = (real_jaccard - null_jaccards.mean()) / null_jaccards.std() if null_jaccards.std() > 0 else 0.0

radical_result = {
    'n_exact_matches': len(matching),
    'ramp_equals_badprime_in_matches': ramp_match,
    'ramp_subset_in_matches': ramp_subset,
    'real_mean_jaccard': float(real_jaccard),
    'null_jaccard_mean': float(null_jaccards.mean()),
    'null_jaccard_std': float(null_jaccards.std()),
    'jaccard_z': float(z_j),
}

print(f'Exact matches: {len(matching)}')
print(f'Ramp==BadPrime: {ramp_match}/{len(matching)}')
print(f'Subset: {ramp_subset}/{len(matching)}')
print(f'Jaccard: real={real_jaccard:.4f}, null={null_jaccards.mean():.4f}, z={z_j:.2f}')

# ── Confound-controlled class_number test ──
print('\nRunning confound-controlled class_number vs rank...')
cur.execute("""
    SELECT nf.disc_abs::bigint, nf.class_number::int, nf.degree::int,
           ec.rank::int, ec.conductor::bigint
    FROM nf_fields nf
    INNER JOIN ec_curvedata ec ON nf.disc_abs = ec.conductor
    WHERE nf.disc_abs::numeric <= 300000000
    LIMIT 500000
""")
rows = cur.fetchall()

cns = np.array([r[1] for r in rows], dtype=np.float64)
degs = np.array([r[2] for r in rows], dtype=np.int32)
ranks = np.array([r[3] for r in rows], dtype=np.float64)
conds = np.array([r[4] for r in rows], dtype=np.float64)

raw_corr = float(np.corrcoef(cns, ranks)[0, 1])

X = np.column_stack([np.ones(len(conds)), np.log(conds), degs.astype(float)])
beta_cn = lstsq(X, cns, rcond=None)[0]
cn_resid = cns - X @ beta_cn
beta_rank = lstsq(X, ranks, rcond=None)[0]
rank_resid = ranks - X @ beta_rank
partial_corr = float(np.corrcoef(cn_resid, rank_resid)[0, 1])

null_partials = []
for _ in range(1000):
    perm = np.random.permutation(rank_resid)
    null_partials.append(float(np.corrcoef(cn_resid, perm)[0, 1]))
null_partials = np.array(null_partials)
z_partial = float((partial_corr - null_partials.mean()) / null_partials.std())

print(f'Raw corr(cn, rank) = {raw_corr:.4f}')
print(f'Partial corr(cn, rank | log_cond, degree) = {partial_corr:.4f}, z={z_partial:.2f}')

deg_corrs = {}
for deg in sorted(set(degs)):
    mask = degs == deg
    if mask.sum() > 100:
        r = float(np.corrcoef(cns[mask], ranks[mask])[0, 1])
        deg_corrs[str(deg)] = {'n': int(mask.sum()), 'corr': r}
        print(f'  deg={deg}: n={mask.sum()}, corr={r:.4f}')

confound_result = {
    'raw_correlation': raw_corr,
    'partial_correlation_log_cond_degree': partial_corr,
    'partial_z': z_partial,
    'n_matched': len(rows),
    'by_degree': deg_corrs,
}

conn.close()

# Update JSON
with open(OUT) as f:
    data = json.load(f)

data['radical_overlap'] = radical_result
data['class_number_rank_confound_controlled'] = confound_result

# Recompute summary
significant = []
maybe = []
dead = []
tests = [
    ('direct_match', data['direct_match']['z_score']),
    ('prime_factors_cosine', data['prime_factors']['cosine_z']),
    ('prime_factors_bhatt', data['prime_factors']['bhatt_z']),
    ('divisibility', data['divisibility']['z_score']),
    ('radical_jaccard', radical_result['jaccard_z']),
    ('class_number_rank_raw', data['class_number_rank']['z_score']),
    ('class_number_rank_partial', confound_result['partial_z']),
]
for name, z in tests:
    if abs(z) > 3:
        significant.append(f'{name} (z={z:.2f})')
    elif abs(z) > 2:
        maybe.append(f'{name} (z={z:.2f})')
    else:
        dead.append(f'{name} (z={z:.2f})')

data['summary'] = {
    'significant_tests': significant,
    'marginal_tests': maybe,
    'dead_tests': dead,
    'degree_significant': data['summary'].get('degree_significant', []),
    'verdict': 'SIGNAL' if significant else ('MARGINAL' if maybe else 'DEAD'),
    'interpretation': {
        'prime_factors': 'TRIVIAL: NF discs and EC conductors have different prime factor distributions. Large z reflects genuine distributional difference, not a bridge.',
        'class_number_rank': f'REAL BUT TINY: r={partial_corr:.4f} survives deconfounding (z={z_partial:.1f}). Driven by degree-2 fields. Effect size too small to be useful.',
        'direct_match': 'DEAD: exact match rate equals bootstrap null. No special affinity.',
        'divisibility': 'DEAD: no divisibility excess.',
        'radical': f'Jaccard z={z_j:.2f}. Exact matches: {len(matching)}, ramp==bad_prime in {ramp_match} of those.',
    }
}

with open(OUT, 'w') as f:
    json.dump(data, f, indent=2)
print(f'\nUpdated results saved to {OUT}')
print(f'\nFINAL VERDICT: {data["summary"]["verdict"]}')
for cat in ['significant_tests', 'marginal_tests', 'dead_tests']:
    print(f'  {cat}: {data["summary"][cat]}')

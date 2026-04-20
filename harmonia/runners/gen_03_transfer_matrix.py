"""
gen_03 execution: domain catalog + applicability classification + transfer matrix.
"""
import os, json, datetime as dt
from pathlib import Path
os.environ.setdefault('AGORA_REDIS_HOST', '192.168.1.176')
os.environ.setdefault('AGORA_REDIS_PASSWORD', 'prometheus')
from agora.tensor import projections, projection_meta

projs = projections()

DOMAINS = [
    {'id': 'D_EC', 'name': 'Elliptic curves over Q',
     'data_source': 'lmfdb.ec_curvedata + lmfdb.bsd_joined + lmfdb.lfunc_lfunctions',
     'cardinality': 3824372,
     'fields': ['conductor', 'rank', 'analytic_rank', 'torsion_order', 'cm_disc',
                'root_number', 'regulator', 'sha_order', 'Lhash', 'class_size',
                'nonmax_primes', 'semistable', 'bad_primes', 'kodaira_symbols'],
     'primary_F_IDs': ['F001','F003','F004','F005','F009','F011','F013','F015','F030',
                       'F033','F041a','F042','F043','F044','F045']},
    {'id': 'D_NF', 'name': 'Number fields',
     'data_source': 'lmfdb.nf_fields',
     'cardinality': 22000000,
     'fields': ['degree','disc_abs','signature','galois_label','galois_group',
                'class_number','regulator','ramified_primes','is_galois'],
     'primary_F_IDs': ['F008','F010','F022']},
    {'id': 'D_MF', 'name': 'Classical modular forms (weight, level, character)',
     'data_source': 'lmfdb.mf_newforms + lmfdb.mf_hecke_nf',
     'cardinality': 450000,
     'fields': ['weight','level','character_orbit','hecke_orbit','trace_hash','Lhash',
                'dim','is_cm','is_rm','self_dual','analytic_rank'],
     'primary_F_IDs': ['F001']},
    {'id': 'D_ARTIN', 'name': 'Artin representations',
     'data_source': 'lmfdb.artin_reps',
     'cardinality': 798000,
     'fields': ['Dim','Conductor','GaloisGroup','Indicator','Is_Even','Baselabel','NFGal'],
     'primary_F_IDs': ['F026']},
    {'id': 'D_G2C', 'name': 'Genus-2 curves over Q',
     'data_source': 'lmfdb.g2c_curves',
     'cardinality': 66158,
     'fields': ['cond','disc','aut_grp','geom_aut_grp','torsion_grp','is_simple_geom',
                'st_group','real_period','regulator','sha','mw_rank'],
     'primary_F_IDs': ['F012']},
    {'id': 'D_KNOTS', 'name': 'Knot invariants and polynomials',
     'data_source': 'harmonia/data/knots/ + KnotInfo mirror',
     'cardinality': 12965,
     'fields': ['alexander','jones','HOMFLY','kauffman','signature','genus','mahler_measure'],
     'primary_F_IDs': ['F027','F032']},
    {'id': 'D_L', 'name': 'L-functions (cross-origin, generic)',
     'data_source': 'lmfdb.lfunc_lfunctions',
     'cardinality': 24000000,
     'fields': ['Lhash','origin','rational','gamma_factors','positive_zeros','plot_values'],
     'primary_F_IDs': ['F011','F013','F031']},
]


def classify(pid, pmeta, domain):
    label = pmeta.get('label', '').lower()
    ptype = pmeta.get('type', 'unknown')
    did = domain['id']
    fields = [f.lower() for f in domain['fields']]

    if ptype in ('null_model', 'preprocessing', 'feature_distribution',
                 'magnitude_axis', 'categorical_object_level', 'feature_extraction'):
        if 'gap' in label or 'unfolding' in label:
            if did in ('D_EC', 'D_MF', 'D_L'):
                return ('applies_directly',
                        'zero-spacing / unfolding applies to any L-function family')
            return ('inapplicable', 'no zero-spacing data in this domain')
        if 'mahler' in label:
            if did in ('D_NF', 'D_KNOTS'):
                return ('applies_directly',
                        'Mahler measure is polynomial-native; direct application')
            return ('applies_with_adaptation',
                    'requires associating a polynomial representative')
        if 'lhash' in label or 'trace_hash' in label:
            if did in ('D_L', 'D_MF', 'D_EC'):
                return ('applies_directly',
                        'Lhash/trace_hash native to L-function + source families')
            return ('inapplicable', 'no L-function origin in this domain')
        if 'galois-label' in label or 'galois_label' in label:
            if did in ('D_NF', 'D_ARTIN'):
                return ('applies_directly',
                        'Galois label is a primary field')
            return ('applies_with_adaptation',
                    'requires Galois-structure proxy')
        return ('applies_directly', '{} scorer is domain-agnostic'.format(ptype))

    if ptype == 'stratification':
        key_terms = {
            'conductor': ['conductor', 'cond', 'level'],
            'bad-prime': ['bad_primes', 'ramified_primes'],
            'rank': ['rank', 'mw_rank', 'analytic_rank'],
            'torsion': ['torsion_order', 'torsion_grp'],
            'cm': ['cm_disc', 'is_cm'],
            'semistable': ['semistable'],
            'ade': ['kodaira_symbols'],
            'aut_grp': ['aut_grp', 'geom_aut_grp'],
            'isogeny': ['class_size'],
            'artin': ['Dim', 'GaloisGroup'],
            'katz-sarnak': ['rank'],
            'frobenius-schur': ['Indicator'],
            'character parity': ['character_orbit'],
            'is_even': ['Is_Even'],
            'kodaira': ['kodaira_symbols'],
            'root number': ['root_number', 'analytic_rank', 'rank'],
            'sato-tate': ['st_group', 'cm_disc'],
            'sha': ['sha', 'sha_order'],
            'galois l-image': ['nonmax_primes'],
            'regulator': ['regulator'],
            'modular_degree': ['dim'],
        }
        for term, field_candidates in key_terms.items():
            if term in label:
                if any(fc.lower() in fields for fc in field_candidates):
                    return ('applies_directly',
                            'stratifier field {} present in {}'.format(
                                field_candidates, did))
                return ('inapplicable',
                        'stratifier field {} not in {} schema'.format(
                            field_candidates, did))
        return ('applies_with_adaptation',
                'stratification axis unclear for {}; needs mapping'.format(did))

    return ('applies_with_adaptation',
            'unclassified; default to adapter-needed')


MATRIX = []
for pid in projs:
    pmeta = projection_meta(pid)
    for d in DOMAINS:
        verdict, reason = classify(pid, pmeta, d)
        MATRIX.append({
            'projection_id': pid,
            'projection_type': pmeta.get('type', ''),
            'projection_label': pmeta.get('label', ''),
            'domain_id': d['id'],
            'verdict': verdict,
            'reason': reason,
        })

from collections import Counter
verdict_counts = Counter(m['verdict'] for m in MATRIX)
print('Total (P, D) cells: {} (= {} projections x {} domains)'.format(
    len(MATRIX), len(projs), len(DOMAINS)))
for v, n in verdict_counts.most_common():
    print('  {:28s} {}'.format(v, n))

Path('harmonia/memory').mkdir(exist_ok=True)
with open('harmonia/memory/transfer_matrix.json', 'w', encoding='utf-8') as fh:
    json.dump({'generated_at': dt.datetime.now(dt.timezone.utc).isoformat(),
               'n_projections': len(projs),
               'n_domains': len(DOMAINS),
               'n_cells': len(MATRIX),
               'verdict_counts': dict(verdict_counts),
               'domains': DOMAINS,
               'cells': MATRIX}, fh, indent=2)
print('Wrote harmonia/memory/transfer_matrix.json')

tasks_direct = [c for c in MATRIX if c['verdict'] == 'applies_directly']
# prioritize cross-domain agnostic scorers: preprocessing/null_model/feature_distribution NOT in D_EC
priority_high = [c for c in tasks_direct
                 if c['projection_type'] in ('preprocessing','null_model','feature_distribution')
                 and c['domain_id'] != 'D_EC']
priority_medium = [c for c in tasks_direct if c not in priority_high]
seeded_tasks = priority_high[:30] + priority_medium[:30]

print('Applies-directly cells: {}'.format(len(tasks_direct)))
print('High-priority (non-EC x agnostic-scorer): {}'.format(len(priority_high)))
print('Transfer tasks to seed: {}'.format(len(seeded_tasks)))

with open('harmonia/memory/transfer_tasks_seeded.json', 'w', encoding='utf-8') as fh:
    json.dump({'generated_at': dt.datetime.now(dt.timezone.utc).isoformat(),
               'n_seeded': len(seeded_tasks),
               'high_priority_count': len(priority_high[:30]),
               'tasks': seeded_tasks}, fh, indent=2)
print('Wrote harmonia/memory/transfer_tasks_seeded.json')

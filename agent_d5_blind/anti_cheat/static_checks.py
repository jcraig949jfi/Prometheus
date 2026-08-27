"""Anti-cheat static battery. Spec: constitution section 39.

Seam doctrine: learner-visible data is ALLOWLISTED at field level. The only
learner-visible object is learner_view(task) == {'domain', 'table'}; both hold
pure integers. Anything else (family, seed, gen_meta, witness, strata, oracle
solutions) is oracle-side.

Checks:
 A1 view allowlist: learner_view yields exactly {'domain','table'}, values are
    ints/tuples of ints only (no strings anywhere -> no IDs, labels, names).
 A2 no metadata correlation channel: serialized view contains no generator
    metadata token (checked by construction in A1 — no strings at all).
 A3 source-level boundary: learner/ and navigators/ sources never reference
    oracle-side field names.
 A4 seed-stream discipline: evidence code paths pull seeds from the declared
    streams (audited by grep for hardcoded out-of-stream literals at freeze).
 A5 train/held-out overlap: dev and alien batteries share no (family, seed)
    pair and no identical task table.
"""
import sys, os, re, json

ROOT = os.path.join(os.path.dirname(__file__), '..')
for d in ('task_generators', 'substrate'):
    sys.path.insert(0, os.path.join(ROOT, d))

FORBIDDEN_IN_LEARNER_SOURCES = [
    "gen_meta", "witness", "'family'", '"family"', "stratum", "difficulty",
    "oracle_solutions", "hidden_library", "make_H", "PREDS", "COMBINERS",
]


def _all_ints(x):
    if isinstance(x, int):
        return True
    if isinstance(x, (tuple, list)):
        return all(_all_ints(v) for v in x)
    return False


def check_view_allowlist(tasks):
    from families import learner_view
    for t in tasks:
        v = learner_view(t)
        assert set(v.keys()) == {'domain', 'table'}, f'view keys: {set(v.keys())}'
        assert _all_ints(v['domain']) and _all_ints(v['table']), 'non-integer leak'
    return {'check': 'A1_A2_view_allowlist', 'n_tasks': len(tasks), 'pass': True}


def check_source_boundary():
    hits = []
    for sub in ('navigators', 'learner'):
        d = os.path.join(ROOT, sub)
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if not fn.endswith('.py'):
                continue
            src = open(os.path.join(d, fn), encoding='utf-8').read()
            # strip comments/docstrings before scanning
            code = re.sub(r'""".*?"""', '', src, flags=re.S)
            code = '\n'.join(l.split('#')[0] for l in code.splitlines())
            for tok in FORBIDDEN_IN_LEARNER_SOURCES:
                if tok in code:
                    hits.append((sub + '/' + fn, tok))
    return {'check': 'A3_source_boundary', 'hits': hits, 'pass': not hits}


def check_overlap(dev_tasks, alien_tasks):
    dev_keys = {(t['family'], t['seed']) for t in dev_tasks}
    alien_keys = {(t['family'], t['seed']) for t in alien_tasks}
    dev_tables = {tuple(map(tuple, t['table'])) for t in dev_tasks}
    dup_tables = sum(1 for t in alien_tasks
                     if tuple(map(tuple, t['table'])) in dev_tables)
    return {'check': 'A5_overlap', 'key_overlap': len(dev_keys & alien_keys),
            'table_dups': dup_tables,
            'pass': not (dev_keys & alien_keys) and dup_tables == 0}


def run_all(dev_tasks, alien_tasks, out_path=None):
    results = [check_view_allowlist(dev_tasks + alien_tasks),
               check_source_boundary(),
               check_overlap(dev_tasks, alien_tasks)]
    report = {'all_pass': all(r['pass'] for r in results), 'results': results}
    if out_path:
        json.dump(report, open(out_path, 'w'), indent=1)
    return report


if __name__ == '__main__':
    from families import gen_task
    dev = [gen_task(f, s) for f in ('F1', 'F2', 'F3', 'F4', 'CTRL')
           for s in range(1100, 1110)]
    alien = [gen_task('ALIEN', s) for s in range(1100, 1110)]
    rep = run_all(dev, alien)
    print(json.dumps(rep, indent=1))
    assert rep['all_pass'], 'ANTI-CHEAT FAILURE'
    print('ANTI-CHEAT STATIC BATTERY PASS (engineering sample)')

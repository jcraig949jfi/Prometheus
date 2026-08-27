"""Compose and freeze the evidence task battery. Spec: PREREG-TASKS s6/s10.

Dev battery (seeds 3000+): F1 x12 (EASY4/MED4/HARD3/VH1), F3 x10 (EASY2/MED5/
HARD3), F4 x12 (EASY4/MED5/HARD3), F2 x8 (HARD2/VH6), CTRL x10, NEGX x6 = 58.
Alien battery (seeds 6000+): ALIEN x20, natural draw.

Trivial rejection (constitution s19, frozen rule): a candidate is rejected if
the frozen comparator M0c-RX with probe seed (7*seed+13) at budget 2000 finds
a solution within 32 evaluations (the first population) — the 'short obvious
program' band. Rejection uses engineering-side machinery, applied
deterministically, before any evidence run.

Sequence order: frozen shuffle Random(31337) over the dev battery.
Outputs: task_manifest.json, oracle_solutions.jsonl, reachability_rows.jsonl,
task_difficulty.json.
"""
import sys, os, json, random
HERE = os.path.dirname(__file__)
for d in ('.', '..\\substrate', '..\\mutation', '..\\exact_oracle',
          '..\\reachability_oracle', '..\\navigators'):
    sys.path.insert(0, os.path.join(HERE, d))
from families import gen_task
from battery import stratum
from oracle import solves
from reachability import classify
from m0 import M0_SUITE

RESULTS = os.path.join(HERE, '..', 'results')

DEV_QUOTAS = {
    'F1': {'EASY': 4, 'MEDIUM': 4, 'HARD': 3, 'VERY_HARD': 1},
    'F3': {'EASY': 2, 'MEDIUM': 5, 'HARD': 3},
    'F4': {'EASY': 4, 'MEDIUM': 5, 'HARD': 3},
    'F2': {'HARD': 2, 'VERY_HARD': 6},
    'CTRL': None,   # natural draw, 10
    'NEGX': None,   # natural draw, 6
}
DEV_COUNTS = {'F1': 12, 'F3': 10, 'F4': 12, 'F2': 8, 'CTRL': 10, 'NEGX': 6}
ALIEN_COUNT = 20


def trivial(task):
    r = M0_SUITE['M0c-RX'](task, random.Random(7 * task['seed'] + 13), 2000)
    return r['first_solve'] is not None and r['first_solve'] <= 32


def fill(family, count, quotas, seed_base, max_scan=3000):
    got, tasks, rejected = {}, [], 0
    for off in range(max_scan):
        if len(tasks) >= count:
            break
        t = gen_task(family, seed_base + off)
        st = stratum(t)
        if quotas is not None:
            if got.get(st, 0) >= quotas.get(st, 0):
                continue
        if trivial(t):
            rejected += 1
            continue
        got[st] = got.get(st, 0) + 1
        tasks.append(t)
    assert len(tasks) == count, f'{family}: {len(tasks)}/{count}'
    return tasks, rejected


def main():
    dev, rej_log = [], {}
    for fam, count in DEV_COUNTS.items():
        ts, rej = fill(fam, count, DEV_QUOTAS[fam], 3000)
        dev.extend(ts)
        rej_log[fam] = rej
        print(f'{fam}: {count} tasks composed, {rej} trivial-rejected', flush=True)
    alien, rej_a = fill('ALIEN', ALIEN_COUNT, None, 6000)
    rej_log['ALIEN'] = rej_a
    print(f'ALIEN: {ALIEN_COUNT} tasks, {rej_a} trivial-rejected', flush=True)

    order = list(range(len(dev)))
    random.Random(31337).shuffle(order)
    dev = [dev[i] for i in order]

    manifest, difficulty = [], {}
    with open(os.path.join(RESULTS, 'oracle_solutions.jsonl'), 'w') as fs, \
         open(os.path.join(RESULTS, 'reachability_rows.jsonl'), 'w') as fr:
        for pos, t in enumerate(dev + alien):
            battery = 'dev' if pos < len(dev) else 'alien'
            assert solves(t['witness'], t)
            reach = classify(t, t['witness'])
            assert reach['status'] == 'REACHABLE'
            key = f"{t['family']}:{t['seed']}"
            manifest.append({'battery': battery, 'position': pos if battery == 'dev'
                             else pos - len(dev), 'family': t['family'],
                             'seed': t['seed'], 'stratum': stratum(t),
                             'wlen': len(t['witness']),
                             'domain_size': len(t['table'])})
            fs.write(json.dumps({'key': key, 'witness': t['witness'],
                                 'witness_len': len(t['witness']),
                                 'expressibility': 'EXPRESSIBLE',
                                 'method': 'constructive_compiler'}) + '\n')
            fr.write(json.dumps({'key': key, 'status': reach['status'],
                                 'path_len': reach['path_len'],
                                 'method': 'structural_insert_path'}) + '\n')
            difficulty[key] = {'stratum': stratum(t), 'wlen': len(t['witness'])}

    json.dump({'n_dev': len(dev), 'n_alien': len(alien),
               'trivial_rejected': rej_log, 'order_seed': 31337,
               'tasks': manifest},
              open(os.path.join(RESULTS, 'task_manifest.json'), 'w'), indent=1)
    json.dump(difficulty,
              open(os.path.join(RESULTS, 'task_difficulty.json'), 'w'), indent=1)
    from collections import Counter
    strata = Counter((m['battery'], m['stratum']) for m in manifest)
    print('strata:', dict(strata))
    print('EC = 1.0 (78/78 constructive witnesses); RC = 1.0 by R==E theorem')


if __name__ == '__main__':
    main()

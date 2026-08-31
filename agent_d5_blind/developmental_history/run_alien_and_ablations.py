"""Run-order steps 4-5: alien zero-shot (M0c-RX vs M1-frozen) + ablation arms.
Spec: PREREG-EVIDENCE.md sections 2, 3, 8. Requires final_libraries/ from the
M1 dev lineages (frozen at end of dev; alien runs never admit)."""
import sys, os, json, random
HERE = os.path.dirname(__file__)
for d in ('..\\task_generators', '..\\substrate', '..\\mutation',
          '..\\exact_oracle', '..\\learner', '..\\navigators', '.'):
    sys.path.insert(0, os.path.join(HERE, d))
from families import gen_task, learner_view
from m1 import m1_rx
from m0 import M0_SUITE
from run_m1_lineage import run_lineage, LADDER, TOP, _row

LEDGERS = os.path.join(HERE, '..', 'ledgers')


def load_final_library(j):
    p = os.path.join(HERE, 'final_libraries', f'lineage_{j}.json')
    return [tuple(tuple(i) for i in g) for g in json.load(open(p))]


def run_alien():
    man = json.load(open(os.path.join(HERE, '..', 'results', 'task_manifest.json')))
    alien = [m for m in man['tasks'] if m['battery'] == 'alien']
    out_path = os.path.join(LEDGERS, 'alien_rows.jsonl')
    done = set()
    if os.path.exists(out_path):
        for line in open(out_path):
            r = json.loads(line)
            done.add((r['arm'], r['lineage'], r['position']))
    with open(out_path, 'a', encoding='utf-8') as f:
        for j in range(5):
            lib = load_final_library(j)
            for m in alien:
                t = gen_task(m['family'], m['seed'])
                view = learner_view(t)
                # M0 alien
                key = ('M0c-RX', j, m['position'])
                if key not in done:
                    ns = 4500 + 100 * j + m['position']
                    res = M0_SUITE['M0c-RX'](view, random.Random(ns), TOP)
                    res['solver'] = None
                    f.write(json.dumps(_row('M0c-RX', j, m, res, ns, 0,
                                            'evidence', 'alien-v1')) + '\n')
                # M1 frozen-library zero-shot
                key = ('M1-frozen', j, m['position'])
                if key not in done:
                    ns = 5500 + 100 * j + m['position']
                    res = m1_rx(view, random.Random(ns), TOP, list(lib))
                    f.write(json.dumps(_row('M1-frozen', j, m, res, ns,
                                            len(lib), 'evidence', 'alien-v1')) + '\n')
                f.flush()
            print(f'alien lineage {j} done', flush=True)


def run_ablations():
    man = json.load(open(os.path.join(HERE, '..', 'results', 'task_manifest.json')))
    dev = [m for m in man['tasks'] if m['battery'] == 'dev']
    out_path = os.path.join(LEDGERS, 'ablation_rows.jsonl')
    for arm in ('M1-random-library', 'M1-shuffled-history', 'M1-frozen-half'):
        for j in range(5):
            print(f'=== {arm} lineage {j} ===', flush=True)
            run_lineage(arm, dev, j, 5000 + 100 * j, out_path, 'evidence',
                        'ablations-v1')


if __name__ == '__main__':
    run_alien()
    print('ALIEN COMPLETE', flush=True)
    run_ablations()
    print('ABLATIONS COMPLETE', flush=True)

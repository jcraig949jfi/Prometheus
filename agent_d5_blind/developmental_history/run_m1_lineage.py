"""M1 lineage harness (oracle-side orchestration; learner logic lives in
learner/m1.py and receives ONLY the learner view).

Arms: M1 (live library), M1-random-library, M1-shuffled-history (two-pass:
libraries accumulated over Random(999)-permuted order, evaluation in frozen
order with position-matched snapshots), M1-frozen-half (no admission after
position 29). Alien zero-shot: frozen library, no admission.
Spec: PREREG-EVIDENCE.md sections 2, 3, 8.
"""
import sys, os, json, random
HERE = os.path.dirname(__file__)
for d in ('..\\task_generators', '..\\substrate', '..\\mutation',
          '..\\exact_oracle', '..\\learner'):
    sys.path.insert(0, os.path.join(HERE, d))
from families import gen_task, learner_view
from m1 import m1_rx, admissions, update_library, LIB_CAP
from physics import mutate, SEED_REPERTOIRE

LADDER = [1000, 3000, 10000, 30000]
TOP = max(LADDER)


def _row(arm, lineage, m, res, nav_seed, lib_size, mode, run_id):
    fs = res['first_solve']
    return {'run_id': run_id, 'mode': mode, 'arm': arm, 'lineage': lineage,
            'position': m['position'], 'family': m['family'], 'seed': m['seed'],
            'stratum': m['stratum'], 'wlen': m['wlen'],
            'solved': res['solved'], 'first_solve': fs, 'evals': res['evals'],
            'ladder': {str(b): (fs is not None and fs <= b) for b in LADDER},
            'nav_seed': nav_seed, 'library_size_at_start': lib_size}


def random_library(size, refresh_idx):
    """Size-matched random-walk genotypes (engineering seed stream 1700+)."""
    lib = []
    rng = random.Random(1700 + refresh_idx)
    while len(lib) < size:
        g = SEED_REPERTOIRE[rng.randrange(len(SEED_REPERTOIRE))]
        for _ in range(rng.randint(5, 40)):
            g = mutate(g, rng)
        if g not in lib:
            lib.append(g)
    return lib


def accumulate_pass(tasks, lineage, seed_base):
    """Run a full sequential pass, returning library snapshots per position.
    snapshots[k] = library state BEFORE evaluating position k."""
    lib, snapshots = [], []
    for m in tasks:
        snapshots.append(list(lib))
        t = gen_task(m['family'], m['seed'])
        view = learner_view(t)
        res = m1_rx(view, random.Random(seed_base + m['position']), TOP,
                    list(lib))
        update_library(lib, admissions(res, view))
    snapshots.append(list(lib))
    return snapshots


def run_lineage(arm, tasks, lineage, seed_base, out_path, mode, run_id,
                frozen_library=None, admit=True):
    done = set()
    if os.path.exists(out_path):
        for line in open(out_path, encoding='utf-8'):
            r = json.loads(line)
            done.add((r['arm'], r['lineage'], r['position']))

    shuffled_snaps = None
    if arm == 'M1-shuffled-history':
        order = list(range(len(tasks)))
        random.Random(999).shuffle(order)
        permuted = [tasks[i] for i in order]
        shuffled_snaps = accumulate_pass(permuted, lineage, seed_base + 50)

    lib = list(frozen_library) if frozen_library is not None else []
    with open(out_path, 'a', encoding='utf-8') as f:
        for k, m in enumerate(tasks):
            if arm == 'M1-shuffled-history':
                lib = list(shuffled_snaps[k])
            elif arm == 'M1-random-library':
                lib = random_library(min(LIB_CAP, 4 + 5 * k), k)
            key = (arm, lineage, m['position'])
            t = gen_task(m['family'], m['seed'])
            view = learner_view(t)
            nav_seed = seed_base + m['position']
            if key not in done:
                res = m1_rx(view, random.Random(nav_seed), TOP, list(lib))
                f.write(json.dumps(_row(arm, lineage, m, res, nav_seed,
                                        len(lib), mode, run_id)) + '\n')
                f.flush()
                print(arm, lineage, k, m['family'], m['seed'],
                      'solved' if res['solved'] else 'unsolved',
                      res['first_solve'], 'lib', len(lib), flush=True)
            else:
                res = m1_rx(view, random.Random(nav_seed), TOP, list(lib))
            if arm in ('M1', 'M1-frozen-half') and admit:
                if not (arm == 'M1-frozen-half' and k >= 29):
                    update_library(lib, admissions(res, view))
    return lib

"""Ergon Gen-1: replay the frozen M1 developmental lineages, with persistence
ON or OFF, through ONE code path.

Why one path: brief section 4A asks for same-seed parity between persistence-on
and persistence-off. If ON and OFF were separate functions, parity would be a
statement about two pieces of code staying in sync. Here `recorder=None` is the
only difference, so the search is literally the same instructions, and the
parity test measures what it claims to.

The frozen M1 developmental driver was NOT committed to agent_d5_blind/ (only
run_lineage(), which no committed caller invokes for arm 'M1'). This module
reconstructs it from the frozen pieces and is validated by exact agreement with
the committed evidence ledger and the committed terminal libraries -- artifacts
written before this seat existed and not tunable by it.
"""
import argparse
import hashlib
import json
import os
import random
import time

import d5_paths
from persistence import LibraryRecorder, genotype_hash, _canon

from families import gen_task, learner_view
from m1 import m1_rx, admissions, update_library
from rm_fast import FastTask

TOP = 30000
SEED_BASE = 5000          # M1 dev lineage j uses SEED_BASE + 100*j + position
OUT = os.path.dirname(os.path.abspath(__file__))

# The ONLY seam in this module. Default is random.Random, so the science path is
# character-identical to the frozen driver. It exists so validate_persistence.py
# can inject an rng-consuming perturbation and DEMONSTRATE that the section-4A
# parity comparator fires -- a comparator never shown to fail is not evidence
# that persistence left search alone. Never rebind this in a scientific run.
RNG_FACTORY = random.Random


def load_dev_battery():
    path = os.path.join(d5_paths.RESULTS, 'task_manifest.json')
    man = json.load(open(path, encoding='utf-8'))
    dev = [m for m in man['tasks'] if m['battery'] == 'dev']
    if not dev:
        raise ValueError('dev battery empty -- manifest lookup found no rows')
    return sorted(dev, key=lambda m: m['position'])


def rng_fingerprint(rng):
    """Hash of the generator's internal state: lets parity assert that the two
    runs consumed the SAME NUMBER of random values, not merely that outcomes
    agreed."""
    return hashlib.sha256(
        json.dumps(rng.getstate(), separators=(',', ':')).encode()
    ).hexdigest()[:16]


def replay_lineage(lineage, dev, recorder=None, run_id='gen1-replay-v1'):
    """One M1 developmental lineage. recorder=None -> persistence OFF."""
    lib = []
    rows = []
    for m in dev:
        task = gen_task(m['family'], m['seed'])
        view = learner_view(task)
        nav_seed = SEED_BASE + 100 * lineage + m['position']
        rng = RNG_FACTORY(nav_seed)

        lib_before = list(lib)
        res = m1_rx(view, rng, TOP, list(lib))
        admitted = admissions(res, view)

        if recorder is not None:
            # Learner-visible only: the distances the learner already computed
            # and the fingerprints admissions() already used.
            # int() below is a lossless numpy-int64 -> Python-int narrowing at
            # the serialization boundary only. The frozen learner keeps using
            # the numpy values; nothing here feeds back into search.
            ft = FastTask(view)
            scores = {}
            for g, d in res['scored']:
                scores.setdefault(genotype_hash(_canon(g)), int(d))
            fingerprints = {genotype_hash(_canon(g)):
                            [int(v) for v in ft.outputs(g)]
                            for g in admitted}

        update_library(lib, admitted)

        if recorder is not None:
            recorder.observe_task(m['position'], m['family'], m['seed'],
                                  nav_seed, lib_before, res, admitted,
                                  list(lib), fingerprints, scores)

        rows.append({
            'run_id': run_id, 'arm': 'M1', 'lineage': lineage,
            'position': m['position'], 'family': m['family'], 'seed': m['seed'],
            'solved': res['solved'], 'first_solve': res['first_solve'],
            'evals': res['evals'], 'nav_seed': nav_seed,
            'library_size_at_start': len(lib_before),
            'n_admitted': len(admitted),
            'rng_state_hash': rng_fingerprint(rng),
            'scored_len': len(res['scored']),
            'candidate_digest': hashlib.sha256(
                json.dumps([[_canon(g), d] for g, d in res['scored']],
                           separators=(',', ':')).encode()).hexdigest()[:16],
        })

    if recorder is not None:
        recorder.observe_final(lib)
    return lib, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lineages', default='0,1,2,3,4')
    ap.add_argument('--persist', action='store_true')
    ap.add_argument('--limit', type=int, default=0,
                    help='first N tasks only (fixture use)')
    ap.add_argument('--out', default=None)
    ap.add_argument('--run-id', default='gen1-replay-v1')
    args = ap.parse_args()

    dev = load_dev_battery()
    if args.limit:
        dev = dev[:args.limit]
    lineages = [int(x) for x in args.lineages.split(',')]
    outdir = args.out or os.path.join(OUT, 'persisted')
    os.makedirs(outdir, exist_ok=True)

    all_rows = []
    t0 = time.time()
    for j in lineages:
        rec = LibraryRecorder(args.run_id, j) if args.persist else None
        lib, rows = replay_lineage(j, dev, rec, args.run_id)
        all_rows.extend(rows)
        if rec is not None:
            rec.write(os.path.join(outdir, 'library_lineage_%d.json' % j))
        print('lineage %d done: %d tasks, final lib %d, %.1fs'
              % (j, len(rows), len(lib), time.time() - t0), flush=True)

    tag = 'on' if args.persist else 'off'
    rows_path = os.path.join(outdir, 'replay_rows_%s.jsonl' % tag)
    with open(rows_path, 'w', encoding='utf-8') as f:
        for r in all_rows:
            f.write(json.dumps(r) + '\n')
        f.flush()
    print('wrote %s (%d rows) in %.1fs' % (rows_path, len(all_rows),
                                           time.time() - t0), flush=True)


if __name__ == '__main__':
    main()

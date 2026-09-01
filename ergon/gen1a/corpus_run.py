"""ERGON GEN-1A / sections 4-5 -- generate the machine-native artifact corpus
that has never existed, and make EFFECTIVE USAGE observable.

This is NOT the Gen-1 retention experiment. It runs the BASELINE policy only
(frozen D-5 admission + most-recent-first eviction) to produce the corpus the
attainable-range analysis needs. No policy is varied here.

THE THREE-POINT WRAP. Effective usage asks whether a draw from the library
produced a measurable improvement. That fact is split across three places in
the frozen core, none of which talk to each other:

    library draw    RecordingLibrary.__getitem__   -> which artifact
    mutation        physics.mutate(parent, rng)    -> parent to child
    scoring         FastTask.dist(child)           -> child's score

So credit needs all three observed and linked. Each wrap is pure observation:
no rng is consumed, no branch is taken differently, no evaluation counter
moves. This is the feasibility finding that makes an EFFECTIVE-USAGE eviction
policy implementable at all without forking the search core.

CREDIT RULE (primary, preregistered here BEFORE any outcome is inspected):
    a draw is CREDITED if the child it produced scores strictly better
    (lower distance) than the median of the last PSIZE scored candidates.
The window is a mechanically available online proxy for "contemporaneous
population", it uses no future information, and it needs no oracle field.

Run:  python -m ergon.gen1a.corpus_run --lineages 5 --budget 30000
"""
import argparse
import collections
import json
import os
import random
import statistics
import sys
import time

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..')))
from ergon.gen1a import persistence as P              # noqa: E402
from ergon.gen1a.persistence import (                 # noqa: E402
    LibraryRecorder, artifact_hash)

sys.path.insert(0, os.path.join(P.D5, 'task_generators'))
from families import gen_task                         # noqa: E402
import m1 as M1                                       # noqa: E402
import physics                                        # noqa: E402
import rm_fast                                        # noqa: E402

PSIZE = 32          # frozen m1_rx default; the credit window matches it
NC = ('F1', 'F2', 'F3', 'F4')


class DeepRecorder:
    """Links draw -> mutate -> score so effective usage is computable."""

    def __init__(self, reclib):
        self.reclib = reclib
        self.pending_parent = None
        self.pending_child = None
        self.recent = collections.deque(maxlen=PSIZE)
        self.draws = collections.Counter()
        self.credited = collections.Counter()
        self._orig_mutate = physics.mutate
        self._orig_dist = rm_fast.FastTask.dist
        self._m1_mutate = M1.mutate

    def __enter__(self):
        rec = self

        def mutate(prog, rng, allowed=None):
            child = rec._orig_mutate(prog, rng, allowed)
            if rec.pending_parent is not None and prog is rec.pending_parent:
                rec.pending_child = (artifact_hash(prog), child)
                rec.pending_parent = None
            return child

        def dist(self_ft, prog):
            d = rec._orig_dist(self_ft, prog)
            pc = rec.pending_child
            if pc is not None and prog is pc[1]:
                if rec.recent:
                    med = statistics.median(rec.recent)
                    if d < med:
                        rec.credited[pc[0]] += 1
                rec.pending_child = None
            rec.recent.append(d)
            return d

        physics.mutate = mutate
        M1.mutate = mutate
        rm_fast.FastTask.dist = dist

        orig_getitem = type(self.reclib).__getitem__

        def getitem(lib, idx):
            item = orig_getitem(lib, idx)
            if isinstance(idx, int):
                rec.pending_parent = item
                rec.draws[artifact_hash(item)] += 1
            return item

        self._orig_getitem = orig_getitem
        type(self.reclib).__getitem__ = getitem
        return self

    def __exit__(self, *a):
        physics.mutate = self._orig_mutate
        M1.mutate = self._m1_mutate
        rm_fast.FastTask.dist = self._orig_dist
        type(self.reclib).__getitem__ = self._orig_getitem
        return False


def battery():
    man = json.load(open(os.path.join(P.D5, 'results', 'task_manifest.json'),
                         encoding='utf-8'))
    return [m for m in man['tasks'] if m['family'] in NC]


def run_lineage(tasks, lineage, nav_base, budget, out_dir):
    rec = LibraryRecorder('gen1a-corpus', lineage)
    rows = []
    meta = {}          # hash -> first-seen record
    t0 = time.time()
    with DeepRecorder(rec.library) as deep:
        for i, m in enumerate(tasks):
            t = gen_task(m['family'], m['seed'])
            v = {'domain': t['domain'], 'table': t['table']}
            rec.begin_task(m['family'], m['seed'])
            size_at_start = len(rec.library)
            res = M1.m1_rx(v, random.Random(nav_base + i), budget, rec.library)
            admits = M1.admissions(res, v)
            ft = rm_fast.FastTask(v)
            for g in admits:
                h = artifact_hash(g)
                if h not in meta:
                    meta[h] = {'hash': h, 'genotype': P.genotype_to_json(g),
                               'len': len(g), 'first_admit_task': i,
                               'first_admit_family': m['family'],
                               'fingerprint': [int(x) for x in ft.outputs(g)],
                               'was_solver': (res['solver'] is not None and
                                              g == res['solver'])}
            rec.record_admissions(admits, v)
            rows.append({'lineage': lineage, 'i': i, 'family': m['family'],
                         'seed': m['seed'], 'solved': res['solved'],
                         'first_solve': res['first_solve'],
                         'evals': res['evals'],
                         'library_size_at_start': size_at_start,
                         'n_admitted': len(admits)})
    secs = time.time() - t0
    for h, d in meta.items():
        d['draws'] = int(deep.draws.get(h, 0))
        d['effective_uses'] = int(deep.credited.get(h, 0))
        d['lineage'] = lineage
    os.makedirs(out_dir, exist_ok=True)
    rec.write(out_dir)
    with open(os.path.join(out_dir, 'lineage_%d_artifacts.jsonl' % lineage),
              'w', encoding='utf-8') as fh:
        for h in sorted(meta):
            fh.write(json.dumps(meta[h], sort_keys=True) + '\n')
    with open(os.path.join(out_dir, 'lineage_%d_rows.jsonl' % lineage),
              'w', encoding='utf-8') as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + '\n')
    return rows, meta, secs, len(rec.library.draws)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lineages', type=int, default=5)
    ap.add_argument('--budget', type=int, default=30000)
    ap.add_argument('--out', default=os.path.join(HERE, 'corpus'))
    a = ap.parse_args()

    tasks = battery()
    print('ERGON GEN-1A -- BASELINE CORPUS GENERATION (not the experiment)')
    print('=' * 68)
    print('tasks %d | lineages %d | budget %d | policy D5_BASELINE_MRU\n'
          % (len(tasks), a.lineages, a.budget))
    total_secs = 0.0
    allrows = []
    for L in range(a.lineages):
        rows, meta, secs, ndraws = run_lineage(tasks, L, 5000 + 1000 * L,
                                               a.budget, a.out)
        total_secs += secs
        allrows += rows
        solved = sum(1 for r in rows if r['solved'])
        used = sum(1 for m in meta.values() if m['draws'] > 0)
        eff = sum(1 for m in meta.values() if m['effective_uses'] > 0)
        print('  lineage %d: %5.1fs | solved %2d/%d | artifacts %3d | '
              'drawn %3d | effective %3d | draws %d'
              % (L, secs, solved, len(rows), len(meta), used, eff, ndraws))
    print('\ntotal %.1fs (%.1f min) for %d lineages -> %.1fs per lineage'
          % (total_secs, total_secs / 60, a.lineages, total_secs / a.lineages))
    json.dump({'lineages': a.lineages, 'budget': a.budget,
               'tasks': len(tasks), 'seconds_total': round(total_secs, 1),
               'seconds_per_lineage': round(total_secs / a.lineages, 1)},
              open(os.path.join(a.out, 'run_meta.json'), 'w'), indent=2)
    return 0


if __name__ == '__main__':
    sys.exit(main())

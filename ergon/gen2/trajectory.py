"""ERGON PROJECT 2 -- candidate-level trajectory instrumentation.

Gen-1B could report LIBRARY divergence but not CANDIDATE divergence, and that
gap is now load-bearing: the Gen-1B autopsy could not say what the induced
search stream actually did differently. This closes it.

DESIGN CONSTRAINT, unchanged from Gen-1A. The frozen search core is not forked.
Every observation is a wrapper around a surface the core already uses:

    library draw      PolicyLibrary.__getitem__   -> which artifact, which slot
    mutation          physics.mutate(parent)      -> operator and parent
    crossover         physics.crossover(p1, p2)   -> two-parent provenance
    scoring           FastTask.dist(child)        -> score and evaluation index

None of these consume randomness, take a branch, or move the evaluation
counter. The parity gate in this module is what tests that claim rather than
asserting it.

WHAT IS RECORDED per scored candidate:
    evaluation index (the position in the metered budget)
    task index, lineage, policy
    candidate genotype hash and behaviour fingerprint hash
    score
    parent hash(es)
    parent source: LIBRARY | POPULATION | REPERTOIRE | CROSSOVER
    mutation operator class
    library state reference (a hash of the ordered library at task start)

FIRST DIVERGENCE INDEX for a paired pair of runs is then the smallest
evaluation index at which the two candidate streams differ.

Run:  python -m ergon.gen2.trajectory --selftest
"""
import argparse
import collections
import hashlib
import json
import os
import random
import statistics
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..')))
from ergon.gen1a import persistence as P                 # noqa: E402
from ergon.gen1a.persistence import artifact_hash        # noqa: E402
from ergon.gen1b import gen1_run as G                    # noqa: E402
sys.path.insert(0, os.path.join(P.D5, 'task_generators'))
from families import gen_task                            # noqa: E402
import m1 as M1                                          # noqa: E402
import physics                                           # noqa: E402
import rm_fast                                           # noqa: E402

LIBRARY, POPULATION, REPERTOIRE, CROSSOVER = 'LIB', 'POP', 'REP', 'XOVER'


def fp_hash(vals):
    return hashlib.sha256(
        json.dumps([int(v) for v in vals], separators=(',', ':'))
        .encode()).hexdigest()[:12]


class TrajectoryRecorder:
    """Observational wrapper over draw / mutate / crossover / dist."""

    def __init__(self, lib, ref):
        self.lib = lib
        self.ref = ref
        self.rows = []
        self.eval_index = 0
        self.task_index = 0
        self.lib_state = None
        # m1_rx BUILDS A WHOLE GENERATION and only then scores it, so a
        # single "pending" slot is overwritten 31 times before the first
        # dist() call and attributes ancestry to almost nothing. The first
        # version of this recorder did exactly that and lost 97% of parents.
        # Provenance is therefore keyed by the child object itself.
        self._built = {}
        self._m = physics.mutate
        self._x = physics.crossover
        self._d = rm_fast.FastTask.dist
        self._m1m = M1.mutate
        self._m1x = M1.crossover
        self._seen_rep = {artifact_hash(g) for g in physics.SEED_REPERTOIRE}

    def set_task(self, i, lib_snapshot):
        self.task_index = i
        self.lib_state = hashlib.sha256(
            json.dumps([artifact_hash(g) for g in lib_snapshot]).encode()
        ).hexdigest()[:12]

    def __enter__(self):
        r = self

        def mutate(prog, rng, allowed=None):
            child = r._m(prog, rng, allowed)
            ph = artifact_hash(prog)
            prior = r._built.get(id(prog))
            if getattr(r.lib, '_last_drawn', None) is prog:
                src = LIBRARY
                r.lib._last_drawn = None
            elif prior is not None and prior[1] == CROSSOVER:
                src = CROSSOVER            # mutate(crossover(...)) composite
            elif ph in r._seen_rep:
                src = REPERTOIRE
            else:
                src = POPULATION
            parents = prior[0] if (prior and prior[1] == CROSSOVER) else (ph,)
            r._built[id(child)] = (parents, src, _infer_op(prog, child))
            return child

        def crossover(p1, p2, rng):
            child = r._x(p1, p2, rng)
            r._built[id(child)] = ((artifact_hash(p1), artifact_hash(p2)),
                                   CROSSOVER, None)
            return child

        def dist(ft, prog):
            d = r._d(ft, prog)
            if ft is not r.ref:                 # only count scored candidates
                r.eval_index += 1
                prov = r._built.pop(id(prog), None)
                r.rows.append({
                    'ev': r.eval_index, 'task': r.task_index,
                    'cand': artifact_hash(prog),
                    'beh': fp_hash(ft.outputs(prog)),
                    'score': int(d),
                    'parents': list(prov[0]) if prov else [],
                    'src': prov[1] if prov else None,
                    'op': prov[2] if prov else None,
                    'lib': r.lib_state,
                })
            return d

        physics.mutate = mutate
        M1.mutate = mutate
        physics.crossover = crossover
        M1.crossover = crossover
        rm_fast.FastTask.dist = dist

        orig_getitem = type(self.lib).__getitem__

        def getitem(lb, idx):
            item = orig_getitem(lb, idx)
            if isinstance(idx, int):
                lb._last_drawn = item
            return item

        self._orig_getitem = orig_getitem
        type(self.lib).__getitem__ = getitem
        return self

    def __exit__(self, *a):
        physics.mutate = self._m
        M1.mutate = self._m1m
        physics.crossover = self._x
        M1.crossover = self._m1x
        rm_fast.FastTask.dist = self._d
        type(self.lib).__getitem__ = self._orig_getitem
        return False


def _infer_op(parent, child):
    """Which mutation class produced child from parent, by structure alone.
    Purely observational: no randomness is drawn and the answer is not used by
    the search."""
    lp, lc = len(parent), len(child)
    if lc > lp:
        return 'DUP_BLOCK' if lc - lp > 1 else 'INSERT'
    if lc < lp:
        return 'DELETE'
    diff = [i for i in range(lp) if parent[i] != child[i]]
    if len(diff) == 2 and parent[diff[0]] == child[diff[1]] \
            and parent[diff[1]] == child[diff[0]]:
        return 'SWAP'
    if len(diff) == 1:
        a, b = parent[diff[0]], child[diff[0]]
        return 'OP_REPLACE' if a[0] != b[0] else 'ARG_TWEAK'
    return 'OTHER'


def run_lineage(tasks, arm, lineage, nav_base, budget, ref, n_tasks=None):
    """Instrumented lineage. Mirrors gen1_run.run_lineage exactly, with the
    trajectory recorder wrapped around it."""
    rng = random.Random(50000 + lineage)
    lib = G.PolicyLibrary(arm, rng, ref)
    lib._last_drawn = None
    rec = TrajectoryRecorder(lib, ref)
    rows = []
    use = tasks if n_tasks is None else tasks[:n_tasks]
    with rec, G.Credit(lib):
        for i, m in enumerate(use):
            t = gen_task(m['family'], m['seed'])
            v = {'domain': t['domain'], 'table': t['table']}
            lib.task_index = i
            rec.set_task(i, list(lib))
            res = M1.m1_rx(v, random.Random(nav_base + i), budget, lib)
            rows.append({'arm': arm, 'lineage': lineage, 'i': i,
                         'family': m['family'], 'seed': m['seed'],
                         'solved': res['solved'],
                         'first_solve': res['first_solve'],
                         'evals': res['evals']})
            ft = rm_fast.FastTask(v)
            lib.admit(M1.admissions(res, v), ft)
    return rows, rec, lib


def control_lineage(tasks, arm, lineage, nav_base, budget, ref, n_tasks=None):
    """The SAME lineage with NO trajectory instrumentation. The parity gate."""
    rng = random.Random(50000 + lineage)
    lib = G.PolicyLibrary(arm, rng, ref)
    rows = []
    use = tasks if n_tasks is None else tasks[:n_tasks]
    with G.Credit(lib):
        for i, m in enumerate(use):
            t = gen_task(m['family'], m['seed'])
            v = {'domain': t['domain'], 'table': t['table']}
            lib.task_index = i
            res = M1.m1_rx(v, random.Random(nav_base + i), budget, lib)
            rows.append({'arm': arm, 'lineage': lineage, 'i': i,
                         'family': m['family'], 'seed': m['seed'],
                         'solved': res['solved'],
                         'first_solve': res['first_solve'],
                         'evals': res['evals']})
            ft = rm_fast.FastTask(v)
            lib.admit(M1.admissions(res, v), ft)
    return rows, lib


def first_divergence(rows_a, rows_b):
    """Smallest evaluation index at which two candidate streams differ."""
    n = min(len(rows_a), len(rows_b))
    for k in range(n):
        if rows_a[k]['cand'] != rows_b[k]['cand']:
            return rows_a[k]['ev'], k
    return None, n


def stream_stats(rows_a, rows_b):
    ca = [r['cand'] for r in rows_a]
    cb = [r['cand'] for r in rows_b]
    ba = [r['beh'] for r in rows_a]
    bb = [r['beh'] for r in rows_b]
    sa = set(ca)
    sb = set(cb)
    return {
        'n_a': len(ca), 'n_b': len(cb),
        'identity_jaccard': round(len(sa & sb) / len(sa | sb), 5) if (sa | sb) else 1.0,
        'behaviour_jaccard': round(len(set(ba) & set(bb)) /
                                   len(set(ba) | set(bb)), 5),
        'score_mean_a': round(statistics.mean(r['score'] for r in rows_a), 3),
        'score_mean_b': round(statistics.mean(r['score'] for r in rows_b), 3),
        'src_dist_a': dict(collections.Counter(r['src'] for r in rows_a)),
        'src_dist_b': dict(collections.Counter(r['src'] for r in rows_b)),
        'op_dist_a': dict(collections.Counter(r['op'] for r in rows_a
                                              if r['op'])),
        'op_dist_b': dict(collections.Counter(r['op'] for r in rows_b
                                              if r['op'])),
        'library_descended_frac_a': round(
            sum(1 for r in rows_a if r['src'] == LIBRARY) / len(rows_a), 5),
        'library_descended_frac_b': round(
            sum(1 for r in rows_b if r['src'] == LIBRARY) / len(rows_b), 5),
    }


def selftest(n_tasks=6, budget=2000):
    """PARITY GATE. Instrumentation must not alter RNG consumption, evaluation
    order, candidate generation, score, CFR or library contents."""
    tasks = G.battery()
    t0 = tasks[0]
    tt = gen_task(t0['family'], t0['seed'])
    ref = rm_fast.FastTask({'domain': tt['domain'], 'table': tt['table']})

    print('ERGON PROJECT 2 -- TRAJECTORY INSTRUMENT PARITY GATE')
    print('=' * 70)
    print('fixture: %d tasks, budget %d, arms I1 and I3\n' % (n_tasks, budget))
    holes = 0
    for arm in ('I1', 'I3'):
        off_rows, off_lib = control_lineage(tasks, arm, 900, 800000, budget,
                                            ref, n_tasks)
        on_rows, rec, on_lib = run_lineage(tasks, arm, 900, 800000, budget,
                                           ref, n_tasks)
        checks = [
            ('rows identical (solved, first_solve, evals)', off_rows == on_rows),
            ('library contents identical', list(off_lib) == list(on_lib)),
            ('library size identical', len(off_lib) == len(on_lib)),
            ('eviction count identical', off_lib.evictions == on_lib.evictions),
            ('total draws identical',
             len(off_lib.draw_log) == len(on_lib.draw_log)),
            ('effective-use totals identical',
             sum(off_lib.eff.values()) == sum(on_lib.eff.values())),
        ]
        print('  arm %s' % arm)
        for label, ok in checks:
            holes += (0 if ok else 1)
            print('    [%s] %s' % ('PASS' if ok else 'FAIL', label))
        print('    candidates recorded: %d | evaluations reported by search: %d'
              % (len(rec.rows), sum(r['evals'] for r in on_rows)))
        cover = len(rec.rows) / max(1, sum(r['evals'] for r in on_rows))
        ok = 0.98 <= cover <= 1.0
        holes += (0 if ok else 1)
        print('    [%s] candidate coverage %.4f of metered evaluations'
              % ('PASS' if ok else 'FAIL', cover))

    # divergence machinery must find a real divergence between two policies
    _r1, rec1, _l1 = run_lineage(tasks, 'I1', 901, 810000, budget, ref, n_tasks)
    _r3, rec3, _l3 = run_lineage(tasks, 'I3', 901, 810000, budget, ref, n_tasks)
    ev, k = first_divergence(rec1.rows, rec3.rows)
    st = stream_stats(rec1.rows, rec3.rows)
    print('\n  PAIRED I1 vs I3, same lineage seed:')
    print('    first divergence at evaluation index %s (position %d of %d)'
          % (ev, k, min(len(rec1.rows), len(rec3.rows))))
    print('    candidate identity Jaccard %.4f | behaviour Jaccard %.4f'
          % (st['identity_jaccard'], st['behaviour_jaccard']))
    print('    library-descended candidate fraction  I1 %.4f  I3 %.4f'
          % (st['library_descended_frac_a'], st['library_descended_frac_b']))
    print('    parent-source distribution I1 %s' % st['src_dist_a'])
    print('    operator distribution      I1 %s' % st['op_dist_a'])

    # POSITIVE CONTROL. The pair above may not diverge at a small fixture,
    # because the cap of 64 is not reached and no eviction has yet differed --
    # so the detector would report None for a reason that has nothing to do
    # with its correctness. A longer fixture forces real eviction divergence
    # and the detector MUST then fire. Without this, a broken detector and a
    # not-yet-diverged pair look identical.
    _r1, recL1, _l = run_lineage(tasks, 'I1', 903, 830000, budget, ref, 24)
    _r3, recL3, _l = run_lineage(tasks, 'I3', 903, 830000, budget, ref, 24)
    evp, kp = first_divergence(recL1.rows, recL3.rows)
    okp = evp is not None
    holes += (0 if okp else 1)
    print('')
    print('  [%s] POSITIVE CONTROL: 24-task fixture reaches the cap, so the'
          % ('PASS' if okp else 'FAIL'))
    print('        policies MUST diverge -- first divergence at ev %s' % evp)
    stp = stream_stats(recL1.rows, recL3.rows)
    print('        candidate identity Jaccard %.4f | behaviour Jaccard %.4f'
          % (stp['identity_jaccard'], stp['behaviour_jaccard']))

    # ANCESTRY COVERAGE. The first version of this recorder used a single
    # pending slot and lost 97% of parents, because m1_rx builds a whole
    # generation before scoring any of it. Coverage is now a gate.
    attributed = sum(1 for r in recL1.rows if r['src'] is not None)
    cov = attributed / len(recL1.rows)
    oka = cov >= 0.99
    holes += (0 if oka else 1)
    print('  [%s] ANCESTRY COVERAGE %.4f of scored candidates carry a parent'
          % ('PASS' if oka else 'FAIL', cov))
    print('        parent-source distribution %s' % stp['src_dist_a'])

    # a same-arm same-seed pair must NOT diverge -- the negative control that
    # proves the divergence detector is not reporting noise
    _r, recA, _l = run_lineage(tasks, 'I1', 902, 820000, budget, ref, n_tasks)
    _r, recB, _l = run_lineage(tasks, 'I1', 902, 820000, budget, ref, n_tasks)
    evc, _kc = first_divergence(recA.rows, recB.rows)
    ok = evc is None
    holes += (0 if ok else 1)
    print('\n  [%s] NEGATIVE CONTROL: identical arm + seed does NOT diverge '
          '(first divergence %s)' % ('PASS' if ok else 'FAIL', evc))

    verdict = ('TRAJECTORY_INSTRUMENT_CLEAN' if holes == 0
               else 'TRAJECTORY_INSTRUMENT_SUSPECT')
    print('\nVERDICT: %s  (%d holes)' % (verdict, holes))
    out = {'verdict': verdict, 'holes': holes, 'n_tasks': n_tasks,
           'budget': budget, 'first_divergence_ev': ev,
           'stream_stats': st, 'negative_control_clean': bool(ok)}
    json.dump(out, open(os.path.join(HERE, 'p2_parity.json'), 'w',
                        encoding='utf-8'), indent=2, sort_keys=True)
    print('wrote p2_parity.json')
    return 0 if holes == 0 else 1


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--tasks', type=int, default=6)
    ap.add_argument('--budget', type=int, default=2000)
    a = ap.parse_args()
    sys.exit(selftest(a.tasks, a.budget) if a.selftest else 0)

"""ERGON GEN-1 / PHASE 4 -- the retention-policy experiment.

Eviction is the ONLY treatment. Admission (m1.admissions), the search core
(m1.m1_rx), the mutation operators, the cap of 64, the task corpus, the budget
and the scoring are all frozen and identical across arms.

ARMS (frozen in PREREG_GEN1_2026-09-01.txt before the first evaluation):

  I0  D5_BASELINE_MRU   evict the oldest resident. Inherited semantics.
  I1  MUT_REDUNDANT     evict a resident that is redundant BOTH behaviourally
                        and mutationally (offspring-sketch Jaccard >= 0.50
                        with a same-fingerprint resident), older first;
                        else fall back to MRU. Repaired after Phase 1 showed
                        behavioural duplicates are usually NOT evolutionarily
                        redundant.
  I2  EFFECTIVE_USAGE   evict the resident with fewest effective uses among
                        those with >= 100 draw opportunities (a grace period,
                        set from the Phase 2 exposure curve); if none qualify,
                        minimise over all residents. Ties by insertion order.
  I3  RANDOM            evict a uniformly random resident. The
                        arbitrary-memory comparator.

EFFECTIVE USE, frozen: a library draw is credited when the child it produced
scores strictly better than the median of the last 32 scored candidates.
Online, learner-visible, no oracle field, no future information.

Run:  python -m ergon.gen1b.gen1_run --arms I0,I1,I2,I3 --lineages 30
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
from ergon.gen1a import persistence as P                    # noqa: E402
from ergon.gen1a.persistence import artifact_hash           # noqa: E402

sys.path.insert(0, os.path.join(P.D5, 'task_generators'))
from families import gen_task                               # noqa: E402
import m1 as M1                                             # noqa: E402
import physics                                              # noqa: E402
import rm_fast                                              # noqa: E402

CAP = 64
PSIZE = 32
K_SKETCH = 32
SKETCH_SEED = 4242
TAU = 0.50
GRACE = 100
NC = ('F1', 'F2', 'F3', 'F4')
ARMS = ('I0', 'I1', 'I2', 'I3')


class PolicyLibrary(list):
    """The library, with a policy-determined eviction rule. Admission,
    dedupe and append order are the frozen D-5 semantics."""

    def __init__(self, policy, rng, ref):
        super().__init__()
        self.policy = policy
        self.rng = rng
        self.ref = ref
        self.fp = {}
        self.sk = {}
        self.seq = {}
        self.draws = collections.Counter()
        self.eff = collections.Counter()
        self.n = 0
        self.evictions = 0
        self.fallbacks = 0
        self.sketch_mutations = 0
        self.draw_log = []
        self.task_index = 0
        self.pending_parent = None
        self.admit_task = {}
        self.evict_log = []

    def __getitem__(self, idx):
        item = super().__getitem__(idx)
        if isinstance(idx, int):
            h = artifact_hash(item)
            self.draws[h] += 1
            self.draw_log.append((self.task_index, h))
            self.pending_parent = item
        return item

    def _sketch(self, g):
        rng = random.Random(SKETCH_SEED)
        s = set()
        for _ in range(K_SKETCH):
            s.add(tuple(int(x) for x in self.ref.outputs(physics.mutate(g, rng))))
        self.sketch_mutations += K_SKETCH
        return frozenset(s)

    def admit(self, new_genotypes, ft):
        for g in new_genotypes:
            h = artifact_hash(g)
            if h not in self.fp:
                self.fp[h] = tuple(int(x) for x in ft.outputs(g))
                if self.policy == 'I1':
                    self.sk[h] = self._sketch(g)
            if g in self:
                super().remove(g)
            self.n += 1
            self.seq[h] = self.n
            self.admit_task.setdefault(h, self.task_index)
            self.append(g)
        while len(self) > CAP:
            self._evict()

    def _evict(self):
        hs = [artifact_hash(g) for g in self]
        victim_i = None
        if self.policy == 'I0':
            victim_i = 0
        elif self.policy == 'I3':
            victim_i = self.rng.randrange(len(self))
        elif self.policy == 'I2':
            elig = [i for i, h in enumerate(hs) if self.draws[h] >= GRACE]
            pool = elig if elig else list(range(len(hs)))
            if not elig:
                self.fallbacks += 1
            victim_i = min(pool, key=lambda i: (self.eff[hs[i]], self.seq[hs[i]]))
        elif self.policy == 'I1':
            byfp = collections.defaultdict(list)
            for i, h in enumerate(hs):
                byfp[self.fp[h]].append(i)
            cands = set()
            for _fp, idxs in byfp.items():
                if len(idxs) < 2:
                    continue
                for a in range(len(idxs)):
                    for b in range(a + 1, len(idxs)):
                        ha, hb = hs[idxs[a]], hs[idxs[b]]
                        sa, sb = self.sk[ha], self.sk[hb]
                        u = len(sa | sb)
                        if u and len(sa & sb) / u >= TAU:
                            cands.add(idxs[a] if self.seq[ha] < self.seq[hb]
                                      else idxs[b])
            if cands:
                victim_i = min(cands, key=lambda i: self.seq[hs[i]])
            else:
                victim_i = 0
                self.fallbacks += 1
        h = hs[victim_i]
        self.evict_log.append({'i': self.task_index, 'hash': h,
                               'age_tasks': self.task_index - self.admit_task.get(h, 0),
                               'draws': int(self.draws[h]),
                               'eff': int(self.eff[h])})
        super().pop(victim_i)
        self.evictions += 1


class Credit:
    """Links draw -> mutate -> score so effective use is credited ONLINE."""

    def __init__(self, lib):
        self.lib = lib
        self.recent = collections.deque(maxlen=PSIZE)
        self.pending_child = None
        self._m = physics.mutate
        self._d = rm_fast.FastTask.dist
        self._m1m = M1.mutate

    def __enter__(self):
        c = self

        def mutate(prog, rng, allowed=None):
            child = c._m(prog, rng, allowed)
            if c.lib.pending_parent is not None and prog is c.lib.pending_parent:
                c.pending_child = (artifact_hash(prog), child)
                c.lib.pending_parent = None
            return child

        def dist(ft, prog):
            d = c._d(ft, prog)
            pc = c.pending_child
            if pc is not None and prog is pc[1]:
                if c.recent and d < statistics.median(c.recent):
                    c.lib.eff[pc[0]] += 1
                c.pending_child = None
            c.recent.append(d)
            return d

        physics.mutate = mutate
        M1.mutate = mutate
        rm_fast.FastTask.dist = dist
        return self

    def __exit__(self, *a):
        physics.mutate = self._m
        M1.mutate = self._m1m
        rm_fast.FastTask.dist = self._d
        return False


def battery():
    man = json.load(open(os.path.join(P.D5, 'results', 'task_manifest.json'),
                         encoding='utf-8'))
    return [m for m in man['tasks'] if m['family'] in NC]


def run_lineage(tasks, arm, lineage, nav_base, budget, ref):
    rng = random.Random(50000 + lineage)
    lib = PolicyLibrary(arm, rng, ref)
    rows = []
    with Credit(lib):
        for i, m in enumerate(tasks):
            t = gen_task(m['family'], m['seed'])
            v = {'domain': t['domain'], 'table': t['table']}
            lib.task_index = i
            size0 = len(lib)
            res = M1.m1_rx(v, random.Random(nav_base + i), budget, lib)
            rows.append({'arm': arm, 'lineage': lineage, 'i': i,
                         'family': m['family'], 'seed': m['seed'],
                         'solved': res['solved'],
                         'first_solve': res['first_solve'],
                         'evals': res['evals'], 'lib_size_at_start': size0})
            ft = rm_fast.FastTask(v)
            lib.admit(M1.admissions(res, v), ft)
    final = [artifact_hash(g) for g in lib]
    summary = {
        'arm': arm, 'lineage': lineage,
        'solved': sum(1 for r in rows if r['solved']), 'n_tasks': len(rows),
        'cfr': sum(1 for r in rows if r['solved']) / len(rows),
        'evictions': lib.evictions, 'fallbacks': lib.fallbacks,
        'sketch_mutations': lib.sketch_mutations,
        'total_draws': len(lib.draw_log),
        'final_library': final,
        'final_behaviours': len({lib.fp[h] for h in final}),
        'final_offspring_behaviours': (
            len(set().union(*[lib.sk[h] for h in final])) if lib.sk else None),
        'n_artifacts_seen': len(lib.fp),
        'eff_total': int(sum(lib.eff.values())),
        'artifacts_with_eff': sum(1 for h in lib.fp if lib.eff[h] > 0),
        'final_median_age': statistics.median(
            [i - lib.admit_task.get(h, 0) for h in final]) if final else None,
        'final_eff_concentration': (
            max(lib.eff[h] for h in final) / max(1, sum(lib.eff[h] for h in final))
            if final else None),
        'evict_log': lib.evict_log,
        'per_artifact': {h: {'draws': int(lib.draws[h]), 'eff': int(lib.eff[h]),
                             'admit': lib.admit_task.get(h),
                             'len': len(lib.fp[h])} for h in lib.fp},
    }
    return rows, summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arms', default='I0,I1,I2,I3')
    ap.add_argument('--lineages', type=int, default=30)
    ap.add_argument('--budget', type=int, default=30000)
    ap.add_argument('--out', default=os.path.join(HERE, 'gen1_results'))
    a = ap.parse_args()
    arms = a.arms.split(',')
    tasks = battery()
    t0 = tasks[0]
    tt = gen_task(t0['family'], t0['seed'])
    ref = rm_fast.FastTask({'domain': tt['domain'], 'table': tt['table']})
    os.makedirs(a.out, exist_ok=True)

    print('ERGON GEN-1 -- RETENTION POLICY EXPERIMENT')
    print('=' * 70)
    print('arms %s | lineages %d | tasks %d | budget %d'
          % (arms, a.lineages, len(tasks), a.budget))
    print('paired: lineage L uses the SAME nav_seed base in every arm\n')

    start = time.time()
    for L in range(a.lineages):
        nav_base = 200000 + 1000 * L      # identical across arms -> paired
        for arm in arms:
            rp = os.path.join(a.out, 'rows_%s_%d.jsonl' % (arm, L))
            sp = os.path.join(a.out, 'summary_%s_%d.json' % (arm, L))
            if os.path.exists(sp):
                continue
            ts = time.time()
            rows, summary = run_lineage(tasks, arm, L, nav_base, a.budget, ref)
            summary['seconds'] = round(time.time() - ts, 1)
            with open(rp, 'w', encoding='utf-8') as fh:
                for r in rows:
                    fh.write(json.dumps(r, sort_keys=True) + '\n')
            json.dump(summary, open(sp, 'w', encoding='utf-8'), sort_keys=True)
        done = [json.load(open(os.path.join(a.out, 'summary_%s_%d.json' % (m, L))))
                for m in arms]
        print('  lineage %2d  ' % L + '  '.join(
            '%s cfr %.3f (%ds)' % (d['arm'], d['cfr'], d['seconds'])
            for d in done))
    print('\ntotal %.1f min' % ((time.time() - start) / 60))
    return 0


if __name__ == '__main__':
    sys.exit(main())

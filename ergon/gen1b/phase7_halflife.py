"""ERGON GEN-1B / PHASE 7 -- experience half-life.

The first empirical survival/recurrence analysis of executable experience in
this programme.

WHY A SEPARATE PASS. Effective-use TIMING is not in the Gen-1 ledger: the
frozen runner records per-artifact totals, not timestamped credit events, and
the runner was hashed before the run so it cannot be changed mid-experiment.
So Phase 7 uses a dedicated OBSERVATIONAL pass under the baseline policy only,
logging each effective-use event with the task index at which it occurred.
This pass is instrument output. It is NOT part of the Gen-1 analysis set and
no Gen-1 contrast depends on it.

Run:  python -m ergon.gen1b.phase7_halflife --lineages 5 --budget 30000
"""
import argparse
import collections
import json
import os
import random
import statistics
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..')))
from ergon.gen1a import persistence as P                # noqa: E402
from ergon.gen1a.persistence import artifact_hash       # noqa: E402
sys.path.insert(0, os.path.join(P.D5, 'task_generators'))
from families import gen_task                           # noqa: E402
import m1 as M1                                         # noqa: E402
import physics                                          # noqa: E402
import rm_fast                                          # noqa: E402

PSIZE = 32
NC = ('F1', 'F2', 'F3', 'F4')


class TimedLibrary(list):
    def __init__(self):
        super().__init__()
        self.task_index = 0
        self.pending_parent = None
        self.draw_events = []      # (task_index, hash)
        self.eff_events = []       # (task_index, hash)
        self.admit_task = {}

    def __getitem__(self, idx):
        item = super().__getitem__(idx)
        if isinstance(idx, int):
            self.draw_events.append((self.task_index, artifact_hash(item)))
            self.pending_parent = item
        return item


class TimedCredit:
    def __init__(self, lib):
        self.lib = lib
        self.recent = collections.deque(maxlen=PSIZE)
        self.pending = None
        self._m, self._d, self._m1 = physics.mutate, rm_fast.FastTask.dist, M1.mutate

    def __enter__(self):
        c = self

        def mutate(prog, rng, allowed=None):
            child = c._m(prog, rng, allowed)
            if c.lib.pending_parent is not None and prog is c.lib.pending_parent:
                c.pending = (artifact_hash(prog), child)
                c.lib.pending_parent = None
            return child

        def dist(ft, prog):
            d = c._d(ft, prog)
            if c.pending is not None and prog is c.pending[1]:
                if c.recent and d < statistics.median(c.recent):
                    c.lib.eff_events.append((c.lib.task_index, c.pending[0]))
                c.pending = None
            c.recent.append(d)
            return d

        physics.mutate = mutate
        M1.mutate = mutate
        rm_fast.FastTask.dist = dist
        return self

    def __exit__(self, *a):
        physics.mutate = self._m
        M1.mutate = self._m1
        rm_fast.FastTask.dist = self._d
        return False


def run(tasks, lineage, budget):
    lib = TimedLibrary()
    with TimedCredit(lib):
        for i, m in enumerate(tasks):
            t = gen_task(m['family'], m['seed'])
            v = {'domain': t['domain'], 'table': t['table']}
            lib.task_index = i
            res = M1.m1_rx(v, random.Random(700000 + 1000 * lineage + i),
                           budget, lib)
            adm = M1.admissions(res, v)
            for g in adm:
                lib.admit_task.setdefault(artifact_hash(g), i)
            M1.update_library(lib, adm)
    return lib


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lineages', type=int, default=5)
    ap.add_argument('--budget', type=int, default=30000)
    a = ap.parse_args()
    man = json.load(open(os.path.join(P.D5, 'results', 'task_manifest.json'),
                         encoding='utf-8'))
    tasks = [m for m in man['tasks'] if m['family'] in NC]

    print('ERGON GEN-1B PHASE 7 -- EXPERIENCE HALF-LIFE')
    print('=' * 70)
    print('observational pass, baseline policy, %d lineages x %d tasks\n'
          % (a.lineages, len(tasks)))

    gaps, first_use, n_uses, dormancy_revivals = [], [], [], 0
    per_art = []
    for L in range(a.lineages):
        lib = run(tasks, L, a.budget)
        eff_by = collections.defaultdict(list)
        for i, h in lib.eff_events:
            eff_by[h].append(i)
        draw_by = collections.defaultdict(list)
        for i, h in lib.draw_events:
            draw_by[h].append(i)
        for h, adm in lib.admit_task.items():
            uses = sorted(eff_by.get(h, []))
            draws = draw_by.get(h, [])
            n_uses.append(len(uses))
            if uses:
                first_use.append(uses[0] - adm)
                for x, y in zip(uses, uses[1:]):
                    gaps.append(y - x)
                if any((y - x) >= 5 for x, y in zip(uses, uses[1:])):
                    dormancy_revivals += 1
            per_art.append({'lineage': L, 'hash': h, 'admit': adm,
                            'n_eff': len(uses), 'n_draws': len(draws),
                            'first_eff_lag': (uses[0] - adm) if uses else None,
                            'last_eff': uses[-1] if uses else None,
                            'span': (uses[-1] - uses[0]) if len(uses) > 1 else 0})
        print('  lineage %d: artifacts %d | eff events %d | draw events %d'
              % (L, len(lib.admit_task), len(lib.eff_events),
                 len(lib.draw_events)))

    print('\n1. IS THERE A HALF-LIFE?')
    tot = len(per_art)
    ever = sum(1 for r in per_art if r['n_eff'] > 0)
    print('   artifacts %d | ever effectively used %d (%.0f%%)'
          % (tot, ever, 100 * ever / tot))
    if first_use:
        fu = sorted(first_use)
        print('   lag from admission to FIRST effective use (tasks):')
        print('     median %.0f   p75 %.0f   p90 %.0f   max %d'
              % (statistics.median(fu), fu[int(.75 * len(fu))],
                 fu[int(.90 * len(fu))], fu[-1]))
    if gaps:
        g = sorted(gaps)
        print('   gap BETWEEN consecutive effective uses (tasks):')
        print('     median %.0f   p75 %.0f   p90 %.0f   p99 %.0f   max %d'
              % (statistics.median(g), g[int(.75 * len(g))],
                 g[int(.90 * len(g))], g[int(.99 * len(g))], g[-1]))
        print('     gaps of 0 tasks (same-task reuse): %.1f%%'
              % (100 * sum(1 for x in g if x == 0) / len(g)))
        print('     gaps >= 5 tasks (dormant then revived): %.1f%%'
              % (100 * sum(1 for x in g if x >= 5) / len(g)))
    print('   artifacts showing a REVIVAL after >=5 dormant tasks: %d (%.1f%%)'
          % (dormancy_revivals, 100 * dormancy_revivals / max(1, ever)))

    # DISCRETE SURVIVAL HAZARD, computed correctly.
    # An earlier version binned artifacts by their FINAL use count and asked
    # whether they had "more", which is definitionally zero in every bin and
    # manufactured a spurious step at 2 uses. The right quantity is
    #     h(j) = P(n_eff >= j+1 | n_eff >= j)
    # estimated over the risk set that actually reached j uses.
    print('\n2. DISCRETE HAZARD  h(j) = P(reach use j+1 | reached use j)')
    counts = [r['n_eff'] for r in per_art]
    hazard = {}
    for j in range(0, 10):
        at_risk = sum(1 for c in counts if c >= j)
        went_on = sum(1 for c in counts if c >= j + 1)
        if at_risk >= 10:
            hazard[j] = {'at_risk': at_risk, 'continued': went_on,
                         'hazard': round(went_on / at_risk, 4)}
            print('   reached %d uses: risk set %4d -> continued %4d   '
                  'h(%d) = %.3f' % (j, at_risk, went_on, j, went_on / at_risk))
    inc = (hazard.get(4, {}).get('hazard', 0) >
           hazard.get(0, {}).get('hazard', 1))
    print('   -> hazard is %s in j: usefulness does NOT decay with use'
          % ('INCREASING' if inc else 'NOT increasing'))

    print('\n3. SUBPOPULATIONS')
    zero = [r for r in per_art if r['n_eff'] == 0]
    one = [r for r in per_art if r['n_eff'] == 1]
    many = [r for r in per_art if r['n_eff'] >= 5]
    print('   never used ...... %4d (%.0f%%)  median draws %.0f'
          % (len(zero), 100 * len(zero) / tot,
             statistics.median([r['n_draws'] for r in zero]) if zero else 0))
    print('   used once ....... %4d (%.0f%%)  median draws %.0f'
          % (len(one), 100 * len(one) / tot,
             statistics.median([r['n_draws'] for r in one]) if one else 0))
    print('   used 5+ times ... %4d (%.0f%%)  median draws %.0f  median span %.0f'
          % (len(many), 100 * len(many) / tot,
             statistics.median([r['n_draws'] for r in many]) if many else 0,
             statistics.median([r['span'] for r in many]) if many else 0))
    if n_uses:
        s = sorted(n_uses, reverse=True)
        top = sum(s[:max(1, len(s) // 10)])
        print('   CONCENTRATION: top 10%% of artifacts hold %.0f%% of all '
              'effective uses' % (100 * top / max(1, sum(s))))

    out = {'lineages': a.lineages, 'budget': a.budget, 'n_artifacts': tot,
           'ever_used': ever, 'ever_used_frac': round(ever / tot, 4),
           'first_use_lag_median': statistics.median(first_use) if first_use else None,
           'gap_median': statistics.median(gaps) if gaps else None,
           'gap_p90': sorted(gaps)[int(.9 * len(gaps))] if gaps else None,
           'gap_max': max(gaps) if gaps else None,
           'same_task_reuse_frac': (round(sum(1 for x in gaps if x == 0) / len(gaps), 4)
                                    if gaps else None),
           'dormant_revival_frac': (round(sum(1 for x in gaps if x >= 5) / len(gaps), 4)
                                    if gaps else None),
           'artifacts_with_revival': dormancy_revivals,
           'subpop': {'never': len(zero), 'once': len(one), 'five_plus': len(many)},
           'hazard': hazard,
           'top10pct_share_of_uses': (round(sum(sorted(n_uses, reverse=True)[:max(1, len(n_uses)//10)])
                                            / max(1, sum(n_uses)), 4) if n_uses else None)}
    json.dump(out, open(os.path.join(HERE, 'phase7_halflife.json'), 'w',
                        encoding='utf-8'), indent=2, sort_keys=True)
    print('\nwrote phase7_halflife.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())

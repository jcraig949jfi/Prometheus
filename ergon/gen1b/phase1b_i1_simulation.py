"""ERGON GEN-1B / PHASE 1b -- simulate the repaired I1 before preregistration.

Phase 1 found that behavioural duplicates are NOT evolutionarily redundant:
median mutational redundancy MR = 0.333, and at the preregistered tau = 0.50
only 23% of duplicate pairs share their offspring neighbourhoods. Median
genotype edit distance between behavioural duplicates is 20 of a maximum 24 --
they are almost entirely different programs that happen to compute the same
function on the shared domain.

So the brief's option A is taken: I1 evicts only when an artifact is redundant
BOTH behaviourally AND mutationally. Option B (evict on behaviour alone) is
also simulated, so the cost of the repair is visible rather than asserted.

ONLINE LEGITIMACY AND ITS PRICE. MR needs each artifact's offspring-behaviour
set. That is computed ONCE at admission as a SKETCH of K_SKETCH matched
mutations, cached, and reused at every later eviction decision. It uses only
the artifact and the frozen mutation operator -- no future information, no
oracle field. It is not free, and section 11 forbids free intelligence, so the
sketch cost is charged and reported.

Run:  python -m ergon.gen1b.phase1b_i1_simulation
"""
import collections
import json
import os
import random
import statistics
import sys

HERE = os.path.dirname(__file__)
D5 = os.path.abspath(os.path.join(HERE, '..', '..', 'agent_d5_blind'))
for _s in ('task_generators', 'substrate', 'mutation', 'exact_oracle'):
    sys.path.insert(0, os.path.join(D5, _s))
from families import gen_task      # noqa: E402
from physics import mutate         # noqa: E402
from rm_fast import FastTask       # noqa: E402

CORPUS = os.path.join(HERE, '..', 'gen1a', 'corpus')
CAP = 64
K_SKETCH = 32
SKETCH_SEED = 4242
TAU = 0.50


def sketch(g, ref):
    rng = random.Random(SKETCH_SEED)
    return frozenset(tuple(int(x) for x in ref.outputs(mutate(g, rng)))
                     for _ in range(K_SKETCH))


def jac(a, b):
    return len(a & b) / len(a | b) if (a | b) else 1.0


def load(L):
    ev = [json.loads(x) for x in
          open(os.path.join(CORPUS, 'lineage_%d_events.jsonl' % L),
               encoding='utf-8') if x.strip()]
    art = {a['hash']: a for a in
           (json.loads(x) for x in
            open(os.path.join(CORPUS, 'lineage_%d_artifacts.jsonl' % L),
                 encoding='utf-8') if x.strip())}
    dr = [json.loads(x) for x in
          open(os.path.join(CORPUS, 'lineage_%d_draws.jsonl' % L),
               encoding='utf-8') if x.strip()]
    return ev, art, dr


def simulate(stream, art, fps, sk, policy, rng):
    lib, seq, n = [], {}, 0
    evictions = 0
    fallbacks = 0
    snaps = {}
    for i, h in stream:
        if h in lib:
            lib.remove(h)
        n += 1
        seq[h] = n
        lib.append(h)
        while len(lib) > CAP:
            victim = None
            if policy == 'MRU':
                victim = lib[0]
            elif policy == 'BEHAV_ONLY':
                cnt = collections.Counter(fps[x] for x in lib)
                cands = [x for x in lib if cnt[fps[x]] > 1]
                victim = min(cands, key=lambda x: seq[x]) if cands else lib[0]
                if not cands:
                    fallbacks += 1
            elif policy == 'MUT_REDUNDANT':
                cnt = collections.defaultdict(list)
                for x in lib:
                    cnt[fps[x]].append(x)
                cands = []
                for fp, xs in cnt.items():
                    if len(xs) < 2:
                        continue
                    for a in range(len(xs)):
                        for b in range(a + 1, len(xs)):
                            if jac(sk[xs[a]], sk[xs[b]]) >= TAU:
                                cands.append(max(xs[a], xs[b], key=lambda y: -seq[y]))
                if cands:
                    victim = min(cands, key=lambda x: seq[x])
                else:
                    victim = lib[0]
                    fallbacks += 1
            lib.remove(victim)
            evictions += 1
        snaps[i] = set(lib)
    return {'final': set(lib), 'snaps': snaps, 'evictions': evictions,
            'fallbacks': fallbacks}


def main():
    man = json.load(open(os.path.join(D5, 'results', 'task_manifest.json'),
                         encoding='utf-8'))
    t0 = [m for m in man['tasks'] if m['family'] in ('F1', 'F2', 'F3', 'F4')][0]
    t = gen_task(t0['family'], t0['seed'])
    ref = FastTask({'domain': t['domain'], 'table': t['table']})

    print('ERGON GEN-1B PHASE 1b -- I1 SIMULATION BEFORE FREEZE')
    print('=' * 70)
    print('K_SKETCH %d, tau %.2f, cap %d\n' % (K_SKETCH, TAU, CAP))

    agg = collections.defaultdict(list)
    sketch_calls = 0
    for L in range(5):
        ev, art, dr = load(L)
        stream = [(e['i'], e['hash']) for e in ev if e['ev'] == 'admit']
        fps = {h: tuple(a['fingerprint']) for h, a in art.items()}
        sk = {}
        for h, a in art.items():
            sk[h] = sketch(tuple(tuple(i) for i in a['genotype']), ref)
            sketch_calls += K_SKETCH
        rng = random.Random(777 + L)
        res = {p: simulate(stream, art, fps, sk, p, rng)
               for p in ('MRU', 'BEHAV_ONLY', 'MUT_REDUNDANT')}
        base = res['MRU']
        for p in ('BEHAV_ONLY', 'MUT_REDUNDANT'):
            agg[p + '_term'].append(jac(base['final'], res[p]['final']))
            common = sorted(set(base['snaps']) & set(res[p]['snaps']))
            agg[p + '_traj'].append(statistics.mean(
                [jac(base['snaps'][i], res[p]['snaps'][i]) for i in common]))
            agg[p + '_fallback'].append(
                res[p]['fallbacks'] / max(1, res[p]['evictions']))
            # behavioural diversity of the terminal library
            agg[p + '_bdiv'].append(len({fps[x] for x in res[p]['final']})
                                    / len(res[p]['final']))
            # mutational-neighbourhood diversity: distinct offspring behaviours
            agg[p + '_mdiv'].append(len(set().union(*[sk[x] for x in res[p]['final']])))
        agg['MRU_bdiv'].append(len({fps[x] for x in base['final']})
                               / len(base['final']))
        agg['MRU_mdiv'].append(len(set().union(*[sk[x] for x in base['final']])))
        agg['evictions'].append(base['evictions'])

    print('DIVERGENCE FROM THE MRU BASELINE (mean over 5 lineages)')
    print('  policy            terminal J   trajectory J   MRU-fallback rate')
    for p in ('BEHAV_ONLY', 'MUT_REDUNDANT'):
        print('  %-16s  %.3f        %.3f          %.3f'
              % (p, statistics.mean(agg[p + '_term']),
                 statistics.mean(agg[p + '_traj']),
                 statistics.mean(agg[p + '_fallback'])))

    print('\nTERMINAL LIBRARY PROPERTIES (mean over 5 lineages)')
    print('  policy            behavioural diversity   distinct offspring behaviours')
    for p in ('MRU', 'BEHAV_ONLY', 'MUT_REDUNDANT'):
        print('  %-16s  %.3f                   %.0f'
              % (p, statistics.mean(agg[p + '_bdiv']),
                 statistics.mean(agg[p + '_mdiv'])))

    mr_term = statistics.mean(agg['MUT_REDUNDANT_term'])
    bo_term = statistics.mean(agg['BEHAV_ONLY_term'])
    ceremonial = mr_term > 0.90
    print('\n  sketch cost: %d extra mutations + fingerprint evaluations over 5'
          ' lineages (%d per lineage)' % (sketch_calls, sketch_calls // 5))
    print('\nVERDICT')
    if ceremonial:
        v = ('I1_CEREMONIAL -- the repaired rule falls back to MRU too often to '
             'diverge; drop the arm rather than run it.')
    else:
        v = ('I1_VIABLE -- the repaired rule diverges materially from baseline '
             'and is worth a scored arm.')
    print('  %s' % v)
    print('  MUT_REDUNDANT terminal overlap %.3f vs BEHAV_ONLY %.3f'
          % (mr_term, bo_term))

    json.dump({'K_sketch': K_SKETCH, 'tau': TAU,
               'sketch_mutations_total': sketch_calls,
               'sketch_mutations_per_lineage': sketch_calls // 5,
               'mut_redundant': {
                   'terminal_jaccard': round(mr_term, 4),
                   'trajectory_jaccard': round(
                       statistics.mean(agg['MUT_REDUNDANT_traj']), 4),
                   'mru_fallback_rate': round(
                       statistics.mean(agg['MUT_REDUNDANT_fallback']), 4)},
               'behav_only': {
                   'terminal_jaccard': round(bo_term, 4),
                   'trajectory_jaccard': round(
                       statistics.mean(agg['BEHAV_ONLY_traj']), 4),
                   'mru_fallback_rate': round(
                       statistics.mean(agg['BEHAV_ONLY_fallback']), 4)},
               'terminal_behavioural_diversity': {
                   p: round(statistics.mean(agg[p + '_bdiv']), 4)
                   for p in ('MRU', 'BEHAV_ONLY', 'MUT_REDUNDANT')},
               'terminal_offspring_behaviours': {
                   p: round(statistics.mean(agg[p + '_mdiv']), 1)
                   for p in ('MRU', 'BEHAV_ONLY', 'MUT_REDUNDANT')},
               'verdict': v.split(' -- ')[0]},
              open(os.path.join(HERE, 'phase1b_i1_simulation.json'), 'w',
                   encoding='utf-8'), indent=2, sort_keys=True)
    print('\nwrote phase1b_i1_simulation.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())

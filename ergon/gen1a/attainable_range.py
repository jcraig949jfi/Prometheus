"""ERGON GEN-1A / section 5 -- the full attainable-range analysis.

Question the brief sets: CAN TWO LEGITIMATE POLICIES ACTUALLY PRODUCE
DIFFERENT LIBRARIES? The 2.67x turnover figure from Gen-1 established only
OPPORTUNITY for divergence. This measures actual divergence.

METHOD AND ITS HONEST LIMIT. Every eviction policy is replayed over the SAME
recorded admission stream from the baseline corpus run. That is what the brief
permits -- simulate over the historical admissible sequence -- and it does NOT
pretend to know the counterfactual search trajectory. In a live run each policy
would induce its own stream (Gen-1 finding 2: exact stream freezing is
architecturally impossible), so the divergences reported here are the
SHARED-STREAM component only. They are a LOWER BOUND on how different two
libraries would actually become, because a live run adds trajectory divergence
on top. Stated as a limit, not buried.

Policies simulated (eviction only; admission is frozen D-5 throughout, per the
Gen-1A ruling):
    MRU      inherited D-5: most-recent-first eviction (evict oldest)
    RANDOM   evict a uniformly random resident
    LRU_DRAW evict the resident with fewest raw draws (the age proxy)
    EFFUSE   evict the resident with fewest EFFECTIVE uses
    RETIRE_N retire residents with zero effective uses after N draw
             opportunities, else fall back to MRU

Run:  python -m ergon.gen1a.attainable_range
"""
import collections
import json
import os
import random
import statistics
import sys

HERE = os.path.dirname(__file__)
CORPUS = os.path.join(HERE, 'corpus')
CAP = 64


def load_lineage(L):
    ev = [json.loads(x) for x in
          open(os.path.join(CORPUS, 'lineage_%d_events.jsonl' % L),
               encoding='utf-8') if x.strip()]
    art = {a['hash']: a for a in
           (json.loads(x) for x in
            open(os.path.join(CORPUS, 'lineage_%d_artifacts.jsonl' % L),
                 encoding='utf-8') if x.strip())}
    draws = [json.loads(x) for x in
             open(os.path.join(CORPUS, 'lineage_%d_draws.jsonl' % L),
                  encoding='utf-8') if x.strip()]
    return ev, art, draws


def admission_stream(ev):
    """(task_index, hash) in order, exactly as the baseline admitted them."""
    return [(e['i'], e['hash']) for e in ev if e['ev'] == 'admit']


def simulate(stream, art, draws_by_task, policy, rng, retire_n=200):
    """Replay the admission stream under one eviction policy.

    Draw pressure is applied per task from the recorded draw log so that
    usage-based policies have a mechanically available online signal. Ties are
    broken deterministically by insertion order, per the arm requirements.
    """
    lib = []                       # list of hashes, oldest first (D-5 order)
    seq = collections.Counter()    # arrival order for deterministic tiebreak
    draws = collections.Counter()
    eff = collections.Counter()
    opportunities = collections.Counter()
    n = 0
    snapshots = {}
    evictions = 0
    retired = 0

    for i, h in stream:
        # apply this task's draw pressure to the CURRENT residents
        for d in draws_by_task.get(i, []):
            if d in draws:          # only credit residents we are tracking
                pass
        for res in lib:
            opportunities[res] += draws_by_task.get(i, {}).get(res, 0)
            draws[res] += draws_by_task.get(i, {}).get(res, 0)
            a = art.get(res)
            if a and a['draws']:
                # effective share observed in the baseline, applied pro-rata
                share = a['effective_uses'] / max(1, a['draws'])
                eff[res] += draws_by_task.get(i, {}).get(res, 0) * share

        if h in lib:
            lib.remove(h)           # frozen dedupe semantics
        n += 1
        seq[h] = n
        lib.append(h)

        if policy == 'RETIRE_N':
            doomed = [x for x in lib[:-1]
                      if opportunities[x] >= retire_n and eff[x] < 1.0]
            for x in doomed:
                lib.remove(x)
                retired += 1

        while len(lib) > CAP:
            if policy == 'MRU':
                victim = lib[0]
            elif policy == 'RANDOM':
                victim = lib[rng.randrange(len(lib))]
            elif policy == 'LRU_DRAW':
                victim = min(lib, key=lambda x: (draws[x], seq[x]))
            elif policy in ('EFFUSE', 'RETIRE_N'):
                victim = min(lib, key=lambda x: (eff[x], seq[x]))
            else:
                raise ValueError(policy)
            lib.remove(victim)
            evictions += 1
        snapshots[i] = set(lib)
    return {'final': set(lib), 'snapshots': snapshots,
            'evictions': evictions, 'retired': retired,
            'eff': eff, 'draws': draws}


def jaccard(a, b):
    return len(a & b) / len(a | b) if (a | b) else 1.0


def main():
    if not os.path.isdir(CORPUS):
        print('corpus missing; run ergon.gen1a.corpus_run first')
        return 1
    lineages = sorted(int(f.split('_')[1]) for f in os.listdir(CORPUS)
                      if f.endswith('_events.jsonl'))
    policies = ['MRU', 'RANDOM', 'LRU_DRAW', 'EFFUSE', 'RETIRE_N']
    agg = collections.defaultdict(list)
    art_all = {}
    print('ERGON GEN-1A -- ATTAINABLE POLICY RANGE (section 5)')
    print('=' * 70)

    for Lx in lineages:
        ev, art, draws = load_lineage(Lx)
        art_all.update(art)
        stream = admission_stream(ev)
        dbt = collections.defaultdict(collections.Counter)
        for d in draws:
            dbt[d['i']][d['hash']] += 1
        rng = random.Random(1234 + Lx)
        res = {p: simulate(stream, art, dbt, p, rng) for p in policies}
        base = res['MRU']
        for p in policies:
            if p == 'MRU':
                continue
            term = jaccard(base['final'], res[p]['final'])
            common = sorted(set(base['snapshots']) & set(res[p]['snapshots']))
            traj = statistics.mean([jaccard(base['snapshots'][i],
                                            res[p]['snapshots'][i])
                                    for i in common]) if common else 1.0
            agg[p + '_terminal'].append(term)
            agg[p + '_trajectory'].append(traj)
        agg['n_admissions'].append(len(stream))
        agg['n_evictions'].append(base['evictions'])
        agg['n_retired'].append(res['RETIRE_N']['retired'])

    print('admission stream: %.0f artifacts/lineage, %.0f evictions/lineage'
          % (statistics.mean(agg['n_admissions']),
             statistics.mean(agg['n_evictions'])))
    print('turnover: %.2fx the 64-slot cap\n'
          % (statistics.mean(agg['n_evictions']) / CAP))

    print('LIBRARY DIVERGENCE FROM THE INHERITED MRU BASELINE')
    print('(Jaccard 1.00 = identical library, 0.00 = disjoint)')
    print('  policy      terminal overlap    mean trajectory overlap')
    out = {'policies': {}}
    for p in policies:
        if p == 'MRU':
            continue
        t = statistics.mean(agg[p + '_terminal'])
        j = statistics.mean(agg[p + '_trajectory'])
        out['policies'][p] = {'terminal_jaccard': round(t, 4),
                              'trajectory_jaccard': round(j, 4)}
        print('  %-10s  %.3f               %.3f' % (p, t, j))
    print('\n  RETIRE_N fired %.1f retirements/lineage'
          % statistics.mean(agg['n_retired']))

    # artifact-property variation: the raw material any policy must exploit
    ds = [a['draws'] for a in art_all.values()]
    es = [a['effective_uses'] for a in art_all.values()]
    ls = [a['len'] for a in art_all.values()]
    fps = collections.Counter(tuple(a['fingerprint']) for a in art_all.values())
    print('\nARTIFACT PROPERTY VARIATION over %d distinct artifacts'
          % len(art_all))

    def desc(name, xs):
        xs = sorted(xs)
        z = sum(1 for x in xs if x == 0)
        print('  %-18s min %-5s med %-6s max %-6s mean %-7.2f zero %d (%.0f%%)'
              % (name, xs[0], statistics.median(xs), xs[-1],
                 statistics.mean(xs), z, 100 * z / len(xs)))
        return {'min': xs[0], 'median': statistics.median(xs), 'max': xs[-1],
                'mean': round(statistics.mean(xs), 3), 'zero_count': z,
                'zero_frac': round(z / len(xs), 4)}

    out['artifacts'] = {'n_distinct': len(art_all),
                        'draws': desc('raw draws', ds),
                        'effective_uses': desc('effective uses', es),
                        'genotype_len': desc('genotype length', ls)}
    dup = sum(c - 1 for c in fps.values() if c > 1)
    out['artifacts']['distinct_fingerprints'] = len(fps)
    out['artifacts']['behaviourally_redundant'] = dup
    print('  distinct behaviour fingerprints %d of %d artifacts '
          '(%d behaviourally redundant)' % (len(fps), len(art_all), dup))

    maxdiv = max(out['policies'][p]['terminal_jaccard'] for p in out['policies'])
    mindiv = min(out['policies'][p]['terminal_jaccard'] for p in out['policies'])
    verdict = ('RETENTION_POLICY_RANGE_EFFECTIVELY_ZERO' if mindiv > 0.90
               else 'RETENTION_POLICY_RANGE_NONTRIVIAL')
    out['verdict'] = verdict
    out['most_similar_policy_terminal_jaccard'] = maxdiv
    out['most_divergent_policy_terminal_jaccard'] = mindiv
    print('\nVERDICT: %s' % verdict)
    print('  most divergent policy retains only %.0f%% overlap with baseline'
          % (100 * mindiv))
    json.dump(out, open(os.path.join(HERE, 'attainable_range_2026-09-01.json'),
                        'w', encoding='utf-8'), indent=2, sort_keys=True)
    print('wrote attainable_range_2026-09-01.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())

"""ERGON GEN-1B / PHASE 2 -- effective-usage opportunity audit.

Gen-1A showed raw draws are non-discriminating (4% zero) while effective uses
are dispersed (42% zero), and concluded effective usage is the better sorting
signal. That established DISPERSION. It did not establish that an ABSOLUTE
effective-use count is free of exposure bias.

The worry is concrete and mechanical: an artifact admitted early sits in the
library longer, is drawn more often, and therefore accumulates more effective
uses without being any better per draw. If that is what drives the counter,
then I2 EFFECTIVE_USAGE is a residence signal wearing a utility name -- the
exact failure the Gen-1 packet caught in the raw-draw version of the same idea.

Diagnostic only. No policy is tuned to CFR here; Gen-1 has not run.

Run:  python -m ergon.gen1b.phase2_effective_usage_audit
"""
import collections
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(__file__)
CORPUS = os.path.join(HERE, '..', 'gen1a', 'corpus')


def load():
    arts, events, draws = {}, [], []
    for L in range(5):
        for line in open(os.path.join(CORPUS, 'lineage_%d_artifacts.jsonl' % L),
                         encoding='utf-8'):
            if line.strip():
                a = json.loads(line)
                a['lineage'] = L
                arts[(L, a['hash'])] = a
        for line in open(os.path.join(CORPUS, 'lineage_%d_events.jsonl' % L),
                         encoding='utf-8'):
            if line.strip():
                e = json.loads(line)
                e['lineage'] = L
                events.append(e)
        for line in open(os.path.join(CORPUS, 'lineage_%d_draws.jsonl' % L),
                         encoding='utf-8'):
            if line.strip():
                d = json.loads(line)
                d['lineage'] = L
                draws.append(d)
    return arts, events, draws


def spearman(xs, ys):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = rank(xs), rank(ys)
    n = len(xs)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    den = math.sqrt(sum((rx[i] - mx) ** 2 for i in range(n)) *
                    sum((ry[i] - my) ** 2 for i in range(n)))
    return num / den if den else 0.0


def main():
    arts, events, draws = load()
    print('ERGON GEN-1B PHASE 2 -- EFFECTIVE-USAGE OPPORTUNITY AUDIT')
    print('=' * 70)
    print('artifact-lineage records %d | events %d | draw records %d\n'
          % (len(arts), len(events), len(draws)))

    # residence: admission task -> eviction task (or end of lineage)
    last_task = collections.defaultdict(int)
    for e in events:
        last_task[e['lineage']] = max(last_task[e['lineage']], e.get('i', 0))
    evicted_at = {}
    for e in events:
        if e['ev'] == 'evict':
            evicted_at[(e['lineage'], e['hash'])] = e['i']

    rows = []
    for (L, h), a in arts.items():
        adm = a['first_admit_task']
        ev = evicted_at.get((L, h))
        end = ev if ev is not None else last_task[L]
        rows.append({
            'lineage': L, 'hash': h,
            'draws': a['draws'], 'eff': a['effective_uses'],
            'admit': adm, 'residence': max(0, end - adm),
            'evicted': ev is not None,
            'len': a['len'], 'family': a['first_admit_family'],
            'solver': bool(a['was_solver']),
            'rate': a['effective_uses'] / a['draws'] if a['draws'] else 0.0,
        })

    D = [r['draws'] for r in rows]
    E = [r['eff'] for r in rows]
    R = [r['residence'] for r in rows]
    A = [r['admit'] for r in rows]

    print('1. IS THE COUNTER AN EXPOSURE SIGNAL? (Spearman rank correlations)')
    print('   effective_uses  vs  draw opportunities .... %+.3f' % spearman(E, D))
    print('   effective_uses  vs  residence (tasks) ..... %+.3f' % spearman(E, R))
    print('   effective_uses  vs  admission position .... %+.3f' % spearman(E, A))
    print('   draws           vs  residence ............. %+.3f' % spearman(D, R))
    print('   RATE (eff/draw) vs  draw opportunities .... %+.3f' % spearman(
        [r['rate'] for r in rows], D))
    print('   RATE            vs  residence ............. %+.3f' % spearman(
        [r['rate'] for r in rows], R))

    # zero-effective-use artifacts: inert or underexposed?
    z = [r for r in rows if r['eff'] == 0]
    nz = [r for r in rows if r['eff'] > 0]
    print('\n2. THE ZERO-EFFECTIVE-USE POPULATION  (%d of %d, %.0f%%)'
          % (len(z), len(rows), 100 * len(z) / len(rows)))
    print('   median draw opportunities   zero-eff %6.0f   nonzero-eff %6.0f'
          % (statistics.median([r['draws'] for r in z]),
             statistics.median([r['draws'] for r in nz])))
    print('   median residence (tasks)    zero-eff %6.1f   nonzero-eff %6.1f'
          % (statistics.median([r['residence'] for r in z]),
             statistics.median([r['residence'] for r in nz])))
    print('   median admission position   zero-eff %6.1f   nonzero-eff %6.1f'
          % (statistics.median([r['admit'] for r in z]),
             statistics.median([r['admit'] for r in nz])))
    n_well = sum(1 for r in z if r['draws'] >= 100)
    print('   zero-eff artifacts WITH >=100 draw opportunities: %d of %d (%.0f%%)'
          % (n_well, len(z), 100 * n_well / max(1, len(z))))

    # matched-opportunity comparison: P(>=1 effective use) within draw bins
    print('\n3. P(at least one effective use) WITHIN MATCHED OPPORTUNITY BINS')
    bins = [(0, 0), (1, 49), (50, 149), (150, 299), (300, 599), (600, 10 ** 9)]
    binrows = []
    for lo, hi in bins:
        sel = [r for r in rows if lo <= r['draws'] <= hi]
        if not sel:
            continue
        p = sum(1 for r in sel if r['eff'] > 0) / len(sel)
        mr = statistics.median([r['rate'] for r in sel])
        binrows.append({'lo': lo, 'hi': hi, 'n': len(sel),
                        'p_any_effective': round(p, 4),
                        'median_rate': round(mr, 5)})
        label = '%d-%s' % (lo, 'inf' if hi > 10 ** 8 else hi)
        print('   draws %-10s n %4d   P(>=1 eff) %.3f   median rate %.4f'
              % (label, len(sel), p, mr))

    spread = ([b['p_any_effective'] for b in binrows if b['n'] >= 20])
    print('\n   P(>=1 eff) ranges %.3f to %.3f across bins with n>=20'
          % (min(spread), max(spread)))

    # empirical-Bayes shrunk rate
    tot_e = sum(E)
    tot_d = sum(D)
    prior = tot_e / tot_d if tot_d else 0.0
    m = statistics.median([r['draws'] for r in rows if r['draws'] > 0])
    for r in rows:
        r['eb'] = (r['eff'] + prior * m) / (r['draws'] + m)
    print('\n4. EMPIRICAL-BAYES SHRUNK RATE (prior rate %.5f, pseudo-count %.0f)'
          % (prior, m))
    print('   EB rate vs raw count  Spearman %+.3f'
          % spearman([r['eb'] for r in rows], E))
    print('   EB rate vs draws      Spearman %+.3f'
          % spearman([r['eb'] for r in rows], D))

    # rank disagreement between candidate credit definitions
    def bottom_k(key, k=64):
        return {(r['lineage'], r['hash'])
                for r in sorted(rows, key=lambda r: (r[key], r['admit']))[:k]}
    b_count = bottom_k('eff')
    b_rate = bottom_k('rate')
    b_eb = bottom_k('eb')
    print('\n5. WOULD THE DEFINITIONS EVICT THE SAME ARTIFACTS?')
    print('   bottom-64 by COUNT vs by RATE : overlap %d/64'
          % len(b_count & b_rate))
    print('   bottom-64 by COUNT vs by EB   : overlap %d/64'
          % len(b_count & b_eb))
    print('   bottom-64 by RATE  vs by EB   : overlap %d/64'
          % len(b_rate & b_eb))

    exposure_driven = abs(spearman(E, D)) > 0.5
    print('\nVERDICT')
    if exposure_driven:
        v = ('EFFECTIVE_USE_COUNT_IS_EXPOSURE_CONFOUNDED -- absolute counts '
             'track opportunity strongly; the credit definition needs '
             'opportunity normalisation to deserve the name.')
    else:
        v = ('EFFECTIVE_USE_COUNT_DEFENSIBLE -- absolute counts are not '
             'dominated by exposure; the counter is measuring something other '
             'than how long an artifact sat in the library.')
    print('  %s' % v)

    out = {'n_records': len(rows),
           'spearman': {
               'eff_vs_draws': round(spearman(E, D), 4),
               'eff_vs_residence': round(spearman(E, R), 4),
               'eff_vs_admit_position': round(spearman(E, A), 4),
               'draws_vs_residence': round(spearman(D, R), 4),
               'rate_vs_draws': round(spearman([r['rate'] for r in rows], D), 4),
               'rate_vs_residence': round(spearman([r['rate'] for r in rows], R), 4)},
           'zero_effective': {
               'n': len(z), 'frac': round(len(z) / len(rows), 4),
               'median_draws': statistics.median([r['draws'] for r in z]),
               'median_draws_nonzero': statistics.median([r['draws'] for r in nz]),
               'median_residence': statistics.median([r['residence'] for r in z]),
               'median_residence_nonzero': statistics.median(
                   [r['residence'] for r in nz]),
               'well_exposed_count': n_well,
               'well_exposed_frac': round(n_well / max(1, len(z)), 4)},
           'opportunity_bins': binrows,
           'empirical_bayes': {'prior_rate': round(prior, 6),
                               'pseudo_count': m},
           'bottom64_overlap': {
               'count_vs_rate': len(b_count & b_rate),
               'count_vs_eb': len(b_count & b_eb),
               'rate_vs_eb': len(b_rate & b_eb)},
           'verdict': v.split(' -- ')[0]}
    json.dump(out, open(os.path.join(HERE, 'phase2_effective_usage_audit.json'),
                        'w', encoding='utf-8'), indent=2, sort_keys=True)
    print('\nwrote phase2_effective_usage_audit.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())

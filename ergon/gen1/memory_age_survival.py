"""Ergon Gen-1: MEMORY-AGE SURVIVAL CURVE BY POLICY.

Mandated by external review, 2026-09-02, as the mechanism test that the newly
persisted trajectory makes possible. Committed BEFORE any treatment arm has
run, so the baseline reference curve is frozen ahead of the comparison.

THE POINT. Terminal library composition -- which 64 genotypes are present at
the end -- is a weak readout. It cannot distinguish these three worlds:

  1. a policy raises CFR without extending useful memory age
     -> long-term retention is NOT the mechanism
  2. a policy grows a long tail of old survivors that are never drawn
     -> persistence alone is NOT the mechanism
  3. old, selectively preserved artifacts are drawn AND carry downstream
     credit -> selective memory is doing work

Reported per policy:
  P(resident originated > 16 tasks ago)     the baseline's own horizon
  P(resident originated > 32 tasks ago)     twice it
  max survivor age
  median resident age, post-saturation
  DRAW MASS attributable to residents older than 16 / 32 tasks

The draw-mass line is the one that separates world 2 from world 3, and it is
only computable because library draws were recorded.

INPUT. A corpus directory holding lineage_<j>_events.jsonl (admit/evict/
task_begin) and, optionally, lineage_<j>_draws.jsonl. This is the schema the
Gen-1A instance emits; that corpus is the I0 baseline, so running this with no
arguments produces the BASELINE REFERENCE CURVE.
"""
import argparse
import json
import os

DEFAULT_CORPUS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              '..', 'gen1a', 'corpus')
AGE_CUTS = (16, 32)


def _load(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f]


def residency(events):
    """(hash, admit_task, evict_task_or_None) for every residency episode.

    An artifact readmitted after eviction has two episodes; readmission while
    resident refreshes recency but is NOT a new episode, matching
    update_library's move-to-end.
    """
    open_ep = {}
    episodes = []
    last_task = 0
    for e in events:
        i = e.get('i', 0)
        last_task = max(last_task, i)
        if e['ev'] == 'admit':
            if e['hash'] not in open_ep:
                open_ep[e['hash']] = i
        elif e['ev'] == 'evict':
            start = open_ep.pop(e['hash'], None)
            if start is not None:
                episodes.append((e['hash'], start, i))
    for h, start in open_ep.items():
        episodes.append((h, start, None))
    if not episodes:
        raise ValueError('no residency episodes -- refusing a vacuous curve')
    return episodes, last_task


def age_of(episodes, h, i):
    """Age of hash h at task i, or None if not resident then."""
    for eh, start, end in episodes:
        if eh == h and start <= i and (end is None or i < end):
            return i - start
    return None


def analyse_lineage(corpus, j):
    events = _load(os.path.join(corpus, 'lineage_%d_events.jsonl' % j))
    if events is None:
        return None
    episodes, last_task = residency(events)
    draws = _load(os.path.join(corpus, 'lineage_%d_draws.jsonl' % j))

    saturation = None
    sizes = {}
    for i in range(last_task + 1):
        n = sum(1 for _h, s, e in episodes if s <= i and (e is None or i < e))
        sizes[i] = n
        if saturation is None and n >= 64:
            saturation = i

    ages_post_sat = []
    over = {c: 0 for c in AGE_CUTS}
    total_resident = 0
    start_at = saturation if saturation is not None else 0
    for i in range(start_at, last_task + 1):
        for _h, s, e in episodes:
            if s <= i and (e is None or i < e):
                a = i - s
                ages_post_sat.append(a)
                total_resident += 1
                for c in AGE_CUTS:
                    if a > c:
                        over[c] += 1

    draw_mass = None
    if draws:
        counts = {c: 0 for c in AGE_CUTS}
        n_aged = 0
        for d in draws:
            a = age_of(episodes, d['hash'], d['i'])
            if a is None:
                continue
            n_aged += 1
            for c in AGE_CUTS:
                if a > c:
                    counts[c] += 1
        if n_aged:
            draw_mass = {'n_draws_resolved': n_aged,
                         **{'frac_draws_older_than_%d' % c: counts[c] / n_aged
                            for c in AGE_CUTS}}

    ages_post_sat.sort()
    return {
        'lineage': j,
        'n_tasks': last_task + 1,
        'saturation_task': saturation,
        'n_episodes': len(episodes),
        'max_survivor_age': max(a for _h, s, e in episodes
                                for a in [( (e - 1) if e is not None
                                            else last_task) - s]),
        'median_resident_age_post_saturation':
            ages_post_sat[len(ages_post_sat) // 2] if ages_post_sat else None,
        **{'p_resident_older_than_%d' % c:
           (over[c] / total_resident if total_resident else None)
           for c in AGE_CUTS},
        'draw_mass': draw_mass,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--corpus', default=DEFAULT_CORPUS)
    ap.add_argument('--policy', default='I0_D5_BASELINE_MRU')
    ap.add_argument('--lineages', default='0,1,2,3,4')
    args = ap.parse_args()

    rows = []
    for j in [int(x) for x in args.lineages.split(',')]:
        r = analyse_lineage(args.corpus, j)
        if r is not None:
            rows.append(r)
    if not rows:
        raise ValueError('no lineages found under %s' % args.corpus)

    print('=== MEMORY-AGE SURVIVAL CURVE -- policy %s ===' % args.policy)
    print('corpus: %s\n' % os.path.normpath(args.corpus))
    hdr = ('lin  tasks  sat  maxAge  medAge  P(>16)  P(>32)  '
           'draws>16  draws>32')
    print(hdr)
    print('-' * len(hdr))
    for r in rows:
        dm = r['draw_mass'] or {}
        print('%3d  %5d  %3s  %6d  %6s  %6.3f  %6.3f  %8s  %8s'
              % (r['lineage'], r['n_tasks'], r['saturation_task'],
                 r['max_survivor_age'],
                 r['median_resident_age_post_saturation'],
                 r['p_resident_older_than_16'], r['p_resident_older_than_32'],
                 ('%.4f' % dm['frac_draws_older_than_16']
                  if 'frac_draws_older_than_16' in dm else 'n/a'),
                 ('%.4f' % dm['frac_draws_older_than_32']
                  if 'frac_draws_older_than_32' in dm else 'n/a')))

    n = len(rows)
    print('\nmean P(resident older than 16 tasks) ... %.4f'
          % (sum(r['p_resident_older_than_16'] for r in rows) / n))
    print('mean P(resident older than 32 tasks) ... %.4f'
          % (sum(r['p_resident_older_than_32'] for r in rows) / n))
    print('max survivor age, any lineage ......... %d'
          % max(r['max_survivor_age'] for r in rows))
    if rows[0]['draw_mass']:
        print('mean draw mass to residents >16 tasks .. %.4f'
              % (sum(r['draw_mass']['frac_draws_older_than_16']
                     for r in rows) / n))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       'memory_age_survival_%s.json' % args.policy)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump({'policy': args.policy, 'corpus': os.path.normpath(args.corpus),
                   'age_cuts': list(AGE_CUTS), 'lineages': rows}, f, indent=1)
        f.flush()
    print('\nwrote', out)


if __name__ == '__main__':
    main()

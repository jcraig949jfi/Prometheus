"""ERGON PROJECT 1 -- the frozen analysis and decision rule.

Implements PREREG_P1_2026-09-01.txt exactly. Written and committed before any
result file is opened.

    endpoint      per-lineage CFR over the frozen 42-task battery
    unit          LINEAGE
    contrast      I1 MUT_REDUNDANT - I3 RANDOM, the ONLY contrast
    test          two-sided paired sign-flip permutation, 50,000 draws,
                  seed 909090
    multiplicity  NONE (one preregistered contrast)
    CI            95% percentile bootstrap over LINEAGES, 20,000 draws
    threshold     T = 2.00 pp, strategic not statistical

DECISION RULE, complete and exhaustive, fixed in the prereg:

    p < 0.05 and d >= T .................. SELECTION_BEATS_CHURN
    p < 0.05 and 0 < d < T ............... SELECTION_EFFECT_BELOW_USEFUL_SCALE
    p >= 0.05 and CI_hi < T .............. SELECTION_NOT_DISTINGUISHABLE_FROM_CHURN
    p >= 0.05 and CI_hi >= T ............. UNDERPOWERED
    p < 0.05 and d < 0 ................... CHURN_BEATS_SELECTION

Run:  python -m ergon.gen2.p1_analyze
"""
import json
import math
import os
import random
import statistics
import sys

HERE = os.path.dirname(__file__)
RES = os.path.join(HERE, 'p1_results')
ARMS = ('I1', 'I3')
NAMES = {'I1': 'MUT_REDUNDANT', 'I3': 'RANDOM'}
N_PERM = 50000
PERM_SEED = 909090
N_BOOT = 20000
T = 0.020
ALPHA = 0.05


def load():
    S = {a: {} for a in ARMS}
    for f in os.listdir(RES):
        if f.startswith('summary_'):
            _, arm, L = f[:-5].split('_')
            S[arm][int(L)] = json.load(open(os.path.join(RES, f),
                                            encoding='utf-8'))
    return S


def perm_p(d, rng):
    obs = sum(d) / len(d)
    ge = 0
    for _ in range(N_PERM):
        m = sum(x if rng.random() < 0.5 else -x for x in d) / len(d)
        if abs(m) >= abs(obs):
            ge += 1
    return obs, (ge + 1) / (N_PERM + 1)


def boot_ci(d, rng, lo=2.5, hi=97.5):
    n = len(d)
    ms = sorted(sum(d[rng.randrange(n)] for _ in range(n)) / n
                for _ in range(N_BOOT))
    return ms[int(lo / 100 * N_BOOT)], ms[int(hi / 100 * N_BOOT)]


def main():
    S = load()
    lins = sorted(set(S['I1']) & set(S['I3']))
    n = len(lins)
    rng = random.Random(PERM_SEED)

    print('ERGON PROJECT 1 -- ARBITRARY-MEMORY DECISION')
    print('=' * 70)
    print('paired lineages: %d (preregistered 100)' % n)
    print('threshold T = %.2f pp, frozen before data\n' % (100 * T))

    caps = {len(S[a][L]['final_library']) for a in ARMS for L in lins}
    tasks = {S[a][L]['n_tasks'] for a in ARMS for L in lins}
    print('validity: library sizes %s | task counts %s' % (sorted(caps),
                                                           sorted(tasks)))
    if caps != {64} or tasks != {42}:
        print('*** VALIDITY VIOLATION -- see prereg section 7 ***')

    cfr = {a: [S[a][L]['cfr'] for L in lins] for a in ARMS}
    for a in ARMS:
        v = cfr[a]
        print('  %-3s %-16s mean %.4f  sd %.4f  min %.3f  max %.3f'
              % (a, NAMES[a], statistics.mean(v), statistics.stdev(v),
                 min(v), max(v)))

    d = [cfr['I1'][i] - cfr['I3'][i] for i in range(n)]
    obs, p = perm_p(d, rng)
    lo, hi = boot_ci(d, rng)
    se = statistics.stdev(d) / math.sqrt(n)
    pos = sum(1 for x in d if x > 0)
    neg = sum(1 for x in d if x < 0)

    print('\nPRIMARY CONTRAST  I1 - I3  (the only contrast; no correction)')
    print('  mean   %+.4f  (%+.2f pp)' % (obs, 100 * obs))
    print('  SE     %.4f' % se)
    print('  95%% CI [%+.4f, %+.4f]  =  [%+.2f, %+.2f] pp'
          % (lo, hi, 100 * lo, 100 * hi))
    print('  p      %.5f  (two-sided paired sign-flip, %d draws)'
          % (p, N_PERM))
    print('  signs  %d positive, %d negative, %d tied of %d'
          % (pos, neg, n - pos - neg, n))

    if p < ALPHA and obs < 0:
        verdict = 'CHURN_BEATS_SELECTION'
        why = ('the arbitrary comparator is significantly BETTER; named in '
               'the prereg in advance as a possible outcome')
    elif p < ALPHA and obs >= T:
        verdict = 'SELECTION_BEATS_CHURN'
        why = ('significant and at or above the strategic threshold of '
               '%.2f pp' % (100 * T))
    elif p < ALPHA:
        verdict = 'SELECTION_EFFECT_BELOW_USEFUL_SCALE'
        why = ('a real effect, but smaller than %.2f pp -- it cannot reliably '
               'move even one task in forty-two' % (100 * T))
    elif hi < T:
        verdict = 'SELECTION_NOT_DISTINGUISHABLE_FROM_CHURN'
        why = ('a BOUNDED null: the 95%% CI upper bound %.2f pp excludes a '
               'strategically meaningful effect' % (100 * hi))
    else:
        verdict = 'UNDERPOWERED'
        why = ('the CI upper bound %.2f pp does not exclude a meaningful '
               'effect' % (100 * hi))

    print('\nVERDICT: %s' % verdict)
    print('  %s' % why)

    out = {'n_lineages': n, 'threshold_pp': 100 * T,
           'arm_mean_cfr': {a: round(statistics.mean(cfr[a]), 5) for a in ARMS},
           'arm_sd_cfr': {a: round(statistics.stdev(cfr[a]), 5) for a in ARMS},
           'arm_cfr_by_lineage': {a: [round(v, 5) for v in cfr[a]]
                                  for a in ARMS},
           'lineage_ids': lins,
           'deltas': [round(v, 6) for v in d],
           'mean': obs, 'se': se, 'ci95': [lo, hi], 'p': p,
           'signs': {'pos': pos, 'neg': neg, 'tied': n - pos - neg},
           'n_perm': N_PERM, 'perm_seed': PERM_SEED,
           'verdict': verdict, 'rationale': why}
    json.dump(out, open(os.path.join(HERE, 'p1_results.json'), 'w',
                        encoding='utf-8'), indent=2, sort_keys=True)
    print('\nwrote p1_results.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())

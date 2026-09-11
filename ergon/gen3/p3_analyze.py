"""ERGON PROJECT 3 -- the frozen inference path and decision rule.

Implements PREREG_P3_MRU_VS_RANDOM.txt. Written, exercised by the gate-fire
worlds (gatefire_p3.py) and the cheat control (cheat_control.py), and
committed BEFORE the preregistration and BEFORE any experimental lineage is
evaluated. The same function `decide` is the ONLY path from per-lineage CFRs
to a verdict: the controls and the experiment go through it unchanged.

    endpoint      per-lineage CFR over the frozen 42-task D-5 battery
    unit          LINEAGE
    contrast      I3 RANDOM - I0 MRU  (positive = MRU is worse than churn)
    test          two-sided paired sign-flip permutation, 50,000 draws,
                  seed 909093
    multiplicity  NONE (one preregistered contrast)
    CI            95% percentile bootstrap over LINEAGES, 20,000 draws
    threshold     T = 2.00 pp, strategic (one task in forty-two), inherited
                  from PREREG_P1_2026-09-01.txt section 2

DECISION RULE, complete and exhaustive (the INDETERMINATE branch is checked
FIRST, before any statistic is read; base s2):

    INDETERMINATE ......................... eligible pairs < n_required, or an
                                            interpretability assertion fails
                                            (library size != cap, task count
                                            != 42), or every pair is tied
                                            (nothing could have fired), or
                                            SE > T/2 (the gate is closer to
                                            zero than two SE)
    p < 0.05 and d >= T ................... MRU_HARMFUL
    p < 0.05 and 0 < d < T ................ MRU_HARMFUL_BELOW_USEFUL_SCALE
    p < 0.05 and d < 0 .................... MRU_BETTER_THAN_RANDOM
    p >= 0.05 and CI inside (-T, T) ....... RETENTION_POLICY_DOES_NOT_MEASURABLY_MATTER
                                            (a bounded null on BOTH sides)
    p >= 0.05 otherwise ................... UNDERPOWERED

The permutation and bootstrap are the same constructions as Project 1
(ergon/gen2/p1_analyze.py); only the seed, the arm labels and the two-sided
bound on the null differ, and each difference is stated in the prereg.

Run:  python -m ergon.gen3.p3_analyze            (reads p3_results/)
"""
import json
import math
import os
import random
import statistics
import sys

HERE = os.path.dirname(__file__)
RES = os.path.join(HERE, 'p3_results')
ARM_A = 'I0'          # comparator: MRU, the inherited D-5 rule
ARM_B = 'I3'          # treatment: RANDOM, the arbitrary comparator
NAMES = {'I0': 'D5_BASELINE_MRU', 'I3': 'RANDOM'}
N_PERM = 50000
PERM_SEED = 909093
N_BOOT = 20000
T = 0.020
ALPHA = 0.05
CAP = 64
N_TASKS = 42
N_REQUIRED = 100


def perm_p(d, rng, n_perm=N_PERM):
    obs = sum(d) / len(d)
    ge = 0
    for _ in range(n_perm):
        m = sum(x if rng.random() < 0.5 else -x for x in d) / len(d)
        if abs(m) >= abs(obs):
            ge += 1
    return obs, (ge + 1) / (n_perm + 1)


def boot_ci(d, rng, n_boot=N_BOOT, lo=2.5, hi=97.5):
    n = len(d)
    ms = sorted(sum(d[rng.randrange(n)] for _ in range(n)) / n
                for _ in range(n_boot))
    return ms[int(lo / 100 * n_boot)], ms[int(hi / 100 * n_boot)]


def decide(cfr_a, cfr_b, n_required=N_REQUIRED, validity_failures=(),
           n_perm=N_PERM, n_boot=N_BOOT, perm_seed=PERM_SEED, t=T):
    """The frozen inference path. cfr_a and cfr_b are per-lineage CFRs in
    the same lineage order; the contrast is B - A. Returns a dict whose
    'verdict' is one of the six labels above and whose rows (the deltas)
    are always present, so no verdict can ship without them."""
    n = min(len(cfr_a), len(cfr_b))
    d = [cfr_b[i] - cfr_a[i] for i in range(n)]
    out = {'n_pairs': n, 'n_required': n_required,
           'validity_failures': list(validity_failures),
           'deltas': [round(v, 6) for v in d], 'threshold_pp': 100 * t}
    if n < 2:
        out.update({'verdict': 'INDETERMINATE',
                    'rationale': 'fewer than two pairs; no statistic exists'})
        return out
    rng = random.Random(perm_seed)
    obs, p = perm_p(d, rng, n_perm)
    lo, hi = boot_ci(d, rng, n_boot)
    se = statistics.stdev(d) / math.sqrt(n)
    pos = sum(1 for x in d if x > 0)
    neg = sum(1 for x in d if x < 0)
    out.update({'mean': obs, 'mean_pp': 100 * obs, 'se': se, 'se_pp': 100 * se,
                'ci95': [lo, hi], 'ci95_pp': [100 * lo, 100 * hi], 'p': p,
                'signs': {'pos': pos, 'neg': neg, 'tied': n - pos - neg},
                'n_perm': n_perm, 'n_boot': n_boot, 'perm_seed': perm_seed,
                'gate_in_se': (t / se) if se > 0 else None})

    # INDETERMINATE first: the statistic is reported but may not decide.
    reasons = []
    if n < n_required:
        reasons.append('eligible pairs %d < required %d' % (n, n_required))
    if validity_failures:
        reasons.append('interpretability assertion failed: %s'
                       % '; '.join(validity_failures))
    if pos + neg == 0:
        reasons.append('all %d pairs tied: no lineage moved in either '
                       'direction, so nothing could have fired' % n)
    elif se > t / 2:
        reasons.append('SE %.2f pp exceeds T/2 = %.2f pp: the gate is '
                       'closer to zero than two SE' % (100 * se, 50 * t))
    if reasons:
        out.update({'verdict': 'INDETERMINATE', 'rationale': '; '.join(reasons)})
        return out

    if p < ALPHA and obs < 0:
        v, why = 'MRU_BETTER_THAN_RANDOM', (
            'RANDOM is significantly WORSE than MRU by %.2f pp; the inherited '
            'rule is not harmful in this consumer' % (100 * -obs))
    elif p < ALPHA and obs >= t:
        v, why = 'MRU_HARMFUL', (
            'RANDOM beats MRU by %.2f pp, significant and at or above the '
            'strategic threshold %.2f pp' % (100 * obs, 100 * t))
    elif p < ALPHA:
        v, why = 'MRU_HARMFUL_BELOW_USEFUL_SCALE', (
            'a real deficit of %.2f pp, smaller than %.2f pp: it cannot '
            'reliably move one task in forty-two' % (100 * obs, 100 * t))
    elif -t < lo and hi < t:
        v, why = 'RETENTION_POLICY_DOES_NOT_MEASURABLY_MATTER', (
            'a BOUNDED null on both sides: the 95%% CI [%+.2f, %+.2f] pp '
            'lies inside (-%.2f, +%.2f) pp' % (100 * lo, 100 * hi,
                                              100 * t, 100 * t))
    else:
        v, why = 'UNDERPOWERED', (
            'the 95%% CI [%+.2f, %+.2f] pp does not exclude a meaningful '
            'effect in at least one direction' % (100 * lo, 100 * hi))
    out.update({'verdict': v, 'rationale': why})
    return out


def load(res=RES, arms=(ARM_A, ARM_B)):
    S = {a: {} for a in arms}
    for f in os.listdir(res):
        if f.startswith('summary_'):
            _, arm, L = f[:-5].split('_')
            if arm in S:
                S[arm][int(L)] = json.load(open(os.path.join(res, f),
                                                encoding='utf-8'))
    return S


def validity(S, lins, arms=(ARM_A, ARM_B)):
    fails = []
    caps = {len(S[a][L]['final_library']) for a in arms for L in lins}
    tasks = {S[a][L]['n_tasks'] for a in arms for L in lins}
    if caps != {CAP}:
        fails.append('final library sizes %s != {%d}' % (sorted(caps), CAP))
    if tasks != {N_TASKS}:
        fails.append('task counts %s != {%d}' % (sorted(tasks), N_TASKS))
    for L in lins:
        nb = {S[a][L].get('nav_base') for a in arms}
        if len(nb) != 1:
            fails.append('lineage %d nav_base differs across arms %s' % (L, nb))
            break
    return fails


def main():
    S = load()
    lins = sorted(set(S[ARM_A]) & set(S[ARM_B]))
    n = len(lins)
    print('ERGON PROJECT 3 -- IS MRU HARMFUL?  (%s - %s)' % (ARM_B, ARM_A))
    print('=' * 70)
    print('paired lineages: %d (preregistered %d)' % (n, N_REQUIRED))
    fails = validity(S, lins) if n else ['no lineages']
    cfr = {a: [S[a][L]['cfr'] for L in lins] for a in (ARM_A, ARM_B)}
    for a in (ARM_A, ARM_B):
        v = cfr[a]
        if len(v) > 1:
            print('  %-3s %-16s mean %.4f  sd %.4f  min %.3f  max %.3f'
                  % (a, NAMES[a], statistics.mean(v), statistics.stdev(v),
                     min(v), max(v)))
    r = decide(cfr[ARM_A], cfr[ARM_B], validity_failures=fails)
    if 'mean' in r:
        print('\nPRIMARY CONTRAST  %s - %s  (the only contrast; no correction)'
              % (ARM_B, ARM_A))
        print('  mean   %+.4f  (%+.2f pp)' % (r['mean'], r['mean_pp']))
        print('  SE     %.4f  (gate T is %.1f SE from zero)'
              % (r['se'], r['gate_in_se']))
        print('  95%% CI [%+.2f, %+.2f] pp' % tuple(r['ci95_pp']))
        print('  p      %.5f  (two-sided paired sign-flip, %d draws)'
              % (r['p'], r['n_perm']))
        print('  signs  %d positive, %d negative, %d tied of %d'
              % (r['signs']['pos'], r['signs']['neg'], r['signs']['tied'], n))
    print('\nVERDICT: %s' % r['verdict'])
    print('  %s' % r['rationale'])
    r.update({'arm_a': ARM_A, 'arm_b': ARM_B, 'lineage_ids': lins,
              'arm_mean_cfr': {a: round(statistics.mean(cfr[a]), 5)
                               for a in (ARM_A, ARM_B) if cfr[a]},
              'arm_sd_cfr': {a: round(statistics.stdev(cfr[a]), 5)
                             for a in (ARM_A, ARM_B) if len(cfr[a]) > 1},
              'arm_cfr_by_lineage': {a: [round(v, 5) for v in cfr[a]]
                                     for a in (ARM_A, ARM_B)}})
    json.dump(r, open(os.path.join(HERE, 'p3_results.json'), 'w',
                      encoding='utf-8'), indent=1, sort_keys=True)
    print('\nwrote p3_results.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())

"""ERGON PROJECT 3 -- MDE, attainable range and eligible count under the
frozen decision rule, BEFORE the experiment runs (ERGON-03).

The rule (p3_analyze.decide): one contrast I3 - I0, two-sided paired
sign-flip permutation at alpha 0.05, no multiplicity correction, strategic
threshold T = 2.00 pp, n = 100 paired lineages.

Two questions the base role requires answered before any null is read:

  1. What is the smallest true effect the rule can call (MDE at 80% and 90%
     power), using the frozen test itself (sign-flip null constructed
     directly, as ergon/gen1/mde_under_multiplicity.py did for Gen-1)?
     sigma is taken from BOTH measured sources for this consumer and the
     larger is frozen as the planning value:
         Gen-1B  I3 - I0 per-lineage SD at n 30    0.0363
         P1      I1 - I3 per-lineage SD at n 100   0.0429   <- frozen
  2. What range of the statistic is attainable, how many pairs are
     eligible, and does the gate T sit outside the measurement error?
     CFR is k/42, so a per-lineage delta is a multiple of 2.38 pp and the
     mean over 100 lineages a multiple of 0.0238 pp. The expected SE at
     the frozen sigma is 0.43 pp; T = 2.00 pp is 4.7 SE from zero, so the
     gate is not inside its own error (base s2). The INDETERMINATE branch
     fires if the observed SE exceeds T/2 = 1.00 pp, i.e. if the observed
     per-lineage SD exceeds 10 pp, more than twice anything measured.

Nothing here changes a frozen quantity; it measures the relationship
between them before data exist.

Run:  python -m ergon.gen3.mde_p3     writes mde_p3.json
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(__file__)
N = 100
SIGMAS = {'gen1b_I3_minus_I0_n30': 0.0363, 'p1_I1_minus_I3_n100': 0.0429}
SIGMA = max(SIGMAS.values())
T = 0.020
ALPHA = 0.05
N_PERM = 2000
N_TRIALS = 3000
SEED = 20260911
N_TASKS = 42


def power_at(delta, alpha, rng, sigma, n):
    d = rng.normal(delta, sigma, size=(N_TRIALS, n))
    obs = np.abs(d.mean(axis=1))
    signs = rng.choice(np.array([-1.0, 1.0]), size=(N_PERM, n))
    null = np.abs(d @ signs.T) / n
    p = (null >= obs[:, None]).mean(axis=1)
    return float((p <= alpha).mean())


def mde(alpha, rng, sigma, n, target, lo=0.0, hi=0.08, tol=5e-5):
    for _ in range(24):
        mid = 0.5 * (lo + hi)
        if power_at(mid, alpha, rng, sigma, n) < target:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


def main():
    rng = np.random.default_rng(SEED)
    print('ERGON PROJECT 3 -- MDE UNDER THE FROZEN RULE, BEFORE THE RUN')
    print('=' * 70)
    print('n = %d pairs, sigma frozen %.4f (the larger of %s), two-sided '
          'sign-flip, alpha %.2f, one contrast\n' % (N, SIGMA, SIGMAS, ALPHA))
    rows = {}
    for label, sig in list(SIGMAS.items()) + [('frozen', SIGMA)]:
        m80 = mde(ALPHA, rng, sig, N, 0.80)
        m90 = mde(ALPHA, rng, sig, N, 0.90)
        rows[label] = {'sigma': sig, 'mde80_pp': round(100 * m80, 2),
                       'mde90_pp': round(100 * m90, 2)}
        print('  sigma %.4f (%-24s)  MDE80 %.2f pp   MDE90 %.2f pp'
              % (sig, label, 100 * m80, 100 * m90))
    se = SIGMA / math.sqrt(N)
    power_at_T = power_at(T, ALPHA, rng, SIGMA, N)
    print('\nexpected SE at frozen sigma      %.2f pp' % (100 * se))
    print('gate T = %.2f pp is              %.1f SE from zero' % (100 * T, T / se))
    print('power to call a true effect of T %.3f' % power_at_T)
    print('CI half-width expected           %.2f pp (bounded null needs < T)'
          % (100 * 1.96 * se))
    print('per-lineage delta granularity    %.2f pp (1/42)' % (100 / N_TASKS))
    print('mean-delta granularity           %.4f pp (1/4200)'
          % (100 / (N_TASKS * N)))
    print('INDETERMINATE SE branch fires if observed per-lineage SD > %.1f pp'
          % (100 * (T / 2) * math.sqrt(N)))
    out = {
        'n_pairs': N, 'alpha': ALPHA, 'threshold_pp': 100 * T,
        'sigma_sources': SIGMAS, 'sigma_frozen': SIGMA,
        'mde': rows, 'n_perm': N_PERM, 'n_trials': N_TRIALS, 'seed': SEED,
        'expected_se_pp': round(100 * se, 3),
        'gate_in_se': round(T / se, 2),
        'power_at_T': round(power_at_T, 3),
        'expected_ci_halfwidth_pp': round(100 * 1.96 * se, 2),
        'attainable': {
            'per_lineage_delta_granularity_pp': round(100 / N_TASKS, 4),
            'mean_delta_granularity_pp': round(100 / (N_TASKS * N), 4),
            'per_lineage_delta_bounds_pp': [-100.0, 100.0],
            'practical_bound_note': (
                'arm CFRs in P1 ranged 0.19..0.40 per lineage; a mean delta '
                'beyond about 20 pp would exceed every measured lineage'),
        },
        'eligible': {
            'pairs_by_construction': N,
            'pairing': 'nav_base = 200000 + 1000 L, identical across arms',
            'expected_tied_fraction_from_p1': 0.20,
            'note': ('a tied pair contributes zero to the sign-flip null and '
                     'is still eligible; only all-tied is INDETERMINATE'),
        },
        'indeterminate_se_branch': {
            'fires_if_observed_se_pp_exceeds': 100 * T / 2,
            'equivalent_per_lineage_sd_pp': round(100 * (T / 2) * math.sqrt(N), 1),
        },
        'chosen_rule': {
            'contrast': 'I3 RANDOM - I0 MRU, the only contrast',
            'test': 'two-sided paired sign-flip permutation, 50000 draws, seed 909093',
            'ci': '95% percentile bootstrap over lineages, 20000 draws',
            'threshold_pp': 100 * T,
            'reason': ('one contrast so no multiplicity correction is owed '
                       '(the Gen-1 lesson); T inherited from P1 section 2 '
                       '(one task in forty-two) so the two bounded nulls are '
                       'comparable; T is %.1f SE from zero, so the gate is '
                       'outside its own measurement error' % (T / se)),
        },
    }
    json.dump(out, open(os.path.join(HERE, 'mde_p3.json'), 'w',
                        encoding='utf-8'), indent=1, sort_keys=True)
    print('\nwrote mde_p3.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())

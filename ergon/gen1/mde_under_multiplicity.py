"""Ergon Gen-1 (second instance): is the preregistered MDE consistent with the
preregistered multiplicity correction?

PREREG_GEN1_2026-09-01.txt section 5 freezes both of these:

    Preregistered MDE    1.9 pp at n=30 (Gen-1A power analysis, sigma 0.0412)
    Multiplicity         5 contrasts; Holm-Bonferroni across the five.
                         A contrast is called ONLY if it survives Holm.

A power analysis states the effect detectable at some alpha. Holm changes the
alpha a contrast must clear: the smallest of five p-values is compared against
alpha/5. If the 1.9pp figure was computed at an uncorrected alpha, then the
effect actually callable under the frozen decision rule is LARGER than the
number the preregistration commits to -- and the gate would sit below the
measurement error it has to clear (feedback_gate_must_exceed_measurement_error;
X-2 burned two passes on exactly this).

This does not change any frozen quantity. It measures the relationship between
two of them, before results exist, which is when it is free to know.

Method: the frozen test itself -- two-sided paired sign-flip permutation on n
lineage-level deltas. No normal approximation is assumed for the null; the
sign-flip null is constructed directly.
"""
import json
import os

import numpy as np

N_LINEAGES = 30
SIGMA = 0.0412          # Gen-1A: M1 vs shuffled-history, true effect zero
N_PERM = 2000           # sign-flip draws per simulated experiment
N_TRIALS = 3000         # simulated experiments per effect size
POWER_TARGET = 0.80
SEED = 20260902


def power_at(delta, alpha, rng, n=N_LINEAGES):
    """Fraction of simulated experiments whose two-sided sign-flip p <= alpha."""
    d = rng.normal(delta, SIGMA, size=(N_TRIALS, n))
    obs = np.abs(d.mean(axis=1))
    signs = rng.choice(np.array([-1.0, 1.0]), size=(N_PERM, n))
    # null means: (N_TRIALS, N_PERM)
    null = np.abs(d @ signs.T) / n
    p = (null >= obs[:, None]).mean(axis=1)
    return float((p <= alpha).mean())


def mde(alpha, rng, lo=0.0, hi=0.12, tol=5e-5):
    """Smallest true effect reaching POWER_TARGET at this alpha."""
    for _ in range(24):
        mid = 0.5 * (lo + hi)
        if power_at(mid, alpha, rng) < POWER_TARGET:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


def main():
    rng = np.random.default_rng(SEED)
    print('=== MDE UNDER THE FROZEN TEST ===')
    print('n = %d lineages, sigma = %.4f, two-sided sign-flip, power %.0f%%\n'
          % (N_LINEAGES, SIGMA, 100 * POWER_TARGET))

    rows = []
    for label, alpha in (('uncorrected            alpha=0.05', 0.05),
                         ('Holm, best of 5     alpha=0.05/5', 0.01),
                         ('Holm, 2nd of 5      alpha=0.05/4', 0.0125),
                         ('Bonferroni-like     alpha=0.05/3', 0.05 / 3)):
        m = mde(alpha, rng)
        rows.append({'label': label.strip(), 'alpha': alpha,
                     'mde_pp': round(100 * m, 2)})
        print('%-36s MDE = %5.2f pp' % (label, 100 * m))

    unc = rows[0]['mde_pp']
    holm = rows[1]['mde_pp']
    print('\nprereg states .................. 1.90 pp')
    print('reproduced at alpha=0.05 ....... %.2f pp' % unc)
    print('required to CALL under Holm .... %.2f pp' % holm)
    print('inflation factor ............... %.2fx' % (holm / unc))

    print('\n=== WHAT THIS MEANS ===')
    print('The frozen MDE and the frozen decision rule refer to different')
    print('alphas. An effect of 1.9 pp is DETECTABLE in the uncorrected sense')
    print('and is NOT CALLABLE under the frozen Holm rule.')
    print('At n=30 the smallest callable effect is about %.1f pp.' % holm)

    # What n would restore a 1.9pp callable effect under Holm?
    print('\n=== n REQUIRED TO MAKE 1.9 pp CALLABLE UNDER HOLM ===')
    need = None
    for n in (30, 40, 50, 60, 80, 100, 120):
        pw = power_at(0.019, 0.01, rng, n=n)
        flag = ''
        if pw >= POWER_TARGET and need is None:
            need = n
            flag = '  <-- first n reaching 80%'
        print('  n=%3d   power at 1.9pp, alpha=0.01 = %.2f%s' % (n, pw, flag))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       'mde_under_multiplicity.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump({'n_lineages': N_LINEAGES, 'sigma': SIGMA,
                   'power_target': POWER_TARGET, 'n_perm': N_PERM,
                   'n_trials': N_TRIALS, 'seed': SEED,
                   'prereg_stated_mde_pp': 1.90, 'rows': rows,
                   'n_for_1p9pp_under_holm': need}, f, indent=1)
        f.flush()
    print('\nwrote', out)


if __name__ == '__main__':
    main()

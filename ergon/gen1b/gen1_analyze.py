"""ERGON GEN-1 / PHASES 4-7 -- primary analysis, mechanism autopsy, half-life.

The primary analysis is exactly what PREREG_GEN1_2026-09-01.txt froze and is
printed FIRST, before any mechanism measure is computed, so the reported order
matches the committed order.

Run:  python -m ergon.gen1b.gen1_analyze
"""
import collections
import json
import math
import os
import random
import statistics
import sys

HERE = os.path.dirname(__file__)
RES = os.path.join(HERE, 'gen1_results')
ARMS = ('I0', 'I1', 'I2', 'I3')
NAMES = {'I0': 'D5_BASELINE_MRU', 'I1': 'MUT_REDUNDANT',
         'I2': 'EFFECTIVE_USAGE', 'I3': 'RANDOM'}
N_PERM = 20000
PERM_SEED = 424242
MDE = 0.019


def load():
    S = collections.defaultdict(dict)
    for f in os.listdir(RES):
        if f.startswith('summary_'):
            _, arm, L = f[:-5].split('_')
            S[arm][int(L)] = json.load(open(os.path.join(RES, f),
                                            encoding='utf-8'))
    return S


def perm_p_two_sided(d, rng):
    obs = sum(d) / len(d)
    ge = 0
    for _ in range(N_PERM):
        m = sum(x if rng.random() < 0.5 else -x for x in d) / len(d)
        if abs(m) >= abs(obs):
            ge += 1
    return obs, (ge + 1) / (N_PERM + 1)


def boot_ci(d, rng, lo=5, hi=95, B=10000):
    ms = []
    n = len(d)
    for _ in range(B):
        ms.append(sum(d[rng.randrange(n)] for _ in range(n)) / n)
    ms.sort()
    return ms[int(lo / 100 * B)], ms[int(hi / 100 * B)]


def holm(pairs):
    """pairs: list of (label, p). Returns dict label -> (p, adj, reject)."""
    m = len(pairs)
    order = sorted(pairs, key=lambda kv: kv[1])
    out = {}
    prev = 0.0
    for i, (k, p) in enumerate(order):
        adj = min(1.0, max(prev, (m - i) * p))
        prev = adj
        out[k] = (p, adj, adj < 0.05)
    return out


def main():
    S = load()
    lins = sorted(set.intersection(*[set(S[a]) for a in ARMS]))
    rng = random.Random(PERM_SEED)
    print('ERGON GEN-1 -- PRIMARY RESULTS (frozen analysis, reported first)')
    print('=' * 72)
    print('paired lineages: %d   arms: %s' % (len(lins), ', '.join(ARMS)))
    if len(lins) < 30:
        print('*** WARNING: fewer than the preregistered 30 lineages; the '
              'primary analysis is UNDERPOWERED and is reported as such ***')

    cfr = {a: [S[a][L]['cfr'] for L in lins] for a in ARMS}
    print('\nARM MEANS (CFR = fraction of 42 tasks solved within 30k evals)')
    for a in ARMS:
        v = cfr[a]
        print('  %-3s %-18s mean %.4f   sd %.4f   min %.3f   max %.3f'
              % (a, NAMES[a], statistics.mean(v), statistics.stdev(v),
                 min(v), max(v)))

    contrasts = [('I1-I0', 'I1', 'I0'), ('I2-I0', 'I2', 'I0'),
                 ('I3-I0', 'I3', 'I0'), ('I1-I3', 'I1', 'I3'),
                 ('I2-I3', 'I2', 'I3')]
    results = {}
    ps = []
    print('\nPRIMARY CONTRASTS (two-sided paired sign-flip permutation, '
          '%d perms)' % N_PERM)
    for label, x, y in contrasts:
        d = [cfr[x][i] - cfr[y][i] for i in range(len(lins))]
        obs, p = perm_p_two_sided(d, rng)
        lo, hi = boot_ci(d, rng)
        se = statistics.stdev(d) / math.sqrt(len(d))
        results[label] = {'deltas': [round(v, 6) for v in d],
                          'mean': obs, 'se': se, 'p': p,
                          'ci90': [lo, hi],
                          'exceeds_mde': abs(obs) >= MDE}
        ps.append((label, p))
        print('  %-7s mean %+.4f (%+.2f pp)  SE %.4f  90%% CI [%+.4f, %+.4f]'
              '  p %.4f  %s MDE'
              % (label, obs, 100 * obs, se, lo, hi, p,
                 '>=' if abs(obs) >= MDE else '<'))

    h = holm(ps)
    print('\n  Holm-Bonferroni across the 5 preregistered contrasts:')
    for label, _x, _y in contrasts:
        p, adj, rej = h[label]
        results[label]['p_holm'] = adj
        results[label]['reject_holm'] = rej
        print('    %-7s p %.4f -> adj %.4f   %s'
              % (label, p, adj, 'SIGNIFICANT' if rej else 'not significant'))

    any_sig = any(results[c[0]]['reject_holm'] for c in contrasts)
    print('\n  ANY CONTRAST SURVIVING HOLM: %s' % ('YES' if any_sig else 'NO'))

    # ---------------- Phase 5: mechanism autopsy -------------------------
    print('\n' + '=' * 72)
    print('MECHANISM AUTOPSY (exploratory; does not modify the result above)')
    print('=' * 72)
    keys = [('final_behaviours', 'terminal distinct behaviours'),
            ('final_offspring_behaviours', 'terminal reachable offspring beh.'),
            ('evictions', 'evictions'),
            ('fallbacks', 'MRU fallbacks'),
            ('total_draws', 'library draws'),
            ('eff_total', 'total effective uses'),
            ('artifacts_with_eff', 'artifacts with >=1 effective use'),
            ('n_artifacts_seen', 'distinct artifacts admitted'),
            ('final_median_age', 'terminal median artifact age (tasks)'),
            ('final_eff_concentration', 'top-artifact share of terminal credit')]
    mech = {}
    print('\n  measure                                 ' +
          '  '.join('%-9s' % a for a in ARMS))
    for k, label in keys:
        row = []
        for a in ARMS:
            vals = [S[a][L].get(k) for L in lins]
            vals = [v for v in vals if v is not None]
            row.append(statistics.mean(vals) if vals else float('nan'))
            mech.setdefault(k, {})[a] = round(row[-1], 4) if vals else None
        print('  %-38s' % label + '  '.join('%-9.3f' % v for v in row))

    # association between mechanism deltas and CFR deltas, across lineages
    print('\n  ACROSS-LINEAGE ASSOCIATION of mechanism delta with CFR delta')
    print('  (Pearson r; association is NOT mediation)')
    assoc = {}
    for label, x, y in contrasts[:2]:
        dc = [cfr[x][i] - cfr[y][i] for i in range(len(lins))]
        print('   %s:' % label)
        for k, lab in keys:
            dm = []
            ok = True
            for i, L in enumerate(lins):
                a_, b_ = S[x][L].get(k), S[y][L].get(k)
                if a_ is None or b_ is None:
                    ok = False
                    break
                dm.append(a_ - b_)
            if not ok or statistics.pstdev(dm) == 0:
                continue
            mx, my = statistics.mean(dm), statistics.mean(dc)
            num = sum((dm[i] - mx) * (dc[i] - my) for i in range(len(dc)))
            den = math.sqrt(sum((v - mx) ** 2 for v in dm) *
                            sum((v - my) ** 2 for v in dc))
            r = num / den if den else 0.0
            assoc.setdefault(label, {})[k] = round(r, 4)
            print('     %-38s r %+.3f' % (lab, r))

    out = {'n_lineages': len(lins), 'arms': list(ARMS),
           'arm_mean_cfr': {a: round(statistics.mean(cfr[a]), 5) for a in ARMS},
           'arm_sd_cfr': {a: round(statistics.stdev(cfr[a]), 5) for a in ARMS},
           'arm_cfr_by_lineage': {a: [round(v, 5) for v in cfr[a]] for a in ARMS},
           'contrasts': results, 'mechanism_means': mech,
           'mechanism_cfr_association': assoc,
           'mde': MDE, 'n_perm': N_PERM, 'perm_seed': PERM_SEED,
           'any_significant_after_holm': any_sig}
    json.dump(out, open(os.path.join(HERE, 'gen1_primary_results.json'), 'w',
                        encoding='utf-8'), indent=2, sort_keys=True)
    print('\nwrote gen1_primary_results.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())

"""ERGON GEN-1A / section 2 -- lineage-level dependence and power.

James's ruling: LINEAGE is the independent experimental unit, because the
retention policy operates on a lineage-scoped persistent library. Tasks within
a lineage are repeated measurements.

This script does four things, all from COMMITTED D-5 data:
  1. reproduces the frozen G4 task-level statistic, as a correctness check on
     the re-derivation;
  2. re-expresses the same evidence at the lineage unit;
  3. decomposes variance into between-lineage and between-task components;
  4. estimates power by SIMULATING the exact test D-5 froze -- a one-sided
     sign-flip permutation test -- rather than a normal approximation.

The sigma that matters for Gen-1 is NOT the library-vs-no-library sigma. Gen-1
contrasts two libraries against each other. D-5's ablation arms are exactly
that kind of contrast, and M1 vs M1-shuffled-history is the purest available:
identical content, different accumulation order, TRUE EFFECT ZERO. Its
per-lineage spread is the noise floor a retention experiment must beat.

Run:  python -m ergon.gen1a.power_analysis
"""
import json
import math
import os
import random
import statistics
import sys

HERE = os.path.dirname(__file__)
L = os.path.abspath(os.path.join(HERE, '..', '..', 'agent_d5_blind', 'ledgers'))
NC = ('F1', 'F2', 'F3', 'F4')
TOP = '30000'
N_PERM = 2000
N_SIM = 400
ALPHA = 0.05
TARGET_POWER = 0.80


def load(f):
    p = os.path.join(L, f)
    return [json.loads(x) for x in open(p, encoding='utf-8', errors='replace')
            if x.strip()]


def cells(rows, arm):
    d = {}
    for r in rows:
        if r['arm'] == arm and r['family'] in NC:
            d[(r['family'], r['seed'], r['lineage'])] = bool(r['ladder'][TOP])
    return d


def perm_p(deltas, rng):
    obs = sum(deltas) / len(deltas)
    ge = 0
    for _ in range(N_PERM):
        m = sum(d if rng.random() < 0.5 else -d for d in deltas) / len(deltas)
        if m >= obs:
            ge += 1
    return obs, (ge + 1) / (N_PERM + 1)


def simulate_power(effect, sigma, n, rng):
    """Power of the frozen one-sided sign-flip permutation test at n paired
    lineages, effect size `effect`, per-lineage SD `sigma`."""
    hits = 0
    for _ in range(N_SIM):
        d = [rng.gauss(effect, sigma) for _ in range(n)]
        obs = sum(d) / n
        ge = 0
        for _ in range(120):          # inner perm; 120 suffices at alpha .05
            m = sum(x if rng.random() < 0.5 else -x for x in d) / n
            if m >= obs:
                ge += 1
        if (ge + 1) / 121 < ALPHA:
            hits += 1
    return hits / N_SIM


def mde(sigma, n, rng, lo=0.0, hi=0.30):
    """Smallest effect reaching TARGET_POWER, by bisection on simulated power."""
    for _ in range(9):
        mid = (lo + hi) / 2
        if simulate_power(mid, sigma, n, rng) >= TARGET_POWER:
            hi = mid
        else:
            lo = mid
    return hi


def main():
    rng = random.Random(20260901)
    rows = (load('m1_rows.jsonl') + load('ablation_rows.jsonl') +
            [r for r in load('m0_rows.jsonl') if r['arm'] == 'M0c-RX'])
    I = {a: cells(rows, a) for a in
         ('M1', 'M0c-RX', 'M1-shuffled-history', 'M1-random-library',
          'M1-frozen-half')}
    lins = sorted({k[2] for k in I['M1']})
    tasks = sorted({(k[0], k[1]) for k in I['M1']})

    out = {'n_lineages_available': len(lins), 'n_tasks': len(tasks)}
    print('ERGON GEN-1A -- LINEAGE DEPENDENCE AND POWER')
    print('=' * 70)
    print('committed D-5 evidence: %d tasks x %d lineages, rung %s\n'
          % (len(tasks), len(lins), TOP))

    # ---- 1. reproduce frozen G4 -----------------------------------------
    A, B = I['M1'], I['M0c-RX']
    tf = {t: statistics.mean([A[(t[0], t[1], l)] for l in lins]) for t in tasks}
    t0 = {t: statistics.mean([B[(t[0], t[1], l)] for l in lins]) for t in tasks}
    td = [tf[t] - t0[t] for t in tasks]
    se_task = statistics.stdev(td) / math.sqrt(len(td))
    print('1. FROZEN G4 REPRODUCTION (task unit, as D-5 computed it)')
    print('   delta %+.4f   n %d   SE %.4f   [D-5 published +0.1095, SE 0.0342]'
          % (statistics.mean(td), len(td), se_task))
    out['task_level'] = {'delta': round(statistics.mean(td), 4),
                         'n': len(td), 'se': round(se_task, 4)}

    # ---- 2/3. lineage unit + variance decomposition ----------------------
    def lin_deltas(x, y):
        P_, Q = I[x], I[y]
        ks = sorted(set(P_) & set(Q))
        ts = sorted({(k[0], k[1]) for k in ks})
        res = []
        for l in lins:
            c = [(t[0], t[1], l) for t in ts
                 if (t[0], t[1], l) in P_ and (t[0], t[1], l) in Q]
            if c:
                res.append(statistics.mean([P_[k] - Q[k] for k in c]))
        return res

    print('\n2. THE SAME EVIDENCE AT THE LINEAGE UNIT')
    contrasts = [('M1', 'M0c-RX', 'library vs none (D-5 headline)'),
                 ('M1', 'M1-shuffled-history', 'library vs library, TRUE NULL'),
                 ('M1', 'M1-random-library', 'adapted vs random content'),
                 ('M1-shuffled-history', 'M1-random-library', 'adapted vs random'),
                 ('M1', 'M1-frozen-half', 'library vs half-frozen')]
    out['contrasts'] = {}
    for x, y, label in contrasts:
        d = lin_deltas(x, y)
        sd = statistics.stdev(d)
        out['contrasts'][x + ' - ' + y] = {
            'label': label, 'per_lineage': [round(v, 4) for v in d],
            'mean': round(statistics.mean(d), 4), 'sd': round(sd, 4),
            'se': round(sd / math.sqrt(len(d)), 4)}
        print('   %-38s mean %+.4f  SD %.4f  SE %.4f'
              % (label, statistics.mean(d), sd, sd / math.sqrt(len(d))))

    # variance decomposition on the headline contrast
    cell = {(t, l): A[(t[0], t[1], l)] - B[(t[0], t[1], l)]
            for t in tasks for l in lins}
    grand = statistics.mean(cell.values())
    lmeans = {l: statistics.mean([cell[(t, l)] for t in tasks]) for l in lins}
    tmeans = {t: statistics.mean([cell[(t, l)] for l in lins]) for t in tasks}
    var_l = statistics.pvariance(list(lmeans.values()))
    var_t = statistics.pvariance(list(tmeans.values()))
    var_c = statistics.pvariance(list(cell.values()))
    icc_l = var_l / var_c if var_c else 0.0
    print('\n3. VARIANCE DECOMPOSITION of the per-cell delta (headline contrast)')
    print('   between-LINEAGE variance %.5f   (share of cell variance %.3f)'
          % (var_l, icc_l))
    print('   between-TASK    variance %.5f   (share of cell variance %.3f)'
          % (var_t, var_t / var_c if var_c else 0))
    print('   per-cell        variance %.5f   grand mean %+.4f' % (var_c, grand))
    print('   -> the lineage component is %s than the task component'
          % ('SMALLER' if var_l < var_t else 'LARGER'))
    out['variance'] = {'between_lineage': round(var_l, 5),
                       'between_task': round(var_t, 5),
                       'per_cell': round(var_c, 5),
                       'lineage_share': round(icc_l, 4),
                       'task_share': round(var_t / var_c, 4) if var_c else None}

    # ---- 4. power ---------------------------------------------------------
    sigma_null = out['contrasts']['M1 - M1-shuffled-history']['sd']
    sigma_head = out['contrasts']['M1 - M0c-RX']['sd']
    print('\n4. POWER, simulating the FROZEN sign-flip permutation test')
    print('   sigma used = %.4f (M1 vs shuffled-history: same content, true'
          ' effect zero)' % sigma_null)
    print('   a conservative alternative is %.4f (headline contrast)\n'
          % sigma_head)
    print('   n_lineages   MDE @80%% power (sigma %.4f)   MDE (sigma %.4f)'
          % (sigma_null, sigma_head))
    grid = [5, 8, 10, 15, 20, 25, 30, 40, 50]
    out['mde'] = {}
    for n in grid:
        m1_ = mde(sigma_null, n, rng)
        m2_ = mde(sigma_head, n, rng)
        out['mde'][n] = {'sigma_null': round(m1_, 4),
                         'sigma_headline': round(m2_, 4)}
        print('   %-12d %-33s %.1f pp' % (n, '%.1f pp' % (100 * m1_),
                                          100 * m2_))

    # reference effects the MDE must be read against
    ref = {
        'full accumulation effect (M1-M0)': out['contrasts']['M1 - M0c-RX']['mean'],
        'content-adaptedness component (M1 - random-library)':
            out['contrasts']['M1 - M1-random-library']['mean'],
        'order component (M1 - shuffled), measured zero':
            out['contrasts']['M1 - M1-shuffled-history']['mean'],
    }
    print('\n   REFERENCE EFFECTS a retention policy would be modulating:')
    for k, v in ref.items():
        print('     %-52s %+.1f pp' % (k, 100 * v))
    out['reference_effects'] = {k: round(v, 4) for k, v in ref.items()}

    json.dump(out, open(os.path.join(HERE, 'power_analysis_2026-09-01.json'),
                        'w', encoding='utf-8'), indent=2, sort_keys=True)
    print('\nwrote power_analysis_2026-09-01.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())

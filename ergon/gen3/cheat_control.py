"""ERGON PROJECT 3 -- cheat control on the REAL execution path (ERGON-04).

The gate-fire worlds show the statistic calls constructed CFR vectors
correctly. This control shows the whole channel -- frozen search, frozen
admission, the I0 library, per-lineage CFR, the paired test, the decision
rule -- can see a retention effect of KNOWN size when one is deliberately
injected. Success is injected by planting the oracle-side witness of a
task into the I0 library immediately before that task (p3_common.
run_lineage_planted). The tasks planted are ones NO lineage-run in Project 1
ever solved (0 of 200: tasks 1 and 2), so each successful plant is worth
exactly one task, 1/42 = 2.38 pp, in that lineage and the comparator cannot
have solved it by chance.

Arms, n = 30 paired lineages, seed space L in 200..229 (disjoint from every
earlier run):

    I0        the comparator, frozen runner verbatim
    I0dup     I0 again, same seeds. Determinism: every delta must be exactly
              0 and the verdict INDETERMINATE (all tied). If any pair
              differs, the channel carries noise that is not the treatment
              and the experiment may not run.
    PLANT1    I0 with the witness of task 1 planted before task 1
    PLANT2    I0 with the witnesses of tasks 1 and 2 planted before each

Pass criteria, fixed before the run:

    I0dup vs I0    verdict INDETERMINATE with signs pos 0 neg 0 tied 30
    PLANT2 vs I0   p < 0.05 and mean >= T (2.00 pp): the label MRU_HARMFUL
                   fires. (The decision rule's n_required is 30 here, the
                   control's own n; the experiment's is 100.)
    PLANT1 vs I0   p < 0.05 (a one-task injection is detected); the label is
                   MRU_HARMFUL if the plant succeeds in at least 84% of
                   lineages, else MRU_HARMFUL_BELOW_USEFUL_SCALE; both are
                   correct calls and the plant success rate is reported.

Anything else is a FAIL and blocks the experiment.

Run:  python -m ergon.gen3.cheat_control [--workers 8]   writes cheat_control.json
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..')))
from ergon.gen3 import p3_common as C                  # noqa: E402
from ergon.gen3.p3_analyze import decide, T           # noqa: E402

N = 30
OUT = os.path.join(HERE, 'cheat_results')
LABELS = {'I0': ('I0', ()), 'I0dup': ('I0', ()),
          'PLANT1': ('I0', (1,)), 'PLANT2': ('I0', (1, 2))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--budget', type=int, default=30000)
    a = ap.parse_args()
    lins = list(range(C.CHEAT_START, C.CHEAT_START + N))
    jobs = [(label, arm, L, a.budget, OUT, plant)
            for L in lins for label, (arm, plant) in LABELS.items()]
    print('ERGON PROJECT 3 -- CHEAT CONTROL (real execution, planted witness)')
    print('=' * 70)
    print('labels %s | lineages %d..%d | %d jobs | %d workers'
          % (list(LABELS), lins[0], lins[-1], len(jobs), a.workers))
    C.run_jobs(jobs, a.workers)

    S = {}
    for label in LABELS:
        S[label] = [json.load(open(os.path.join(OUT, 'summary_%s_%d.json'
                                                % (label, L)),
                                   encoding='utf-8')) for L in lins]
    cfr = {label: [s['cfr'] for s in S[label]] for label in LABELS}
    out = {'n': N, 'lineages': lins, 'threshold_pp': 100 * T,
           'contrasts': {}, 'plant_success': {}}
    ok = True
    for label in ('I0dup', 'PLANT1', 'PLANT2'):
        r = decide(cfr['I0'], cfr[label], n_required=N)
        r['arm_cfr'] = {'I0': cfr['I0'], label: cfr[label]}
        out['contrasts'][label + '-I0'] = r
        print('\n%s - I0: %s' % (label, r['verdict']))
        if 'mean' in r:
            print('  mean %+.2f pp  SE %.2f pp  CI [%+.2f, %+.2f] pp  p %.5f'
                  '  signs %s' % (r['mean_pp'], r['se_pp'], r['ci95_pp'][0],
                                  r['ci95_pp'][1], r['p'], r['signs']))
        print('  %s' % r['rationale'])
    # plant success: was the planted task solved in that lineage?
    for label in ('PLANT1', 'PLANT2'):
        plant = LABELS[label][1]
        succ = {}
        for i in plant:
            n_solved = 0
            for L in lins:
                rows = [json.loads(l) for l in open(
                    os.path.join(OUT, 'rows_%s_%d.jsonl' % (label, L)),
                    encoding='utf-8')]
                n_solved += 1 if rows[i]['solved'] else 0
            succ['task_%d' % i] = {'solved_lineages': n_solved, 'of': N}
        out['plant_success'][label] = succ
        print('  %s plant success %s' % (label, succ))

    dup = out['contrasts']['I0dup-I0']
    c1 = out['contrasts']['PLANT1-I0']
    c2 = out['contrasts']['PLANT2-I0']
    checks = {
        'dup_all_tied_indeterminate': (dup['verdict'] == 'INDETERMINATE'
                                       and dup['signs']['tied'] == N),
        'plant2_fires_MRU_HARMFUL': (c2['verdict'] == 'MRU_HARMFUL'),
        'plant1_detected': ('p' in c1 and c1['p'] < 0.05 and c1['verdict']
                            in ('MRU_HARMFUL',
                                'MRU_HARMFUL_BELOW_USEFUL_SCALE')),
    }
    ok = all(checks.values())
    out['checks'] = checks
    out['all_pass'] = ok
    print('\nCHECKS: %s' % checks)
    print('CHEAT CONTROL %s' % ('PASS' if ok else 'FAIL'))
    json.dump(out, open(os.path.join(HERE, 'cheat_control.json'), 'w',
                        encoding='utf-8'), indent=1, sort_keys=True)
    print('wrote cheat_control.json')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

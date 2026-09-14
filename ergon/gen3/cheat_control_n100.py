"""ERGON PROJECT 3 -- cheat control, second run, at the experiment's n (ERGON-04).

The first cheat control (cheat_control.py, cheat_control.json, n 30) FAILED
its preregistered checks and that file stands as written:

    I0dup - I0    INDETERMINATE, 30/30 tied            (pass: determinism)
    PLANT2 - I0   MRU_HARMFUL  +6.67 pp p 0.00002       (pass)
    PLANT1 - I0   INDETERMINATE: SE 1.04 pp > T/2       (FAIL by the check
                  = 1.00 pp, although mean +3.33 pp,     as written)
                  p 0.00452, plant solved 30/30

What the failure says, read before anything is changed: the frozen rule's
SE branch is a function of n. A one-artifact plant leaves a footprint on
LATER tasks (the library the search draws from differs from the plant
onward), so the per-lineage delta SD of a single-task intervention is
about 5.7 pp -- larger than the 4.3 pp measured between whole arms -- and
at n 30 that puts the gate inside two SE. At the experiment's n 100 the
same SD gives an expected SE of 0.57 pp, below T/2. The n 30 control
exercised the rule at an n it will never be used at. Nothing in the rule
is changed; the control is re-run at n 100.

Criterion, fixed before this run: PLANT1 - I0 at n 100 (L 200..299; the
first 30 lineages are the n 30 rows re-used unchanged, the other 70 are
fresh) must return p < 0.05 with the label MRU_HARMFUL or
MRU_HARMFUL_BELOW_USEFUL_SCALE. Anything else is a FAIL and the experiment
does not run.

Run:  python -m ergon.gen3.cheat_control_n100 [--workers 8]
      writes cheat_control_n100.json; rows in cheat_results/
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..')))
from ergon.gen3 import p3_common as C                  # noqa: E402
from ergon.gen3.p3_analyze import decide, T           # noqa: E402

N = 100
OUT = os.path.join(HERE, 'cheat_results')
LABELS = {'I0': ('I0', ()), 'PLANT1': ('I0', (1,))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--budget', type=int, default=30000)
    a = ap.parse_args()
    lins = list(range(C.CHEAT_START, C.CHEAT_START + N))
    jobs = [(label, arm, L, a.budget, OUT, plant)
            for L in lins for label, (arm, plant) in LABELS.items()]
    print('ERGON PROJECT 3 -- CHEAT CONTROL AT n 100 (one-task plant)')
    print('=' * 70)
    print('labels %s | lineages %d..%d | %d jobs (existing summaries reused) '
          '| %d workers' % (list(LABELS), lins[0], lins[-1], len(jobs),
                            a.workers))
    C.run_jobs(jobs, a.workers)

    cfr = {}
    for label in LABELS:
        cfr[label] = [json.load(open(os.path.join(
            OUT, 'summary_%s_%d.json' % (label, L)),
            encoding='utf-8'))['cfr'] for L in lins]
    r = decide(cfr['I0'], cfr['PLANT1'], n_required=N)
    r['arm_cfr'] = cfr
    n_solved = 0
    for L in lins:
        rows = [json.loads(l) for l in open(
            os.path.join(OUT, 'rows_PLANT1_%d.jsonl' % L), encoding='utf-8')]
        n_solved += 1 if rows[1]['solved'] else 0
    print('\nPLANT1 - I0 at n %d: %s' % (N, r['verdict']))
    if 'mean' in r:
        print('  mean %+.2f pp  SE %.2f pp  CI [%+.2f, %+.2f] pp  p %.5f'
              '  signs %s' % (r['mean_pp'], r['se_pp'], r['ci95_pp'][0],
                              r['ci95_pp'][1], r['p'], r['signs']))
    print('  %s' % r['rationale'])
    print('  plant success task_1: %d of %d' % (n_solved, N))
    ok = ('p' in r and r['p'] < 0.05 and r['verdict'] in
          ('MRU_HARMFUL', 'MRU_HARMFUL_BELOW_USEFUL_SCALE'))
    out = {'n': N, 'lineages': lins, 'threshold_pp': 100 * T,
           'first_run_n30': 'cheat_control.json (FAILED as written; kept)',
           'contrast': r, 'plant_success': {'task_1': {'solved_lineages': n_solved, 'of': N}},
           'check_plant1_detected_at_n100': ok, 'all_pass': ok}
    print('\nCHEAT CONTROL n 100 %s' % ('PASS' if ok else 'FAIL'))
    json.dump(out, open(os.path.join(HERE, 'cheat_control_n100.json'), 'w',
                        encoding='utf-8'), indent=1, sort_keys=True)
    print('wrote cheat_control_n100.json')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

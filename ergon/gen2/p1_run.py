"""ERGON PROJECT 1 -- I1 MUT_REDUNDANT vs I3 RANDOM at n=100 fresh lineages.

The Gen-1B runner is imported UNCHANGED so its hashed blob
(577125847aabf6a3087d06935e39701cffc751be) remains the executing code. Only
the driver differs: gen1_run.main() loops lineage indices from 0, and Project 1
needs indices 100..199 so its seed space is disjoint from Gen-1B's 0..29.
Adding a --start flag to the frozen runner would have changed its blob, so the
loop lives here instead and run_lineage is called verbatim.

nav_base and the policy rng seed are pure functions of the lineage index inside
the frozen runner (200000 + 1000*L and 50000 + L), so passing L in 100..199
yields nav bases 300000..399000 and policy seeds 50100..50199. No Gen-1B
lineage is reused.

Run:  python -m ergon.gen2.p1_run --lineages 100
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..')))
from ergon.gen1b import gen1_run as G          # noqa: E402  frozen runner
import rm_fast                                  # noqa: E402
from families import gen_task                   # noqa: E402

ARMS = ('I1', 'I3')
START = 100


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lineages', type=int, default=100)
    ap.add_argument('--budget', type=int, default=30000)
    ap.add_argument('--out', default=os.path.join(HERE, 'p1_results'))
    a = ap.parse_args()

    tasks = G.battery()
    t0 = tasks[0]
    tt = gen_task(t0['family'], t0['seed'])
    ref = rm_fast.FastTask({'domain': tt['domain'], 'table': tt['table']})
    os.makedirs(a.out, exist_ok=True)

    print('ERGON PROJECT 1 -- ARBITRARY-MEMORY DECISION')
    print('=' * 70)
    print('arms %s | fresh lineages %d..%d | tasks %d | budget %d'
          % (list(ARMS), START, START + a.lineages - 1, len(tasks), a.budget))
    print('frozen runner imported unchanged; seed space disjoint from Gen-1B\n')

    start = time.time()
    for k in range(a.lineages):
        L = START + k
        nav_base = 200000 + 1000 * L
        for arm in ARMS:
            sp = os.path.join(a.out, 'summary_%s_%d.json' % (arm, L))
            if os.path.exists(sp):
                continue
            ts = time.time()
            rows, summary = G.run_lineage(tasks, arm, L, nav_base, a.budget, ref)
            summary['seconds'] = round(time.time() - ts, 1)
            summary['nav_base'] = nav_base
            with open(os.path.join(a.out, 'rows_%s_%d.jsonl' % (arm, L)),
                      'w', encoding='utf-8') as fh:
                for r in rows:
                    fh.write(json.dumps(r, sort_keys=True) + '\n')
            json.dump(summary, open(sp, 'w', encoding='utf-8'), sort_keys=True)
        if k % 5 == 0 or k == a.lineages - 1:
            done = [json.load(open(os.path.join(a.out, 'summary_%s_%d.json'
                                                % (m, L)), encoding='utf-8'))
                    for m in ARMS]
            print('  lineage %3d  ' % L + '  '.join(
                '%s cfr %.3f' % (d['arm'], d['cfr']) for d in done)
                + '   [%.1f min elapsed]' % ((time.time() - start) / 60))
    print('\ntotal %.1f min' % ((time.time() - start) / 60))
    return 0


if __name__ == '__main__':
    sys.exit(main())

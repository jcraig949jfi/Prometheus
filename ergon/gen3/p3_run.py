"""ERGON PROJECT 3 -- I0 MRU vs I3 RANDOM at n = 100 fresh paired lineages.

The one discriminating experiment the Tier A gate packet (c3797f865) asked
for. Runs ONLY after PREREG_P3_MRU_VS_RANDOM.txt is committed; the frozen
runner (ergon/gen1b/gen1_run.py) is called verbatim through p3_common for
both arms. Seed space L in 300..399: disjoint from Gen-1B (0..29), Project 1
(100..199) and the cheat controls (200..299).

Run:  python -m ergon.gen3.p3_run [--workers 8]
Then: python -m ergon.gen3.p3_analyze
"""
import argparse
import os
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..')))
from ergon.gen3 import p3_common as C                  # noqa: E402

ARMS = ('I0', 'I3')
N = 100
OUT = os.path.join(HERE, 'p3_results')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--budget', type=int, default=30000)
    ap.add_argument('--lineages', type=int, default=N)
    a = ap.parse_args()
    lins = list(range(C.EXP_START, C.EXP_START + a.lineages))
    jobs = [(arm, arm, L, a.budget, OUT, ()) for L in lins for arm in ARMS]
    print('ERGON PROJECT 3 -- IS MRU HARMFUL?  I0 MRU vs I3 RANDOM')
    print('=' * 70)
    print('arms %s | fresh lineages %d..%d | %d jobs | %d workers | budget %d'
          % (list(ARMS), lins[0], lins[-1], len(jobs), a.workers, a.budget))
    print('frozen runner imported unchanged (blob %s)\n' % C.FROZEN_RUNNER_BLOB)
    C.run_jobs(jobs, a.workers)
    print('\ndone; now: python -m ergon.gen3.p3_analyze')
    return 0


if __name__ == '__main__':
    sys.exit(main())

"""Step-8 synthetic validation (designer-side, DEV tasks only, no learner evidence).

World W+ : a useful hidden coordinate exists -> z tables seeded with the TRUE module wire
           behaviors (privileged designer info the learner never gets).
World W- : no coordinate exists -> same z genome, tables filled with a matched-size random
           subset of hoard behaviors.
Arm NONE : z=None (H1 physics).

If W+ does not beat NONE substantially at any k, the interface cannot transmit even a
perfect signal and must be strengthened BEFORE Z1/M1 evidence. If W- beats NONE, the
tournament interface itself (not signal content) confers advantage -> defect.
Fixes K_TOURN, then frozen.
"""
import json, random, sys, time
from multiprocessing import Pool
sys.path.insert(0, 'F:/SerendipityA/src')
import substrate as S
import arena as A
import zsig as Z

GENOME = (1, 0, 0, 0, 2, 0, 0)      # sum of positivity indicators over wire behaviors
SEEDS = 4
BUDGET = 200_000

_G = {}


def _init(hoard_blob, table0):
    _G['hoard'] = A.Hoard.load(hoard_blob)
    _G['z'] = Z.make_z(GENOME, (table0, {}, {}, {})) if table0 is not None else None


def _run(job):
    tid, target, n_out, seed, k = job
    r = A.search(tuple(int(x, 16) for x in target), n_out, BUDGET, seed,
                 _G['hoard'], z=_G['z'], k=k)
    return (tid, seed, r['solved'], r['calls'])


def truth_table():
    md = json.load(open('F:/SerendipityA/runs/modules.json'))
    T = {}
    for p, tt, c in md['modules']:
        prog = tuple(tuple(i) for i in p)
        for b in S.evaluate(prog)[S.N_IN:]:
            T[b] = 1.0
    return T


def main():
    st = json.load(open('F:/SerendipityA/runs/dev_state.json'))
    tasks = [t for t in json.load(open('F:/SerendipityA/runs/battery.json'))['tasks']
             if t['family'] == 'DEV' and t['tier'] == 2][:6]
    Tt = truth_table()
    rng = random.Random(4242)
    hoard_behs = [int(b, 16) for b, _ in st['hoard']]
    Tr = {b: 1.0 for b in rng.sample(hoard_behs, min(len(Tt), len(hoard_behs)))}
    print('truth table keys=%d  random table keys=%d' % (len(Tt), len(Tr)))
    out = {}
    for label, tab, ks in (('NONE', None, [1]), ('W+', Tt, [4, 8, 16]), ('W-', Tr, [4, 8, 16])):
        for k in ks:
            jobs = [(t['id'], t['target'], t['n_out'], 9000 + i * 100 + s, k)
                    for i, t in enumerate(tasks) for s in range(SEEDS)]
            t0 = time.time()
            with Pool(10, initializer=_init, initargs=(st['hoard'], tab)) as pool:
                res = pool.map(_run, jobs, chunksize=1)
            ns = sum(r[2] for r in res)
            out['%s_k%d' % (label, k)] = ns
            print('%-4s k=%2d  solved %2d/%d  (%.0fs)' % (label, k, ns, len(res), time.time() - t0))
    json.dump(out, open('F:/SerendipityA/runs/validate_step8.json', 'w'))


if __name__ == '__main__':
    main()

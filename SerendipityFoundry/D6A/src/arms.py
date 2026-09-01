"""Frozen-state evaluation arms. Usage: python arms.py <FAMILY> [<FAMILY> ...]

Runs, per task and seed, the preregistered arms on the FROZEN dev state:
  H1    : hoard, z=None                                (M1-HOARD; also gate-F ablation)
  H2    : hoard, z* genome, tables from SHUFFLED history
  H3    : hoard, z* genome, tables from INTACT history (M1-REL)
  RANDZ : hoard, per-seed random genome, intact tables (gate G)
  Z0ARM : hoard, best Z0 genome, hoard-intrinsic tables (section 13 baseline)

No history recording, no hoard growth, no z reselection: everything is frozen.
"""
import json, random, sys, time
from multiprocessing import Pool
sys.path.insert(0, 'F:/SerendipityA/src')
import substrate as S
import arena as A
import zsig as Z

BUDGET = 200_000
SEEDS = 12
SHUFFLE_SEED = 777
_G = {}


def _init(state):
    _G['hoard'] = A.Hoard.load(state['hoard'])
    hist = A.History.load(state['history'])
    _G['T_int'] = Z.tables_from_history(hist)
    _G['T_shuf'] = Z.tables_from_history(hist.shuffled(random.Random(SHUFFLE_SEED)))
    _G['T_hoard'] = Z.tables_from_hoard(_G['hoard'])
    _G['zstar'] = tuple(state['zstar'])
    _G['z0'] = tuple(state['z0'])
    _G['cache'] = {}


def _z_for(arm, seed):
    key = (arm, seed if arm == 'RANDZ' else 0)
    if key in _G['cache']:
        return _G['cache'][key]
    if arm == 'H1':
        z = None
    elif arm == 'H2':
        z = Z.make_z(_G['zstar'], _G['T_shuf'])
    elif arm == 'H3':
        z = Z.make_z(_G['zstar'], _G['T_int'])
    elif arm == 'RANDZ':
        z = Z.make_z(Z.rand_genome(random.Random(31337 + seed)), _G['T_int'])
    elif arm == 'Z0ARM':
        z = Z.make_z(_G['z0'], _G['T_hoard'])
    else:
        raise ValueError(arm)
    _G['cache'][key] = z
    return z


def _run(job):
    arm, tid, target, n_out, seed = job
    z = _z_for(arm, seed)
    r = A.search(tuple(int(x, 16) for x in target), n_out, BUDGET,
                 (seed * 1_000_003) ^ (hash(tid) & 0xffffff), _G['hoard'], z=z)
    return dict(arm=arm, tid=tid, seed=seed, solved=r['solved'],
                calls=r['calls'], gen=r['gen'])


ARMS = ('H1', 'H2', 'H3', 'RANDZ', 'Z0ARM')


def main():
    fams = sys.argv[1:]
    st = json.load(open('F:/SerendipityA/runs/dev_state.json'))
    assert st['phase'] == 'E-FROZEN', 'dev state not frozen'
    tasks = json.load(open('F:/SerendipityA/runs/battery.json'))['tasks']
    for fam in fams:
        fts = [t for t in tasks if t['family'] == fam]
        arms = ARMS if fam == 'CONF' else ('H1', 'H3')
        jobs = [(a, t['id'], t['target'], t['n_out'], s)
                for t in fts for a in arms for s in range(SEEDS)]
        t0 = time.time()
        with Pool(10, initializer=_init, initargs=(st,)) as pool:
            res = pool.map(_run, jobs, chunksize=1)
        json.dump(res, open('F:/SerendipityA/runs/arms_%s.json' % fam, 'w'))
        agg = {}
        for r in res:
            agg.setdefault(r['arm'], []).append(r['solved'])
        print('[%s] %d runs, %.0fs' % (fam, len(res), time.time() - t0))
        for a in arms:
            v = agg[a]
            print('   %-6s solve_rate=%.3f  (%d/%d)' % (a, sum(v) / len(v), sum(v), len(v)))


if __name__ == '__main__':
    main()

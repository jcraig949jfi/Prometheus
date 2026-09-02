"""Step-8 continuation: draw-only tournament (cand_batch=1) at larger k, truth-z."""
import sys, json, time
sys.path.insert(0, 'F:/SerendipityA/src')
from multiprocessing import Pool
import arena as A
import zsig as Z
import substrate as S

_G = {}


def init(hoard_blob, T):
    _G['h'] = A.Hoard.load(hoard_blob)
    _G['z'] = Z.make_z((1, 0, 0, 0, 2, 0, 0), (T, {}, {}, {}))


def run(job):
    tid, target, n_out, seed, k, cb = job
    r = A.search(tuple(int(x, 16) for x in target), n_out, 200000, seed,
                 _G['h'], z=_G['z'], k=k, cand_batch=cb)
    return r['solved']


def main():
    st = json.load(open('F:/SerendipityA/runs/dev_state.json'))
    md = json.load(open('F:/SerendipityA/runs/modules.json'))
    T = {}
    for p, tt, c in md['modules']:
        prog = tuple(tuple(i) for i in p)
        for b in S.evaluate(prog)[S.N_IN:]:
            T[b] = 1.0
    tasks = [t for t in json.load(open('F:/SerendipityA/runs/battery.json'))['tasks']
             if t['family'] == 'DEV' and t['tier'] == 2][:6]
    out = {}
    for k, cb in ((16, 1), (32, 1), (64, 1), (32, 4)):
        jobs = [(t['id'], t['target'], t['n_out'], 9000 + i * 100 + s, k, cb)
                for i, t in enumerate(tasks) for s in range(4)]
        t0 = time.time()
        with Pool(10, initializer=init, initargs=(st['hoard'], T)) as pool:
            res = pool.map(run, jobs, chunksize=1)
        out['k%d_cb%d' % (k, cb)] = sum(res)
        print('W+ k=%2d cb=%d  solved %2d/24  (%.0fs)' % (k, cb, sum(res), time.time() - t0), flush=True)
    json.dump(out, open('F:/SerendipityA/runs/variant_test.json', 'w'))


if __name__ == '__main__':
    main()

"""Mechanistic probe (designer-side): with truth-z, how strongly does each (k, cb) config
concentrate submitted candidates onto module-pair compositions?

Counts, per config, over N probe rounds against an unsolvable dummy target:
  pair_rate : submitted candidate is combine(a, b, op) with BOTH operand outputs true modules
  one_rate  : at least one operand output a true module
Direct expected exact hits at full budget = pair_rate * (frac of the 56 ordered module
pairs x 8 ops that match a task) -> pair_rate is the transmissible signal strength.
"""
import sys, json, random, time
sys.path.insert(0, 'F:/SerendipityA/src')
import substrate as S
import arena as A
import zsig as Z

N = 20_000


def probe(hoard, z, k, cb, mods, seed):
    rng = random.Random(seed)
    hscores = [z(p) for p in hoard.items] if z else None
    ascores = [] if z else None
    archive = []
    seen = set()
    pair = one = 0
    for _ in range(N):
        if z is None:
            cand, par = A.propose(rng, hoard, None, archive, None)
            cs = None
        else:
            cand = par = cs = None
            for _ in range(cb):
                c, pr = A.propose(rng, hoard, hscores, archive, ascores, k)
                s = z(c)
                if cs is None or s > cs:
                    cand, par, cs = c, pr, s
        # classify: is cand a top-level combine of two module-output subprograms?
        w = S.evaluate(cand)
        op, a, b = cand[-1]
        am = w[a] in mods
        bm = w[b] in mods
        if am and bm and a != b:
            pair += 1
        if am or bm:
            one += 1
        bb = S.behavior(cand)
        if bb not in seen:
            seen.add(bb)
            if len(archive) < A.ARCHIVE_CAP:
                archive.append(cand)
                if ascores is not None:
                    ascores.append(cs)
            else:
                i = rng.randrange(A.ARCHIVE_CAP)
                archive[i] = cand
                if ascores is not None:
                    ascores[i] = cs
    return pair / N, one / N


def main():
    st = json.load(open('F:/SerendipityA/runs/dev_state.json'))
    md = json.load(open('F:/SerendipityA/runs/modules.json'))
    hoard = A.Hoard.load(st['hoard'])
    mods = {int(tt, 16) for _, tt, _ in md['modules']}
    T = {}
    for p, tt, c in md['modules']:
        for b in S.evaluate(tuple(tuple(i) for i in p))[S.N_IN:]:
            T[b] = 1.0
    z = Z.make_z((1, 0, 0, 0, 2, 0, 0), (T, {}, {}, {}))
    print('%-14s %-10s %-10s' % ('config', 'pair_rate', 'one_rate'))
    out = {}
    for label, zz, k, cb in (
            ('none', None, 1, 1),
            ('k8_cb8', z, 8, 8), ('k16_cb16', z, 16, 16),
            ('k16_cb1', z, 16, 1), ('k32_cb1', z, 32, 1), ('k32_cb4', z, 32, 4),
            ('k32_cb8', z, 32, 8), ('k64_cb8', z, 64, 8), ('k16_cb8', z, 16, 8),
            ('k8_cb16', z, 8, 16), ('k4_cb16', z, 4, 16)):
        t0 = time.time()
        pr, onr = probe(hoard, zz, k, cb, mods, 555)
        out[label] = [pr, onr]
        print('%-14s %-10.5f %-10.5f (%.0fs)' % (label, pr, onr, time.time() - t0), flush=True)
    json.dump(out, open('F:/SerendipityA/runs/mech_probe.json', 'w'))


if __name__ == '__main__':
    main()

"""Section-15 geometry diagnostics. ANALYSIS ONLY - these never admit or select z.

Measures, for H1 vs H3 on CONF tasks:
  first_passage : distribution of oracle calls to first exact solve (solved runs)
  probe rates   : on-manifold concentration of submitted candidates (module wires),
                  using privileged module knowledge the learner never had
  rank corr     : Spearman rank correlation between z score and privileged oracle
                  distance (min Hamming of candidate output to target over tasks)
"""
import json, random, sys
sys.path.insert(0, 'F:/SerendipityA/src')
import substrate as S
import arena as A
import zsig as Z

N_PROBE = 20_000


def spearman(x, y):
    def rank(v):
        idx = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(idx):
            j = i
            while j + 1 < len(idx) and v[idx[j + 1]] == v[idx[i]]:
                j += 1
            avg = (i + j) / 2.0
            for t in range(i, j + 1):
                r[idx[t]] = avg
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    mx = sum(rx) / len(rx)
    my = sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = sum((a - mx) ** 2 for a in rx) ** 0.5
    dy = sum((b - my) ** 2 for b in ry) ** 0.5
    return num / (dx * dy) if dx and dy else 0.0


def main():
    st = json.load(open('F:/SerendipityA/runs/dev_state.json'))
    md = json.load(open('F:/SerendipityA/runs/modules.json'))
    conf = json.load(open('F:/SerendipityA/runs/arms_CONF.json'))
    hoard = A.Hoard.load(st['hoard'])
    hist = A.History.load(st['history'])
    z = Z.make_z(tuple(st['zstar']), Z.tables_from_history(hist))
    mods = {int(tt, 16) for _, tt, _ in md['modules']}
    modwires = set()
    for p, tt, c in md['modules']:
        modwires |= set(S.evaluate(tuple(tuple(i) for i in p))[S.N_IN:])

    out = {}
    # 1. first-passage distributions
    for arm in ('H1', 'H3'):
        fp = sorted(r['calls'] for r in conf if r['arm'] == arm and r['solved'])
        out['first_passage_' + arm] = dict(
            n=len(fp), median=fp[len(fp) // 2] if fp else None,
            q1=fp[len(fp) // 4] if fp else None, q3=fp[3 * len(fp) // 4] if fp else None)
        print('first-passage %s: n=%d %s' % (arm, len(fp), out['first_passage_' + arm]))

    # 2. on-manifold concentration of submitted candidates (privileged classification)
    rng = random.Random(99)
    for arm, zz in (('H1', None), ('H3', z)):
        hs = [zz(p) for p in hoard.items] if zz else None
        asc = [] if zz else None
        archive, seen = [], set()
        pair = one = 0
        for _ in range(N_PROBE):
            cand, par = A.propose(rng, hoard, hs, archive, asc, A.K_TOURN if zz else 1)
            cs = zz(cand) if zz else None
            w = S.evaluate(cand)
            op, a, b = cand[-1]
            am, bm = w[a] in mods, w[b] in mods
            pair += am and bm and a != b
            one += am or bm
            bb = S.behavior(cand)
            if bb not in seen:
                seen.add(bb)
                if len(archive) < A.ARCHIVE_CAP:
                    archive.append(cand)
                    if asc is not None:
                        asc.append(cs)
                else:
                    i = rng.randrange(A.ARCHIVE_CAP)
                    archive[i] = cand
                    if asc is not None:
                        asc[i] = cs
        out['manifold_' + arm] = dict(pair_rate=pair / N_PROBE, one_rate=one / N_PROBE)
        print('manifold %s: pair=%.5f one=%.5f' % (arm, pair / N_PROBE, one / N_PROBE))

    # 3. rank correlation of z with privileged oracle distance (CONF tier2 targets)
    bat = json.load(open('F:/SerendipityA/runs/battery.json'))['tasks']
    t2 = [int(t['target'][0], 16) for t in bat if t['family'] == 'CONF' and t['tier'] == 2]
    rng = random.Random(7)
    zs, ds = [], []
    for _ in range(3000):
        p = S.random_program(rng, 2, 12)
        b = S.behavior(p)[0]
        zs.append(z(p))
        ds.append(min(bin(b ^ t).count('1') for t in t2))
    rho = spearman(zs, [-d for d in ds])
    out['spearman_z_vs_negdist'] = rho
    print('spearman(z, -oracle_distance) over random programs: %.3f' % rho)
    json.dump(out, open('F:/SerendipityA/runs/geometry.json', 'w'), indent=1)


if __name__ == '__main__':
    main()

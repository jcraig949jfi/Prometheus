"""Construct the exact task battery and PROVE solver existence (P0).

Every task carries a constructively built witness program whose full-domain behavior is
verified equal to the hidden target. Witnesses are designer-side and are never exposed to
any learner arm.

CALIBRATION RULE (fixed before any M0 evidence): a composite task is admitted only if every
one of its target outputs is non-degenerate AND was never produced by any of the 500,000
blind samples. Compositions that collapse onto common behaviors are rejected, so no task is
solvable by luck alone. DEV tier1 targets are the modules themselves and keep their measured
rarity of 1-4 hits per 500,000.
"""
import json, random, sys
sys.path.insert(0, 'F:/SerendipityA/src')
import substrate as S
import build_battery as B

SEED = 20260827
N_T2, N_T3 = 12, 12          # per split
N_ALIEN, N_STRUCT = 12, 12


def copy_out(prog, wires):
    """Append idempotent copies so the designated outputs are the final wires, in order."""
    p = tuple(prog)
    for w in wires:
        p = p + ((0, w, w),)          # AND(w,w) == w
    return p


def t2(mods, c):
    i, j, op = c
    return S.combine(mods[i][0], mods[j][0], op)


def t3(mods, c):
    i, j, k, o1, o2 = c
    return S.combine(S.combine(mods[i][0], mods[j][0], o1), mods[k][0], o2)


def alien(mods, c):
    """Different surface: TWO designated outputs, the second consuming the first."""
    a, b, cc, o1, o2 = c
    p1 = S.combine(mods[a][0], mods[b][0], o1)
    prog, w1, _ = S.splice(p1, mods[cc][0])
    wc = S.N_IN + len(prog) - 1
    prog = prog + ((o2, wc, w1),)
    w2 = S.N_IN + len(prog) - 1
    return copy_out(prog, [w1, w2])


def mk(tid, family, tier, witness, n_out, freq):
    beh = S.behavior(witness, n_out)
    assert len(witness) <= S.LMAX, (tid, len(witness))
    return dict(id=tid, family=family, tier=tier, n_out=n_out,
                target=[hex(x) for x in beh],
                witness=[list(i) for i in witness], wlen=len(witness),
                blind_count=[freq.get(x, 0) for x in beh])


def sample_tasks(rng, mods, arity, n, used, build, family, tier, n_out, freq, prefix,
                 seen_targets):
    """Propose index/op combinations until n admissible tasks are found."""
    out, tries = [], 0
    while len(out) < n:
        tries += 1
        assert tries < 200000, (family, tier)
        c = tuple(rng.randrange(len(mods)) for _ in range(arity)) + \
            tuple(rng.randrange(S.N_OPS) for _ in range(arity - 1))
        if len(set(c[:arity])) < arity or c in used:
            continue
        w = build(mods, c)
        if len(w) > S.LMAX:
            continue
        beh = S.behavior(w, n_out)
        if any(freq.get(x, 0) != 0 or B.degenerate(x) for x in beh):
            continue
        if len(set(beh)) < n_out:                     # outputs must not be identical
            continue
        if beh in seen_targets:                       # global target uniqueness
            continue
        seen_targets.add(beh)
        used.add(c)
        out.append(mk('%s_%d' % (prefix, len(out)), family, tier, w, n_out, freq))
    return out


def main():
    rng = random.Random(SEED + 1)
    md = json.load(open('F:/SerendipityA/runs/modules.json'))
    mods = [(tuple(tuple(i) for i in p), int(tt, 16), c) for p, tt, c in md['modules']]
    negm = [(tuple(tuple(i) for i in p), int(tt, 16), c) for p, tt, c in md['neg_modules']]
    freq = B.blind_freq()

    tasks, used, seen_targets = [], set(), set()

    for i, (p, tt, c) in enumerate(mods):                       # DEV tier1 = bare modules
        tasks.append(mk('dev1_%d' % i, 'DEV', 1, p, 1, freq))
        seen_targets.add(S.behavior(p, 1))

    for lbl, split in (('dev', 'DEV'), ('conf', 'CONF')):
        tasks += sample_tasks(rng, mods, 2, N_T2, used, t2, split, 2, 1, freq, lbl + '2', seen_targets)
        tasks += sample_tasks(rng, mods, 3, N_T3, used, t3, split, 3, 1, freq, lbl + '3', seen_targets)

    tasks += sample_tasks(rng, mods, 3, N_ALIEN, used, alien, 'ALIEN', 3, 2, freq, 'alien', seen_targets)

    nused = set()
    tasks += sample_tasks(rng, negm, 2, N_T2, nused, t2, 'NEG', 2, 1, freq, 'neg2', seen_targets)
    tasks += sample_tasks(rng, negm, 3, N_T3, nused, t3, 'NEG', 3, 1, freq, 'neg3', seen_targets)

    n = 0                                                        # STRUCT: no module content
    while n < N_STRUCT:
        p = S.random_program(rng, 10, 16)
        tt = S.behavior(p)[0]
        if freq.get(tt, 0) != 0 or B.degenerate(tt) or (tt,) in seen_targets:
            continue
        seen_targets.add((tt,))
        tasks.append(mk('struct_%d' % n, 'STRUCT', 3, p, 1, freq))
        n += 1

    # ---- P0: verify every witness solves its own task exactly, over the full domain
    bad = [t['id'] for t in tasks
           if [hex(x) for x in S.behavior(tuple(tuple(i) for i in t['witness']), t['n_out'])]
           != t['target'] or t['wlen'] > S.LMAX]
    assert not bad, bad

    ids = [t['id'] for t in tasks]
    assert len(set(ids)) == len(ids)
    dev_t = {tuple(t['target']) for t in tasks if t['family'] == 'DEV'}
    conf_t = {tuple(t['target']) for t in tasks if t['family'] == 'CONF'}
    assert not (dev_t & conf_t), 'DEV/CONF target overlap'

    fams = {}
    for t in tasks:
        fams.setdefault((t['family'], t['tier']), []).append(t)
    print('[P0] %d tasks, all witnesses verified exact over all 64 rows' % len(tasks))
    for k in sorted(fams):
        g = fams[k]
        print('   %-9s tier%d  n=%2d  witness_len %2d-%2d  target blind_count max=%d'
              % (k[0], k[1], len(g), min(x['wlen'] for x in g), max(x['wlen'] for x in g),
                 max(max(x['blind_count']) for x in g)))
    print('[P0] DEV/CONF target disjointness verified')
    json.dump(dict(seed=SEED, tasks=tasks), open('F:/SerendipityA/runs/battery.json', 'w'))
    print('[P0] wrote runs/battery.json')


if __name__ == '__main__':
    main()

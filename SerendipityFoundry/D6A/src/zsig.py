"""Frozen signal grammar (PREREG AMENDMENT 2) and table construction per condition.

genome = (w0, w1, w2, w3, tf, agg, lw)
  wi  in {-1,0,1} : weight on table slot Ti
  tf  in {0,1,2}  : per-wire transform  id | signed-log1p | positivity indicator
  agg in {0,1,2,3}: sum | max | mean | count-positive   over distinct wire behaviors
  lw  in {-1,0,1} : + lw * 0.1 * len(prog)
2916 genomes. Same grammar for Z0, Z1, H2, RAND-Z; only table CONTENTS differ.
"""
import math, random, sys
sys.path.insert(0, 'F:/SerendipityA/src')
import substrate as S

GRID = dict(w=(-1, 0, 1), tf=(0, 1, 2), agg=(0, 1, 2, 3), lw=(-1, 0, 1))


def rand_genome(rng):
    w = GRID['w']
    return (rng.choice(w), rng.choice(w), rng.choice(w), rng.choice(w),
            rng.choice(GRID['tf']), rng.choice(GRID['agg']), rng.choice(GRID['lw']))


def all_genomes():
    out = []
    w = GRID['w']
    for w0 in w:
        for w1 in w:
            for w2 in w:
                for w3 in w:
                    for tf in GRID['tf']:
                        for agg in GRID['agg']:
                            for lw in GRID['lw']:
                                out.append((w0, w1, w2, w3, tf, agg, lw))
    return out


def make_z(genome, tables):
    """Compile a genome + 4 table slots into an executable scoring artifact."""
    w0, w1, w2, w3, tf, agg, lw = genome
    T0, T1, T2, T3 = tables
    g0, g1, g2, g3 = T0.get, T1.get, T2.get, T3.get
    log1p = math.log1p

    def z(prog):
        vals = []
        for b in set(S.evaluate(prog)[S.N_IN:]):
            v = 0.0
            if w0: v += w0 * g0(b, 0.0)
            if w1: v += w1 * g1(b, 0.0)
            if w2: v += w2 * g2(b, 0.0)
            if w3: v += w3 * g3(b, 0.0)
            if tf == 1:
                v = log1p(v) if v >= 0 else -log1p(-v)
            elif tf == 2:
                v = 1.0 if v > 0 else 0.0
            vals.append(v)
        if agg == 0:
            s = sum(vals)
        elif agg == 1:
            s = max(vals)
        elif agg == 2:
            s = sum(vals) / len(vals)
        else:
            s = float(sum(1 for v in vals if v > 0))
        return s + lw * 0.1 * len(prog)

    return z


def tables_from_history(hist):
    """Z1/H3 slots: recurrence, ancestry, co-occurrence degree, solved-output indicator."""
    deg = {}
    for (a, b), v in hist.cooc.items():
        deg[a] = deg.get(a, 0) + v
        deg[b] = deg.get(b, 0) + v
    return (dict(hist.recur), dict(hist.anc), deg, {b: 1.0 for b in hist.solved})


def tables_from_hoard(hoard):
    """Z0 slots: membership, entry length, behavior popcount, empty. Bag-intrinsic only."""
    mem, ln, pc = {}, {}, {}
    for b, p in hoard.by_beh.items():
        mem[b] = 1.0
        ln[b] = float(len(p))
        pc[b] = float(bin(b).count('1'))
    return (mem, ln, pc, {})

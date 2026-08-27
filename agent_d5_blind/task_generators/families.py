"""Task family generators + constructive compiler. Spec: PREREG-TASKS.md.

gen_task(family, seed) -> task dict:
  learner-visible:  {'domain': [...], 'table': [(inputs, output), ...]}
  oracle-side ONLY: {'family', 'seed', 'gen_meta', 'witness'} — stripped
  before anything reaches a navigator or learner (anti-cheat checks this).

The compiled witness is the constructive expressibility proof (E gate); its
correctness is verified against the table by the exact oracle at generation
time. A witness longer than MAX_LEN -> expressibility falls to bounded
synthesis or UNKNOWN (handled by the caller; compiler returns it regardless).
"""
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'substrate'))
from rm_vm import MAX_LEN
from hidden_library import make_H, make_PREDS, COMBINERS, PIDX, M

H = make_H(poison=False)
H_POISON = make_H(poison=True)
PREDS = make_PREDS()
PAL = sorted(PIDX)

D64 = [(x,) for x in range(64)]
D4 = [(x,) for x in range(4)]
D8x8 = [(x, y) for x in range(8) for y in range(8)]


def _compose_py(prims):
    def f(x):
        for p in prims:
            x = p['py'](x)
        return x
    return f


def _compose_tmpl(prims):
    out = []
    for p in prims:
        out.extend(p['tmpl'])
    return tuple(out)


def _pick(rng, pool, k):
    return [pool[rng.randrange(len(pool))] for _ in range(k)]


def gen_f1(seed, pool=None):
    """AFFMOD: composition of k=2..5 unary primitives on D64."""
    pool = pool or H
    rng = random.Random(seed)
    k = rng.randint(1, 5)   # depth-1 on-ramp included (curriculum needs a
    prims = _pick(rng, pool, k)   # findable band; calibrated 2026-08-27)
    f = _compose_py(prims)
    return {'family': 'F1', 'seed': seed, 'domain': D64,
            'table': [((x,), f(x)) for (x,) in D64],
            'gen_meta': {'depth': k, 'prims': [p['name'] for p in prims]},
            'witness': _compose_tmpl(prims)}


def gen_f2(seed, pool=None):
    """PIECE: if p(x) then gA(x) else gB(x) via arithmetic select."""
    pool = pool or H
    rng = random.Random(seed)
    p = PREDS[rng.randrange(len(PREDS))]
    ga = _pick(rng, pool, rng.randint(1, 2))
    gb = _pick(rng, pool, rng.randint(1, 2))
    fa, fb, fp = _compose_py(ga), _compose_py(gb), p['py']

    def f(x):
        return fa(x) if fp(x) else fb(x)
    # r4=x; r0=gA(x); r5=gA; r0=gB(x); r3=p; r0 = gB + p*(gA-gB)
    w = [('MOV', 4, 0)]
    w += list(_compose_tmpl(ga))
    w += [('MOV', 5, 0), ('MOV', 0, 4)]
    w += list(_compose_tmpl(gb))
    w += list(p['tmpl'])
    w += [('SUB', 5, 0), ('MUL', 5, 3), ('ADD', 0, 5)]
    return {'family': 'F2', 'seed': seed, 'domain': D64,
            'table': [((x,), f(x)) for (x,) in D64],
            'gen_meta': {'pred': p['name'], 'ga': [q['name'] for q in ga],
                         'gb': [q['name'] for q in gb]},
            'witness': tuple(w)}


def gen_f3(seed, pool=None):
    """ITER: g^k. Witness = min(unrolled, loop form) that fits."""
    pool = pool or H
    rng = random.Random(seed)
    k = rng.choice([2, 3, 5, 7])            # palette values (loop form needs SET k)
    g = _pick(rng, pool, rng.randint(1, 2))
    gf = _compose_py(g)

    def f(x):
        for _ in range(k):
            x = gf(x)
        return x
    body = list(_compose_tmpl(g))
    unrolled = tuple(body * k)
    candidates = [unrolled]
    if len(body) + 1 <= 8:                   # JNZ back-jump limit
        loop = [('SET', 6, PIDX[k]), ('SET', 7, PIDX[1])] + body + \
               [('SUB', 6, 7), ('JNZ', 6, len(body) + 1)]
        candidates.append(tuple(loop))
    w = min(candidates, key=len)
    return {'family': 'F3', 'seed': seed, 'domain': D64,
            'table': [((x,), f(x)) for (x,) in D64],
            'gen_meta': {'k': k, 'g': [q['name'] for q in g],
                         'loop_form': len(candidates) > 1 and w != unrolled},
            'witness': w}


def gen_f4(seed, pool=None):
    """BIT: composition of bit-flavored primitives on D64."""
    pool = pool or H
    bitpool = [p for p in pool if p['name'].startswith(
        ('SWAP3', 'ANDC', 'ORC', 'XORC', 'SHLC', 'SHRC'))]
    rng = random.Random(seed)
    k = rng.randint(1, 4)
    prims = _pick(rng, bitpool, k)
    f = _compose_py(prims)
    return {'family': 'F4', 'seed': seed, 'domain': D64,
            'table': [((x,), f(x)) for (x,) in D64],
            'gen_meta': {'depth': k, 'prims': [p['name'] for p in prims]},
            'witness': _compose_tmpl(prims)}


def gen_ctrl(seed):
    """CTRL-RAND: independently random lookup table on {0..n-1}, n in {2,3,4},
    outputs in the palette. Structureless by construction (content is iid
    random). Case-count mix keeps part of the family inside the M0-findable
    band so the G8 selectivity gate is not a floor effect (fixed wlen-21
    4-case tables measured 0/8 findable at 30k on engineering seeds)."""
    rng = random.Random(seed)
    n = rng.choice([2, 3, 4])
    ys = [PAL[rng.randrange(len(PAL))] for _ in range(n)]
    # SET r1 0; SET r6 y0; for i in 1..n-1: MOV r2 r0; SET r3 i; XOR r2 r3;
    #   SET r4 yi; SKG r2 r1; MOV r6 r4;  then MOV r0 r6
    w = [('SET', 1, PIDX[0]), ('SET', 6, PIDX[ys[0]])]
    for i in range(1, n):
        w += [('MOV', 2, 0), ('SET', 3, PIDX[i]), ('XOR', 2, 3),
              ('SET', 4, PIDX[ys[i]]), ('SKG', 2, 1), ('MOV', 6, 4)]
    w += [('MOV', 0, 6)]
    dom = [(x,) for x in range(n)]
    return {'family': 'CTRL', 'seed': seed, 'domain': dom,
            'table': [((x,), ys[x]) for (x,) in dom],
            'gen_meta': {'ys': ys, 'cases': n},
            'witness': tuple(w)}


def gen_negxfer(seed):
    """NEGXFER: F1/F2 surface with poisoned constants H'."""
    rng = random.Random(seed)
    sub = rng.choice(['F1', 'F2'])
    t = gen_f1(seed * 2 + 1, pool=H_POISON) if sub == 'F1' \
        else gen_f2(seed * 2 + 1, pool=H_POISON)
    t['family'] = 'NEGX'
    t['seed'] = seed
    t['gen_meta']['poisoned'] = True
    return t


def gen_alien(seed):
    """ALIEN: f(x,y) = combiner(hA(x), hB(y)) on 8x8. Two inputs (r0, r1)."""
    rng = random.Random(seed)
    ha = _pick(rng, H, rng.randint(1, 2))
    hb = _pick(rng, H, rng.randint(1, 2))
    c = COMBINERS[rng.randrange(len(COMBINERS))]
    fa, fb = _compose_py(ha), _compose_py(hb)

    def f(x, y):
        return c['py'](fa(x), fb(y))
    # y arrives in r1 which is primitive scratch: stash to r7 first.
    # r0=hA(x); r6=hA; r0 <- r7 (y); r0=hB(y); combine(r6, r0) -> r0
    w = [('MOV', 7, 1)]
    w += list(_compose_tmpl(ha))
    w += [('MOV', 6, 0), ('MOV', 0, 7)]
    w += list(_compose_tmpl(hb))
    w += list(c['tmpl'])
    return {'family': 'ALIEN', 'seed': seed, 'domain': D8x8,
            'table': [((x, y), f(x, y)) for (x, y) in D8x8],
            'gen_meta': {'ha': [q['name'] for q in ha],
                         'hb': [q['name'] for q in hb], 'comb': c['name']},
            'witness': tuple(w)}


GENERATORS = {'F1': gen_f1, 'F2': gen_f2, 'F3': gen_f3, 'F4': gen_f4,
              'CTRL': gen_ctrl, 'NEGX': gen_negxfer, 'ALIEN': gen_alien}


def gen_task(family, seed):
    """Deterministic resample-until-fit: if a compiled witness exceeds MAX_LEN
    (~0.6% of raw draws, measured on engineering seeds), redraw from a derived
    sub-seed. Truncates the deepest tail of the raw distribution; frozen
    behavior, documented in PREREG-TASKS.md section 4."""
    for attempt in range(50):
        t = GENERATORS[family](seed + attempt * 100003)
        if len(t['witness']) <= MAX_LEN:
            t['seed'] = seed
            t['gen_meta']['resampled'] = attempt
            return t
    raise RuntimeError(f'no fitting witness for {family} seed {seed}')


def learner_view(task):
    """The ONLY fields a navigator/learner may receive."""
    return {'domain': task['domain'], 'table': task['table']}

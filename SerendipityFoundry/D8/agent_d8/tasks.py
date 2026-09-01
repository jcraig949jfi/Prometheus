"""Task generation and verification for D-8.

QUARANTINE NOTE (anti-tautology discipline):
  ORACLE-SIDE fields of a task: 'family', 'gen', 'hidden', 'resamples'.
  LEARNER-VISIBLE interface: 'uid' and 'revealed' ONLY (6 input/output pairs).
  No family labels, generator structure, or hidden inputs may reach the
  learner. The verifier returns a single boolean and nothing else.

Families (mechanisms hidden from the learner):
  F1  op-soup biased toward 8-bit arithmetic ops.
  F2  motif-composed: prefix + motif(s) + glue drawn from a secret pool of 12
      motifs shared across F2 tasks (planted reusable structure; hidden;
      the positive verdict must not rest on F2 alone -- per-family
      heterogeneity is reported).
  F3  op-soup biased toward bit-logic / comparison / SEL ops.
  F4  HELD-OUT (eval only): compiled parametric affine/xor templates -- a
      materially different generative mechanism (dense constants, fixed
      shapes) from the sampled op-soups.
  F5  STRUCTURELESS control: outputs are SHA-derived random bytes; no
      generating program exists; history should not help; solve rate should
      be ~0 everywhere.
  F6  MISLEADING (eval only): same construction as F2 but an independent,
      disjoint motif pool -- surface-similar, statistics anti-transfer.

Exactness: a candidate 'solves' a task iff it matches all 6 revealed pairs
AND all 24 hidden verification pairs. The verifier answers only yes/no.
"""

import hashlib

from svm import (rng, run, LD0, LD1, LD2, ADD, SUB, MUL, MULHI, AND_, OR_,
                 XOR, NOT_, SHL, SHR, INC, DEC, NEG, DUP, SWAP, OVER, STO,
                 RCL, EQ, LT, SEL, MAXLEN)

_C = "C"  # placeholder meaning: emit a literal token

F1_POOL = ([LD0] * 3 + [LD1] * 3 + [LD2] * 2 + [_C] * 3 + [ADD] * 3 +
           [SUB] * 2 + [MUL] * 2 + [MULHI] + [INC] + [DEC] + [NEG] +
           [DUP] * 2 + [SWAP] + [STO] + [RCL])

F3_POOL = ([LD0] * 3 + [LD1] * 3 + [LD2] * 2 + [_C] * 2 + [AND_] * 2 +
           [OR_] * 2 + [XOR] * 3 + [NOT_] * 2 + [SHL] * 2 + [SHR] * 2 +
           [EQ] + [LT] + [SEL] * 2 + [DUP] * 2 + [OVER])

MIX_POOL = F1_POOL + F3_POOL


def _tok(r, pool):
    t = r.choice(pool)
    if t == _C:
        return 256 + r.randrange(256)
    return t


def _motif_pool(tag):
    """Secret pool of 12 motifs (len 3-5). tag 'A' feeds F2, 'B' feeds F6."""
    r = rng("motifpool-v1", tag)
    return [tuple(_tok(r, MIX_POOL) for _ in range(r.randint(3, 5)))
            for _ in range(12)]


_POOLS = {}


def motif_pool(tag):
    if tag not in _POOLS:
        _POOLS[tag] = _motif_pool(tag)
    return _POOLS[tag]


def _gen_soup(r, pool, lmin, lmax):
    n = r.randint(lmin, lmax)
    return [_tok(r, pool) for _ in range(n)]


def _gen_motif(r, tag):
    pool = motif_pool(tag)
    g = [r.choice((LD0, LD1, LD2)) for _ in range(r.randint(1, 2))]
    g += list(r.choice(pool))
    g += [_tok(r, MIX_POOL) for _ in range(r.randint(0, 2))]
    if r.random() < 0.7:
        g += list(r.choice(pool))
    return g[:MAXLEN]


def _gen_f4(r):
    p = r.sample([LD0, LD1, LD2], 3)
    a, b = 256 + r.randrange(1, 256), 256 + r.randrange(1, 256)
    t = r.randrange(6)
    if t == 0:
        return [p[0], a, ADD, p[1], XOR]
    if t == 5:
        return [p[0], a, ADD, p[1], ADD]
    if t == 1:
        return [a, p[0], MUL, b, ADD, p[1], XOR]
    if t == 2:
        return [p[0], p[1], ADD, a, MUL, p[2], XOR]
    if t == 3:
        return [p[0], a, MUL, p[1], ADD, b, XOR]
    return [p[0], p[1], XOR, a, MUL, b, ADD, p[2], SUB]


def _revealed_inputs(uid):
    r = rng("inputs-v1", uid)
    xs = [(r.randrange(256), r.randrange(256), r.randrange(256))
          for _ in range(4)]
    xs += [(0, 0, 0), (1, 255, 128)]
    return xs


def _hidden_inputs(uid, revealed):
    r = rng("hidden-v1", uid)
    seen = set(revealed)
    xs = []
    fixed = [(255, 255, 255), (128, 64, 32), (2, 3, 5), (7, 0, 255)]
    for f in fixed:
        if f not in seen:
            xs.append(f)
            seen.add(f)
    while len(xs) < 24:
        x = (r.randrange(256), r.randrange(256), r.randrange(256))
        if x not in seen:
            xs.append(x)
            seen.add(x)
    return xs


def _screen_trivial(uid, attempt, g, ri):
    """ORACLE-SIDE difficulty screen: a task is 'trivial' if a fixed
    250-candidate uniform random probe (seeded from the uid, independent of
    any learner's search stream) reproduces all 6 revealed outputs. Trivial
    generators are resampled. This keeps exact solutions in existence while
    removing tasks crackable by noise."""
    rr = rng("screen-v1", uid, attempt)
    target = [run(g, *x)[0] for x in ri]
    for _ in range(250):
        n = rr.randint(1, MAXLEN)
        p = []
        for _ in range(n):
            i = rr.randrange(26)
            p.append(256 + rr.randrange(256) if i == 3 else i)
        ok = True
        for x, y in zip(ri, target):
            if run(p, *x)[0] != y:
                ok = False
                break
        if ok:
            return True
    return False


def _f5_out(uid, x):
    h = hashlib.sha256(("F5|%s|%d,%d,%d" % (uid, x[0], x[1], x[2])).encode())
    return h.digest()[0]


def make_task(family, uid):
    """Deterministic task construction from (family, uid)."""
    ri = _revealed_inputs(uid)
    hi = _hidden_inputs(uid, ri)
    if family == "F5":
        revealed = [(x, _f5_out(uid, x)) for x in ri]
        hidden = [(x, _f5_out(uid, x)) for x in hi]
        return dict(uid=uid, family=family, gen=None, revealed=revealed,
                    hidden=hidden, resamples=0)
    r = rng("gen-v1", uid)
    gen = None
    resamples = 0
    for attempt in range(60):
        if family == "F1":
            g = _gen_soup(r, F1_POOL, 7, 12)
        elif family == "F3":
            g = _gen_soup(r, F3_POOL, 7, 12)
        elif family == "F2":
            g = _gen_motif(r, "A")
        elif family == "F6":
            g = _gen_motif(r, "B")
        elif family == "F4":
            g = _gen_f4(r)
        else:
            raise ValueError(family)
        outs = [run(g, *x)[0] for x in hi]
        if len(set(outs)) >= 4 and not _screen_trivial(uid, attempt, g, ri):
            gen = g
            break
        resamples += 1
    if gen is None:
        gen = g  # accept last; flagged by resamples==60
    revealed = [(x, run(gen, *x)[0]) for x in ri]
    hidden = [(x, run(gen, *x)[0]) for x in hi]
    return dict(uid=uid, family=family, gen=gen, revealed=revealed,
                hidden=hidden, resamples=resamples)


def make_battery(spec, prefix):
    """spec: list of (family, count). uids are '{prefix}-{family}-{i:02d}'."""
    out = []
    for fam, n in spec:
        for i in range(n):
            out.append(make_task(fam, "%s-%s-%02d" % (prefix, fam, i)))
    return out


CAL_SPEC = [("F1", 10), ("F2", 10), ("F3", 10), ("F4", 8), ("F5", 4)]
VAL_SPEC = [("F1", 7), ("F2", 7), ("F3", 6)]
DEV_SPEC = [("F1", 20), ("F2", 20), ("F3", 20)]
EV_SPEC = [("F1", 20), ("F2", 20), ("F3", 20), ("F4", 16), ("F5", 8),
           ("F6", 12)]

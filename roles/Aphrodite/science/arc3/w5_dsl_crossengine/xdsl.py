"""ARC3 / W5 -- a MODIFIED COPY of the fold evaluator with candidate DSL extensions.

Forensic, not a disposition. Label APHRODITE/ARC3/W5/v1. Engine files are imported
READ-ONLY (basis_v4 for the G4 grammar and its semantics); nothing in engine/ is
modified. The DSL extension is PARKED by the operator: this module CHARACTERISES
candidate extensions, it does not adopt any.

Extended state (all extensions share one evaluator; an atom that a grammar does not
contain is simply never mentioned):
    acc  accumulator                 v  current list element
    p    PREVIOUS list element (lag register on v; 0 before the first step)
    q    PREVIOUS accumulator  (lag register on acc; 0 before the first step)
    i    1-based position of v in the list (index atom); in the FINAL, i = n (length)
    first, last (query m) as in G4; integer literals 2..9 as atoms (CONST)
    max/min as extra binary operators (OPS)
Semantics otherwise identical to basis_v4.run_program / tribunal_t4.run: guarded pow
(exponent outside 0..32 -> 0, counted as a guard hit), gcd of absolute values,
x // 0 and x % 0 raise -> None, |value| > 10^40 -> None. In the FINAL, v = last list
element and p = the element before it (T4 convention: final sees v = vals[-1]).
"""
import math
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
ENG = HERE.parents[2] / "engine"
if str(ENG) not in sys.path:
    sys.path.insert(0, str(ENG))
import basis_v4 as G      # noqa: E402  (read-only)
import engine as E        # noqa: E402  (read-only: PRIMITIVES)

LABEL = "APHRODITE/ARC3/W5/v1"
CEIL = G.CEIL
_GUARD = [0]


def _pw(a, b):
    if b < 0 or b > 32:
        _GUARD[0] += 1
        return 0
    return pow(a, b)


_GX = {"__builtins__": {}, "math": math, "abs": abs, "pow": _pw, "max": max, "min": min}
_FN: Dict[str, object] = {}
ARGS = "acc, v, p, q, i, first, last"


def fn(expr):
    f = _FN.get(expr)
    if f is None:
        f = eval("lambda %s: (%s)" % (ARGS, expr), _GX)   # noqa: S307
        if len(_FN) > 400_000:
            _FN.clear()
        _FN[expr] = f
    return f


def run(prog, xs: List[int], m: int, trace: Optional[list] = None) -> Tuple[Optional[int], int]:
    _GUARD[0] = 0
    vals, first, last = list(xs), (xs[0] if xs else m), m
    try:
        if prog[0] == "expr":
            out = fn(prog[1])(0, 0, 0, 0, 0, first, last)
        else:
            _, init, body, final = prog
            bf = fn(body)
            acc = fn(init)(0, 0, 0, 0, 0, first, last)
            p = q = 0
            for k, v in enumerate(vals, 1):
                new = bf(acc, v, p, q, k, first, last)
                if new is None or abs(new) > CEIL:
                    return None, _GUARD[0]
                q, p, acc = acc, v, new
                if trace is not None:
                    trace.append(acc)
            vl = vals[-1] if vals else 0
            pl = vals[-2] if len(vals) > 1 else 0
            out = fn(final)(acc, vl, pl, q, len(vals), first, last)
        if out is None or abs(out) > CEIL:
            return None, _GUARD[0]
        return out, _GUARD[0]
    except Exception:      # noqa: BLE001
        return None, _GUARD[0]


# ---------------------------------------------------------------- grammars
PRIMS = sorted(E.PRIMITIVES.items())
TMPL = [t for _n, (_f, t) in PRIMS]
EXTRA_OPS = ["max({0}, {1})", "min({0}, {1})"]
CONSTS = [str(c) for c in range(2, 10)]


def exprs(atoms, depth, tmpls=None, symmetric=False):
    """basis_v4._exprs generalised: left-atom templates op(atom, level1) at depth 2
    (G4 convention). symmetric=True additionally adds op(level1, atom) and
    op(level1, level1) (compound LEFT operands)."""
    tmpls = TMPL if tmpls is None else tmpls
    out = list(atoms)
    if depth >= 1:
        for t in tmpls:
            for a in atoms:
                for b in atoms:
                    out.append(t.format(a, b))
    if depth >= 2:
        level1 = list(out)
        comp = [b for b in level1 if b not in atoms]
        for t in tmpls:
            for a in atoms:
                for b in comp:
                    out.append(t.format(a, b))
        if symmetric:
            for t in tmpls:
                for a in comp:
                    for b in atoms:
                        out.append(t.format(a, b))
                for a in comp:
                    for b in comp:
                        out.append(t.format(a, b))
    return list(dict.fromkeys(out))


VARIANTS = {
    # name: (body atoms, init atoms, final atoms, templates, symmetric)
    "G4":     (G.BODY_ATOMS, G.INIT_ATOMS, G.FINAL_ATOMS, TMPL, False),
    "CONST":  (G.BODY_ATOMS + CONSTS, G.INIT_ATOMS + CONSTS, G.FINAL_ATOMS + CONSTS, TMPL, False),
    "LAGV":   (G.BODY_ATOMS + ["p"], G.INIT_ATOMS, G.FINAL_ATOMS + ["p"], TMPL, False),
    "LAGACC": (G.BODY_ATOMS + ["q"], G.INIT_ATOMS, G.FINAL_ATOMS + ["q"], TMPL, False),
    "INDEX":  (G.BODY_ATOMS + ["i"], G.INIT_ATOMS, G.FINAL_ATOMS + ["i"], TMPL, False),
    "SYM":    (G.BODY_ATOMS, G.INIT_ATOMS, G.FINAL_ATOMS, TMPL, True),
    "OPS":    (G.BODY_ATOMS, G.INIT_ATOMS, G.FINAL_ATOMS, TMPL + EXTRA_OPS, False),
}


def grammar(name):
    ba, ia, fa, tm, sym = VARIANTS[name]
    return {"body": exprs(ba, 2, tm, sym), "init": exprs(ia, 1, tm), "final": exprs(fa, 1, tm),
            "level1": exprs(ba, 1, tm), "h2": exprs(["acc", "v"] + ([] if name != "CONST" else CONSTS)
                                                     + (["p"] if name == "LAGV" else [])
                                                     + (["q"] if name == "LAGACC" else [])
                                                     + (["i"] if name == "INDEX" else []), 2, tm, sym)}


# ---------------------------------------------------------------- T4 family_profile (copied logic)
LADDER = (20, 25, 30, 40, 60, 80, 100, 150, 200)
BASE_LENGTHS = (2, 3, 4, 5, 6, 7, 8, 9)
K_DISTINCT, MODE_MAX, SENS_MIN, COPY_MAX, ABSORB_MAX = 5, 0.5, 0.2, 0.9, 0.9


def _rand_list(rng, L):
    return [rng.randint(2, 30) for _ in range(L)]


def _extremes(L):
    return [[2] * L, [30] * L, [2 if i % 2 == 0 else 30 for i in range(L)],
            [30 if i % 2 == 0 else 2 for i in range(L)],
            [2 + (i % 29) for i in range(L)], [30 - (i % 29) for i in range(L)]]


def family_profile(witness) -> Dict:
    """tribunal_t4.family_profile, verbatim logic, on the extended evaluator. For a
    G4 witness this reproduces T4 exactly (checked in probes.py)."""
    key = tuple(witness)
    rng = random.Random("APHRODITE/T4/PROFILE/v1/" + repr(key))
    reasons, guard = [], 0

    def total_on(L, nrand):
        nonlocal guard
        probes = [(xs, m) for xs in _extremes(L) for m in (1, 2, 3, 41, 97)]
        probes += [(_rand_list(rng, L), rng.randint(1, 97)) for _ in range(nrand)]
        for xs, m in probes:
            out, g = run(witness, xs, m)
            guard += g
            if out is None or g:
                return False
        return True

    base_ok = all(total_on(L, 6) for L in BASE_LENGTHS)
    l_max = None
    if base_ok:
        for L in LADDER:
            if not total_on(L, 16):
                break
            l_max = L
    if not base_ok:
        reasons.append("NONE_OR_GUARD_ON_DEV_LENGTHS")
    elif l_max is None:
        reasons.append("DOMAIN_TOO_SHORT")
    outs, copies, mid_ch, last_ch = [], 0, 0, 0
    for _ in range(60):
        xs = _rand_list(rng, rng.randint(5, 9))
        m = rng.randint(3, 97)
        o, g = run(witness, xs, m)
        guard += g
        outs.append(o)
        copies += o is not None and (o in xs or o == m)
        i = len(xs) // 2
        ys = list(xs)
        ys[i] = rng.choice([u for u in range(2, 31) if u != xs[i]])
        mid_ch += run(witness, ys, m)[0] != o
        zs = list(xs)
        zs[-1] = rng.choice([u for u in range(2, 31) if u != xs[-1]])
        last_ch += run(witness, zs, m)[0] != o
    cnt = Counter(outs)
    distinct = len([o for o in cnt if o is not None])
    mode_share = cnt.most_common(1)[0][1] / len(outs)
    mid_s, last_s, copy_s = mid_ch / 60, last_ch / 60, copies / 60
    absorbed, n_abs = 0, 0
    La = min(30, l_max or 30)
    for _ in range(30):
        tr = []
        out, g = run(witness, _rand_list(rng, La), rng.randint(3, 97), trace=tr)
        if len(tr) > 6:
            n_abs += 1
            absorbed += len(set(tr[5:])) == 1
    absorb_s = absorbed / n_abs if n_abs else 0.0
    if None in cnt:
        reasons.append("NONE_ON_DEV_DISTRIBUTION")
    if distinct < K_DISTINCT or mode_share > MODE_MAX:
        reasons.append("CONSTANT_OR_NEAR_CONSTANT")
    if mid_s < SENS_MIN:
        reasons.append("MIDDLE_INSENSITIVE")
    if last_s < SENS_MIN:
        reasons.append("LAST_INSENSITIVE")
    if copy_s > COPY_MAX:
        reasons.append("COPIES_INPUT")
    if absorb_s >= ABSORB_MAX:
        reasons.append("FIXED_POINT_DYNAMICS")
    if guard:
        reasons.append("POW_GUARD_HIT")
    return {"L_max": l_max, "middle_sensitivity": round(mid_s, 3),
            "last_sensitivity": round(last_s, 3), "reasons": sorted(set(reasons)),
            "admissible": not reasons}


def perm_invariant(prog, n=25):
    """Old-tribunal permutation invariance (first element pinned)."""
    rng = random.Random(LABEL + "/perm")
    for _ in range(n):
        xs = [rng.randint(2, 30) for _ in range(rng.randint(5, 30))]
        m = rng.randint(3, 97)
        ys = [xs[0]] + sorted(xs[1:])
        if run(prog, xs, m)[0] != run(prog, ys, m)[0]:
            return False
    return True

"""S3 TRS -- ordered local sequence-rewrite rules.

A program is a list of rules  LHS -> RHS  over linear patterns of CONST/VAR
atoms, separated by RULESEP(1), with ARROW(0) inside each rule.  Execution
scans the working list left to right, applies the first matching rule, and
repeats to fixpoint or fuel exhaustion.

Validity is a genuinely partial structural predicate (arrow/separator shape,
LHS length and CONST requirement, RHS variable indices bound), so this basis
is the one where generic local edits can and do fall out of the language.
"""
from . import common
from .common import clampl, MAXVAL, MAXLEN, PROG_MAX

NAME = "S3"
ARROW = 0
RULESEP = 1
NPAY = 16
NKIND = 2
FUEL = 80
MAX_RULES = 6
MAX_LHS = 4
MAX_RHS = 5

_PERMK = list(range(NKIND))
_IPERMK = list(range(NKIND))
_PERMA = list(range(NPAY))
_IPERMA = list(range(NPAY))
_PARSE_CACHE = {}


def set_order(perm_kind, perm_pay):
    global _PERMK, _IPERMK, _PERMA, _IPERMA, _PARSE_CACHE
    _PERMK = list(perm_kind)
    _IPERMK = [0] * NKIND
    for i, v in enumerate(_PERMK):
        _IPERMK[v] = i
    _PERMA = list(perm_pay)
    _IPERMA = [0] * NPAY
    for i, v in enumerate(_PERMA):
        _IPERMA[v] = i
    _PARSE_CACHE = {}


def _atom_tok(kind, pay):
    return 2 + (_IPERMK[kind] + NKIND * _IPERMA[pay % NPAY])


def _untok(t):
    a = t - 2
    return _PERMK[a % NKIND], _PERMA[(a // NKIND) % NPAY]


def parse(prog):
    """-> list of (lhs_atoms, rhs_atoms) or None."""
    c = _PARSE_CACHE.get(prog)
    if c is not None:
        return c[0]
    res = _parse_raw(prog)
    if len(_PARSE_CACHE) < 200000:
        _PARSE_CACHE[prog] = (res,)
    return res


def _parse_raw(prog):
    if not isinstance(prog, tuple) or not (0 < len(prog) <= PROG_MAX):
        return None
    for t in prog:
        if t < 0 or t > MAXVAL:
            return None
    chunks = []
    cur = []
    for t in prog:
        if t == RULESEP:
            chunks.append(cur)
            cur = []
        else:
            cur.append(t)
    chunks.append(cur)
    if not (1 <= len(chunks) <= MAX_RULES):
        return None
    rules = []
    for ch in chunks:
        if ch.count(ARROW) != 1:
            return None
        k = ch.index(ARROW)
        lhs_t, rhs_t = ch[:k], ch[k + 1:]
        if not (1 <= len(lhs_t) <= MAX_LHS):
            return None
        if len(rhs_t) > MAX_RHS:
            return None
        lhs = [_untok(t) for t in lhs_t]
        rhs = [_untok(t) for t in rhs_t]
        nvars = sum(1 for kd, _ in lhs if kd == 1)
        if not any(kd == 0 for kd, _ in lhs):
            return None
        for kd, pay in rhs:
            if kd == 1 and pay >= nvars:
                return None
        rules.append((lhs, rhs, nvars))
    return rules


def is_valid(prog):
    return parse(prog) is not None


def run(prog, inp):
    common.METER["runs"] += 1
    rules = parse(prog)
    if rules is None:
        return None, "invalid"
    L = list(clampl(inp))
    fuel = FUEL
    while True:
        hit = None
        for pos in range(len(L)):
            for (lhs, rhs, nvars) in rules:
                m = len(lhs)
                if pos + m > len(L):
                    continue
                binds = []
                ok = True
                for j in range(m):
                    kd, pay = lhs[j]
                    v = L[pos + j]
                    if kd == 0:
                        if v % NPAY != pay:
                            ok = False
                            break
                    else:
                        binds.append(v)
                if ok:
                    hit = (pos, lhs, rhs, binds)
                    break
            if hit:
                break
        if not hit:
            return clampl(L), "ok"
        fuel -= 1
        if fuel < 0:
            return None, "timeout"
        pos, lhs, rhs, binds = hit
        out = []
        for kd, pay in rhs:
            out.append(pay if kd == 0 else binds[pay])
        L = L[:pos] + out + L[pos + len(lhs):]
        if len(L) > MAXLEN:
            L = L[:MAXLEN]


def random_program(rng, size_hint=10):
    toks = []
    nr = max(1, min(MAX_RULES, 1 + size_hint // 6))
    for r in range(nr):
        if r:
            toks.append(RULESEP)
        nl = rng.randrange(1, MAX_LHS + 1)
        lhs = []
        for _ in range(nl):
            lhs.append(rng.randrange(NKIND))
        if 0 not in lhs:
            lhs[rng.randrange(nl)] = 0
        nvars = sum(1 for k in lhs if k == 1)
        for k in lhs:
            toks.append(_atom_tok(k, rng.randrange(NPAY)))
        toks.append(ARROW)
        nrh = rng.randrange(0, MAX_RHS + 1)
        for _ in range(nrh):
            if nvars and rng.random() < 0.45:
                toks.append(_atom_tok(1, rng.randrange(nvars)))
            else:
                toks.append(_atom_tok(0, rng.randrange(NPAY)))
        if len(toks) > PROG_MAX - 2:
            break
    p = tuple(toks[:PROG_MAX])
    if is_valid(p):
        return p
    return (_atom_tok(0, 0), ARROW, _atom_tok(0, 1))


def random_tokens(rng, n):
    return tuple(rng.choice([ARROW, RULESEP] + [2 + i for i in range(NKIND * NPAY)])
                 for _ in range(n))

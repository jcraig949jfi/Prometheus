"""G2 PATHEDIT basis.

A transform is a Val describing positional edits of a term.

  T ::= E | (seq T T)
  E ::= (at P O) | (every C)
  P ::= root | (d0 P) | (d1 P) | (d2 P)
  O ::= (put C) | del | dup
  C ::= here | nilc | (qq S) | (L2 C C) | (L3 C C C) | (L4 C C C C)

`here` is the subterm at the edit site. `every C` rewrites every node bottom-up.
No recursion, no matching: the bias is positional.

The OBJECT language is still G1: artifacts are G1 terms, run by g1.run.
"""
from . import g1

NAME = "G2_PATHEDIT"
SYMS = g1.SYMS

C_TERMS = ["here", "nilc"] + [("qq", s) for s in SYMS]     # 20
O_TERMS = ["del", "dup"]                                    # 2
C_FORMS = ["L2", "L3", "L4"]                                # 3
P_FORMS = ["d0", "d1", "d2"]                                # 3
E_FORMS = ["at", "every"]
ORDER_DIMS = (len(C_TERMS), len(O_TERMS), len(C_FORMS), len(P_FORMS))

_IDX = {"d0": 0, "d1": 1, "d2": 2}

run = g1.run          # object level is unchanged


def size(t):
    if type(t) is str:
        return 1
    h = t[0]
    if h == "qq":
        return 1
    return 1 + sum(size(u) for u in t[1:])


class _E(Exception):
    def __init__(self, kind):
        self.kind = kind


def _build(c, here, ctr, limit):
    ctr[0] += 1
    if ctr[0] > limit:
        raise _E("budget")
    if type(c) is str:
        if c == "here":
            return here
        return ()                                  # nilc
    h = c[0]
    if h == "qq":
        return c[1]
    return tuple(_build(u, here, ctr, limit) for u in c[1:])


def _at(term, path, op, ctr, limit):
    ctr[0] += 1
    if ctr[0] > limit:
        raise _E("budget")
    if path == "root":
        if op == "del":
            raise _E("del_root")
        if op == "dup":
            raise _E("dup_root")
        return _build(op[1], term, ctr, limit)
    idx = _IDX[path[0]]
    if type(term) is not tuple or idx >= len(term):
        raise _E("nopath")
    rest = path[1]
    sub = term[idx]
    if rest == "root":
        if op == "del":
            return term[:idx] + term[idx + 1:]
        if op == "dup":
            return term[:idx + 1] + (sub,) + term[idx + 1:]
        return term[:idx] + (_build(op[1], sub, ctr, limit),) + term[idx + 1:]
    return term[:idx] + (_at(sub, rest, op, ctr, limit),) + term[idx + 1:]


def _every(term, c, ctr, limit):
    ctr[0] += 1
    if ctr[0] > limit:
        raise _E("budget")
    if type(term) is tuple:
        term = tuple(_every(u, c, ctr, limit) for u in term)
    return _build(c, term, ctr, limit)


def _exec(t, term, ctr, limit):
    ctr[0] += 1
    if ctr[0] > limit:
        raise _E("budget")
    h = t[0]
    if h == "seq":
        return _exec(t[2], _exec(t[1], term, ctr, limit), ctr, limit)
    if h == "at":
        return _at(term, t[1], t[2], ctr, limit)
    return _every(term, t[1], ctr, limit)          # every


def apply_transform(t, term, limit=2000, dmax=16):
    ctr = [0]
    try:
        v = _exec(t, term, ctr, limit)
    except _E as e:
        return ("err", e.kind)
    except RecursionError:
        return ("err", "hostdepth")
    if g1.valid_V(v):
        return ("ok", v)
    return ("invalid", v)


def _parts(n, k):
    """compositions of n into k positive parts"""
    if k == 1:
        yield (n,)
        return
    for i in range(1, n - k + 2):
        for rest in _parts(n - i, k - 1):
            yield (i,) + rest


class Enum:
    def __init__(self, cterm_perm=None, oterm_perm=None, cform_perm=None,
                 pform_perm=None, store_max=None):
        self.cterms = [C_TERMS[i] for i in (cterm_perm or range(len(C_TERMS)))]
        self.oterms = [O_TERMS[i] for i in (oterm_perm or range(len(O_TERMS)))]
        self.cforms = [C_FORMS[i] for i in (cform_perm or range(len(C_FORMS)))]
        self.pforms = [P_FORMS[i] for i in (pform_perm or range(len(P_FORMS)))]
        self.C = {1: list(self.cterms)}
        self.P = {1: ["root"]}
        self.O = {1: list(self.oterms)}
        self.E = {1: []}
        self.T = {1: []}
        self._built = 1

    def _ensure(self, n):
        while self._built < n:
            m = self._built + 1
            self.C[m] = list(self._genC(m))
            self.P[m] = [(f, p) for f in self.pforms for p in self.P[m - 1]]
            self.O[m] = [("put", c) for c in self.C[m - 1]]
            self.E[m] = list(self._genE(m))
            self.T[m] = list(self._genT(m))
            self._built = m

    def _genC(self, n):
        C = self.C
        for f in self.cforms:
            k = int(f[1])
            for comp in _parts(n - 1, k):
                if any(c not in C for c in comp):
                    continue
                for item in self._prod(C, comp, f):
                    yield item

    def _prod(self, table, comp, head):
        acc = [()]
        for c in comp:
            nxt = []
            for a in acc:
                for u in table[c]:
                    nxt.append(a + (u,))
            acc = nxt
        return [(head,) + a for a in acc]

    def _genE(self, n):
        for f in E_FORMS:
            if f == "at":
                for i in range(1, n - 1):
                    j = n - 1 - i
                    if i not in self.P or j not in self.O:
                        continue
                    for p in self.P[i]:
                        for o in self.O[j]:
                            yield ("at", p, o)
            else:
                if n - 1 in self.C:
                    for c in self.C[n - 1]:
                        yield ("every", c)

    def _genT(self, n):
        for e in self.E[n]:
            yield e
        for i in range(1, n - 1):
            j = n - 1 - i
            if i not in self.T or j not in self.T:
                continue
            for a in self.T[i]:
                for b in self.T[j]:
                    yield ("seq", a, b)

    def gen(self, n):
        self._ensure(n)
        return iter(self.T[n])

    def counts(self, nmax):
        self._ensure(nmax)
        return {n: len(self.T[n]) for n in range(1, nmax + 1)}

    def stream(self, nmax):
        r = 0
        for n in range(1, nmax + 1):
            for t in self.gen(n):
                yield r, t
                r += 1


def valid_C(c):
    if type(c) is str:
        return c in ("here", "nilc")
    if c[0] == "qq":
        return len(c) == 2 and c[1] in SYMS
    if c[0] in ("L2", "L3", "L4"):
        return len(c) == int(c[0][1]) + 1 and all(valid_C(u) for u in c[1:])
    return False


def valid_P(p):
    if type(p) is str:
        return p == "root"
    return len(p) == 2 and p[0] in _IDX and valid_P(p[1])


def valid_O(o):
    if type(o) is str:
        return o in ("del", "dup")
    return len(o) == 2 and o[0] == "put" and valid_C(o[1])


def valid_transform(t):
    if type(t) is not tuple or not t:
        return False
    if t[0] == "seq":
        return len(t) == 3 and valid_transform(t[1]) and valid_transform(t[2])
    if t[0] == "at":
        return len(t) == 3 and valid_P(t[1]) and valid_O(t[2])
    if t[0] == "every":
        return len(t) == 2 and valid_C(t[1])
    return False

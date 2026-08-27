"""G3 REWRITE basis.

A transform is an ordered rule list applied leftmost-outermost to a fixpoint.

  T ::= (r1 R) | (r2 R T)
  R ::= (rule P C)
  P ::= pv0 | pv1 | pany | nilp | (qp S) | (M2 P P) | (M3 P P P) | (M4 P P P P)
  C ::= v0  | v1  | nilc | (qq S) | (L2 C C) | (L3 C C C) | (L4 C C C C)

pv0/pv1 bind (consistently); pany matches without binding. A rewrite whose
replacement equals the matched subterm counts as no match, so trivial identity
loops terminate; growing loops hit the step budget. The bias is matching.

The OBJECT language is still G1: artifacts are G1 terms, run by g1.run.
"""
from . import g1

NAME = "G3_REWRITE"
SYMS = g1.SYMS

P_TERMS = ["pv0", "pv1", "pany", "nilp"] + [("qp", s) for s in SYMS]   # 22
C_TERMS = ["v0", "v1", "nilc"] + [("qq", s) for s in SYMS]             # 21
P_FORMS = ["M2", "M3", "M4"]
C_FORMS = ["L2", "L3", "L4"]
ORDER_DIMS = (len(P_TERMS), len(C_TERMS), len(P_FORMS), len(C_FORMS))

run = g1.run


def size(t):
    if type(t) is str:
        return 1
    if t[0] in ("qp", "qq"):
        return 1
    return 1 + sum(size(u) for u in t[1:])


class _E(Exception):
    def __init__(self, kind):
        self.kind = kind


def _match(pat, term, b):
    if type(pat) is str:
        if pat == "pany":
            return True
        if pat == "nilp":
            return term == ()
        k = 0 if pat == "pv0" else 1
        if k in b:
            return b[k] == term
        b[k] = term
        return True
    if pat[0] == "qp":
        return term == pat[1]
    k = int(pat[0][1])
    if type(term) is not tuple or len(term) != k:
        return False
    for i in range(k):
        if not _match(pat[i + 1], term[i], b):
            return False
    return True


def _inst(tpl, b, ctr, limit):
    ctr[0] += 1
    if ctr[0] > limit:
        raise _E("budget")
    if type(tpl) is str:
        if tpl == "nilc":
            return ()
        k = 0 if tpl == "v0" else 1
        if k not in b:
            raise _E("unbound")
        return b[k]
    if tpl[0] == "qq":
        return tpl[1]
    return tuple(_inst(u, b, ctr, limit) for u in tpl[1:])


def _rules(t):
    out = []
    while True:
        if t[0] == "r1":
            out.append(t[1])
            return out
        out.append(t[1])
        t = t[2]


def _step(term, rules, ctr, limit):
    """One leftmost-outermost rewrite. Returns (new_term, True) or (term, False)."""
    ctr[0] += 1
    if ctr[0] > limit:
        raise _E("budget")
    for r in rules:
        b = {}
        if _match(r[1], term, b):
            new = _inst(r[2], b, ctr, limit)
            if new != term:
                return new, True
    if type(term) is tuple:
        for i, u in enumerate(term):
            nu, hit = _step(u, rules, ctr, limit)
            if hit:
                return term[:i] + (nu,) + term[i + 1:], True
    return term, False


def apply_transform(t, term, limit=2000, dmax=16):
    ctr = [0]
    rules = _rules(t)
    try:
        cur = term
        for _ in range(64):
            cur, hit = _step(cur, rules, ctr, limit)
            if not hit:
                break
        else:
            return ("err", "fixpoint")
    except _E as e:
        return ("err", e.kind)
    except RecursionError:
        return ("err", "hostdepth")
    if g1.valid_V(cur):
        return ("ok", cur)
    return ("invalid", cur)


def _parts(n, k):
    if k == 1:
        yield (n,)
        return
    for i in range(1, n - k + 2):
        for rest in _parts(n - i, k - 1):
            yield (i,) + rest


class Enum:
    def __init__(self, pterm_perm=None, cterm_perm=None, pform_perm=None,
                 cform_perm=None):
        self.pterms = [P_TERMS[i] for i in (pterm_perm or range(len(P_TERMS)))]
        self.cterms = [C_TERMS[i] for i in (cterm_perm or range(len(C_TERMS)))]
        self.pforms = [P_FORMS[i] for i in (pform_perm or range(len(P_FORMS)))]
        self.cforms = [C_FORMS[i] for i in (cform_perm or range(len(C_FORMS)))]
        self.P = {1: list(self.pterms)}
        self.C = {1: list(self.cterms)}
        self.R = {}
        self.T = {}
        self._N = 0

    def _sub(self, table, forms, n):
        out = []
        for f in forms:
            k = int(f[1])
            for comp in _parts(n - 1, k):
                if any(c not in table for c in comp):
                    continue
                acc = [()]
                for c in comp:
                    acc = [a + (u,) for a in acc for u in table[c]]
                out.extend((f,) + a for a in acc)
        return out

    def _ensure(self, N):
        if N <= self._N:
            return
        for m in range(2, N - 1):                     # P, C up to N-2
            if m not in self.P:
                self.P[m] = self._sub(self.P, self.pforms, m)
                self.C[m] = self._sub(self.C, self.cforms, m)
        for m in range(3, N):                         # R up to N-1
            if m not in self.R:
                r = []
                for i in range(1, m - 1):
                    j = m - 1 - i
                    if i not in self.P or j not in self.C:
                        continue
                    for p in self.P[i]:
                        for c in self.C[j]:
                            r.append(("rule", p, c))
                self.R[m] = r
        for m in range(1, N + 1):                     # T up to N
            if m in self.T:
                continue
            t = []
            if m - 1 in self.R:
                t.extend(("r1", r) for r in self.R[m - 1])
            for i in range(1, m - 1):
                j = m - 1 - i
                if i in self.R and j in self.T:
                    for r in self.R[i]:
                        for u in self.T[j]:
                            t.append(("r2", r, u))
            self.T[m] = t
        self._N = N

    def gen(self, n):
        return iter(self.T.get(n, []))

    def counts(self, nmax):
        self._ensure(nmax)
        return {n: len(self.T.get(n, [])) for n in range(1, nmax + 1)}

    def stream(self, nmax):
        self._ensure(nmax)
        r = 0
        for n in range(1, nmax + 1):
            for t in self.gen(n):
                yield r, t
                r += 1


def valid_P(p):
    if type(p) is str:
        return p in ("pv0", "pv1", "pany", "nilp")
    if p[0] == "qp":
        return len(p) == 2 and p[1] in SYMS
    if p[0] in ("M2", "M3", "M4"):
        return len(p) == int(p[0][1]) + 1 and all(valid_P(u) for u in p[1:])
    return False


def valid_C(c):
    if type(c) is str:
        return c in ("v0", "v1", "nilc")
    if c[0] == "qq":
        return len(c) == 2 and c[1] in SYMS
    if c[0] in ("L2", "L3", "L4"):
        return len(c) == int(c[0][1]) + 1 and all(valid_C(u) for u in c[1:])
    return False


def valid_R(r):
    return type(r) is tuple and len(r) == 3 and r[0] == "rule" and valid_P(r[1]) and valid_C(r[2])


def valid_transform(t):
    if type(t) is not tuple or not t:
        return False
    if t[0] == "r1":
        return len(t) == 2 and valid_R(t[1])
    if t[0] == "r2":
        return len(t) == 3 and valid_R(t[1]) and valid_transform(t[2])
    return False

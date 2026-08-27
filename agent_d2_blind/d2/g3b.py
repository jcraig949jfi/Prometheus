"""G3B REWRITE-ONEPASS basis.

Identical grammar to G3. Only the rewrite strategy differs: a single pre-order
pass over the ORIGINAL positions, each position rewritten at most once and the
result never re-scanned.

Why this variant exists (disclosed multiplicity): a smoke test — run before any
census — showed that the fixpoint strategy declared for G3 diverges on every
non-shrinking rule, so a wrap-shaped rule is inexpressible there. Both variants
are censused and both are preserved. Neither was modified after its census.
"""
from . import g1, g3

NAME = "G3B_REWRITE_ONEPASS"
SYMS = g3.SYMS
P_TERMS = g3.P_TERMS
C_TERMS = g3.C_TERMS
P_FORMS = g3.P_FORMS
C_FORMS = g3.C_FORMS
ORDER_DIMS = g3.ORDER_DIMS
Enum = g3.Enum
size = g3.size
run = g1.run

_E = g3._E


def _pass(term, rules, ctr, limit):
    ctr[0] += 1
    if ctr[0] > limit:
        raise _E("budget")
    for r in rules:
        b = {}
        if g3._match(r[1], term, b):
            new = g3._inst(r[2], b, ctr, limit)
            if type(term) is tuple:
                # children of the ORIGINAL term are still visited, in place
                return new
            return new
    if type(term) is tuple:
        return tuple(_pass(u, rules, ctr, limit) for u in term)
    return term


def apply_transform(t, term, limit=2000, dmax=16):
    ctr = [0]
    rules = g3._rules(t)
    try:
        v = _pass(term, rules, ctr, limit)
    except _E as e:
        return ("err", e.kind)
    except RecursionError:
        return ("err", "hostdepth")
    if g1.valid_V(v):
        return ("ok", v)
    return ("invalid", v)


valid_transform = g3.valid_transform

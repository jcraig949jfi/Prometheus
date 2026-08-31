"""Executable transformation-family classifiers (human side only).

These implement PREREG-CENSUS section 4 and 5. They are used to ATTACK the
grammar (is a human mutation taxonomy privileged by the physics?). They are
never visible to any learner, never enter generation, selection, routing or
admission, and are recorded in a file separate from machine state.
"""
from .core import contains, count_occ, proper_subterm, skeleton, leaves, nodes

LEGACY = ("WRAP", "APPEND", "PRE", "ROUTE", "DELETE", "RELABEL", "DUP")
COND_HEAD = "if"          # the conditional head of the object language


def _pred(p, o):
    """Labels satisfied by a single (input term, output term) pair."""
    s = set()
    if contains(o, p) and o != p:
        s.add("WRAP")
    if type(p) is tuple and type(o) is tuple and len(o) > len(p):
        if o[:len(p)] == p:
            s.add("APPEND")
        if o[-len(p):] == p:
            s.add("PRE")
    if type(o) is tuple and o and o[0] == COND_HEAD and contains(o, p):
        s.add("ROUTE")
    if proper_subterm(o, p):
        s.add("DELETE")
    if skeleton(o) == skeleton(p) and o != p:
        s.add("RELABEL")
    if count_occ(o, p) >= 2:
        s.add("DUP")
    return s


def _pred2(p, o):
    """Secondary (residual-audit) labels. Only S1/S2/S7 and DUP2 are substantive."""
    s = set()
    if not contains(o, p):
        for u in _subs(p):
            if u != p and nodes(u) >= 2 and contains(o, u):
                s.add("S1_PARTIAL")
                break
    if sorted(leaves(o)) == sorted(leaves(p)) and o != p:
        s.add("S2_PERMUTE")
    for u in _subs(p):
        if u != p and count_occ(o, u) > count_occ(p, u):
            s.add("DUP2")
            break
    no, np_ = nodes(o), nodes(p)
    if no > np_:
        s.add("Z_GROW")
    elif no < np_:
        s.add("Z_SHRINK")
    else:
        s.add("Z_SAME")
    return s


def _subs(v):
    yield v
    if type(v) is tuple:
        for u in v:
            yield from _subs(u)


def labels(pairs, c=0.9):
    """pairs: list of (probe_term, output_term) with output a Val and != probe."""
    n = len(pairs)
    if n < 3:
        return set(), n
    cnt = {}
    for p, o in pairs:
        for lab in _pred(p, o):
            cnt[lab] = cnt.get(lab, 0) + 1
    out = {lab for lab, k in cnt.items() if k / n >= c}
    return out, n


def secondary(pairs, c=0.9):
    n = len(pairs)
    if n < 3:
        return set()
    cnt = {}
    for p, o in pairs:
        for lab in _pred2(p, o):
            cnt[lab] = cnt.get(lab, 0) + 1
    return {lab for lab, k in cnt.items() if k / n >= c}


def feature_collapse(pairs):
    """S7: output constant within each partition of probes by head symbol."""
    part = {}
    for p, o in pairs:
        k = p if type(p) is str else p[0]
        part.setdefault(k, []).append(o)
    big = [v for v in part.values() if len(v) >= 2]
    if not big:
        return False
    return all(all(o == v[0] for o in v) for v in big)


SUBSTANTIVE = ("S1_PARTIAL", "S2_PERMUTE", "DUP2", "S7_COLLAPSE")

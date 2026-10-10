"""TFS-1 simple library compressor: anti-unification of subterm pairs, scored by corpus size reduction.

Nothing here knows a task, family, target or arm. Input: a corpus of solved programs (terms, possibly calling library
entries) and the current library. Output: ranked CANDIDATE abstractions (bodies over holes h0, h1). Promotion is the
caller's decision (Library.promote_body); this module never registers anything.

1. refactor(program, lib): rewrite a program modulo the library -- every subterm matching an entry's EXPANSION becomes a
   call to that entry (deepest / largest entries first, then id). Lets expanded observations expose S_b(L_a(x)).
2. candidates: for every pair of non-leaf, non-lambda subterm occurrences with the same head symbol, compute the
   anti-unifier (Plotkin LGG generalised to binders):
     - identical subterms with no variable escaping the pattern stay;
     - a lambda-variable bound OUTSIDE the pattern always becomes a hole (bodies must be closed);
     - a differing pair becomes a hole; the same (left, right) pair reuses the same hole (multi-use holes);
     - a differing pair that mentions a variable bound INSIDE the pattern cannot be a first-order hole: the difference
       is lifted to the nearest enclosing pattern lambda, which becomes a FUNCTION-typed hole;
     - more than 2 distinct holes -> discarded.
   Kept: patterns with >= 2 application nodes (prim / library calls; a lambda is not an application). A pattern that is
   a single library call over atoms is an alias and is discarded (alias rule A2).
3. score: rewrite the corpus top-down (outermost-first, left-to-right, non-overlapping; arguments of a match are
   rewritten recursively) and count
       gain = sum(size before) - sum(size after) - size(pattern body)
   (simple count, not MDL). Keep gain > 0 and uses >= 2. Rank by (-gain, -uses, body size, canonical text).
"""
from typing import Dict, List, Optional, Sequence, Tuple

from . import core as C
from .library import Library, infer_hole_types

MAX_HOLES = 2
_LIFT = object()


class _TooMany(Exception):
    pass


def _is_leaf(t) -> bool:
    return t[0] in ("int", "var", "xs", "hole")


def n_apps(t) -> int:
    tag = t[0]
    if _is_leaf(t):
        return 0
    if tag == "lam":
        return n_apps(t[2])
    return 1 + sum(n_apps(a) for a in t[1:])


def occurrences(t, d: int = 0, out=None) -> List[Tuple[tuple, int]]:
    """(subterm, binders above it) for every non-leaf, non-lambda node."""
    out = [] if out is None else out
    tag = t[0]
    if _is_leaf(t):
        return out
    if tag == "lam":
        occurrences(t[2], d + t[1], out)
        return out
    out.append((t, d))
    for a in t[1:]:
        occurrences(a, d, out)
    return out


def antiunify(s, t, max_holes: int = MAX_HOLES):
    """Anti-unifier of two terms taken from contexts with arbitrary binders above them. Returns the pattern (holes
    numbered in pre-order of first creation) or None."""
    holes: Dict[Tuple, int] = {}

    def mkhole(a, b, d):
        if C.refs_range(a, 0, d) or C.refs_range(b, 0, d):
            return _LIFT
        a0 = C.shift(a, -d) if d else a
        b0 = C.shift(b, -d) if d else b
        key = (a0, b0)
        if key not in holes:
            if len(holes) >= max_holes:
                raise _TooMany
            holes[key] = len(holes)
        return ("hole", holes[key])

    def au(a, b, d):
        if a == b and not C.refs_range(a, d, 1 << 30):
            return a
        if a[0] == b[0] and not _is_leaf(a) and len(a) == len(b):
            if a[0] == "lam":
                if a[1] == b[1]:
                    r = au(a[2], b[2], d + a[1])
                    if r is not _LIFT:
                        return ("lam", a[1], r)
                return mkhole(a, b, d)
            args = []
            for x, y in zip(a[1:], b[1:]):
                r = au(x, y, d)
                if r is _LIFT:
                    return _LIFT
                args.append(r)
            return (a[0],) + tuple(args)
        return mkhole(a, b, d)

    try:
        p = au(s, t, 0)
    except _TooMany:
        return None
    if p is _LIFT or p[0] == "hole":
        return None
    return p


def match(p, t, d: int, binds: Dict[int, tuple]) -> bool:
    tag = p[0]
    if tag == "hole":
        if C.refs_range(t, 0, d):
            return False
        f = C.shift(t, -d) if d else t
        j = p[1]
        if j in binds:
            return binds[j] == f
        binds[j] = f
        return True
    if tag != t[0] or len(p) != len(t):
        return False
    if _is_leaf(p):
        return p == t
    if tag == "lam":
        return p[1] == t[1] and match(p[2], t[2], d + p[1], binds)
    for a, b in zip(p[1:], t[1:]):
        if not match(a, b, d, binds):
            return False
    return True


def rewrite(t, pattern, name: str, arity: int, counter: Optional[List[int]] = None):
    """Outermost-first rewrite of every match of `pattern` into (name, args...)."""
    if not _is_leaf(t) and t[0] != "lam":
        binds: Dict[int, tuple] = {}
        if match(pattern, t, 0, binds):
            if counter is not None:
                counter[0] += 1
            return (name,) + tuple(rewrite(binds[j], pattern, name, arity, counter) for j in range(arity))
    tag = t[0]
    if _is_leaf(t):
        return t
    if tag == "lam":
        return ("lam", t[1], rewrite(t[2], pattern, name, arity, counter))
    return (tag,) + tuple(rewrite(a, pattern, name, arity, counter) for a in t[1:])


def refactor(t, lib: Library):
    """Rewrite a program modulo the library: each entry's expansion pattern -> a call to the entry. Entries are tried
    deepest first, then larger expansion, then id (deterministic), each to a fixpoint-free single pass."""
    if lib is None or not len(lib):
        return t
    order = sorted(lib.entries.values(), key=lambda e: (-e.depth, -e.expansion_size, e.id))
    for e in order:
        if e.alias_of is not None:
            continue
        t = rewrite(t, e.exp_t, e.id, len(e.params))
    return t


def propose(corpus: Sequence, lib: Optional[Library] = None, max_candidates: int = 20,
            refactor_first: bool = True, min_uses: int = 2) -> List[Dict]:
    """Ranked candidate abstractions from a corpus of solved programs (trees or contract text)."""
    lib = lib if lib is not None else Library()
    progs = [C.parse(p) if isinstance(p, str) else p for p in corpus]
    if refactor_first:
        progs = [refactor(p, lib) for p in progs]
    occ = []
    for p in progs:
        occ += occurrences(p)
    by_head: Dict[str, List[Tuple[tuple, int]]] = {}
    for o in occ:
        by_head.setdefault(o[0][0], []).append(o)
    patterns = {}
    for head in sorted(by_head):
        lst = by_head[head]
        for i in range(len(lst)):
            for j in range(i + 1, len(lst)):
                p = antiunify(lst[i][0], lst[j][0])
                if p is None or n_apps(p) < 2:
                    continue
                if p[0].startswith("L_") and all(_is_leaf(a) for a in p[1:]):
                    continue                        # alias rule A2: a bare re-expression of an entry
                patterns.setdefault(C.to_str(p), p)
    before = sum(C.size(p) for p in progs)
    out = []
    for text in sorted(patterns):
        p = patterns[text]
        k = C.max_hole(p) + 1
        try:
            ht = infer_hole_types(p, lib, None)
            params = [ht[j] for j in range(k)]
            ret = C.type_of(p, 0, params, lib)
        except (C.TypeErr, KeyError):
            continue
        cnt = [0]
        new = [rewrite(q, p, "L_CANDIDATE", k, cnt) for q in progs]
        uses = cnt[0]
        if uses < min_uses:
            continue
        gain = before - sum(C.size(q) for q in new) - C.size(p)
        if gain <= 0:
            continue
        users = sum(1 for q in new if "L_CANDIDATE" in C.calls_in(q))
        out.append({"body": text, "body_t": p, "params": params, "ret": ret, "gain": gain, "uses": uses,
                    "programs_using": users, "body_size": C.size(p),
                    "deps": sorted(set(C.calls_in(p)))})
    out.sort(key=lambda c: (-c["gain"], -c["uses"], c["body_size"], c["body"]))
    return out[:max_candidates]

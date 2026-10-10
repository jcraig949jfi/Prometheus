"""Exhaustive typed enumerator over contract-v0 terms, used by the SMALL SEARCH null and the ORACLE known-positive.

Order: increasing ENUMERATION SIZE (interp_a.esize: lam binders are free, every other node counts 1), then a
fixed production order. The search returns the FIRST dev-consistent program. The search charge is 1 per top-level
candidate evaluated on dev (contract section 1).

Pruning. It is meant to remove only programs that are behaviourally equal to (or dominated by) a program that is
already enumerated. Every rule is listed in PRUNE_RULES and in FOUNDRY_DESIGN.md section 3:
    P1 commutative canonical order: add mul gcd eq and or need uid(arg1) <= uid(arg2);
    P2 identical arguments: sub div mod lt gt eq and or with arg1 == arg2 are pruned (a constant or the argument);
    P3 identity / absorbing literals: (add e 0) (sub e 0) (sub 0 e) (mul e 0) (mul e 1) (div e 1) (mod e 1)
       (pow e 0) (pow e 1) (take 0 l) (drop 0 l);
    P4 involutions: (neg (neg e)) (not (not e)) (rev (rev l));
    P5 ground constants: a variable-free Int/Bool subterm is evaluated; FAIL, or a value already produced by an
       earlier ground term in the same context, is pruned (observational equivalence on constants only, sound);
    P6 (if c a a), and `if` with a ground condition;
    P7 (map (lam v v) l) (identity map).
There is no semantic pruning of open terms. `app` is not enumerated, because (app (lam v B) e) equals B[v:=e],
which is enumerated.
"""
from typing import Dict, List, Optional, Tuple

import fastc
from interp_a import FAIL, Fail, INPUT_VAR

PRUNE_RULES = ["P1 commutative order", "P2 identical args", "P3 identity/absorbing literals", "P4 involutions",
               "P5 ground-constant OE", "P6 trivial if", "P7 identity map"]

LITERALS = (0, 1, 2, 3)
INT_BIN = ("add", "sub", "mul", "div", "mod", "gcd", "pow")
CMP = ("lt", "eq", "gt")
LIST_RED = ("len", "head", "last", "sum", "max", "min")
COMM = {"add", "mul", "gcd", "eq", "and", "or"}
IDENT_PRUNE = {"sub", "div", "mod", "lt", "gt", "eq", "and", "or"}
UNARY_VARS = ("x", "y", "a", "b")
BINARY_VARS = (("a", "b"), ("x", "y"), ("a", "x"), ("y", "b"))


class Node:
    __slots__ = ("ast", "fn", "ground", "uid", "head", "lit")

    def __init__(self, ast, fn, ground, uid, head=None, lit=None):
        self.ast, self.fn, self.ground, self.uid, self.head, self.lit = ast, fn, ground, uid, head, lit


def fresh1(ctx):
    for v in UNARY_VARS:
        if v not in ctx:
            return v
    return None


def fresh2(ctx):
    for a, b in BINARY_VARS:
        if a not in ctx and b not in ctx:
            return a, b
    return None


class Grammar:
    """extra: name -> (sig tuple of 'I', ret 'I'|'B', closed lambda term). These are the promoted/oracle
    primitives. Each is called as (name ARGS...) and has enumeration size 1 + args."""

    def __init__(self, extra: Optional[Dict[str, Tuple[Tuple[str, ...], str, tuple]]] = None,
                 literals=LITERALS, with_input=True, memo_max=7):
        self.memo_max = memo_max                      # levels above this size are regenerated, not stored (memory)
        self.with_input = with_input                  # False: no xs / list productions (mechanism-body tables)
        self.extra = dict(sorted((extra or {}).items()))
        self.extra_fun = {k: fastc.closed_fun(v[2]) for k, v in self.extra.items()}
        self.literals = literals
        self.memo: Dict[tuple, List[Node]] = {}
        self.seen_ground: Dict[tuple, tuple] = {}
        self.generated = 0

    # ------------------------------------------------------------ node makers
    def _mk(self, ast, fn, ground, head=None, lit=None):
        self.generated += 1
        return Node(ast, fn, ground, None, head, lit)

    def _ground_ok(self, T, ctx, node):
        if not node.ground:
            return True
        try:
            v = node.fn({})
        except (Fail, ZeroDivisionError):
            return False
        key = (ctx, T, type(v).__name__, v)
        prev = self.seen_ground.get(key)
        if prev is None:
            self.seen_ground[key] = node.ast
            return True
        return prev == node.ast

    def _prim(self, name, kids):
        ast = ("prim", name, tuple(k.ast for k in kids))
        if name in self.extra:
            fn = fastc.compile_promoted_call(self.extra_fun[name], [k.fn for k in kids])
        else:
            fn = fastc.compile_node(ast, [k.fn for k in kids])
        return self._mk(ast, fn, all(k.ground for k in kids), head=name)

    # ------------------------------------------------------------ memoised / lazy levels
    def _levelize(self, n, it):
        """Position-based uid (size, index): deterministic, so P1/P2/P6 stay consistent when a lazy level is
        regenerated."""
        for i, nd in enumerate(it):
            nd.uid = (n, i)
            yield nd

    def _level(self, T, n, ctx):
        if n <= self.memo_max:
            return list(self._levelize(n, self.produce(T, n, ctx)))
        return LazyLevel(self, T, n, ctx)

    def get(self, T, n, ctx):
        key = (T, n, ctx)
        got = self.memo.get(key)
        if got is None:
            for k in range(1, min(n, self.memo_max + 1)):  # fill smaller sizes first: P5 representatives minimal
                for T2 in ("I", "B", "L"):
                    if (T2, k, ctx) not in self.memo:
                        self.memo[(T2, k, ctx)] = self._level(T2, k, ctx)
            got = self._level(T, n, ctx)
            self.memo[key] = got
        return got

    def splits(self, n, parts):
        if parts == 1:
            if n >= 1:
                yield (n,)
            return
        for k in range(1, n - parts + 2):
            for rest in self.splits(n - k, parts - 1):
                yield (k,) + rest

    # ------------------------------------------------------------ productions
    def produce(self, T, n, ctx):
        if T == "I":
            yield from self._int(n, ctx)
        elif T == "B":
            yield from self._bool(n, ctx)
        elif T == "L":
            yield from self._list(n, ctx)
        elif T in ("F1", "P"):
            v = fresh1(ctx)
            if v is None:
                return
            inner = "I" if T == "F1" else "B"
            for b in self.get(inner, n, ctx + (v,)):
                if T == "F1" and b.ast == ("var", v):
                    lam_identity = True
                else:
                    lam_identity = False
                nd = self._mk(("lam", v, b.ast), fastc.compile_lam(v, b.fn), False, head="lam")
                nd.lit = "ID" if lam_identity else None
                yield nd
        elif T == "F2":
            vv = fresh2(ctx)
            if vv is None:
                return
            a, b_ = vv
            for b in self.get("I", n, ctx + (a, b_)):
                inner = fastc.compile_lam(b_, b.fn)

                def mk(env, a=a, inner=inner):
                    def g(v):
                        e = dict(env)
                        e[a] = v
                        return inner(e)
                    return g
                yield self._mk(("lam", a, ("lam", b_, b.ast)), mk, False, head="lam2")

    def _ok_bin(self, name, x, y):
        if name in COMM and x.uid > y.uid:
            return False
        if name in IDENT_PRUNE and x.uid == y.uid:
            return False
        xl, yl = x.lit, y.lit
        if name == "add" and (xl == 0 or yl == 0):
            return False
        if name == "sub" and (yl == 0 or xl == 0):
            return False
        if name == "mul" and (xl in (0, 1) or yl in (0, 1)):
            return False
        if name in ("div", "mod") and yl == 1:
            return False
        if name == "pow" and yl in (0, 1):
            return False
        return True

    def _emit(self, T, ctx, node):
        if node.ground and not self._ground_ok(T, ctx, node):
            return None
        return node

    def _int(self, n, ctx):
        if n == 1:
            for v in ctx:
                yield self._mk(("var", v), fastc.compile_node(("var", v), ()), False)
            for k in self.literals:
                nd = self._mk(("lit", k), fastc.compile_node(("lit", k), ()), True, lit=k)
                if self._emit("I", ctx, nd):
                    yield nd
            return
        # unary
        for a in self.get("I", n - 1, ctx):
            if a.head == "neg":
                continue
            nd = self._emit("I", ctx, self._prim("neg", [a]))
            if nd:
                yield nd
        for name in (LIST_RED if self.with_input else ()):
            for a in self.get("L", n - 1, ctx):
                yield self._prim(name, [a])
        for name, (sig, ret, _t) in self.extra.items():
            if sig == ("I",) and ret == "I":
                for a in self.get("I", n - 1, ctx):
                    nd = self._emit("I", ctx, self._prim(name, [a]))
                    if nd:
                        yield nd
        # binary
        bins = list(INT_BIN) + [nm for nm, (sig, ret, _t) in self.extra.items() if sig == ("I", "I") and ret == "I"]
        if n >= 3:
            for name in bins:
                for k1, k2 in self.splits(n - 1, 2):
                    L1, L2 = self.get("I", k1, ctx), self.get("I", k2, ctx)
                    for x in L1:
                        for y in L2:
                            if name in INT_BIN and not self._ok_bin(name, x, y):
                                continue
                            nd = self._emit("I", ctx, self._prim(name, [x, y]))
                            if nd:
                                yield nd
        if n >= 4:
            for k1, k2, k3 in self.splits(n - 1, 3):
                for c in self.get("B", k1, ctx):
                    if c.ground:
                        continue
                    for x in self.get("I", k2, ctx):
                        for y in self.get("I", k3, ctx):
                            if x.uid == y.uid:
                                continue
                            nd = self._emit("I", ctx, self._prim("if", [c, x, y]))
                            if nd:
                                yield nd
            for k1, k2, k3 in (self.splits(n - 1, 3) if self.with_input else ()):
                Fs = self.get("F2", k1, ctx)
                if not Fs:
                    continue
                for f in Fs:
                    for i in self.get("I", k2, ctx):
                        for l in self.get("L", k3, ctx):
                            yield self._prim("foldl", [f, i, l])

    def _bool(self, n, ctx):
        if n >= 2:
            for a in self.get("B", n - 1, ctx):
                if a.head == "not":
                    continue
                nd = self._emit("B", ctx, self._prim("not", [a]))
                if nd:
                    yield nd
            for name, (sig, ret, _t) in self.extra.items():
                if sig == ("I",) and ret == "B":
                    for a in self.get("I", n - 1, ctx):
                        nd = self._emit("B", ctx, self._prim(name, [a]))
                        if nd:
                            yield nd
        if n >= 3:
            for name in CMP:
                for k1, k2 in self.splits(n - 1, 2):
                    for x in self.get("I", k1, ctx):
                        for y in self.get("I", k2, ctx):
                            if not self._ok_bin(name, x, y):
                                continue
                            nd = self._emit("B", ctx, self._prim(name, [x, y]))
                            if nd:
                                yield nd
            for name in ("and", "or"):
                for k1, k2 in self.splits(n - 1, 2):
                    for x in self.get("B", k1, ctx):
                        for y in self.get("B", k2, ctx):
                            if not self._ok_bin(name, x, y):
                                continue
                            nd = self._emit("B", ctx, self._prim(name, [x, y]))
                            if nd:
                                yield nd

    def _list(self, n, ctx):
        if not self.with_input:
            return
        if n == 1:
            yield self._mk(("var", INPUT_VAR), fastc.compile_node(("var", INPUT_VAR), ()), False)
            return
        for a in self.get("L", n - 1, ctx):
            if a.head == "rev":
                continue
            yield self._prim("rev", [a])
        if n >= 3:
            for name in ("take", "drop"):
                for k1, k2 in self.splits(n - 1, 2):
                    for i in self.get("I", k1, ctx):
                        if i.lit == 0:
                            continue
                        for l in self.get("L", k2, ctx):
                            yield self._prim(name, [i, l])
            for k1, k2 in self.splits(n - 1, 2):
                for f in self.get("F1", k1, ctx):
                    if f.lit == "ID":
                        continue
                    for l in self.get("L", k2, ctx):
                        yield self._prim("map", [f, l])
            for k1, k2 in self.splits(n - 1, 2):
                for p in self.get("P", k1, ctx):
                    for l in self.get("L", k2, ctx):
                        yield self._prim("filter", [p, l])
        if n >= 4:
            for k1, k2, k3 in self.splits(n - 1, 3):
                Fs = self.get("F2", k1, ctx)
                for f in Fs:
                    for l1 in self.get("L", k2, ctx):
                        for l2 in self.get("L", k3, ctx):
                            yield self._prim("zipw", [f, l1, l2])
            for k1, k2, k3 in self.splits(n - 1, 3):
                Fs = self.get("F2", k1, ctx)
                for f in Fs:
                    for i in self.get("I", k2, ctx):
                        for l in self.get("L", k3, ctx):
                            yield self._prim("scanl", [f, i, l])

    # ------------------------------------------------------------ top-level search
    def iter_top(self, T, n, ctx=()):
        key = (T, n, ctx)
        if key in self.memo:
            yield from self.memo[key]
            return
        for k in range(1, min(n, self.memo_max + 1)):
            for T2 in ("I", "B", "L"):
                self.get(T2, k, ctx)
        buf = [] if n <= self.memo_max else None
        for nd in self._levelize(n, self.produce(T, n, ctx)):
            if buf is not None:
                buf.append(nd)
            yield nd
        if buf is not None:
            self.memo[key] = buf                      # only reached when the level was exhausted


class LazyLevel:
    """A level above memo_max: iterating it regenerates the level (same order, same uids)."""
    __slots__ = ("g", "T", "n", "ctx")

    def __init__(self, g, T, n, ctx):
        self.g, self.T, self.n, self.ctx = g, T, n, ctx

    def __iter__(self):
        return self.g._levelize(self.n, self.g.produce(self.T, self.n, self.ctx))

    def __bool__(self):
        return True


def _match(fn, dev):
    for xs, out in dev:
        try:
            v = fn({INPUT_VAR: xs})
        except (Fail, ZeroDivisionError, RecursionError, TypeError):
            return False
        if v != out or type(v) is not type(out):
            return False
    return True


def search(grammar: Grammar, T: str, dev, budget: int, max_size: int = 40, hindsight_test=None):
    """First dev-consistent program in enumeration order within `budget` candidates (contract protocol).
    Returns dict(found ast|None, charge, size_reached, complete_size).

    With hindsight_test (a list of test examples), the walk does not stop at the first dev-consistent program. It
    continues until some dev-consistent program is also correct on hindsight_test (N6-style, favourable to the
    null), or the budget runs out. Extra keys: hindsight_found, hindsight_charge, n_dev_consistent."""
    charge = 0
    complete = 0
    first, first_charge, first_n = None, None, None
    n_cons = 0

    def res(found_charge, size_reached, hfound=None, hcharge=None):
        r = {"found": first, "charge": first_charge if first is not None else found_charge,
             "size_reached": first_n if first is not None and hindsight_test is None else size_reached,
             "complete_size": complete}
        if hindsight_test is not None:
            r.update({"hindsight_found": hfound, "hindsight_charge": hcharge, "n_dev_consistent": n_cons,
                      "walk_charge": found_charge})
        return r

    for n in range(1, max_size + 1):
        it = grammar.iter_top(T, n)
        for nd in it:
            charge += 1
            if charge > budget:
                it.close()
                return res(budget, n)
            if _match(nd.fn, dev):
                n_cons += 1
                if first is None:
                    first, first_charge, first_n = nd.ast, charge, n
                if hindsight_test is None:
                    it.close()
                    return res(charge, n)
                if _match(nd.fn, hindsight_test):
                    it.close()
                    return res(charge, n, nd.ast, charge)
        complete = n
    return res(charge, max_size)


# ---------------------------------------------------------------- unpruned space counts (reporting only)
def count_space(T, n, ctx_n=0, extra_sig=None, _memo=None):
    """Number of well-typed terms of enumeration size n WITHOUT pruning. ctx_n = number of Int variables in
    scope (xs always in scope). extra_sig: list of (sig, ret) of extra primitives."""
    extra_sig = extra_sig or []
    memo = {} if _memo is None else _memo

    def c(T, n, k):
        key = (T, n, k)
        if key in memo:
            return memo[key]
        r = 0
        if n <= 0:
            memo[key] = 0
            return 0
        if T == "I":
            if n == 1:
                r = k + len(LITERALS)
            else:
                r += c("I", n - 1, k) + len(LIST_RED) * c("L", n - 1, k)
                r += sum(1 for s, rt in extra_sig if s == ("I",) and rt == "I") * c("I", n - 1, k)
                nb = len(INT_BIN) + sum(1 for s, rt in extra_sig if s == ("I", "I"))
                r += nb * sum(c("I", a, k) * c("I", n - 1 - a, k) for a in range(1, n - 1))
                for a in range(1, n - 2):
                    for b in range(1, n - 1 - a):
                        cc = n - 1 - a - b
                        r += c("B", a, k) * c("I", b, k) * c("I", cc, k)
                        r += c("F2", a, k) * c("I", b, k) * c("L", cc, k)
        elif T == "B":
            if n >= 2:
                r += c("B", n - 1, k) + sum(1 for s, rt in extra_sig if rt == "B") * c("I", n - 1, k)
                r += 3 * sum(c("I", a, k) * c("I", n - 1 - a, k) for a in range(1, n - 1))
                r += 2 * sum(c("B", a, k) * c("B", n - 1 - a, k) for a in range(1, n - 1))
        elif T == "L":
            if n == 1:
                r = 1
            else:
                r += c("L", n - 1, k)
                r += 2 * sum(c("I", a, k) * c("L", n - 1 - a, k) for a in range(1, n - 1))
                r += sum(c("F1", a, k) * c("L", n - 1 - a, k) for a in range(1, n - 1))
                r += sum(c("P", a, k) * c("L", n - 1 - a, k) for a in range(1, n - 1))
                for a in range(1, n - 2):
                    for b in range(1, n - 1 - a):
                        cc = n - 1 - a - b
                        r += c("F2", a, k) * c("L", b, k) * c("L", cc, k)
                        r += c("F2", a, k) * c("I", b, k) * c("L", cc, k)
        elif T == "F1":
            r = c("I", n, k + 1) if k < 4 else 0
        elif T == "P":
            r = c("B", n, k + 1) if k < 4 else 0
        elif T == "F2":
            r = c("I", n, k + 2) if k < 3 else 0
        memo[key] = r
        return r

    return c(T, n, ctx_n)

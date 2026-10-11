"""Reference interpreter A for the Beta-04 shared interface contract v0.

Written by the FOUNDRY lead from EXPERIMENT_PLAN.md section 1 only. It does not read or import tfs1/ (interpreter B).
This file is the REFERENCE: it is a plain tree walker, kept simple on purpose. The fast search evaluator
(fastc.py) is a separate implementation that is checked against this one.

AST (internal, tuples):
    ('lit', k)                   integer literal
    ('var', name)                variable (x y a b, and the task input xs)
    ('lam', name, body)          single-parameter lambda; the parameter is Int
    ('app', f, (arg, ...))       curried application, strict, left to right
    ('prim', name, (arg, ...))   primitive application (also promoted primitives, see PROMOTED below)

Contract choices that v0 leaves open (each one is documented in FOUNDRY_DESIGN.md section 2 and flagged):
    C1  An Int->Int->Int argument is the curried lambda (lam a (lam b BODY)). (app F A B) applies F to A, then
        the result to B.
    C2  The interpreter accepts any integer literal with |k| <= 10^18. The generator and the enumerators use
        only 0 1 2 3.
    C3  An ill-typed program is rejected by typecheck(). If one is evaluated anyway, a dynamic type error is FAIL.
        That includes a Bool where an Int is expected: Python's bool is not accepted as an int.
    C4  Execution units: +1 per primitive application, including the HOF primitive itself and every primitive
        executed inside its function argument. Literals, variables, lam and app cost 0. If a program FAILs, the
        units spent up to the FAIL are reported.
    C5  The ceiling check applies to every Int that a primitive produces, including sum/len and each element
        that scanl produces (map/zipw elements are already checked by the function body's own primitives).
    C6  There is no list-length guard. 16 is the input-distribution default. No primitive can lengthen a list,
        except scanl (+1).
    C7  `if` is strict: all three arguments are evaluated, so a FAIL in the branch not taken still FAILs.
    C8  Bool output is supported (lt/eq/gt/and/or/not), but the pilot generator emits only Int and List tasks.
"""
import math
import re
from typing import Any, Dict, List, Optional, Tuple

CEIL = 10 ** 18
VARS = ("x", "y", "a", "b")
INPUT_VAR = "xs"


class Fail(Exception):
    """Runtime FAIL. A FAIL anywhere makes the whole program output FAIL."""


FAIL = "FAIL"   # the program-level FAIL sentinel returned by run()


class TermError(ValueError):
    """Malformed term (parse error / unknown name)."""


# ---------------------------------------------------------------- primitive table
# name -> (arity, signature) ; signature types: I B L F1 (Int->Int) P (Int->Bool) F2 (Int->Int->Int)
PRIMS: Dict[str, Tuple[Tuple[str, ...], str]] = {
    "add": (("I", "I"), "I"), "sub": (("I", "I"), "I"), "mul": (("I", "I"), "I"),
    "div": (("I", "I"), "I"), "mod": (("I", "I"), "I"), "gcd": (("I", "I"), "I"),
    "pow": (("I", "I"), "I"), "neg": (("I",), "I"),
    "lt": (("I", "I"), "B"), "eq": (("I", "I"), "B"), "gt": (("I", "I"), "B"),
    "and": (("B", "B"), "B"), "or": (("B", "B"), "B"), "not": (("B",), "B"),
    "if": (("B", "I", "I"), "I"),
    "len": (("L",), "I"), "head": (("L",), "I"), "last": (("L",), "I"),
    "sum": (("L",), "I"), "max": (("L",), "I"), "min": (("L",), "I"),
    "rev": (("L",), "L"), "take": (("I", "L"), "L"), "drop": (("I", "L"), "L"),
    "map": (("F1", "L"), "L"), "filter": (("P", "L"), "L"), "foldl": (("F2", "I", "L"), "I"),
    "zipw": (("F2", "L", "L"), "L"), "scanl": (("F2", "I", "L"), "L"),
}

# ---------------------------------------------------------------- types
T_INT, T_BOOL, T_LIST = "Int", "Bool", "List"


def fn(a, r):
    return ("->", a, r)


SLOT_TYPES = {"I": T_INT, "B": T_BOOL, "L": T_LIST,
              "F1": fn(T_INT, T_INT), "P": fn(T_INT, T_BOOL), "F2": fn(T_INT, fn(T_INT, T_INT))}


def type_str(t) -> str:
    if isinstance(t, tuple):
        a = type_str(t[1])
        return "%s->%s" % (a, type_str(t[2]))
    return t


# ---------------------------------------------------------------- parse / print
_TOK = re.compile(r"\(|\)|[^\s()]+")


def parse(src: str):
    toks = _TOK.findall(src)
    pos = 0

    def expr():
        nonlocal pos
        if pos >= len(toks):
            raise TermError("unexpected end")
        t = toks[pos]
        pos += 1
        if t == "(":
            if pos >= len(toks):
                raise TermError("unexpected end")
            head = toks[pos]
            pos += 1
            items = []
            while pos < len(toks) and toks[pos] != ")":
                items.append(expr())
            if pos >= len(toks):
                raise TermError("missing )")
            pos += 1
            if head == "lam":
                if len(items) != 2 or items[0][0] != "var" or items[0][1] not in VARS:
                    raise TermError("lam needs (lam VAR BODY) with VAR in x y a b")
                return ("lam", items[0][1], items[1])
            if head == "app":
                if len(items) < 2:
                    raise TermError("app needs F and >=1 argument")
                return ("app", items[0], tuple(items[1:]))
            if head == "(" or head == ")":
                raise TermError("bad head")
            return ("prim", head, tuple(items))
        if t == ")":
            raise TermError("unexpected )")
        if re.fullmatch(r"-?\d+", t):
            k = int(t)
            if abs(k) > CEIL:
                raise TermError("literal beyond ceiling")
            return ("lit", k)
        return ("var", t)

    out = expr()
    if pos != len(toks):
        raise TermError("trailing tokens")
    return out


def show(t) -> str:
    """Canonical whitespace: single spaces, no space after '(' or before ')'."""
    k = t[0]
    if k == "lit":
        return str(t[1])
    if k == "var":
        return t[1]
    if k == "lam":
        return "(lam %s %s)" % (t[1], show(t[2]))
    if k == "app":
        return "(app %s %s)" % (show(t[1]), " ".join(show(a) for a in t[2]))
    return "(%s %s)" % (t[1], " ".join(show(a) for a in t[2])) if t[2] else "(%s)" % t[1]


def size(t) -> int:
    """Full node count: every node counts 1, including lam and app."""
    k = t[0]
    if k in ("lit", "var"):
        return 1
    if k == "lam":
        return 1 + size(t[2])
    if k == "app":
        return 1 + size(t[1]) + sum(size(a) for a in t[2])
    return 1 + sum(size(a) for a in t[2])


def esize(t) -> int:
    """ENUMERATION size: lam binders are free (forced by the argument type), app counts 1. This is the size that
    the foundry enumerators order by (FOUNDRY_DESIGN.md section 3)."""
    k = t[0]
    if k in ("lit", "var"):
        return 1
    if k == "lam":
        return esize(t[2])
    if k == "app":
        return 1 + esize(t[1]) + sum(esize(a) for a in t[2])
    return 1 + sum(esize(a) for a in t[2])


def free_vars(t, bound=()) -> set:
    k = t[0]
    if k == "lit":
        return set()
    if k == "var":
        return set() if t[1] in bound else {t[1]}
    if k == "lam":
        return free_vars(t[2], bound + (t[1],))
    if k == "app":
        s = free_vars(t[1], bound)
        for a in t[2]:
            s |= free_vars(a, bound)
        return s
    s = set()
    for a in t[2]:
        s |= free_vars(a, bound)
    return s


def subst(t, var, rep):
    """Capture-avoiding only in the trivial sense: the foundry substitutes only into first-order mechanism bodies
    (which contain no binders), so capture cannot arise. A binder of `var` stops the substitution."""
    k = t[0]
    if k == "lit":
        return t
    if k == "var":
        return rep if t[1] == var else t
    if k == "lam":
        if t[1] == var:
            return t
        if t[1] in free_vars(rep):
            raise TermError("substitution would capture %s" % t[1])
        return ("lam", t[1], subst(t[2], var, rep))
    if k == "app":
        return ("app", subst(t[1], var, rep), tuple(subst(a, var, rep) for a in t[2]))
    return ("prim", t[1], tuple(subst(a, var, rep) for a in t[2]))


# ---------------------------------------------------------------- typecheck
class TypeErr(ValueError):
    pass


def typecheck(t, env: Optional[Dict[str, Any]] = None, promoted: Optional[Dict[str, "Promoted"]] = None):
    """Return the type of t. env maps variable -> type; by default {xs: List}. Lambda parameters are Int."""
    env = {INPUT_VAR: T_LIST} if env is None else env
    promoted = promoted or {}
    k = t[0]
    if k == "lit":
        return T_INT
    if k == "var":
        if t[1] not in env:
            raise TypeErr("unbound variable %s" % t[1])
        return env[t[1]]
    if k == "lam":
        e2 = dict(env)
        e2[t[1]] = T_INT
        return fn(T_INT, typecheck(t[2], e2, promoted))
    if k == "app":
        ft = typecheck(t[1], env, promoted)
        for a in t[2]:
            at = typecheck(a, env, promoted)
            if not (isinstance(ft, tuple) and ft[1] == at):
                raise TypeErr("bad application")
            ft = ft[2]
        return ft
    name, args = t[1], t[2]
    if name in promoted:
        sig, ret = promoted[name].sig, promoted[name].ret
    elif name in PRIMS:
        sig, ret = PRIMS[name]
    else:
        raise TypeErr("unknown primitive %s" % name)
    if len(args) != len(sig):
        raise TypeErr("arity of %s" % name)
    for a, s in zip(args, sig):
        if typecheck(a, env, promoted) != SLOT_TYPES[s]:
            raise TypeErr("argument type of %s" % name)
    return SLOT_TYPES[ret]


# ---------------------------------------------------------------- runtime values
class Closure:
    __slots__ = ("var", "body", "env")

    def __init__(self, var, body, env):
        self.var, self.body, self.env = var, body, env


class Promoted:
    """A promoted (library) primitive: name -> closed lambda term. Billed both as 1 call (promoted ledger) and at
    full expansion (expanded ledger)."""

    def __init__(self, name: str, term, sig: Tuple[str, ...], ret: str):
        self.name, self.term, self.sig, self.ret = name, term, sig, ret


class Units:
    __slots__ = ("promoted", "expanded")

    def __init__(self):
        self.promoted = 0
        self.expanded = 0


def _int(v):
    if type(v) is not int:
        raise Fail("type: expected Int")
    return v


def _bool(v):
    if type(v) is not bool:
        raise Fail("type: expected Bool")
    return v


def _list(v):
    if type(v) is not list:
        raise Fail("type: expected List")
    return v


def _ceil(v: int) -> int:
    if v > CEIL or v < -CEIL:
        raise Fail("ceiling")
    return v


class Interp:
    def __init__(self, promoted: Optional[Dict[str, Promoted]] = None):
        self.promoted = promoted or {}
        self.units = Units()
        self._in_promoted = 0

    def _tick(self):
        self.units.expanded += 1
        if not self._in_promoted:
            self.units.promoted += 1

    def apply(self, f, arg):
        if not isinstance(f, Closure):
            raise Fail("type: apply non-function")
        _int(arg)
        e = dict(f.env)
        e[f.var] = arg
        return self.ev(f.body, e)

    def apply2(self, f, a, b):
        return self.apply(self.apply(f, a), b)

    def ev(self, t, env):
        k = t[0]
        if k == "lit":
            return t[1]
        if k == "var":
            if t[1] not in env:
                raise Fail("unbound")
            return env[t[1]]
        if k == "lam":
            return Closure(t[1], t[2], env)
        if k == "app":
            f = self.ev(t[1], env)
            args = [self.ev(a, env) for a in t[2]]
            for a in args:
                f = self.apply(f, a)
            return f
        name, args = t[1], t[2]
        if name in self.promoted:
            return self._promoted(self.promoted[name], args, env)
        if name not in PRIMS:
            raise Fail("unknown primitive")
        if len(args) != len(PRIMS[name][0]):
            raise Fail("arity")
        vals = [self.ev(a, env) for a in args]       # strict, left to right
        self._tick()
        return self._prim(name, vals)

    def _promoted(self, p: Promoted, args, env):
        vals = [self.ev(a, env) for a in args]
        self.units.promoted += 0 if self._in_promoted else 1
        self._in_promoted += 1
        try:
            f = self.ev(p.term, {})
            for v in vals:
                f = self.apply(f, v)
        finally:
            self._in_promoted -= 1
        if p.ret == "I":
            _ceil(_int(f))
        elif p.ret == "B":
            _bool(f)
        return f

    def _prim(self, n, v):
        if n == "add":
            return _ceil(_int(v[0]) + _int(v[1]))
        if n == "sub":
            return _ceil(_int(v[0]) - _int(v[1]))
        if n == "mul":
            return _ceil(_int(v[0]) * _int(v[1]))
        if n == "div":
            if _int(v[1]) == 0:
                raise Fail("div0")
            return _ceil(_int(v[0]) // v[1])
        if n == "mod":
            if _int(v[1]) == 0:
                raise Fail("mod0")
            return _ceil(_int(v[0]) % v[1])
        if n == "gcd":
            return _ceil(math.gcd(abs(_int(v[0])), abs(_int(v[1]))))
        if n == "pow":
            a, b = _int(v[0]), _int(v[1])
            if b < 0 or b > 32:
                return 0
            return _ceil(a ** b)
        if n == "neg":
            return _ceil(-_int(v[0]))
        if n == "lt":
            return _int(v[0]) < _int(v[1])
        if n == "eq":
            return _int(v[0]) == _int(v[1])
        if n == "gt":
            return _int(v[0]) > _int(v[1])
        if n == "and":
            return _bool(v[0]) and _bool(v[1])
        if n == "or":
            return _bool(v[0]) or _bool(v[1])
        if n == "not":
            return not _bool(v[0])
        if n == "if":
            c, a, b = _bool(v[0]), _int(v[1]), _int(v[2])
            return a if c else b
        if n == "len":
            return _ceil(len(_list(v[0])))
        if n == "head":
            xs = _list(v[0])
            if not xs:
                raise Fail("head empty")
            return xs[0]
        if n == "last":
            xs = _list(v[0])
            if not xs:
                raise Fail("last empty")
            return xs[-1]
        if n == "sum":
            return _ceil(sum(_list(v[0])))
        if n == "max":
            xs = _list(v[0])
            if not xs:
                raise Fail("max empty")
            return max(xs)
        if n == "min":
            xs = _list(v[0])
            if not xs:
                raise Fail("min empty")
            return min(xs)
        if n == "rev":
            return list(reversed(_list(v[0])))
        if n == "take":
            k, xs = _int(v[0]), _list(v[1])
            k = max(0, min(k, len(xs)))
            return xs[:k]
        if n == "drop":
            k, xs = _int(v[0]), _list(v[1])
            k = max(0, min(k, len(xs)))
            return xs[k:]
        if n == "map":
            f, xs = v[0], _list(v[1])
            return [_ceil(_int(self.apply(f, x))) for x in xs]
        if n == "filter":
            p, xs = v[0], _list(v[1])
            return [x for x in xs if _bool(self.apply(p, x))]
        if n == "foldl":
            g, acc, xs = v[0], _int(v[1]), _list(v[2])
            for x in xs:
                acc = _ceil(_int(self.apply2(g, acc, x)))
            return acc
        if n == "zipw":
            g, xs, ys = v[0], _list(v[1]), _list(v[2])
            return [_ceil(_int(self.apply2(g, a, b))) for a, b in zip(xs, ys)]
        if n == "scanl":
            g, acc, xs = v[0], _int(v[1]), _list(v[2])
            out = [acc]
            for x in xs:
                acc = _ceil(_int(self.apply2(g, acc, x)))
                out.append(acc)
            return out
        raise Fail("unknown primitive")


def run(term, xs: List[int], promoted: Optional[Dict[str, Promoted]] = None, with_units: bool = False):
    """Run a program on input list xs. Returns the value, or FAIL. With with_units, returns (value, Units)."""
    it = Interp(promoted)
    try:
        out = it.ev(term, {INPUT_VAR: list(xs)})
        if isinstance(out, Closure):
            out = FAIL                       # a program must produce a first-order value
    except Fail:
        out = FAIL
    except RecursionError:
        out = FAIL
    return (out, it.units) if with_units else out


def run_src(src: str, xs: List[int], **kw):
    return run(parse(src), xs, **kw)

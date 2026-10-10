"""Fast evaluator for the foundry's searches: compiles a term into nested Python closures.

This is a SECOND implementation of contract v0 semantics. It skips unit counting and most dynamic type checks,
because the enumerators only build well-typed terms. tests/test_interp.py checks that it agrees with interp_a on
random well-typed (term, input) pairs. Any search result that matters (a SOLVED verdict) is re-checked with
interpreter A (qualify.py).
"""
import math

from interp_a import CEIL, FAIL, Fail, INPUT_VAR

_C = CEIL
_N = -CEIL


def _ck(v):
    if v > _C or v < _N:
        raise Fail
    return v


def _pow(a, b):
    if b < 0 or b > 32:
        return 0
    return _ck(a ** b)


def _div(a, b):
    if b == 0:
        raise Fail
    return _ck(a // b)


def _mod(a, b):
    if b == 0:
        raise Fail
    return a % b


def _head(xs):
    if not xs:
        raise Fail
    return xs[0]


def _last(xs):
    if not xs:
        raise Fail
    return xs[-1]


def _max(xs):
    if not xs:
        raise Fail
    return max(xs)


def _min(xs):
    if not xs:
        raise Fail
    return min(xs)


def _clip(k, n):
    return 0 if k < 0 else (n if k > n else k)


BIN_INT = {
    "add": lambda a, b: _ck(a + b), "sub": lambda a, b: _ck(a - b), "mul": lambda a, b: _ck(a * b),
    "div": _div, "mod": _mod, "gcd": lambda a, b: math.gcd(abs(a), abs(b)), "pow": _pow,
    "lt": lambda a, b: a < b, "eq": lambda a, b: a == b, "gt": lambda a, b: a > b,
    "and": lambda a, b: a and b, "or": lambda a, b: a or b,
}
UN = {"neg": lambda a: _ck(-a), "not": lambda a: not a,
      "len": len, "head": _head, "last": _last, "sum": lambda xs: _ck(sum(xs)),
      "max": _max, "min": _min, "rev": lambda xs: xs[::-1]}


def compile_lam(var, bodyf):
    def mk(env):
        def g(v):
            e = dict(env)
            e[var] = v
            return bodyf(e)
        return g
    return mk


def compile_node(t, kids):
    """Compile node t given the compiled closures of its children (`kids`, aligned with t's subterms).
    For 'lam' kids = (bodyf,), for 'app' kids = (ff, argf...), for 'prim' kids = argfs.
    Promoted primitives are compiled by the caller (enum.Grammar) and passed as ('promoted', fn) heads."""
    k = t[0]
    if k == "lit":
        v = t[1]
        return lambda env: v
    if k == "var":
        name = t[1]
        return lambda env: env[name]
    if k == "lam":
        return compile_lam(t[1], kids[0])
    if k == "app":
        ff, afs = kids[0], kids[1:]

        def app(env):
            f = ff(env)
            vals = [a(env) for a in afs]
            for v in vals:
                f = f(v)
            return f
        return app
    name = t[1]
    if name in BIN_INT:
        op = BIN_INT[name]
        a, b = kids
        return lambda env: op(a(env), b(env))
    if name in UN:
        op = UN[name]
        a = kids[0]
        return lambda env: op(a(env))
    if name == "if":
        c, a, b = kids

        def iff(env):
            cv, av, bv = c(env), a(env), b(env)
            return av if cv else bv
        return iff
    if name == "take":
        n, l = kids

        def take(env):
            k_, xs = n(env), l(env)
            return xs[:_clip(k_, len(xs))]
        return take
    if name == "drop":
        n, l = kids

        def drop(env):
            k_, xs = n(env), l(env)
            return xs[_clip(k_, len(xs)):]
        return drop
    if name == "map":
        f, l = kids

        def mp(env):
            g, xs = f(env), l(env)
            return [g(x) for x in xs]
        return mp
    if name == "filter":
        f, l = kids

        def fl(env):
            g, xs = f(env), l(env)
            return [x for x in xs if g(x)]
        return fl
    if name == "foldl":
        f, i, l = kids

        def fo(env):
            g, acc, xs = f(env), i(env), l(env)
            for x in xs:
                acc = g(acc)(x)
            return acc
        return fo
    if name == "zipw":
        f, l1, l2 = kids

        def zw(env):
            g, xs, ys = f(env), l1(env), l2(env)
            return [g(a)(b) for a, b in zip(xs, ys)]
        return zw
    if name == "scanl":
        f, i, l = kids

        def sc(env):
            g, acc, xs = f(env), i(env), l(env)
            out = [acc]
            for x in xs:
                acc = g(acc)(x)
                out.append(acc)
            return out
        return sc
    raise ValueError("cannot compile %s" % name)


def compile_promoted_call(pfun, kids):
    """pfun: a compiled CLOSED curried function value (python callable chain)."""
    if len(kids) == 1:
        a = kids[0]
        return lambda env: pfun(a(env))
    a, b = kids
    return lambda env: pfun(a(env))(b(env))


def compile_term(t, promoted_funs=None):
    """Compile a whole term (recursive). promoted_funs: name -> python callable (curried)."""
    promoted_funs = promoted_funs or {}
    k = t[0]
    if k in ("lit", "var"):
        return compile_node(t, ())
    if k == "lam":
        return compile_node(t, (compile_term(t[2], promoted_funs),))
    if k == "app":
        return compile_node(t, tuple([compile_term(t[1], promoted_funs)] +
                                     [compile_term(a, promoted_funs) for a in t[2]]))
    kids = tuple(compile_term(a, promoted_funs) for a in t[2])
    if t[1] in promoted_funs:
        return compile_promoted_call(promoted_funs[t[1]], kids)
    return compile_node(t, kids)


def closed_fun(term, promoted_funs=None):
    """Compile a CLOSED lambda term to a python callable."""
    return compile_term(term, promoted_funs)({})


def runf(f, xs):
    """Run a compiled program on input xs -> value or FAIL."""
    try:
        return f({INPUT_VAR: xs})
    except (Fail, ZeroDivisionError, RecursionError):
        return FAIL

"""TFS-1 minimal core: types, terms, parser/printer, type checker and INTERPRETER B (contract v0).

Contract: roles/Aphrodite/beta04/EXPERIMENT_PLAN.md s1 (frozen shared interface contract v0). This module implements it
independently of the FOUNDRY lead's interpreter A (not read, not imported).

Internal term representation (nested tuples; de Bruijn indices, so alpha-equivalent terms are structurally equal):
    ('int', n)              integer literal
    ('var', i)              lambda-bound variable, de Bruijn index i (0 = innermost binder)
    ('xs',)                 the task input (List); global, visible everywhere (also inside library bodies)
    ('hole', j)             parameter j of a library-entry body (only inside entry bodies)
    ('lam', k, body)        k in {1, 2}; k = 2 is the curried (lam a (lam b BODY)); inside BODY, b = 0 and a = 1
    ('app', f, a1, ...)     application of a lambda (or function-typed hole) to Int arguments
    (name, a1, ...)         base primitive or library entry application (library names start with 'L_')

Canonical text (s-expressions, single spaces). Binder names are a deterministic function of the binder structure:
a unary binder takes the first of x, y, x1, y1, ... not already in scope; a binary binder takes the first free pair of
(a, b), (a1, b1), ... . With at most two nested unary binders and one binary binder only the contract names x, y, a, b
are used (see TFS1_DESIGN.md, OPEN DECISION D3).

Evaluation (exact; strict; left-to-right):
  - FAIL is an exception (Fail); a FAIL anywhere makes the whole program output FAIL (run() returns the FAIL sentinel).
  - Ceiling: every Int-valued primitive output with |v| > 10**18 is FAIL.
  - Execution units are counted in two ledgers at once:
        U[0]  EXPANDED ledger : 1 per base-primitive application actually executed, including those inside library
                                bodies (identical to evaluating the fully expanded program; tested);
        U[1]  PROMOTED ledger : 1 per base-primitive application written in the caller's own code, plus 1 per library
                                call made from the caller's own code; work inside a library body is not billed here
                                (except argument expressions and caller-written lambdas, which are caller code).
  - Library calls are evaluated by CALL-BY-NAME (argument thunks re-evaluated at each use). Because the language is
    pure, this is exactly evaluation by expansion (substitution), including FAIL behaviour and the expanded-unit count.
"""
from typing import Dict, List, Optional, Sequence, Tuple

CONTRACT = "beta04-contract-v0"
CEIL = 10 ** 18

INT, BOOL, LIST = "Int", "Bool", "List"
F_II, F_IB, F_III = "Int->Int", "Int->Bool", "Int->Int->Int"
VALUE_TYPES = (INT, BOOL, LIST)
FN_TYPES = (F_II, F_IB, F_III)
LAMBDA_TYPE = {(1, INT): F_II, (1, BOOL): F_IB, (2, INT): F_III}
FN_SHAPE = {F_II: (1, INT), F_IB: (1, BOOL), F_III: (2, INT)}

# name -> (argument types, result type). Semantics below; frozen by contract v0.
PRIM_SIGS: Dict[str, Tuple[Tuple[str, ...], str]] = {
    "add": ((INT, INT), INT), "sub": ((INT, INT), INT), "mul": ((INT, INT), INT),
    "div": ((INT, INT), INT), "mod": ((INT, INT), INT), "gcd": ((INT, INT), INT),
    "pow": ((INT, INT), INT), "neg": ((INT,), INT),
    "lt": ((INT, INT), BOOL), "eq": ((INT, INT), BOOL), "gt": ((INT, INT), BOOL),
    "and": ((BOOL, BOOL), BOOL), "or": ((BOOL, BOOL), BOOL), "not": ((BOOL,), BOOL),
    "if": ((BOOL, INT, INT), INT),
    "len": ((LIST,), INT), "head": ((LIST,), INT), "last": ((LIST,), INT),
    "sum": ((LIST,), INT), "max": ((LIST,), INT), "min": ((LIST,), INT),
    "rev": ((LIST,), LIST), "take": ((INT, LIST), LIST), "drop": ((INT, LIST), LIST),
    "map": ((F_II, LIST), LIST), "filter": ((F_IB, LIST), LIST),
    "foldl": ((F_III, INT, LIST), INT), "zipw": ((F_III, LIST, LIST), LIST),
    "scanl": ((F_III, INT, LIST), LIST),
}
# Strict + FAIL-absorbing => argument order is semantically irrelevant for these (used only by the enumerator's
# optional commutative canonicalisation).
COMMUTATIVE = frozenset({"add", "mul", "gcd", "eq", "and", "or"})
RESERVED = frozenset({"int", "var", "xs", "hole", "lam", "app"})
LITERALS = (0, 1, 2, 3)


class Fail(Exception):
    """The contract's FAIL."""


FAIL = "FAIL"           # sentinel returned by run() for a FAILed program
_FAIL_EXC = Fail()

# ================================================================ names / printing
UNARY_POOL = ["x", "y"] + ["%s%d" % (c, i) for i in range(1, 64) for c in "xy"]
BINARY_POOL = [("a", "b")] + [("a%d" % i, "b%d" % i) for i in range(1, 64)]


def bind_names(k: int, names: Tuple[str, ...]) -> Tuple[str, ...]:
    used = set(names)
    if k == 1:
        for n in UNARY_POOL:
            if n not in used:
                return (n,)
    else:
        for p in BINARY_POOL:
            if p[0] not in used and p[1] not in used:
                return p
    raise ValueError("binder name pool exhausted")


def to_str(t, names: Tuple[str, ...] = ()) -> str:
    tag = t[0]
    if tag == "int":
        return str(t[1])
    if tag == "var":
        return names[-1 - t[1]]
    if tag == "xs":
        return "xs"
    if tag == "hole":
        return "h%d" % t[1]
    if tag == "lam":
        bn = bind_names(t[1], names)
        body = to_str(t[2], names + bn)
        if t[1] == 1:
            return "(lam %s %s)" % (bn[0], body)
        return "(lam %s (lam %s %s))" % (bn[0], bn[1], body)
    if tag == "app":
        return "(app " + " ".join(to_str(a, names) for a in t[1:]) + ")"
    if len(t) == 1:
        return "(%s)" % tag
    return "(" + tag + " " + " ".join(to_str(a, names) for a in t[1:]) + ")"


# ================================================================ parsing
def _tokens(s: str) -> List[str]:
    return s.replace("(", " ( ").replace(")", " ) ").split()


def parse(s: str, names: Tuple[str, ...] = ()):
    """Contract s-expression -> term. `(lam a (lam b B))` and `(lam a b B)` both give the binary ('lam', 2, B).
    Names: lambda variables are looked up innermost-first (shadowing allowed); `xs`; `hN` = hole N; integers."""
    toks = _tokens(s)
    pos = [0]

    def atom(tok, scope):
        if tok == "xs":
            return ("xs",)
        if tok.lstrip("-").isdigit():
            return ("int", int(tok))
        for i in range(len(scope) - 1, -1, -1):
            if scope[i] == tok:
                return ("var", len(scope) - 1 - i)
        if tok[0] == "h" and tok[1:].isdigit():
            return ("hole", int(tok[1:]))
        raise ValueError("unbound name %r" % tok)

    def expr(scope):
        tok = toks[pos[0]]
        pos[0] += 1
        if tok != "(":
            if tok == ")":
                raise ValueError("unexpected )")
            return atom(tok, scope)
        head = toks[pos[0]]
        pos[0] += 1
        if head == "lam":
            n1 = toks[pos[0]]
            pos[0] += 1
            binders = [n1]
            if _is_name(toks[pos[0]]) and toks[pos[0] + 1] != ")":
                binders.append(toks[pos[0]])           # (lam a b BODY) sugar
                pos[0] += 1
            elif toks[pos[0]] == "(" and toks[pos[0] + 1] == "lam":
                # (lam a (lam b BODY)) -> binary
                pos[0] += 2
                n2 = toks[pos[0]]
                pos[0] += 1
                body = expr(tuple(scope) + (n1, n2))
                if toks[pos[0]] != ")":
                    raise ValueError("bad inner lam")
                pos[0] += 1
                if toks[pos[0]] != ")":
                    raise ValueError("bad outer lam")
                pos[0] += 1
                if body[0] == "lam":
                    raise ValueError("lambda nesting deeper than 2 is not a contract type")
                return ("lam", 2, body)
            body = expr(tuple(scope) + tuple(binders))
            if toks[pos[0]] != ")":
                raise ValueError("bad lam")
            pos[0] += 1
            if body[0] == "lam":
                raise ValueError("lambda nesting deeper than 2 is not a contract type")
            return ("lam", len(binders), body)
        args = []
        while toks[pos[0]] != ")":
            args.append(expr(scope))
        pos[0] += 1
        if head == "app":
            return ("app",) + tuple(args)
        if head in RESERVED or head.lstrip("-").isdigit():
            raise ValueError("bad operator %r" % head)
        return (head,) + tuple(args)

    t = expr(tuple(names))
    if pos[0] != len(toks):
        raise ValueError("trailing tokens in %r" % s)
    return t


def _is_name(tok: str) -> bool:
    return tok.isidentifier() and tok != "xs"


# ================================================================ structure helpers
def size(t) -> int:
    """Enumerator size: every primitive/library application node and every leaf counts 1; a lambda binder counts 0
    (function arguments are always lambdas, so the binder carries no choice)."""
    tag = t[0]
    if tag == "lam":
        return size(t[2])
    if tag in ("int", "var", "xs", "hole"):
        return 1
    if tag == "app":
        return 1 + sum(size(a) for a in t[1:])
    return 1 + sum(size(a) for a in t[1:])


def nodes(t) -> int:
    """Node count including lambda binders (reported only)."""
    tag = t[0]
    if tag == "lam":
        return 1 + nodes(t[2])
    if tag in ("int", "var", "xs", "hole"):
        return 1
    return 1 + sum(nodes(a) for a in t[1:])


def children(t):
    tag = t[0]
    if tag in ("int", "var", "xs", "hole"):
        return ()
    if tag == "lam":
        return (t[2],)
    return t[1:]


def calls_in(t) -> List[str]:
    """Library names referenced (with multiplicity, pre-order)."""
    out = []
    tag = t[0]
    if tag.startswith("L_"):
        out.append(tag)
    for c in children(t):
        out += calls_in(c)
    return out


def has_call(t) -> bool:
    if t[0].startswith("L_"):
        return True
    return any(has_call(c) for c in children(t))


def max_hole(t) -> int:
    if t[0] == "hole":
        return t[1]
    return max([-1] + [max_hole(c) for c in children(t)])


def holes_in(t) -> List[int]:
    if t[0] == "hole":
        return [t[1]]
    out = []
    for c in children(t):
        out += holes_in(c)
    return out


def free_var_min_escape(t, depth: int = 0) -> bool:
    """True iff t has a variable that escapes t (refers to a binder outside t)."""
    tag = t[0]
    if tag == "var":
        return t[1] >= depth
    if tag == "lam":
        return free_var_min_escape(t[2], depth + t[1])
    return any(free_var_min_escape(c, depth) for c in children(t))


def refs_range(t, lo: int, hi: int, depth: int = 0) -> bool:
    """True iff t contains a variable whose index, measured at t's root, lies in [lo, hi)."""
    tag = t[0]
    if tag == "var":
        j = t[1] - depth
        return lo <= j < hi
    if tag == "lam":
        return refs_range(t[2], lo, hi, depth + t[1])
    return any(refs_range(c, lo, hi, depth) for c in children(t))


def shift(t, by: int, cutoff: int = 0):
    """Add `by` to every variable index >= cutoff (free at t's root)."""
    tag = t[0]
    if tag == "var":
        return ("var", t[1] + by) if t[1] >= cutoff else t
    if tag in ("int", "xs", "hole"):
        return t
    if tag == "lam":
        return ("lam", t[1], shift(t[2], by, cutoff + t[1]))
    return (tag,) + tuple(shift(a, by, cutoff) for a in t[1:])


def subst_holes(body, args: Sequence, depth: int = 0):
    """Replace ('hole', j) in body by args[j] (args are terms in the CALLER context; shifted under body binders)."""
    tag = body[0]
    if tag == "hole":
        a = args[body[1]]
        return shift(a, depth) if depth else a
    if tag in ("int", "xs", "var"):
        return body
    if tag == "lam":
        return ("lam", body[1], subst_holes(body[2], args, depth + body[1]))
    return (tag,) + tuple(subst_holes(a, args, depth) for a in body[1:])


# ================================================================ type checking
class TypeErr(Exception):
    pass


def type_of(t, nvars: int = 0, holes: Optional[Sequence[str]] = None, lib=None) -> str:
    """Infer the type of t with nvars Int lambda variables in scope. holes: parameter types (entry bodies).
    lib: an object with .sig(name) -> (arg types, result type) for 'L_' names."""
    tag = t[0]
    if tag == "int":
        return INT
    if tag == "var":
        if t[1] >= nvars:
            raise TypeErr("unbound variable index %d" % t[1])
        return INT
    if tag == "xs":
        return LIST
    if tag == "hole":
        if holes is None or t[1] >= len(holes):
            raise TypeErr("hole h%d outside an entry body" % t[1])
        return holes[t[1]]
    if tag == "lam":
        bt = type_of(t[2], nvars + t[1], holes, lib)
        ft = LAMBDA_TYPE.get((t[1], bt))
        if ft is None:
            raise TypeErr("lambda of arity %d with %s body is not a contract type" % (t[1], bt))
        return ft
    if tag == "app":
        ft = type_of(t[1], nvars, holes, lib)
        if ft not in FN_SHAPE:
            raise TypeErr("app of non-function %s" % ft)
        k, rt = FN_SHAPE[ft]
        if len(t) - 2 != k:
            raise TypeErr("app arity")
        for a in t[2:]:
            if type_of(a, nvars, holes, lib) != INT:
                raise TypeErr("app argument must be Int")
        return rt
    if tag in PRIM_SIGS:
        ats, rt = PRIM_SIGS[tag]
    elif tag.startswith("L_") and lib is not None:
        ats, rt = lib.sig(tag)
    else:
        raise TypeErr("unknown operator %r" % tag)
    if len(t) - 1 != len(ats):
        raise TypeErr("%s expects %d args" % (tag, len(ats)))
    for a, at in zip(t[1:], ats):
        if at in FN_SHAPE and a[0] not in ("lam", "hole"):
            raise TypeErr("function argument of %s must be a lambda (or a function-typed hole)" % tag)
        got = type_of(a, nvars, holes, lib)
        if got != at:
            raise TypeErr("%s argument: expected %s got %s" % (tag, at, got))
    return rt


# ================================================================ interpreter B
U = [0, 0]          # [expanded units, promoted units]
D = [0]             # how many library bodies we are currently inside (0 = caller code)
XS = [None]         # the current task input
EMPTY = ()


def _bill():
    U[0] += 1
    if not D[0]:
        U[1] += 1


def _chk(r):
    if r > CEIL or r < -CEIL:
        raise _FAIL_EXC
    return r


def _mk_bin(op):
    if op == "add":
        def mk(a, b):
            def f(env):
                r = a(env) + b(env)
                U[0] += 1
                if not D[0]:
                    U[1] += 1
                if r > CEIL or r < -CEIL:
                    raise _FAIL_EXC
                return r
            return f
    elif op == "sub":
        def mk(a, b):
            def f(env):
                r = a(env) - b(env)
                U[0] += 1
                if not D[0]:
                    U[1] += 1
                if r > CEIL or r < -CEIL:
                    raise _FAIL_EXC
                return r
            return f
    elif op == "mul":
        def mk(a, b):
            def f(env):
                r = a(env) * b(env)
                U[0] += 1
                if not D[0]:
                    U[1] += 1
                if r > CEIL or r < -CEIL:
                    raise _FAIL_EXC
                return r
            return f
    elif op == "div":
        def mk(a, b):
            def f(env):
                x = a(env)
                y = b(env)
                U[0] += 1
                if not D[0]:
                    U[1] += 1
                if y == 0:
                    raise _FAIL_EXC
                r = x // y
                if r > CEIL or r < -CEIL:
                    raise _FAIL_EXC
                return r
            return f
    elif op == "mod":
        def mk(a, b):
            def f(env):
                x = a(env)
                y = b(env)
                U[0] += 1
                if not D[0]:
                    U[1] += 1
                if y == 0:
                    raise _FAIL_EXC
                return x % y
            return f
    elif op == "gcd":
        import math
        g = math.gcd

        def mk(a, b):
            def f(env):
                r = g(abs(a(env)), abs(b(env)))
                U[0] += 1
                if not D[0]:
                    U[1] += 1
                if r > CEIL:
                    raise _FAIL_EXC
                return r
            return f
    elif op == "pow":
        def mk(a, b):
            def f(env):
                x = a(env)
                y = b(env)
                U[0] += 1
                if not D[0]:
                    U[1] += 1
                if y < 0 or y > 32:
                    return 0
                r = x ** y
                if r > CEIL or r < -CEIL:
                    raise _FAIL_EXC
                return r
            return f
    elif op in ("lt", "eq", "gt", "and", "or"):
        import operator
        fn = {"lt": operator.lt, "eq": operator.eq, "gt": operator.gt,
              "and": lambda p, q: p and q, "or": lambda p, q: p or q}[op]

        def mk(a, b):
            def f(env):
                x = a(env)
                y = b(env)              # strict: both sides always evaluated
                U[0] += 1
                if not D[0]:
                    U[1] += 1
                return fn(x, y)
            return f
    elif op in ("take", "drop"):
        take = op == "take"

        def mk(a, b):
            def f(env):
                n = a(env)
                xs = b(env)
                U[0] += 1
                if not D[0]:
                    U[1] += 1
                L = len(xs)
                n = 0 if n < 0 else (L if n > L else n)
                return xs[:n] if take else xs[n:]
            return f
    else:
        raise KeyError(op)
    return mk


def _mk_un(op):
    if op == "neg":
        def f1(x):
            r = -x
            if r > CEIL or r < -CEIL:
                raise _FAIL_EXC
            return r
    elif op == "not":
        def f1(x):
            return not x
    elif op == "len":
        f1 = len
    elif op in ("head", "last", "max", "min"):
        idx = {"head": 0, "last": -1}.get(op)
        agg = {"max": max, "min": min}.get(op)

        def f1(xs):
            if not xs:
                raise _FAIL_EXC
            r = xs[idx] if agg is None else agg(xs)
            if r > CEIL or r < -CEIL:
                raise _FAIL_EXC
            return r
    elif op == "sum":
        def f1(xs):
            r = sum(xs)
            if r > CEIL or r < -CEIL:
                raise _FAIL_EXC
            return r
    elif op == "rev":
        def f1(xs):
            return xs[::-1]
    else:
        raise KeyError(op)

    def mk(a):
        def f(env):
            x = a(env)
            U[0] += 1
            if not D[0]:
                U[1] += 1
            return f1(x)
        return f
    return mk


def _mk_if(c, a, b):
    def f(env):
        p = c(env)
        x = a(env)
        y = b(env)          # strict: both branches evaluated (a FAIL in either is FAIL)
        U[0] += 1
        if not D[0]:
            U[1] += 1
        return x if p else y
    return f


def _mk_map(fc, lc):
    def f(env):
        fn = fc(env)
        xs = lc(env)
        U[0] += 1
        if not D[0]:
            U[1] += 1
        return [fn(v) for v in xs]
    return f


def _mk_filter(fc, lc):
    def f(env):
        fn = fc(env)
        xs = lc(env)
        U[0] += 1
        if not D[0]:
            U[1] += 1
        return [v for v in xs if fn(v)]
    return f


def _mk_foldl(fc, ic, lc):
    def f(env):
        fn = fc(env)
        acc = ic(env)
        xs = lc(env)
        U[0] += 1
        if not D[0]:
            U[1] += 1
        for v in xs:
            acc = fn(acc, v)
        if acc > CEIL or acc < -CEIL:
            raise _FAIL_EXC
        return acc
    return f


def _mk_scanl(fc, ic, lc):
    def f(env):
        fn = fc(env)
        acc = ic(env)
        xs = lc(env)
        U[0] += 1
        if not D[0]:
            U[1] += 1
        out = [acc]                 # Haskell convention: init included, length len(xs) + 1 (OPEN DECISION D1)
        for v in xs:
            acc = fn(acc, v)
            out.append(acc)
        return out
    return f


def _mk_zipw(fc, ac, bc):
    def f(env):
        fn = fc(env)
        xs = ac(env)
        ys = bc(env)
        U[0] += 1
        if not D[0]:
            U[1] += 1
        return [fn(p, q) for p, q in zip(xs, ys)]
    return f


_BIN = {op: _mk_bin(op) for op in ("add", "sub", "mul", "div", "mod", "gcd", "pow", "lt", "eq", "gt", "and", "or",
                                   "take", "drop")}
_UN = {op: _mk_un(op) for op in ("neg", "not", "len", "head", "last", "max", "min", "sum", "rev")}
_HO = {"map": _mk_map, "filter": _mk_filter, "foldl": _mk_foldl, "scanl": _mk_scanl, "zipw": _mk_zipw}


def _xs(env):
    return XS[0]


def compile_term(t, lib=None, cache: Optional[dict] = None, swap: bool = True):
    """Term -> closure env -> value. env is a tuple: lambda values at the END (de Bruijn index i -> env[-1-i]);
    inside a library body, argument thunks are at the START (hole j -> env[j]).
    cache: optional dict id(subterm) -> closure (callers must keep the subterms alive).
    swap: lambdas restore the caller's billing depth when invoked (needed only when library calls are present)."""
    if cache is not None:
        c = cache.get(id(t))
        if c is not None:
            return c
    tag = t[0]
    if tag == "int":
        v = t[1]

        def c(env, v=v):
            return v
    elif tag == "var":
        i = -1 - t[1]

        def c(env, i=i):
            return env[i]
    elif tag == "xs":
        c = _xs
    elif tag == "hole":
        j = t[1]

        def c(env, j=j):
            a, cenv, d = env[j]
            s = D[0]
            D[0] = d
            v = a(cenv)
            D[0] = s
            return v
    elif tag == "lam":
        body = compile_term(t[2], lib, cache, swap)
        if t[1] == 1:
            if swap:
                def c(env, body=body):
                    d = D[0]

                    def fn(v):
                        s = D[0]
                        D[0] = d
                        r = body(env + (v,))
                        D[0] = s
                        return r
                    return fn
            else:
                def c(env, body=body):
                    return lambda v: body(env + (v,))
        else:
            if swap:
                def c(env, body=body):
                    d = D[0]

                    def fn(p, q):
                        s = D[0]
                        D[0] = d
                        r = body(env + (p, q))
                        D[0] = s
                        return r
                    return fn
            else:
                def c(env, body=body):
                    return lambda p, q: body(env + (p, q))
    elif tag == "app":
        fc = compile_term(t[1], lib, cache, swap)
        acs = [compile_term(a, lib, cache, swap) for a in t[2:]]
        if len(acs) == 1:
            a0 = acs[0]

            def c(env, fc=fc, a0=a0):
                return fc(env)(a0(env))
        else:
            a0, a1 = acs

            def c(env, fc=fc, a0=a0, a1=a1):
                return fc(env)(a0(env), a1(env))
    elif tag in _BIN:
        c = _BIN[tag](compile_term(t[1], lib, cache, swap), compile_term(t[2], lib, cache, swap))
    elif tag in _UN:
        c = _UN[tag](compile_term(t[1], lib, cache, swap))
    elif tag == "if":
        c = _mk_if(*[compile_term(a, lib, cache, swap) for a in t[1:]])
    elif tag in _HO:
        c = _HO[tag](*[compile_term(a, lib, cache, swap) for a in t[1:]])
    elif tag.startswith("L_"):
        if lib is None:
            raise KeyError("library call %s without a library" % tag)
        body = lib.compiled_body(tag)
        acs = tuple(compile_term(a, lib, cache, swap) for a in t[1:])

        def c(env, body=body, acs=acs):
            d = D[0]
            if not d:
                U[1] += 1
            th = tuple((a, env, d) for a in acs)
            D[0] = d + 1
            r = body(th)
            D[0] = d
            return r
    else:
        raise KeyError("unknown operator %r" % tag)
    if cache is not None:
        cache[id(t)] = c
    return c


def run(fn, inp: List[int]):
    """Run a compiled program on one input. Returns the value or FAIL. Units accumulate in U (caller resets)."""
    XS[0] = inp
    D[0] = 0
    try:
        return fn(EMPTY)
    except Fail:
        return FAIL
    finally:
        D[0] = 0


def evaluate(t, inp: List[int], lib=None) -> Tuple[object, int, int]:
    """Convenience: (value or FAIL, expanded units, promoted units) for a single run."""
    fn = compile_term(t, lib, None, swap=has_call(t))
    U[0] = U[1] = 0
    v = run(fn, list(inp))
    return v, U[0], U[1]


def outputs(fn, inputs) -> list:
    return [run(fn, list(i)) for i in inputs]


def check_dev(fn, examples) -> bool:
    """True iff the program is correct on ALL examples (early exit at the first wrong / FAIL example)."""
    for inp, out in examples:
        XS[0] = inp
        D[0] = 0
        try:
            v = fn(EMPTY)
        except Fail:
            D[0] = 0
            return False
        if v != out or type(v) is not type(out):
            return False
    return True


def same_value(a, b) -> bool:
    return a == b and type(a) is type(b)

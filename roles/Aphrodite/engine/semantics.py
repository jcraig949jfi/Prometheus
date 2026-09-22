"""Deterministic semantic identity for the bounded Aphrodite DSL.

AMENDMENT 10 section 1, frozen at commit 169dc6c67 before this was written.

Source-string equality is no longer admissible as mechanism identity. Identity
here is PRIMARILY DENOTATIONAL: an expression's value vector over a frozen,
exhaustive probe battery covering the declared bounded input domain. AST
normalisation selects the canonical representative inside a class and gives a
readable name; it never decides identity on its own, because identities like
gcd(acc, v + acc) == gcd(acc, v) are number-theoretic and no rewrite rule in a
small table would catch them.

Original source strings are preserved for provenance.
"""
import ast
import math
from typing import Dict, List, Optional, Tuple

# The declared bounded input domain. Exhaustive over a small grid, which for
# these four variables is a complete denotational signature for the DSL's
# purposes: every primitive is a total function of (acc, v, first, last).
PROBE_ACC = (0, 1, 2, 3, 6, 12, 35, 210)
PROBE_V = (0, 1, 2, 5, 7, 12, 30, 97)
PROBE_FIRST = (1, 3, 8, 30)
PROBE_LAST = (1, 2, 7, 97)

PROBES: List[Dict[str, int]] = [
    {"acc": a, "v": v, "first": f, "last": l}
    for a in PROBE_ACC for v in PROBE_V for f in PROBE_FIRST for l in PROBE_LAST
]

CEIL = 10 ** 40
_G = {"__builtins__": {}, "math": math, "abs": abs}


def _pw(a, b):
    if b < 0 or b > 32:
        return 0
    return pow(a, b)


_G["pow"] = _pw
_CODE: Dict[str, object] = {}


def signature(expr: str) -> Tuple:
    """The denotational signature: the value vector over the probe battery.
    A value that errors or escapes the ceiling is recorded as None, so partial
    functions are distinguished by WHERE they are undefined."""
    code = _CODE.get(expr)
    if code is None:
        code = compile(expr, "<sem>", "eval")
        _CODE[expr] = code
    out = []
    for env in PROBES:
        try:
            val = eval(code, _G, dict(env))
            if val is None or abs(val) > CEIL:
                val = None
        except Exception:      # noqa: BLE001 -- undefined here is part of the signature
            val = None
        out.append(val)
    return tuple(out)


# ---------------------------------------------------------------- AST normalisation
COMMUTATIVE = {"add", "mul", "gcd"}
OPNAME = {ast.Add: "add", ast.Sub: "sub", ast.Mult: "mul",
          ast.FloorDiv: "fdiv", ast.Mod: "mod"}


def to_term(src: str):
    node = ast.parse(src.strip(), mode="eval").body

    def conv(n):
        if isinstance(n, ast.BinOp):
            return (OPNAME[type(n.op)], [conv(n.left), conv(n.right)])
        if isinstance(n, ast.Call):
            name = n.func.attr if isinstance(n.func, ast.Attribute) else n.func.id
            if name == "abs":
                return conv(n.args[0])              # canonical primitive names:
            if name in ("gcd",):                     # math.gcd(abs(a), abs(b))
                return ("gcd", [conv(a) for a in n.args])   # -> gcd(a, b)
            if name in ("pow", "_pw"):
                return ("powr", [conv(a) for a in n.args])
            return (name, [conv(a) for a in n.args])
        if isinstance(n, ast.Name):
            return ("var:" + n.id, [])
        if isinstance(n, ast.Constant):
            return ("const:%d" % n.value, [])
        raise ValueError("unsupported node %r" % type(n))

    return conv(node)


def term_str(t) -> str:
    op, args = t
    if op.startswith("var:"):
        return op[4:]
    if op.startswith("const:"):
        return op[6:]
    return "%s(%s)" % (op, ", ".join(term_str(a) for a in args))


def _const(t) -> Optional[int]:
    return int(t[0][6:]) if t[0].startswith("const:") else None


def normalise(t):
    """Algebraic simplification plus canonical ordering for commutative ops.
    Every rule below is general -- none names a particular observed example."""
    op, args = t
    args = [normalise(a) for a in args]
    if op in COMMUTATIVE:
        args = sorted(args, key=term_str)
    if op == "gcd" and len(args) == 2 and args[0] == args[1]:
        return args[0]                                    # gcd(x, x) = |x|
    if op == "add":
        if _const(args[0]) == 0:
            return args[1]
        if _const(args[1]) == 0:
            return args[0]
    if op == "mul":
        if _const(args[0]) == 1:
            return args[1]
        if _const(args[1]) == 1:
            return args[0]
        if _const(args[0]) == 0 or _const(args[1]) == 0:
            return ("const:0", [])
    if op == "sub" and args[0] == args[1]:
        return ("const:0", [])                            # x - x = 0
    if op == "mod" and args[0] == args[1]:
        return ("const:0", [])                            # x % x = 0
    if op == "fdiv" and args[0] == args[1]:
        return ("const:1", [])                            # x // x = 1 (x != 0)
    if op == "powr" and _const(args[1]) == 1:
        return args[0]
    if op == "powr" and _const(args[1]) == 0:
        return ("const:1", [])
    return (op, args)


def canonical_form(src: str) -> str:
    """A readable canonical NAME for the expression. Never used as identity."""
    return term_str(normalise(to_term(src)))


# ---------------------------------------------------------------- classes
class SemanticIndex:
    """Groups expressions into semantic classes and picks a representative:
    the shortest canonical form, ties broken lexicographically."""

    def __init__(self):
        self.by_sig: Dict[Tuple, List[str]] = {}

    def add(self, src: str) -> Tuple:
        sig = signature(src)
        self.by_sig.setdefault(sig, []).append(src)
        return sig

    def add_all(self, srcs):
        for s in srcs:
            self.add(s)
        return self

    def representative(self, sig: Tuple) -> str:
        """Shortest canonical form first, then the shortest SOURCE. Without the
        source-length term a baroque spelling whose canonical form happens to
        be short -- acc + gcd(v, v) canonicalises to add(acc, v) -- would be
        chosen over the plain one and would then be what the library carries."""
        members = self.by_sig[sig]
        return sorted(members,
                      key=lambda s: (len(canonical_form(s)), canonical_form(s),
                                     len(s), s))[0]

    def classes(self) -> List[Tuple]:
        return list(self.by_sig)

    def representatives(self) -> List[str]:
        return [self.representative(sig) for sig in self.by_sig]


def equivalent(a: str, b: str) -> bool:
    return signature(a) == signature(b)

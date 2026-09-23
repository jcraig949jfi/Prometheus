"""S1: whole-program identity for the bounded Aphrodite DSL.

Frozen by AMENDMENT_12_2026-09-23.md (commit 287d208ea) before this was
written.

The object is the WHOLE executable program plus its input convention:
('fold', init, body, final) or ('expr', final), TRAILING or PLAIN, exactly as
basis_v4.run_program executes it. Three identities are kept side by side:

    source_id     the exact evolved representation -- provenance only
    structure_id  canonical form under the SAFE rewrites R1-R4 -- genotype
    behavior_id   whole-program denotation over the frozen primary battery B1
                  under the declared domain D_NONNEG_v1 -- the mechanism

Behavior is computed by basis_v4.run_program itself, so this module contains
no second implementation of the DSL. It imports no catalog, witness, tribunal
or runner: nothing here knows any family or any target.

semantics.py (AMENDMENT 10) is deliberately untouched so Tiers 3B and 3C stay
reproducible; its canonical_form admits rewrites (x // x -> 1, x % x -> 0,
gcd(x, x) -> x) that are unsound under the declared semantics.
"""
import ast
import hashlib
import json
import random
from typing import Dict, List, Optional, Sequence, Tuple

import basis_v4 as G

DOMAIN = "D_NONNEG_v1"
C = 10 ** 40
TRAILING, PLAIN = "TRAILING", "PLAIN"
FAIL = "FAIL"


def _seed(label: str) -> int:
    return int(hashlib.sha256(label.encode()).hexdigest()[:16], 16)


def _sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"))
                          .encode()).hexdigest()


# ================================================================ terms
# A term is (op, [args]). Leaves are ("var:<name>", []) and ("const:<n>", []).
BINOPS = {ast.Add: "add", ast.Sub: "sub", ast.Mult: "mul",
          ast.FloorDiv: "fdiv", ast.Mod: "mod"}
COMMUTATIVE = ("add", "mul", "gcd")
INFIX = {"add": "+", "sub": "-", "mul": "*", "fdiv": "//", "mod": "%"}


def _is_abs(n) -> bool:
    return (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            and n.func.id == "abs" and len(n.args) == 1)


def parse(src: str):
    """Concrete DSL syntax -> term. R1 (canonical primitive names) happens here:
    math.gcd(abs(a), abs(b)) -> gcd(a, b) and pow(a, b) -> powr(a, b). An abs()
    anywhere else is KEPT as an abs node -- dropping it would be unsound."""
    def conv(n):
        if isinstance(n, ast.BinOp) and type(n.op) in BINOPS:
            return (BINOPS[type(n.op)], [conv(n.left), conv(n.right)])
        if isinstance(n, ast.Call):
            f = n.func
            if (isinstance(f, ast.Attribute) and f.attr == "gcd" and len(n.args) == 2
                    and all(_is_abs(a) for a in n.args)):
                return ("gcd", [conv(a.args[0]) for a in n.args])
            if isinstance(f, ast.Name) and f.id in ("pow", "_pw") and len(n.args) == 2:
                return ("powr", [conv(a) for a in n.args])
            if _is_abs(n):
                return ("abs", [conv(n.args[0])])
            raise ValueError("unsupported call in DSL source: %s" % ast.dump(n))
        if isinstance(n, ast.Name):
            return ("var:" + n.id, [])
        if isinstance(n, ast.Constant) and isinstance(n.value, int):
            return ("const:%d" % n.value, [])
        raise ValueError("unsupported node %r" % type(n).__name__)
    return conv(ast.parse(src.strip(), mode="eval").body)


def term_str(t) -> str:
    op, args = t
    if op.startswith("var:"):
        return op[4:]
    if op.startswith("const:"):
        return op[6:]
    return "%s(%s)" % (op, ", ".join(term_str(a) for a in args))


def to_src(t) -> str:
    """Term -> concrete DSL syntax that run_program and the emitted artifact
    both accept."""
    op, args = t
    if op.startswith("var:"):
        return op[4:]
    if op.startswith("const:"):
        return op[6:]
    if op in INFIX:
        return "(%s %s %s)" % (to_src(args[0]), INFIX[op], to_src(args[1]))
    if op == "gcd":
        return "math.gcd(abs(%s), abs(%s))" % (to_src(args[0]), to_src(args[1]))
    if op == "powr":
        return "pow(%s, %s)" % (to_src(args[0]), to_src(args[1]))
    if op == "abs":
        return "abs(%s)" % to_src(args[0])
    raise ValueError(op)


def nodes(t) -> int:
    return 1 + sum(nodes(a) for a in t[1])


def _const(t) -> Optional[int]:
    return int(t[0][6:]) if t[0].startswith("const:") else None


def total(t) -> bool:
    """TOTAL = cannot fail under the declared semantics: contains no fdiv and
    no mod (the only primitives with a failure mode; powr is guarded)."""
    return t[0] not in ("fdiv", "mod") and all(total(a) for a in t[1])


ZERO, ONE = ("const:0", []), ("const:1", [])


def normalise(t):
    """R2-R4 of AMENDMENT 12 s3, bottom-up. Every rule is stated over
    variables, preserves value and failure disposition on every input, and
    none moves an operation across the accumulator."""
    op, args = t
    if not args:
        return t
    args = [normalise(a) for a in args]
    if op in COMMUTATIVE:                                         # R2
        args = sorted(args, key=term_str)
    a0 = args[0]
    a1 = args[1] if len(args) > 1 else None
    # R3 neutral elements (x is still evaluated, so failures are preserved)
    if op == "add" and _const(a0) == 0:
        return a1
    if op == "add" and _const(a1) == 0:
        return a0
    if op == "mul" and _const(a0) == 1:
        return a1
    if op == "mul" and _const(a1) == 1:
        return a0
    if op in ("sub", ) and _const(a1) == 0:
        return a0
    if op in ("fdiv", "powr") and _const(a1) == 1:
        return a0
    # R4 absorbing / cancelling, ONLY when the discarded operand is TOTAL
    if op == "mul" and _const(a0) == 0 and total(a1):
        return ZERO
    if op == "mul" and _const(a1) == 0 and total(a0):
        return ZERO
    if op == "sub" and a0 == a1 and total(a0):
        return ZERO
    if op == "mod" and _const(a1) == 1 and total(a0):
        return ZERO
    if op == "powr" and _const(a1) == 0 and total(a0):
        return ONE
    return (op, args)


# ================================================================ programs
def _norm_prog(prog) -> Tuple:
    prog = tuple(prog)
    if prog[0] not in ("fold", "expr") or len(prog) != (4 if prog[0] == "fold" else 2):
        raise ValueError("not a DSL program: %r" % (prog,))
    return prog


def convention(trailing: bool) -> str:
    return TRAILING if trailing else PLAIN


def structural_form(prog) -> Tuple:
    prog = _norm_prog(prog)
    return (prog[0],) + tuple(term_str(normalise(parse(s))) for s in prog[1:])


def structural_program(prog) -> Tuple:
    """The structural form re-emitted as executable source -- used by the gate
    to check that every rewrite preserved behaviour (G-S1.4)."""
    prog = _norm_prog(prog)
    return (prog[0],) + tuple(to_src(normalise(parse(s))) for s in prog[1:])


def source_id(prog, trailing: bool) -> str:
    return _sha({"convention": convention(trailing), "source": list(_norm_prog(prog))})


def structure_id(prog, trailing: bool) -> str:
    return _sha({"convention": convention(trailing),
                 "structure": list(structural_form(prog))})


def program_nodes(prog) -> int:
    return sum(nodes(parse(s)) for s in _norm_prog(prog)[1:])


# ================================================================ batteries
CEILING_BAND = [C - 97, C - 30, C - 2, C - 1, C, C + 1, C // 2, C // 2 + 1,
                10 ** 20, 10 ** 20 + 1, 10 ** 13, 3 * 10 ** 13]


def _dedupe(inputs: List[List[int]]) -> List[List[int]]:
    seen, out = set(), []
    for x in inputs:
        k = tuple(x)
        if k not in seen:
            seen.add(k)
            out.append(list(x))
    return out


def build_b1() -> List[List[int]]:
    """PRIMARY battery, AMENDMENT 12 s4 (a)-(d). Each input is the full prompt
    integer list: the sequence followed by the query parameter."""
    rng = random.Random(_seed("APHRODITE/S1/B1/v1"))
    vals = [0, 1, 2, 3, 5, 7, 12, 30, 97]
    qs = [0, 1, 2, 3, 7, 32, 33, 97]
    out: List[List[int]] = []
    # (a) small-value grid
    for L in (1, 2, 3, 4, 6):
        seqs = [[0] * L, [1] * L,
                [0] + [rng.choice(vals) for _ in range(L - 1)],
                [rng.choice(vals) for _ in range(L - 1)] + [0]]
        seqs += [[rng.choice(vals) for _ in range(L)] for _ in range(6)]
        for s in seqs:
            for q in qs:
                out.append(s + [q])
    # (b) exponent-guard band
    for g in (31, 32, 33, 34):
        for base in (0, 1, 2, 3):
            out += [[base, g, g], [g, base, base], [base, base, base, g]]
    # (c) ceiling band
    partners = [0, 1, 2, 7]
    for cb in CEILING_BAND:
        p = rng.choice(partners)
        for s in ([cb], [cb, p], [p, cb], [cb, cb], [p, cb, p]):
            for q in (1, 2, 7, 97):
                out.append(s + [q])
    # (d) length band
    for L in (9, 20, 60):
        for _ in range(4):
            out.append([rng.randint(0, 30) for _ in range(L)] + [rng.randint(0, 97)])
    out.append([29] * 200 + [7])
    return _dedupe(out)


def _b2_value(rng: random.Random) -> int:
    r = rng.random()
    if r < 0.50:
        return rng.randint(0, 40)
    if r < 0.65:
        return rng.randint(0, 10 ** 6)
    if r < 0.75:
        return max(0, C + rng.randint(-200, 200))
    if r < 0.85:
        return max(0, C // rng.randint(2, 5) + rng.randint(-50, 50))
    if r < 0.90:
        return 10 ** 20 + rng.randint(-50, 50)
    return rng.randint(28, 36)


def build_b2(n: int = 5000) -> List[List[int]]:
    """AUDIT battery: independent seed, never contributes to an identity."""
    rng = random.Random(_seed("APHRODITE/S1/B2/v1"))
    out = []
    for _ in range(n):
        L = 1
        while L < 60 and rng.random() > 1 / 8:
            L += 1
        out.append([_b2_value(rng) for _ in range(L)] + [_b2_value(rng)])
    return out


def build_b1_neg() -> List[List[int]]:
    """SENSITIVITY only: B1 with signs drawn at random. Never an identity."""
    rng = random.Random(_seed("APHRODITE/S1/B1NEG/v1"))
    return [[x if rng.random() < 0.5 else -x for x in inp] for inp in build_b1()]


B1 = build_b1()
B1_SHA = _sha(B1)
_B2: Optional[List[List[int]]] = None
_B1N: Optional[List[List[int]]] = None


def b2() -> List[List[int]]:
    global _B2
    if _B2 is None:
        _B2 = build_b2()
    return _B2


def b1_neg() -> List[List[int]]:
    global _B1N
    if _B1N is None:
        _B1N = build_b1_neg()
    return _B1N


# ================================================================ behaviour
def _admissible(inp: Sequence[int], trailing: bool) -> bool:
    """Domain D: the fold sequence has length >= 1."""
    return len(inp) >= (2 if trailing else 1)


def values(prog, trailing: bool, battery: Sequence[Sequence[int]]) -> Tuple:
    """The program's value on every admissible battery input, by the SAME
    evaluator the search uses. None (failure or ceiling) is the token FAIL."""
    prog = _norm_prog(prog)
    out = []
    for inp in battery:
        if not _admissible(inp, trailing):
            continue
        got = G.run_program(prog, list(inp), trailing)
        out.append(FAIL if got is None else str(got))
    return tuple(out)


def behavior_id(prog, trailing: bool) -> str:
    return _sha({"domain": DOMAIN, "convention": convention(trailing),
                 "battery": B1_SHA, "values": list(values(prog, trailing, B1))})


def audit_id(prog, trailing: bool) -> str:
    """Denotation over the AUDIT battery. Never an identity; used by the gate
    to detect a B1 merge that B2 separates."""
    return _sha({"domain": DOMAIN, "convention": convention(trailing),
                 "audit": list(values(prog, trailing, b2()))})


def identify(prog, trailing: bool = True) -> Dict:
    """The full identity record. Source and structural form are PRESERVED even
    when programs share a behavior_id: genotype and phenotype are separate
    evidence."""
    prog = _norm_prog(prog)
    return {"convention": convention(trailing), "domain": DOMAIN,
            "source": list(prog), "source_id": source_id(prog, trailing),
            "structure": list(structural_form(prog)),
            "structure_id": structure_id(prog, trailing),
            "behavior_id": behavior_id(prog, trailing), "battery_sha256": B1_SHA}


def same_behavior(a, b, trailing: bool = True) -> bool:
    return behavior_id(a, trailing) == behavior_id(b, trailing)


def representative(members: Sequence, trailing: bool = True) -> Tuple:
    """DISPLAY ONLY (AMENDMENT 12 s6): fewest nodes, then structural form, then
    source. Not evidence of which factorisation is 'the' mechanism."""
    return min((_norm_prog(m) for m in members),
               key=lambda p: (program_nodes(p), json.dumps(structural_form(p)),
                              json.dumps(list(p))))


class BehaviorIndex:
    """Groups whole programs by behavior_id; every member keeps its own record."""

    def __init__(self, trailing: bool = True):
        self.trailing = trailing
        self.records: Dict[str, List[Dict]] = {}

    def add(self, prog) -> str:
        rec = identify(prog, self.trailing)
        self.records.setdefault(rec["behavior_id"], []).append(rec)
        return rec["behavior_id"]

    def classes(self) -> List[str]:
        return list(self.records)

    def members(self, bid: str) -> List[Tuple]:
        return [tuple(r["source"]) for r in self.records[bid]]

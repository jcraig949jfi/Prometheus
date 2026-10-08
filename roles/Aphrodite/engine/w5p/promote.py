"""W5P: bounded representation promotion (Beta-03 E3).

A certified one-hole body schema S (selected by a donor) becomes a PROMOTED PRIMITIVE

    P(x) := S[{H} := x]          (unary, evaluated in the current fold environment acc, v, first, last)

P is written in promoted-form DSL strings as a single node `P_<12 hex>(x)`. Its identity is content-addressed:
id = "P_" + sha256(canonical({grammar, schema, deps}))[:12], so the same schema promoted by two arms gets the same id
and nothing about the arm enters the record.

Evaluation contract (PROMOTION_SEMANTICS): a program containing promoted nodes evaluates EXACTLY as its expansion into
the original DSL. The engine never sees a promoted node: every library entry stores EXPANDED base-DSL bodies, so
basis_v4.run_program, accel/fasteval, a18.fast_cost, walk.iter_hits and the T4 tribunal run unchanged. The promoted
form is kept beside the expansion and is used only for (a) derivation (LGG treats P as one node, so depth is not
consumed by the abstraction) and (b) the W5P instantiation rule (depth counted with P as one node). An independent
call-by-value evaluator (run_program_direct) exists only to TEST the contract.

Nothing in this module knows a family, a target, a catalog or an arm.
"""
import ast
import hashlib
import json
import re
from typing import Dict, Iterable, List, Optional, Tuple

from . import _paths  # noqa: F401
import basis_v4 as G
import identity as I

GRAMMAR = "w5p-v1"
HOLE = "{H}"
HOLEVAR = "HOLEVAR_W5P"
NAME_RE = re.compile(r"\bP_[0-9a-f]{12}\b")
_NAME_FULL = re.compile(r"^P_[0-9a-f]{12}$")
MAX_DEPTH = 3                 # W5's body depth bound, counted with a promoted node as ONE node
CEIL = G.CEIL                 # basis_v4 fold-interpreter ceiling (10**40); engine.VALUE_CEILING (10**18) is not
#                               used by fold programs


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def sha(obj) -> str:
    return hashlib.sha256(canon(obj)).hexdigest()


def has_promoted(src: str) -> bool:
    return NAME_RE.search(src) is not None


# ================================================================ terms (identity.py terms + two node kinds)
# ("prim:P_xxx", [arg])  a promoted node;  ("hole", [])  the schema hole
def _is_abs(n) -> bool:
    return (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            and n.func.id == "abs" and len(n.args) == 1)


def parse(src: str):
    """identity.parse extended with promoted calls P_xxx(arg) and the {H} hole. On base-DSL strings it returns
    exactly identity.parse(src) (tested)."""
    s = src.strip().replace(HOLE, HOLEVAR)

    def conv(n):
        if isinstance(n, ast.BinOp) and type(n.op) in I.BINOPS:
            return (I.BINOPS[type(n.op)], [conv(n.left), conv(n.right)])
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name) and _NAME_FULL.match(f.id) and len(n.args) == 1 and not n.keywords:
                return ("prim:" + f.id, [conv(n.args[0])])
            if (isinstance(f, ast.Attribute) and f.attr == "gcd" and len(n.args) == 2
                    and all(_is_abs(a) for a in n.args)):
                return ("gcd", [conv(a.args[0]) for a in n.args])
            if isinstance(f, ast.Name) and f.id in ("pow", "_pw") and len(n.args) == 2:
                return ("powr", [conv(a) for a in n.args])
            if _is_abs(n):
                return ("abs", [conv(n.args[0])])
            raise ValueError("unsupported call in W5P source: %s" % ast.dump(n))
        if isinstance(n, ast.Name):
            if n.id == HOLEVAR:
                return ("hole", [])
            return ("var:" + n.id, [])
        if isinstance(n, ast.Constant) and isinstance(n.value, int):
            return ("const:%d" % n.value, [])
        raise ValueError("unsupported node %r" % type(n).__name__)
    return conv(ast.parse(s, mode="eval").body)


def is_prim(t) -> bool:
    return t[0].startswith("prim:")


def is_hole(t) -> bool:
    return t[0] == "hole" or t[0].startswith("hole:")


def is_atom(t) -> bool:
    return t[0].startswith("var:") or t[0].startswith("const:")


def to_src(t) -> str:
    """Term -> promoted-form source. Base terms emit exactly identity.to_src; holes emit {H}."""
    op, args = t
    if is_hole(t):
        return HOLE
    if op.startswith("var:"):
        return op[4:]
    if op.startswith("const:"):
        return op[6:]
    if op.startswith("prim:"):
        return "%s(%s)" % (op[5:], to_src(args[0]))
    if op in I.INFIX:
        return "(%s %s %s)" % (to_src(args[0]), I.INFIX[op], to_src(args[1]))
    if op == "gcd":
        return "math.gcd(abs(%s), abs(%s))" % (to_src(args[0]), to_src(args[1]))
    if op == "powr":
        return "pow(%s, %s)" % (to_src(args[0]), to_src(args[1]))
    if op == "abs":
        return "abs(%s)" % to_src(args[0])
    raise ValueError(op)


def prims_in(t) -> List[str]:
    out = [t[0][5:]] if is_prim(t) else []
    for a in t[1]:
        out += prims_in(a)
    return out


def holes_in(t) -> int:
    return (1 if is_hole(t) else 0) + sum(holes_in(a) for a in t[1])


def depth(t) -> int:
    """Node depth: leaves 0, every operator node (base or promoted) 1 + max child."""
    return 0 if not t[1] else 1 + max(depth(a) for a in t[1])


def nodes(t) -> int:
    return 1 + sum(nodes(a) for a in t[1])


def subst_hole(t, x):
    if is_hole(t):
        return x
    if not t[1]:
        return t
    return (t[0], [subst_hole(a, x) for a in t[1]])


# ---------------------------------------------------------------- normalisation (identity R2-R4, prim-aware)
def total(t, reg) -> bool:
    """identity.total, except a promoted node is total iff its EXPANSION is total (and its argument is). Without this
    the R4 absorbing rules would be unsound around a promoted node that hides an fdiv/mod."""
    if is_prim(t):
        return reg[t[0][5:]].total and all(total(a, reg) for a in t[1])
    return t[0] not in ("fdiv", "mod") and all(total(a, reg) for a in t[1])


def normalise(t, reg=None):
    """identity.normalise, verbatim rules, with total() made promotion-aware. Promoted nodes are opaque unary nodes
    (no rule rewrites them). On base terms it returns exactly identity.normalise(t) (tested)."""
    reg = reg or {}
    op, args = t
    if not args:
        return t
    args = [normalise(a, reg) for a in args]
    if op in I.COMMUTATIVE:
        args = sorted(args, key=I.term_str)
    a0 = args[0]
    a1 = args[1] if len(args) > 1 else None
    c0, c1 = I._const(a0), (I._const(a1) if a1 is not None else None)
    if op == "add" and c0 == 0:
        return a1
    if op == "add" and c1 == 0:
        return a0
    if op == "mul" and c0 == 1:
        return a1
    if op == "mul" and c1 == 1:
        return a0
    if op in ("sub", ) and c1 == 0:
        return a0
    if op in ("fdiv", "powr") and c1 == 1:
        return a0
    if op == "mul" and c0 == 0 and total(a1, reg):
        return I.ZERO
    if op == "mul" and c1 == 0 and total(a0, reg):
        return I.ZERO
    if op == "sub" and a0 == a1 and total(a0, reg):
        return I.ZERO
    if op == "mod" and c1 == 1 and total(a0, reg):
        return I.ZERO
    if op == "powr" and c1 == 0 and total(a0, reg):
        return I.ONE
    return (op, args)


# ================================================================ the promoted primitive
class Promoted:
    """P(x) := schema[{H} := x]. Immutable record; see to_json for the serialized fields."""

    FIELDS = ("grammar", "id", "schema", "expansion", "deps", "lineage", "depth", "contract",
              "source_artifact_sha256", "source_kind")

    def __init__(self, rec: Dict):
        self.rec = dict(rec)
        for k in self.FIELDS:
            setattr(self, k, self.rec[k])
        self.total = self.contract["total"]
        self.hash = self.rec.get("hash") or sha({k: self.rec[k] for k in self.FIELDS})

    # ---- construction
    @staticmethod
    def make_id(schema: str, deps: List[str]) -> str:
        return "P_" + sha({"grammar": GRAMMAR, "schema": schema, "deps": sorted(deps)})[:12]

    @classmethod
    def from_schema(cls, schema: str, reg: Dict[str, "Promoted"], source_artifact_sha256: str,
                    source_kind: str = "selected_entry") -> "Promoted":
        """Promote a one-hole schema (promoted-form; it may use earlier promoted primitives held in reg)."""
        t = parse(schema)
        if holes_in(t) != 1:
            raise ValueError("promotion needs exactly one hole: %r" % schema)
        if is_hole(t):
            raise ValueError("root hole is not a schema: %r" % schema)
        deps = sorted(set(prims_in(t)))
        missing = [d for d in deps if d not in reg]
        if missing:
            raise KeyError("unknown dependencies %s" % missing)
        canon_schema = to_src(t)
        base = expand_term(t, reg)
        expansion = to_src(base)
        lineage = sorted(set(deps) | {x for d in deps for x in reg[d].lineage})
        dep_depth = max((reg[d].depth for d in deps), default=0)
        tot = total(subst_hole(base, ("var:v", [])), {})
        rec = {"grammar": GRAMMAR, "id": cls.make_id(canon_schema, deps), "schema": canon_schema,
               "expansion": expansion, "deps": deps, "lineage": lineage, "depth": 1 + dep_depth,
               "contract": {
                   "arity": 1,
                   "argument": "one int-valued W5P body expression over {acc, v, first, last} (base or promoted)",
                   "result": "int, or FAIL (run_program returns None for the whole program)",
                   "environment": ["acc", "v", "first", "last"],
                   "semantics": "P(x) == expansion[{H} := x]; call-by-value; the argument occurs exactly once in "
                                "the expansion, so call-by-value and textual expansion coincide",
                   "guards": {"pow": "pow(a, b) = 0 if b < 0 or b > 32 (basis_v4._pw)",
                              "fdiv_mod_by_zero": "FAIL (exception -> run_program None)",
                              "ceiling": "FAIL if |acc| > 10**40 after any body step or |output| > 10**40 "
                                         "(basis_v4.CEIL); intermediate values are not checked, as in run_program"},
                   "total": bool(tot),
                   "expansion_nodes": nodes(base) - 1,
                   "admissible_in": "fold BODY only (init/final stay base DSL)"},
               "source_artifact_sha256": source_artifact_sha256, "source_kind": source_kind}
        return cls(rec)

    # ---- serialization
    def to_json(self) -> Dict:
        out = {k: self.rec[k] for k in self.FIELDS}
        out["hash"] = sha(out)
        return out

    def dumps(self) -> str:
        return canon(self.to_json()).decode()

    @classmethod
    def from_json(cls, rec: Dict, reg: Dict[str, "Promoted"]) -> "Promoted":
        """Load and VERIFY: hash, content id, dependency presence, and that the expansion re-derives exactly."""
        body = {k: rec[k] for k in cls.FIELDS}
        if rec.get("hash") != sha(body):
            raise ValueError("promoted record hash mismatch for %s" % rec.get("id"))
        p = cls.from_schema(rec["schema"], reg, rec["source_artifact_sha256"], rec["source_kind"])
        if p.to_json() != dict(body, hash=rec["hash"]):
            raise ValueError("promoted record does not re-derive: %s" % rec.get("id"))
        return p

    def pattern(self, reg):
        """Normalised promoted-form schema term (hole kept) -- used by recognition."""
        return normalise(parse(self.schema), reg)


# ================================================================ registry helpers
def register(reg: Dict[str, Promoted], p: Promoted) -> Promoted:
    if p.id in reg:
        if reg[p.id].schema != p.schema:
            raise ValueError("id collision %s" % p.id)
        return reg[p.id]
    reg[p.id] = p
    _DIRECT.pop(id(reg), None)
    return p


def load_records(recs: Iterable[Dict], reg: Optional[Dict[str, Promoted]] = None) -> Dict[str, Promoted]:
    """Load serialized records in dependency order (deps first), verifying each."""
    reg = {} if reg is None else reg
    pending = [r for r in recs if r["id"] not in reg]
    while pending:
        ready = [r for r in pending if all(d in reg for d in r["deps"])]
        if not ready:
            raise KeyError("unresolvable promoted dependencies: %s" % [r["id"] for r in pending])
        for r in sorted(ready, key=lambda r: (r["depth"], r["id"])):
            register(reg, Promoted.from_json(r, reg))
        pending = [r for r in pending if r["id"] not in reg]
    return reg


def lineage_records(reg: Dict[str, Promoted], ids: Iterable[str]) -> List[Dict]:
    """Serialized records of ids and all their transitive dependencies (deps first)."""
    need = set()
    for i in ids:
        need.add(i)
        need |= set(reg[i].lineage)
    return [reg[i].to_json() for i in sorted(need, key=lambda i: (reg[i].depth, i))]


def dag_depth(reg: Dict[str, Promoted]) -> int:
    return max((p.depth for p in reg.values()), default=0)


# ================================================================ expansion (the evaluation path the engine uses)
_SCHEMA_TERM: Dict[str, tuple] = {}


def expand_term(t, reg):
    """Replace every promoted node by its schema with the (expanded) argument in the hole, recursively."""
    if is_prim(t):
        p = reg[t[0][5:]]
        st = _SCHEMA_TERM.get(p.id)          # ids are content-addressed, so a global cache is safe
        if st is None:
            st = _SCHEMA_TERM[p.id] = parse(p.schema)
        return subst_hole(expand_term(st, reg), expand_term(t[1][0], reg))
    if not t[1]:
        return t
    return (t[0], [expand_term(a, reg) for a in t[1]])


def expand(src: str, reg) -> str:
    """Promoted-form source -> base-DSL source. A string with no promoted node is returned UNCHANGED (byte-identical),
    which is what makes zero-promotion runs identical to W5."""
    if not has_promoted(src):
        return src
    return to_src(expand_term(parse(src), reg))


def expand_program(prog, reg):
    return tuple([prog[0]] + [expand(s, reg) for s in prog[1:]])


# ================================================================ direct evaluator (TEST ORACLE ONLY)
_DIRECT: Dict[int, Dict] = {}


def _emit_direct(t) -> str:
    op, args = t
    if is_hole(t):
        return "H"
    if is_prim(t):
        return "%s(%s, acc, v, first, last)" % (op[5:], _emit_direct(args[0]))
    if not args:
        return to_src(t)
    if op in I.INFIX:
        return "(%s %s %s)" % (_emit_direct(args[0]), I.INFIX[op], _emit_direct(args[1]))
    if op == "gcd":
        return "math.gcd(abs(%s), abs(%s))" % (_emit_direct(args[0]), _emit_direct(args[1]))
    if op == "powr":
        return "pow(%s, %s)" % (_emit_direct(args[0]), _emit_direct(args[1]))
    if op == "abs":
        return "abs(%s)" % _emit_direct(args[0])
    raise ValueError(op)


def _direct_env(reg):
    env = _DIRECT.get(id(reg))
    if env is None or set(env["ids"]) != set(reg):
        g = dict(G._G)
        for pid, p in reg.items():
            # each promoted primitive is a real Python function of its argument VALUE (call-by-value), closed over
            # the same guarded globals; nested promoted calls resolve through the same dict
            g[pid] = eval("lambda H, acc, v, first, last: (%s)" % _emit_direct(parse(p.schema)), g)  # noqa: S307
        env = {"ids": list(reg), "g": g, "fns": {}}
        _DIRECT[id(reg)] = env
    return env


def direct_fn(src: str, reg):
    env = _direct_env(reg)
    f = env["fns"].get(src)
    if f is None:
        f = env["fns"][src] = eval("lambda acc, v, first, last: (%s)" % _emit_direct(parse(src)),  # noqa: S307
                                   env["g"])
    return f


def run_program_direct(prog, nums, trailing, reg):
    """Independent evaluator of promoted-form programs (promoted nodes are function CALLS, not expansions). Mirrors
    basis_v4.run_program exactly: env starts acc=v=0; ceiling checked after every body step and on the output; any
    exception -> None."""
    vals = nums[:-1] if trailing else nums
    first, last = nums[0], nums[-1]
    try:
        if prog[0] == "expr":
            out = direct_fn(prog[1], reg)(0, 0, first, last)
        else:
            _, init, body, final = prog
            bfn = direct_fn(body, reg)
            acc = direct_fn(init, reg)(0, 0, first, last)
            v = 0
            for v in vals:
                acc = bfn(acc, v, first, last)
                if acc is None or abs(acc) > CEIL:
                    return None
            out = direct_fn(final, reg)(acc, v, first, last)
        if out is None or abs(out) > CEIL:
            return None
        return out
    except Exception:      # noqa: BLE001
        return None


# ================================================================ recognition (fold base bodies into promoted form)
def _match(p, t, bind) -> bool:
    if is_hole(p):
        if "x" in bind:
            return bind["x"] == t
        bind["x"] = t
        return True
    if not p[1]:
        return p == t
    if p[0] != t[0] or len(p[1]) != len(t[1]):
        return False
    orders = [t[1]]
    if p[0] in I.COMMUTATIVE and len(t[1]) == 2:
        orders.append([t[1][1], t[1][0]])
    for ta in orders:
        b = dict(bind)
        if all(_match(pa, x, b) for pa, x in zip(p[1], ta)):
            bind.clear()
            bind.update(b)
            return True
    return False


def _patterns(reg):
    """Most specific first: deeper primitives, then larger expansions, then id (deterministic)."""
    ps = sorted(reg.values(), key=lambda p: (-p.depth, -p.contract["expansion_nodes"], p.id))
    return [(p, p.pattern(reg)) for p in ps]


def fold_term(t, reg, pats=None):
    """Bottom-up: rewrite every subterm that matches a promoted pattern (modulo commutative argument order) into
    P(x). A rewrite is kept only if the normalised EXPANSION of the result equals the normalised node (so recognition
    is sound by construction: normalise is value-preserving). Recognition is deliberately incomplete (e.g. a
    neutral-element rewrite like (acc + 0) -> acc hides the pattern)."""
    if not reg:
        return t
    pats = pats if pats is not None else _patterns(reg)
    if t[1]:
        t = (t[0], [fold_term(a, reg, pats) for a in t[1]])
    if is_atom(t):
        return t
    base_norm = None
    for p, pat in pats:
        b = {}
        if _match(pat, t, b) and "x" in b:
            cand = ("prim:" + p.id, [b["x"]])
            if base_norm is None:
                base_norm = normalise(expand_term(t, reg))
            if normalise(expand_term(cand, reg)) == base_norm:
                return cand
    return t


def forms(body: str, reg, pats=None) -> List[str]:
    """The representations of a base body that derivation sees: [body] plus its folded promoted form when that differs.
    With an empty registry this is exactly [body]."""
    if not reg:
        return [body]
    t = normalise(parse(body), reg)
    f = fold_term(t, reg, pats)
    if prims_in(f):
        return [body, to_src(f)]
    return [body]


# ================================================================ W5P instantiation space
def g5p_admissible(t) -> bool:
    """W5P body grammar for a promoted-form body that CONTAINS a promoted node: node depth <= 3 counting each promoted
    node as one unary node, and every binary node has at least one atom child (W5's spine shape, both argument orders).
    Bodies with no promoted node use W5's exact in-space rule instead (tier3d.in_space_body)."""
    if depth(t) > MAX_DEPTH:
        return False

    def ok(n):
        if not n[1]:
            return True
        if len(n[1]) == 2 and not (is_atom(n[1][0]) or is_atom(n[1][1])):
            return False
        return all(ok(a) for a in n[1])
    return ok(t)


def fillers(reg) -> List[str]:
    """Hole filler set: W5's LEVEL1 (identical order) followed by P(a) for every promoted P (id order) and every body
    atom. With an empty registry this is exactly fair.LEVEL1."""
    import fair as FR
    return list(FR.LEVEL1) + ["%s(%s)" % (pid, a) for pid in sorted(reg) for a in G.BODY_ATOMS]


def instantiate(schema: str, reg, form_map: Optional[Dict[str, str]] = None) -> List[str]:
    """W5P instantiation of a promoted-form one-hole schema. Returns EXPANDED base bodies (what the engine walks).
    For each filler f (fillers(reg) order): b = schema[{H} := f];
      - no promoted node in b: W5's exact rule (tier3d.in_space_body), identical to tier3d.instantiate;
      - otherwise: kept iff g5p_admissible(normalised b); its expansion is mapped to W5's in-space representative when
        the expansion is in G5, else kept as the expansion string, deduplicated by normalised structure.
    form_map (optional) receives expanded body -> promoted form, for cost accounting and recognition.
    With an empty registry and a base schema the output equals tier3d.instantiate(schema) (tested)."""
    import tier3d as T3D
    out, seen = [], set()
    for f in fillers(reg):
        b = schema.replace(HOLE, f)
        if not has_promoted(b):
            rb = T3D.in_space_body(b)
            if rb is not None:
                out.append(rb)
            continue
        t = normalise(parse(b), reg)
        if not g5p_admissible(t):
            continue
        exp = to_src(expand_term(t, reg))
        rb = T3D.in_space_body(exp)
        if rb is None:
            key = I.term_str(normalise(parse(exp)))
            if key in seen:
                continue
            seen.add(key)
            rb = exp
        out.append(rb)
        if form_map is not None:
            form_map.setdefault(rb, to_src(t))
    return list(dict.fromkeys(out))


def schema_expansion(schema: str, reg) -> str:
    return expand(schema, reg)


# ================================================================ derivation (tier3d D4 over promoted forms)
def _lgg_pairs(lists, reg, found, need_promoted=False):
    import tier3d as T3D
    terms = [[(a, normalise(parse(a), reg)) for a in dict.fromkeys(cls)] for cls in lists]
    for ci in range(len(terms)):
        for cj in range(ci + 1, len(terms)):
            for a, ta in terms[ci]:
                for b, tb in terms[cj]:
                    if need_promoted and not (has_promoted(a) or has_promoted(b)):
                        continue            # plain-plain pairs were already taken in the plain pass
                    g, table = T3D.lgg(ta, tb)
                    if len(table) != 1 or g[0].startswith("hole"):
                        continue
                    found.setdefault(to_src(g), []).append((ci, cj, a, b))
    return found


def derive_schemas(member_bodies_by_class: List[List[str]], reg) -> List[Dict]:
    """tier3d.derive_schemas (D4) in two representations, merged:
      pass 1 (W5):  LGG over every pair of DISTINCT classes and every pair of their members' PLAIN base bodies --
                    exactly tier3d.derive_schemas;
      pass 2 (W5P): the same over the members' FOLDED forms (fold_term with the registry), counting only pairs in
                    which at least one member actually contains a promoted node.
    A promoted node is ONE node to the LGG, so a pass-2 schema can contain a promoted primitive (the depth-2
    dependency). Pairs never mix representations (a plain body against a folded body would generalise the whole
    differing subterm into the hole, an artefact of the encoding, not of the behaviour classes). Keep
    exactly-one-hole, non-root. With an empty registry the output equals tier3d.derive_schemas (tested)."""
    found = _lgg_pairs(member_bodies_by_class, reg, {})
    if reg:
        pats = _patterns(reg)
        folded = [[forms(b, reg, pats)[-1] for b in cls] for cls in member_bodies_by_class]
        if any(has_promoted(x) for cls in folded for x in cls):
            _lgg_pairs(folded, reg, found, need_promoted=True)
    return [{"schema": s, "witness_pairs": v[:4], "n_pairs": len(v)}
            for s, v in sorted(found.items())]

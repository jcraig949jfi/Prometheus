"""TFS-1 learned primitives: promotion, exact semantics by expansion, hashing, lineage, depth, alias collapse,
deterministic serialization.

An ENTRY is a named typed primitive  L_<12 hex>(h0, ..., h_{k-1}) := BODY, k <= 2, where BODY is a term whose only
free names are the parameters h0..h_{k-1} (holes) and the global task input xs (no free lambda variables). BODY may
call earlier entries (its DEPENDENCIES). Parameters may be value-typed (Int, Bool, List) or function-typed
(Int->Int, Int->Bool, Int->Int->Int; such a parameter is passed a lambda and may be used where a lambda is expected).

  id         = "L_" + sha256(canonical{version, params, body})[:12]     content-addressed; arm/name/provenance-blind
  expansion  = BODY with every library call replaced (recursively) by its callee's expansion; base contract-v0 only
  deps       = sorted distinct entries BODY calls directly;  lineage = deps + their lineages (transitive)
  depth      = 1 + max(dep depth) (1 if no deps)  -- EXCEPT an alias (below), whose depth is its callee's depth
  hash       = sha256 of the canonical record (every field except hash)

ALIAS RULES (the Beta-03 O1 defect: a bare re-expression P_x({H}) was recorded at depth 2):
  A1 (collapse)       if BODY's expansion (with the same parameter types), after commutative canonicalisation (args of
                      add mul gcd eq and or sorted), equals an existing entry's, the
                      promotion returns THAT entry: no new id, no new depth level. Covers eta-aliases (L_k h0 h1) and
                      any re-spelling of an existing mechanism.
  A2 (re-expression)  if BODY is a single library call whose arguments are all atoms (holes, literals, xs), the entry is
                      kept (it is a distinct function, e.g. L_k(h0, 1)) but alias_of = callee and depth = callee depth.
  A0 (trivial)        bodies of size 1 (a bare hole / literal / xs) are rejected.

SEMANTICS: an entry is evaluated by expansion. The interpreter's direct path (call-by-name thunks, core.py) is proven
equal to expansion by test (value, FAIL and the expanded execution-unit ledger).
"""
import hashlib
import json
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from . import core as C
from .enum import canon_comm

VERSION = "tfs1-lib-v0"
MAX_ARITY = 2


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def sha(obj) -> str:
    return hashlib.sha256(canon(obj)).hexdigest()


def infer_hole_types(t, lib=None, expected: Optional[str] = None, nvars: int = 0,
                     acc: Optional[Dict[int, str]] = None) -> Dict[int, str]:
    """Hole types from the positions the holes occupy (top-down expected types)."""
    acc = {} if acc is None else acc
    tag = t[0]

    def put(j, ty):
        if ty is None:
            raise C.TypeErr("cannot infer the type of hole h%d" % j)
        if acc.get(j, ty) != ty:
            raise C.TypeErr("hole h%d used at %s and %s" % (j, acc[j], ty))
        acc[j] = ty

    if tag == "hole":
        put(t[1], expected)
        return acc
    if tag in ("int", "var", "xs"):
        return acc
    if tag == "lam":
        bt = C.FN_SHAPE[expected][1] if expected in C.FN_SHAPE else None
        infer_hole_types(t[2], lib, bt, nvars + t[1], acc)
        return acc
    if tag == "app":
        f = t[1]
        k = len(t) - 2
        if f[0] == "hole":
            put(f[1], C.LAMBDA_TYPE.get((k, expected)))
        else:
            infer_hole_types(f, lib, C.LAMBDA_TYPE.get((k, expected)), nvars, acc)
        for a in t[2:]:
            infer_hole_types(a, lib, C.INT, nvars, acc)
        return acc
    if tag in C.PRIM_SIGS:
        ats = C.PRIM_SIGS[tag][0]
    else:
        ats = lib.sig(tag)[0]
    for a, at in zip(t[1:], ats):
        infer_hole_types(a, lib, at, nvars, acc)
    return acc


def lambda_to_body(lam) -> Tuple[tuple, int]:
    """(lam k BODY) -> BODY with the k lambda parameters turned into holes (a = h0, b = h1; unary x = h0)."""
    if lam[0] != "lam":
        raise ValueError("not a lambda")
    k = lam[1]

    def go(t, d):
        tag = t[0]
        if tag == "var":
            i = t[1]
            if i < d:
                return t
            j = i - d
            if j >= k:
                raise ValueError("lambda is not closed (free variable)")
            return ("hole", k - 1 - j)
        if tag in ("int", "xs"):
            return t
        if tag == "hole":
            raise ValueError("lambda already contains holes")
        if tag == "lam":
            return ("lam", t[1], go(t[2], d + t[1]))
        return (tag,) + tuple(go(a, d) for a in t[1:])
    return go(lam[2], 0), k


def _is_atom(t) -> bool:
    return t[0] in ("hole", "int", "xs")


class Entry:
    FIELDS = ("version", "id", "params", "ret", "body", "expansion", "deps", "lineage", "depth", "alias_of",
              "body_size", "expansion_size", "provenance")

    def __init__(self, rec: Dict):
        self.rec = {k: rec[k] for k in self.FIELDS}
        for k in self.FIELDS:
            setattr(self, k, self.rec[k])
        self.body_t = C.parse(self.body)
        self.exp_t = C.parse(self.expansion)
        self.hash = sha(self.rec)

    def to_json(self) -> Dict:
        out = dict(self.rec)
        out["hash"] = self.hash
        return out

    def sig(self):
        return tuple(self.params), self.ret


class Library:
    """A registry of entries. Iteration order everywhere is by id (content), never by insertion."""

    def __init__(self):
        self.entries: Dict[str, Entry] = {}
        self._by_expansion: Dict[Tuple, str] = {}
        self._compiled: Dict[str, object] = {}

    # ---- interface used by core / enumerator
    def sig(self, name: str):
        return self.entries[name].sig()

    def __contains__(self, name):
        return name in self.entries

    def __len__(self):
        return len(self.entries)

    def ids(self) -> List[str]:
        return sorted(self.entries)

    def compiled_body(self, name: str):
        c = self._compiled.get(name)
        if c is None:
            c = self._compiled[name] = C.compile_term(self.entries[name].body_t, self, None, swap=True)
        return c

    # ---- expansion
    def expand(self, t):
        tag = t[0]
        if tag.startswith("L_"):
            e = self.entries[tag]
            return C.subst_holes(e.exp_t, [self.expand(a) for a in t[1:]])
        if tag in ("int", "var", "xs", "hole"):
            return t
        if tag == "lam":
            return ("lam", t[1], self.expand(t[2]))
        return (tag,) + tuple(self.expand(a) for a in t[1:])

    # ---- promotion
    def promote_body(self, body, params: Optional[Sequence[str]] = None, provenance: Optional[Dict] = None,
                     _register: bool = True) -> Tuple[Entry, str]:
        """Promote BODY (a term over holes h0..h_{k-1}, k <= 2). Returns (entry, status) with status in
        {'new', 'exists', 'collapsed'}; 'collapsed' = alias rule A1 returned an existing entry."""
        provenance = dict(provenance or {})
        if C.free_var_min_escape(body):
            raise ValueError("body has a free lambda variable (not closed)")
        if C.size(body) < 2:
            raise ValueError("A0: trivial body (bare hole/literal/xs) is not promotable")
        if body[0] == "lam":
            raise ValueError("body must be value-typed (promote a lambda with promote_lambda)")
        hs = C.holes_in(body)
        if params is None:
            ht = infer_hole_types(body, self, None)
            k = (max(hs) + 1) if hs else 0
            if sorted(ht) != list(range(k)):
                raise ValueError("holes must be h0..h%d" % (k - 1))
            params = [ht[j] for j in range(k)]
        params = list(params)
        if len(params) > MAX_ARITY:
            raise ValueError("arity %d > %d" % (len(params), MAX_ARITY))
        if hs and max(hs) >= len(params):
            raise ValueError("hole index beyond arity")
        ret = C.type_of(body, 0, params, self)
        if ret not in C.VALUE_TYPES:
            raise C.TypeErr("entry result must be a value type")
        exp_t = self.expand(body)
        exp_s = C.to_str(exp_t)
        key = (tuple(params), C.to_str(canon_comm(exp_t)))    # commuted re-spellings collapse too
        if key in self._by_expansion:
            return self.entries[self._by_expansion[key]], "collapsed"
        body_s = C.to_str(body)
        deps = sorted(set(C.calls_in(body)))
        lineage = sorted(set(deps).union(*[set(self.entries[d].lineage) for d in deps]) if deps else set())
        alias_of = None
        if body[0].startswith("L_") and all(_is_atom(a) for a in body[1:]):
            alias_of = body[0]
            depth = self.entries[alias_of].depth
        else:
            depth = 1 + max([self.entries[d].depth for d in deps], default=0)
        eid = "L_" + sha({"version": VERSION, "params": params, "body": body_s})[:12]
        if eid in self.entries:
            return self.entries[eid], "exists"
        rec = {"version": VERSION, "id": eid, "params": params, "ret": ret, "body": body_s, "expansion": exp_s,
               "deps": deps, "lineage": lineage, "depth": depth, "alias_of": alias_of,
               "body_size": C.size(body), "expansion_size": C.size(exp_t), "provenance": provenance}
        e = Entry(rec)
        if _register:
            self._add(e, key)
        return e, "new"

    def _add(self, e: Entry, key):
        self.entries[e.id] = e
        self._by_expansion[key] = e.id

    def promote_term(self, t, provenance=None):
        """A closed term (no free lambda variables, no holes; xs allowed) -> arity-0 entry."""
        if C.holes_in(t):
            raise ValueError("closed term expected")
        return self.promote_body(t, [], provenance)

    def promote_lambda(self, lam, provenance=None):
        """A closed lambda of arity <= 2 -> entry with Int parameters (lam x B) -> L(h0), (lam a (lam b B)) -> L(h0, h1).
        Unused lambda parameters are allowed (call-by-name: the argument is then never evaluated)."""
        body, k = lambda_to_body(lam)
        return self.promote_body(body, [C.INT] * k, provenance)

    # ---- serialization (entries only)
    def records(self, ids: Optional[Iterable[str]] = None) -> List[Dict]:
        need = set(self.entries) if ids is None else set()
        if ids is not None:
            for i in ids:
                need.add(i)
                need |= set(self.entries[i].lineage)
        return [self.entries[i].to_json() for i in sorted(need, key=lambda i: (self.entries[i].depth, i))]

    def to_json(self, ids=None) -> Dict:
        return {"format": VERSION, "contract": C.CONTRACT, "entries": self.records(ids)}

    def dumps(self, ids=None) -> str:
        return canon(self.to_json(ids)).decode()

    def sha256(self) -> str:
        return hashlib.sha256(self.dumps().encode()).hexdigest()

    @classmethod
    def from_json(cls, obj: Dict) -> "Library":
        """Load and VERIFY: format, each record's hash, and that every record re-derives byte-identically from its body
        (deps first)."""
        if obj.get("format") != VERSION:
            raise ValueError("library format %r" % obj.get("format"))
        lib = cls()
        pending = list(obj["entries"])
        for r in pending:
            body = {k: r[k] for k in Entry.FIELDS}
            if r.get("hash") != sha(body):
                raise ValueError("record hash mismatch for %s" % r.get("id"))
        while pending:
            ready = [r for r in pending if all(d in lib.entries for d in r["deps"])]
            if not ready:
                raise KeyError("unresolvable dependencies: %s" % [r["id"] for r in pending])
            for r in sorted(ready, key=lambda r: (r["depth"], r["id"])):
                e, st = lib.promote_body(C.parse(r["body"]), r["params"], r["provenance"])
                if st != "new" or e.to_json() != r:
                    raise ValueError("record does not re-derive: %s (%s)" % (r["id"], st))
            pending = [r for r in pending if r["id"] not in lib.entries]
        return lib

    @classmethod
    def loads(cls, s: str) -> "Library":
        return cls.from_json(json.loads(s))

    def copy(self) -> "Library":
        return Library.from_json(self.to_json())

    # ---- ledgers
    def static_sizes(self, t) -> Dict[str, int]:
        """Static cost ledgers of a program: promoted-form size (a call is one node) and fully expanded size."""
        return {"size_promoted": C.size(t), "size_expanded": C.size(self.expand(t))}

    def max_depth(self) -> int:
        return max((e.depth for e in self.entries.values()), default=0)

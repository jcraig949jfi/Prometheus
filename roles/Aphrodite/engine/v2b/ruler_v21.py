# V2B FROZEN COPY (C-006 Beta-01, DEV-1, 2026-10-04): byte-identical body of
#   roles/Aphrodite/science/arc3/w7_instrument_hygiene/ruler_v21.py  (git blob 959ff02b261061da357ae3fcd73ab08a3edb6905, sha256 fb49eec5e8c2bd95fd377f751d7ab653fee916fc49522d50013f6cd04f0b860e)
# Frozen as an apparatus instrument of v2b-1. The historical instrument it repairs is untouched.
"""DRAFT -- RULER v2.1 (W7, ARC3 PKG-7). NEW FILE; science/compounding/rb1/
ruler_v2.py is imported and never modified. NOTHING HERE IS ADOPTED: it is an
instrument only if the Aphrodite seat freezes it in a dated AMENDMENT.

Repairs relative to RULER v2 (W3 F1, F4, F5-partial; PKG-7):
  R1  RELATIONS CLOSED OVER RE-EXPRESSIONS OF THE REFERENCE.
      rel21(S, G) = OR over r in reexpressions(G) of v2.relations(S, r)
                    OR the SIGNED-SUM relations below.
      Signed sums: a +/- chain is flattened into a signed multiset of operands
      (const 0 dropped; x - (0 - y) = x + y). For a reference whose root is +/-
      (G1 = acc + {H}): fixed(G) = its hole-free operands, e.g. {+acc}.
        EQUAL_C    F(S) = fixed(G) + {+-hole}           (re-expression of G)
        REFINES_C  fixed(G) is a signed sub-multiset of F(S) and the remaining
                   operands contain the hole and are not a single bare +-hole
                   ((acc - {H}*first), ((acc - {H}) + v), (first + (acc + {H})))
        COMPOSES_C fixed(G) with ALL signs flipped is a sub-multiset of F(S) and
                   the remaining operands contain the hole (a negated G inside a
                   context: (v - (acc - {H})) = SHAM_0, ((v - acc) - {H})), or
                   some maximal proper +/- chain or other proper subterm of S is
                   EQUAL_C / REFINES_C / COMPOSES_C to G.
      EQUAL in the verdict = literal EQUAL or EQUAL_C.
  R2  SAME-WITNESS REQUIREMENT. NEW_FINAL counts the instances that are BOTH
      grid-novel and trajectory-novel; |both| >= 2 and >= 10% of accumulating
      instances (v2 counted the two sets separately; they can be disjoint).
  R3  NONE TOLERANCE + DECLARED LENGTH DOMAIN on the trajectory battery (the
      frozen 80-input battery, lengths 2..40). For each (instance, init):
        L_dom = the largest rung r in RUNGS such that at most NONE_TOL of the
                battery inputs of length <= r give None (T4's L_max idea with a
                tolerance). DEFAULT NONE_TOL = 0.0 (strict totality inside the
                declared domain): 0.25 was tested and fixes no additional
                adversarial case while raising the W5 random-schema base rate
                from 24.5% to 29% (it admits division-by-zero junk). L_dom undefined (even r = 20 fails) -> the
                (instance, init) trajectory is DEGENERATE (T4: DOMAIN_TOO_SHORT).
        Inputs longer than L_dom are OUT OF DOMAIN (masked, never compared).
        Non-degenerate: >= 5 distinct defined values in domain.
        Novel: no reference trajectory AGREES with it, where agree = equal on
        every position defined in both (and in the candidate's domain), with
        >= MIN_COMMON such positions. (v2: any None anywhere -> degenerate;
        products of length > ~30 overflow the ceiling, so ((acc + {H}) * v)
        read as trajectory-novel on 0/144 instances.)
  R4  BASE RATE REPORTED PER WORLD. w7_ruler_validate.py reports the
      random-schema (RB-1 junk generator) NEW_FINAL rate for G4 and W5 under
      v2 and v2.1; any NEW verdict must be quoted beside its world's rate.
NOT repaired (documented): distributed re-expressions ((acc*v) + ({H}*v)) are
not factored; the grid still assumes acc >= 0 (W3 F5); inert wraps are still
COMPOSES (W3 F6); efficiency-only schemas are still NEW (W3 F7).
"""
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path

RB1 = Path(__file__).resolve().parents[2] / "compounding" / "rb1"
sys.path.insert(0, str(RB1))
import ruler_v2 as R2          # noqa: E402
import fasteval as FE          # noqa: E402  (path set by ruler_v2)
import tier3d as T3D           # noqa: E402

VERSION = "RULER_v2.1_DRAFT_W7"
RUNGS = (20, 25, 30, 35, 40)
NONE_TOL = float(__import__("os").environ.get("W7_NONE_TOL", "0.0"))   # recommended 0.0; 0.25 tested (ablation hook)
MIN_COMMON = 10
DISTINCT = 5
FLOOR, MINCOUNT = 0.10, 2

vec, conj_vec, accumulating, fclass = R2.vec, R2.conj_vec, R2.accumulating, R2.fclass
reexpressions, span, span_of_schema = R2.reexpressions, R2.span, R2.span_of_schema
reexpression_bodies = R2.reexpression_bodies


# ================================================================ R1 relations
def _is_zero(t):
    return t[0] == "const:0"


def _flat_signed(t, sign=1):
    """Signed operand multiset of a maximal +/- chain rooted at t."""
    if t[0] == "add":
        out = []
        for a in t[1]:
            out += _flat_signed(a, sign)
        return out
    if t[0] == "sub":
        return _flat_signed(t[1][0], sign) + _flat_signed(t[1][1], -sign)
    if _is_zero(t):
        return []
    return [(sign, t)]


def _key(op):
    return (op[0], repr(op[1]))


def _submultiset(small, big):
    c = Counter(_key(x) for x in big)
    for x in small:
        k = _key(x)
        if c[k] <= 0:
            return None
        c[k] -= 1
    rest = []
    for x in big:
        k = _key(x)
        if c[k] > 0:
            rest.append(x)
            c[k] -= 1
    return rest


def _hole_in(ops):
    return any(R2._contains_hole(t) for _s, t in ops)


def _signed_rel(s_term, g_term):
    """(EQUAL_C, REFINES_C, NEG_COMPOSES) of the chain rooted at s_term vs a
    +/- reference g_term; None if the reference is not a +/- chain."""
    if g_term[0] not in ("add", "sub"):
        return None
    fg = _flat_signed(g_term)
    fixed = [x for x in fg if not R2._contains_hole(x[1])]
    holes = [x for x in fg if R2._contains_hole(x[1])]
    if len(holes) != 1:
        return None
    fs = _flat_signed(s_term)
    eq = ref = neg = False
    rest = _submultiset(fixed, fs)
    if rest is not None and _hole_in(rest):
        bare = len(rest) == 1 and R2._is_hole(rest[0][1])
        if bare and R2._is_hole(holes[0][1]):
            eq = True
        elif bare and _key(rest[0]) == _key(holes[0]):
            eq = True
        else:
            ref = True
    flipped = [(-sg, t) for sg, t in fixed]
    rest2 = _submultiset(flipped, fs)
    if fixed and rest2 is not None and _hole_in(rest2):
        neg = True
    return eq, ref, neg


def _chains(t, parent_is_chain=False, depth=0):
    """Maximal +/- chains and other subterms, with depth (root = 0)."""
    is_chain = t[0] in ("add", "sub")
    if not (is_chain and parent_is_chain):
        yield t, depth
    for a in t[1]:
        yield from _chains(a, is_chain, depth + 1)


@lru_cache(maxsize=None)
def relations(schema, ref_schema):
    """v2.1 structural relations, closed over re-expressions of ref_schema."""
    out = {"EQUAL": False, "REFINES": False, "COMPOSES": False,
           "EQUAL_C": False, "REFINES_C": False, "COMPOSES_C": False, "via": []}
    for r in reexpressions(ref_schema):
        x = R2.relations(schema, r)
        for k in ("EQUAL", "REFINES", "COMPOSES"):
            if x[k] and not out[k]:
                out[k] = True
                out["via"].append("%s:literal:%s" % (k, r))
    s, g = R2._term(schema), R2._term(ref_schema)
    root = _signed_rel(s, g)
    if root is not None:
        eq, ref, neg = root
        out["EQUAL_C"] = eq
        out["REFINES_C"] = ref and not eq
        if neg:
            out["COMPOSES_C"] = True
            out["via"].append("COMPOSES:negated-reference-at-root")
        for sub, d in _chains(s):
            if d == 0 or out["COMPOSES_C"]:
                continue
            x = _signed_rel(sub, g)
            if x and any(x) and R2._contains_hole(sub):
                out["COMPOSES_C"] = True
                out["via"].append("COMPOSES:subchain")
    out["EQUAL_ANY"] = out["EQUAL"] or out["EQUAL_C"]
    out["REFINES_ANY"] = (out["REFINES"] or out["REFINES_C"]) and not out["EQUAL_ANY"]
    out["COMPOSES_ANY"] = out["COMPOSES"] or out["COMPOSES_C"]
    return out


# ================================================================ R3 trajectory
_BAT = None
_LENS = None


def battery():
    global _BAT, _LENS
    if _BAT is None:
        _BAT = R2._traj_inputs()                 # the frozen v2 battery (80 inputs, lengths 2..40)
        _LENS = [len(x) - 1 for x in _BAT]
    return _BAT


def lengths():
    battery()
    return _LENS


@lru_cache(maxsize=None)
def traj_raw(b, init):
    return tuple(FE.run_program(("fold", init, b, "acc"), x, True) for x in battery())


@lru_cache(maxsize=None)
def domain(b, init):
    """(L_dom or None, masked trajectory: out-of-domain -> None)."""
    t, Ls = traj_raw(b, init), lengths()
    l_dom = None
    for r in RUNGS:
        idx = [k for k, L in enumerate(Ls) if L <= r]
        nn = sum(t[k] is None for k in idx)
        if nn <= NONE_TOL * len(idx):
            l_dom = r
        else:
            break
    if l_dom is None:
        return None, None
    return l_dom, tuple(x if L <= l_dom else None for x, L in zip(t, Ls))


def nondegenerate(b, init):
    l_dom, m = domain(b, init)
    if l_dom is None:
        return False
    return len({x for x in m if x is not None}) >= DISTINCT


class RefIndex:
    """Reference trajectories (raw, unmasked), indexed on the positions of
    length <= 20 (always inside any admissible domain)."""

    def __init__(self, ref_bodies, inits=("0", "1")):
        self.short = [k for k, L in enumerate(lengths()) if L <= RUNGS[0]]
        self.idx, self.slow = {}, []
        seen = set()
        for r in ref_bodies:
            for i in inits:
                t = traj_raw(r, i)
                if t in seen:
                    continue
                seen.add(t)
                key = tuple(t[k] for k in self.short)
                if any(x is None for x in key):
                    self.slow.append(t)
                else:
                    self.idx.setdefault(key, []).append(t)
        self.n = len(seen)

    @staticmethod
    def _agree(m, t):
        common = 0
        for x, y in zip(m, t):
            if x is None or y is None:
                continue
            if x != y:
                return False
            common += 1
        return common >= MIN_COMMON

    def novel(self, m):
        key = tuple(m[k] for k in self.short)
        if all(x is not None for x in key):
            cands = self.idx.get(key, []) + self.slow
        else:
            cands = [t for v in self.idx.values() for t in v] + self.slow
        return not any(self._agree(m, t) for t in cands)


def traj_novel_instance(b, rindex, inits=("0", "1")):
    for i in inits:
        if nondegenerate(b, i) and rindex.novel(domain(b, i)[1]):
            return True
    return False


# ================================================================ verdict
def grid_novel_instance(b, ref_span, exclude_classes=("ADDITIVE",)):
    return vec(b) not in ref_span and fclass(b) not in exclude_classes


def verdict_full(schema, ref_schema, ref_span, rindex, inst=None):
    inst = inst if inst is not None else T3D.instantiate(schema)
    acc = [b for b in inst if accumulating(b)]
    g = {b for b in acc if grid_novel_instance(b, ref_span)}
    t = {b for b in acc if traj_novel_instance(b, rindex)}
    both = g & t
    ok = lambda c: c >= MINCOUNT and c >= FLOOR * max(1, len(acc))   # noqa: E731
    rel = relations(schema, ref_schema)
    doms = Counter()
    for b in acc:
        for i in ("0", "1"):
            doms[domain(b, i)[0]] += 1
    r = {"ruler": VERSION, "schema": schema, "instantiations": len(inst), "accumulating": len(acc),
         "grid_novel": len(g), "traj_novel": len(t), "both_novel": len(both),
         "NEW_GRID": ok(len(g)), "NEW_TRAJ": ok(len(t)), "NEW_BOTH": ok(len(both)),
         "domain_hist": {str(k): v for k, v in sorted(doms.items(), key=lambda kv: (kv[0] is None, kv[0] or 0))},
         "examples": sorted(both)[:4]}
    r.update({k: rel[k] for k in ("EQUAL_ANY", "REFINES_ANY", "COMPOSES_ANY", "EQUAL", "REFINES", "COMPOSES",
                                  "EQUAL_C", "REFINES_C", "COMPOSES_C", "via")})
    r["NEW_FINAL"] = r["NEW_BOTH"] and not rel["EQUAL_ANY"] and not rel["REFINES_ANY"]
    r["COMPOSITIONAL_NOVELTY"] = r["NEW_FINAL"] and rel["COMPOSES_ANY"]
    return r


def reference(ref_schema="(acc + {H})"):
    """(ref_span, RefIndex) for a reference schema: its instantiations and those
    of its re-expressions (and conjugates on the grid)."""
    return span_of_schema(ref_schema), RefIndex(reexpression_bodies(ref_schema))

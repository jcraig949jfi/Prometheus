"""RULER v2 -- a task-grounded, conjugate-closed novelty ruler plus separate
structural relations (RB-1; threads T01/T02). Forensic tooling; nothing frozen
is modified. The old ruler (tier3e.semantically_new) is untouched and remains
the instrument of record for AMENDMENTs 12-17.

Definitions (a body b is a function b(acc, v, first, last)):
  GRID        task-reachable states: acc >= 0 (fold accumulators on the task
              domain start at init in {0,1} or small values and stay >= 0 for
              the families of interest), v in 2..30, first in 2..30, last in 1..97.
  vec(b)      b's values on GRID ('N' = None/ceiling, 'E' = exception).
  ACCUMULATING(b)  vec depends on acc AND on v somewhere on GRID (else the fold
              ignores its state or its input: junk for abstraction purposes).
  conj(r)     the body -r(-acc, v, first, last): the compensating-factorisation
              partner (a sign flip of the accumulator undone by the final).
  SPAN(ref)   {vec(r), vec(conj r) : r a reference body}.
  NEW_V2(S, ref)  let A = ACCUMULATING instantiations of S, N = {b in A :
              vec(b) not in SPAN(ref)}; NEW iff |N| >= 2 and |N| >= 0.10|A|.
              (a proportion floor: novelty must belong to the schema, not to a
              few edge instantiations -- the R-a false-positive channel.)
  FCLASS(b)   functional class on GRID: CONST_IN_ACC (junk), ADDITIVE
              (b - acc independent of acc), AFFINE (b = m*acc + c, m != 1, per
              (v, first, last)), OTHER.
Structural relations to a reference schema G (independent of NEW):
  REFINES(S, G)   S = G[t] with t a proper term containing the hole
                  (a specialisation that re-opens the hole deeper).
  COMPOSES(S, G)  S = C[G[t]] for a NON-EMPTY context C (S uses G inside).
  EXTENDS_REACH(S, cov)  S has an accumulating instantiation whose vec is not
                  the vec of any body in the reference library coverage.
"""
import sys
from functools import lru_cache
from pathlib import Path

ENG = Path(__file__).resolve().parents[3] / "engine"
sys.path.insert(0, str(ENG))
sys.path.insert(0, str(ENG / "accel"))
import fasteval as FE     # noqa: E402
import identity as I      # noqa: E402
import tier3d as T3D      # noqa: E402

CEIL = 10 ** 40
ACCS = (0, 1, 2, 3, 5, 8, 13, 29, 64, 97, 150, 512, 1000, 4096, 10007)
VS = (2, 3, 5, 7, 12, 19, 30)
FIRSTS = (2, 7, 23)
LASTS = (1, 3, 41, 97)
GRID = [(a, v, f, l) for a in ACCS for v in VS for f in FIRSTS for l in LASTS]


def _val(fn, a, v, f, l):
    try:
        x = fn(a, v, f, l)
    except Exception:  # noqa: BLE001
        return "E"
    if x is None or abs(x) > CEIL:
        return "N"
    return x


@lru_cache(maxsize=None)
def vec(b):
    fn = FE.fn(b)
    return tuple(_val(fn, a, v, f, l) for a, v, f, l in GRID)


@lru_cache(maxsize=None)
def conj_vec(b):
    fn = FE.fn(b)
    out = []
    for a, v, f, l in GRID:
        x = _val(fn, -a, v, f, l)
        out.append(-x if isinstance(x, int) else x)
    return tuple(out)


def _index(a_i, v_i, f_i, l_i):
    return ((a_i * len(VS) + v_i) * len(FIRSTS) + f_i) * len(LASTS) + l_i


@lru_cache(maxsize=None)
def accumulating(b):
    x = vec(b)
    dep_acc = dep_v = False
    for vi in range(len(VS)):
        for fi in range(len(FIRSTS)):
            for li in range(len(LASTS)):
                col = {x[_index(ai, vi, fi, li)] for ai in range(len(ACCS))}
                if len(col) > 1:
                    dep_acc = True
    for ai in range(len(ACCS)):
        for fi in range(len(FIRSTS)):
            for li in range(len(LASTS)):
                row = {x[_index(ai, vi, fi, li)] for vi in range(len(VS))}
                if len(row) > 1:
                    dep_v = True
    return dep_acc and dep_v


@lru_cache(maxsize=None)
def fclass(b):
    x = vec(b)
    if not accumulating(b):
        return "CONST_IN_ACC_OR_V"
    add = aff = True
    for vi in range(len(VS)):
        for fi in range(len(FIRSTS)):
            for li in range(len(LASTS)):
                ys = [x[_index(ai, vi, fi, li)] for ai in range(len(ACCS))]
                if any(not isinstance(y, int) for y in ys):
                    add = aff = False
                    break
                d = {y - a for y, a in zip(ys, ACCS)}
                if len(d) != 1:
                    add = False
                # affine: y = m*a + c with a0 = 0 -> c = ys[0]; m from a=1
                c, m = ys[0], ys[1] - ys[0]
                if any(y != m * a + c for y, a in zip(ys, ACCS)):
                    aff = False
            if not (add or aff):
                break
        if not (add or aff):
            break
    return "ADDITIVE" if add else ("AFFINE" if aff else "OTHER")


COMMUTATIVE_ROOTS = ("+", "*", "math.gcd")


def reexpressions(schema):
    """Schema-level re-expressions of a reference schema that the operator's
    definition excludes from novelty: argument swap at a commutative root and
    the additive sign flip (a + {H}) <-> (a - {H}) (i.e. H -> 0 - H). Returned
    as schema strings; instantiated over the same filler class (LEVEL1)."""
    out = {schema}
    t = schema.strip()
    for op in (" + ", " - ", " * "):
        if t.startswith("(") and t.endswith(")"):
            inner = t[1:-1]
            depth = 0
            for i, ch in enumerate(inner):
                depth += ch == "("
                depth -= ch == ")"
                if depth == 0 and inner[i:i + len(op)] == op:
                    a, b = inner[:i], inner[i + len(op):]
                    if op in (" + ", " * "):
                        out.add("(%s%s%s)" % (b, op, a))
                    if op in (" + ", " - "):
                        flip = " - " if op == " + " else " + "
                        out.add("(%s%s%s)" % (a, flip, b))
                    break
    return sorted(out)


def span_of_schema(schema):
    """SPAN of a reference SCHEMA: its instantiations and those of its
    re-expressions, each with its conjugate."""
    bodies = []
    for r in reexpressions(schema):
        bodies += T3D.instantiate(r)
    return span(list(dict.fromkeys(bodies)))


def span(ref_bodies):
    s = set()
    for r in ref_bodies:
        s.add(vec(r))
        s.add(conj_vec(r))
    return s


def new_v2(schema, ref_span, inst=None, exclude_classes=("ADDITIVE",)):
    """exclude_classes: functional classes that ARE the reference's semantic idea
    (for G1 = (acc + {H}) that is ADDITIVE: any acc + f(...) body, however deep
    its filler, is a specialisation/re-expression of G1, never novelty)."""
    inst = inst if inst is not None else T3D.instantiate(schema)
    acc_inst = [b for b in inst if accumulating(b)]
    novel = [b for b in acc_inst if vec(b) not in ref_span and fclass(b) not in exclude_classes]
    classes = sorted({fclass(b) for b in novel})
    return {"schema": schema, "instantiations": len(inst), "accumulating": len(acc_inst),
            "novel": len(novel), "novel_classes": classes, "novel_examples": novel[:6],
            "NEW_V2": len(novel) >= 2 and len(novel) >= 0.10 * max(1, len(acc_inst))}


# ---------------------------------------------------------------- structure
def _term(src):
    return I.normalise(I.parse(src.replace("{H}", "HOLEVAR")))


def _is_hole(t):
    return t[0] == "var:HOLEVAR" or (t[0].startswith("var") and "HOLEVAR" in t[0])


def _contains_hole(t):
    return _is_hole(t) or any(_contains_hole(a) for a in t[1])


def _match(p, t, bind):
    """pattern p (with one hole) against term t; binds the hole."""
    if _is_hole(p):
        if "h" in bind:
            return bind["h"] == t
        bind["h"] = t
        return True
    if p[0] != t[0] or len(p[1]) != len(t[1]):
        return False
    orders = [t[1]]
    if p[0] in ("add", "mul", "gcd") and len(t[1]) == 2:
        orders.append([t[1][1], t[1][0]])          # modulo commutativity
    for args in orders:
        trial = dict(bind)
        if all(_match(x, y, trial) for x, y in zip(p[1], args)):
            bind.clear()
            bind.update(trial)
            return True
    return False


def _subterms(t, depth=0):
    yield t, depth
    for a in t[1]:
        yield from _subterms(a, depth + 1)


ASSOC = ("add", "mul", "gcd")


def _flat(t, op):
    if t[0] == op:
        out = []
        for a in t[1]:
            out += _flat(a, op)
        return out
    return [t]


def _refines_assoc(s, g):
    """S refines G modulo associativity/commutativity at an associative root:
    G's non-hole operands are a sub-multiset of S's operands, and the rest of
    S's operands contain the hole (e.g. ((acc + {H}) + first) refines G1)."""
    if s[0] != g[0] or g[0] not in ASSOC:
        return False
    so, go = _flat(s, s[0]), _flat(g, g[0])
    g_fixed = [x for x in go if not _is_hole(x)]
    rest = list(so)
    for x in g_fixed:
        if x in rest:
            rest.remove(x)
        else:
            return False
    return len(go) - len(g_fixed) == 1 and any(_contains_hole(x) for x in rest) and not (
        len(rest) == 1 and _is_hole(rest[0]))


def relations(schema, ref_schema):
    """REFINES / COMPOSES of schema w.r.t. ref_schema (structural, normalised)."""
    s, g = _term(schema), _term(ref_schema)
    refines = composes = False
    b = {}
    if _match(g, s, b) and not _is_hole(b["h"]) and _contains_hole(b["h"]):
        refines = True
    if _refines_assoc(s, g):
        refines = True
    for sub, d in _subterms(s):
        if d == 0:
            continue
        b = {}
        if _match(g, sub, b) and _contains_hole(sub):
            composes = True
            break
    return {"REFINES": refines, "COMPOSES": composes, "EQUAL": s == g}


def verdict(schema, ref_schema, ref_span, inst=None):
    """FINAL novelty verdict relative to a reference schema: NEW iff NEW_V2 and
    the schema is neither equal to nor a refinement (specialisation) of it."""
    r = new_v2(schema, ref_span, inst)
    rel = relations(schema, ref_schema)
    r.update(rel)
    r["NEW"] = r["NEW_V2"] and not rel["REFINES"] and not rel["EQUAL"]
    return r


def verdict_full(schema, ref_schema, ref_span, ref_tspan, inst=None):
    """The RULER v2 FINAL verdict: NEW iff grid-level NEW_V2, trajectory-level
    NEW_TRAJ, and not EQUAL/REFINES to the reference schema."""
    inst = inst if inst is not None else T3D.instantiate(schema)
    r = verdict(schema, ref_schema, ref_span, inst)
    r.update(new_traj(schema, ref_tspan, inst))
    r["NEW_FINAL"] = r["NEW"] and r["NEW_TRAJ"]
    return r


# ---------------------------------------------------------------- trajectory level
import random as _random
_TRAJ_INPUTS = None


def _traj_inputs():
    global _TRAJ_INPUTS
    if _TRAJ_INPUTS is None:
        rng = _random.Random("APHRODITE/COMPOUNDING/RULER_V2/TRAJ/v1")
        _TRAJ_INPUTS = [[rng.randint(2, 30) for _ in range(rng.randint(2, 40))] + [rng.randint(3, 97)]
                        for _ in range(80)]
    return _TRAJ_INPUTS


@lru_cache(maxsize=None)
def traj(b, init):
    """Final accumulator of the fold ('fold', init, b, 'acc') on the task-domain
    battery: what the body actually DOES when folded, not what it does on a grid."""
    return tuple(FE.run_program(("fold", init, b, "acc"), x, True) for x in _traj_inputs())


def traj_nondegenerate(t):
    vals = [x for x in t if x is not None]
    return len(vals) == len(t) and len(set(vals)) >= 5


def traj_span(ref_bodies, inits=("0", "1")):
    return {traj(r, i) for r in ref_bodies for i in inits}


def new_traj(schema, ref_traj_span, inst=None, inits=("0", "1")):
    """NEW at trajectory level: accumulating instantiations whose folded
    trajectory (for some init) is non-degenerate and differs from every
    reference trajectory. Same proportion floor as NEW_V2."""
    inst = inst if inst is not None else T3D.instantiate(schema)
    acc_inst = [b for b in inst if accumulating(b)]
    novel = [b for b in acc_inst
             if any(traj_nondegenerate(traj(b, i)) and traj(b, i) not in ref_traj_span for i in inits)]
    return {"accumulating": len(acc_inst), "novel_traj": len(novel), "novel_traj_examples": novel[:4],
            "NEW_TRAJ": len(novel) >= 2 and len(novel) >= 0.10 * max(1, len(acc_inst))}


def reexpression_bodies(schema):
    out = []
    for r in reexpressions(schema):
        out += T3D.instantiate(r)
    return list(dict.fromkeys(out))


def extends_reach(schema, cov_vecs, inst=None):
    inst = inst if inst is not None else T3D.instantiate(schema)
    out = [b for b in inst if accumulating(b) and vec(b) not in cov_vecs]
    return {"EXTENDS_REACH": bool(out), "n_outside_coverage": len(out), "examples": out[:4]}


if __name__ == "__main__":
    import tier3e as T3E
    g1 = T3D.instantiate("(acc + {H})")
    sp = span_of_schema("(acc + {H})")
    for s in ["(acc + {H})", "(acc - {H})", "({H} + v)", "(acc * {H})", "math.gcd(abs(acc), abs({H}))",
              "(acc + math.gcd(abs({H}), abs(v)))", "((acc + {H}) * last)", "(0 // {H})", "({H} + first)"]:
        r = new_v2(s, sp)
        print("%-40s old_NEW=%-5s NEW_V2=%-5s acc=%3d novel=%3d %s rel=%s" % (
            s, T3E.semantically_new(s)["SEMANTICALLY_NEW"], r["NEW_V2"], r["accumulating"], r["novel"],
            r["novel_classes"], relations(s, "(acc + {H})")))

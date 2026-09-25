"""S1 gate fixtures (AMENDMENT 12 s6). Frozen at 287d208ea before this was written.

This module MAY read the catalogs -- it builds the tests. identity.py may not,
and the static audit (G-S1.6) checks that.

Every COLLAPSE fixture carries the argument for its equivalence under the
declared semantics. Every SEPARATION fixture carries an explicit input on which
the two programs differ, which the gate re-verifies with the evaluator rather
than trusting the comment.
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import basis_v4 as G                 # noqa: E402
import certify_expressivity as CX    # noqa: E402
import engine as E                   # noqa: E402
import identity as I                 # noqa: E402
import improver as T3A               # noqa: E402
import semantics as S                # noqa: E402
import tier3b as T3B                 # noqa: E402
import tier3c as T3C                 # noqa: E402
import tier3d as T3D                 # noqa: E402

C = I.C


# ---------------------------------------------------------------- catalog witnesses
def catalog_witnesses() -> List[Dict]:
    """EVERY declared witness program inside D_TASK_T3_v1, not a selection.
    ADDENDUM 2 s2/s4: the basis_v4 catalog (PLAIN, wider supports) is outside
    the domain and leaves; the Tier-3D catalog joins."""
    out = []
    for name, mod in (("tier3a", T3A), ("tier3b", T3B), ("tier3c", T3C), ("tier3d", T3D)):
        for fam in sorted(mod.FAMILY_SPEC):
            out.append({"catalog": name, "family": fam, "program": mod.witness(fam),
                        "trailing": True})
    return out


# ---------------------------------------------------------------- general constructions
def _subst_acc(t, repl):
    op, args = t
    if op == "var:acc":
        return repl
    return (op, [_subst_acc(a, repl) for a in args])


NEG_ACC = ("sub", [I.ZERO, ("var:acc", [])])


def negation_conjugate(prog) -> Tuple:
    """init' = 0 - init; body' = 0 - body[acc := 0 - acc]; final' = final[acc :=
    0 - acc]. EXACT under the declared semantics: acc' = -acc after every step,
    |acc'| = |acc| so the ceiling is crossed at the same step, and each primitive
    is evaluated on the same arguments, so failures coincide."""
    _, init, body, final = prog
    b = I.parse(body)
    return ("fold",
            I.to_src(("sub", [I.ZERO, I.parse(init)])),
            I.to_src(("sub", [I.ZERO, _subst_acc(b, NEG_ACC)])),
            I.to_src(_subst_acc(I.parse(final), NEG_ACC)))


def _mirror(t):
    op, args = t
    args = [_mirror(a) for a in args]
    if op in I.COMMUTATIVE:
        args = list(reversed(args))
    return (op, args)


def commuted(prog) -> Tuple:
    """Every commutative node's operands swapped (R2 in reverse). Exact."""
    return (prog[0],) + tuple(I.to_src(_mirror(I.parse(s))) for s in prog[1:])


def neutral_padded(prog) -> Tuple:
    """init * 1, 0 + body, final - 0 (R3 in reverse). Exact."""
    _, init, body, final = prog
    return ("fold", "(%s * 1)" % init, "(0 + %s)" % body, "(%s - 0)" % final)


# ---------------------------------------------------------------- historical
def _artifact(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def historical_observed() -> List[Dict]:
    """Every observed whole program recorded in the Tier-3A and Tier-3C
    artifacts, against its family's witness. The family of each observation
    follows from the artifact's recorded order (Tier 3A: two per meta-dev
    family; Tier 3C: three repetitions per OBSERVE family)."""
    out = []
    a = _artifact("TIER3A_ARTIFACT_2026-09-22.json")
    fams = a["meta_dev_families"]
    for k, prog in enumerate(a["observed_successful_programs"]):
        fam = fams[k // 2]
        out.append({"source": "tier3a", "family": fam, "observed": tuple(prog),
                    "witness": T3A.witness(fam)})
    c = _artifact("TIER3C_ARTIFACT_2026-09-22.json")
    used = c["observe_used"]
    for k, prog in enumerate(c["observed_programs"]):
        fam = used[k // 3]
        out.append({"source": "tier3c", "family": fam, "observed": tuple(prog),
                    "witness": T3C.witness(fam)})
    return out


# Tier-3A body equivalences (AMENDMENT 10 s1) and the Tier-3B observed-source ->
# representative pairs, as recorded. Lifted into whole programs only in contexts
# where the accumulator provably stays NON-NEGATIVE: init in {0, 1}, every input
# non-negative, and each body maps non-negative (acc, v) to a non-negative value.
TIER3A_BODY_ALIASES = [
    ("(acc + v)", "(v + acc)"),
    ("(acc * math.gcd(abs(v), abs(v)))", "(acc * v)"),
    ("math.gcd(abs(v), abs(math.gcd(abs(acc), abs(acc))))", "math.gcd(abs(acc), abs(v))"),
    ("math.gcd(abs(acc), abs((v + acc)))", "math.gcd(abs(acc), abs(v))"),
    ("(acc + math.gcd(abs(v), abs(v)))", "(acc + v)"),
]


def tier3b_body_aliases() -> List[Tuple[str, str]]:
    b = _artifact("TIER3B_ARTIFACT_2026-09-22.json")
    reps = b["observed_semantic_representatives"]
    by_sig = {S.signature(r): r for r in reps}
    return sorted({(src, by_sig[S.signature(src)]) for src in b["observed_sources"]
                   if by_sig[S.signature(src)] != src})


LIFT_INITS = ["0", "1"]


def lift_finals() -> List[str]:
    return sorted({T3B.FAMILY_SPEC[f][1] for f in T3B.META_DEV})


def historical_body_lifts() -> List[Dict]:
    out = []
    for origin, pairs in (("tier3a_body", TIER3A_BODY_ALIASES),
                          ("tier3b_body", tier3b_body_aliases())):
        for a, b in pairs:
            for init in LIFT_INITS:
                for final in lift_finals():
                    out.append({"source": origin, "a": ("fold", init, a, final),
                                "b": ("fold", init, b, final)})
    return out


# ---------------------------------------------------------------- collapse set
def collapse_pairs() -> List[Dict]:
    """(name, a, b, trailing, argument) for every G-S1.1 fixture."""
    out = []
    for w in catalog_witnesses():
        p, tr = w["program"], w["trailing"]
        tag = "%s/%s" % (w["catalog"], w["family"])
        out.append({"name": "negation_conjugate:" + tag, "a": p, "b": negation_conjugate(p),
                    "trailing": tr, "kind": "general",
                    "argument": "acc' = -acc invariant; |acc'| = |acc|; same primitive arguments"})
        out.append({"name": "commuted:" + tag, "a": p, "b": commuted(p), "trailing": tr,
                    "kind": "general", "argument": "R2 in reverse"})
        out.append({"name": "neutral_padded:" + tag, "a": p, "b": neutral_padded(p),
                    "trailing": tr, "kind": "general", "argument": "R3 in reverse"})
    for h in historical_observed():
        out.append({"name": "observed:%s/%s:%s" % (h["source"], h["family"],
                                                   json.dumps(list(h["observed"]))),
                    "a": h["witness"], "b": h["observed"], "trailing": True,
                    "kind": "historical",
                    "argument": "recorded observation of the family; equivalence argued "
                                "per program in AMENDMENT 12 fixtures notes"})
    for r in RECLASSIFIED_EQUIVALENT:
        out.append({"name": "reclassified:" + r["name"], "a": r["a"], "b": r["b"],
                    "trailing": True, "kind": "general", "argument": r["argument"]})
    for h in historical_body_lifts():
        out.append({"name": "lifted:%s:%s|%s" % (h["source"], h["a"][2], h["b"][2])
                            + ":init=%s:final=%s" % (h["a"][1], h["a"][3]),
                    "a": h["a"], "b": h["b"], "trailing": True, "kind": "historical",
                    "argument": "accumulator stays non-negative, where the body alias "
                                "holds as integer arithmetic"})
    return out


# ---------------------------------------------------------------- separation set
NEAR_NEIGHBOURS = [                      # ADDENDUM 2 s4: in-domain witnesses only
    {"name": "naive_sign_flip_across_floor_division",
     "a": ("fold", "first", "(acc // last)", "acc"),
     "b": ("fold", "(0 - first)", "(acc // last)", "(0 - acc)"),
     "trailing": True, "witness": [7, 2]},
    {"name": "naive_sign_flip_across_modulo",
     "a": ("fold", "0", "(acc - v)", "(acc % last)"),
     "b": ("fold", "0", "(acc - v)", "(0 - ((0 - acc) % last))"),
     "trailing": True, "witness": [5, 5, 3]},
    {"name": "guarded_pow_vs_unguarded_expansion",
     "a": ("fold", "0", "(acc + pow(v, last))", "acc"),
     "b": ("fold", "0", "(acc + (v * pow(v, (last - 1))))", "acc"),
     "trailing": True, "witness": [2, 2, 33]},
    {"name": "tier3b_alias_in_negative_accumulator_context",
     "a": ("fold", "(0 - first)", "(v + math.gcd(abs(acc), abs(acc)))", "acc"),
     "b": ("fold", "(0 - first)", "(v + acc)", "acc"),
     "trailing": True, "witness": [5, 2, 2]},
    {"name": "product_overflow_on_valid_input_vs_constant",
     "a": ("fold", "1", "(acc * v)", "(0 * acc)"),
     "b": ("expr", "0"),
     "trailing": True, "witness": [30] * 28 + [7]},
    {"name": "scale_conjugate_of_product_crosses_ceiling_earlier",
     "a": ("fold", "1", "(acc * v)", "(acc - first)"),
     "b": ("fold", "2", "(acc * v)", "((acc // 2) - first)"),
     "trailing": True, "witness": [30] * 27 + [5]},
    {"name": "failure_disposition_on_valid_input",
     "a": ("fold", "0", "(acc + v)", "acc"),
     "b": ("fold", "0", "(acc + (v + (0 * (last // (v - first)))))", "acc"),
     "trailing": True, "witness": [5, 5, 3]},
]

# ADDENDUM 2 s4: equivalent INSIDE D_TASK_T3_v1 (their only witnesses were
# impossible external inputs), so now asserted to COLLAPSE.
RECLASSIFIED_EQUIVALENT = [
    {"name": "offset_conjugate_of_sum",
     "a": ("fold", "0", "(acc + v)", "(acc * last)"),
     "b": ("fold", "first", "(acc + v)", "((acc - first) * last)"),
     "argument": "a sum of valid inputs is at most 6,000, far below the ceiling"},
    {"name": "identity_body_fold_vs_inlined",
     "a": ("fold", "first", "acc", "(acc - first)"),
     "b": ("expr", "(first - first)"),
     "argument": "valid inputs are at most 97, so the init never exceeds the ceiling"},
    {"name": "zero_times_first_div_last",
     "a": ("fold", "0", "(acc + v)", "acc"),
     "b": ("fold", "0", "(acc + v)", "(acc + (0 * (first // last)))"),
     "argument": "last >= 1 in the domain, so first // last never fails"},
]


# single-point mutations
PRIMS = sorted(E.PRIMITIVES)
_OP_FOR_PRIM = {"add": "add", "sub": "sub", "mul": "mul", "fdiv": "fdiv", "mod": "mod",
                "gcd": "gcd", "powr": "powr"}
SLOT_ATOMS = {1: G.INIT_ATOMS, 2: G.BODY_ATOMS, 3: G.FINAL_ATOMS}


def _atom_term(a: str):
    return ("const:" + a, []) if a.isdigit() else ("var:" + a, [])


def _point_mutations(t, atoms):
    """Every term obtained by replacing ONE node: an operator by another
    primitive, or a leaf by another atom of the slot."""
    op, args = t
    out = []
    if not args:
        for a in atoms:
            at = _atom_term(a)
            if at != t:
                out.append(at)
        return out
    for p in PRIMS:
        if p != op and len(args) == 2:
            out.append((p, args))
    for i, sub in enumerate(args):
        for m in _point_mutations(sub, atoms):
            out.append((op, args[:i] + [m] + args[i + 1:]))
    return out


def mutants(prog) -> List[Tuple]:
    out = []
    for slot in (1, 2, 3):
        t = I.parse(prog[slot])
        for m in _point_mutations(t, SLOT_ATOMS[slot]):
            q = list(prog)
            q[slot] = I.to_src(m)
            out.append(tuple(q))
    return out

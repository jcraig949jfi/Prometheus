"""Tier 3D: the S3/S4 catalog, generator qualification and the donor's
mechanical derivation (LGG over whole-program behavior classes).

Frozen by AMENDMENT_14_2026-09-23.md (commit 4a6bbf55d) before this was
written. The catalog below is copied verbatim from AMENDMENT 14 s1.
"""
import math
import random
import re
import statistics
from typing import Dict, List, Optional, Tuple

import basis_v4 as G
import engine as E
import fair as FR
import identity as I

# (body, final, init)
FAMILY_SPEC = {
    "md_a_sum_times_last":           ("(acc + v)", "(acc * last)", "0"),
    "md_b_sumsq_plus_first":         ("(acc + (v * v))", "(acc + first)", "0"),
    "md_c_prod_minus_first":         ("(acc * v)", "(acc - first)", "1"),
    "md_d_gcd_plus_last":            ("math.gcd(abs(acc), abs(v))", "(acc + last)", "0"),
    "md_e_negsum_times_first":       ("(acc - v)", "(acc * first)", "0"),
    "md_f_sumdec_plus_last":         ("(acc + (v - 1))", "(acc + last)", "0"),
    "md_g_prodinc_minus_first":      ("(acc * (v + 1))", "(acc - first)", "1"),
    "md_h_gcdinc_plus_first":        ("math.gcd(abs(acc), abs((v + 1)))", "(acc + first)", "0"),
    "tc_rel_sum_minus_last":         ("(acc + v)", "(acc - last)", "0"),
    "tc_rel_sumsq_times_first":      ("(acc + (v * v))", "(acc * first)", "0"),
    "tc_new_summod_times_first":     ("(acc + (v % last))", "(acc * first)", "0"),
    "tc_new_sumdiv_plus_first":      ("(acc + (v // last))", "(acc + first)", "0"),
    "tc_new_sumgcdlast_minus_first": ("(acc + math.gcd(abs(v), abs(last)))", "(acc - first)", "0"),
    "tc_new_sumscaled_minus_last":   ("(acc + (v * last))", "(acc - last)", "0"),
    "tc_new_negmod_plus_first":      ("(acc - (v % last))", "(acc + first)", "0"),
    "tc_new_gcdshift_times_first":   ("math.gcd(abs(acc), abs((v + last)))", "(acc * first)", "0"),
}
META_DEV = sorted(k for k in FAMILY_SPEC if k.startswith("md_"))
OBSERVE = META_DEV[:3]
VALIDATE = META_DEV[3:]
TRANSFER = sorted(k for k in FAMILY_SPEC if k.startswith("tc_"))
RELATED = [k for k in TRANSFER if k.startswith("tc_rel_")]
UNSEEN_BODY = [k for k in TRANSFER if k.startswith("tc_new_")]

CALIBRATION_DRAWS = 200
DEV_SIZES = (4, 6, 8, 12, 16, 24)
DISCRIM_THRESHOLD = 0.05
POOL_SIZE = 240


def witness(family: str) -> Tuple:
    body, final, init = FAMILY_SPEC[family]
    return ("fold", init, body, final)


def task(family: str, rng: random.Random, length_range=G.SEARCH_LENGTHS):
    lo, hi = length_range
    xs = [rng.randint(2, 30) for _ in range(rng.randint(lo, hi))]
    m = rng.randint(3, 97)
    gold = G.run_program(witness(family), xs + [m], True)
    return (("Family %s over: " % family) + ", ".join(map(str, xs)) + " with %d." % m,
            str(gold))


def tasks(family: str, n: int, seed: int, length_range=G.SEARCH_LENGTHS) -> List[Dict]:
    rng = random.Random((seed, family, length_range).__str__())
    out = []
    for i in range(n):
        p, g = task(family, rng, length_range)
        out.append({"family": family, "prompt": p, "gold": g,
                    "key": "%s-%d-%d" % (family, seed, i)})
    return out


def nums_of(t) -> List[int]:
    return [int(x) for x in re.findall(r"-?\d+", t["prompt"])]


# ---------------------------------------------------------------- G2 (AMENDMENT 11 s3, unchanged)
_REACHABLE: Optional[List[Tuple]] = None


def reachable_programs() -> List[Tuple]:
    """The frozen Tier-3C rule, unchanged: the PRISTINE entry space with bodies
    deduplicated by the AMENDMENT-10 body signature."""
    global _REACHABLE
    if _REACHABLE is None:
        import tier3c as T3C
        _REACHABLE = T3C.reachable_programs()
    return _REACHABLE


def qualify_generator(family: str) -> Dict:
    target = witness(family)
    pool = tasks(family, POOL_SIZE, E.dev_entropy("T3D-pool-" + family, 0))
    probes = [nums_of(t) for t in pool]
    tvals = tuple(G.run_program(target, nums, True) for nums in probes)
    wrong = {}
    for p in reachable_programs():
        vals = tuple(G.run_program(p, nums, True) for nums in probes)
        if vals == tvals or vals in wrong:
            continue
        wrong[vals] = p
    wrong_vals = list(wrong)
    rng = random.Random(E.dev_entropy("T3D-draws-" + family, 0))
    rows = []
    for size in DEV_SIZES:
        survivors = []
        for _d in range(CALIBRATION_DRAWS):
            idx = rng.sample(range(POOL_SIZE), size)
            survivors.append(sum(1 for vals in wrong_vals
                                 if all(vals[i] is not None and vals[i] == tvals[i] for i in idx)))
        mean = statistics.mean(survivors)
        upper = mean + 1.96 * statistics.pstdev(survivors) / math.sqrt(len(survivors))
        rows.append({"dev_size": size, "mean_surviving_wrong_classes": round(mean, 4),
                     "upper95": round(upper, 4), "meets_threshold": bool(upper < DISCRIM_THRESHOLD)})
        if upper < DISCRIM_THRESHOLD:
            return {"family": family, "qualified_dev_size": size,
                    "distinct_wrong_classes_on_pool": len(wrong_vals),
                    "calibration": rows, "QUALIFIED": True}
    return {"family": family, "qualified_dev_size": None,
            "distinct_wrong_classes_on_pool": len(wrong_vals), "calibration": rows,
            "QUALIFIED": False}


# ---------------------------------------------------------------- D3: class members
def member_space() -> List[Tuple]:
    """M = H1 x H2 x FINAL_SPACE, the PRISTINE entry (AMENDMENT 14 D3)."""
    return [("fold", i, b, f) for i in G.H1_SPACE for b in G.H2_SPACE for f in G.FINAL_SPACE]


def class_members(observed: Tuple, examples: List[Dict]) -> List[Tuple]:
    """Every program in M with the observed program's behavior_id: filtered on
    the observed program's development examples, confirmed on the full B1."""
    parsed = [(nums_of(t), t["gold"]) for t in examples]
    target = I.behavior_id(observed, True)
    out = []
    for p in member_space():
        ok = True
        for nums, gold in parsed:
            got = G.run_program(p, nums, True)
            if got is None or str(got) != gold:
                ok = False
                break
        if ok and I.behavior_id(p, True) == target:
            out.append(p)
    return out


# ---------------------------------------------------------------- D4: LGG
HOLE = ("hole", [])


def lgg(a, b, table=None):
    """Standard first-order least general generalisation of two terms. The
    same differing pair of subterms maps to the same hole."""
    if table is None:
        table = {}
    if a == b:
        return a, table
    if a[0] == b[0] and len(a[1]) == len(b[1]) and a[1]:
        kids = []
        for x, y in zip(a[1], b[1]):
            k, table = lgg(x, y, table)
            kids.append(k)
        return (a[0], kids), table
    key = (I.term_str(a), I.term_str(b))
    if key not in table:
        table[key] = ("hole:%d" % len(table), [])
    return table[key], table


def schema_src(t) -> str:
    op, args = t
    if op.startswith("hole"):
        return "{H}"
    if op.startswith("var:") or op.startswith("const:"):
        return I.to_src(t)
    return _emit(op, [schema_src(a) for a in args])


def _emit(op, parts):
    if op in I.INFIX:
        return "(%s %s %s)" % (parts[0], I.INFIX[op], parts[1])
    if op == "gcd":
        return "math.gcd(abs(%s), abs(%s))" % (parts[0], parts[1])
    if op == "powr":
        return "pow(%s, %s)" % (parts[0], parts[1])
    if op == "abs":
        return "abs(%s)" % parts[0]
    raise ValueError(op)


def derive_schemas(member_bodies_by_class: List[List[str]]) -> List[Dict]:
    """D4: LGG over every pair of DISTINCT classes and every pair of their
    members' bodies (S1 structural form). Keep exactly-one-hole, non-root."""
    found = {}
    for ci in range(len(member_bodies_by_class)):
        for cj in range(ci + 1, len(member_bodies_by_class)):
            for a in member_bodies_by_class[ci]:
                ta = I.normalise(I.parse(a))
                for b in member_bodies_by_class[cj]:
                    tb = I.normalise(I.parse(b))
                    g, table = lgg(ta, tb)
                    if len(table) != 1 or g[0].startswith("hole"):
                        continue
                    s = schema_src(g)
                    found.setdefault(s, []).append((ci, cj, a, b))
    return [{"schema": s, "witness_pairs": v[:4], "n_pairs": len(v)}
            for s, v in sorted(found.items())]


# the in-space body for each structural form (the Tier-3C filler rule: only
# bodies inside BODY_SPACE; a structurally identical in-space body stands in)
_STRUCT_TO_BODY: Optional[Dict[str, str]] = None


def in_space_body(src: str) -> Optional[str]:
    global _STRUCT_TO_BODY
    if _STRUCT_TO_BODY is None:
        _STRUCT_TO_BODY = {}
        for b in G.BODY_SPACE:
            _STRUCT_TO_BODY.setdefault(I.term_str(I.normalise(I.parse(b))), b)
    return _STRUCT_TO_BODY.get(I.term_str(I.normalise(I.parse(src))))


def instantiate(schema: str) -> List[str]:
    out = []
    for f in FR.LEVEL1:
        b = in_space_body(schema.replace("{H}", f))
        if b is not None:
            out.append(b)
    return list(dict.fromkeys(out))

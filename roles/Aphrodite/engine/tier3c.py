"""Tier 3C: semantic abstraction as improver heredity.

Frozen by AMENDMENT_11_2026-09-22.md (commit 13fd1d9b9).

The donor may form HOLE-BEARING SCHEMAS by anti-unifying the semantic classes
of its own successful bodies. A schema like add(acc, H) covers bodies the
donor never saw, which is the only mechanism here by which cross-family
transfer can occur without memorisation.
"""
import hashlib
import json
import math
import random
import re
import statistics
from typing import Dict, List, Optional, Tuple

import basis_v4 as G
import engine as E
import semantics as S

# ---------------------------------------------------------------- catalogs
# (body, final, init). OBSERVE / VALIDATE split by the frozen lexicographic
# rule: the first half of the sorted meta-dev names are OBSERVE.
FAMILY_SPEC = {
    # meta-development
    "md_a_sum_times_last":      ("(acc + v)", "(acc * last)", "0"),
    "md_b_sumsq_plus_first":    ("(acc + (v * v))", "(acc + first)", "0"),
    "md_c_prod_minus_first":    ("(acc * v)", "(acc - first)", "1"),
    "md_d_gcd_plus_last":       ("math.gcd(abs(acc), abs(v))", "(acc + last)", "0"),
    # transfer challenge -- RELATED (body class the donor can observe)
    "tc_rel_sum_minus_first":   ("(acc + v)", "(acc - first)", "0"),
    "tc_rel_gcd_times_first":   ("math.gcd(abs(acc), abs(v))", "(acc * first)", "0"),
    # transfer challenge -- UNSEEN BODY (never observed, but inside add(acc,H))
    "tc_new_summod_times_first": ("(acc + (v % last))", "(acc * first)", "0"),
    "tc_new_sumdiv_plus_first":  ("(acc + (v // last))", "(acc + first)", "0"),
    "tc_new_sumgcdlast_minus_first": ("(acc + math.gcd(abs(v), abs(last)))",
                                      "(acc - first)", "0"),
}
META_DEV = sorted(k for k in FAMILY_SPEC if k.startswith("md_"))
OBSERVE = META_DEV[:2]                      # frozen lexicographic split
VALIDATE = META_DEV[2:]
TRANSFER = sorted(k for k in FAMILY_SPEC if k.startswith("tc_"))
RELATED = [k for k in TRANSFER if k.startswith("tc_rel_")]
UNSEEN_BODY = [k for k in TRANSFER if k.startswith("tc_new_")]

CALIBRATION_DRAWS = 200
DEV_SIZES = (4, 6, 8, 12, 16, 24)
DISCRIM_THRESHOLD = 0.05
DESCENDANT_HORIZON = 64
SHAM_COUNT = 8


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


# ---------------------------------------------------------------- generator qualification
_REACHABLE: Dict[str, List[Tuple]] = {}


def reachable_programs() -> List[Tuple]:
    """FROZEN rule: the PRISTINE entry space, deduplicated by SEMANTIC class of
    the body (the init and final spaces are enumerated in full)."""
    key = "all"
    if key not in _REACHABLE:
        idx = S.SemanticIndex().add_all(G.H2_SPACE)
        bodies = sorted(idx.representative(sig) for sig in idx.classes())
        _REACHABLE[key] = [("fold", i, b, f)
                           for i in G.H1_SPACE for b in bodies for f in G.FINAL_SPACE]
    return _REACHABLE[key]


POOL_SIZE = 240


def qualify_generator(family: str) -> Dict:
    """Qualify the GENERATOR, not one sample: how often does a wrong semantic
    class survive an INDEPENDENTLY DRAWN development set?

    Each reachable program is evaluated once over a frozen instance pool; a
    draw is then a subset of pool indices, and a wrong class survives that draw
    when it agrees with the target on every index in it. Behaviourally
    identical to re-evaluating per draw, without the redundant evaluations
    that made the direct form intractable.
    """
    target = witness(family)
    pool = tasks(family, POOL_SIZE, E.dev_entropy("T3C-pool-" + family, 0))
    probes = [nums_of(t) for t in pool]
    tvals = tuple(G.run_program(target, nums, True) for nums in probes)

    wrong = {}
    for p in reachable_programs():
        vals = tuple(G.run_program(p, nums, True) for nums in probes)
        if vals == tvals or vals in wrong:
            continue
        wrong[vals] = p
    wrong_vals = list(wrong)

    rng = random.Random(E.dev_entropy("T3C-draws-" + family, 0))
    rows = []
    for size in DEV_SIZES:
        survivors = []
        for _d in range(CALIBRATION_DRAWS):
            idx = rng.sample(range(POOL_SIZE), size)
            n = 0
            for vals in wrong_vals:
                if all(vals[i] is not None and vals[i] == tvals[i] for i in idx):
                    n += 1
            survivors.append(n)
        mean = statistics.mean(survivors)
        sd = statistics.pstdev(survivors)
        upper = mean + 1.96 * sd / math.sqrt(len(survivors))
        rows.append({"dev_size": size, "mean_surviving_wrong_classes": round(mean, 4),
                     "upper95": round(upper, 4), "draws": CALIBRATION_DRAWS,
                     "meets_threshold": bool(upper < DISCRIM_THRESHOLD)})
        if upper < DISCRIM_THRESHOLD:
            return {"family": family, "qualified_dev_size": size,
                    "distinct_wrong_classes_on_pool": len(wrong_vals),
                    "calibration": rows, "QUALIFIED": True}
    return {"family": family, "qualified_dev_size": None,
            "distinct_wrong_classes_on_pool": len(wrong_vals),
            "calibration": rows, "QUALIFIED": False}


# ---------------------------------------------------------------- schemas
LEVEL1 = [a for a in G.BODY_ATOMS] + [tmpl.format(a, b)
                                      for _n, (_f, tmpl) in sorted(E.PRIMITIVES.items())
                                      for a in G.BODY_ATOMS for b in G.BODY_ATOMS]


def expand_entry(entry: Dict) -> List[str]:
    """Concrete bodies plus every instantiation of the entry's schemas."""
    out = list(entry.get("bodies", []))
    for sch in entry.get("schemas", []):
        for f in LEVEL1:
            body = sch.replace("{H}", f)
            if body in G.BODY_SPACE:
                out.append(body)
    for spec in entry.get("op_schemas", []):
        out.extend(expand_operator_schema(spec))
    seen, uniq = set(), []
    for b in out:
        if b not in seen:
            seen.add(b)
            uniq.append(b)
    return uniq


OP_HOLE = "{OP}"


def antiunify_operator(a: str, b: str) -> Optional[str]:
    """Same arguments, different primitive -> an OPERATOR hole (AMENDMENT 11
    s1: OP(acc, v)). Expands to one body per declared primitive."""
    ta, tb = S.to_term(a), S.to_term(b)
    if ta[0] == tb[0] or ta[1] != tb[1] or len(ta[1]) != 2:
        return None
    return "%s|%s" % (S.term_str(ta[1][0]), S.term_str(ta[1][1]))


def expand_operator_schema(spec: str) -> List[str]:
    left, right = spec.split("|", 1)
    out = []
    for _n, (_f, tmpl) in sorted(E.PRIMITIVES.items()):
        body = tmpl.format(left, right)
        if body in G.BODY_SPACE:
            out.append(body)
    return out


def antiunify_bodies(a: str, b: str) -> Optional[str]:
    """Generalise two bodies into a schema with ONE hole, or None.

    Operates on canonical structural forms so that spelling differences do not
    block generalisation, then emits a template in concrete syntax."""
    ta, tb = S.to_term(a), S.to_term(b)
    if ta[0] != tb[0] or len(ta[1]) != len(tb[1]) or not ta[1]:
        return None
    diffs = [i for i in range(len(ta[1])) if ta[1][i] != tb[1][i]]
    if len(diffs) != 1:
        return None
    i = diffs[0]
    parts = []
    for j, sub in enumerate(ta[1]):
        parts.append("{H}" if j == i else S.term_str(sub))
    op = ta[0]
    tmpl = dict((n, t) for n, (_f, t) in E.PRIMITIVES.items()).get(op)
    if tmpl is None:
        return None
    schema = tmpl.format(parts[0], parts[1])
    return schema if "{H}" in schema else None

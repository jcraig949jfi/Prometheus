"""Tier 3B: frozen catalogs, discrimination qualification, sham distribution.

AMENDMENT 10 (169dc6c67) froze every constant here before it was written.
Semantic classes come from semantics.py; source strings are provenance only.
"""
import hashlib
import json
import random
import re
from typing import Dict, List, Optional, Tuple

import basis_v4 as G
import engine as E
import semantics as S

# ---------------------------------------------------------------- catalogs (frozen)
FAMILY_SPEC = {
    # META-DEV
    "md_sum_times_last":         ("(acc + v)", "(acc * last)", "0"),
    "md_prod_plus_first":        ("(acc * v)", "(acc + first)", "1"),
    "md_gcd_minus_first":        ("math.gcd(abs(acc), abs(v))", "(acc - first)", "0"),
    "md_sumsq_plus_last":        ("(acc + (v * v))", "(acc + last)", "0"),
    # META-TRIBUNAL: 2 TRANSFER + 3 UNSEEN-BODY
    "mt_sum_minus_last":         ("(acc + v)", "(acc - last)", "0"),
    "mt_gcd_plus_first":         ("math.gcd(abs(acc), abs(v))", "(acc + first)", "0"),
    "mt_summodlast_times_first": ("(acc + (v % last))", "(acc * first)", "0"),
    "mt_sumdivlast_minus_first": ("(acc + (v // last))", "(acc - first)", "0"),
    "mt_gcdsq_plus_last":        ("math.gcd(abs(acc), abs((v * v)))", "(acc + last)", "0"),
}
META_DEV = sorted(k for k in FAMILY_SPEC if k.startswith("md_"))
META_TRIBUNAL = sorted(k for k in FAMILY_SPEC if k.startswith("mt_"))
TRANSFER = ["mt_gcd_plus_first", "mt_sum_minus_last"]
UNSEEN_BODY = ["mt_gcdsq_plus_last", "mt_sumdivlast_minus_first",
               "mt_summodlast_times_first"]

DEV_CAP = 16                     # AMENDMENT 10 s2
DEV_START = 4
SHAM_COUNT = 8                   # AMENDMENT 10 s3
SHAM_BODIES = 8
DESCENDANT_HORIZON = 64          # AMENDMENT 10 s9


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


# ---------------------------------------------------------------- semantic body space
_BODY_INDEX: Optional[S.SemanticIndex] = None


def body_index() -> S.SemanticIndex:
    """The declared body space, collapsed into semantic classes ONCE."""
    global _BODY_INDEX
    if _BODY_INDEX is None:
        _BODY_INDEX = S.SemanticIndex().add_all(G.H2_SPACE + G.BODY_SPACE)
    return _BODY_INDEX


# ---------------------------------------------------------------- discrimination (s2)
def program_semantic_key(prog, probes: List[List[int]]) -> Tuple:
    """A program's behaviour on a frozen probe set of task inputs."""
    return tuple(G.run_program(prog, nums, True) for nums in probes)


def reachable_programs(family: str) -> List[Tuple]:
    """FROZEN exhaustive rule: the PRISTINE library entry space -- the
    programs reachable under the declared grammar within the declared budget.
    Deduplicated by SEMANTIC class of the (init, body, final) triple."""
    inits, finals = G.H1_SPACE, G.FINAL_SPACE
    bodies = [body_index().representative(sig)
              for sig in S.SemanticIndex().add_all(G.H2_SPACE).classes()]
    out = []
    for i in inits:
        for b in bodies:
            for f in finals:
                out.append(("fold", i, b, f))
    return out


def qualify_family(family: str, pool_seed: int) -> Dict:
    """Grow the development set by the frozen greedy max-split rule until the
    false-positive basin is empty, or declare the family UNSUITABLE."""
    target = witness(family)
    pool = tasks(family, 64, pool_seed)                 # frozen candidate pool
    probes = [nums_of(t) for t in pool]
    target_key = program_semantic_key(target, probes)

    progs = reachable_programs(family)
    classes: Dict[Tuple, Tuple] = {}
    for p in progs:
        k = program_semantic_key(p, probes)
        classes.setdefault(k, p)
    incorrect = [k for k in classes if k != target_key]

    dev_idx = list(range(DEV_START))
    history = []

    def survivors(idxs):
        out = []
        for k in incorrect:
            if all(k[i] == target_key[i] for i in idxs):
                out.append(k)
        return out

    surv = survivors(dev_idx)
    history.append({"dev_size": len(dev_idx), "false_positive_basin": len(surv)})
    while surv and len(dev_idx) < DEV_CAP:
        best_i, best_kill = None, -1
        for i in range(len(pool)):
            if i in dev_idx:
                continue
            kill = sum(1 for k in surv if k[i] != target_key[i])
            if kill > best_kill:
                best_i, best_kill = i, kill
        if best_kill <= 0:
            break
        dev_idx.append(best_i)
        surv = survivors(dev_idx)
        history.append({"dev_size": len(dev_idx), "false_positive_basin": len(surv),
                        "added_instance": best_i, "eliminated": best_kill})

    return {
        "family": family,
        "reachable_semantic_classes": len(classes),
        "incorrect_classes": len(incorrect),
        "initial_false_positive_basin": history[0]["false_positive_basin"],
        "final_false_positive_basin": len(surv),
        "development_size": len(dev_idx),
        "development_indices": dev_idx,
        "history": history,
        "SUITABLE": len(surv) == 0,
        "pool_seed": pool_seed,
    }


def dev_instances(family: str, qual: Dict, seed: int) -> List[Dict]:
    """The qualified development battery, re-drawn per recipient from that
    recipient's own entropy but with the QUALIFIED SIZE."""
    return tasks(family, qual["development_size"], seed)


# ---------------------------------------------------------------- sham distribution (s3)
def sham_libraries(base_entries: List[Dict]) -> List[Dict]:
    """EIGHT matched shams, each 8 body SEMANTIC CLASSES drawn uniformly under
    a frozen per-sham seed. No hand labelling, no filtering on usefulness."""
    idx = S.SemanticIndex().add_all(G.H2_SPACE)
    reps = sorted(idx.representatives())
    out = []
    for k in range(SHAM_COUNT):
        rng = random.Random(int(hashlib.sha256(
            ("APHRODITE/TIER3B/SHAM/v1/%d" % k).encode()).hexdigest()[:16], 16))
        bodies = sorted(rng.sample(reps, SHAM_BODIES))
        entries = [{"name": "sham_%d" % k, "inits": ["0", "1"], "bodies": bodies,
                    "finals": list(G.FINAL_SPACE)}] + base_entries
        canon = json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()
        out.append({"index": k, "entries": entries,
                    "sha256": hashlib.sha256(canon).hexdigest(),
                    "bodies": bodies})
    return out

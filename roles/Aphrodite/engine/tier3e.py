"""Tier 3E: the treatment-blind catalog, body mechanism keys and the
SEMANTICALLY_NEW test for the G1 -> G2 recursion assay.

Frozen by AMENDMENT_15_2026-09-24.md (commit aaae70067) before this was
written. The catalog is GENERATED (generate_catalog) and stored in
T3E_CATALOG_2026-09-24.json; the provider functions below read it.
"""
import hashlib
import json
import math
import random
import re
import statistics
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import basis_v4 as G
import engine as E
import identity as I
import tier3d as T3D

HERE = Path(__file__).resolve().parent
CATALOG_FILE = HERE / "T3E_CATALOG_2026-09-24.json"
STRATA = ["add", "sub", "mul", "fdiv", "mod", "gcd", "powr"]
K = 4
LETTERS = "abcd"
C = 10 ** 40

FAMILY_SPEC: Dict[str, Tuple[str, str, str]] = {}
ROLE: Dict[str, str] = {}
STRATUM: Dict[str, str] = {}


def _load():
    if CATALOG_FILE.exists():
        cat = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
        for f in cat["families"]:
            FAMILY_SPEC[f["name"]] = (f["body"], f["final"], f["init"])
            ROLE[f["name"]] = f["role"]
            STRATUM[f["name"]] = f["stratum"]


_load()


def witness(family: str) -> Tuple:
    body, final, init = FAMILY_SPEC[family]
    return ("fold", init, body, final)


def task(family, rng, length_range=G.SEARCH_LENGTHS):
    lo, hi = length_range
    xs = [rng.randint(2, 30) for _ in range(rng.randint(lo, hi))]
    m = rng.randint(3, 97)
    gold = G.run_program(witness(family), xs + [m], True)
    return (("Family %s over: " % family) + ", ".join(map(str, xs)) + " with %d." % m, str(gold))


def tasks(family, n, seed, length_range=G.SEARCH_LENGTHS):
    rng = random.Random((seed, family, length_range).__str__())
    out = []
    for i in range(n):
        p, g = task(family, rng, length_range)
        out.append({"family": family, "prompt": p, "gold": g, "key": "%s-%d-%d" % (family, seed, i)})
    return out


def nums_of(t):
    return [int(x) for x in re.findall(r"-?\d+", t["prompt"])]


def by_role(role):
    return sorted(f for f in FAMILY_SPEC if ROLE[f] == role)


# ---------------------------------------------------------------- generation (s3)
def _top_op(body: str) -> Optional[str]:
    t = I.parse(body)
    return t[0] if t[1] else None


def _mentions(src, name):
    return re.search(r"\b%s\b" % name, src) is not None


def _probe_sets():
    rng = random.Random(I._seed("APHRODITE/T3E/PROBES/v1"))
    order = []
    for _ in range(50):
        xs = [rng.randint(2, 30) for _ in range(rng.randint(3, 30))]
        order.append((xs, rng.randint(1, 97)))
    trib = []
    lengths = list(range(2, 61)) + [80, 150, 200]
    for _ in range(120):
        L = rng.choice(lengths)
        trib.append([rng.randint(2, 30) for _ in range(L)] + [rng.randint(1, 97)])
    return order, trib, rng


def generate_catalog() -> Dict:
    order, trib, _ = _probe_sets()
    rng = random.Random(I._seed("APHRODITE/T3E/CATALOG/v1"))
    bodies = {op: [b for b in G.BODY_SPACE if _top_op(b) == op and _mentions(b, "acc")
                   and _mentions(b, "v")] for op in STRATA}
    finals = [f for f in G.FINAL_SPACE if _mentions(f, "acc")]
    accepted, seen_bids, log = [], set(), {op: {"tried": 0, "rejected": {}} for op in STRATA}
    for op in STRATA:
        got = []
        while len(got) < K:
            log[op]["tried"] += 1
            if log[op]["tried"] > 20000:
                break
            p = ("fold", rng.choice(G.H1_SPACE), rng.choice(bodies[op]), rng.choice(finals))
            why = None
            for xs, m in order:                                       # F1
                perm = xs[1:]
                random.Random(len(xs) * 7919 + m).shuffle(perm)
                if G.run_program(p, xs + [m], True) != G.run_program(p, [xs[0]] + perm + [m], True):
                    why = "F1_order"
                    break
            if why is None and any(G.run_program(p, inp, True) is None for inp in trib):
                why = "F2_fails"                                      # F2
            if why is None:                                           # F3
                by_q = {}
                for inp in trib:
                    by_q.setdefault(inp[-1], set()).add(G.run_program(p, inp, True))
                if not any(len(v) > 1 for v in by_q.values()):
                    why = "F3_constant"
            if why is None:                                           # F4
                bid = I.behavior_id(p, True)
                if bid in seen_bids:
                    why = "F4_duplicate"
            if why:
                log[op]["rejected"][why] = log[op]["rejected"].get(why, 0) + 1
                continue
            seen_bids.add(bid)
            got.append(p)
        roles = ["OBSERVE", "VALIDATE", "TRANSFER", "TRANSFER"][:len(got)]
        random.Random(I._seed("APHRODITE/T3E/ASSIGN/v1/" + op)).shuffle(roles)
        for k, (p, role) in enumerate(zip(got, roles)):
            accepted.append({"name": "tE_%s_%s" % (op, LETTERS[k]), "stratum": op, "role": role,
                             "init": p[1], "body": p[2], "final": p[3]})
    return {"families": accepted, "generation_log": log, "K": K, "strata": STRATA}


# ---------------------------------------------------------------- G2 qualification
POOL_SIZE, DRAWS, DEV_SIZES, THRESH = 240, 200, (4, 6, 8, 12, 16, 24), 0.05


def qualify_generator(family):
    target = witness(family)
    pool = tasks(family, POOL_SIZE, E.dev_entropy("T3E-pool-" + family, 0))
    probes = [nums_of(t) for t in pool]
    tvals = tuple(G.run_program(target, n, True) for n in probes)
    wrong = {}
    for p in T3D.reachable_programs():
        vals = tuple(G.run_program(p, n, True) for n in probes)
        if vals == tvals or vals in wrong:
            continue
        wrong[vals] = p
    wv = list(wrong)
    rng = random.Random(E.dev_entropy("T3E-draws-" + family, 0))
    rows = []
    for size in DEV_SIZES:
        surv = []
        for _ in range(DRAWS):
            idx = rng.sample(range(POOL_SIZE), size)
            surv.append(sum(1 for v in wv if all(v[i] is not None and v[i] == tvals[i] for i in idx)))
        mean = statistics.mean(surv)
        up = mean + 1.96 * statistics.pstdev(surv) / math.sqrt(len(surv))
        rows.append({"dev_size": size, "mean": round(mean, 4), "upper95": round(up, 4)})
        if up < THRESH:
            return {"family": family, "qualified_dev_size": size, "calibration": rows, "QUALIFIED": True}
    return {"family": family, "qualified_dev_size": None, "calibration": rows, "QUALIFIED": False}


# ---------------------------------------------------------------- mechanism keys (s5)
GRID_ACC = (-10 ** 6, -97, -30, -7, -2, -1, 0, 1, 2, 7, 30, 97, 10 ** 6)
GRID_V, GRID_FIRST, GRID_LAST = (2, 3, 7, 30), (2, 5, 30), (1, 2, 7, 33, 97)
_KEY: Dict[str, str] = {}


def _body_val(code, acc, v, first, last):
    try:
        out = eval(code, G._G, {"acc": acc, "v": v, "first": first, "last": last})
        if out is None or abs(out) > C:
            return None
        return out
    except Exception:          # noqa: BLE001
        return None


def body_key(body: str) -> str:
    """{sig(b), sig(b*)}, b*(acc, ...) = 0 - b(0 - acc, ...), over the frozen grid."""
    k = _KEY.get(body)
    if k is None:
        code = G._code(body)
        sig, conj = [], []
        for a in GRID_ACC:
            for v in GRID_V:
                for f in GRID_FIRST:
                    for l in GRID_LAST:
                        x = _body_val(code, a, v, f, l)
                        y = _body_val(code, -a, v, f, l)
                        sig.append("F" if x is None else str(x))
                        conj.append("F" if y is None else str(-y))
        hs = sorted(hashlib.sha256(json.dumps(s).encode()).hexdigest() for s in (sig, conj))
        k = hs[0] + hs[1]
        _KEY[body] = k
    return k


_G1M = None


def g1_mechanisms() -> set:
    global _G1M
    if _G1M is None:
        _G1M = {body_key(b) for b in T3D.instantiate("(acc + {H})")}
    return _G1M


def semantically_new(schema: str) -> Dict:
    inst = T3D.instantiate(schema)
    new = [b for b in inst if _mentions(b, "v") and body_key(b) not in g1_mechanisms()]
    return {"schema": schema, "instantiations": len(inst), "new_mechanism_bodies": new[:12],
            "n_new_mechanism_bodies": len(new), "SEMANTICALLY_NEW": bool(new)}

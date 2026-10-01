"""SPIKE K1 -- task-supply census (Block D). Read-only forensics; no frozen
artifact is touched. Two layers:

  (1) BODY LEVEL, exhaustive over the 10,842 G4 bodies: is the fold body
      right-commutative, b(b(a,x),y) == b(b(a,y),x), on a grid (the property
      the tribunal's metamorphic permutation check demands of every fold)?
      Does it mention first/last/constants? Is it a G1 (acc + {H}) mechanism?
  (2) WITNESS LEVEL, a seeded sample of the AMENDMENT-16/17 candidate
      distribution (N per stratum, forensic seed, never a catalog seed): does
      the witness pass the tribunal's STRUCTURAL preconditions (permutation
      invariance on the tribunal's own probe shape, no None/ceiling at
      extrapolation lengths 20-60 and stress length 200, counterexample
      shapes), is it non-degenerate (>= 3 distinct outputs on 60 random
      inputs, output depends on a non-first list element), and is its body a
      G1 mechanism?
Q2 (generator qualification) and Q4 (headroom) are not re-run here; the
foundry evals file gives their observed rates.
"""
import json
import os
import random
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ENG = Path(__file__).resolve().parents[3] / "engine"
sys.path.insert(0, str(ENG))
sys.path.insert(0, str(ENG / "accel"))
import basis_v4 as G      # noqa: E402
import fasteval as FE     # noqa: E402
import identity as I      # noqa: E402
import tier3e as T3E      # noqa: E402

STRATA = ["add", "sub", "mul", "fdiv", "mod", "gcd", "powr"]
N_PER = int(os.environ.get("K1_N", "1500"))
GRID = [(a, x, y) for a in (-7, 0, 1, 2, 5, 13) for x in (2, 3, 7, 11, 30) for y in (2, 4, 9, 17, 29)]
FL = [(f, l) for f in (2, 5, 17) for l in (1, 3, 41)]


def body_fn(b):
    return FE.fn(b)


def right_commutative(b):
    f = body_fn(b)
    bad = 0
    for a, x, y in GRID:
        for fi, la in FL:
            try:
                u = f(f(a, x, fi, la), y, fi, la)
            except Exception:  # noqa: BLE001
                u = "E"
            try:
                w = f(f(a, y, fi, la), x, fi, la)
            except Exception:  # noqa: BLE001
                w = "E"
            if u != w:
                bad += 1
    return bad == 0


def mentions(src, n):
    import re
    return re.search(r"\b%s\b" % n, src) is not None


def body_row(b):
    return {"body": b, "op": T3E._top_op(b), "rc": right_commutative(b),
            "acc_v": mentions(b, "acc") and mentions(b, "v"),
            "uses_fl": mentions(b, "first") or mentions(b, "last"),
            "g1": T3E.body_key(b) in T3E.g1_mechanisms() if (mentions(b, "acc") and mentions(b, "v")) else None}


def witness_row(p):
    rng = random.Random(repr(p))
    run = lambda xs, m: FE.run_program(p, xs + [m], True)
    # tribunal metamorphic shape: len 5-30, perm of xs[1:], m 3-97
    inv = True
    for _ in range(25):
        xs = [rng.randint(2, 30) for _ in range(rng.randint(5, 30))]
        m = rng.randint(3, 97)
        perm = xs[1:]
        rng.shuffle(perm)
        a, b = run(xs, m), run([xs[0]] + perm, m)
        if a is None or b is None or a != b:
            inv = False
            break
    ext_none = sum(run([rng.randint(2, 30) for _ in range(rng.randint(20, 60))], rng.randint(3, 97)) is None
                   for _ in range(20))
    st_none = sum(run([rng.randint(2, 30) for _ in range(200)], rng.randint(3, 97)) is None for _ in range(10))
    ce_none = 0
    for i in range(12):
        k = rng.choice([2, 3, 80, 150])
        xs = [rng.randint(2, 30)] * k if i % 3 == 0 else [rng.randint(2, 30) for _ in range(k)]
        ce_none += run(xs, rng.choice([1, 2, rng.randint(3, 97)])) is None
    outs, dep = set(), False
    for _ in range(60):
        xs = [rng.randint(2, 30) for _ in range(rng.randint(4, 9))]
        m = rng.randint(3, 97)
        o = run(xs, m)
        outs.add(o)
        ys = list(xs)
        ys[-1] = ys[-1] + 1 if ys[-1] < 30 else 2
        if run(ys, m) != o:
            dep = True
    nondeg = len(outs - {None}) >= 3 and dep and None not in outs
    struct_ok = inv and ext_none == 0 and st_none == 0 and ce_none == 0
    return {"init": p[1], "body": p[2], "final": p[3], "invariant": inv, "ext_none": ext_none,
            "stress_none": st_none, "ce_none": ce_none, "distinct": len(outs), "depends_on_list": dep,
            "nondegenerate": nondeg, "struct_ok": struct_ok, "admissible": struct_ok and nondeg,
            "g1_body": T3E.body_key(p[2]) in T3E.g1_mechanisms(),
            "uses_fl_body": mentions(p[2], "first") or mentions(p[2], "last")}


def sample():
    rng = random.Random(I._seed("APHRODITE/FRONTIER/K1/FORENSIC/v1"))
    finals = [f for f in G.FINAL_SPACE if mentions(f, "acc")]
    out = []
    for op in STRATA:
        pool = [b for b in G.BODY_SPACE if T3E._top_op(b) == op and mentions(b, "acc") and mentions(b, "v")]
        for _ in range(N_PER):
            out.append((op, ("fold", rng.choice(G.H1_SPACE), rng.choice(pool), rng.choice(finals))))
    return out


def _w(args):
    op, p = args
    return op, witness_row(p)


if __name__ == "__main__":
    with ProcessPoolExecutor(8) as ex:
        bodies = list(ex.map(body_row, G.BODY_SPACE, chunksize=200))
        wit = list(ex.map(_w, sample(), chunksize=20))
    bsum = defaultdict(Counter)
    for r in bodies:
        if r["acc_v"]:
            bsum[r["op"]]["n"] += 1
            bsum[r["op"]]["rc"] += r["rc"]
            bsum[r["op"]]["g1"] += r["g1"]
            bsum[r["op"]]["rc_and_not_g1"] += r["rc"] and not r["g1"]
    wsum = defaultdict(Counter)
    for op, r in wit:
        c = wsum[op]
        c["n"] += 1
        for k in ("invariant", "struct_ok", "nondegenerate", "admissible", "g1_body"):
            c[k] += bool(r[k])
        c["stress_none_any"] += r["stress_none"] > 0
        c["admissible_and_g1"] += r["admissible"] and r["g1_body"]
        c["admissible_not_g1"] += r["admissible"] and not r["g1_body"]
    adm_ng = Counter(T3E.body_key(r["body"])[:12] for op, r in wit if r["admissible"] and not r["g1_body"])
    ex_ng = defaultdict(list)
    for op, r in wit:
        if r["admissible"] and not r["g1_body"] and len(ex_ng[op]) < 6:
            ex_ng[op].append([r["init"], r["body"], r["final"]])
    out = {"body_level": {op: dict(v) for op, v in bsum.items()},
           "witness_level": {op: dict(v) for op, v in wsum.items()},
           "admissible_non_g1_examples": ex_ng,
           "admissible_non_g1_distinct_body_mechanisms": len(adm_ng), "N_per_stratum": N_PER}
    Path(__file__).with_name("K1_SUPPLY_CENSUS.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: out[k] for k in ("body_level", "witness_level")}, indent=1))
    print("admissible non-G1 distinct mechanisms:", len(adm_ng))
    for op, v in ex_ng.items():
        print(op, v)

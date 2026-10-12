"""AR-1 conformance known answer: hand-written AR-1 tapes for pilot_v2 witnesses must agree with tfs1.core (interpreter
B) running the sealed witness, value-or-FAIL, on every dev / test / tribunal input and on extra adversarial inputs
(empty, singleton, extremes, shifted distribution). EXPOSED pilot data only.

The tapes were written by hand from the (exposed) pilot witnesses; they are an expressivity / interpreter check, NOT
units used by any search (the given-true-stones row is NOT_DEFINABLE natively; see AR1_DESIGN.md s7).
"""
import random
from typing import Dict, List

from tfs1 import core as C
from tfs1.e3 import worlds as WD
from alien import machine as M

# family_id -> hand-written tape (pilot_v2)
HAND: Dict[str, str] = {
    # W1d5301d0: f1 = (lam x (div (add 1 x) 3)); p0 = (lam x (lt x (add 2 3))); s0 = (lam a (lam b (sub b (div a 3))))
    "W1d5301d0-F006-R1": "[ 1 + 3 / ]",                                         # last (map f1 xs)
    "W1d5301d0-F007-R1": "[ 1 + 3 / ] d [ p A d a < s d n a + A s a * + ]",     # max (map f1 xs)
    "W1d5301d0-F008-R1": "[ d 2 3 + < ? . ]",                                   # filter p0 xs
    "W1d5301d0-F009-R1": "[ 2 3 + < a + A ] a",                                 # len (filter p0 xs)
    "W1d5301d0-F010-R1": "1 A [ a 3 / - A ] a",                                 # foldl s0 1 xs
    "W1d5301d0-F012-R1": "1 d . A [ a 3 / - d . A ]",                           # scanl s0 1 xs
    "W1d5301d0-F035-R3": "[ a 3 / - A ] a 1 + 3 /",                             # f1 (foldl s0 0 xs)
    "W1d5301d0-F027-R3": "[ 1 + 3 / a 3 / - A ] a",                             # foldl (s0 a (f1 b)) 0 xs
    "W1d5301d0-F071-R4": "[ 1 + 3 / d 2 3 + < ? . ]",                           # filter p0 (map f1 xs)
    "W1d5301d0-F077-R4": "[ d 2 3 + < A d 1 + 3 / a * s d a * - + . ]",             # map (if p0 then f1 else id)
    # W0467897d: f1 = (lam x (pow (gcd x x) 3)) = |x|^3; p0 = (lam x (gt x (add 2 2)))
    "W0467897d-F010-R1": "[ d 2 2 + s < ? . ]",                                 # filter p0 xs
    "W0467897d-F008-R1": "[ 2 2 + s < a + A ] a",                               # len (filter p0 xs)
    "W0467897d-F007-R1": "[ d 0 < ? n d d * * ] d [ p A d a < s d n a + A s a * + ]",   # max (map f1 xs)
    "W0467897d-F061-R3": "[ d 2 2 + s < s d 0 < ? n d d * * * a + A ] a",       # sum (map f1 (filter p0 xs))
    "W0467897d-F085-R3": "[ d 2 2 + s < A d d 0 < ? n d d * * a * s d a * - + . ]",  # map (if p0 then f1 else id)
}


def extra_inputs(seed: int = 7, n: int = 60) -> List[List[int]]:
    rng = random.Random(seed)
    out = [[], [0], [5], [-5], [4], [10 ** 6, -10 ** 6], [2, 2, 2], list(range(-8, 9))]
    for _ in range(n):
        lo, hi, ln = (-20, 20, rng.randint(0, 8)) if rng.random() < 0.5 else (-40, 40, rng.randint(9, 16))
        out.append([rng.randint(lo, hi) for _ in range(ln)])
    return out


def check(root="foundry/pilot_v2") -> Dict:
    man = WD.world_manifest(root)
    rows = []
    for fid, tape in HAND.items():
        world = fid.split("-")[0]
        ev = WD.Evaluator(root, world)
        by = {m["family_id"]: o for o, m in ev.id_map.items()}
        sealed = {f["family_id"]: f for f in WD.sealed(root, world)["families"]}
        task = ev.task(by[fid])
        T = task["output_type"]
        wit = C.parse(sealed[fid]["witness"])
        fn = C.compile_term(wit, None, None, swap=False)
        prog = M.compile_tape(M.parse(tape))
        n = bad = 0
        first_bad = None
        for part in ("dev", "test", "tribunal", "extra"):
            ins = [i for i, _o in task[part]] if part != "extra" else extra_inputs()
            for xs in ins:
                vb = C.run(fn, list(xs))
                va = M.run_compiled(prog, list(xs), T)
                n += 1
                if not M.same_value(va, vb):
                    bad += 1
                    first_bad = first_bad or {"part": part, "xs": xs, "ar1": va, "tfs1": vb}
        exc = getattr(C, "_FAIL_EXC", None)
        if exc is not None:
            exc.__traceback__ = None
        rows.append({"family_id": fid, "tape": tape, "tape_len": len(M.parse(tape)), "witness": sealed[fid]["witness"],
                     "witness_size": C.size(wit), "n_inputs": n, "disagreements": bad, "first_bad": first_bad})
    return {"n_witnesses": len(rows), "all_agree": all(r["disagreements"] == 0 for r in rows), "rows": rows,
            "manifest_worlds": sorted(man["worlds"])}


if __name__ == "__main__":
    import json
    r = check()
    for row in r["rows"]:
        print(row["family_id"], row["tape_len"], row["witness_size"], row["n_inputs"], row["disagreements"],
              row["first_bad"])
    print("ALL_AGREE", r["all_agree"])
    _ = json

"""PLANTED CALIBRATION TASKS (instrument calibration, never discovery). All witnesses and dev designs are hand-made.

  TOY-D2-calibration   the TFS-1 substrate lead's depth-2 toy (tfs1.toy_calibration.task) with the planted level-1
                       primitive P1 = (lam x (add (mul x x) 1)) promoted; witness (sum (map (lam x (L_P1 (L_P1 x))) xs)).
  ATLAS-TOY-GRADED     witness (map (lam x (pow (mul x x) 2)) xs) [x -> x^4]; dev STRATIFIED so that the route
                       xs -> (map id) -> (map x^2) -> W has strictly increasing EXACT credit (3/10, 6/10, 10/10):
                       3 dev lists over {0,1}, 3 over {-1,0,1} with a -1, 4 with an element |v| >= 2.
  ATLAS-TOY-DESERT     the SAME witness and test set; dev lists use only |v| >= 2, so every lattice intermediate has
                       exact AND partial credit 0 (flat). (A numeric-closeness credit would still see x^2 closer than
                       x -- reported as a diagnostic, see ATLAS_DESIGN.md.)
  ATLAS-TOY-CREDIT     witness (map (lam x (mod (mul x x) 3)) xs); dev lists of length >= 3 over |v| >= 2 that always
                       contain an element = 2 (mod 3) AND an element = 0 (mod 3) (so no constant list and not
                       (mod x 3) is ever exactly right): exact credit is flat along the route, but the lattice member
                       (map (lam x (mod x 3)) xs) earns PARTIAL (per-position) credit -> planted credit-channel contrast.
"""
import random
from typing import Dict, List

from tfs1 import core as C

LABEL = "PLANTED INSTRUMENT CALIBRATION (hand-made witness and dev design); NOT DISCOVERY"


def _lists(r: random.Random, k: int, vals: List[int], lmin: int, lmax: int, seen: set, pred=None) -> List[List[int]]:
    out = []
    while len(out) < k:
        l = [r.choice(vals) for _ in range(r.randint(lmin, lmax))]
        if tuple(l) in seen or (pred is not None and not pred(l)):
            continue
        seen.add(tuple(l))
        out.append(l)
    return out


def _mk(fid: str, witness: str, dev_in, test_in) -> Dict:
    w = C.parse(witness)
    f = lambda l: C.evaluate(w, l)[0]               # noqa: E731
    return {"family_id": fid, "rung": "CALIBRATION", "generator_seed": None, "witness": witness,
            "dev": [[i, f(i)] for i in dev_in], "test": [[i, f(i)] for i in test_in],
            "input_dist": "planted (see atlas/toys.py)", "output_type": C.type_of(w), "provenance": LABEL}


def _test_inputs(seen: set, seed: int) -> List[List[int]]:
    return _lists(random.Random(seed), 32, list(range(-4, 7)), 0, 6, seen)


W_POW4 = "(map (lam x (pow (mul x x) 2)) xs)"
W_MOD3 = "(map (lam x (mod (mul x x) 3)) xs)"


def graded() -> Dict:
    r, seen = random.Random(2026101011), set()
    dev = (_lists(r, 3, [0, 1], 1, 5, seen, lambda l: 1 in l)
           + _lists(r, 3, [-1, 0, 1], 1, 5, seen, lambda l: -1 in l)
           + _lists(r, 4, list(range(-4, 6)), 2, 6, seen, lambda l: any(abs(v) >= 2 for v in l)))
    return _mk("ATLAS-TOY-GRADED", W_POW4, dev, _test_inputs(seen, 2026101019))


def desert() -> Dict:
    r, seen = random.Random(2026101012), set()
    vals = [v for v in range(-5, 7) if abs(v) >= 2]
    dev = _lists(r, 10, vals, 1, 6, seen)
    return _mk("ATLAS-TOY-DESERT", W_POW4, dev, _test_inputs(seen, 2026101019))


def credit() -> Dict:
    r, seen = random.Random(2026101013), set()
    vals = [v for v in range(-6, 7) if abs(v) >= 2]
    ok = lambda l: (any(v % 3 == 2 for v in l) and any(v % 3 == 0 for v in l))   # noqa: E731
    dev = _lists(r, 10, vals, 3, 6, seen, ok)
    return _mk("ATLAS-TOY-CREDIT", W_MOD3, dev, _test_inputs(seen, 2026101029))


def tfs1_toy():
    """(task, library, promoted witness) of the substrate lead's toy. Labelled calibration."""
    from tfs1.toy_calibration import task, libraries
    T = task()
    libs, p1 = libraries()
    T = dict(T)
    T["witness"] = "(sum (map (lam x (%s (%s x))) xs))" % (p1, p1)
    T["rung"] = "CALIBRATION"
    return T, libs["PROMOTED"]


def all_toys():
    """name -> (task, library)."""
    t, lib = tfs1_toy()
    return {"TOY-D2": (t, lib), "GRADED": (graded(), None), "DESERT": (desert(), None), "CREDIT": (credit(), None)}

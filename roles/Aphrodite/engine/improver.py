"""The improver: a proposal library (MUTABLE) over an unchanged grammar.

Frozen by AMENDMENT_9_2026-09-22.md (commit fe1ca23c6).

A proposal library is DATA: an ordered list of entries, each three sets of
expression strings. It selects and orders G4 programs; it cannot express
anything G4 cannot. Every improver, pristine or modified, falls back to the
complete G4 enumeration, so expressive power is identical by construction.

Everything else in this file -- the mutation operators, the fitness rule, the
selection rule -- is IMMUTABLE machinery and is never part of the artifact.
"""
import hashlib
import json
import random
import re
from typing import Dict, List, Optional, Tuple

import basis_v4 as G
import engine as E

# ---------------------------------------------------------------- families
# (body, final) pairs over G4. Catalogs are disjoint and were frozen in the
# amendment before anything was built.
FAMILY_SPEC = {
    # META-DEV
    "md_sum_times_last":      ("(acc + v)", "(acc * last)"),
    "md_prod_plus_first":     ("(acc * v)", "(acc + first)"),
    "md_gcd_minus_first":     ("math.gcd(abs(acc), abs(v))", "(acc - first)"),
    "md_sumsq_plus_last":     ("(acc + (v * v))", "(acc + last)"),
    # META-TRIBUNAL (unseen; two shared body kinds, two unseen body kinds)
    "mt_sum_minus_last":      ("(acc + v)", "(acc - last)"),
    "mt_gcd_plus_first":      ("math.gcd(abs(acc), abs(v))", "(acc + first)"),
    "mt_summod_times_first":  ("(acc + (v % last))", "(acc * first)"),
    "mt_prodshift_minus_first": ("(acc * (v + first))", "(acc - first)"),
}
META_DEV = [k for k in FAMILY_SPEC if k.startswith("md_")]
META_TRIBUNAL = [k for k in FAMILY_SPEC if k.startswith("mt_")]
INIT_FOR = {"(acc * v)": "1", "(acc * (v + first))": "1"}


def init_for(body: str) -> str:
    return INIT_FOR.get(body, "0")


def witness(family: str) -> Tuple:
    body, final = FAMILY_SPEC[family]
    return ("fold", init_for(body), body, final)


def task(family: str, rng: random.Random, length_range=G.SEARCH_LENGTHS):
    lo, hi = length_range
    k = rng.randint(lo, hi)
    xs = [rng.randint(2, 30) for _ in range(k)]
    m = rng.randint(3, 97)
    nums = xs + [m]
    prog = witness(family)
    gold = G.run_program(prog, nums, True)
    prompt = ("Family %s over: " % family) + ", ".join(map(str, xs)) + " with %d." % m
    return prompt, str(gold)


def tasks(family: str, n: int, seed: int, length_range=G.SEARCH_LENGTHS) -> List[Dict]:
    rng = random.Random((seed, family, length_range).__str__())
    out = []
    for i in range(n):
        p, g = task(family, rng, length_range)
        out.append({"family": family, "prompt": p, "gold": g,
                    "key": "%s-%d-%d" % (family, seed, i)})
    return out


def run(prog, nums):
    return G.run_program(prog, nums, True)      # every family has a trailing param


# ---------------------------------------------------------------- library
class Library:
    """The MUTABLE artifact. Entries are data, never code."""

    def __init__(self, entries: List[Dict]):
        self.entries = entries

    def canonical(self) -> bytes:
        return json.dumps(self.entries, sort_keys=True, separators=(",", ":")).encode()

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical()).hexdigest()

    def size(self) -> int:
        return sum(len(e["inits"]) * len(e["bodies"]) * len(e["finals"]) for e in self.entries)

    def desugars_into_g4(self) -> Tuple[bool, List[str]]:
        bad = []
        for e in self.entries:
            for i in e["inits"]:
                if i not in G.INIT_SPACE:
                    bad.append("init:" + i)
            for b in e["bodies"]:
                if b not in G.BODY_SPACE:
                    bad.append("body:" + b)
            for f in e["finals"]:
                if f not in G.FINAL_SPACE:
                    bad.append("final:" + f)
        return (not bad), bad

    def candidates(self, rng: Optional[random.Random] = None):
        """Entries in order, then the COMPLETE base grammar as fallback."""
        for e in self.entries:
            inits, bodies, finals = list(e["inits"]), list(e["bodies"]), list(e["finals"])
            if rng:
                for lst in (inits, bodies, finals):
                    rng.shuffle(lst)
            for i in inits:
                for b in bodies:
                    for f in finals:
                        yield ("fold", i, b, f), e["name"]
        for prog, _tag in G.scratch_candidates(rng):
            yield prog, "g4_fallback"


def pristine_library() -> Library:
    """L0: the slice-4 organ coordinate, expressed as a library entry."""
    return Library([{"name": "organ_fold",
                     "inits": list(G.H1_SPACE),
                     "bodies": list(G.H2_SPACE),
                     "finals": list(G.FINAL_SPACE)}])


# ---------------------------------------------------------------- search
def search(library: Library, examples: List[Dict], escrow: E.Escrow, cap: int,
           rng: Optional[random.Random] = None):
    parsed = [([int(x) for x in re.findall(r"-?\d+", t["prompt"])], t["gold"])
              for t in examples]
    for prog, coord in library.candidates(rng):
        if escrow.remaining() <= 0 or escrow.spent >= cap:
            return None
        escrow.charge(1)
        ok = True
        for nums, gold in parsed:
            got = run(prog, nums)
            if got is None or str(got) != gold:
                ok = False
                break
        if ok:
            return prog, coord, escrow.spent
    return None


# ---------------------------------------------------------------- mutation (IMMUTABLE)
def op_specialise_from(observed: List[Tuple], name: str, base: Library) -> Library:
    """OP1: an entry whose INIT/BODY sets are the parts actually observed,
    with the FINAL set left general."""
    inits = sorted({p[1] for p in observed}) or ["0"]
    bodies = sorted({p[2] for p in observed})
    if not bodies:
        return base
    entry = {"name": name, "inits": inits, "bodies": bodies,
             "finals": list(G.FINAL_SPACE)}
    return Library([entry] + base.entries)


def op_antiunify_pair(observed: List[Tuple], base: Library) -> Library:
    """OP2: generalise two observed programs by the slice-3 LGG. Where the two
    bodies differ structurally the generalisation admits both."""
    if len(observed) < 2:
        return base
    a, b = observed[0], observed[1]
    bodies = sorted({a[2], b[2]})
    inits = sorted({a[1], b[1]})
    entry = {"name": "antiunified", "inits": inits, "bodies": bodies,
             "finals": list(G.FINAL_SPACE)}
    return Library([entry] + base.entries)


def op_reorder(base: Library) -> Library:
    if len(base.entries) < 2:
        return base
    return Library([base.entries[-1]] + base.entries[:-1])


def op_drop(base: Library) -> Library:
    if len(base.entries) < 2:
        return base
    return Library(base.entries[1:])


def candidate_libraries(observed: List[Tuple], failed_bodies: List[str],
                        base: Library) -> List[Tuple[str, Library]]:
    out = [("unchanged", base),
           ("specialise_from_successes", op_specialise_from(observed, "specialised", base)),
           ("antiunify_pair", op_antiunify_pair(observed, base)),
           ("reorder", op_reorder(base)),
           ("drop", op_drop(base))]
    return [(n, lib) for n, lib in out if lib is not None]


def sham_library(failed_bodies: List[str], base: Library) -> Library:
    """The declared mechanical SHAM: the same specialising entry shape, built
    from bodies the donor tried and that did NOT succeed. Equal interface,
    comparable size, no useful structure."""
    bodies = sorted(set(failed_bodies))[:8] or [G.BODY_SPACE[0]]
    entry = {"name": "sham_specialised", "inits": ["0", "1"], "bodies": bodies,
             "finals": list(G.FINAL_SPACE)}
    return Library([entry] + base.entries)


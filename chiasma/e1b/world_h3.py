"""Paradigm World family H3 (PW-H3): three staged false abstractions with different loads.

PW-H has one latent abstraction Y = c & f, and the ydep:decoy ratio of the whole world
decides which pre-shock bet (keep f or drop f) wins. PW-H3 puts K abstractions
Y_j = c_j & f_j in one world, each with its own load (ydep_j, decoy_j). A single
global bet is right for one abstraction and wrong for another, so an organism wins
across the world only if it decides per abstraction, from evidence.

  ydep    Z<j>_<i> = c_j & f_j & u & v
  decoy   D<j>_<k> = c_j & u & v
  unrel   as PW-H (avoid every c_j, f_j)
  invalid as PW-H
  new     N<j>_<i> = c_j & f_j & u & v, active only in phase F

Phases as PW-H. In A-C the sampler forces c_j -> f_j for every j. In C, each object
is, with probability exc_permille/1000, forced to c_j & not-f_j for ONE j drawn
uniformly. D-F are unconstrained.

Interface is the PW-H World interface (targets, active, observe, invalid, describe),
so chiasma.runner's scoring applies unchanged.
"""
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

from ..world import Target, World, bits, _draw

LOADS = ((12, 4), (8, 8), (4, 12))


@dataclass(frozen=True)
class WorldSpecH3:
    m: int = 24
    loads: Tuple[Tuple[int, int], ...] = LOADS
    n_unrel: int = 8
    n_unrel_disj: int = 3
    n_invalid_laws: int = 3
    n_new_per: int = 2
    rho_permille: int = 500
    exc_permille: int = 20
    phase_len: Tuple[Tuple[str, int], ...] = (("A", 1500), ("B", 1500), ("C", 1000),
                                              ("D", 500), ("E", 1500), ("F", 1500))
    n_probe_random: int = 300
    n_probe_critical: int = 4

    def as_dict(self) -> Dict:
        d = dict(self.__dict__)
        d["loads"] = [list(p) for p in self.loads]
        d["phase_len"] = [list(p) for p in self.phase_len]
        return d


class WorldH3(World):
    family = "PW-H3"

    def __init__(self, spec: WorldSpecH3, seed: int, pairs: List[Tuple[int, int]]):
        super().__init__(spec=spec, seed=seed, c=pairs[0][0], f=pairs[0][1])
        self.pairs = pairs
        self.abs_of: Dict[str, int] = {}

    def describe(self) -> Dict:
        d = super().describe()
        d["family"] = self.family
        d["pairs"] = [list(p) for p in self.pairs]
        d["abs_of"] = dict(sorted(self.abs_of.items()))
        return d


def _rng(seed: int, salt: str) -> random.Random:
    return random.Random("h3:{}:{}".format(seed, salt))


def make_world_h3(spec: WorldSpecH3, seed: int) -> WorldH3:
    r = _rng(seed, "laws")
    prims = list(range(spec.m))
    r.shuffle(prims)
    K = len(spec.loads)
    pairs = [(prims[2 * j], prims[2 * j + 1]) for j in range(K)]
    rest = prims[2 * K:]
    used = set()

    def fresh_pair() -> int:
        for _ in range(10000):
            u, v = r.sample(rest, 2)
            key = (min(u, v), max(u, v))
            if key not in used:
                used.add(key)
                return (1 << u) | (1 << v)
        raise ValueError("ran out of distinct primitive pairs")

    w = WorldH3(spec, seed, pairs)

    def add(t: Target, j: int) -> None:
        w.targets.append(t)
        if j >= 0:
            w.abs_of[t.name] = j

    for j, (ny, nd) in enumerate(spec.loads):
        C, F = 1 << pairs[j][0], 1 << pairs[j][1]
        for i in range(ny):
            add(Target("Z{}_{:02d}".format(j, i), "ydep", (C | F | fresh_pair(),),
                       "A" if i < (ny + 1) // 2 else "B"), j)
        for k in range(nd):
            add(Target("D{}_{:02d}".format(j, k), "decoy", (C | fresh_pair(),),
                       "A" if k < (nd + 1) // 2 else "B"), j)
    for jj in range(spec.n_unrel):
        n_terms = 2 if jj < spec.n_unrel_disj else 1
        terms = []
        for _ in range(n_terms):
            terms.append(sum(1 << p for p in r.sample(rest, r.choice((2, 3)))))
        add(Target("U{:02d}".format(jj), "unrel", tuple(terms), "A"), -1)
    laws = [sum(1 << p for p in r.sample(rest, 4)) for _ in range(spec.n_invalid_laws)]
    add(Target("INVALID", "invalid", tuple(laws), "A"), -1)
    for j in range(K):
        C, F = 1 << pairs[j][0], 1 << pairs[j][1]
        for i in range(spec.n_new_per):
            add(Target("N{}_{:02d}".format(j, i), "new", (C | F | fresh_pair(),), "F"), j)
    return w


def stream_h3(w: WorldH3):
    r = _rng(w.seed, "stream")
    CF = [(1 << c, 1 << f) for c, f in w.pairs]
    t = 0
    for phase, n in w.spec.phase_len:
        for _ in range(n):
            x = _draw(r, w.spec)
            if phase in ("A", "B", "C"):
                for C, F in CF:
                    if x & C:
                        x |= F
                if phase == "C" and r.randrange(1000) < w.spec.exc_permille:
                    C, F = CF[r.randrange(len(CF))]
                    x = (x | C) & ~F
            yield t, phase, x
            t += 1


def probes_h3(w: WorldH3) -> List[Tuple[str, int]]:
    r = _rng(w.seed, "probes")
    out = [("random", _draw(r, w.spec)) for _ in range(w.spec.n_probe_random)]
    for t in w.targets:
        if t.group in ("ydep", "decoy", "new"):
            c, f = w.pairs[w.abs_of[t.name]]
            C, F = 1 << c, 1 << f
            core = t.terms[0] & ~F
            n_made, tries = 0, 0
            while n_made < w.spec.n_probe_critical and tries < 1000:
                tries += 1
                x = (_draw(r, w.spec) | core | C) & ~F
                if not w.invalid.holds(x):
                    out.append(("crit:" + t.name, x))
                    n_made += 1
    return out

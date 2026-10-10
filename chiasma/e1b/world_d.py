"""Paradigm World family D (PW-D): deep, widely shared abstractions (HADES-29).

PW-H and PW-H3 have two-literal abstractions, so shared structure is a small part of
any representation and compression cannot pay without destroying knowledge (DEV_NOTES
s10). PW-D keeps PW-H3's staged false foundations and loads, and makes each abstraction
deep:

  Y_j = core_j & f_j, core_j = L_core primitives (default 4)
  ydep  Z<j>_<i> = core_j & f_j & u & v
  decoy D<j>_<k> = core_j & u & v
  new   N<j>_<i> = core_j & f_j & u & v, active only in phase F
  unrel over the remaining primitives (some disjunctive); invalid = OR of laws over the
  remaining primitives, each law LAW_SIZE literals

Sampler (latent causes, so cores are instantiated as blocks and also occur partially):
  - each core_j is instantiated whole with probability block_permille/1000; otherwise
    each of its literals is present independently with probability partial_permille/1000
  - f_j: independent at 1/2, except that in A-C it is forced on whenever core_j is whole
    (as PW-H forces c -> f: "core alone suffices" predicts every A/B label); in C, with
    probability exc_permille/1000 one j drawn uniformly gets a whole core with f_j
    absent; in D-F, f_j is independent at 1/2 always.
    (A first draft set f_j ONLY with a whole core in A-C. Then f_j implies every core
    literal, consolidation prunes the whole core down to the marker f_j, and a second
    false foundation appears beside the first. That variant, PW-Dm, is kept for a later
    single-variable run; dev seed 910001 only, DEV_NOTES s11.)
  - every other primitive is independent at 1/2

Interface: the PW-H World interface, plus `cores` (list of masks) and `fs` (list of bit
indices) and `abs_of` (target -> j), so chiasma.runner's scoring applies unchanged.
"""
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

from ..world import Target, World, bits

LOADS = ((12, 4), (8, 8), (4, 12))


@dataclass(frozen=True)
class WorldSpecD:
    m: int = 32
    l_core: int = 4
    loads: Tuple[Tuple[int, int], ...] = LOADS
    block_permille: int = 333
    partial_permille: int = 250
    n_unrel: int = 8
    n_unrel_disj: int = 3
    n_invalid_laws: int = 2
    law_size: int = 5
    n_new_per: int = 2
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


class WorldD(World):
    family = "PW-D"

    def __init__(self, spec: WorldSpecD, seed: int, cores: List[int], fs: List[int]):
        super().__init__(spec=spec, seed=seed, c=bits(cores[0])[0], f=fs[0])
        self.cores = cores
        self.fs = fs
        self.rest: List[int] = []
        self.abs_of: Dict[str, int] = {}

    def describe(self) -> Dict:
        d = super().describe()
        d["family"] = self.family
        d["cores"] = [bits(c) for c in self.cores]
        d["fs"] = list(self.fs)
        d["abs_of"] = dict(sorted(self.abs_of.items()))
        return d


def _rng(seed: int, salt: str) -> random.Random:
    return random.Random("d:{}:{}".format(seed, salt))


def make_world_d(spec: WorldSpecD, seed: int) -> WorldD:
    r = _rng(seed, "laws")
    prims = list(range(spec.m))
    r.shuffle(prims)
    K, L = len(spec.loads), spec.l_core
    cores, fs = [], []
    for j in range(K):
        block = prims[j * (L + 1):(j + 1) * (L + 1)]
        cores.append(sum(1 << p for p in block[:L]))
        fs.append(block[L])
    rest = prims[K * (L + 1):]
    used = set()

    def fresh_pair() -> int:
        for _ in range(10000):
            u, v = r.sample(rest, 2)
            key = (min(u, v), max(u, v))
            if key not in used:
                used.add(key)
                return (1 << u) | (1 << v)
        raise ValueError("ran out of distinct primitive pairs")

    w = WorldD(spec, seed, cores, fs)
    w.rest = rest

    def add(t: Target, j: int) -> None:
        w.targets.append(t)
        if j >= 0:
            w.abs_of[t.name] = j

    for j, (ny, nd) in enumerate(spec.loads):
        C, F = cores[j], 1 << fs[j]
        for i in range(ny):
            add(Target("Z{}_{:02d}".format(j, i), "ydep", (C | F | fresh_pair(),),
                       "A" if i < (ny + 1) // 2 else "B"), j)
        for k in range(nd):
            add(Target("D{}_{:02d}".format(j, k), "decoy", (C | fresh_pair(),),
                       "A" if k < (nd + 1) // 2 else "B"), j)
    for jj in range(spec.n_unrel):
        n_terms = 2 if jj < spec.n_unrel_disj else 1
        terms = [sum(1 << p for p in r.sample(rest, r.choice((2, 3)))) for _ in range(n_terms)]
        add(Target("U{:02d}".format(jj), "unrel", tuple(terms), "A"), -1)
    laws = [sum(1 << p for p in r.sample(rest, spec.law_size)) for _ in range(spec.n_invalid_laws)]
    add(Target("INVALID", "invalid", tuple(laws), "A"), -1)
    for j in range(K):
        C, F = cores[j], 1 << fs[j]
        for i in range(spec.n_new_per):
            add(Target("N{}_{:02d}".format(j, i), "new", (C | F | fresh_pair(),), "F"), j)
    return w


def _draw_d(r: random.Random, w: WorldD, phase: str) -> int:
    s = w.spec
    x = 0
    for p in w.rest:
        if r.randrange(2):
            x |= 1 << p
    whole = []
    for core in w.cores:
        if r.randrange(1000) < s.block_permille:
            x |= core
            whole.append(True)
        else:
            for p in bits(core):
                if r.randrange(1000) < s.partial_permille:
                    x |= 1 << p
            whole.append((x & core) == core)
    for j, f in enumerate(w.fs):
        if r.randrange(2) or (phase in ("A", "B", "C") and whole[j]):
            x |= 1 << f
    return x


def stream_d(w: WorldD):
    r = _rng(w.seed, "stream")
    t = 0
    for phase, n in w.spec.phase_len:
        for _ in range(n):
            x = _draw_d(r, w, phase)
            if phase == "C" and r.randrange(1000) < w.spec.exc_permille:
                j = r.randrange(len(w.cores))
                x = (x | w.cores[j]) & ~(1 << w.fs[j])
            yield t, phase, x
            t += 1


def probes_d(w: WorldD) -> List[Tuple[str, int]]:
    r = _rng(w.seed, "probes")
    out = [("random", _draw_d(r, w, "D")) for _ in range(w.spec.n_probe_random)]
    for t in w.targets:
        if t.group in ("ydep", "decoy", "new"):
            j = w.abs_of[t.name]
            F = 1 << w.fs[j]
            core = t.terms[0] & ~F
            n_made, tries = 0, 0
            while n_made < w.spec.n_probe_critical and tries < 1000:
                tries += 1
                x = (_draw_d(r, w, "D") | core) & ~F
                if not w.invalid.holds(x):
                    out.append(("crit:" + t.name, x))
                    n_made += 1
    return out

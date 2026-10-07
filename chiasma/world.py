"""Paradigm Worlds, family H (PW-H): Horn-law universes with a staged false foundation.

An object is a set of latent primitives, stored as an int bitmask over m primitives.
Every target (observable property) is a disjunction of conjunctions of primitives; the
world knows each target's exact truth. The latent abstraction Y = {c, f} is never
labelled. Targets fall into groups:

  ydep    Z_i  = c & f & u_i & v_i        (true dependents of the latent Y)
  decoy   D_k  = c & u'_k & v'_k          (depend on c alone; indistinguishable from
                                           ydep while the sampler forces c -> f)
  unrel   U_j  = one or two conjunctions avoiding c and f (some disjunctive)
  invalid INVALID = OR of incompatibility laws; an invalid object is a failed
                    experiment: it returns INVALID=1 and no other label
  new     Z_new_i = c & f & u & v with pairs never used before, active only in phase F

Phases (the organism never receives the phase name; the stream is unlabelled):
  A learn        c -> f forced (if c is present, f is set)
  B reinforce    same sampler; the second half of ydep/decoy targets becomes active
  C exceptions   as B, but with probability exc_permille/1000 an object is forced to
                 c & not-f (the first exceptions e_1, e_2, ...)
  D falsify      unconstrained sampler (c & not-f in about a quarter of objects)
  E relearn      unconstrained
  F novel        unconstrained; the `new` targets become active

Everything is drawn from random.Random(seed) streams with fixed string salts, so the
same (spec, seed) gives byte-identical worlds, streams and probes.
"""
import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

PHASES = ("A", "B", "C", "D", "E", "F")


def popcount(x: int) -> int:
    return bin(x).count("1")


def bits(x: int) -> List[int]:
    out, i = [], 0
    while x:
        if x & 1:
            out.append(i)
        x >>= 1
        i += 1
    return out


@dataclass(frozen=True)
class WorldSpec:
    m: int = 16                 # latent primitives
    n_ydep: int = 16
    n_decoy: int = 8
    n_unrel: int = 8
    n_unrel_disj: int = 3       # of the unrel targets, how many have two conjunctions
    n_invalid_laws: int = 3
    n_new: int = 6
    rho_permille: int = 500     # P(primitive present)
    exc_permille: int = 20      # phase C exception rate
    phase_len: Tuple[Tuple[str, int], ...] = (("A", 1500), ("B", 1500), ("C", 1000),
                                              ("D", 500), ("E", 1500), ("F", 1500))
    n_probe_random: int = 300
    n_probe_critical: int = 4   # per ydep / decoy / new target

    def as_dict(self) -> Dict:
        d = dict(self.__dict__)
        d["phase_len"] = [list(p) for p in self.phase_len]
        return d


@dataclass
class Target:
    name: str
    group: str                  # ydep | decoy | unrel | invalid | new
    terms: Tuple[int, ...]      # disjunction of conjunction masks
    phase_on: str               # first phase in which it is labelled

    def holds(self, x: int) -> bool:
        return any((t & x) == t for t in self.terms)


@dataclass
class World:
    spec: WorldSpec
    seed: int
    c: int
    f: int
    targets: List[Target] = field(default_factory=list)

    @property
    def invalid(self) -> Target:
        return next(t for t in self.targets if t.group == "invalid")

    def active(self, phase: str) -> List[Target]:
        """Targets labelled in `phase` (INVALID is always active)."""
        k = PHASES.index(phase)
        return [t for t in self.targets if PHASES.index(t.phase_on) <= k]

    def observe(self, x: int, phase: str) -> Dict[str, int]:
        """The world's answer to object x: INVALID=1 alone, or every active label."""
        if self.invalid.holds(x):
            return {"INVALID": 1}
        return {t.name: int(t.holds(x)) for t in self.active(phase)}

    def describe(self) -> Dict:
        """Ground truth, for receipts and known-answer checks (never shown to organisms)."""
        return {"seed": self.seed, "c": self.c, "f": self.f,
                "targets": [{"name": t.name, "group": t.group, "phase_on": t.phase_on,
                             "terms": [bits(m) for m in t.terms]} for t in self.targets]}


def _rng(seed: int, salt: str) -> random.Random:
    return random.Random("{}:{}".format(seed, salt))


def make_world(spec: WorldSpec, seed: int) -> World:
    r = _rng(seed, "laws")
    prims = list(range(spec.m))
    r.shuffle(prims)
    c, f = prims[0], prims[1]
    rest = prims[2:]
    C, F = 1 << c, 1 << f
    used_pairs = set()

    def fresh_pair() -> int:
        for _ in range(10000):
            u, v = r.sample(rest, 2)
            key = (min(u, v), max(u, v))
            if key not in used_pairs:
                used_pairs.add(key)
                return (1 << u) | (1 << v)
        raise ValueError("ran out of distinct primitive pairs; lower the target counts")

    w = World(spec=spec, seed=seed, c=c, f=f)
    for i in range(spec.n_ydep):
        w.targets.append(Target("Z{:02d}".format(i), "ydep", (C | F | fresh_pair(),),
                                "A" if i < (spec.n_ydep + 1) // 2 else "B"))
    for k in range(spec.n_decoy):
        w.targets.append(Target("D{:02d}".format(k), "decoy", (C | fresh_pair(),),
                                "A" if k < (spec.n_decoy + 1) // 2 else "B"))
    for j in range(spec.n_unrel):
        n_terms = 2 if j < spec.n_unrel_disj else 1
        terms = []
        for _ in range(n_terms):
            size = r.choice((2, 3))
            terms.append(sum(1 << p for p in r.sample(rest, size)))
        w.targets.append(Target("U{:02d}".format(j), "unrel", tuple(terms), "A"))
    laws = []
    for _ in range(spec.n_invalid_laws):
        laws.append(sum(1 << p for p in r.sample(rest, 4)))
    w.targets.append(Target("INVALID", "invalid", tuple(laws), "A"))
    for i in range(spec.n_new):
        w.targets.append(Target("N{:02d}".format(i), "new", (C | F | fresh_pair(),), "F"))
    return w


def _draw(r: random.Random, spec: WorldSpec) -> int:
    x = 0
    for p in range(spec.m):
        if r.randrange(1000) < spec.rho_permille:
            x |= 1 << p
    return x


def stream(w: World):
    """Yield (t, phase, x) for the whole curriculum; deterministic in (spec, seed)."""
    r = _rng(w.seed, "stream")
    C, F = 1 << w.c, 1 << w.f
    t = 0
    for phase, n in w.spec.phase_len:
        for _ in range(n):
            x = _draw(r, w.spec)
            if phase in ("A", "B", "C"):
                if x & C:
                    x |= F
                if phase == "C" and r.randrange(1000) < w.spec.exc_permille:
                    x = (x | C) & ~F
            yield t, phase, x
            t += 1


def probes(w: World) -> List[Tuple[str, int]]:
    """Fixed probe objects, each tagged with the probe family it came from:
    'random' (unconstrained draw) or 'crit:<target>' (c & not-f & the target's other
    literals, i.e. the region where the false foundation and the truth disagree)."""
    r = _rng(w.seed, "probes")
    C, F = 1 << w.c, 1 << w.f
    out = [("random", _draw(r, w.spec)) for _ in range(w.spec.n_probe_random)]
    for t in w.targets:
        if t.group in ("ydep", "decoy", "new"):
            core = t.terms[0] & ~F
            n_made, tries = 0, 0
            while n_made < w.spec.n_probe_critical and tries < 1000:
                tries += 1
                x = (_draw(r, w.spec) | core | C) & ~F
                if not w.invalid.holds(x):
                    out.append(("crit:" + t.name, x))
                    n_made += 1
    return out

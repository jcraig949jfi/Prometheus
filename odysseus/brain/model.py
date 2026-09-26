"""The circuit model: specification, partition, procedural connectivity.

Integer-only (DESIGN D6) and independent of the shard count, so the same
brain split N ways evolves bit-identically (DESIGN D1, D7). The model is
a placeholder that exercises the substrate; it will be replaced.
"""
import dataclasses
import hashlib
import json
from functools import lru_cache

MASK64 = (1 << 64) - 1


def mix64(x):
    """splitmix64 finaliser: a portable, integer-only hash."""
    x = (x + 0x9E3779B97F4A7C15) & MASK64
    x = ((x ^ (x >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    x = ((x ^ (x >> 27)) * 0x94D049BB133111EB) & MASK64
    return x ^ (x >> 31)


def hash_ints(*parts):
    h = 0x6A09E667F3BCC909
    for p in parts:
        h = mix64(h ^ (p & MASK64))
    return h


@dataclasses.dataclass(frozen=True)
class ModelSpec:
    n_neurons: int
    n_shards: int
    seed: int
    fanout: int = 8
    w_exc: int = 520
    w_inh: int = -900
    inh_every: int = 5  # every 5th neuron is inhibitory
    theta: int = 1000  # firing threshold
    leak_shift: int = 3  # v -= v >> leak_shift each tick
    refractory: int = 2  # ticks a neuron cannot fire after firing
    drive_mod: int = 4  # a neuron gets external drive on ~1/drive_mod ticks
    drive: int = 450
    v_clip: int = 1 << 24

    def __post_init__(self):
        if self.n_neurons < 1:
            raise ValueError("n_neurons must be >= 1")
        if not 1 <= self.n_shards <= self.n_neurons:
            raise ValueError("need 1 <= n_shards <= n_neurons")
        if self.n_neurons > 1 and not 1 <= self.fanout < self.n_neurons:
            raise ValueError("need 1 <= fanout < n_neurons")

    def to_json(self):
        return json.dumps(dataclasses.asdict(self), sort_keys=True)

    @classmethod
    def from_json(cls, text):
        return cls(**json.loads(text))

    def spec_hash(self):
        return hashlib.sha256(self.to_json().encode("ascii")).digest()


def shard_range(spec, shard):
    """Contiguous block [lo, hi) of global neuron ids owned by `shard`."""
    base, rem = divmod(spec.n_neurons, spec.n_shards)
    lo = shard * base + min(shard, rem)
    return lo, lo + base + (1 if shard < rem else 0)


def owner(spec, gid):
    base, rem = divmod(spec.n_neurons, spec.n_shards)
    big = rem * (base + 1)
    if gid < big:
        return gid // (base + 1)
    return rem + (gid - big) // base


@lru_cache(maxsize=1 << 20)
def targets(spec, j):
    """Outgoing synapses of neuron j as (target gid, weight): a pure function of (seed, j)."""
    if spec.n_neurons == 1:
        return ()
    w = spec.w_inh if j % spec.inh_every == 0 else spec.w_exc
    out, seen, k = [], set(), 0
    while len(out) < spec.fanout:
        g = hash_ints(spec.seed, j, k) % spec.n_neurons
        k += 1
        if g != j and g not in seen:
            seen.add(g)
            out.append((g, w))
    return tuple(out)


@lru_cache(maxsize=1 << 20)
def _dest_shards(spec, j):
    return tuple(sorted({owner(spec, g) for g, _ in targets(spec, j)}))


def dest_shards(spec, j):
    """Shards that own at least one target of j: where a spike from j must be sent."""
    return list(_dest_shards(spec, j))


def drive_at(spec, tick, gid):
    """External drive for gid at tick: deterministic, integer, per (seed, tick, gid)."""
    if hash_ints(spec.seed, 0xD21E, tick, gid) % spec.drive_mod == 0:
        return spec.drive
    return 0

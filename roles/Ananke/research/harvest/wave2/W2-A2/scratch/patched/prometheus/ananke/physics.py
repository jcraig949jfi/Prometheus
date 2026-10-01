"""PTE physics dials (roles/Ananke/pte/DESIGN.md s1).

A Physics is every dial except seeds and genomes. It is frozen, hashable,
serialises to a flat dict with exactly the DESIGN.md dial names (plus
topo_seed), and validates the ranges the integer engine relies on.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import math

SUBSTRATE_VERSION = "PTE-SUB-1"
OPS_VERSION = "PTE-OPS-1"

TOPOLOGIES = ("ring", "torus", "random", "smallworld", "global")
DEST_MODES = ("sample", "all")
COLLISIONS = ("none", "aloha", "saturate")
UPDATE_MODES = ("sync", "async")

INT_MAX = 2 ** 31 - 1
REG_MAX = 32767


@dataclasses.dataclass(frozen=True)
class Physics:
    topology: str = "torus"
    n_sites: int = 256
    radius: int = 1
    k_random: int = 4
    rewire: int = 0
    state_dim: int = 4
    payload_width: int = 2
    channels: int = 2
    fanout: int = 2
    dest_mode: str = "sample"
    loss: float = 0.0
    loss_per_hop: int = 0
    lat_base: int = 1
    lat_hop: int = 0
    lat_jitter: int = 0
    dup: float = 0.0
    noise: int = 0
    cap: int = 0
    collision: str = "none"
    decay_shift: int = 0
    update_mode: str = "sync"
    update_period: int = 1
    update_p: float = 1.0
    rules: int = 1
    prog_len: int = 12
    plastic_route: int = 0
    adapt_shift: int = 4
    wimm: int = 0
    setrule: int = 0
    mut_site: float = 0.0
    e_income: int = 0
    e_max: int = 1000
    c_emit: int = 0
    c_op: int = 0
    c_mem: int = 0
    topo_seed: int = 0

    # ------------------------------------------------------------ derived
    @property
    def side(self) -> int:
        return math.isqrt(self.n_sites)

    @property
    def economy_on(self) -> bool:
        return any((self.e_income, self.c_emit, self.c_op, self.c_mem))

    def n_write(self) -> int:
        return self.state_dim + 8 + self.payload_width

    def n_read(self) -> int:
        return self.n_write() + self.channels * self.payload_width + self.channels + 3

    def p16(self, p: float) -> int:
        return int(round(p * 65536))

    def validate(self) -> "Physics":
        assert self.topology in TOPOLOGIES, self.topology
        assert self.dest_mode in DEST_MODES
        assert self.collision in COLLISIONS
        assert self.update_mode in UPDATE_MODES
        assert self.n_sites >= 2
        if self.topology in ("torus", "smallworld"):
            assert self.side * self.side == self.n_sites, "torus needs a square n_sites"
        if self.topology == "global":
            assert self.dest_mode == "sample", "global topology has no table for dest_mode=all"
        assert self.state_dim >= 1 and self.payload_width >= 1 and self.channels >= 1
        assert 1 <= self.payload_width <= 16, "noise sub-index f*16+p needs P<=16"
        assert self.fanout >= 1 and self.rules >= 1 and self.prog_len >= 1
        for p in (self.loss, self.dup, self.update_p, self.mut_site):
            assert 0.0 <= p <= 1.0
        assert 0 <= self.rewire <= 1000
        assert self.update_period >= 1 and self.adapt_shift >= 0
        assert min(self.lat_base, self.lat_hop, self.lat_jitter, self.noise, self.cap,
                   self.decay_shift, self.e_income, self.e_max, self.c_emit, self.c_op,
                   self.c_mem) >= 0
        assert self.fanout < 4096, "duplicate sub-index f+4096 must not collide"
        # mailbox int32 headroom: every sender x every copy x dup x REG_MAX
        worst = self.n_sites * max(self.fanout, self.table_width()) * 2 * REG_MAX
        assert worst < INT_MAX, "mailbox could overflow int32; shrink n_sites*fanout"
        assert 0 <= self.topo_seed < 2 ** 32
        return self

    def table_width(self) -> int:
        """R: entries in the neighbour table (0 for global)."""
        if self.topology == "ring":
            return 2 * self.radius
        if self.topology == "torus":
            return 2 * self.radius * (self.radius + 1)
        if self.topology == "random":
            return self.k_random
        if self.topology == "smallworld":
            return 4
        return 0

    def max_dist(self) -> int:
        if self.topology in ("ring", "torus"):
            return self.radius
        return 1

    def lm(self) -> int:
        """Mailbox ring length (DESIGN.md s6, last line)."""
        return 1 + (self.lat_base + self.lat_hop * self.max_dist()
                    + self.lat_jitter + self.lat_jitter + 1)

    def copies(self) -> int:
        return self.table_width() if self.dest_mode == "all" else self.fanout

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    def digest(self) -> str:
        blob = json.dumps(self.to_dict(), sort_keys=True).encode()
        return hashlib.sha256(blob).hexdigest()[:16]

    def replace(self, **kw) -> "Physics":
        return dataclasses.replace(self, **kw)

    @classmethod
    def from_dict(cls, d: dict) -> "Physics":
        names = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in d.items() if k in names})

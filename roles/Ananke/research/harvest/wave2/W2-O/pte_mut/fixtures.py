"""Small fixtures for the mutation score: hand-written plants (known mechanism) and real C1 champions.

Each Fixture carries the PROPERTIES the metamorphic relations need (comm-dependence, timing sensitivity,
directed topology, ...). Plant properties are known by construction; C1-champion properties come from the
record (C1 rows, harvest audit) and are marked as such.
"""
from __future__ import annotations

import dataclasses
import gzip
import importlib.util
import json

import numpy as np

from . import env as _env  # noqa: F401  (CPU guard first)
from prometheus.ananke import envs, plants
from prometheus.ananke.physics import Physics

ROWS = _env.ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz"
_ROWS = None


def c1_rows():
    global _ROWS
    if _ROWS is None:
        _ROWS = {}
        with gzip.open(ROWS, "rt") as f:
            for line in f:
                r = json.loads(line)
                _ROWS[r["cell_id"]] = r
    return _ROWS


def _hp_plants():
    """harvest/H-PLANT/hp_plants.py loaded by path (read-only)."""
    p = _env.HARVEST / "H-PLANT/hp_plants.py"
    spec = importlib.util.spec_from_file_location("hp_plants_ro", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@dataclasses.dataclass
class Fixture:
    name: str
    ph: Physics
    env: envs.EnvSpec
    genome: np.ndarray            # [G, L, 5]
    props: dict                   # comm, timing, directed, local, source
    seed: int = 20261001          # search_seed used by the held stage
    row: dict | None = None       # C1 row when the fixture is a recorded champion

    def describe(self) -> dict:
        return {"name": self.name, "physics_digest": self.ph.digest(), "topology": self.ph.topology,
                "n_sites": self.ph.n_sites, "env": self.env.to_dict(), "props": self.props,
                "cell": None if self.row is None else self.row["cell_id"]}


# small shared physics for the plants: 8x8 torus, radius 1, flood to all 4 neighbours, lossless
PH_SMALL = Physics(topology="torus", n_sites=64, radius=1, dest_mode="all", prog_len=12,
                   state_dim=4, payload_width=2, channels=2).validate()


def relay64() -> Fixture:
    ph = PH_SMALL
    env = envs.EnvSpec(family="RELAY", d=2, delta=8, trials=8)
    return Fixture("relay64", ph, env, plants.plant("relay_flood", ph),
                   {"comm": True, "timing": False, "directed": False, "local": False, "multi_hop": True,
                    "source": "plants.relay_flood (2 hops at d=2, r=1)"})


def hold64() -> Fixture:
    ph = PH_SMALL
    env = envs.EnvSpec(family="HOLD", gap=8, trials=8)
    return Fixture("hold64", ph, env, plants.plant("hold_latch", ph),
                   {"comm": False, "timing": False, "directed": False, "local": True,
                    "source": "plants.hold_latch (sensor == actuator, local latch, never emits)"})


def echo() -> Fixture:
    ph = plants.c1b_echo_physics()
    env = envs.EnvSpec(family="HOLD", gap=8, cue_len=2, iti=2, trials=8)
    g = np.broadcast_to(plants.echo_hold(ph), (ph.rules, ph.prog_len, 5)).copy()
    return Fixture("echo", ph, env, g,
                   {"comm": True, "timing": True, "directed": False, "local": False,
                    "source": "plants.echo_hold (bit only in flight; delay 5 tuned to cue 2 + gap 8)"})


def random_dir() -> Fixture:
    """relay_flood on a DIRECTED random graph (k=3 out-edges): the only plant where edge direction matters."""
    ph = Physics(topology="random", n_sites=64, k_random=3, dest_mode="all", prog_len=12, state_dim=4,
                 payload_width=2, channels=2, topo_seed=7).validate()
    env = envs.EnvSpec(family="RELAY", d=2, delta=8, trials=8)
    return Fixture("relay_dirgraph", ph, env, plants.plant("relay_flood", ph),
                   {"comm": True, "timing": False, "directed": True, "local": False, "multi_hop": True,
                    "source": "plants.relay_flood on topology=random (directed out-tables)"})


def xor_hp() -> Fixture:
    hp = _hp_plants()
    ph = Physics(topology="torus", n_sites=64, radius=3, dest_mode="all", loss=0.0, lat_base=1,
                 lat_hop=0, lat_jitter=0, dup=0.0, noise=0, cap=0, collision="none", decay_shift=0,
                 update_mode="sync", update_period=1, state_dim=4, payload_width=2, channels=1,
                 rules=1, prog_len=16).validate()           # H-PLANT run_xor.X0
    env = envs.EnvSpec(family="XOR", d=3, delta=8, trials=12)  # H-PLANT run_xor.ENV0
    return Fixture("xor_hp", ph, env, hp.p_xor(ph, env.period()),
                   {"comm": True, "timing": True, "directed": False, "local": False,
                    "source": "H-PLANT hp_plants.p_xor at run_xor.X0/ENV0 (trial-phase counter: Pd-coupled)"})


def flip_hp() -> Fixture:
    hp = _hp_plants()
    ph = PH_SMALL.replace(prog_len=16, channels=1).validate()
    env = envs.EnvSpec(family="FLIP", d=1, delta=8, block=4, trials=8)
    return Fixture("flip_hp", ph, env, hp.p_flip(ph),
                   {"comm": True, "timing": False, "directed": False, "local": False,
                    "source": "H-PLANT hp_plants.p_flip on the small torus (d=1, one hop)"})


def c1(cell: str, name: str, props: dict, trials: int | None = 8) -> Fixture:
    r = c1_rows()[cell]
    ph = Physics.from_dict(r["physics"]).validate()
    ev = dict(r["env"])
    if trials is not None:
        ev["trials"] = trials
    env = envs.EnvSpec(**ev)
    g = np.asarray(r["result"]["champion"], dtype=np.int64)
    p = dict(props)
    p["source"] = f"C1 row {cell} (recorded held {r['result']['held']['acc']:.3f}); env trials -> {env.trials}"
    return Fixture(name, ph, env, g, p, seed=int(r["search_seed"]) & 0xFFFFFFFF, row=r)


def c1_relay() -> Fixture:
    # torus 100 r3, flood to all; one-hop relay at d=1 (harvest audit: evolved transport is one hop)
    return c1("b059e735fe16de49", "c1_relay", {"comm": True, "timing": None, "directed": False, "local": False})


def c1_maj() -> Fixture:
    return c1("88a1a041197e2661", "c1_maj", {"comm": True, "timing": None, "directed": False, "local": False})


def c1_hold() -> Fixture:
    # recorded zero_comm == held: a local mechanism
    return c1("523e5f65ce7102ef", "c1_hold", {"comm": False, "timing": None, "directed": False, "local": True})


def sel_random() -> Fixture:
    """Selection fixture: relay64 physics/env with a RANDOM population (pop 16) so champion selection is real
    and selection bias exists (used only by reuse_selection_seeds)."""
    f = relay64()
    return Fixture("sel_random", f.ph, f.env, f.genome,
                   {"comm": None, "timing": None, "directed": False, "local": None, "selection": True,
                    "source": "16 partially working mutants of relay_flood (search.mutate p_field .04, kept iff screen "
                              "acc in (.55, .90) on a private screen namespace); uniform random genomes are "
                              "silent (every one scores .5), so they cannot show selection bias"})


_POOL = {}


def selection_pool(f: Fixture, n: int = 16) -> np.ndarray:
    """Deterministic pool of partially working mutants, screened on worlds disjoint from every pipeline
    namespace (screen base 0x5C2EE7)."""
    if f.name in _POOL:
        return _POOL[f.name]
    from prometheus.ananke import assays, search
    g = np.random.default_rng(0x5E1EC7)
    msp = search.SearchSpec(p_field=0.04, p_instr=0.0, p_swap=0.0)
    keep = []
    while len(keep) < n:
        cand = np.stack([search.mutate(g, f.genome, msp) for _ in range(32)])
        r = assays.evaluate(f.ph, cand, f.env, assays.world_seeds(0x5C2EE7, 16), device="cpu")
        keep += [c for c, a in zip(cand, r.mean()) if 0.55 < a < 0.90]
    _POOL[f.name] = np.stack(keep[:n])
    return _POOL[f.name]


ALL = {f.__name__: f for f in (sel_random, relay64, hold64, echo, random_dir, xor_hp, flip_hp, c1_relay, c1_maj, c1_hold)}


def get(name: str) -> Fixture:
    for fn in ALL.values():
        if fn.__name__ == name:
            return fn()
    for fn in ALL.values():
        f = fn()
        if f.name == name:
            return f
    raise KeyError(name)

"""Shared B1 plumbing: world construction, the action tensor, the wforge reference
trace, and hashing a recorded state log exactly the way Encounter hashes it.

wforge is READ ONLY (production seat): imported from the tree, never edited.
"""
from __future__ import annotations

import hashlib
import pathlib
import sys

import numpy as np

_WF = pathlib.Path(__file__).resolve().parents[3] / "SerendipityFoundry" / "worldfoundry"
if str(_WF) not in sys.path:
    sys.path.insert(0, str(_WF))

from wforge import GRAMMAR_VERSION  # noqa: E402
from wforge.genome import de_novo  # noqa: E402
from wforge.world import M, Encounter, expand, stream  # noqa: E402

MASK64 = (1 << 64) - 1


def make_world(gen_seed: int):
    g = de_novo(GRAMMAR_VERSION, gen_seed)
    return expand(g), g.world_id


def action_tensor(mech, n_envs: int, seed: int, abstain_p: float = 0.6) -> np.ndarray:
    """int32 [T, n_envs, n_slots, act_width]; values in [0,16) so `% 8` is exercised,
    ~abstain_p of (tick, env, slot) rows zeroed so episodes are not all drained."""
    rng = np.random.default_rng(seed)
    T, S, W = mech.horizon, mech.n_slots, mech.act_width
    a = rng.integers(0, 16, size=(T, n_envs, S, W), dtype=np.int32)
    a *= (rng.random((T, n_envs, S, 1)) >= abstain_p)
    return a


def episode_seeds(n_envs: int, base: int = 7000) -> np.ndarray:
    return np.arange(base, base + n_envs, dtype=np.int64)


def init_regs(mech, world_id: str, seeds: np.ndarray) -> np.ndarray:
    return np.array([[stream("init", world_id, int(s), i).below(M) for i in range(mech.n_regs)]
                     for s in seeds], dtype=np.int64).reshape(len(seeds), mech.n_regs)


def stream_state(*tags) -> int:
    """Raw xorshift state of stream(*tags), for re-implementation elsewhere."""
    return stream(*tags).s


def reference(mech, world_id: str, seed: int, acts_env: np.ndarray, with_obs: bool = False):
    """Run the wforge Encounter. acts_env: [T, S, W]. Returns (trace_hash, obs_hash|None)."""
    e = Encounter(mech, world_id, int(seed))
    oh = hashlib.sha256() if with_obs else None
    done = False
    t = 0
    while not done:
        if with_obs:
            for s in range(mech.n_slots):
                oh.update(bytes(str((t, s, e.observe(s))), "ascii"))
        done = e.step([[int(x) for x in acts_env[t, s]] for s in range(mech.n_slots)])
        t += 1
    return e.outcome()["trace_hash"], (oh.hexdigest() if with_obs else None)


def _lst(row) -> str:
    return "[" + ", ".join(str(int(v)) for v in row) + "]"


def _blst(row) -> str:
    return "[" + ", ".join("True" if v else "False" for v in row) + "]"


def hash_log(regs: np.ndarray, charge: np.ndarray, alive: np.ndarray, n_ticks: int) -> str:
    """regs [T,R], charge [T,S], alive [T,S] (post-step state per tick) -> Encounter trace hash."""
    h = hashlib.sha256()
    for t in range(n_ticks):
        h.update(bytes(f"({t}, {_lst(regs[t])}, {_lst(charge[t])}, {_blst(alive[t])})", "ascii"))
    return h.hexdigest()


def hash_obs(obs: np.ndarray, n_ticks: int) -> str:
    """obs [T,S,D] (pre-step observation per tick and slot) -> reference obs hash."""
    h = hashlib.sha256()
    for t in range(n_ticks):
        for s in range(obs.shape[1]):
            h.update(bytes(f"({t}, {s}, {_lst(obs[t, s])})", "ascii"))
    return h.hexdigest()

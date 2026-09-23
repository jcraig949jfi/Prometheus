"""World identity and evaluation: one node = (family, version, params)."""
from __future__ import annotations

from typing import Any, Dict

import numpy as np

from prometheus.cosmos.contract import MECHANISMS, Family
from prometheus.cosmos.hashing import derive_seed, h
from prometheus.cosmos.phenomenon import certify

DEFAULT_EPISODES = 400


def world_id(fam: Family, params: Dict[str, Any]) -> str:
    return h({"family": fam.name, "family_version": fam.version, "params": params})


def evaluate(fam: Family, params: Dict[str, Any], replicate: int = 0, episodes: int = DEFAULT_EPISODES,
             campaign: str = "c0") -> Dict[str, Any]:
    """Run the three reference mechanisms on common random numbers and certify.

    The seed is derived from (campaign, family, world id, replicate), never shared across families.
    """
    wid = world_id(fam, params)
    seed = derive_seed(campaign, fam.name, wid, replicate) % (2 ** 31)
    obs = {m: fam.run(params, m, seed, episodes) for m in MECHANISMS}
    cert = certify(obs, fam.units(params)["reward_per_success"], boot_seed=seed)
    obs_digest = h({m: {k: np.asarray(v).round(9).tolist() for k, v in o.items()} for m, o in obs.items()})
    meters = {m: {k: float(np.mean(v)) for k, v in o.items() if k not in ("reward", "cost")} for m, o in obs.items()}
    return {"world_id": wid, "family": fam.name, "params": params, "replicate": replicate, "seed": seed,
            "episodes": episodes, "obs_digest": obs_digest, "meters": meters, **cert}

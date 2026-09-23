"""AXIS W generator: PROCEDURAL sampling of composed worlds with complete provenance.

    rec = sample_world(seed, lane="PROCEDURAL", bin_target=None)
    -> {"schema", "params" (the ComposedWorld params), "provenance", "complexity_bin", "world_id"}

The distribution: each feature is switched on with probability p_on (default .5; bin_target forces a
feature count), parameters drawn from published ranges. No feature is chosen for being interesting;
the sampler has no opinion. Every record carries generator id + version + seed + the draws, so a
world is reproducible from its record and nothing else. HUMAN_DIRECTED / LLM_PROPOSED worlds use
the same record shape with their lane label and a `rationale` field the sampler never fills.
"""
from __future__ import annotations

from proteus.foundry.prng import SplitMix64, seed_from
from archaeon.campaign6 import schemas as S
from .runtime import ComposedWorld, FEATURES

GENERATOR = "archaeon.c6.world_gen"
VERSION = "0.1"
RANGES = {
    "resources": {"types": (1, 6), "regen": (0.0, 0.3), "deplete": (0.2, 0.9)},
    "locality": {"nodes": (2, 12)},
    "objects": {"cells": (1, 6), "bonus": (0.1, 1.0)},
    "delayed": {"d": (1, 6)},
    "hidden": {"noise": (0.0, 0.6)},
    "hazards": {"cost": (0.05, 0.5), "lethal": (0, 1)},
    "history": {"k": (1, 6), "pool": (0, 5)},
    "coupling": {},
    "regime": {"every": (4, 16), "regen_factor": (0.2, 0.9)},
    "channels": {"k": (2, 4)},
}


def _draw(rng: SplitMix64, lo, hi):
    if isinstance(lo, int) and isinstance(hi, int):
        return rng.randint(lo, hi)
    return round(lo + (hi - lo) * (rng.next_u32() / 2 ** 32), 3)


def sample_world(seed: int, *, lane: str = "PROCEDURAL", bin_target: int | None = None, p_on: float | None = None, ticks: int = 24, rationale: str = "") -> dict:
    """p_on is retained in the record for compatibility; the count is drawn uniformly over 0..len(FEATURES) (v0.1)."""
    rng = SplitMix64(seed_from(GENERATOR, VERSION, seed))
    n_on = rng.randint(0, len(FEATURES)) if bin_target is None else max(0, min(len(FEATURES), bin_target))
    idx = list(range(len(FEATURES)))
    for i in range(len(idx) - 1, 0, -1):                          # Fisher-Yates with the same stream
        j = rng.randbelow(i + 1); idx[i], idx[j] = idx[j], idx[i]
    on = [FEATURES[i] for i in sorted(idx[:n_on])]
    params = {"ticks": ticks}
    draws = {}
    for f in FEATURES:
        if f not in on:
            params[f] = {"on": False}; continue
        pf = {"on": True}
        for k, (lo, hi) in RANGES[f].items():
            v = _draw(rng, lo, hi); pf[k] = bool(v) if k == "lethal" else v
        params[f] = pf; draws[f] = {k: v for k, v in pf.items() if k != "on"}
    if params["channels"]["on"] is False:
        params["channels"] = {"on": True, "k": 1}                  # the base: one action channel; "channels" is a feature only at k >= 2
    world = ComposedWorld(params)
    prov = S.provenance(lane, GENERATOR, VERSION, seed, {"p_on": p_on, "bin_target": bin_target, "ticks": ticks, "draws": draws}, note=rationale)
    return {"schema": "archaeon.c6.world_record.v1", "kind": "c6.composed.v1", "params": params, "provenance": prov, "complexity_bin": world.complexity_bin(),
            "features": world.features, "world_id": world.world_id(), "name": world.name}


def world_from_record(rec: dict) -> ComposedWorld:
    return ComposedWorld(rec["params"])

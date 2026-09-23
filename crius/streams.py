"""Lifetime dispatch by world: one entry point for search, qualify, baselines and the gate."""

from __future__ import annotations

from . import tasks as tasks_c0


def world_id(cfg: dict) -> str:
    return cfg.get("world", {}).get("id", "c0")


def lifetime(cfg: dict, seed: int, suite: str) -> list:
    """suite: c0 -> 'search' | 'heldout_v1'; c1 -> 'search' | 'qual' | 'gate' (a namespace)."""
    if world_id(cfg) == "c1":
        from . import tasks_c1
        return tasks_c1.make_stream(cfg, suite, seed)["tasks"]
    return tasks_c0.make_lifetime(cfg, seed, suite)


def search_stream_seed(cfg: dict, iteration: int, base_seed: int) -> int:
    """Rotating streams (DESIGN_C1 s2): a new stream per iteration, common to the whole population."""
    st = cfg.get("streams", {})
    if st.get("rotate", False):
        return st.get("base", 1000) + 100000 * base_seed + iteration
    return base_seed


def qualification_suite(cfg: dict) -> str:
    return "qual" if world_id(cfg) == "c1" else "heldout_v1"


def fingerprints(cfg: dict) -> dict:
    if world_id(cfg) == "c1":
        from . import tasks_c1, world_c1
        return {"world_fingerprint": world_c1.world_fingerprint(),
                "partitions_fingerprint": tasks_c1.generator_fingerprint(cfg)}
    from . import world
    parts = tasks_c0.build_partitions(cfg)
    return {"world_fingerprint": world.world_fingerprint(),
            "partitions_fingerprint": tasks_c0.partitions_fingerprint(parts)}

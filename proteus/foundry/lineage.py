"""Lineage, descent, checkpoints. Append-only; every record content-addressed.

A descendant record carries every field brief S8 requires: parent(s), mutation seed, exact
operators, pre/post hashes, state inheritance policy, resource budget, runtime version. Records
are never edited. A checkpoint is a content-addressed snapshot of a player's state bound to the
encounter and tick it was taken at, so that any adaptive transition can be replayed from it.
"""
from __future__ import annotations

from .generate import organism_record
from .grammar import GRAMMAR_HASH, GRAMMAR_VERSION, GRAMMARS, mutate
from .identity import RUNTIME_HASH, hash_obj
from .prng import SplitMix64, seed_from

LINEAGE_SCHEMA = "proteus.lineage_record.v0"
CHECKPOINT_SCHEMA = "proteus.checkpoint.v0"
STATE_INHERITANCE = ("PRISTINE", "INHERIT")


def descend(parent: dict, mutation_seed: int, mate: dict | None = None,
            state_inheritance: str = "PRISTINE", n_ops: int = 1, force_operator: str | None = None,
            grammar_version: str = GRAMMAR_VERSION):
    """Produce one child organism and its lineage record from one parent (and an optional mate).

    mutation_seed is the caller's; the operator stream is derived from (seed, parent id, mate id)
    so that the same seed on the same parent always yields the same child.
    """
    if state_inheritance not in STATE_INHERITANCE:
        raise ValueError("unknown state inheritance policy")
    rng = SplitMix64(seed_from("proteus.descend.v0", mutation_seed, parent["organism_id"],
                               mate["organism_id"] if mate else "",
                               GRAMMARS[grammar_version][3]))
    m = parent["manifest"]
    ops = []
    for _ in range(n_ops):
        m, rec = mutate(m, rng, mate["manifest"] if mate else None, force_operator,
                        version=grammar_version)
        ops.append(rec)
    child = organism_record(m, parent["lineage_id"], parent["generation"] + 1)
    record = {
        "schema_version": LINEAGE_SCHEMA,
        "organism_id": child["organism_id"],
        "lineage_id": child["lineage_id"],
        "generation": child["generation"],
        "parent_ids": [parent["organism_id"]] + ([mate["organism_id"]] if mate else []),
        "mutation_seed": mutation_seed,
        "operators": ops,
        "pre_hash": parent["organism_id"],
        "post_hash": child["organism_id"],
        "state_inheritance_policy": state_inheritance,
        "resource_budget": {k: m[k] for k in ("tick_budget", "tape_words", "n_regs", "out_cap")},
        "runtime_hash": RUNTIME_HASH,
        "grammar_hash": GRAMMARS[grammar_version][3],
        "grammar_version": grammar_version,
    }
    record["record_id"] = hash_obj(record)
    return child, record


def checkpoint(organism_id: str, state: dict, encounter_id: str | None, tick: int) -> dict:
    snap = {
        "schema_version": CHECKPOINT_SCHEMA,
        "organism_id": organism_id,
        "encounter_id": encounter_id,
        "tick": tick,
        "runtime_hash": RUNTIME_HASH,
        "state": {"tape": list(state["tape"]), "regs": list(state["regs"]),
                  "ip": state["ip"], "ticks": state["ticks"]},
    }
    snap["checkpoint_id"] = hash_obj(snap)
    return snap


def restore(snap: dict) -> dict:
    if snap["runtime_hash"] != RUNTIME_HASH:
        raise ValueError("checkpoint was taken under a different runtime; refusing to restore")
    s = snap["state"]
    return {"tape": list(s["tape"]), "regs": list(s["regs"]), "ip": s["ip"], "ticks": s["ticks"]}

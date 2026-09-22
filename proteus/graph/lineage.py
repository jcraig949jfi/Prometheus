"""Descent for graph organisms: proteus.lineage_record.v1 = v0's fields + the explicit edit list.

A child's genome is `apply_edits(parent.manifest, concat(op.edits))` and the record says so;
`verify_record(parent, child, record)` replays the edits and refuses any record that does not
rebuild the child byte for byte. Records are never edited.
"""
from __future__ import annotations

from proteus.foundry.prng import SplitMix64, seed_from

from .generate import organism_record
from .grammar import GRAMMAR_HASH, GRAMMAR_VERSION, apply_edits, mutate
from .identity import RUNTIME_HASH, hash_obj

LINEAGE_SCHEMA = "proteus.lineage_record.v1"
STATE_INHERITANCE = ("PRISTINE", "INHERIT")


def descend(parent: dict, mutation_seed: int, mate: dict | None = None,
            state_inheritance: str = "PRISTINE", n_ops: int = 1, force_operator: str | None = None):
    if state_inheritance not in STATE_INHERITANCE:
        raise ValueError("unknown state inheritance policy")
    rng = SplitMix64(seed_from("proteus.graph.descend.v1", mutation_seed, parent["organism_id"],
                               mate["organism_id"] if mate else "", GRAMMAR_HASH))
    m = parent["manifest"]
    ops = []
    for _ in range(n_ops):
        m, rec = mutate(m, rng, mate["manifest"] if mate else None, force_operator)
        ops.append(rec)
    child = organism_record(m, parent["lineage_id"], parent["generation"] + 1)
    record = {
        "schema_version": LINEAGE_SCHEMA,
        "organism_id": child["organism_id"],
        "lineage_id": child["lineage_id"],
        "generation": child["generation"],
        "parent_ids": [parent["organism_id"]] + ([mate["organism_id"]] if mate else []),
        "mutation_seed": mutation_seed,
        "operators": ops,                       # each: operator, edits, pre_hash, post_hash, noop
        "edits": [e for rec in ops for e in rec["edits"]],
        "pre_hash": parent["organism_id"],
        "post_hash": child["organism_id"],
        "state_inheritance_policy": state_inheritance,
        "resource_budget": {k: m[k] for k in ("tick_budget", "state_words", "out_cap", "call_depth_max")},
        "n_nodes": {"parent": len(parent["manifest"]["nodes"]), "child": len(m["nodes"])},
        "runtime_hash": RUNTIME_HASH,
        "grammar_hash": GRAMMAR_HASH,
        "grammar_version": GRAMMAR_VERSION,
    }
    record["record_id"] = hash_obj(record)
    return child, record


def verify_record(parent_manifest: dict, record: dict) -> dict:
    """Replay the record's edits on the parent; return the rebuilt child manifest or raise."""
    rebuilt = apply_edits(parent_manifest, record["edits"])
    if hash_obj(rebuilt) != record["post_hash"]:
        raise ValueError("edits do not rebuild the child")
    if hash_obj(parent_manifest) != record["pre_hash"]:
        raise ValueError("record does not belong to this parent")
    body = {k: v for k, v in record.items() if k != "record_id"}
    if hash_obj(body) != record["record_id"]:
        raise ValueError("record_id does not recompute")
    return rebuilt

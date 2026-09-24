"""The substrate HANDOVER for Campaign 6 executors (Archaeon's segment loop, Vivarium's kind): one
dispatch table keyed on the manifest's schema_version, with the exact call shapes the consumers
already use for v0 (archaeon/wse/evolve.py: Player(m), Meter(), meter.as_dict(m),
G.organism_record(m, lineage, gen), descend(parent, seed, mate=...)).

    substrate_of(manifest)                 -> "v0" | "graph"
    player_for(manifest)                   -> proteus.foundry.vm.Player | proteus.graph.vm.GraphPlayer
    meter_for(manifest)                    -> Meter() | GraphMeter(n_nodes)     (both .as_dict(manifest))
    organism_record_for(m, lineage, gen)   -> record stamped with the RIGHT runtime_hash
    descend_for(parent, seed, mate=None)   -> (child, lineage_record)  v0 -> lineage_record.v0, graph -> .v1
    generate_for(foundry_manifest)         -> population for either foundry schema
    fingerprint_for(manifest, meter_dict, ...) -> proteus.behavior_fingerprint.v1 row
    PROFILES                               -> the two profile ids + hashes, for receipts

An executor that replaces its five v0 calls with these runs both substrates unchanged, and a v0
manifest can never receive the graph runtime hash or vice versa (asserted in test_graph_handover.py).
The world ABI is identical (A1 channels): run_tick(state, inputs, n_out, rng, meter) on both.

Nothing here evaluates against a world or scores; `answers`/`evaluate` stay the executor's, built on
player_for.
"""
from __future__ import annotations

from proteus.eval import fingerprint as FP
from proteus.foundry import generate as G0
from proteus.foundry import lineage as L0
from proteus.foundry.identity import RUNTIME_HASH as V0_RUNTIME_HASH
from proteus.foundry.vm import SCHEMA as V0_SCHEMA
from proteus.foundry.vm import Meter, Player
from proteus.graph import generate as G1
from proteus.graph import grammar as GR1
from proteus.graph import lineage as L1
from proteus.graph.identity import RUNTIME_HASH as GRAPH_RUNTIME_HASH
from proteus.graph.vm import SCHEMA as GRAPH_SCHEMA
from proteus.graph.vm import GraphMeter, GraphPlayer

PROFILES = {
    "v0": {"manifest_schema": V0_SCHEMA, "runtime_hash": V0_RUNTIME_HASH, "runtime_version": "proteus.runtime.v0",
           "grammar_version": "proteus.grammar.v0.4", "catalog": "proteus/eval/FOUNDRY_PROFILE_CATALOG.json",
           "foundry_schema": G0.FOUNDRY_SCHEMA},
    "graph": {"manifest_schema": GRAPH_SCHEMA, "runtime_hash": GRAPH_RUNTIME_HASH, "runtime_version": "proteus.runtime.graph.v1",
              "grammar_version": GR1.GRAMMAR_VERSION, "grammar_hash": GR1.GRAMMAR_HASH,
              "catalog": "proteus/graph/GRAPH_PROFILE_CATALOG.json", "foundry_schema": G1.FOUNDRY_SCHEMA},
}
_BY_SCHEMA = {V0_SCHEMA: "v0", GRAPH_SCHEMA: "graph"}
_BY_FOUNDRY = {G0.FOUNDRY_SCHEMA: "v0", G1.FOUNDRY_SCHEMA: "graph"}


def substrate_of(manifest: dict) -> str:
    try:
        return _BY_SCHEMA[manifest["schema_version"]]
    except KeyError:
        raise ValueError("unknown manifest schema %r" % manifest.get("schema_version"))


def player_for(manifest: dict):
    return Player(manifest) if substrate_of(manifest) == "v0" else GraphPlayer(manifest)


def meter_for(manifest: dict):
    return Meter() if substrate_of(manifest) == "v0" else GraphMeter(len(manifest["nodes"]))


def organism_record_for(manifest: dict, lineage_id: str | None, generation: int) -> dict:
    if substrate_of(manifest) == "v0":
        return G0.organism_record(manifest, lineage_id, generation)
    return G1.organism_record(manifest, lineage_id, generation)


def descend_for(parent: dict, mutation_seed: int, mate: dict | None = None, **kw):
    sub = substrate_of(parent["manifest"])
    if mate is not None and substrate_of(mate["manifest"]) != sub:
        raise ValueError("mate is from another substrate; no cross-substrate descent exists")
    if sub == "v0":
        return L0.descend(parent, mutation_seed, mate=mate, **kw)
    return L1.descend(parent, mutation_seed, mate=mate, **kw)


def generate_for(foundry_manifest: dict) -> list:
    try:
        sub = _BY_FOUNDRY[foundry_manifest["schema_version"]]
    except KeyError:
        raise ValueError("unknown foundry schema %r" % foundry_manifest.get("schema_version"))
    return G0.generate(foundry_manifest) if sub == "v0" else G1.generate(foundry_manifest)


def fingerprint_for(manifest: dict, meter_dict: dict, *, organism_id: str, parent_id: str | None,
                    eval_ordinal: int, logical_time: int, outputs: list, extra: dict | None = None) -> dict:
    if substrate_of(manifest) == "v0":
        beh = FP.from_v0_meter(meter_dict)
    else:
        from proteus.graph.vm import live_nodes
        n_dormant = len(manifest["nodes"]) - len(live_nodes(manifest))
        beh = FP.from_graph_meter(meter_dict, n_dormant)
    return FP.fingerprint(organism_id=organism_id, parent_id=parent_id, eval_ordinal=eval_ordinal,
                          logical_time=logical_time, behaviour=beh, outputs=outputs, extra=extra)

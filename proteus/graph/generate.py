"""Deterministic generation of graph organisms from a compact graph-foundry manifest.

Same discipline as proteus/foundry/generate.py: same manifest + same runtime => byte-identical
population; the generator holds no opinion about which kinds or wirings are common (kinds
uniform over the table; edges uniform over admissible ports at the declared densities). Whatever
bias exists is the affordance table's own, which is published and hashed.
"""
from __future__ import annotations

from proteus.foundry.prng import SplitMix64, seed_from

from .affordances import BOUNDS, CONTROL_OUT, DATA_IN, N_KINDS, N_PARAMS
from .identity import RUNTIME_HASH, hash_obj
from .vm import MASK32, SCHEMA, canonicalize, validate_manifest

FOUNDRY_SCHEMA = "proteus.graph_foundry_manifest.v1"

DEFAULT_FOUNDRY_MANIFEST = {
    "schema_version": FOUNDRY_SCHEMA,
    "seed": 0,
    "n": 0,
    "n_nodes_range": [2, 24],
    "data_edge_density_range": [0.0, 1.0],      # fraction of data-in ports wired
    "control_edge_density_range": [0.2, 1.0],   # fraction of control-out ports wired
    "persist_node_weights": [3, 1],             # [false, true]
    "persist_state_weights": [1, 1],            # [false, true]
    "state_words_choices": [4, 16, 64, 256],
    "tick_budget_choices": [16, 64, 256, 1024],
    "out_cap_choices": [1, 4, 16],
    "call_depth_choices": [0, 2, 8],
}


def validate_foundry_manifest(fm: dict) -> None:
    if fm.get("schema_version") != FOUNDRY_SCHEMA:
        raise ValueError("graph foundry manifest schema mismatch")
    b = BOUNDS
    lo, hi = fm["n_nodes_range"]
    if not (b["n_nodes"]["min"] <= lo <= hi <= b["n_nodes"]["max"]):
        raise ValueError("n_nodes_range outside bounds")
    for key in ("data_edge_density_range", "control_edge_density_range"):
        lo, hi = fm[key]
        if not (0.0 <= lo <= hi <= 1.0):
            raise ValueError("%s invalid" % key)
    for key, bkey in (("state_words_choices", "state_words"), ("tick_budget_choices", "tick_budget"),
                      ("out_cap_choices", "out_cap"), ("call_depth_choices", "call_depth_max")):
        for t in fm[key]:
            if not (b[bkey]["min"] <= t <= b[bkey]["max"]):
                raise ValueError("%s choice invalid" % key)
    if len(fm["persist_node_weights"]) != 2 or len(fm["persist_state_weights"]) != 2:
        raise ValueError("weight vectors wrong length")
    if not isinstance(fm["n"], int) or fm["n"] < 0:
        raise ValueError("n invalid")


def sample_manifest(fm: dict, rng: SplitMix64) -> dict:
    n = rng.randint(fm["n_nodes_range"][0], fm["n_nodes_range"][1])
    nodes = []
    for _ in range(n):
        k = rng.randbelow(N_KINDS)
        params = [rng.next_u32() & MASK32 for _ in range(N_PARAMS[k])]
        persist = rng.weighted([False, True], fm["persist_node_weights"])
        nodes.append({"kind": k, "params": params, "persist": persist})
    dlo, dhi = fm["data_edge_density_range"]
    clo, chi = fm["control_edge_density_range"]
    ddens = dlo + (dhi - dlo) * rng.unit()
    cdens = clo + (chi - clo) * rng.unit()
    data_edges, control_edges = [], []
    for d in range(n):
        for p in range(DATA_IN[nodes[d]["kind"]]):
            if rng.unit() < ddens:
                data_edges.append([rng.randbelow(n), d, p])
    for s in range(n):
        for p in range(CONTROL_OUT[nodes[s]["kind"]]):
            if rng.unit() < cdens:
                control_edges.append([s, p, rng.randbelow(n)])
    m = {
        "schema_version": SCHEMA,
        "nodes": nodes,
        "data_edges": data_edges,
        "control_edges": control_edges,
        "entry": rng.randbelow(n),
        "state_words": rng.choice(fm["state_words_choices"]),
        "tick_budget": rng.choice(fm["tick_budget_choices"]),
        "out_cap": rng.choice(fm["out_cap_choices"]),
        "call_depth_max": rng.choice(fm["call_depth_choices"]),
        "persist_state": rng.weighted([False, True], fm["persist_state_weights"]),
    }
    return canonicalize(m)


def organism_record(manifest: dict, lineage_id: str | None, generation: int) -> dict:
    oid = hash_obj(manifest)
    return {"organism_id": oid, "lineage_id": lineage_id or oid, "generation": generation,
            "runtime_hash": RUNTIME_HASH, "manifest": manifest}


def generate(fm: dict) -> list:
    validate_foundry_manifest(fm)
    root = SplitMix64(seed_from("proteus.graph.generate.v1", fm["seed"], RUNTIME_HASH))
    return [organism_record(sample_manifest(fm, root.derive("organism", i)), None, 0) for i in range(fm["n"])]

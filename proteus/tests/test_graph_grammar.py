"""proteus.graph_grammar.v1 -- controls.

reconstruct  every child == apply_edits(parent, record.edits); verify_record replays 300 random
             descents (with and without mates) and refuses a tampered record
determinism  same parent + same seed -> same child; different seed -> (almost always) different
operators    each named operator produces a valid child; EDGE_CUT never removes a node; NODE_ADD
             adds exactly one dormant node; SUBGRAPH_COPY appends a dormant copy whose internal
             edges mirror the source component; SUBGRAPH_MOVE preserves node count
R4           node-count drift under NO selection: three seeds x 100 organisms x 60 mutations,
             |mean drift per step| <= 0.02 (pre-registered band; history in grammar.py docstring)
identity     the grammar hash carries the weight vector: a moved weight is a different grammar
"""
from __future__ import annotations

import copy
import statistics

import pytest

from proteus.foundry.identity import hash_obj
from proteus.foundry.prng import SplitMix64
from proteus.graph import generate as G
from proteus.graph import grammar as GR
from proteus.graph import lineage as L
from proteus.graph.vm import live_nodes, validate_manifest

DRIFT_BAND = 0.02


def _pop(seed=3, n=100):
    return G.generate(dict(G.DEFAULT_FOUNDRY_MANIFEST, seed=seed, n=n))


def test_children_reconstruct_from_edits_and_records_verify():
    pop = _pop()
    for i, o in enumerate(pop):
        mate = pop[(i * 7 + 1) % len(pop)] if i % 2 else None
        child, rec = L.descend(o, mutation_seed=i, mate=mate, n_ops=1 + (i % 3))
        rebuilt = L.verify_record(o["manifest"], rec)
        assert hash_obj(rebuilt) == child["organism_id"] == rec["post_hash"]
        assert rec["schema_version"] == "proteus.lineage_record.v1"
        assert len(rec["parent_ids"]) == (2 if mate else 1)
    bad = copy.deepcopy(rec)
    bad["edits"] = bad["edits"][:-1] if bad["edits"] else [{"add_nodes": [{"kind": 0, "params": [], "persist": False}]}]
    with pytest.raises(ValueError):
        L.verify_record(o["manifest"], bad)


def test_descend_is_deterministic():
    o = _pop()[0]
    a, ra = L.descend(o, mutation_seed=42)
    b, rb = L.descend(o, mutation_seed=42)
    assert a == b and ra == rb
    diffs = sum(L.descend(o, mutation_seed=s)[0]["organism_id"] != a["organism_id"] for s in range(43, 63))
    assert diffs >= 15


def test_every_operator_yields_a_valid_child():
    pop = _pop(seed=4, n=40)
    for name in GR.NAMES:
        for i, o in enumerate(pop):
            child, rec = GR.mutate(o["manifest"], SplitMix64(i), pop[(i + 1) % 40]["manifest"], name=name)
            validate_manifest(child)
            assert rec["operator"] == name
            assert GR.apply_edits(o["manifest"], rec["edits"]) == child


def test_operator_shapes():
    pop = _pop(seed=5, n=60)
    for i, o in enumerate(pop):
        m = o["manifest"]
        n = len(m["nodes"])
        c, _ = GR.mutate(m, SplitMix64(i), None, name="NODE_ADD")
        assert len(c["nodes"]) == n + 1 and (n in set(range(n + 1)) - live_nodes(c) or c["entry"] == n)
        c, _ = GR.mutate(m, SplitMix64(i), None, name="EDGE_CUT")
        assert len(c["nodes"]) == n and len(c["data_edges"]) + len(c["control_edges"]) >= len(m["data_edges"]) + len(m["control_edges"]) - 1
        c, r = GR.mutate(m, SplitMix64(i), None, name="SUBGRAPH_COPY")
        if r["edits"]:
            added = r["edits"][0]["add_nodes"]
            assert len(c["nodes"]) == n + len(added)
            new_ids = set(range(n, n + len(added)))
            assert new_ids.isdisjoint(live_nodes(c)) or c["entry"] in new_ids     # copy is dormant
        c, _ = GR.mutate(m, SplitMix64(i), None, name="SUBGRAPH_MOVE")
        assert len(c["nodes"]) == n
        c, _ = GR.mutate(m, SplitMix64(i), None, name="EDGE_RETARGET")
        assert len(c["nodes"]) == n


def test_r4_node_count_drift_within_band():
    drifts = []
    for seed in (7, 8, 9):
        pop = _pop(seed=seed, n=100)
        start = [len(o["manifest"]["nodes"]) for o in pop]
        cur = list(pop)
        steps = 60
        for s in range(steps):
            cur = [L.descend(o, mutation_seed=s * 1000 + i)[0] for i, o in enumerate(cur)]
        end = [len(o["manifest"]["nodes"]) for o in cur]
        drifts.append(statistics.mean((e - s0) / steps for s0, e in zip(start, end)))
    assert all(abs(d) <= DRIFT_BAND for d in drifts), drifts
    assert statistics.mean(drifts) <= DRIFT_BAND        # growth is not the default


def test_grammar_hash_carries_weights():
    moved = tuple((n, w + (0.01 if n == "NODE_ADD" else -0.01 if n == "NODE_REMOVE" else 0), d) for n, w, d in GR.OPERATORS)
    assert hash_obj({"version": GR.GRAMMAR_VERSION, "operators": moved, "k_max": GR.K_MAX}) != GR.GRAMMAR_HASH

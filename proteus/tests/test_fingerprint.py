"""proteus.behavior_fingerprint.v1 -- controls.

repro    40/40 identical rows for the same organism on the same inputs (v0 and graph); the v0 row
         is identical although the raw meter's wall_s/cpu_s differ between runs
cap      every row <= 1 KiB canonical JSON, including a 256-node graph organism (long vectors digested)
envelope the consumer's required keys {eval, lt, organism_id, parent_id, digest} present; verify()
         recomputes the digest and refuses a tampered row
cheat    a producer `extra` block carrying reward / fitness / heldout / world_id is REFUSED
sensitivity a different input sequence changes the digest; a different organism changes it
"""
from __future__ import annotations

import copy

import pytest

from proteus.eval import fingerprint as F
from proteus.eval.keyed_memory_witness import keyed_memory_genome, manifest_for, one_value_genome
from proteus.foundry.identity import canonical_json
from proteus.foundry.prng import SplitMix64
from proteus.foundry.vm import Meter, Player
from proteus.graph import generate as G
from proteus.graph.affordances import BOUNDS
from proteus.graph.vm import GraphMeter, GraphPlayer

INPUTS = [[3, 9, 3], [1001, 2002]]


def _v0_row(manifest, inputs=INPUTS, ticks=3):
    p = Player(manifest); st = p.fresh_state(); rng = SplitMix64(0); mt = Meter(); outs = []
    for _ in range(ticks):
        o, _s = p.run_tick(st, inputs, 1, rng, meter=mt); outs.append(o); st["ticks"] += 1
    md = mt.as_dict(manifest)
    return F.fingerprint(organism_id="o1", parent_id=None, eval_ordinal=1, logical_time=0,
                         behaviour=F.from_v0_meter(md), outputs=[sum((x[0] for x in outs), [])]), md


def _graph_row(manifest, inputs=INPUTS, ticks=3, oid="g1"):
    p = GraphPlayer(manifest); st = p.fresh_state(); rng = SplitMix64(0); mt = GraphMeter(p.n); outs = []
    for _ in range(ticks):
        o, _s = p.run_tick(st, inputs, 1, rng, meter=mt); outs.append(o); st["ticks"] += 1
    return F.fingerprint(organism_id=oid, parent_id="g0", eval_ordinal=7, logical_time=2,
                         behaviour=F.from_graph_meter(mt.as_dict(), len(p.dormant)), outputs=[sum((x[0] for x in outs), [])])


def test_v0_row_reproduces_40_of_40_despite_timings():
    m = manifest_for(keyed_memory_genome(48))
    rows, timings = [], set()
    for _ in range(40):
        row, md = _v0_row(m)
        rows.append(canonical_json(row)); timings.add((md["wall_s"], md["cpu_s"]))
    assert len(set(rows)) == 1
    assert "wall_s" not in rows[0] and "cpu_s" not in rows[0]


def test_graph_row_reproduces_40_of_40_and_fits_cap_at_max_nodes():
    fm = dict(G.DEFAULT_FOUNDRY_MANIFEST, seed=11, n=5, n_nodes_range=[BOUNDS["n_nodes"]["max"], BOUNDS["n_nodes"]["max"]],
              control_edge_density_range=[1.0, 1.0], data_edge_density_range=[1.0, 1.0])
    for o in G.generate(fm):
        rows = {canonical_json(_graph_row(o["manifest"], oid=o["organism_id"])) for _ in range(40)}
        assert len(rows) == 1
        assert len(rows.pop().encode("utf-8")) <= F.ROW_BYTES_MAX


def test_envelope_and_verify():
    m = manifest_for(keyed_memory_genome(48))
    row, _ = _v0_row(m)
    for k in ("eval", "lt", "organism_id", "parent_id", "digest", "schema_version"):
        assert k in row
    F.verify(row)
    bad = copy.deepcopy(row); bad["behaviour"]["ops"] += 1
    with pytest.raises(ValueError):
        F.verify(bad)


def test_cheat_reward_leak_is_refused():
    m = manifest_for(keyed_memory_genome(48))
    p = Player(m); st = p.fresh_state(); mt = Meter(); p.run_tick(st, INPUTS, 1, SplitMix64(0), meter=mt)
    beh = F.from_v0_meter(mt.as_dict(m))
    for extra in ({"reward": 0.5}, {"heldout": {"W2_K2": 1.0}}, {"lineage": {"world_id": "wld_1"}}, {"fitness_rank": 3}):
        with pytest.raises(ValueError, match="forbidden"):
            F.fingerprint(organism_id="o", parent_id=None, eval_ordinal=1, logical_time=0, behaviour=beh, outputs=[[]], extra=extra)
    ok = F.fingerprint(organism_id="o", parent_id=None, eval_ordinal=1, logical_time=0, behaviour=beh, outputs=[[]],
                       extra={"lineage_record": "sha256:abc"})
    F.verify(ok)


def test_sensitivity():
    m = manifest_for(keyed_memory_genome(48))
    a, _ = _v0_row(m); b, _ = _v0_row(m, inputs=[[3], []])                    # PUT ticks vs ASK ticks: outputs differ
    same, _ = _v0_row(m, inputs=[[3, 9, 9], [1001, 2002]])                     # a never-read key: same behaviour
    assert same["digest"] == a["digest"]
    # KNOWN LIMIT of the v0 row (frozen Meter has no address set): a PUT to key 3 and a PUT to key 9
    # are indistinguishable at T0 on v0; the graph meter carries state_addrs and separates them.
    put9, _ = _v0_row(m, inputs=[[9, 3, 3], [1001, 2002]])
    assert put9["digest"] == a["digest"]
    assert a["digest"] != b["digest"]
    m2 = manifest_for(one_value_genome())                                    # a different program
    c, _ = _v0_row(m2)
    assert c["digest"] != a["digest"]
    off, _ = _v0_row(manifest_for(keyed_memory_genome(52)))                   # only the OFFSET constant differs and
    assert off["digest"] == a["digest"]                                        # no ASK is answered: v0 cannot see it

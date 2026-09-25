"""The substrate handover -- dispatch by manifest schema; a consumer's five v0 call shapes run both substrates."""
from __future__ import annotations

import pytest

from proteus.eval.keyed_memory_witness import keyed_memory_genome, manifest_for
from proteus.foundry import generate as G0
from proteus.foundry.identity import RUNTIME_HASH as V0
from proteus.foundry.prng import SplitMix64
from proteus.graph import generate as G1
from proteus.graph import handover as H
from proteus.graph.identity import RUNTIME_HASH as GRAPH
from proteus.graph.witness import keyed_memory_manifest


def _consumer_loop(manifest, inputs, ticks=3):
    """Exactly the shape archaeon/wse/evolve.evaluate uses, with the five calls swapped for the dispatchers."""
    player = H.player_for(manifest)
    meter = H.meter_for(manifest)
    st = player.fresh_state()
    rng = SplitMix64(0)
    outs = []
    for _ in range(ticks):
        player.begin_tick(st)
        o, _status = player.run_tick(st, inputs, 1, rng, meter=meter)
        outs.append(o[0])
        st["ticks"] += 1
    return outs, meter.as_dict(manifest)


def test_same_loop_runs_both_substrates_on_the_same_probe():
    v0 = manifest_for(keyed_memory_genome(48))
    gr = keyed_memory_manifest()
    # PUT (3, 1001) then ASK 3 -> both substrates answer 1001 on the ASK tick
    for m in (v0, gr):
        put, md1 = _consumer_loop(m, [[3], [1001]], ticks=1)
        p = H.player_for(m); st = p.fresh_state(); mt = H.meter_for(m); rng = SplitMix64(0)
        p.run_tick(st, [[3], [1001]], 1, rng, meter=mt); st["ticks"] += 1
        o, _ = p.run_tick(st, [[3], []], 1, rng, meter=mt)
        assert o[0] == [1001]
        assert "footprint" in mt.as_dict(m) or "footprint_words" in mt.as_dict(m)


def test_records_carry_the_right_runtime_hash_and_never_cross():
    v0 = manifest_for(keyed_memory_genome(48))
    gr = keyed_memory_manifest()
    assert H.organism_record_for(v0, None, 0)["runtime_hash"] == V0
    assert H.organism_record_for(gr, None, 0)["runtime_hash"] == GRAPH
    assert V0 != GRAPH
    with pytest.raises(ValueError):
        H.substrate_of({"schema_version": "proteus.other.v9"})


def test_descend_dispatches_and_refuses_cross_substrate_mates():
    pv0 = G0.generate(dict(G0.DEFAULT_FOUNDRY_MANIFEST, seed=1, n=2))
    pg = G1.generate(dict(G1.DEFAULT_FOUNDRY_MANIFEST, seed=1, n=2))
    c0, r0 = H.descend_for(pv0[0], 5, mate=pv0[1])
    c1, r1 = H.descend_for(pg[0], 5, mate=pg[1])
    assert r0["schema_version"] == "proteus.lineage_record.v0" and r1["schema_version"] == "proteus.lineage_record.v1"
    assert c0["runtime_hash"] == V0 and c1["runtime_hash"] == GRAPH
    with pytest.raises(ValueError, match="another substrate"):
        H.descend_for(pv0[0], 5, mate=pg[0])


def test_generate_and_fingerprint_dispatch():
    assert H.generate_for(dict(G0.DEFAULT_FOUNDRY_MANIFEST, seed=2, n=3))[0]["runtime_hash"] == V0
    assert H.generate_for(dict(G1.DEFAULT_FOUNDRY_MANIFEST, seed=2, n=3))[0]["runtime_hash"] == GRAPH
    for m in (manifest_for(keyed_memory_genome(48)), keyed_memory_manifest()):
        outs, md = _consumer_loop(m, [[3], [1001]])
        row = H.fingerprint_for(m, md, organism_id="x", parent_id=None, eval_ordinal=1, logical_time=0, outputs=[sum(outs, [])])
        assert row["behaviour"]["substrate"] == H.substrate_of(m)
    assert set(H.PROFILES) == {"v0", "graph"}

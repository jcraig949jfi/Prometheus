"""Tests for the Z80 x Atlas campaign harness: the VM, the reproduction physics (with the endogenous guard), the
frozen grammar, the geometry instrument, the observatory triggers and the scheduler's mechanics."""
from __future__ import annotations

import json
import random

import pytest

from prometheus.z80atlas import vm, grammar as G, geometry, observatory as O, controls as C
from prometheus.z80atlas.tasks import Task, score, Environment
from prometheus.z80atlas.world import World, Config, ENDOGENOUS


# ---- VM -------------------------------------------------------------------------------------------------------------
def test_vm_witnesses_and_replicator():
    r = C.vm_executes()
    assert r["passed"], r["checks"]


def test_vm_is_sandboxed_and_reinterprets_after_mutation():
    L = 64
    mem = bytearray(256); mem[:8] = vm.replicator(L)
    mem[3] = 0xF0                                   # LD T,0xF0: the copy now runs into the top of the address space and WRAPS
    tr = vm.execute(mem, L, 0, 512, [])
    assert max(tr.writes) <= 0xFF and tr.steps == 512   # nothing outside the sandbox; the copy overwrote its own HALT (self-overwrite) and ran to budget
    prog = bytearray(vm.witness_inc()); prog[1] = 0x41   # INC_A -> OUT_A: the byte is now a different instruction
    mem = bytearray(256); mem[:4] = prog; mem[vm.IN_BASE] = 5
    tr = vm.execute(mem, L, 0, 64, [5])
    assert tr.outputs == [5, 5]                    # IN, OUT, OUT: the mutated byte is reinterpreted, not an error


def test_forced_read_gate_rejects_answer_before_read():
    t = Task("ECHO")
    assert score(t, [7], [7], "ATOMIC", "ABR", first_out_step=1, first_in_step=None) == 1.0
    assert score(t, [7], [7], "ATOMIC", "FORCED", first_out_step=1, first_in_step=None) == 0.0
    assert score(t, [7], [7], "ATOMIC", "FORCED", first_out_step=2, first_in_step=1) == 1.0
    assert 0.0 < score(Task("CONST", k=10), [12], [10], "INCREMENTAL", "ABR", 1, None) < 1.0    # incrementally reachable
    assert score(Task("CONST", k=10), [12], [10], "ATOMIC", "ABR", 1, None) == 0.0               # a zero-fitness valley


# ---- physics --------------------------------------------------------------------------------------------------------
def _cfg(**kw):
    base = dict(ticks=40, cells=64)
    base.update(kw)
    return Config(**base)


def test_endogenous_treatments_never_get_population_manager_reproduction():
    for physics in ENDOGENOUS:
        w = World(_cfg(reproduction=physics, init="SEEDED_REPLICATOR"), 1); s = w.run()
        assert s["external_births"] == 0, physics
        assert s["endogenous_births"] > 0, physics
    with pytest.raises(AssertionError):
        w = World(_cfg(reproduction="ENDOGENOUS_COPY"), 1); w.cfg.reproduction = "ENDOGENOUS_COPY"; w._external_reproduce()


def test_external_control_reproduces_and_evolves():
    w = World(_cfg(reproduction="EXTERNAL", pressure="EXPLICIT", task="INC", scoring="INCREMENTAL", ticks=120, cells=144), 3); s = w.run()
    assert s["external_births"] > 0 and s["endogenous_births"] == 0 and s["first_crossing"] is not None


def test_constructive_refuses_occupied_and_overwrite_refuses_empty():
    wc = World(_cfg(reproduction="CONSTRUCTIVE", init="SEEDED_REPLICATOR"), 2); sc = wc.run()
    assert sc["refused_writes"] > 0 and sc["overwrite_deaths"] == 0        # never replaces a living organism
    wo = World(_cfg(reproduction="OVERWRITE", init="SEEDED_REPLICATOR"), 2); so = wo.run()
    assert so["overwrite_deaths"] > 0                                       # reproduction replaces others


def test_offspring_inherit_nothing_non_heritable():
    w = World(_cfg(reproduction="ENDOGENOUS_COPY", init="SEEDED_REPLICATOR", ticks=5), 4)
    w.step(); w.step()
    kids = [o for o in w.cells if o is not None and o.parent is not None]
    assert kids and all(o.energy <= 12.0 + 3.0 and o.age <= 2 and o.replications <= 2 for o in kids)   # fresh energy, no inherited counters


def test_seeded_replication_is_tagged_seeded_and_random_is_not():
    ws = World(_cfg(reproduction="ENDOGENOUS_COPY", init="SEEDED_REPLICATOR"), 5); ss = ws.run()
    assert ss["first_replication"]["seeded"] is True
    wr = World(_cfg(reproduction="ENDOGENOUS_PARTIAL", init="RANDOM"), 5); sr = wr.run()
    if sr["first_replication"]:
        assert sr["first_replication"]["seeded"] is False


def test_pair_execution_soup_runs_and_records_copies():
    w = World(_cfg(reproduction="PAIR_EXECUTION", world="SOUP", spatial="WELL_MIXED", init="SEEDED_REPLICATOR"), 6); s = w.run()
    assert s["endogenous_births"] > 0 and any(e["kind"] == "copy" and e["mechanism"] == "PAIR_EXECUTION" for e in w.events)


def test_environment_dynamics_change_and_reproduce():
    e = Environment("CONST", "DRIFT", 1, 3, drift_rate=1.0); k0 = e.tasks[0].k; e.step(1)
    assert e.tasks[0].k != k0 and e.history[-1]["why"] == "drift"
    e = Environment("INC", "SHIFT", 1, 3, shift_every=2); e.step(2); assert e.tasks[0].kind == "COND_ONE"
    e = Environment("CONST", "COEVOLVE", 1, 3); k = e.tasks[0].k; e.step(1, modal_answers=[k]); assert e.tasks[0].k != k
    e = Environment("INC", "ENV_REPRO", 4, 3)
    for tick in range(20, 400, 20):                                     # reproduction fires with probability 0.5 per eligible check
        e.step(tick, persistent=[True, False, False, False])
    assert e.lineage and e.lineage[0]["parent_niche"] == 0


def test_migration_and_reservoir_transport():
    w = World(_cfg(world="NICHES", spatial="RESERVOIR", task="COND_MULTI", reproduction="EXTERNAL", pressure="EXPLICIT", ticks=60, cells=144), 7); s = w.run()
    assert s["cross_niche_transport"] > 0 and w.env.tasks[0].kind == "ECHO"


# ---- grammar --------------------------------------------------------------------------------------------------------
def test_grammar_is_frozen_and_samples_only_valid_vectors():
    h1 = G.grammar_hash(); h2 = G.grammar_hash(); assert h1 == h2
    rng = random.Random(0)
    vs = G.sample_sparse(rng, 20, set())
    assert len(vs) == 20 and all(G.is_valid(v) for v in vs)
    assert not G.is_valid(dict(vs[0], recombination="CROSSOVER", reproduction="ENDOGENOUS_COPY"))
    assert not G.is_valid(dict(vs[0], world="SOUP", spatial="LOCAL"))
    for v in vs[:5]:
        for nb in G.neighbours(v, rng, 5):
            assert G.is_valid(nb) and sum(1 for a in G.AXES if nb[a] != v[a]) == 1
        for name, cv in G.matched_controls(v).items():
            assert G.is_valid(cv) and 1 <= sum(1 for a in G.AXES if cv[a] != v[a]) <= 2
        for name, t in G.COLLISIONS:
            c = G.cross(v, t)
            assert c is None or (G.is_valid(c) and all(c[k] == val for k, val in t.items()))
    assert "representation:NESTOR_TAPE" in G.UNAVAILABLE


def test_vec_id_is_stable_and_config_roundtrips():
    v = G.random_vec(random.Random(1)); assert v and G.vec_id(v) == G.vec_id(dict(v))
    cfg = G.to_config(v, 10, 16); assert cfg.ticks == 10 and cfg.cells == 16 and all(getattr(cfg, a) == v[a] for a in G.AXES)


# ---- geometry / observatory --------------------------------------------------------------------------------------------------
def test_geometry_measures_topology_not_semantics():
    cfg = _cfg(reproduction="ENDOGENOUS_COPY", task="INC")
    rep = vm.hybrid(vm.replicator(64), vm.witness_inc())
    sc = geometry.scan(rep, cfg, Task("INC"), 1, n=30)
    assert sc["base_replicates"] and sc["base_score"] == 1.0 and sc["replication_lethal_fraction"] is not None
    assert sc["next_task"] == "COND_ONE" and 0.0 <= sc["moat_density"] <= 1.0
    dc = geometry.damage_cliff(rep, cfg, Task("INC"), 1, trials=6)
    assert dc["cliff"]["k1"]["replicates"] >= dc["cliff"]["k16"]["replicates"]


def test_triggers_are_mechanical_and_thresholds_hash():
    assert O.thresholds_hash() == O.thresholds_hash()
    vec = G.random_vec(random.Random(2)); vec["reproduction"] = "ENDOGENOUS_COPY"; vec["init"] = "RANDOM"; vec["recombination"] = "NONE"
    s = {"alive_fraction": 0.5, "extinct": False, "replication_rate_tail": 0.2, "mean_fidelity_tail": 0.95, "first_replication": {"seeded": False, "span": 10},
         "repro_span_tail": 6, "solvers_tail": 2, "first_crossing": {"tick": 3}, "escape_events": [], "cross_niche_transport": 0, "env_lineage": [],
         "coexistence_ticks": 0, "lineages_final": 1, "n_exploits": 0, "arch_clusters_final": 4, "top": [{"tape": "00" * 64}]}
    t = O.triggers(s, vec, 100)
    assert t["replication"] and t["spontaneous_replication"] and t["reproductive_compression"] and t["task_reproduction_coupling"] and t["novel_architecture"]
    assert O.trigger_score(t) >= 5
    s2 = dict(s, mean_fidelity_tail=0.5); assert not O.triggers(s2, vec, 100)["replication"]


def test_scheduler_runs_a_tiny_campaign_and_emits_a_packet(tmp_path):
    from prometheus.z80atlas.scheduler import Campaign
    c = Campaign(str(tmp_path / "c"), hours=0.004, workers=2, ticks=12, cells=36, seed=3)
    c.run(batch_mult=1, quiet=True)
    assert (tmp_path / "c" / "CAMPAIGN_PACKET.md").exists() and (tmp_path / "c" / "state.json").exists()
    st = json.loads((tmp_path / "c" / "state.json").read_text(encoding="utf-8"))
    assert st["positive_controls"] is not None and st["n_runs"] and st["decisions"][0]["kind"] == "start"
    runs = [json.loads(l) for l in (tmp_path / "c" / "runs.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    assert all(r["kind"] == "positive_control" for r in runs[:len(C.CONTROL_VECS)])
    # resume refuses a changed grammar hash
    st["grammar_hash"] = "0" * 64; (tmp_path / "c" / "state.json").write_text(json.dumps(st), encoding="utf-8")
    with pytest.raises(AssertionError):
        Campaign(str(tmp_path / "c"), hours=0.004, workers=1, resume=True)

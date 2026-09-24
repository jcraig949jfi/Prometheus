"""DF-017: causal genetic provenance in the Z80 x Atlas engine (directive 2026-09-23, Phase 2).

The 72-hour campaign flagged 26 runs spontaneous_replication. All 26 were transplant verification runs: the constructor injected
evolved tapes (themselves descended from a seeded replicator) and labelled the spec init="random"; the predicate read the label.
These tests pin the repaired invariant: a replication is spontaneous only if the replicating lineage has no seeded or
transplanted founder anywhere in its genetic ancestry, and that tag survives every way material moves in the engine.

The ten numbered tests are the directive's required list; the unit tests below them pin the contribution rule they rest on.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from archaeon.z80atlas import engine as E, grammar as GR, tasks as T

G = 32


def _world(topology="well_mixed", migration="none", env_dynamics="fixed", reservoir=False):
    return {"topology": topology, "migration": migration, "resources": "unlimited", "env_dynamics": env_dynamics, "reservoir": reservoir,
            "niches": 4 if topology == "niches" else 1}


def _spec(*, init="random", reproduction="ENDOGENOUS_COPY", task="none", pressure=("implicit_survival",), sub="z80", epochs=60,
          transplant=None, **world):
    s = GR.make(_world(**world), {"substrate": sub, "genome": G, "layout": "shared"}, reproduction, list(pressure), task, "local_byte", init,
                stage="early", reason="test:provenance")
    assert s is not None, "grammar refused the test spec"
    s["budget"] = {"vm_steps": 3_000_000, "step_cap": 256, "max_epochs": epochs}
    if transplant is not None:
        s["transplant"] = {"from_run": "test_source_run", "tapes": transplant}
    return s


REPL = T.pad(T.replicator(False), G)


def _lucky_random(monkeypatch, every=1):
    """Simulate a random draw that happens to produce a working replicator (every `every`-th random founder). The origin stays
    random because the tape really does come from the random path: this is the one legitimate way a random founder replicates."""
    calls = {"n": 0}
    real = E.random_tape

    def fake(rng, g):
        calls["n"] += 1
        t = real(rng, g)                                                   # still consume the same draws
        return REPL if calls["n"] % every == 0 else t
    monkeypatch.setattr(E, "random_tape", fake)


def _prov(out):
    return out["signals"]["provenance"]


# ---------------------------------------------------------------------------------------------------------------- required 1-10
def test_01_random_founder_random_descendant_qualifying_replicator_may_be_spontaneous(monkeypatch):
    _lucky_random(monkeypatch)
    out = E.run(_spec(init="random"), 1)
    p = _prov(out); sig = out["signals"]
    assert p["founders"] == {"random": p["founders"]["random"], "seeded_replicator": 0, "transplanted_lineage": 0} and p["founders"]["random"] > 0
    assert p["births_endo_clean"] >= GR.FROZEN["spont_births"] and p["births_endo_inserted"] == 0
    assert p["first_clean_replication"] is not None and p["first_clean_replication"]["origins"] == ["random"]
    assert sig["spontaneous_replication"] is True
    assert all(o["origin_class"] == "random_only" for o in out["final_population"])


def test_02_seeded_replicator_descendants_can_never_be_spontaneous():
    out = E.run(_spec(init="seeded_replicator"), 3)
    p = _prov(out); seeded = {f for f, r in out["founders"].items() if r["origin"] == E.ORIGIN_SEEDED}
    assert seeded and p["births_endo_inserted"] >= 50
    for o in out["final_population"]:
        if set(o["founders"]) & seeded:
            assert o["inserted_ancestry"] is True and o["origin_class"] == "inserted_lineage"
    assert out["signals"]["spontaneous_replication"] is False
    assert p["first_inserted_replication"]["origins"] == ["seeded_replicator"]


def test_03_transplanted_replicator_descendants_can_never_be_spontaneous():
    out = E.run(_spec(init="random", transplant=[REPL.hex()] * 64), 5)
    p = _prov(out)
    assert p["founders"] == {"random": 0, "seeded_replicator": 0, "transplanted_lineage": 64}
    assert p["births_endo_inserted"] >= 50 and p["births_endo_clean"] == 0
    assert out["signals"]["spontaneous_replication"] is False and out["signals"]["inserted_lineage_replication"] is True
    assert all(o["inserted_ancestry"] for o in out["final_population"])
    assert all(r["from_run"] == "test_source_run" for r in out["founders"].values())


def test_04_transplanted_lineage_stays_tagged_over_many_generations():
    out = E.run(_spec(transplant=[REPL.hex()] * 64, epochs=400), 7)
    p = _prov(out)
    assert p["max_generation_inserted"] >= 50, p["max_generation_inserted"]
    fp = out["final_population"]
    assert fp and max(o["generation"] for o in fp) >= 20
    assert all(o["inserted_ancestry"] and o["origin_class"] == "inserted_lineage" for o in fp)
    assert out["signals"]["spontaneous_replication"] is False


@pytest.mark.parametrize("topology", ["well_mixed", "grid_vn", "ring_soup", "graph", "niches"])
def test_05_world_swap_does_not_erase_provenance(topology):
    out = E.run(_spec(transplant=[REPL.hex()] * 64, topology=topology), 11)
    p = _prov(out)
    assert p["founders"]["transplanted_lineage"] == 64 and p["births_endo_clean"] == 0
    assert out["signals"]["spontaneous_replication"] is False
    assert all(o["inserted_ancestry"] for o in out["final_population"])


@pytest.mark.parametrize("task,env", [("COND_multi", "fixed"), ("ECHO_forced", "nonstationary"), ("INC1", "env_mutate")])
def test_06_environment_or_task_swap_does_not_erase_provenance(task, env):
    tapes = [T.pad(T.task_then_replicate("CONST_incremental", False), G).hex()] * 64
    out = E.run(_spec(transplant=tapes, task=task, env_dynamics=env, epochs=250), 13)
    assert _prov(out)["births_endo_clean"] == 0 and out["signals"]["spontaneous_replication"] is False
    assert all(o["inserted_ancestry"] for o in out["final_population"])


def test_07_migration_does_not_erase_provenance():
    out = E.run(_spec(transplant=[REPL.hex()] * 128, topology="niches", migration="periodic", epochs=301), 17)
    assert out["signals"]["migrations"] > 0
    assert _prov(out)["births_endo_clean"] == 0
    assert all(o["inserted_ancestry"] for o in out["final_population"])
    assert out["signals"]["spontaneous_replication"] is False


@pytest.mark.parametrize("phys", ["OVERWRITE", "ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "PAIR_EXECUTION", "CONSTRUCTIVE"])
def test_08_endogenous_overwrite_or_copy_cannot_launder_inserted_ancestry(phys):
    """A seeded world: inserted replicators copy into, over and around random organisms. No child of an inserted parent, and
    no child that could carry an inserted occupant's bytes, may come out random_only."""
    out = E.run(_spec(init="seeded_replicator", reproduction=phys), 19)
    seeded = {f for f, r in out["founders"].items() if r["origin"] == E.ORIGIN_SEEDED}
    for o in out["final_population"]:
        if set(o["founders"]) & seeded:
            assert o["inserted_ancestry"], o
    assert out["signals"]["spontaneous_replication"] is False


def test_09_independent_random_lineage_stays_distinguishable_from_inserted_one_in_same_world(monkeypatch):
    """A seeded world in which one random founder in three is (by simulated luck) also a replicator: both kinds replicate side
    by side, and every organism is classified by its own ancestry, not by the world it lives in.

    Measured at epoch 15 while both kinds coexist. Run longer (120 epochs) and the clean kind disappears: ~19 mutant clean
    replicators write 31/32 bytes over an inserted occupant, keep one inserted byte, and are (correctly, conservatively) tagged
    inserted, after which drift fixes the tagged class. Contamination is permitted in that direction, never the other."""
    _lucky_random(monkeypatch, every=3)
    out = E.run(_spec(init="seeded_replicator", epochs=15), 23)
    p = _prov(out); origin = {f: r["origin"] for f, r in out["founders"].items()}
    assert p["world_has_inserted_material"] is True
    assert p["births_endo_clean"] > 0 and p["births_endo_inserted"] > 0
    assert p["first_clean_replication"]["origins"] == ["random"]
    kinds = set()
    for o in out["final_population"]:
        ins = any(origin[f] != E.ORIGIN_RANDOM for f in o["founders"])
        assert o["inserted_ancestry"] is ins
        kinds.add(ins)
    assert kinds == {True, False}, "both lineage kinds should survive to the end in this world"


def test_10_regression_campaign_transplant_labelled_random_is_not_spontaneous():
    """The exact campaign pattern: transplant tapes + init label "random" + ENDOGENOUS_COPY in niches. The defective label fires;
    the repaired predicate does not; the event is reported as inserted-lineage replication."""
    out = E.run(_spec(init="random", transplant=[REPL.hex()] * 120, topology="niches", epochs=200), 100)
    sig = out["signals"]
    assert sig["spontaneous_replication_legacy_label"] is True, "regression fixture must reproduce the old false positive"
    assert sig["spontaneous_replication"] is False
    assert sig["inserted_lineage_replication"] is True
    assert sig["provenance"]["founders"]["transplanted_lineage"] == 120


# ---------------------------------------------------------------------------------------------------------------- rule units
def _res(mask_full=True, reads=0, execf=0, sealed=False):
    return {"reads_nbr": reads, "exec_foreign": execf, "sealed": sealed, "nbr_mask": bytes([1] * G if mask_full else [1] * (G - 1) + [0])}


def test_donor_rule_complete_clean_write_carries_nothing():
    assert E.donor_contributes(True, _res(), "ENDOGENOUS_COPY") is False
    assert E.donor_contributes(False, _res(mask_full=False, reads=3), "OVERWRITE") is False     # empty cell: nothing to carry


@pytest.mark.parametrize("res", [_res(mask_full=False), _res(reads=1), _res(execf=1), _res(sealed=True)])
def test_donor_rule_any_route_for_occupant_bytes_counts(res):
    assert E.donor_contributes(True, res, "ENDOGENOUS_COPY") is True
    assert E.donor_contributes(True, res, "OVERWRITE") is True


def test_donor_rule_partial_refill_is_rng_not_occupant():
    assert E.donor_contributes(True, _res(mask_full=False), "ENDOGENOUS_PARTIAL") is False
    assert E.donor_contributes(True, _res(mask_full=False, reads=1), "ENDOGENOUS_PARTIAL") is True


def test_recombination_partner_ancestry_is_inherited():
    tapes = [REPL.hex()] * 16                                              # 16 transplanted founders, the rest of the world empty
    s = _spec(reproduction="EXTERNAL", pressure=("recombination",), task="CONST_incremental", transplant=tapes, epochs=40)
    out = E.run(s, 29)
    assert all(o["inserted_ancestry"] for o in out["final_population"])
    assert _prov(out)["recombination_mixed_births"] > 0
    assert out["signals"]["spontaneous_replication"] is False              # EXTERNAL is never spontaneous


def _campaign_engine():
    """The engine exactly as it ran the 72-hour campaign (commit c7610ea19), loaded beside the repaired one."""
    import importlib.util
    import subprocess
    import sys
    import tempfile
    root = Path(__file__).resolve().parents[2]
    try:
        src = subprocess.run(["git", "show", "c7610ea19:archaeon/z80atlas/engine.py"], cwd=root, capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("campaign engine source not reachable through git")
    f = Path(tempfile.mkdtemp()) / "engine_campaign.py"; f.write_bytes(src)
    spec = importlib.util.spec_from_file_location("z80atlas_engine_campaign", f); mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod; spec.loader.exec_module(mod)
    return mod


LEGACY_EVENT_KEYS = ("e", "k", "mech", "p", "c", "cell", "fid", "mig", "victim", "by", "id", "n", "task", "from", "to")


@pytest.mark.parametrize("kw", [dict(init="seeded_replicator", topology="niches", migration="high"),
                                dict(init="random", reproduction="EXTERNAL", pressure=("recombination",), task="CONST_incremental"),
                                dict(init="random", reproduction="ENDOGENOUS_PARTIAL", topology="grid_vn"),
                                dict(init="random", transplant=[REPL.hex()] * 90, topology="niches", migration="periodic")])
def test_repair_is_rng_neutral_against_the_campaign_engine(kw):
    """The repair adds no draw and changes no behaviour: every pre-existing output of the campaign engine is reproduced exactly
    (new keys are additions), so every historical (spec, seed) still means what it meant."""
    old_E = _campaign_engine()
    s = _spec(epochs=120, **kw)
    a, b = old_E.run(s, 31), E.run(s, 31)
    for k, v in a["signals"].items():
        if k == "spontaneous_replication":
            assert b["signals"]["spontaneous_replication_legacy_label"] == v
        else:
            assert b["signals"][k] == v, k
    assert [{k: r[k] for k in r if k not in ("pop_clean", "endo_clean")} for r in b["telemetry"]] == a["telemetry"]
    assert [{k: ev[k] for k in ev if k in LEGACY_EVENT_KEYS} for ev in b["events"]] == a["events"]
    assert [{k: o[k] for k in o if k not in ("generation", "founders", "inserted_ancestry", "origin_class")} for o in b["final_population"]] == a["final_population"]


@pytest.mark.parametrize("phys", ["EXTERNAL", "ENDOGENOUS_COPY"])
def test_first_clean_crossing_is_random_only_and_consistent_with_first_crossing(phys):
    """Ruling 1: a crossing counts as provenance-qualified only if the crosser has random-only ancestry; recorded even when an
    inserted organism (the seeded witness) crossed first."""
    s = _spec(init="seeded_replicator", reproduction=phys, task="CONST_atomic", pressure=("implicit_survival",), epochs=150)
    p = _prov(E.run(s, 41))
    fc, cc = p["first_crossing"], p["first_clean_crossing"]
    for t, c in cc.items():
        assert c["origins"] == ["random"]
        assert t in fc and fc[t]["epoch"] <= c["epoch"]
        if not fc[t]["inserted_ancestry"]:
            assert fc[t]["epoch"] == c["epoch"] and fc[t]["id"] == c["id"]
    assert any(c["inserted_ancestry"] for c in fc.values()), "fixture should have the seeded witness cross first"


# ---------------------------------------------------------------------------------------------------------------- historical replay
HIST = Path(os.environ.get("Z80ATLAS_HISTORICAL_RUNS", r"D:\Prometheus-worktrees\archaeon-wse-2026-09-16\archaeon\z80atlas\campaign\runs"))


@pytest.mark.skipif(not (HIST / "5b237a475b69" / "4e132c6e0178-t_s100_veri" / "SPEC.json").exists() or not os.environ.get("Z80ATLAS_SLOW"),
                    reason="historical campaign records not present, or Z80ATLAS_SLOW unset (about 5 minutes)")
def test_historical_flagged_run_replays_identically_and_is_reclassified():
    d = HIST / "5b237a475b69" / "4e132c6e0178-t_s100_veri"
    spec = json.loads((d / "SPEC.json").read_text(encoding="utf-8")); rec = json.loads((d / "RECEIPT.json").read_text(encoding="utf-8"))
    sig = E.run(spec, rec["seed"])["signals"]
    for k, v in rec["signals"].items():
        if k != "spontaneous_replication":
            assert sig[k] == v, k
    assert rec["signals"]["spontaneous_replication"] is True and sig["spontaneous_replication_legacy_label"] is True
    assert sig["spontaneous_replication"] is False and sig["inserted_lineage_replication"] is True

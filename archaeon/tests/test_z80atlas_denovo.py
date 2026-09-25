"""Phase 4 (directive 2026-09-23): the pre-registered de-novo endpoint, controls and interval arithmetic."""
from __future__ import annotations

import pytest

from archaeon.z80atlas import engine as E, grammar as GR
from archaeon.z80atlas.denovo import run_denovo as D

N = GR.FROZEN["N"]


def _sig(random=80, seeded=0, transplanted=0, clean=500, pop_clean=100, fid=0.95, extinct=None, epochs=4000, spont=True, ins_pop=0):
    return {"extinct_epoch": extinct, "epochs": epochs, "spontaneous_replication": spont, "spontaneous_replication_legacy_label": spont, "inserted_lineage_replication": False,
            "provenance": {"founders": {"random": random, "seeded_replicator": seeded, "transplanted_lineage": transplanted}, "world_has_inserted_material": bool(seeded or transplanted),
                           "births_endo_clean": clean, "final_pop_clean": pop_clean, "fid_clean": fid, "births_endo_inserted": 0, "fid_inserted": 0.0, "final_pop_inserted": ins_pop}}


def test_primary_requires_clean_world_alive_after_founders_and_repaired_predicate():
    assert D.endpoint(_sig(), N)["DE_NOVO_REPLICATION"] is True
    assert D.endpoint(_sig(seeded=3), N)["DE_NOVO_REPLICATION"] is False
    assert D.endpoint(_sig(transplanted=5), N)["DE_NOVO_REPLICATION"] is False
    assert D.endpoint(_sig(extinct=700), N)["DE_NOVO_REPLICATION"] is False
    assert D.endpoint(_sig(epochs=2 * GR.FROZEN["max_age"] - 1), N)["DE_NOVO_REPLICATION"] is False
    assert D.endpoint(_sig(spont=False), N)["DE_NOVO_REPLICATION"] is False


def test_secondary_is_the_low_fidelity_class_and_never_the_primary():
    e = D.endpoint(_sig(fid=0.485, spont=False), N)
    assert e["SUSTAINED_LOW_FIDELITY_REPRODUCTION"] is True and e["DE_NOVO_REPLICATION"] is False
    assert D.endpoint(_sig(), N)["SUSTAINED_LOW_FIDELITY_REPRODUCTION"] is False


def test_clopper_pearson_known_values():
    assert D.clopper_pearson(0, 16) == [0.0, 0.2059]
    assert D.clopper_pearson(16, 16) == [0.7941, 1.0]
    lo, hi = D.clopper_pearson(1, 16)
    assert 0.0015 < lo < 0.0017 and 0.30 < hi < 0.31


def test_every_arm_is_grammar_legal_random_only_and_arm_e_is_the_candidate_world():
    for a in D.ARMS:
        s = D.make(a, "random", "t")
        assert s["init"] == "random" and "transplant" not in s and s["spec_id"] == GR.spec_id(s)
    assert D.make("E_well_mixed", "random", "t")["spec_id"] == "84616cf8257b"
    assert {D.make(a, "random", "t")["world"]["topology"] for a in D.ARMS} == {"niches", "well_mixed"}


def test_controls_classify_as_intended_on_short_worlds():
    """Short-budget smoke of the control constructions: a seeded arm world is inserted, a transplant labelled random is inserted."""
    s = D.make("B_niches_bare", "seeded_replicator", "t"); s["budget"] = {"vm_steps": 2_000_000, "step_cap": 256, "max_epochs": 40}
    sig = E.run(s, 2000)["signals"]
    assert sig["provenance"]["founders"]["seeded_replicator"] > 0 and sig["spontaneous_replication"] is False
    n = D.negctrl("E_well_mixed"); n["budget"] = {"vm_steps": 2_000_000, "step_cap": 256, "max_epochs": 40}
    sig = E.run(n, 3000)["signals"]
    assert D.negctrl_pass(sig, len(n["transplant"]["tapes"]))["PASS"] is True

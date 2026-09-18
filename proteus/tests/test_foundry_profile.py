"""proteus.foundry_profile.v1 -- acceptance (repair order s3 / PROTEUS-29).

positive   the committed catalog recomputes from the live runtime, grammar and registry; Archaeon's
           three recorded regime strings are reproduced byte-exactly, including one read from a
           committed campaign receipt (archaeon/campaign2/C2-SFE-02/PREREG.json, budget.foundry_id)
invariance seed and n do not enter the profile id (a population is not a regime)
no-alias   runtime, affordance, regime, grammar version/hash, ANY weight, kernel qualification
           each change the id; the catalog's ids are pairwise distinct
cheat      a record whose regime was edited after minting is refused by verify_profile; a record
           whose archaeon_regime_id was hand-typed wrongly is refused
"""
from __future__ import annotations

import json
import os

import pytest

from proteus.eval import foundry_profile as FP
from proteus.foundry import grammar as G
from proteus.foundry.generate import DEFAULT_FOUNDRY_MANIFEST
from proteus.foundry.identity import RUNTIME_HASH

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RECEIPT = os.path.join(ROOT, "archaeon", "campaign2", "C2-SFE-02", "PREREG.json")


def test_committed_catalog_recomputes():
    live = FP.build_catalog()
    committed = json.load(open(FP.CATALOG_PATH, encoding="utf-8"))
    assert committed["catalog_id"] == live["catalog_id"]
    assert committed["runtime_hash"] == RUNTIME_HASH
    assert committed["grammar"]["grammar_hash"] == G.GRAMMAR_HASH
    for row in committed["profiles"]:
        FP.verify_profile(row)


def test_archaeon_strings_reproduce_from_the_regime_dicts():
    cat = FP.build_catalog()
    got = {r["name"]: r["archaeon_regime_id"] for r in cat["profiles"]}
    assert got == {
        "c1_c2_c3_instr1_16": "instr1-16:6528b9dc",
        "c2_default_instr1_32": "instr1-32:199105b4",
        "registry_instr1_64": "instr1-64:97ce0af8",
    }
    for r in cat["profiles"]:
        assert r["archaeon_regime_id"] == r["recorded_archaeon_id"]


def test_archaeon_string_matches_a_committed_campaign_receipt():
    if not os.path.exists(RECEIPT):
        pytest.skip("campaign 2 receipt not present")
    prereg = json.load(open(RECEIPT, encoding="utf-8"))
    recorded = prereg["budget"]["foundry_id"]
    cat = FP.build_catalog()
    ids = {r["archaeon_regime_id"] for r in cat["profiles"]}
    assert recorded in ids, recorded


def test_seed_and_n_do_not_enter_the_profile():
    fm = dict(DEFAULT_FOUNDRY_MANIFEST, seed=15025105317373938188, n=64)
    a = FP.build_profile(fm)
    b = FP.build_profile(dict(fm, seed=1, n=3))
    assert a["profile_id"] == b["profile_id"]
    assert a["archaeon_regime_id"] == b["archaeon_regime_id"]
    assert "seed" not in a["regime"] and "n" not in a["regime"]


def _base():
    return dict(DEFAULT_FOUNDRY_MANIFEST, seed=0, n=0)


def test_every_identity_bearing_field_changes_the_id():
    ref = FP.build_profile(_base())
    variants = [
        FP.build_profile(_base(), runtime_hash="0" * 64),
        FP.build_profile(_base(), affordance_hash="1" * 64),
        FP.build_profile(dict(_base(), genome_instr_range=[1, 63])),
        FP.build_profile(_base(), grammar=FP.grammar_identity(version="proteus.grammar.v0.5-test")),
        FP.build_profile(_base(), grammar=FP.grammar_identity(ghash="2" * 64)),
        FP.build_profile(_base(), kernel_qualification=dict(FP.registry_kernel_qualification(),
                                                            mutation_neutrality="QUALIFIED_TEST")),
    ]
    ids = {ref["profile_id"]} | {v["profile_id"] for v in variants}
    assert len(ids) == len(variants) + 1


def test_different_grammar_weights_cannot_alias():
    """A grammar MASS profile (Round 2 lane 3) with the same version string but a moved weight is a
    different profile: the id carries the weight vector, not only the version and hash."""
    ref = FP.build_profile(_base())
    w = list(G.WEIGHTS)
    i, j = G.NAMES.index("splice"), G.NAMES.index("operand_perturbation")
    w[i], w[j] = w[i] + 0.01, w[j] - 0.01
    moved = FP.build_profile(_base(), grammar=FP.grammar_identity(names=G.NAMES, weights=tuple(w)))
    assert moved["profile_id"] != ref["profile_id"]
    assert moved["archaeon_regime_id"] == ref["archaeon_regime_id"]   # Archaeon's string is regime-only


def test_catalog_ids_pairwise_distinct():
    cat = FP.build_catalog()
    ids = [r["profile_id"] for r in cat["profiles"]]
    assert len(set(ids)) == len(ids) == 3
    ar = [r["archaeon_regime_id"] for r in cat["profiles"]]
    assert len(set(ar)) == 3


def test_cheat_edited_regime_is_refused():
    p = FP.build_profile(_base())
    p["regime"] = dict(p["regime"], genome_instr_range=[1, 8])
    with pytest.raises(ValueError):
        FP.verify_profile(p)


def test_cheat_hand_typed_archaeon_id_is_refused():
    p = FP.build_profile(_base())
    p["archaeon_regime_id"] = "instr1-64:deadbeef"
    with pytest.raises(ValueError):
        FP.verify_profile(p)


def test_regime_must_be_a_valid_foundry_manifest():
    with pytest.raises(ValueError):
        FP.build_profile(dict(_base(), genome_instr_range=[5, 2]))

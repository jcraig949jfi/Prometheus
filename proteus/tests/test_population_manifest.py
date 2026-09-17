"""proteus.population_manifest.v1 -- acceptance (repair order s3 / PROTEUS-30).

positive    the committed registry manifest recomputes; same profile + seed => same declared
            population (manifest_hash and population_manifest_id equal on two builds and on a
            regeneration); a common_fill-shaped population (imports in front) is described with
            its composition, its imports and a recipe that still verifies the gen0 members
negative    a different seed is a different population; a different regime is a different profile
            and a different population; key order in the input manifests does not matter
defect      L-008 / L-030 (campaign 1: harness-seeded organisms replaced generation 0 without a
            record): an organism NOT produced by the recipe but labelled gen0 is REFUSED
cheat       a record whose organism_id does not hash from its manifest is refused; a duplicate
            member is refused; a selection with evidence recorded AFTER the seal is refused
            (future information); a declared foundry_profile that disagrees with the manifest is
            refused; a tampered count is refused by verify
"""
from __future__ import annotations

import json

import pytest

from proteus.eval import foundry_profile as FP
from proteus.eval import population_manifest as PM
from proteus.foundry import generate as GEN
from proteus.foundry.generate import DEFAULT_FOUNDRY_MANIFEST
from proteus.foundry.prng import SplitMix64


def _fm(seed=12345, n=20, **over):
    fm = dict(DEFAULT_FOUNDRY_MANIFEST, seed=seed, n=n)
    fm.update(over)
    return fm


def test_committed_registry_manifest_recomputes():
    committed = json.load(open(PM.REGISTRY_MANIFEST_PATH, encoding="utf-8"))
    live = PM.registry_population_manifest()
    assert committed == live
    assert committed["count"] == 64 and committed["lineage_composition"] == {"gen0": 64}
    assert committed["recipe"]["recipe_population_hash"] == committed["manifest_hash"]
    cat = json.load(open(FP.CATALOG_PATH, encoding="utf-8"))
    reg_profile = next(r for r in cat["profiles"] if r["name"] == "registry_instr1_64")["profile_id"]
    assert committed["foundry_profile"] == reg_profile
    r = json.load(open(PM.REGISTRY_PATH, encoding="utf-8"))
    PM.verify_population_manifest(committed, members=r["entries"], foundry_manifest=r["build"]["foundry_manifest"])


def test_same_profile_and_seed_yield_the_same_declared_population():
    fm = _fm()
    a = PM.build_population_manifest(GEN.generate(fm), foundry_manifest=fm)
    b = PM.build_population_manifest(GEN.generate(dict(fm)), foundry_manifest=dict(fm))
    assert a == b
    assert a["recipe"]["recipe_population_hash"] == a["manifest_hash"]
    PM.verify_population_manifest(a, members=GEN.generate(fm), foundry_manifest=fm)


def test_different_seed_or_regime_is_a_different_population():
    a = PM.build_population_manifest(GEN.generate(_fm()), foundry_manifest=_fm())
    b = PM.build_population_manifest(GEN.generate(_fm(seed=12346)), foundry_manifest=_fm(seed=12346))
    c_fm = _fm(genome_instr_range=[1, 16])
    c = PM.build_population_manifest(GEN.generate(c_fm), foundry_manifest=c_fm)
    assert a["manifest_hash"] != b["manifest_hash"]
    assert a["foundry_profile"] == b["foundry_profile"]           # seed is not a regime
    assert a["foundry_profile"] != c["foundry_profile"]           # regime is
    assert len({a["population_manifest_id"], b["population_manifest_id"], c["population_manifest_id"]}) == 3


def test_input_key_order_does_not_matter():
    fm = _fm(n=6)
    pop = GEN.generate(fm)
    shuffled = []
    for o in pop:
        m = {k: o["manifest"][k] for k in reversed(list(o["manifest"]))}
        shuffled.append({"origins": ["gen0"], "manifest": m, "organism_id": o["organism_id"]})
    a = PM.build_population_manifest(pop, foundry_manifest=fm)
    b = PM.build_population_manifest(list(reversed(shuffled)), foundry_manifest=fm)
    assert a == b


def test_common_fill_shape_is_described_with_imports_and_composition():
    fm = _fm(n=10)
    base = GEN.generate(fm)
    foreign = GEN.generate(_fm(seed=999, n=3))
    subs = [dict(o, origins=["import"]) for o in foreign]
    pop = subs + base[: 10 - 3]                         # common_fill(position="front")
    pm = PM.build_population_manifest(pop, foundry_manifest=fm,
                                      gen0_provenance={"fill": "wse.gen0", "n_substituted": 3},
                                      imported_sources={foreign[0]["organism_id"]: {"source_world": "wld_test"}})
    assert pm["count"] == 10
    assert pm["lineage_composition"] == {"gen0": 7, "import": 3}
    assert len(pm["imported"]) == 3
    assert pm["recipe"]["gen0_members_in_recipe"] == 7
    assert pm["manifest_hash"] != pm["recipe"]["recipe_population_hash"]   # imports changed the population
    src = {r["organism_ref"]: r["source"] for r in pm["imported"]}
    assert src[foreign[0]["organism_id"]] == {"source_world": "wld_test"}
    assert all(v == "UNKNOWN" for k, v in src.items() if k != foreign[0]["organism_id"])


def test_defect_L008_harness_seeded_organism_labelled_gen0_is_refused():
    """Campaign 1 L-008/L-030: a harness-seeded fill was recorded as generation 0. Under the
    recipe check that population cannot be declared."""
    fm = _fm(n=5)
    pop = GEN.generate(fm)
    rng = SplitMix64(7)
    stranger = GEN.organism_record(GEN.sample_manifest(_fm(seed=4242, n=1), rng), None, 0)
    stranger["origins"] = ["gen0"]
    pop[0] = stranger
    with pytest.raises(ValueError, match="not produced by the recipe"):
        PM.build_population_manifest(pop, foundry_manifest=fm)


def test_cheat_organism_id_must_hash_from_its_manifest():
    fm = _fm(n=3)
    pop = GEN.generate(fm)
    pop[1] = dict(pop[1], organism_id="0" * 64)
    with pytest.raises(ValueError, match="does not hash"):
        PM.build_population_manifest(pop)


def test_cheat_duplicate_member_is_refused():
    fm = _fm(n=3)
    pop = GEN.generate(fm)
    with pytest.raises(ValueError, match="duplicate"):
        PM.build_population_manifest(pop + [pop[0]])


def test_selection_rules():
    fm = _fm(n=4)
    pop = GEN.generate(fm)
    with pytest.raises(ValueError):
        PM.build_population_manifest(pop, selection_criteria="NONE",
                                     selection_evidence_ref={"ref": "x", "recorded_at": "2026-09-17T00:00:00Z"})
    with pytest.raises(ValueError):
        PM.build_population_manifest(pop, selection_criteria="top_by_capability_X")
    with pytest.raises(ValueError, match="future"):
        PM.build_population_manifest(pop, selection_criteria="top_by_capability_X",
                                     selection_evidence_ref={"ref": "pew:1", "recorded_at": "2026-09-18T00:00:00Z"},
                                     sealed_at="2026-09-17T12:00:00Z")
    ok = PM.build_population_manifest(pop, selection_criteria="top_by_capability_X",
                                      selection_evidence_ref={"ref": "pew:1", "recorded_at": "2026-09-17T11:00:00Z"},
                                      sealed_at="2026-09-17T12:00:00Z")
    assert ok["selection_criteria"] == "top_by_capability_X"


def test_declared_profile_must_agree_with_the_manifest():
    fm = _fm(n=3)
    with pytest.raises(ValueError, match="disagrees"):
        PM.build_population_manifest(GEN.generate(fm), foundry_manifest=fm, foundry_profile="pfp1:0000000000000000")


def test_verify_refuses_tampered_count():
    fm = _fm(n=3)
    pm = PM.build_population_manifest(GEN.generate(fm), foundry_manifest=fm)
    bad = dict(pm, count=4)
    with pytest.raises(ValueError):
        PM.verify_population_manifest(bad)


def test_structural_descriptor_is_static_and_pure():
    fm = _fm(n=2)
    m = GEN.generate(fm)[0]["manifest"]
    d1, d2 = PM.structural_descriptor(m), PM.structural_descriptor(dict(m))
    assert d1 == d2
    assert d1["genome_words"] == 4 * d1["genome_instructions"] == len(m["genome"])
    assert sum(d1["opcode_category_counts_static"].values()) == len(m["genome"])

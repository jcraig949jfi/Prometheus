"""Round 2 L0 anatomy (PROTEUS-37) -- controls.

positive   the committed result recomputes from the committed specimens at a reduced permutation
           count (structure and programs identical; only floor_p differs); every knockout manifest
           is valid, differs from its parent, and has a distinct organism_id
firewall   Archaeon's behavioural columns (heldout_*) are stripped before anything reads a specimen
cheat      two identical groups give floor_p == 1.0 on every non-constant statistic (the floor
           cannot manufacture separation); a specimen whose organism_id does not hash from its
           manifest is refused
"""
from __future__ import annotations

import copy
import json
import os

import pytest

from proteus.eval import anatomy as AN
from proteus.foundry.prng import SplitMix64
from proteus.foundry.vm import validate_manifest


def _doc():
    if not os.path.exists(AN.SPECIMENS):
        pytest.skip("specimens not present")
    return AN.load_specimens()


def test_behavioural_columns_are_stripped():
    doc = _doc()
    for g in AN.GROUPS:
        for e in doc["specimens"][g]:
            assert not any(k.startswith("heldout") for k in e)


def test_committed_structure_recomputes():
    doc = _doc()
    result, abl = AN.run(doc, n_perm=50)
    committed = json.load(open(AN.RESULT, encoding="utf-8"))
    for g in AN.GROUPS:
        for live, com in zip(result["per_organism"][g], committed["per_organism"][g]):
            assert live["organism_id"] == com["organism_id"]
            assert live["program_reachable"] == com["program_reachable"]
            assert live["stats"] == com["stats"]
    assert result["group_programs"] == committed["group_programs"]
    for pair in result["separation"]:
        for k in result["separation"][pair]:
            assert result["separation"][pair][k]["diff"] == committed["separation"][pair][k]["diff"]
    c_abl = json.load(open(AN.ABLATION, encoding="utf-8"))
    assert [[a["organism_id"] for a in s["knockouts"]] for g in AN.GROUPS for s in abl["sets"][g]] == \
           [[a["organism_id"] for a in s["knockouts"]] for g in AN.GROUPS for s in c_abl["sets"][g]]


def test_knockouts_are_valid_distinct_and_differ_from_parent():
    doc = _doc()
    _, abl = AN.run(doc, n_perm=1)
    for g in AN.GROUPS:
        for s in abl["sets"][g]:
            ids = [k["organism_id"] for k in s["knockouts"]]
            assert s["parent_organism_id"] not in ids
            assert len(set(ids)) == len(ids)
            for k in s["knockouts"]:
                validate_manifest(k["manifest"])


def test_cheat_identical_groups_show_no_separation():
    doc = _doc()
    stats = [AN.numeric_stats(AN.structure(e["manifest"])) for e in doc["specimens"]["w0_solver"]]
    rows = AN.separation(stats, list(stats), SplitMix64(1), n_perm=300)
    for k, r in rows.items():
        assert r["diff"] == 0.0 and r["floor_p"] == 1.0


def test_cheat_forged_organism_id_refused():
    doc = _doc()
    bad = copy.deepcopy(doc)
    bad["specimens"]["shelf"][0]["organism_id"] = "a" * 64
    with pytest.raises(ValueError, match="does not hash"):
        AN.run(bad, n_perm=1)

"""Graph foundry profile -- recompute, no-alias against v0, v0 catalog untouched."""
from __future__ import annotations

import json

from proteus.eval import foundry_profile as FP
from proteus.graph import profile as GP
from proteus.graph.generate import DEFAULT_FOUNDRY_MANIFEST


def test_committed_graph_catalog_recomputes():
    committed = json.load(open(GP.CATALOG_PATH, encoding="utf-8"))
    assert committed == GP.build_catalog()
    for row in committed["profiles"]:
        GP.verify_graph_profile(row)


def test_graph_profile_cannot_alias_any_v0_profile():
    v0 = {r["profile_id"] for r in FP.build_catalog()["profiles"]}
    g = GP.build_graph_profile(dict(DEFAULT_FOUNDRY_MANIFEST, seed=0, n=0))
    assert g["profile_id"] not in v0 and g["runtime_hash"] != FP.RUNTIME_HASH


def test_v0_catalog_is_untouched_by_the_graph_package():
    committed = json.load(open(FP.CATALOG_PATH, encoding="utf-8"))
    assert committed["catalog_id"] == FP.build_catalog()["catalog_id"]
    assert committed["catalog_id"].startswith("42e4db36db259a16")


def test_seed_and_n_do_not_enter_graph_profile():
    a = GP.build_graph_profile(dict(DEFAULT_FOUNDRY_MANIFEST, seed=1, n=5))
    b = GP.build_graph_profile(dict(DEFAULT_FOUNDRY_MANIFEST, seed=2, n=50))
    assert a["profile_id"] == b["profile_id"]

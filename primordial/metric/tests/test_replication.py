"""G-R6-3: the replication trigger publishes ONE frozen-recipe record per new SURVIVED cell, idempotently."""
from __future__ import annotations

import json

import pytest

from primordial.metric import replication as RP
from primordial.metric import screen as SC
from primordial.tests._live import live_url


@pytest.fixture
def r(monkeypatch):
    redis = pytest.importorskip("redis")
    c = redis.Redis.from_url(live_url(), decode_responses=True)
    try:
        c.ping()
    except Exception:
        pytest.skip("substrate not reachable")
    monkeypatch.setattr(RP, "STREAM", "pm:test:g-replication")
    monkeypatch.setattr(RP, "PUBLISHED", "pm:test:g-replication:published:{}|{}")
    for k in list(c.scan_iter("pm:test:g-replication*", count=1000)):
        c.delete(k)
    yield c
    for k in list(c.scan_iter("pm:test:g-replication*", count=1000)):
        c.delete(k)


def doc_with(survivors):
    cells = []
    for w, p in [("w13", "train128_held64"), ("w4", "train8_held64"), ("w7", "train8_held64")]:
        v = "SURVIVED" if (w, p) in survivors else "CULLED"
        cells.append({"world": w, "pressure": p, "verdicts": {SC.vkey(*x): {"verdict": v} for x in SC.VARIANTS}})
    return {"q1_floor_policy": "gate_in", "q2_policy": "HOLD", "cells": cells}


def test_origin_alone_publishes_nothing(r):
    assert RP.publish_new_survivors(r, doc_with({("w13", "train128_held64")})) == []
    assert RP.records(r) == []


def test_a_planted_new_survivor_publishes_exactly_once_with_the_frozen_recipe(r):
    doc = doc_with({("w13", "train128_held64"), ("w4", "train8_held64")})
    first = RP.publish_new_survivors(r, doc, now=1.0)
    assert len(first) == 1 and first[0]["cell"] == {"world": "w4", "pressure": "train8_held64", "gen_seed": 4}
    again = RP.publish_new_survivors(r, doc, now=2.0)
    assert again == [] and len(RP.records(r)) == 1                                  # idempotent
    rec = RP.records(r)[0]
    assert rec["recipe"]["id"] == "B-R5-1" and rec["recipe"]["frozen_code_sha"] == "c2e9b5ec3"
    assert rec["recipe"]["search_budget"] == {"search_generations": 800, "search_batch": 128, "search_evals": 102400,
                                              "rule": "absolute; not rescaled by genome size (conductor 1789479784674-0)"}
    assert rec["recipe"]["sample"]["runs_total"] == 32 and rec["recipe"]["readout"] == "top1_train"
    assert rec["applicability"] == "APPLICABLE" and rec["layout"]["genome_bytes"] > 0
    from primordial.cohorts.b.b1_qlinear import QLin
    assert rec["layout"]["genome_bytes"] == QLin(4, 4, 4).glen                        # derived by the frozen rule
    assert QLin(13, 4, 4).glen == 16                                                 # the origin's 16 B reproduces
    t = rec["predicate_template"]
    assert t["experiment_class"] == "REPLICATION" and t["cell"] == {"world": "w4", "pressure": "train8_held64"}
    later = RP.publish_new_survivors(r, doc_with({("w13", "train128_held64"), ("w4", "train8_held64"), ("w7", "train8_held64")}))
    assert [x["cell"]["world"] for x in later] == ["w7"] and len(RP.records(r)) == 2


def test_inapplicable_layout_is_named_not_a_fail(r, monkeypatch):
    import primordial.cohorts.b.b1_qlinear as BQ

    class Broken:
        def __init__(self, *a, **k):
            raise ValueError("planted: layout rule cannot instantiate")
    monkeypatch.setattr(BQ, "QLin", Broken)
    rec = RP.publish_new_survivors(r, doc_with({("w4", "train8_held64")}))[0]
    assert rec["applicability"] == "INAPPLICABLE" and "planted" in rec["layout"]["reason"]
    assert rec["layout"]["genome_bytes"] is None


def test_the_recipe_code_is_frozen_at_its_sha():
    assert RP.frozen_code_intact(), "B-R5-1 recipe files changed since c2e9b5ec3: the frozen recipe no longer matches"

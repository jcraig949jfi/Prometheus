"""ARCH-26: the dead-stream control's own controls -- the dead stream keeps
both marginals and breaks only the relation; the cheat score is the solve
count; the sealed manifest on disk is the one the code regenerates; the
run is deterministic."""
from __future__ import annotations

import json
from collections import Counter

from archaeon.producer import h3_dead_stream as D
from archaeon.producer import h3_replay as H


def test_dead_keeps_score_and_descriptor_marginals_and_breaks_the_relation():
    s = D.make_streams(seed=3)
    live, dead = s["live"], s["dead"]
    assert [c.descriptors for c in live] == [c.descriptors for c in dead]
    assert [c.replay_ref for c in live] == [c.replay_ref for c in dead]
    assert Counter(c.score for c in live) == Counter(c.score for c in dead)
    assert [c.score for c in live] != [c.score for c in dead]
    assert [c.birth_status for c in live] == [c.birth_status for c in dead]
    tasks = D.make_tasks()["queries"]
    # live: score tracks the solve count; dead: it does not (rank correlation via a crude split)
    def relation(stream):
        ev = [c for c in stream if c.score is not None]
        hi = sorted(ev, key=lambda c: -c.score)[:40]
        lo = sorted(ev, key=lambda c: c.score)[:40]
        return (sum(D.solve_count(D.table_of(c), tasks) for c in hi) - sum(D.solve_count(D.table_of(c), tasks) for c in lo)) / 40.0
    assert relation(live) > 1.0
    assert abs(relation(dead)) < 0.75


def test_cheat_score_is_exactly_the_solve_fraction():
    tasks = D.make_tasks()["queries"]
    for c in D.make_streams(seed=1)["cheat"]:
        if c.score is not None:
            assert c.score == round(D.solve_count(D.table_of(c), tasks) / D.N_TASKS, 6)


def test_table_roundtrip_and_descriptors_are_of_the_table():
    c = D.make_streams(seed=2)["live"][5]
    t = D.table_of(c)
    assert len(t) == 128 and c.descriptors == D.descriptors_of(t)
    assert c.descriptors[0] == float(sum(t))


def test_sealed_manifest_on_disk_matches_the_generator():
    on_disk = json.loads(D.TASKS_PATH.read_text(encoding="utf-8"))
    assert on_disk["manifest_digest"] == D.make_tasks()["manifest_digest"]
    assert on_disk["n"] == D.N_TASKS


def test_run_one_is_deterministic_and_within_attainable_range():
    sealed = D.make_tasks()
    a = D.run_one(1, sealed); b = D.run_one(1, sealed)
    assert a == b
    for arm in ("live", "dead", "cheat"):
        assert a["arms"][arm]["stream_ceiling_family_b"] <= D.N_TASKS
        for name in H.POLICIES:
            p = a["arms"][arm]["policies"][name]
            assert 0 <= p["family_b_solved"] <= D.N_TASKS and 0 <= p["coverage"] <= 1.0
            assert p["retained_n"] <= D.CAPS["items"]
    assert a["arms"]["live"]["score_multiset_digest"] == a["arms"]["dead"]["score_multiset_digest"]

"""CHAOS proposes and never admits; the health report measures and never
judges; coverage weighting is a named policy that prefers the less used."""
from __future__ import annotations

import json
import uuid

import pytest

from archaeon import config as cfg
from archaeon.producer import chaos, health_report, templates as T
from archaeon.producer import tick as tickmod

psycopg2 = pytest.importorskip("psycopg2")


def _connect():
    try:
        from evidence_wiki.ew import db as ewdb
        return ewdb.connect()
    except Exception as exc:                       # pragma: no cover
        pytest.skip("PostgreSQL unavailable: {}".format(exc))


@pytest.fixture
def conn():
    c = _connect()
    yield c
    c.close()


@pytest.fixture
def lane(conn):
    name = "test-{}".format(uuid.uuid4().hex[:8])
    yield name
    from archaeon import vivqueue as vq
    cur = conn.cursor()
    for tbl, col in (("archaeon.substrate_census", "lane"),
                     ("archaeon.cadence_log", "lane"),
                     (str(vq.QUEUE), "cadence_lane"),
                     ("archaeon.cadence_gate", "lane")):
        cur.execute("DELETE FROM {} WHERE {} = %s".format(tbl, col), (name,))
    conn.commit()


def _cfg(lane):
    return cfg.ArchaeonConfig(cadence=cfg.CadenceConfig(lane=lane))


def _parent(tid="p.v0"):
    return {"template_id": tid, "kind": "evaluate_bitstring",
            "param_space": {"world": {"seed_root": {"int_range": [100, 200]}},
                            "payload": {"length": {"choices": [16, 24, 32]},
                                        "bits": {"uniform_bits": "length"}}}}


# --------------------------------------------------------------------------
# CHAOS
# --------------------------------------------------------------------------
def test_chaos_proposes_into_the_inbox_only(tmp_path):
    inbox = tmp_path / "inbox"
    p = chaos.mutate([_parent()], "WIDEN", directory=inbox)
    t = json.loads(p.read_text())
    assert t["status"] == "PROPOSED" and t["origin"]["source"] == "CHAOS"
    assert t["origin"]["parents"] == ["p.v0"]
    assert "admitted_by" not in t
    assert T.admitted(tmp_path) == [], "a chaos product must never be on the menu"


def test_chaos_is_reproducible_from_its_seed(tmp_path):
    a = json.loads(chaos.mutate([_parent()], "WIDEN", nonce="7",
                                directory=tmp_path / "a").read_text())
    b = json.loads(chaos.mutate([_parent()], "WIDEN", nonce="7",
                                directory=tmp_path / "b").read_text())
    assert a["param_space"] == b["param_space"]
    assert a["origin"]["seed"] == b["origin"]["seed"]


def test_widen_widens_and_narrow_narrows(tmp_path):
    w = json.loads(chaos.mutate([_parent()], "WIDEN", directory=tmp_path / "w").read_text())
    n = json.loads(chaos.mutate([_parent()], "NARROW", directory=tmp_path / "n").read_text())
    lo, hi = w["param_space"]["world"]["seed_root"]["int_range"]
    assert lo <= 100 and hi >= 200
    assert len(w["param_space"]["payload"]["length"]["choices"]) == 4
    lo, hi = n["param_space"]["world"]["seed_root"]["int_range"]
    assert lo >= 100 and hi <= 200
    assert len(n["param_space"]["payload"]["length"]["choices"]) == 2


def test_cross_refuses_to_invent_a_kind(tmp_path):
    a = _parent("a.v0")
    b = dict(_parent("b.v0"), kind="noop_v0")
    with pytest.raises(ValueError, match="share a kind"):
        chaos.mutate([a, b], "CROSS", directory=tmp_path)


def test_chaos_output_is_still_drawable_after_admission(tmp_path):
    """A widened template must remain a valid template: admit it by hand in
    the test and draw from it."""
    p = chaos.mutate([_parent()], "WIDEN", directory=tmp_path / "inbox")
    t = json.loads(p.read_text())
    t.update({"status": "ADMITTED", "admitted_by": "test",
              "admitted_at": "2026-09-06T00:00:00+00:00"})
    t["admitted_content_hash"] = T._content_hash(t)
    (tmp_path / "{}.json".format(t["template_id"])).write_text(json.dumps(t))
    d = T.draw("l", "2026-09-06", directory=tmp_path)
    assert d["template_id"] == t["template_id"]
    assert len(d["params"]["bits"]) == d["params"]["length"]


# --------------------------------------------------------------------------
# Health report
# --------------------------------------------------------------------------
def test_health_report_runs_and_flags_are_measurements(conn, lane):
    tickmod.tick(conn, _cfg(lane))
    r = health_report.report(conn, days=1, lane=lane)
    assert r["queue_rows"] == 1
    for f in r["flags"]:
        for k in ("flag", "value", "threshold", "lane", "unblocks"):
            assert k in f
    # one template, one kind: monoculture by construction, and it must SAY so
    names = {f["flag"] for f in r["flags"]}
    assert "TEMPLATE_MONOCULTURE" in names and "KIND_MONOCULTURE" in names


def test_health_report_is_read_only():
    from archaeon.tests.conftest import executable_source
    src = executable_source(health_report).upper()
    for banned in ("INSERT ", "UPDATE ", "DELETE ", "ALTER ", "CREATE "):
        assert banned not in src


def test_health_report_never_emits_a_verdict(conn, lane):
    from archaeon.queue import assert_no_negative_authority
    tickmod.tick(conn, _cfg(lane))
    assert_no_negative_authority(health_report.report(conn, days=1, lane=lane))


# --------------------------------------------------------------------------
# Coverage-weighted choice
# --------------------------------------------------------------------------
def test_coverage_choice_prefers_the_less_used():
    menu = [{"template_id": "used"}, {"template_id": "fresh"}]
    counts = {"used": 50}
    picks = [T.choose_template_coverage(menu, counts, "l", "2026-09-06",
                                        nonce=str(i))["template_id"]
             for i in range(200)]
    assert picks.count("fresh") > 150, picks.count("fresh")


def test_coverage_choice_is_uniform_when_nothing_is_used():
    menu = [{"template_id": "a"}, {"template_id": "b"}]
    picks = [T.choose_template_coverage(menu, {}, "l", "2026-09-06",
                                        nonce=str(i))["template_id"]
             for i in range(200)]
    assert 60 < picks.count("a") < 140


def test_tick_still_uses_the_uniform_baseline(conn, lane):
    """Coverage weighting exists as a NAMED policy and is not switched on:
    the baseline must stay the baseline until a comparison is designed."""
    r = tickmod.tick(conn, _cfg(lane))
    assert r["policy"] == "menu.uniform.v0"

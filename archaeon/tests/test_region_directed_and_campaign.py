"""The signal can now change the experiment -- and only when it should.

Region-directed templates take parameters FROM the fired region; they live on
a separate menu the random baseline never draws from; a directed draw without
a region refuses. The M-ELIGIBLE campaign builder produces eight v3 requests
that validate against Vivarium's live validator and names its own blockers.
"""
from __future__ import annotations

import json
import os
import sqlite3
import uuid

import pytest

from archaeon import config as cfg
from archaeon import fossils
from archaeon.producer import campaign, templates as T
from archaeon.producer import tick as tickmod

psycopg2 = pytest.importorskip("psycopg2")

REGION_T = {
    "template_id": "rd.v0", "registry_version": T.REGISTRY_VERSION,
    "kind": "evaluate_bitstring",
    "param_space": {"world": {"seed_root": {"from_region": "seed_root"}},
                    "payload": {"length": {"from_region": "length"},
                                "bits": {"uniform_bits": "length"}}},
    "origin": {"source": "HUMAN", "proposed_by": "t"},
    "status": "ADMITTED", "admitted_by": "t",
    "admitted_at": "2026-09-06T00:00:00+00:00"}
RANDOM_T = {
    "template_id": "rn.v0", "registry_version": T.REGISTRY_VERSION,
    "kind": "evaluate_bitstring",
    "param_space": {"world": {"seed_root": {"int_range": [1, 9]}},
                    "payload": {"length": {"choices": [16]},
                                "bits": {"uniform_bits": "length"}}},
    "origin": {"source": "RNG", "proposed_by": "t"},
    "status": "ADMITTED", "admitted_by": "t",
    "admitted_at": "2026-09-06T00:00:00+00:00"}


def _put(tmp_path, t):
    t = dict(t)
    t["admitted_content_hash"] = T._content_hash(t)
    (tmp_path / "{}.json".format(t["template_id"])).write_text(
        json.dumps(t, sort_keys=True))


# --------------------------------------------------------------------------
# Region-directed draws
# --------------------------------------------------------------------------
def test_parameters_actually_change_with_the_region(tmp_path):
    _put(tmp_path, REGION_T)
    a = T.draw("l", "d", directory=tmp_path,
               region={"seed_root": 111, "length": 24})["params"]
    b = T.draw("l", "d", directory=tmp_path,
               region={"seed_root": 222, "length": 32})["params"]
    assert (a["seed_root"], a["length"]) == (111, 24)
    assert (b["seed_root"], b["length"]) == (222, 32)
    assert len(a["bits"]) == 24 and len(b["bits"]) == 32


def test_directed_draw_without_a_region_refuses(tmp_path):
    _put(tmp_path, REGION_T)
    with pytest.raises(T.TemplateError, match="directed label"):
        T.draw_params(T.load(tmp_path / "rd.v0.json"), seed=1)


def test_the_two_menus_never_mix(tmp_path):
    _put(tmp_path, REGION_T)
    _put(tmp_path, RANDOM_T)
    assert {t["template_id"] for t in T.admitted(tmp_path)} == {"rn.v0"}
    assert {t["template_id"] for t in T.admitted(tmp_path, region_directed=True)} == {"rd.v0"}
    # the baseline draw can never return the directed template
    for i in range(20):
        assert T.draw("l", "d", nonce=str(i), directory=tmp_path)["template_id"] == "rn.v0"


def test_directed_policy_is_named_and_records_the_region(tmp_path):
    _put(tmp_path, REGION_T)
    d = T.draw("l", "d", directory=tmp_path, region={"seed_root": 5, "length": 16})
    assert d["policy"] == "menu.region_directed.v0"
    assert d["region"] == {"seed_root": 5, "length": 16}


def test_shipped_region_template_is_proposed_not_admitted():
    inbox = T.INBOX_DIR / "bitstring.resample_region.v0.json"
    assert inbox.exists()
    t = json.loads(inbox.read_text())
    assert t["status"] == "PROPOSED" and T.is_region_directed(t)
    # and therefore is on NEITHER live menu
    assert not any(x["template_id"] == t["template_id"]
                   for x in T.admitted(region_directed=True))


# --------------------------------------------------------------------------
# Region parameters from the ledger
# --------------------------------------------------------------------------
def _ledger(path):
    cx = sqlite3.connect(path)
    cx.executescript("""
        CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        INSERT INTO meta VALUES ('schema_version','6');
        CREATE TABLE clients (client_id TEXT PRIMARY KEY, name TEXT);
        INSERT INTO clients VALUES ('c','harmonia-m2');
        CREATE TABLE worlds (world_id TEXT PRIMARY KEY, client_id TEXT,
                             topology_group TEXT, parent_world_id TEXT,
                             seed_root INTEGER);
        CREATE TABLE experiments (exp_id TEXT PRIMARY KEY, world_id TEXT,
                                  spec TEXT, spec_hash TEXT, committed_seq INTEGER,
                                  state TEXT);
        INSERT INTO worlds VALUES ('w1','c',NULL,NULL,4242);
        INSERT INTO worlds VALUES ('w2','c',NULL,NULL,777);
        INSERT INTO worlds VALUES ('w3','c',NULL,NULL,NULL);
    """)
    cx.execute("INSERT INTO experiments VALUES ('e1','w1',?,'h',1,'OBSERVED')",
               (json.dumps({"work": {"kind": "evaluate_bitstring",
                                     "payload": {"bits": "0", "length": 24}}}),))
    cx.execute("INSERT INTO experiments VALUES ('e2','w2',?,'h',2,'OBSERVED')",
               (json.dumps({"work": {"payload": {"length": 16}}}),))
    cx.execute("INSERT INTO experiments VALUES ('e3','w2',?,'h',3,'OBSERVED')",
               (json.dumps({"work": {"payload": {"length": 32}}}),))
    cx.commit()
    cx.close()


def test_region_params_read_from_the_ledger(tmp_path):
    db = str(tmp_path / "r.db")
    _ledger(db)
    assert fossils.region_params("w1", db) == {"world_id": "w1", "seed_root": 4242,
                                               "length": 24}


def test_ambiguous_landscape_is_reported_not_resolved(tmp_path):
    db = str(tmp_path / "r.db")
    _ledger(db)
    r = fossils.region_params("w2", db)
    assert "length" not in r and r["length_ambiguous"] == [16, 32]


def test_missing_seed_root_gives_no_region(tmp_path):
    db = str(tmp_path / "r.db")
    _ledger(db)
    assert fossils.region_params("w3", db) is None
    assert fossils.region_params("nope", db) is None


# --------------------------------------------------------------------------
# The tick records WHY it could or could not direct
# --------------------------------------------------------------------------
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


def test_tick_states_why_a_signal_did_not_direct(conn, lane):
    r = tickmod.tick(conn, cfg.ArchaeonConfig(cadence=cfg.CadenceConfig(lane=lane)),
                     dry_run=True)
    ev = r["source_evidence"]
    assert ev["selection_basis"] in ("region_directed",
                                     "weak_signal_recorded_only", "random")
    rd = ev["region_direction"]
    if ev["selection_basis"] == "weak_signal_recorded_only":
        assert rd["note"], "a signal that did not direct must say why"
    if ev["selection_basis"] == "region_directed":
        assert rd["region"] and r["policy"] == "menu.region_directed.v0"
        assert r["spec"]["world"]["seed_root"] == rd["region"]["seed_root"]


# --------------------------------------------------------------------------
# M-ELIGIBLE campaign builder
# --------------------------------------------------------------------------
def test_campaign_plan_has_the_declared_shape():
    rows = campaign.plan()
    assert len(rows) == 8
    assert {r["family_id"] for r in rows} == set(campaign.FAMILIES)
    assert {r["arm_id"] for r in rows} == set(campaign.ARMS)
    for r in rows:
        assert r["spec"]["spec_version"] == 3
        assert r["spec"]["repeat"]["count"] == 4
        assert r["spec"]["repeat"]["seed_derivation"] != "constant"
    # arms differ by an execution parameter, so the contrast is a condition
    lens = {r["arm_id"]: r["length"] for r in rows}
    assert lens["arm-a"] != lens["arm-b"]


def test_campaign_specs_validate_against_vivarium_v3():
    c = campaign.check()
    assert c["invalid"] == [], c["invalid"]
    assert c["ok_to_issue"] is True
    assert c["observations_planned"] == 32


def test_campaign_names_the_arm_blocker():
    c = campaign.check()
    assert any("arm" in b["what"] for b in c["blockers"])
    assert "S17 transfer" in c["note"]


def test_campaign_specs_carry_no_provenance():
    from archaeon import vivqueue as vq
    for r in campaign.plan():
        vq.assert_spec_is_execution_only(r["spec"])
        assert "arm" not in r["spec"] and "family_id" not in r["spec"]


def test_campaign_plan_is_deterministic():
    a = [r["spec"] for r in campaign.plan()]
    b = [r["spec"] for r in campaign.plan()]
    assert a == b


def test_design_owner_declares_the_three_levels():
    """Harmonia (5759518f0): the design owner must name SELECTED / RANDOMIZED /
    ANALYZED before any power statement; ANALYZED is never finer than
    RANDOMIZED. The campaign builder is the design owner."""
    from archaeon.producer import campaign
    lv = campaign.check()["levels"]
    assert {"selected", "randomized", "analyzed", "declared_by"} <= set(lv)
    assert lv["randomized"].startswith("WORLD")
    assert lv["analyzed"].startswith("WORLD")

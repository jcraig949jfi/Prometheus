"""Declared tenancy, observation-level player attribution, the census, and the
policy/template provenance that makes post-hoc evaluation possible."""
from __future__ import annotations

import json
import os
import sqlite3
import uuid

import pytest

from archaeon import config as cfg
from archaeon import fossils
from archaeon.producer import census as census_mod
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
    cur.execute("DELETE FROM archaeon.substrate_census WHERE lane = %s", (name,))
    cur.execute("DELETE FROM archaeon.cadence_log WHERE lane = %s", (name,))
    cur.execute("DELETE FROM {q} WHERE cadence_lane = %s".format(q=vq.QUEUE),
                (name,))
    cur.execute("DELETE FROM archaeon.cadence_gate WHERE lane = %s", (name,))
    conn.commit()


def _cfg(lane):
    return cfg.ArchaeonConfig(cadence=cfg.CadenceConfig(lane=lane))


# --------------------------------------------------------------------------
# A synthetic SFE ledger with several tenants and both evidence classes
# --------------------------------------------------------------------------
def _ledger(path, schema_version=6):
    cx = sqlite3.connect(path)
    cx.executescript("""
        CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE clients (client_id TEXT PRIMARY KEY, name TEXT NOT NULL);
        CREATE TABLE worlds (world_id TEXT PRIMARY KEY, client_id TEXT,
                             topology_group TEXT, parent_world_id TEXT);
        CREATE TABLE experiments (exp_id TEXT PRIMARY KEY, world_id TEXT,
                                  spec TEXT, spec_hash TEXT, committed_seq INTEGER,
                                  state TEXT);
        CREATE TABLE observations (obs_id TEXT PRIMARY KEY, world_id TEXT,
                                   exp_id TEXT, content TEXT, outcome TEXT,
                                   evidence_class TEXT, work_id TEXT,
                                   created_seq INTEGER);
    """)
    cx.execute("INSERT INTO meta VALUES ('schema_version', ?)",
               (str(schema_version),))
    tenants = {"harmonia-m2": "cli_h", "vivarium-selftest": "cli_st",
               "vivarium": "cli_v"}
    for name, cid in tenants.items():
        cx.execute("INSERT INTO clients VALUES (?,?)", (cid, name))
    seq = 0

    def obs(world, cid, ev, players=None, score=0.5):
        nonlocal seq
        seq += 1
        cx.execute("INSERT OR IGNORE INTO worlds VALUES (?,?,?,?)",
                   (world, cid, "g", None))
        spec = {"pew": {"players": players}} if players is not None else {}
        eid = "exp_{}".format(seq)
        cx.execute("INSERT INTO experiments VALUES (?,?,?,?,?,?)",
                   (eid, world, json.dumps(spec), "sha256:" + "0" * 64, seq,
                    "OBSERVED"))
        cx.execute("INSERT INTO observations VALUES (?,?,?,?,?,?,?,?)",
                   ("obs_{}".format(seq), world, eid,
                    json.dumps({"result": {"score": score}}), "SURVIVED", ev,
                    "wrk", seq))

    for i in range(10):
        obs("w_h", "cli_h", "ENGINE_WORK_RESULT")
    for i in range(5):
        obs("w_h", "cli_h", "CLIENT_ASSERTED")
    for i in range(7):
        obs("w_st", "cli_st", "ENGINE_WORK_RESULT")          # selftest: excluded
    obs("w_v", "cli_v", "ENGINE_WORK_RESULT", players=["pA"])
    obs("w_v", "cli_v", "ENGINE_WORK_RESULT", players=["pB"])
    obs("w_v", "cli_v", "ENGINE_WORK_RESULT", players=["pA", "pB"])  # ambiguous
    obs("w_v", "cli_v", "ENGINE_WORK_RESULT", players=[])
    cx.commit()
    cx.close()


def test_tenancy_filter_excludes_and_counts(tmp_path):
    db = str(tmp_path / "t.db")
    _ledger(db)
    c = fossils.read_sfe(db)
    t = c.window["tenancy"]
    assert "harmonia-m2" in t["admitted_client_names"]
    assert "vivarium-selftest" not in t["admitted_client_names"]
    assert t["excluded_attested_by_client_name"]["vivarium-selftest"] == 7
    assert {r.region for r in c.rows} == {"w_h", "w_v"}


def test_client_asserted_is_not_a_fossil(tmp_path):
    db = str(tmp_path / "t.db")
    _ledger(db)
    c = fossils.read_sfe(db)
    assert all(r.anchors["evidence_class"] == "ENGINE_WORK_RESULT"
               for r in c.rows)
    assert len([r for r in c.rows if r.region == "w_h"]) == 10


def test_newer_schema_is_refused_not_misread(tmp_path):
    db = str(tmp_path / "t7.db")
    _ledger(db, schema_version=7)
    c = fossils.read_sfe(db)
    assert c.rows == [] and "newer" in c.window["error"]


def test_read_is_one_transaction():
    """A multi-statement read of a live WAL database is not one observation of
    one state unless it is inside one transaction (consumer contract s2)."""
    from archaeon.tests.conftest import executable_source
    src = executable_source(fossils)
    i = src.index("def read_sfe(")
    body = src[i:src.index("def read_pew(")]
    # ast.unparse normalises string quotes, so match on the statement text
    # rather than on a particular quoting.
    assert "execute('BEGIN')" in body or 'execute("BEGIN")' in body
    assert "execute('COMMIT')" in body or 'execute("COMMIT")' in body
    assert "isolation_level=None" in body


# --------------------------------------------------------------------------
# Observation-level player attribution
# --------------------------------------------------------------------------
def test_spec_players_chart_attributes_per_observation(tmp_path):
    db = str(tmp_path / "t.db")
    _ledger(db)
    c = fossils.read_sfe(db, chart=cfg.SFE_SPEC_PLAYERS_CHART)
    players = {r.player for r in c.rows if r.player}
    assert players == {"pA", "pB"}, players
    # two players in ONE region -- the shape D2/D4 could never get from a
    # world-level manifest attribution
    in_w_v = {r.player for r in c.rows if r.region == "w_v" and r.player}
    assert in_w_v == {"pA", "pB"}


def test_multi_player_experiment_is_unattributed_and_counted(tmp_path):
    db = str(tmp_path / "t.db")
    _ledger(db)
    c = fossils.read_sfe(db, chart=cfg.SFE_SPEC_PLAYERS_CHART)
    assert c.window["unattributed_multi_player_experiments"] == 1
    assert all(r.player != "['pA', 'pB']" for r in c.rows)


# --------------------------------------------------------------------------
# Census
# --------------------------------------------------------------------------
def test_tick_persists_a_census_row(conn, lane):
    r = tickmod.tick(conn, _cfg(lane))
    assert r.get("census_id"), r.get("census_error")
    s = census_mod.series(conn, lane)
    assert len(s) == 1 and s[0]["rows"] == r["fossils"]["rows"]


def test_census_carries_wishlist_for_blocked_detectors(conn, lane):
    r = tickmod.tick(conn, _cfg(lane))
    assert isinstance(r.get("wishlist"), list)
    names = {w["detector"] for w in r["wishlist"]}
    # on the default chart the player detectors are blocked, so they must be
    # named with a lane that could unblock them
    assert {"REPEATED_SMALL_DEVIATION", "SIGN_INSTABILITY",
            "PLAYER_ORDER_REVERSAL"} <= names
    assert all("lane" in w and "need" in w for w in r["wishlist"])


def test_census_records_tenancy(conn, lane):
    tickmod.tick(conn, _cfg(lane))
    cur = conn.cursor()
    cur.execute("SELECT tenancy FROM archaeon.substrate_census WHERE lane=%s",
                (lane,))
    t = cur.fetchone()[0]
    assert "admitted_client_names" in t and "evidence_classes" in t


def test_census_failure_does_not_stop_a_proposal(conn, lane, monkeypatch):
    monkeypatch.setattr(census_mod, "persist",
                        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("x")))
    r = tickmod.tick(conn, _cfg(lane))
    assert r["wrote"] and "census_error" in r


# --------------------------------------------------------------------------
# Provenance for post-hoc policy evaluation
# --------------------------------------------------------------------------
def test_queue_row_carries_policy_version_and_template(conn, lane):
    from archaeon import vivqueue as vq
    r = tickmod.tick(conn, _cfg(lane))
    cur = conn.cursor()
    cur.execute("SELECT source_evidence FROM {q} WHERE experiment_id=%s"
                .format(q=vq.QUEUE), (r["experiment_id"],))
    ev = cur.fetchone()[0]
    # the draw policy is the uniform menu; the TEMPLATE is the frozen baseline
    assert ev["policy_version"].startswith("menu.uniform.v0@")
    assert ev["template_id"] == "bitstring.uniform.v0"
    assert ev["policy"]["template_content_hash"].startswith("sha256:")
    assert ev["selection_basis"] in ("random", "weak_signal_recorded_only")


def test_policy_identity_is_not_in_the_sealed_spec(conn, lane):
    from archaeon import vivqueue as vq
    r = tickmod.tick(conn, _cfg(lane))
    cur = conn.cursor()
    cur.execute("SELECT experiment_spec FROM {q} WHERE experiment_id=%s"
                .format(q=vq.QUEUE), (r["experiment_id"],))
    spec = json.dumps(cur.fetchone()[0])
    for banned in ("policy_version", "template_id", "random.v0"):
        assert banned not in spec

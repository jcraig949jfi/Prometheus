"""viv/deliver.py -- the outbox deliverer against a fake PEW, on a drafted
throwaway schema (PEW_OUTBOX_DESIGN.md s7).

    POSITIVE  an attempt completes with PEW DOWN: the row is COMPLETED, its
              events are PENDING; PEW comes back; the deliverer drains in
              sequence, marks DELIVERED, stamps pew_reference on the row
    NEGATIVE  PEW answers 422 -> REJECTED, never retried; a 503 mid-stream
              stops that stream (lower sequences first, VIV42 never fires)
    CHEAT     delivering twice (the ack was lost) posts the encounter twice
              and PEW's duplicate answer marks DELIVERED once with ONE fossil
              counted; the bound parks the deliverer after N idle ticks with
              pending rows; the 10,000-row backlog parks it synthetically;
              the consumer's tick path never imports the HTTP client
"""
from __future__ import annotations

import json
import os

import pytest

from viv import db as _db
from viv import deliver as _dl
from viv import outbox as _ob
from viv import queue as _q
from viv import spec as _spec
from viv.loop import EXECUTED, Vivarium
from tests.test_loop import make_spec
from tests.test_point_release_attempts import VerifyingClient, _runner_over, drafted  # noqa: F401


class FakePew:
    """Counts bodies; can be DOWN, can reject, remembers encounters for
    duplicate answers."""

    namespace = "test"

    def __init__(self):
        self.down = False
        self.reject = False
        self.worlds = []
        self.encounters = {}
        self.posts = 0

    def _req(self, method, path, body=None):
        if self.down:
            raise ConnectionError("PEW down")
        if path == "/fossil/worlds":
            self.worlds.append(body)
            return 200, {"status": "inserted"}
        if path == "/fossil/encounters":
            self.posts += 1
            if self.reject:
                return 422, {"detail": "bad body"}
            key = (body["encounter_id"], body["run_id"])
            if key in self.encounters:
                return 200, {"status": "duplicate_identical"}
            self.encounters[key] = body
            return 200, {"status": "inserted"}
        if path.startswith("/fossil/encounters/"):
            return 200, {"encounter_id": path.rsplit("/", 1)[1]}
        return 404, {}


def _run_one(conn, schema, encounter_id, worker="dl-worker"):
    spec = make_spec(pew={"encounter_id": encounter_id, "players": []})
    eid = str(_q.enqueue(conn, created_by="dl", source_reason="deliver", experiment_spec=spec, schema=schema))
    conn.commit()
    runner = _runner_over(VerifyingClient(), _spec.spec_hash(spec))
    v = Vivarium(worker_id=worker, schema=schema, runner=runner, pew_client=None, log=lambda *_a: None)
    assert v.tick(conn).outcome == EXECUTED
    return eid


def _deliverer(tmp_path, fake, **kw):
    cfg = _dl.Config(producer=kw.pop("producer", "dl-worker"), var_dir=tmp_path, post=False, disable_task=False, **kw)
    return _dl.Deliverer(cfg, client_factory=lambda: fake, log=lambda *_a: None)


def _states(conn, schema, eid):
    with conn.cursor() as cur:
        cur.execute("SELECT event_kind, state, pew_reference FROM " + schema + ".pew_outbox WHERE source_experiment=%s ORDER BY sequence", (eid,))
        rows = cur.fetchall()
    conn.rollback()
    return rows


def test_positive_execution_completes_with_pew_down_and_delivers_later(conn, drafted, tmp_path):
    schema = drafted
    eid = _run_one(conn, schema, "enc-dl-1")
    assert _q.get(conn, eid, schema=schema)["status"] == "completed"
    assert all(s == "PENDING" for _, s, _ in _states(conn, schema, eid))
    fake = FakePew(); fake.down = True
    d = _deliverer(tmp_path, fake)
    r = d.tick(conn)
    assert r["verdict"] in ("STUCK",) and r["delivered"] == 0
    assert all(s == "PENDING" for _, s, _ in _states(conn, schema, eid))
    fake.down = False
    r = d.tick(conn)
    assert r["delivered"] >= 1
    st = _states(conn, schema, eid)
    enc = [row for row in st if row[0] == "ENCOUNTER_RECORDED"][0]
    assert enc[1] == "DELIVERED" and enc[2].startswith("pew:encounter/enc-dl-1:")
    # the terminal row stays frozen (pew_reference NULL); the reference is on the outbox row
    assert _q.get(conn, eid, schema=schema)["pew_reference"] is None
    assert fake.posts == 1 and len(fake.encounters) == 1


def test_negative_a_4xx_is_rejected_and_never_retried(conn, drafted, tmp_path):
    schema = drafted
    eid = _run_one(conn, schema, "enc-dl-2")
    fake = FakePew(); fake.reject = True
    d = _deliverer(tmp_path, fake)
    d.tick(conn)
    st = {k: s for k, s, _ in _states(conn, schema, eid)}
    assert st["ENCOUNTER_RECORDED"] == "REJECTED"
    posts = fake.posts
    fake.reject = False
    d.tick(conn)
    assert fake.posts == posts                       # not retried
    assert {k: s for k, s, _ in _states(conn, schema, eid)}["ENCOUNTER_RECORDED"] == "REJECTED"


def test_negative_a_transport_failure_stops_the_stream_in_order(conn, drafted, tmp_path):
    schema = drafted
    e1 = _run_one(conn, schema, "enc-dl-3a")
    e2 = _run_one(conn, schema, "enc-dl-3b")
    fake = FakePew()
    calls = {"n": 0}
    real = fake._req

    def flaky(method, path, body=None):
        calls["n"] += 1
        if path == "/fossil/encounters" and calls["n"] < 3:
            raise ConnectionError("blip")
        return real(method, path, body)
    fake._req = flaky
    d = _deliverer(tmp_path, fake)
    d.tick(conn)
    # the first encounter failed on transport: it and EVERYTHING after it in
    # the stream stay PENDING; nothing was delivered out of order
    s1 = {k: s for k, s, _ in _states(conn, schema, e1)}
    s2 = {k: s for k, s, _ in _states(conn, schema, e2)}
    assert s1["ENCOUNTER_RECORDED"] == "PENDING" and s2["ENCOUNTER_RECORDED"] == "PENDING"
    d.tick(conn); d.tick(conn)
    assert {k: s for k, s, _ in _states(conn, schema, e1)}["ENCOUNTER_RECORDED"] == "DELIVERED"


def test_cheat_a_lost_ack_does_not_double_count(conn, drafted, tmp_path):
    schema = drafted
    eid = _run_one(conn, schema, "enc-dl-4")
    fake = FakePew()
    d = _deliverer(tmp_path, fake)
    d.tick(conn)
    assert fake.posts == 1
    # simulate the lost ack: set the row back to PENDING by hand -- the
    # trigger forbids DELIVERED -> PENDING (VIV43), which is the point: a
    # delivered row cannot regress. So the only way to "deliver twice" is a
    # second deliverer instance racing; emulate by posting the payload again.
    with conn.cursor() as cur:
        cur.execute("SELECT payload FROM " + schema + ".pew_outbox WHERE source_experiment=%s AND event_kind='ENCOUNTER_RECORDED'", (eid,))
        payload = cur.fetchone()[0]
    conn.rollback()
    from viv import pew as _pew
    out = _pew.post_bodies(fake, payload)
    assert out["idempotent_replay"] is True and fake.posts == 2 and len(fake.encounters) == 1


def test_cheat_the_bound_parks_after_idle_ticks_with_pending_rows(conn, drafted, tmp_path):
    schema = drafted
    _run_one(conn, schema, "enc-dl-5")
    fake = FakePew(); fake.down = True
    d = _deliverer(tmp_path, fake, bound=3)
    r = [d.tick(conn) for _ in range(3)]
    assert r[-1]["verdict"] == "PARKED_DELIVERER"
    assert d.park_path.exists()
    assert d.tick(conn)["verdict"] == "PARKED"          # refuses until cleared


def test_cheat_the_backlog_threshold_parks(conn, drafted, tmp_path):
    schema = drafted
    _run_one(conn, schema, "enc-dl-6")
    fake = FakePew()
    d = _deliverer(tmp_path, fake, park_backlog=1)       # synthetic: 3 pending > 1
    r = d.tick(conn)
    assert r["verdict"] == "PARKED_DELIVERER" and "backlog" in r["park"]["reason"]


def test_cheat_the_tick_path_does_not_import_the_http_client():
    """viv/loop.py may build bodies but never posts; only viv/deliver.py
    (and the pre-outbox synchronous fallback through viv/pew.py) may."""
    import viv.loop as L
    src = open(L.__file__, encoding="utf-8").read()
    assert "post_bodies(" not in src
    assert "urllib.request" not in src

"""A6 wiring + B3 health, through the real HTTP app (TestClient).

Controls:
  positive   a mutating request writes intent then effected; the response
             carries X-SFE-Request-Id; attest(rid) -> CONFIRMED_EFFECT
  refusal    a 4xx writes intent then refused -> CONFIRMED_NO_EFFECT
  lock       a lock timeout (unhandled OperationalError in the handler)
             writes refused with the reason, returns 500, ledger untouched
  epistemic  an intent with no outcome is UNKNOWN_RECONCILABLE when it has
             an idempotency key and UNKNOWN_UNRECONCILABLE when it does not;
             reconciliation by the ledger flips it; a refused line that the
             ledger contradicts is reported as a contradiction, ledger wins
  cheat      the journal never claims CONFIRMED from intent alone, however
             the caller's error looked (took_effect is None)
  read-only  GET writes nothing to the journal
  fail-open  a journal that cannot be written leaves the request served
  health     /v2/health reports only measured fields; write_lock counts
             match the writes the test made; the ledger volume is the db's
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import threading

import pytest
from fastapi.testclient import TestClient

_ENGINE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ENGINE_ROOT not in sys.path:
    sys.path.insert(0, _ENGINE_ROOT)

from sfe import attestation                    # noqa: E402
from sfe.api import create_app                 # noqa: E402
from sfe.store import WRITE_LOCK_STATS, Store  # noqa: E402


@pytest.fixture
def app(tmp_path):
    a = create_app(str(tmp_path / "w.db"), incidents_dir=str(tmp_path / "inc"))
    with TestClient(a) as c:
        yield a, c


def _lines(d):
    out = []
    for n in sorted(os.listdir(d)):
        if n.endswith(".jsonl"):
            with open(os.path.join(d, n), encoding="ascii") as fh:
                out += [json.loads(line) for line in fh]
    return out


def test_positive_mutating_request_is_attested_confirmed_effect(app):
    a, c = app
    r = c.post("/v2/clients", json={"name": "a6"})
    assert r.status_code == 200
    rid = r.headers["X-SFE-Request-Id"]
    kinds = [(line["kind"], line["rid"]) for line in _lines(a.state.journal.directory)]
    assert ("intent", rid) in kinds and ("effected", rid) in kinds
    v = a.state.journal.attest(rid)
    assert v["state"] == "CONFIRMED_EFFECT" and v["took_effect"] is True
    assert v["reached_engine"] is True


def test_refusal_4xx_is_confirmed_no_effect(app):
    a, c = app
    r = c.post("/v2/worlds", json={"name": "x"})   # no bearer -> 401
    assert r.status_code == 401
    rid = r.headers["X-SFE-Request-Id"]
    v = a.state.journal.attest(rid)
    assert v["state"] == "CONFIRMED_NO_EFFECT" and v["took_effect"] is False
    assert v["refused_reason"] == "http_401"


def test_get_writes_nothing(app):
    a, c = app
    before = len(_lines(a.state.journal.directory))
    r = c.get("/v2/version")
    assert r.status_code == 200 and "X-SFE-Request-Id" not in r.headers
    assert len(_lines(a.state.journal.directory)) == before


def test_lock_timeout_is_refused_in_the_journal_and_leaves_the_ledger_alone(app, tmp_path):
    a, c = app
    tok = c.post("/v2/clients", json={"name": "victim"}).json()["token"]
    hdr = {"authorization": "Bearer " + tok}
    sid = c.post("/v2/sessions", json={"name": "s"}, headers=hdr).json()["session_id"]
    holder_up, release = threading.Event(), threading.Event()

    def holder():
        h = Store(str(tmp_path / "w.db"))
        h.initialize()
        with h.write() as cx:
            cx.execute("SELECT 1")
            holder_up.set()
            release.wait(30)

    threading.Thread(target=holder, daemon=True).start()
    holder_up.wait(10)
    orig = Store.__init__

    def fast(self, db_path, *, timeout=0.5):        # a 30 s wait, compressed
        orig(self, db_path, timeout=timeout)

    Store.__init__ = fast
    try:
        cx = sqlite3.connect(str(tmp_path / "w.db"))
        before = cx.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        cx.close()
        r = c.post("/v2/worlds", json={"name": "w", "session_id": sid},
                   headers=dict(hdr, **{"Idempotency-Key": "k-146"}))
        assert r.status_code == 500
        rid = r.headers["X-SFE-Request-Id"]
    finally:
        Store.__init__ = orig
        release.set()
    v = a.state.journal.attest(rid)
    assert v["state"] == "CONFIRMED_NO_EFFECT" and v["took_effect"] is False
    assert "OperationalError" in v["refused_reason"] and "locked" in v["refused_reason"]
    cx = sqlite3.connect(str(tmp_path / "w.db"))
    assert cx.execute("SELECT COUNT(*) FROM events").fetchone()[0] == before
    cx.close()
    assert WRITE_LOCK_STATS.snapshot()["failures"] >= 1


def test_epistemic_rule_unknown_stays_unknown_until_reconciled(tmp_path):
    j = attestation.Journal(str(tmp_path / "inc"))
    with_key = j.intent(route="POST /v2/worlds", idem_key="k1")
    no_key = j.intent(route="POST /v2/worlds")
    assert j.attest(with_key)["state"] == "UNKNOWN_RECONCILABLE"
    assert j.attest(no_key)["state"] == "UNKNOWN_UNRECONCILABLE"
    for rid in (with_key, no_key):
        assert j.attest(rid)["took_effect"] is None          # never "failed"
    assert j.attest(with_key, ledger_has_effect=True)["state"] == "CONFIRMED_EFFECT"
    assert j.attest(with_key, ledger_has_effect=False)["state"] == "CONFIRMED_NO_EFFECT"
    j.refused(with_key, reason="lock timeout")
    v = j.attest(with_key, ledger_has_effect=True)
    assert v["state"] == "CONFIRMED_EFFECT" and v.get("contradiction") is True
    assert j.attest("req_nope")["state"] == "UNKNOWN_UNRECONCILABLE"
    assert j.attest("req_nope")["reached_engine"] is False


def test_cold_scan_reads_another_process_journal(tmp_path):
    j1 = attestation.Journal(str(tmp_path / "inc"))
    rid = j1.intent(route="POST /v2/x", idem_key="z")
    j1.effected(rid, kind="POST /v2/x", ref="wld_1")
    j2 = attestation.Journal(str(tmp_path / "inc"))     # fresh memory
    v = j2.attest(rid)
    assert v["state"] == "CONFIRMED_EFFECT" and v["ref"] == "wld_1"


def test_fail_open_journal_still_serves(tmp_path):
    a = create_app(str(tmp_path / "w.db"), incidents_dir="/nonexistent/x/y/z")
    with TestClient(a) as c:
        assert a.state.journal.degraded is True
        r = c.post("/v2/clients", json={"name": "still-served"})
        assert r.status_code == 200 and r.headers.get("X-SFE-Request-Id")
        h = c.get("/v2/health").json()
        assert h["attestation"]["degraded"] is True


def test_health_reports_measured_quantities(app, tmp_path):
    a, c = app
    WRITE_LOCK_STATS.reset()
    tok = c.post("/v2/clients", json={"name": "h"}).json()["token"]
    hdr = {"authorization": "Bearer " + tok}
    sid = c.post("/v2/sessions", json={"name": "s"}, headers=hdr).json()["session_id"]
    c.post("/v2/worlds", json={"name": "w", "session_id": sid}, headers=hdr)
    h = c.get("/v2/health").json()
    assert set(h) >= {"process", "ledger", "write_lock", "attestation",
                      "engine_source_hash", "engine_instance_id"}
    assert h["ledger"]["path"].lower() == os.path.abspath(str(tmp_path / "w.db")).lower()
    assert h["ledger"]["volume"] == os.path.splitdrive(os.path.abspath(str(tmp_path)))[0]
    assert h["ledger"]["last_event_age_s"] is not None and h["ledger"]["last_event_age_s"] < 60
    assert h["ledger"]["events_last_hour"] >= 1
    assert h["write_lock"]["acquisitions"] >= 3          # client, session, world
    assert h["write_lock"]["failures"] == 0
    assert h["write_lock"]["max_wait_s"] < 1.0
    assert h["process"]["requests"] >= 4
    assert h["attestation"]["counts"]["intent"] >= 3
    assert h["attestation"]["open_intents_over_60s"] == 0

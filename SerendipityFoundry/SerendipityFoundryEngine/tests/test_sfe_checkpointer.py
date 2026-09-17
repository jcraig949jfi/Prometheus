"""9.0.1: WAL maintenance leaves the request path (SFE_LONG_RUN_REPORT.md s7-s8).

The defect these tests would have caught: (a) a request-path handle that
checkpoints inside COMMIT (autocheckpoint on), and (b) a WAL that nothing
ever resets, so its file grows to a high-water mark and every checkpoint
walks it. Both are pinned here at the level a unit test can reach; the
real-process acceptance is deploy/longrun_load.py.
"""
import os
import sqlite3
import sys
import time

from fastapi.testclient import TestClient

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from sfe.api import create_app                                    # noqa: E402
from sfe.runtime import Foundry                                   # noqa: E402
from sfe.store import Checkpointer, Store, WAL_SIZE_LIMIT_BYTES    # noqa: E402

HDR = "X-SFE-Session"


def test_request_path_handles_never_checkpoint_and_bound_the_wal_file(tmp_path):
    s = Store(str(tmp_path / "a.db"))
    s.initialize()
    assert s._conn.execute("PRAGMA wal_autocheckpoint").fetchone()[0] == 0
    assert s._conn.execute("PRAGMA journal_size_limit").fetchone()[0] == WAL_SIZE_LIMIT_BYTES
    assert s._conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    # a non-request-path handle (the checkpointer's kind) keeps SQLite's default
    c = Store(str(tmp_path / "a.db"), request_path=False)
    assert c._conn.execute("PRAGMA wal_autocheckpoint").fetchone()[0] == 1000
    s.close(); c.close()


def test_checkpointer_backfills_and_truncates_a_wal_the_request_path_left_alone(tmp_path):
    db = str(tmp_path / "w.db")
    f = Foundry(db)
    cid = f.create_client("x")
    sid = f.create_session(cid, "s")
    sid = sid["session_id"] if isinstance(sid, dict) else sid
    w = f.create_world(sid, "w")["world_id"]
    f.start_world(w, cid)
    for i in range(1500):                                    # > 1000 pages of WAL, no autocheckpoint
        e = f.create_experiment(w, {"i": i, "pad": "x" * 512}, client_id=cid)["exp_id"]
        f.commit_experiment(w, e, client_id=cid)
    wal = db + "-wal"
    grown = os.path.getsize(wal)
    assert grown > 1_000_000, grown                          # the request path did NOT checkpoint
    ck = Checkpointer(db, interval_s=60)                     # drive it by hand
    out = ck.tick()
    busy, log_frames, backfilled = out["passive"]
    assert busy == 0 and log_frames == backfilled and log_frames > 0
    assert out["truncate"] is not None and out["truncate"][0] == 0   # clean -> truncated
    assert os.path.getsize(wal) < grown and os.path.getsize(wal) <= WAL_SIZE_LIMIT_BYTES
    snap = ck.snapshot()
    assert snap["runs"] == 1 and snap["truncates"] == 1 and snap["errors"] == 0
    assert snap["max_wal_bytes_seen"] >= 0 and snap["request_path_autocheckpoint"] == 0
    # with a reader holding the WAL, TRUNCATE is refused (busy), never blocked
    for i in range(300):
        e = f.create_experiment(w, {"i": i}, client_id=cid)["exp_id"]
        f.commit_experiment(w, e, client_id=cid)
    reader = sqlite3.connect(db, isolation_level=None)
    cur = reader.execute("SELECT * FROM events")                # open read snapshot
    cur.fetchone()
    t0 = time.monotonic()
    out2 = ck.tick()
    assert time.monotonic() - t0 < 2.0                        # did not block behind the reader
    assert out2["passive"][0] in (0, 1)                        # passive never fails the tick
    cur.close(); reader.close()
    f.close()


def test_checkpointer_thread_is_alive_and_visible_on_health(tmp_path):
    app = create_app(str(tmp_path / "h.db"), checkpoint_interval_s=0.2)
    c = TestClient(app)
    tok = c.post("/v2/clients", json={"name": "h"}).json()["token"]
    h = {"Authorization": "Bearer " + tok}
    sess = c.post("/v2/sessions", json={"name": "s"}, headers=h).json()
    h[HDR] = sess["session_key"]
    w = c.post("/v2/worlds", json={"session_id": sess["session_id"], "name": "w"}, headers=h).json()["world_id"]
    c.post("/v2/worlds/%s/start" % w, headers=h)
    for i in range(50):
        e = c.post("/v2/worlds/%s/experiments" % w, json={"spec": {"i": i}}, headers=h).json()["exp_id"]
        c.post("/v2/worlds/%s/experiments/%s/commit" % (w, e), json={}, headers=h)
    time.sleep(0.8)
    hh = c.get("/v2/health").json()["checkpointer"]
    assert hh["alive"] is True and hh["runs"] >= 2 and hh["errors"] == 0
    assert hh["last_run_age_s"] is not None and hh["last_run_age_s"] < 5
    assert hh["last_passive"] is not None and hh["request_path_autocheckpoint"] == 0
    assert hh["wal_bytes"] is not None and hh["wal_size_limit_bytes"] == WAL_SIZE_LIMIT_BYTES
    app.state.checkpointer.stop()
    assert c.get("/v2/health").json()["checkpointer"]["alive"] is False   # its death is visible
